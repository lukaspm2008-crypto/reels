"""Reel engine runner.

usage:
  python3 engine/run.py episodes/<id>            full build -> episodes/<id>/build/final.mp4 + upload.mp4 + contact.png
  python3 engine/run.py episodes/<id> test 3@1.2 8@0.5   render single frames (scene@seconds) to build/test_*.png

An episode folder holds episode.py with: META, VOICE, SPEED, LINES (one per scene), CAPS (caption blocks per scene),
optional TAIL / DESIGN_DUR, SCENES (list of scene functions f(canvas, t, D)), sfx_cues(put, S, K, D, fx).
Optional (engine v2):
  TRANSITIONS = ['whip', 'zoom', 'wipe', 'whipv', 'cut', ...]  one per scene boundary (n-1; never at the loop seam).
                Default: whip/zoom/wipe rotation. ~0.27 s centred on the cut, whoosh SFX added automatically.
  TRANSITION_SFX = True    auto whoosh at every transition
  AMBIENCE = ['room', 'cafe', None, ('birds', 0.8), ...]  one bed per scene (see sfx.AMBIENCES), crossfaded, ducked under VO
  POST = True | {'vig': 64, 'grain': 1.0}   final look pass (vignette + paper grain); False disables
"""
import os, sys, json, math, time, subprocess, importlib.util, wave
import numpy as np

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
sys.path.insert(0, ENGINE)
import lib
import sfx as fx

KOKORO_DIR = os.environ.get('KOKORO_DIR', '/tmp/kokoro')


def load_episode(ep_dir):
    spec = importlib.util.spec_from_file_location('episode', os.path.join(ep_dir, 'episode.py'))
    ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
    return ep


# ------------------------------------------------------------------ voice
def tts(ep, build):
    info_p = os.path.join(build, 'vo_info.json')
    key = json.dumps([ep.LINES, ep.VOICE, ep.SPEED])
    if os.path.exists(info_p):
        info = json.load(open(info_p))
        if info.get('key') == key:
            return info
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(KOKORO_DIR, 'kokoro-v1.0.onnx'), os.path.join(KOKORO_DIR, 'voices-v1.0.bin'))
    dur = []
    for i, t in enumerate(ep.LINES):
        a, sr = k.create(t, voice=ep.VOICE, speed=ep.SPEED, lang='en-us')
        a = np.asarray(a, np.float32) * 32767
        idx = np.where(np.abs(a) > 400)[0]
        a = a[max(idx[0] - int(.02 * sr), 0):idx[-1] + int(.08 * sr)]
        np.save(os.path.join(build, f'vo{i + 1:02d}.npy'), a); dur.append(len(a) / sr)
    info = {'sr': sr, 'dur': dur, 'key': key}
    json.dump(info, open(info_p, 'w'))
    return info


# ------------------------------------------------------------------ timeline
class Timeline:
    def __init__(self, ep, vo):
        n = len(ep.LINES)
        self.n = n
        self.VO = vo['dur']
        self.LEAD = [0.05] + [0.1] * (n - 1)
        self.TAIL = list(getattr(ep, 'TAIL', [0.25] * n))
        self.DUR = [self.LEAD[i] + self.VO[i] + self.TAIL[i] for i in range(n)]
        self.START = [sum(self.DUR[:i]) for i in range(n)]
        dd = getattr(ep, 'DESIGN_DUR', None)
        self.DESIGN = dd if dd else self.DUR
        self.K = [self.DUR[i] / self.DESIGN[i] for i in range(n)]
        self.CAPT = [self.cap_times(ep.CAPS[i], i) for i in range(n)]
        self.frames = [int(round((self.START[i] + self.DUR[i]) * lib.FPS)) - int(round(self.START[i] * lib.FPS)) for i in range(n)]
        self.F0 = [sum(self.frames[:i]) for i in range(n)]
        self.TOTAL = sum(self.frames) / lib.FPS
        tr = getattr(ep, 'TRANSITIONS', None)
        if tr is None: tr = [('whip', 'zoom', 'wipe')[k % 3] for k in range(n - 1)]
        self.TR = (list(tr) + ['cut'] * n)[:n - 1]

    def cap_times(self, blocks, i):
        wts = []
        for b in blocks:
            s = b.replace('*', ''); w = len(s) + 2
            if s.endswith(','): w += 4
            if s.endswith(('.', ':', '?', '!')): w += 7
            wts.append(w)
        tot = sum(wts); t = self.LEAD[i]; out = []
        for b, w in zip(blocks, wts):
            out.append((t, b)); t += self.VO[i] * w / tot
        return out


