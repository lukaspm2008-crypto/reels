"""Reel engine runner.

usage:
  python3 engine/run.py episodes/<id>            full build -> episodes/<id>/build/final.mp4 + upload.mp4 + contact.png
  python3 engine/run.py episodes/<id> test 3@1.2 8@0.5   render single frames (scene@seconds) to build/test_*.png

An episode folder holds episode.py with: META, VOICE, SPEED, LINES (one per scene), CAPS (caption blocks per scene),
optional TAIL / DESIGN_DUR, SCENES (list of scene functions f(canvas, t, D)), sfx_cues(put, S, K, D, fx).
"""
import os, sys, json, math, subprocess, importlib.util, wave
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
        self.TOTAL = sum(self.frames) / lib.FPS

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


def draw_frame(surf, ep, tl, i, t):
    c = surf.getCanvas(); c.clear(lib.C(lib.CREAM))
    c.save(); ep.SCENES[i](c, t / tl.K[i], tl.DESIGN[i]); c.restore()
    lib.caption(c, tl.CAPT[i], t)


def render_scene(ep_dir, i):
    ep = load_episode(ep_dir); build = os.path.join(ep_dir, 'build')
    tl = Timeline(ep, json.load(open(os.path.join(build, 'vo_info.json'))))
    out = os.path.join(build, f'scene{i + 1:02d}.mp4'); tmp = out[:-4] + '.tmp.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{lib.W}x{lib.H}',
                           '-r', str(lib.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
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
    m = fx.duck(fx.music_bed(tl.TOTAL + 1, seed)[:N], v)
    full = fx.hp(v, 90) + s * 0.3 + m * 0.16
    full = full / max(1e-9, np.max(np.abs(full))) * 0.89
    p = os.path.join(build, 'mix.wav')
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((full * 32767).astype(np.int16).tobytes()); w.close()
    return p


def build_all(ep_dir, procs=2):
    ep = load_episode(ep_dir); build = os.path.join(ep_dir, 'build'); os.makedirs(build, exist_ok=True)
    assert len(ep.LINES) == len(ep.CAPS) == len(ep.SCENES), 'LINES, CAPS and SCENES must have the same length'
    vo = tts(ep, build); tl = Timeline(ep, vo)
    print('scene durations', [round(d, 2) for d in tl.DUR], 'total', round(tl.TOTAL, 2), flush=True)
    order = sorted(range(tl.n), key=lambda i: -tl.frames[i])
    buckets = [order[k::procs] for k in range(procs)]
    ps = [subprocess.Popen([sys.executable, __file__, ep_dir, 'scenes'] + [str(i) for i in b]) for b in buckets]
    if any(p.wait() for p in ps): raise SystemExit('render failed')
    lst = os.path.join(build, 'list.txt')
    open(lst, 'w').write(''.join(f"file 'scene{i + 1:02d}.mp4'\n" for i in range(tl.n)))
    vid = os.path.join(build, 'video_only.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid], check=True)
    wav = mix(ep, tl, vo, build, seed=sum(map(ord, ep.META['id'])))
    final = os.path.join(build, 'final.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', final], check=True)
    # browser uploads are capped at 3.8 MB -> make a copy below 3.6 MB
    up = os.path.join(build, 'upload.mp4')
    for crf in (27, 29, 31, 33, 35):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', final, '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf),
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', up], check=True)
        if os.path.getsize(up) < 3.6e6: break
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
    print('DONE', final, round(tl.TOTAL, 2), 's | upload copy', round(os.path.getsize(up) / 1e6, 2), 'MB', flush=True)


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