TRANS_H = 4          # frames on each side of a cut -> 8 frames ~ 0.27 s
_AUX = []


def _aux(k):
    import skia
    while len(_AUX) <= k: _AUX.append(skia.Surface(lib.W, lib.H))
    return _AUX[k]


def scene_into(c, ep, tl, i, t):
    c.clear(lib.C(lib.CREAM))
    c.save(); ep.SCENES[i](c, t / tl.K[i], tl.DESIGN[i]); c.restore()


def _smoother(p):
    p = min(1.0, max(0.0, p)); return p * p * p * (p * (p * 6 - 15) + 10)


def composite(c, kind, p, imA, imB):
    """transition between outgoing image A and incoming image B at progress p (0..1)"""
    import skia
    W, H = lib.W, lib.H
    lin = skia.SamplingOptions(skia.FilterMode.kLinear)
    if kind in ('whip', 'whipv'):
        e = _smoother(p); speed = (W if kind == 'whip' else H) * 30 * p * p * (1 - p) * (1 - p) / (2 * TRANS_H)
        sig = min(80.0, speed * 0.32)
        tmp = _aux(2); tc = tmp.getCanvas(); tc.clear(lib.C(lib.CREAM))
        if kind == 'whip':
            tc.drawImage(imA, -W * e, 0); tc.drawImage(imB, W * (1 - e), 0)
            blur = skia.ImageFilters.Blur(sig, sig * 0.05, skia.TileMode.kClamp)
        else:
            tc.drawImage(imA, 0, -H * e); tc.drawImage(imB, 0, H * (1 - e))
            blur = skia.ImageFilters.Blur(sig * 0.05, sig, skia.TileMode.kClamp)
        pt = skia.Paint(); pt.setImageFilter(blur)
        c.clear(lib.C(lib.CREAM)); c.drawImage(tmp.makeImageSnapshot(), 0, 0, lin, pt)
    elif kind == 'zoom':
        c.clear(lib.C(lib.CREAM))
        if p < 0.5:
            q = p / 0.5; z = 1 + 0.85 * q * q; sig = 26 * q; im = imA
        else:
            q = (p - 0.5) / 0.5; z = 1.45 - 0.45 * (1 - (1 - q) ** 2); sig = 26 * (1 - q); im = imB
        pt = skia.Paint(); pt.setImageFilter(skia.ImageFilters.Blur(sig, sig, skia.TileMode.kClamp))
        c.save(); c.translate(540, 900); c.scale(z, z); c.translate(-540, -900)
        c.drawImage(im, 0, 0, lin, pt); c.restore()
        fl = 1 - abs(p - 0.5) / 0.2
        if fl > 0: c.drawRect(skia.Rect.MakeWH(W, H), lib.P('#FFFFFF', 110 * fl))
    elif kind == 'wipe':
        BW, tn = 120, math.tan(math.radians(14))
        lead = -280 + (W + 560 + 4 * BW) * p
        def region(e):
            pth = skia.Path(); pth.moveTo(-2000, -20); pth.lineTo(e + (-20 - 960) * tn, -20); pth.lineTo(e + (H + 20 - 960) * tn, H + 20); pth.lineTo(-2000, H + 20); pth.close()
            return pth
        c.clear(lib.C(lib.CREAM)); c.drawImage(imA, 0, 0)
        for k, col in enumerate((lib.YEL, lib.CORAL, lib.SKY, lib.NAVY)):
            r = region(lead - k * BW); c.drawPath(r, lib.P(col)); c.drawPath(r, lib.P(lib.NAVY, 255, 6))
        c.save(); c.clipPath(region(lead - 4 * BW), doAntiAlias=True); c.drawImage(imB, 0, 0); c.restore()
    else:
        c.drawImage(imB if p >= 0.5 else imA, 0, 0)


def draw_frame(surf, ep, tl, i, t):
    f = int(round(t * lib.FPS)); g = tl.F0[i] + f
    lib.set_clock(g / lib.FPS, tl.TOTAL, g)
    c = surf.getCanvas()
    tr = None
    if i < tl.n - 1 and f >= tl.frames[i] - TRANS_H and tl.TR[i] != 'cut': tr = (tl.TR[i], i, f - tl.frames[i])
    elif i > 0 and f < TRANS_H and tl.TR[i - 1] != 'cut': tr = (tl.TR[i - 1], i - 1, f)
    if tr is None:
        scene_into(c, ep, tl, i, t)
    else:
        kind, a, j = tr
        p = (j + TRANS_H + 0.5) / (2 * TRANS_H)
        tA = t if i == a else (tl.frames[a] - 1) / lib.FPS
        tB = t if i == a + 1 else 0.0
        sa, sb = _aux(0), _aux(1)
        scene_into(sa.getCanvas(), ep, tl, a, tA); scene_into(sb.getCanvas(), ep, tl, a + 1, tB)
        composite(c, kind, p, sa.makeImageSnapshot(), sb.makeImageSnapshot())
    post = getattr(ep, 'POST', True)
    if post:
        kw = post if isinstance(post, dict) else {}
        lib.post(c, **kw)
    lib.caption(c, tl.CAPT[i], t)


def render_scene(ep_dir, i):
    ep = load_episode(ep_dir); build = os.path.join(ep_dir, 'build')
    tl = Timeline(ep, json.load(open(os.path.join(build, 'vo_info.json'))))
    out = os.path.join(build, f'scene{i + 1:02d}.mp4'); tmp = out[:-4] + '.tmp.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{lib.W}x{lib.H}',
                           '-r', str(lib.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'superfast', '-crf', '17',
                           '-pix_fmt', 'yuv420p', '-r', str(lib.FPS), tmp], stdin=subprocess.PIPE)
    import skia
    surf = skia.Surface(lib.W, lib.H)
    for f in range(tl.frames[i]):
        draw_frame(surf, ep, tl, i, f / lib.FPS)
        pr.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    pr.stdin.close()
    if pr.wait() == 0: os.replace(tmp, out)
    else: raise SystemExit(f'scene {i + 1} failed')


# ------------------------------------------------------------------ audio
def mix(ep, tl, vo, build, seed=0):
    from scipy.signal import resample_poly
    SR = fx.SR; N = int(round(tl.TOTAL * SR))
    v = np.zeros(N); s = np.zeros(N)
    g = math.gcd(SR, vo['sr'])
    for i in range(tl.n):
        a = np.load(os.path.join(build, f'vo{i + 1:02d}.npy')) / 32768.0
        fx.put(v, tl.START[i] + tl.LEAD[i], resample_poly(a, SR // g, vo['sr'] // g))
    ep.sfx_cues(lambda t, x, gain=1.0: fx.put(s, t, x, gain), tl.START, tl.K, tl.DUR, fx)
    # automatic whoosh on every scene transition
    if getattr(ep, 'TRANSITION_SFX', True):
        for k, kind in enumerate(tl.TR):
            if kind == 'cut': continue
            tb = tl.F0[k + 1] / lib.FPS
            x = fx.transition_whoosh(kind)
            fx.put(s, max(0, tb - len(x) / SR * 0.55), x, 0.55)
    # ambience beds per scene (crossfaded, lightly ducked)
    amb = np.zeros(N)
    beds = getattr(ep, 'AMBIENCE', None)
    if beds:
        for i, b in enumerate(beds[:tl.n]):
            if not b: continue
            name, g = (b, 1.0) if isinstance(b, str) else b
            t0 = max(0, tl.START[i] - 0.25); d = tl.DUR[i] + 0.5
            x = fx.ambience(name, d, seed=i)
            fo = int(0.25 * SR); env = np.ones(len(x)); env[:fo] = np.linspace(0, 1, fo); env[-fo:] = np.linspace(1, 0, fo)
            fx.put(amb, t0, x * env, g)
        amb = fx.duck(amb, v, 0.35)
    m = fx.duck(fx.music_bed(tl.TOTAL + 1, seed)[:N], v)
    full = fx.hp(v, 90) + s * 0.3 + m * 0.16 + amb * 0.22
    full = full / max(1e-9, np.max(np.abs(full))) * 0.89
    p = os.path.join(build, 'mix.wav')
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((full * 32767).astype(np.int16).tobytes()); w.close()
    return p


def build_all(ep_dir, procs=2):
    T0 = time.time()
    ep = load_episode(ep_dir); build = os.path.join(ep_dir, 'build'); os.makedirs(build, exist_ok=True)
    assert len(ep.LINES) == len(ep.CAPS) == len(ep.SCENES), 'LINES, CAPS and SCENES must have the same length'
    vo = tts(ep, build); tl = Timeline(ep, vo)
    print('scene durations', [round(d, 2) for d in tl.DUR], 'total', round(tl.TOTAL, 2), flush=True)
    order = sorted(range(tl.n), key=lambda i: -tl.frames[i])
    buckets = [order[k::procs] for k in range(procs)]
    ps = [subprocess.Popen([sys.executable, __file__, ep_dir, 'scenes'] + [str(i) for i in b]) for b in buckets]
    if any(p.wait() for p in ps): raise SystemExit('render failed')
    print('render', round(time.time() - T0, 1), 's', flush=True)
    lst = os.path.join(build, 'list.txt')
    open(lst, 'w').write(''.join(f"file 'scene{i + 1:02d}.mp4'\n" for i in range(tl.n)))
    vid = os.path.join(build, 'video_only.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid], check=True)
    wav = mix(ep, tl, vo, build, seed=sum(map(ord, ep.META['id'])))
    final = os.path.join(build, 'final.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', final], check=True)
    print('mux+mix', round(time.time() - T0, 1), 's', flush=True)
    # browser uploads are capped at 3.8 MB -> 2-pass encode at a bitrate that lands just below 3.6 MB
    up = os.path.join(build, 'upload.mp4'); crf = '2pass'
    abr = 128
    for target in (3.45e6, 3.3e6, 3.1e6):
        vbr = int(target * 8 / tl.TOTAL / 1000) - abr - 12
        common = ['-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{vbr}k', '-pix_fmt', 'yuv420p', '-tune', 'animation']
        plog = os.path.join(build, 'x264pass')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', final] + common + ['-pass', '1', '-passlogfile', plog, '-an', '-f', 'mp4', os.devnull], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', final] + common + ['-pass', '2', '-passlogfile', plog, '-c:a', 'aac', '-b:a', f'{abr}k',
                        '-movflags', '+faststart', up], check=True)
        if os.path.getsize(up) < 3.6e6: break
    for f in os.listdir(build):
        if f.startswith('x264pass'): os.remove(os.path.join(build, f))
    # QA contact sheet: middle frame of every scene
    from PIL import Image
    tiles = []
    for i in range(tl.n):
        t = tl.START[i] + tl.DUR[i] * 0.6
        pth = os.path.join(build, f'qa{i + 1:02d}.png')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.2f}', '-i', final, '-frames:v', '1', '-vf', 'scale=216:384', pth], check=True)
        tiles.append(Image.open(pth))
    sheet = Image.new('RGB', (216 * 6, 384 * math.ceil(tl.n / 6)), 'white')
    for k, im in enumerate(tiles): sheet.paste(im, ((k % 6) * 216, (k // 6) * 384))
    sheet.save(os.path.join(build, 'contact.png'))
    for f in os.listdir(build):
        if f.startswith('qa') or f.startswith('scene') or f in ('video_only.mp4', 'list.txt'): os.remove(os.path.join(build, f))
    print('DONE', final, round(tl.TOTAL, 2), 's | upload copy', round(os.path.getsize(up) / 1e6, 2), 'MB | build',
          round(time.time() - T0, 1), 's', flush=True)


if __name__ == '__main__':
    ep_dir = os.path.abspath(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else 'build'
    if mode == 'scenes':
        for a in sys.argv[3:]: render_scene(ep_dir, int(a))
    elif mode == 'test':
        import skia
        ep = load_episode(ep_dir); build = os.path.join(ep_dir, 'build'); os.makedirs(build, exist_ok=True)
        tl = Timeline(ep, tts(ep, build))
        for spec in sys.argv[3:]:
            i, t = spec.split('@'); i = int(i) - 1; t = float(t)
            surf = skia.Surface(lib.W, lib.H); draw_frame(surf, ep, tl, i, t)
            surf.makeImageSnapshot().save(os.path.join(build, f'test_s{i + 1:02d}_{t:.2f}.png'), skia.kPNG)
        print('durations', [round(d, 2) for d in tl.DUR])
    else:
        build_all(ep_dir)
