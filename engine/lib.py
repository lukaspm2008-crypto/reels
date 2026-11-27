"""Reel engine: shared drawing library (style-lock, characters, props, text).
Episodes do `from lib import *` and define their own scene functions.

Engine v2 ("Liebe im Detail"): characters get contact shadows, 2-tone shading and automatic idle life (blink, breathing,
sway) driven by the global clock NOW that run.py sets every frame. Idle cycles are quantised to the loop length LOOP so the
loop seam stays seamless. See RUNBOOK 2b "Engine features" for the helper list."""
import skia, math, os
from contextlib import contextmanager
W, H, FPS = 1080, 1920, 30
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ---------------------------------------------------------------- style
def C(h, a=255):
    return skia.Color(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), int(max(0, min(255, a))))


CREAM, CORAL, SKY, YEL, NAVY = '#FFF4E0', '#FF6B5B', '#4FC3F7', '#FFD54F', '#1E2A47'
MUSTARD, FLOOR, WOOD, GREY = '#F2B630', '#F6E3C4', '#C98B4E', '#B7C0CF'
SAGE, LEAF, TERRA = '#7FB7A4', '#5E9C88', '#E07A5F'
SKINS = ['#F5C6A5', '#D9A07A', '#A86B4A', '#F0D2B8', '#C68863']
HAIRS = ['#3B2A20', '#1E2A47', '#E0B04A', '#6B3E26', '#2B2B2B']
HOODS = ['#6C8EBF', '#8FA3BF', '#7FB7A4', '#A99BC9', '#88A9C9']

F_OST = skia.Typeface.MakeFromFile(os.path.join(_ROOT, 'assets/fonts/InterDisplay-Black.otf'))
F_CAP = skia.Typeface.MakeFromFile(os.path.join(_ROOT, 'assets/fonts/Poppins-Bold.ttf'))


def P(col, a=255, stroke=None):
    p = skia.Paint(AntiAlias=True, Color=C(col, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def tint(col, f):
    """f < 1 darkens (toward a navy-ish shadow), f > 1 lightens toward white. Returns hex."""
    r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)
    if f <= 1:  # multiply toward a cool shadow so shades stay in palette mood
        sr, sg, sb = 30, 42, 71
        k = 1 - f
        r, g, b = r + (sr - r) * k * 1.4, g + (sg - g) * k * 1.4, b + (sb - b) * k * 1.4
    else:
        k = f - 1
        r, g, b = r + (255 - r) * k, g + (255 - g) * k, b + (255 - b) * k
    cl = lambda v: int(max(0, min(255, v)))
    return '#%02X%02X%02X' % (cl(r), cl(g), cl(b))


def blurred(col, a, sigma):
    p = P(col, a)
    if sigma > 0.3: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eout(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def einout(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x


def ein(x):
    x = clamp(x); return x ** 3


def eback(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ebounce(x):
    x = clamp(x); n1, d1 = 7.5625, 2.75
    if x < 1 / d1: return n1 * x * x
    if x < 2 / d1: x -= 1.5 / d1; return n1 * x * x + .75
    if x < 2.5 / d1: x -= 2.25 / d1; return n1 * x * x + .9375
    x -= 2.625 / d1; return n1 * x * x + .984375


def squash(u, amt=0.16):
    """squash & stretch pair (sx, sy) for a pop-in; u = 0..1 progress. Overshoots like eback and wobbles."""
    if u <= 0: return 0.0, 0.0
    k = eback(u); u = clamp(u)
    w = math.sin(u * math.pi * 2.0) * (1 - u) * amt
    return k * (1 - w), k * (1 + w)


def rrect(c, x0, y0, x1, y1, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r), paint)


def outlined(draw, fill, sw):
    draw(P(fill)); draw(P(NAVY, 255, sw))


def cam(c, z, fx, fy, cx=540, cy=960):
    c.translate(cx, cy); c.scale(z, z); c.translate(-fx, -fy)


# ---------------------------------------------------------------- global clock (run.py sets it every frame)
NOW = 0.0     # seconds since the start of the video (continuous across scenes)
LOOP = 0.0    # total video length; idle cycles are quantised to it -> seamless loop seam
FRAME = 0


def set_clock(now, loop=None, frame=0):
    global NOW, LOOP, FRAME
    NOW = now; FRAME = frame
    if loop is not None: LOOP = loop


def qf(f):
    """frequency (Hz) quantised so a whole number of cycles fits the loop"""
    if LOOP > 0: return max(1, round(f * LOOP)) / LOOP
    return f


def osc(f, ph=0.0, t=None):
    """seamless idle oscillator in -1..1 driven by the global clock"""
    return math.sin(2 * math.pi * qf(f) * (NOW if t is None else t) + ph)


def loop_drift(speed, length, t=None):
    """offset 0..length that moves at ~speed px/s and wraps seamlessly at the loop seam (clouds, motes, scrolling)"""
    if length <= 0: return 0.0
    tt = NOW if t is None else t
    if LOOP > 0:
        cyc = max(1, round(abs(speed) * LOOP / length)) * (1 if speed >= 0 else -1)
        return (tt / LOOP * cyc * length) % length
    return (tt * speed) % length


def rnd(*a):
    """deterministic hash -> 0..1"""
    s = 0.0
    for k, v in enumerate(a): s += (k + 1) * 12.9898 * (v + 0.137 * k) + 3.17 * k
    return (math.sin(s + 78.233) * 43758.5453) % 1.0


def blink_amt(seed=0.0, t=None):
    """0..1 eyelid closure; a blink every 2-4 s per character, none right at the loop seam"""
    t = NOW if t is None else t
    if LOOP > 0 and (t < 0.35 or t > LOOP - 0.35): return 0.0
    per = 3.0; off = (seed * 1.37) % per
    k = math.floor((t - off) / per)
    best = 0.0
    for kk in (k - 1, k, k + 1):
        tb = kk * per + off + 0.5 + rnd(kk, seed) * 1.0
        best = max(best, clamp(1 - abs(t - tb) / 0.075))
    return best


def eye_drift(seed=0.0, amp=0.14):
    """small saccades (look offset) that change every ~1.7 s"""
    if LOOP > 0 and (NOW < 0.3 or NOW > LOOP - 0.3): return 0.0, 0.0
    per = 1.7; tt = NOW + seed * 0.61; k = math.floor(tt / per); f = clamp((tt - k * per) / 0.1)
    a = ((rnd(k - 1, seed) - .5) * 2 * amp, (rnd(k - 1, seed + 9) - .5) * amp)
    b = ((rnd(k, seed) - .5) * 2 * amp, (rnd(k, seed + 9) - .5) * amp)
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def _seed_of(*cols):
    return sum(int(col[1:], 16) % 997 for col in cols if isinstance(col, str) and col.startswith('#')) / 97.0


# ---------------------------------------------------------------- depth helpers
def contact_shadow(c, x, y, w, h=None, a=70, blur=None):
    """soft ellipse shadow on the ground centred at (x, y)"""
    h = h if h is not None else w * 0.16
    c.drawOval(skia.Rect.MakeLTRB(x - w / 2, y - h / 2, x + w / 2, y + h / 2), blurred(NAVY, a, blur if blur is not None else h * 0.35))


def box_shadow(c, x0, y0, x1, y1, r=16, dy=14, blur=16, a=60, dx=0):
    """soft drop shadow for cards / plates"""
    rrect(c, x0 + dx, y0 + dy, x1 + dx, y1 + dy, r, blurred(NAVY, a, blur))


def shaded_rrect(c, x0, y0, x1, y1, r, col, sw=6, shade=0.86, hi=True, shadow=False, side='r'):
    """2-tone shaded rounded box: base, darker side/bottom crescent, light top edge, navy outline"""
    if shadow: box_shadow(c, x0, y0, x1, y1, r, dy=12, blur=12, a=55)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r)
    c.drawRRect(rr, P(col))
    c.save(); c.clipRRect(rr, True)
    w, h = x1 - x0, y1 - y0; sc = P(tint(col, shade))
    if side == 'r':
        c.drawOval(skia.Rect.MakeLTRB(x0 + w * 0.62, y0 - h * 0.3, x1 + w * 0.9, y1 + h * 0.4), sc)
        c.drawRect(skia.Rect.MakeLTRB(x0, y1 - min(h * 0.12, 18), x1, y1), sc)
    else:  # bottom
        c.drawRect(skia.Rect.MakeLTRB(x0, y0 + h * 0.62, x1, y1), sc)
    if hi:
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + min(h * 0.14, 16)), P('#FFFFFF', 70))
    c.restore()
    if sw: c.drawRRect(rr, P(NAVY, 255, sw))


def shaded_circle(c, x, y, r, col, sw=6, shade=0.86, hi=True):
    c.drawCircle(x, y, r, P(tint(col, shade)))
    c.save(); pth = skia.Path(); pth.addCircle(x, y, r); c.clipPath(pth, doAntiAlias=True)
    c.drawCircle(x - r * 0.16, y - r * 0.16, r * 0.98, P(col))
    if hi: c.drawCircle(x - r * 0.42, y - r * 0.42, r * 0.22, P('#FFFFFF', 90))
    c.restore()
    if sw: c.drawCircle(x, y, r, P(NAVY, 255, sw))


def shaded_path(c, pth, col, sw=6, shade=0.86, light=(-1, -1), shift=0.12):
    """2-tone fill for an arbitrary path: darker copy, lighter copy offset toward the light, outline"""
    b = pth.computeTightBounds(); w, h = b.width(), b.height()
    c.drawPath(pth, P(tint(col, shade)))
    c.save(); c.clipPath(pth, doAntiAlias=True); c.translate(light[0] * w * shift, light[1] * h * shift)
    c.drawPath(pth, P(col)); c.restore()
    if sw: c.drawPath(pth, P(NAVY, 255, sw))


def glow(c, x, y, r, col=YEL, a=150):
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), max(1, r), [C(col, a), C(col, 0)]))
    c.drawCircle(x, y, r, g)


@contextmanager
def defocus(c, sigma=10, bounds=None):
    """draw an out-of-focus foreground element: with defocus(c, 12): plant(c, ...)"""
    p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma))
    c.saveLayer(skia.Rect.MakeLTRB(*bounds) if bounds else None, p)
    try: yield
    finally: c.restore()


# ---------------------------------------------------------------- characters
def head(c, x, y, r, skin, hair, look=(0, 0), eyes='dot', blush=False, sweat=False, mood='neutral', tuft=False,
         seed=None, idle=True, shade=True):
    s = r / 60
    seed = _seed_of(skin, hair) if seed is None else seed
    bl = blink_amt(seed) if idle else 0.0
    if idle:
        dx, dy = eye_drift(seed); look = (look[0] + dx, look[1] + dy)
    # face with 2-tone shading (light from upper left)
    if shade:
        c.drawCircle(x, y, r, P(tint(skin, 0.88)))
        c.save(); fp = skia.Path(); fp.addCircle(x, y, r); c.clipPath(fp, doAntiAlias=True)
        c.drawCircle(x - r * 0.13, y - r * 0.12, r * 0.99, P(skin))
        c.restore()
    else:
        c.drawCircle(x, y, r, P(skin))
    # hair cap
    if hair:
        path = skia.Path()
        path.addArc(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), 190, 160)
        path.close()
        c.drawPath(path, P(hair))
        if tuft:
            tw = osc(0.45, seed) * 3 * s if idle else 0
            t = skia.Path(); t.moveTo(x - 8 * s, y - r + 4 * s); t.quadTo(x + 5 * s + tw, y - r - 34 * s, x + 30 * s + tw * 1.6, y - r - 22 * s)
            t.quadTo(x + 18 * s + tw, y - r - 4 * s, x + 22 * s, y - r + 8 * s); t.close(); c.drawPath(t, P(hair))
        if shade:  # hair shine
            c.drawArc(skia.Rect.MakeLTRB(x - r * 0.78, y - r * 0.78, x + r * 0.78, y + r * 0.78), 214, 34, False, P('#FFFFFF', 55, 6 * s))
    c.drawCircle(x, y, r, P(NAVY, 255, 6 * s))
    lx, ly = look
    if eyes == 'dot':
        for dx in (-21, 21):
            ex, ey = x + (dx + lx * 7) * s, y + (6 + ly * 6) * s
            if bl > 0.45:
                c.drawLine(ex - 8 * s, ey + 1 * s, ex + 8 * s, ey + 1 * s, P(NAVY, 255, 4.5 * s))
            else:
                c.drawCircle(ex, ey, 7.5 * s, P(NAVY))
                if shade: c.drawCircle(ex + 2.6 * s, ey - 2.6 * s, 2.3 * s, P('#FFFFFF', 230))
    else:  # big staring eyes
        for dx in (-23, 23):
            ex, ey = x + dx * s, y + 4 * s
            c.drawCircle(ex, ey, 17 * s, P('#FFFFFF'))
            c.drawCircle(ex + (dx * 0 + lx * 8) * s, ey + ly * 8 * s, 8 * s, P(NAVY))
            if shade: c.drawCircle(ex + (lx * 8 + 3) * s, ey + (ly * 8 - 3) * s, 2.6 * s, P('#FFFFFF'))
            if bl > 0:
                c.save(); ep = skia.Path(); ep.addCircle(ex, ey, 17 * s); c.clipPath(ep, doAntiAlias=True)
                c.drawRect(skia.Rect.MakeLTRB(ex - 18 * s, ey - 18 * s, ex + 18 * s, ey - 17 * s + 34 * s * bl), P(skin))
                c.restore()
            c.drawCircle(ex, ey, 17 * s, P(NAVY, 255, 4 * s))
    if blush:
        for dx in (-34, 34):
            c.drawOval(skia.Rect.MakeXYWH(x + dx * s - 12 * s, y + 22 * s, 24 * s, 12 * s), P('#FF8FA3', 200))
    m = skia.Path()
    if mood == 'smile':
        m.moveTo(x - 14 * s, y + 30 * s); m.quadTo(x, y + 42 * s, x + 14 * s, y + 30 * s)
        c.drawPath(m, P(NAVY, 255, 4.5 * s))
    elif mood == 'worried':
        m.moveTo(x - 12 * s, y + 38 * s); m.quadTo(x, y + 30 * s, x + 12 * s, y + 38 * s)
        c.drawPath(m, P(NAVY, 255, 4.5 * s))
    elif mood == 'o':
        c.drawOval(skia.Rect.MakeXYWH(x - 7 * s, y + 28 * s, 14 * s, 16 * s), P(NAVY))
    if sweat:
        d = skia.Path(); sx, sy = x + r * 0.78, y - r * 0.25 + (osc(1.3, seed) + 1) * 3 * s
        d.moveTo(sx, sy - 18 * s); d.quadTo(sx + 12 * s, sy + 2 * s, sx, sy + 8 * s); d.quadTo(sx - 12 * s, sy + 2 * s, sx, sy - 18 * s)
        c.drawPath(d, P(SKY)); c.drawPath(d, P(NAVY, 255, 3 * s))
        c.drawCircle(sx - 3 * s, sy - 2 * s, 2.5 * s, P('#FFFFFF', 220))


def person(c, x, y, s, hood, skin, hair, look=(0, 0), eyes='dot', walk=0.0, blush=False, sweat=False,
           mood='neutral', tuft=False, lamp=False, lamp_on=False, shirt=None, seed=None, idle=True, shadow=True):
    """standing figure, (x,y) = feet baseline centre. idle=True adds breathing, sway and blinking (global clock)."""
    sw = 6 * s
    seed = _seed_of(hood, skin, hair) if seed is None else seed
    br = (osc(0.27, seed) + 1) / 2 if idle else 0.0          # breathing 0..1
    sway = osc(0.16, seed * 2) if idle else 0.0
    bounce = abs(math.sin(walk)) * 7 * s if walk else 0.0
    by = -3.5 * s * br - bounce                                # body lift
    hx = x + 2.5 * s * sway                                    # head sway
    if shadow:
        contact_shadow(c, x, y - 2 * s, 200 * s, 30 * s, a=70)
    # legs
    for i, dx in enumerate((-30, 30)):
        lift = max(0, math.sin(walk + i * math.pi)) * 18 * s
        sh = math.sin(walk + i * math.pi) * 14 * s
        rrect(c, x + dx * s - 19 * s + sh, y - 95 * s - lift + by * 0.3, x + dx * s + 19 * s + sh, y - lift - 8 * s, 18 * s, P(NAVY))
        so = skia.Rect.MakeLTRB(x + dx * s - 30 * s + sh, y - 26 * s - lift, x + dx * s + 30 * s + sh, y - lift)
        c.drawOval(so, P('#FFFFFF'))
        c.save(); c.clipRect(skia.Rect.MakeLTRB(so.left(), so.top() + so.height() * 0.62, so.right(), so.bottom() + 2))
        c.drawOval(so, P('#D5DBE6')); c.restore()
        c.drawOval(so, P(NAVY, 255, 4 * s))
    # lamp pole behind body
    if lamp:
        px = x + 58 * s
        c.drawLine(px, y - 200 * s, px, y - 520 * s, P('#5A6478', 255, 8 * s))
        lp = skia.Path()
        lx, ly = px, y - 520 * s
        lp.moveTo(lx - 10 * s, ly - 26 * s); lp.lineTo(lx + 20 * s, ly - 30 * s); lp.lineTo(lx + 8 * s, ly + 20 * s); lp.lineTo(lx - 40 * s, ly + 14 * s); lp.close()
        c.drawPath(lp, P(CORAL)); c.drawPath(lp, P(NAVY, 255, 4 * s))
        c.drawCircle(lx - 16 * s, ly + 18 * s, 11 * s, P('#FFF7C2' if lamp_on else '#8A8F9C'))
    # arms
    armc = hood if shirt is None else shirt
    for dx, sg in ((-78, -1), (78, 1)):
        asw = math.sin(walk + (0 if sg < 0 else math.pi)) * 12 * s + (sg * 1.5 * s * br)
        sx0, sy0 = x + dx * s * 0.85, y - 225 * s + by
        hx1, hy1 = x + dx * s + asw, y - 120 * s + by * 0.5
        c.drawLine(sx0, sy0, hx1, hy1, P(NAVY, 255, 38 * s))
        c.drawLine(sx0, sy0, hx1, hy1, P(armc if sg < 0 else tint(armc, 0.9), 255, 26 * s))
        c.drawCircle(hx1, hy1 + 8 * s, 14 * s, P(skin)); c.drawCircle(hx1, hy1 + 8 * s, 14 * s, P(NAVY, 255, 4 * s))
    # body (2-tone)
    bc = hood if shirt is None else shirt
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 78 * s, y - 250 * s + by, x + 78 * s, y - 82 * s), 46 * s, 46 * s)
    c.drawRRect(rr, P(bc))
    c.save(); c.clipRRect(rr, True)
    c.drawOval(skia.Rect.MakeLTRB(x + 22 * s, y - 330 * s, x + 190 * s, y - 20 * s), P(tint(bc, 0.86)))
    c.drawRect(skia.Rect.MakeLTRB(x - 80 * s, y - 100 * s, x + 80 * s, y - 80 * s), P(tint(bc, 0.86)))
    c.drawOval(skia.Rect.MakeLTRB(x - 66 * s, y - 244 * s + by, x - 30 * s, y - 200 * s + by), P('#FFFFFF', 55))
    c.restore()
    c.drawRRect(rr, P(NAVY, 255, sw))
    if shirt is None:  # hood collar, pocket + strings
        rrect(c, x - 52 * s, y - 262 * s + by, x + 52 * s, y - 230 * s + by, 16 * s, P(tint(bc, 0.88)))
        rrect(c, x - 52 * s, y - 262 * s + by, x + 52 * s, y - 230 * s + by, 16 * s, P(NAVY, 255, 4 * s))
        rrect(c, x - 40 * s, y - 150 * s, x + 40 * s, y - 108 * s, 14 * s, P(NAVY, 60))
        c.drawLine(x - 40 * s, y - 150 * s, x + 40 * s, y - 150 * s, P(NAVY, 90, 3 * s))
        ss = 3 * s * osc(0.55, seed) + 2 * s * sway
        for sg in (-1, 1):
            x0s = x + sg * 14 * s
            c.drawLine(x0s, y - 238 * s + by, x0s + sg * 2 * s + ss, y - 200 * s + by, P('#FFFFFF', 230, 5 * s))
            c.drawCircle(x0s + sg * 2 * s + ss, y - 198 * s + by, 4 * s, P('#FFFFFF'))
    head(c, hx, y - 310 * s + by * 1.15, 62 * s, skin, hair, look, eyes, blush, sweat, mood, tuft, seed=seed, idle=idle)


def mika(c, x, y, s, **kw):
    kw.setdefault('tuft', True)
    kw.setdefault('seed', 1.0)
    person(c, x, y, s, MUSTARD, '#F5C6A5', '#2A2233', **kw)


def bust(c, x, y, s, hood, skin, hair, look=(0, 0), eyes='dot', mood='neutral', glow=0.0, seed=None, idle=True):
    """head + shoulders; (x,y) = shoulder base"""
    seed = _seed_of(hood, skin, hair) + (x * 0.013 + y * 0.007) % 5 if seed is None else seed
    br = (osc(0.27, seed) + 1) / 2 if idle else 0.0
    if glow > 0:
        g = skia.Paint(AntiAlias=True)
        g.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y - 110 * s), 190 * s,
                    [C(YEL, int(200 * glow)), C(YEL, 0)]))
        c.drawCircle(x, y - 110 * s, 190 * s, g)
    pth = skia.Path(); pth.moveTo(x - 95 * s, y); pth.cubicTo(x - 95 * s, y - 110 * s - 3 * s * br, x + 95 * s, y - 110 * s - 3 * s * br, x + 95 * s, y); pth.close()
    shaded_path(c, pth, hood, 6 * s, 0.86, light=(-1, -0.4), shift=0.14)
    head(c, x + 1.5 * s * osc(0.15, seed), y - 140 * s - 3 * s * br, 58 * s, skin, hair, look, eyes, mood=mood, seed=seed, idle=idle)


def beam(c, x0, y0, w0, x1, y1, w1, a=1.0):
    pth = skia.Path(); pth.moveTo(x0 - w0 / 2, y0); pth.lineTo(x0 + w0 / 2, y0); pth.lineTo(x1 + w1 / 2, y1); pth.lineTo(x1 - w1 / 2, y1); pth.close()
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [C('#FFF6C8', int(210 * a)), C(YEL, int(110 * a))]))
    c.drawPath(pth, p)
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial(skia.Point(x1, y1), w1 * 0.75, [C('#FFF6C8', int(200 * a)), C(YEL, 0)]))
    c.save(); c.translate(x1, y1); c.scale(1, 0.28); c.drawCircle(0, 0, w1 * 0.75, g); c.restore()


def dim(c, a):
    c.drawRect(skia.Rect.MakeWH(W, H), P(NAVY, a))


# ---------------------------------------------------------------- text
def parse(s):
    out = []; hl = False
    for i, part in enumerate(s.split('*')):
        if part:
            out.append((part, hl))
        hl = not hl
    return out


def draw_rich(c, s, cx, cy, size, font_tf, col, hlcol, max_w=None):
    font = skia.Font(font_tf, size)
    parts = parse(s)
    wtot = sum(font.measureText(p) for p, _ in parts)
    if max_w and wtot > max_w:
        size = size * max_w / wtot; font = skia.Font(font_tf, size)
        wtot = sum(font.measureText(p) for p, _ in parts)
    x = cx - wtot / 2
    # vertical centre via cap height approx
    y = cy + size * 0.36
    return font, parts, x, y, wtot, size


def ost(c, text, t, t0=0.12, y0=300):
    """on-screen headline: navy 2-tone plate with soft drop shadow, squash&stretch pop, words pop in one by one"""
    if t < t0: return
    u = t - t0
    sx, sy = squash(u / 0.3, 0.12)
    font, parts, x, y, wtot, size = draw_rich(c, text, 540, y0, 92, F_OST, '#FFFFFF', YEL, max_w=900)
    c.save(); c.translate(540, y0); c.rotate(-2.0); c.scale(sx, sy); c.translate(-540, -y0)
    pad = 34
    px0, py0, px1, py1 = x - pad, y0 - size * 0.62 - 14, x + wtot + pad, y0 + size * 0.62 + 6
    box_shadow(c, px0, py0, px1, py1, 26, dy=16, blur=14, a=80, dx=6)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(px0, py0, px1, py1), 26, 26)
    c.drawRRect(rr, P(NAVY))
    c.save(); c.clipRRect(rr, True)
    c.drawRect(skia.Rect.MakeLTRB(px0, py0, px1, py0 + (py1 - py0) * 0.48), P('#27365C'))
    c.drawRect(skia.Rect.MakeLTRB(px0, py1 - 7, px1, py1), P('#141C33'))
    c.restore()
    # words, staggered
    words = []
    for p, hl in parts:
        for tok in p.split(' '):
            if tok: words.append((tok, hl, x, font.measureText(tok)))
            x += font.measureText(tok + ' ')
        x -= font.measureText(' ')
    for n, (tok, hl, wx, ww) in enumerate(words):
        uk = (u - 0.06 - n * 0.065) / 0.2
        if uk <= 0: continue
        k = eback(uk); cxw = wx + ww / 2
        c.save(); c.translate(cxw, y - size * 0.36 + 14 * (1 - clamp(uk))); c.scale(k, k); c.translate(-cxw, -(y - size * 0.36))
        c.drawString(tok, wx, y + 5, font, P('#0E1426', 160))
        c.drawString(tok, wx, y, font, P(YEL if hl else '#FFFFFF'))
        c.restore()
    c.restore()


def caption(c, blocks, t):
    """blocks: list of (start_time, text) for the current scene; *word* = highlighted"""
    cur = None
    for k, (t0, b) in enumerate(blocks):
        if t >= t0 - 0.03: cur = (k, t0, b)
    if cur is None: return
    k, t0, b = cur
    pop = 0.86 + 0.14 * eback((t - t0) / 0.12)
    font, parts, x, y, wtot, size = draw_rich(c, b, 540, 1470, 74, F_CAP, '#FFFFFF', YEL, max_w=880)
    c.save(); c.translate(540, 1470); c.scale(pop, pop); c.translate(-540, -1470)
    box_shadow(c, x - 30, 1470 - 58, x + wtot + 30, 1470 + 52, 30, dy=10, blur=12, a=70)
    rrect(c, x - 30, 1470 - 58, x + wtot + 30, 1470 + 52, 30, P(NAVY, 242))
    for p, hl in parts:
        c.drawString(p, x, y, font, P(YEL if hl else '#FFFFFF'))
        x += font.measureText(p)
    c.restore()


def count(t, t0, dur, v0, v1, ease=None):
    """count-up value at time t (eased); format it yourself, e.g. f"{int(count(...))} %" """
    if t < t0: return v0
    e = (ease or eout)((t - t0) / dur)
    return v0 + (v1 - v0) * e


def count_ticks(t0, dur, v0, v1, ease=None, min_gap=0.045, step=1):
    """times (relative to the scene) where the counted integer changes -> put fx.tick() there"""
    out = []; last = None; lt = -9
    for k in range(int(dur * 240) + 2):
        tt = t0 + k / 240
        v = int(count(tt, t0, dur, v0, v1, ease) // step)
        if last is not None and v != last and tt - lt >= min_gap:
            out.append(tt); lt = tt
        last = v
    return out


def sticker(c, text, x, y, size=56, bg=YEL, fg=NAVY, k=1.0, rot=0.0, shape='pill', tf=None, sk=None):
    """die-cut sticker / badge: white border, soft shadow, 2-tone fill, shine. shape: pill | circle | burst | tag.
    k = scale (use squash() pair via sk=(sx, sy) for squash & stretch)."""
    if (sk is None and k <= 0) or (sk is not None and sk[0] <= 0): return
    f = skia.Font(tf or F_OST, size); w = f.measureText(text)
    c.save(); c.translate(x, y); c.rotate(rot)
    if sk: c.scale(*sk)
    else: c.scale(k, k)
    pth = skia.Path()
    if shape == 'circle':
        R = max(w / 2 + size * 0.45, size * 0.95); pth.addCircle(0, 0, R)
    elif shape == 'burst':
        R = max(w / 2 + size * 0.55, size * 1.05); n = 18
        for q in range(n * 2):
            rr = R * (1.0 if q % 2 == 0 else 0.86); a = math.pi * q / n
            (pth.moveTo if q == 0 else pth.lineTo)(rr * math.cos(a), rr * math.sin(a))
        pth.close()
    elif shape == 'tag':
        hw, hh = w / 2 + size * 0.45, size * 0.62
        pth.moveTo(-hw - hh * 0.8, 0); pth.lineTo(-hw, -hh); pth.lineTo(hw, -hh); pth.lineTo(hw, hh); pth.lineTo(-hw, hh); pth.close()
    else:
        hw, hh = w / 2 + size * 0.42, size * 0.64
        pth.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-hw, -hh, hw, hh), hh * 0.55, hh * 0.55))
    c.save(); c.translate(4, 12); c.drawPath(pth, blurred(NAVY, 80, 9)); c.restore()
    c.drawPath(pth, P('#FFFFFF', 255, size * 0.30))   # die-cut white border
    shaded_path(c, pth, bg, 0, 0.88, light=(0, -1), shift=0.1)
    c.save(); c.clipPath(pth, doAntiAlias=True)
    b = pth.computeTightBounds()
    sh = skia.Path(); sh.moveTo(b.left() + b.width() * 0.12, b.top()); sh.lineTo(b.left() + b.width() * 0.26, b.top())
    sh.lineTo(b.left() + b.width() * 0.1, b.bottom()); sh.lineTo(b.left() - b.width() * 0.04, b.bottom()); sh.close()
    c.drawPath(sh, P('#FFFFFF', 60))
    c.restore()
    c.drawPath(pth, P(NAVY, 255, 5))
    c.drawString(text, -w / 2, size * 0.35, f, P(fg))
    c.restore()


# ---------------------------------------------------------------- post pass (vignette + paper grain)
_VIG = {}
_PAPER = None


def vignette(c, a=64, cx=540, cy=900):
    key = (a, cx, cy)
    if key not in _VIG:
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), 1260, [C(NAVY, 0), C(NAVY, 0), C(NAVY, int(a * 0.45)), C(NAVY, a)],
                                                   [0.0, 0.5, 0.8, 1.0]))
        _VIG[key] = p
    c.drawRect(skia.Rect.MakeWH(W, H), _VIG[key])


def paper_image():
    """cached full-frame paper/grain texture (RGBA, mostly transparent)"""
    global _PAPER
    if _PAPER is None:
        import numpy as np
        rng = np.random.default_rng(11)
        fine = rng.standard_normal((H, W)).astype(np.float32)
        lo = rng.standard_normal((H // 24 + 2, W // 24 + 2)).astype(np.float32)
        lo = np.kron(lo, np.ones((24, 24), np.float32))[:H, :W]
        from scipy.ndimage import gaussian_filter
        lo = gaussian_filter(lo, 14)
        lo = lo / (np.abs(lo).max() + 1e-6)
        fib = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), (0.6, 5.0)); fib /= (np.abs(fib).max() + 1e-6)
        n = fine * 0.1 + lo * 1.3 + fib * 0.8      # mostly low-frequency paper mottling: looks crafted, compresses well
        a = np.clip(np.abs(n) * 6.5, 0, 17).astype(np.uint8)
        rgb = np.where(n[..., None] > 0, np.array([255, 255, 255], np.uint8), np.array([40, 34, 30], np.uint8))
        rgbp = (np.broadcast_to(rgb, (H, W, 3)).astype(np.uint16) * a[..., None] // 255).astype(np.uint8)   # premultiplied
        arr = np.ascontiguousarray(np.dstack([rgbp, a]).astype(np.uint8))
        _PAPER = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType).makeRasterImage()
    return _PAPER


def paper_texture(c, a=1.0):
    p = skia.Paint(); p.setAlphaf(a)
    c.drawImage(paper_image(), 0, 0, skia.SamplingOptions(), p)


_POST = {}


def post(c, vig=64, grain=1.0):
    """final look pass (run.py calls it on every frame): vignette + paper texture, baked once into one cached overlay"""
    key = (vig, grain)
    if key not in _POST:
        s = skia.Surface(W, H); sc = s.getCanvas(); sc.clear(skia.ColorTRANSPARENT)
        if vig: vignette(sc, vig)
        if grain: paper_texture(sc, grain)
        _POST[key] = s.makeImageSnapshot().makeRasterImage()
    c.drawImage(_POST[key], 0, 0)


# ---------------------------------------------------------------- backgrounds / environments
def bg(c, top, bot=None, y0=0, y1=H, x0=0, x1=W):
    """vertical gradient fill (bot defaults to a slightly darker top)"""
    bot = bot or tint(top, 0.94)
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [C(top), C(bot)]))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), g)


def radial_bg(c, inner, outer, cx=540, cy=820, r=1300):
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [C(inner), C(outer)]))
    c.drawRect(skia.Rect.MakeWH(W, H), g)


def sunburst(c, cx, cy, col, a=40, n=16, rot=0.0, r=2400):
    """rotating rays background (game-show / reveal energy)"""
    p = P(col, a)
    for k in range(n):
        a0 = math.radians(rot + k * 360 / n); a1 = a0 + math.radians(180 / n)
        pth = skia.Path(); pth.moveTo(cx, cy); pth.lineTo(cx + r * math.cos(a0), cy + r * math.sin(a0)); pth.lineTo(cx + r * math.cos(a1), cy + r * math.sin(a1)); pth.close()
        c.drawPath(pth, p)


def wall(c, x0, y0, x1, y1, col, pattern=None, pcol=None):
    """wall with light-top gradient; pattern: None | 'stripes' | 'dots' | 'panel' (wainscot lower third)"""
    bg(c, tint(col, 1.06), tint(col, 0.95), y0, y1, x0, x1)
    pc = pcol or tint(col, 0.96)
    c.save(); c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    if pattern == 'stripes':
        for x in range(int(x0) - 40, int(x1) + 40, 90): c.drawRect(skia.Rect.MakeLTRB(x, y0, x + 40, y1), P(pc, 120))
    elif pattern == 'dots':
        for j, y in enumerate(range(int(y0) + 30, int(y1), 70)):
            for x in range(int(x0) + 30 + (35 if j % 2 else 0), int(x1), 70): c.drawCircle(x, y, 5, P(pc, 170))
    elif pattern == 'panel':
        yp = y0 + (y1 - y0) * 0.62
        c.drawRect(skia.Rect.MakeLTRB(x0, yp, x1, y1), P(tint(col, 0.94)))
        c.drawRect(skia.Rect.MakeLTRB(x0, yp - 10, x1, yp + 8), P(tint(col, 1.12)))
        c.drawLine(x0, yp + 8, x1, yp + 8, P(NAVY, 60, 3))
        for x in range(int(x0) + 60, int(x1), 170):
            rrect(c, x, yp + 40, x + 120, y1 - 40, 8, P(tint(col, 0.9), 255, 4))
    c.restore()


def skirting(c, y, x0=-50, x1=W + 50, col='#FFFFFF', h=30):
    c.drawRect(skia.Rect.MakeLTRB(x0, y - h, x1, y), P(col))
    c.drawRect(skia.Rect.MakeLTRB(x0, y - h * 0.35, x1, y), P(tint(col, 0.9)))
    c.drawLine(x0, y - h, x1, y - h, P(NAVY, 255, 4))


def floor(c, y, col=FLOOR, kind='wood', x0=-300, x1=W + 300, vp_x=540, y1=H + 300, plank=130, skirt=True, skirt_col='#FFFFFF',
          line=True, scroll=0.0):
    """perspective floor from the wall line y down to the bottom: wood | tiles | carpet | concrete.
    Fills the lower part of the frame with detail (seams, AO band, lighter foreground)."""
    bg(c, tint(col, 0.9), tint(col, 1.05), y, y1, x0, x1)
    yh = y - 650.0                      # horizon
    sc = lambda yy: (yy - yh) / (y - yh)
    c.save(); c.clipRect(skia.Rect.MakeLTRB(x0, y, x1, y1))
    lc = P(tint(col, 0.8), 150, 3)
    rows = [y]
    z0, dz = 10.0, 0.75
    n = 1
    while rows[-1] < y1 and n < 40:
        z = z0 - dz * n
        if z <= 0.2: break
        rows.append(yh + (y - yh) * z0 / z); n += 1
    if kind in ('wood', 'tiles'):
        off = scroll % plank
        for k in range(-14, 15):
            xf = vp_x + k * plank - off
            xb = vp_x + (xf - vp_x) * sc(y1)
            c.drawLine(xf, y, xb, y1, lc)
        for r in range(len(rows) - 1):
            ya, yb = rows[r], rows[r + 1]
            if kind == 'tiles':
                c.drawLine(x0, yb, x1, yb, lc)
                if r % 2 == 0:
                    for k in range(-14, 15, 2):
                        xa = vp_x + (k * plank - off) * sc(ya); xb2 = vp_x + ((k + 1) * plank - off) * sc(ya)
                        xc = vp_x + ((k + 1) * plank - off) * sc(yb); xd = vp_x + (k * plank - off) * sc(yb)
                        pth = skia.Path(); pth.moveTo(xa, ya); pth.lineTo(xb2, ya); pth.lineTo(xc, yb); pth.lineTo(xd, yb); pth.close()
                        c.drawPath(pth, P(tint(col, 0.94), 130))
            else:  # staggered cross joints
                for k in range(-14, 15):
                    if (k + r) % 3: continue
                    xm = vp_x + ((k + 0.5) * plank - off) * sc((ya + yb) / 2)
                    c.drawLine(xm - 0 * plank, ya, xm, yb, P(tint(col, 0.8), 0))
                    xj = vp_x + (k * plank - off) * sc(yb)
                    xj2 = vp_x + ((k + 1) * plank - off) * sc(yb)
                    c.drawLine(xj, yb, xj2, yb, lc)
                # subtle grain
                for k in range(-10, 11, 3):
                    xg = vp_x + ((k + 0.3 + 0.2 * (r % 2)) * plank - off) * sc((ya + yb) / 2)
                    c.drawLine(xg, ya + (yb - ya) * 0.3, xg + 0.25 * plank * sc(yb), ya + (yb - ya) * 0.32, P(tint(col, 0.85), 70, 2))
    elif kind == 'carpet':
        for j in range(60):
            xx = x0 + rnd(j, 3) * (x1 - x0); yy = y + rnd(j, 4) * (y1 - y)
            c.drawCircle(xx, yy, 2 + 3 * sc(yy), P(tint(col, 0.9), 90))
    elif kind == 'concrete':
        for r in range(1, len(rows), 2): c.drawLine(x0, rows[r], x1, rows[r], lc)
        for j in range(40):
            xx = x0 + rnd(j, 7) * (x1 - x0); yy = y + rnd(j, 8) * (y1 - y)
            c.drawCircle(xx, yy, 1.5 + 2 * sc(yy), P(tint(col, 0.86), 110))
    # ambient occlusion at the wall line
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y), skia.Point(0, y + 70)], [C(NAVY, 50), C(NAVY, 0)]))
    c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + 70), g)
    c.restore()
    if skirt: skirting(c, y, x0, x1, skirt_col)
    if line: c.drawLine(x0, y, x1, y, P(NAVY, 255, 6))


def rug(c, cx, cy, w, h, col=CORAL, col2=None, stripes=3):
    """flat oval rug lying on the floor (perspective squashed), with stripes + fringe + shadow"""
    col2 = col2 or tint(col, 1.25)
    r = skia.Rect.MakeLTRB(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    c.drawOval(skia.Rect.MakeLTRB(cx - w / 2 + 6, cy - h / 2 + 8, cx + w / 2 + 6, cy + h / 2 + 8), blurred(NAVY, 50, 8))
    c.drawOval(r, P(col))
    for k in range(1, stripes + 1):
        f = 1 - k * 0.22
        c.drawOval(skia.Rect.MakeLTRB(cx - w / 2 * f, cy - h / 2 * f, cx + w / 2 * f, cy + h / 2 * f), P(col2 if k % 2 else col, 255, 6))
    c.drawOval(r, P(NAVY, 255, 5))


def light_patch(c, pts, a=70, col='#FFF6C8'):
    """window light on floor / wall: polygon with a soft warm fill"""
    pth = skia.Path(); pth.moveTo(*pts[0])
    for p in pts[1:]: pth.lineTo(*p)
    pth.close()
    p = P(col, a); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    c.drawPath(pth, p)


def cloud(c, x, y, s, a=255):
    p = skia.Path()
    for dx, dy, r in ((-40, 8, 30), (0, -10, 40), (42, 6, 30), (0, 14, 26)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p.setFillType(skia.PathFillType.kWinding)
    c.drawPath(p, P('#FFFFFF', a))


def window(c, x0, y0, x1, y1, curtains=CORAL, sky=('#7CCBF2', '#DDF2FB'), panes=(2, 2), sill=True, clouds=True, sun=False, night=False):
    """window with sky gradient, drifting clouds (seamless), glare, sill and swaying curtains"""
    box_shadow(c, x0, y0, x1, y1, 12, dy=12, blur=10, a=45)
    rrect(c, x0 - 10, y0 - 10, x1 + 10, y1 + 10, 14, P('#FFFFFF'))
    bg(c, sky[0], sky[1], y0, y1, x0, x1)
    c.save(); c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    if sun: glow(c, x1 - (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.28, (x1 - x0) * 0.35, '#FFF3B0', 220); c.drawCircle(x1 - (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.28, 26, P('#FFE9A0'))
    if clouds:
        span = (x1 - x0) + 260
        for k, (fy, s, v) in enumerate(((0.3, 0.9, 9), (0.62, 0.7, 6), (0.45, 0.55, 4))):
            cx = x0 - 130 + (loop_drift(v, span) + k * span / 3) % span
            cloud(c, cx, y0 + (y1 - y0) * fy, s, 235)
    # hill / tree line
    hp = skia.Path(); hp.moveTo(x0, y1); hp.quadTo((x0 + x1) / 2, y1 - (y1 - y0) * 0.35, x1, y1 - (y1 - y0) * 0.1); hp.lineTo(x1, y1); hp.close()
    c.drawPath(hp, P('#9FD3B8'))
    gl = skia.Path(); gl.moveTo(x0 + (x1 - x0) * 0.15, y0); gl.lineTo(x0 + (x1 - x0) * 0.4, y0); gl.lineTo(x0 + (x1 - x0) * 0.1, y1); gl.lineTo(x0 - (x1 - x0) * 0.15, y1); gl.close()
    c.drawPath(gl, P('#FFFFFF', 55))
    c.restore()
    nx, ny = panes
    for k in range(1, nx): c.drawLine(x0 + (x1 - x0) * k / nx, y0, x0 + (x1 - x0) * k / nx, y1, P('#FFFFFF', 255, 12))
    for k in range(1, ny): c.drawLine(x0, y0 + (y1 - y0) * k / ny, x1, y0 + (y1 - y0) * k / ny, P('#FFFFFF', 255, 12))
    for k in range(1, nx): c.drawLine(x0 + (x1 - x0) * k / nx, y0, x0 + (x1 - x0) * k / nx, y1, P(NAVY, 255, 3))
    for k in range(1, ny): c.drawLine(x0, y0 + (y1 - y0) * k / ny, x1, y0 + (y1 - y0) * k / ny, P(NAVY, 255, 3))
    rrect(c, x0 - 10, y0 - 10, x1 + 10, y1 + 10, 14, P(NAVY, 255, 6))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P(NAVY, 255, 3))
    if sill:
        shaded_rrect(c, x0 - 30, y1 + 6, x1 + 30, y1 + 30, 6, '#FFFFFF', 5, 0.85)
    if curtains:
        for side in (-1, 1):
            xe = x0 - 40 if side < 0 else x1 + 40
            sw_ = 6 * osc(0.12, side)
            cp = skia.Path(); xi = xe - side * 70
            cp.moveTo(xe + side * 10, y0 - 40); cp.lineTo(xi, y0 - 40)
            cp.quadTo(xi + side * 30 + sw_, (y0 + y1) / 2, xi - side * 6 + sw_ * 1.5, y1 + 60)
            cp.lineTo(xe + side * 10, y1 + 60); cp.close()
            shaded_path(c, cp, curtains, 5, 0.85, light=(-side, 0), shift=0.18)
            for q in (0.35, 0.68):
                xq = xe + (xi - xe) * q
                c.drawLine(xq, y0 - 30, xq + sw_ * q, y1 + 50, P(tint(curtains, 0.82), 255, 4))
        rrect(c, x0 - 80, y0 - 52, x1 + 80, y0 - 38, 7, P(WOOD)); rrect(c, x0 - 80, y0 - 52, x1 + 80, y0 - 38, 7, P(NAVY, 255, 4))


def picture(c, x0, y0, x1, y1, kind=0, frame=WOOD, rot=0.0):
    """framed wall picture with shadow; kind 0 mountains, 1 sun/sea, 2 abstract circles, 3 heart"""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c.save(); c.translate(cx, cy); c.rotate(rot + 1.2 * osc(0.05, kind)); c.translate(-cx, -cy)
    c.drawLine(cx, y0 - 40, x0 + 20, y0, P(NAVY, 160, 3)); c.drawLine(cx, y0 - 40, x1 - 20, y0, P(NAVY, 160, 3)); c.drawCircle(cx, y0 - 40, 5, P(NAVY))
    box_shadow(c, x0, y0, x1, y1, 6, dy=10, blur=8, a=55)
    shaded_rrect(c, x0, y0, x1, y1, 6, frame, 5, 0.82)
    ix0, iy0, ix1, iy1 = x0 + 14, y0 + 14, x1 - 14, y1 - 14
    c.save(); c.clipRect(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1))
    k = kind % 4
    if k == 0:
        bg(c, '#CFEAF7', '#F4FBFF', iy0, iy1, ix0, ix1)
        m = skia.Path(); m.moveTo(ix0, iy1); m.lineTo(ix0 + (ix1 - ix0) * 0.38, iy0 + (iy1 - iy0) * 0.35); m.lineTo(ix0 + (ix1 - ix0) * 0.6, iy0 + (iy1 - iy0) * 0.7)
        m.lineTo(ix0 + (ix1 - ix0) * 0.75, iy0 + (iy1 - iy0) * 0.5); m.lineTo(ix1, iy1); m.close(); shaded_path(c, m, SAGE, 0, 0.85)
        c.drawCircle(ix1 - (ix1 - ix0) * 0.22, iy0 + (iy1 - iy0) * 0.25, (ix1 - ix0) * 0.09, P(YEL))
    elif k == 1:
        bg(c, '#FFE2B8', '#FFC9A8', iy0, iy1, ix0, ix1)
        c.drawCircle((ix0 + ix1) / 2, iy0 + (iy1 - iy0) * 0.55, (ix1 - ix0) * 0.22, P(CORAL))
        c.drawRect(skia.Rect.MakeLTRB(ix0, iy0 + (iy1 - iy0) * 0.62, ix1, iy1), P(SKY))
        for q in range(3): c.drawLine(ix0 + 12 + q * 30, iy0 + (iy1 - iy0) * (0.72 + q * 0.08), ix0 + 50 + q * 40, iy0 + (iy1 - iy0) * (0.72 + q * 0.08), P('#FFFFFF', 160, 4))
    elif k == 2:
        c.drawColor(C('#FBF3E6'))
        c.drawCircle(ix0 + (ix1 - ix0) * 0.38, iy0 + (iy1 - iy0) * 0.45, (ix1 - ix0) * 0.25, P(SKY))
        c.drawCircle(ix0 + (ix1 - ix0) * 0.62, iy0 + (iy1 - iy0) * 0.6, (ix1 - ix0) * 0.2, P(CORAL, 220))
        c.drawRect(skia.Rect.MakeLTRB(ix0 + (ix1 - ix0) * 0.2, iy0 + (iy1 - iy0) * 0.78, ix1 - (ix1 - ix0) * 0.15, iy0 + (iy1 - iy0) * 0.84), P(NAVY))
    else:
        c.drawColor(C('#FFF0F0'))
        hx, hy, hs = (ix0 + ix1) / 2, (iy0 + iy1) / 2, (ix1 - ix0) * 0.012
        hp = skia.Path(); hp.moveTo(hx, hy + 22 * hs); hp.cubicTo(hx - 40 * hs, hy - 5 * hs, hx - 18 * hs, hy - 30 * hs, hx, hy - 12 * hs)
        hp.cubicTo(hx + 18 * hs, hy - 30 * hs, hx + 40 * hs, hy - 5 * hs, hx, hy + 22 * hs); c.drawPath(hp, P(CORAL))
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), P(NAVY, 255, 3))
    c.restore()


def plant(c, x, y, s=1.0, pot=TERRA, seed=0.0):
    """potted plant, (x, y) = pot bottom centre; leaves sway with the global clock"""
    contact_shadow(c, x, y, 150 * s, 22 * s, a=60)
    leaves = ((-60, -150, -25), (60, -160, 25), (-20, -200, -8), (30, -210, 10), (-80, -100, -45), (85, -110, 45), (0, -240, 0))
    for k, (lx, ly, rot) in enumerate(leaves):
        sw_ = 4 * osc(0.22 + 0.03 * k, seed + k)
        c.save(); c.translate(x + lx * s * 0.3, y - 110 * s); c.rotate(rot + sw_)
        lp = skia.Path(); L = math.hypot(lx, ly + 110) * s * 0.95
        lp.moveTo(0, 0); lp.quadTo(-34 * s, -L * 0.5, 0, -L); lp.quadTo(34 * s, -L * 0.5, 0, 0)
        shaded_path(c, lp, SAGE if k % 2 else '#8CC4AE', 4 * s, 0.82, light=(-1, 0), shift=0.22)
        c.drawLine(0, -4 * s, 0, -L * 0.85, P(LEAF, 255, 3 * s))
        c.restore()
    pth = skia.Path(); pth.moveTo(x - 62 * s, y - 120 * s); pth.lineTo(x + 62 * s, y - 120 * s); pth.lineTo(x + 46 * s, y); pth.lineTo(x - 46 * s, y); pth.close()
    shaded_path(c, pth, pot, 5 * s, 0.84, light=(-1, 0), shift=0.2)
    shaded_rrect(c, x - 70 * s, y - 130 * s, x + 70 * s, y - 100 * s, 8 * s, pot, 5 * s, 0.86)


def shelf(c, x0, y, x1, seed=0, books=True, deco=True):
    """wall shelf (board at y) with books in palette colours + a small deco"""
    contact_shadow(c, (x0 + x1) / 2, y + 26, (x1 - x0) * 1.05, 26, a=45)
    if books:
        x = x0 + 16; k = 0; cols = [CORAL, SKY, YEL, SAGE, NAVY, '#B98AE6', MUSTARD]
        while x < x1 - 110:
            bw = 26 + int(rnd(k, seed) * 20); bh = 90 + int(rnd(k, seed + 1) * 50)
            col = cols[int(rnd(k, seed + 2) * len(cols))]
            if k == 4:   # leaning book
                c.save(); c.translate(x, y); c.rotate(14); shaded_rrect(c, 0, -bh, bw, 0, 4, col, 4, 0.82, hi=False); c.restore(); x += bw + 26
            else:
                shaded_rrect(c, x, y - bh, x + bw, y, 4, col, 4, 0.82, hi=False)
                c.drawLine(x + 5, y - bh + 16, x + bw - 5, y - bh + 16, P('#FFFFFF', 130, 3)); x += bw + 2
            k += 1
    if deco:
        dx = x1 - 70
        shaded_rrect(c, dx - 30, y - 70, dx + 30, y, 10, '#FFFFFF', 4, 0.86)
        for q, (lx, rot) in enumerate(((-12, -20), (12, 20), (0, 0))):
            c.save(); c.translate(dx + lx, y - 66); c.rotate(rot + 5 * osc(0.2, q + seed))
            lp = skia.Path(); lp.moveTo(0, 0); lp.quadTo(-16, -30, 0, -58); lp.quadTo(16, -30, 0, 0)
            c.drawPath(lp, P(SAGE)); c.drawPath(lp, P(NAVY, 255, 3)); c.restore()
    shaded_rrect(c, x0, y, x1, y + 20, 5, WOOD, 5, 0.8)
    for bx in (x0 + 40, x1 - 40):
        p = skia.Path(); p.moveTo(bx, y + 20); p.lineTo(bx, y + 50); p.lineTo(bx + 18, y + 20); p.close(); c.drawPath(p, P(NAVY))


def wall_clock(c, x, y, r=60, col='#FFFFFF'):
    """clock whose second hand ticks with the global clock"""
    contact_shadow(c, x + 6, y + r * 0.9, r * 1.4, r * 0.3, a=0)
    c.drawCircle(x + 5, y + 9, r, blurred(NAVY, 60, 7))
    shaded_circle(c, x, y, r, col, 7, 0.88)
    for k in range(12):
        a = math.radians(k * 30); r0 = r * (0.78 if k % 3 else 0.7)
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r * 0.86 * math.cos(a), y + r * 0.86 * math.sin(a), P(NAVY, 255, 3 if k % 3 else 5))
    sec = math.floor(NOW) + ebounce(clamp((NOW % 1) / 0.25)) if NOW % 1 < 0.25 else math.floor(NOW) + 1
    a = math.radians(-90 + 6 * sec); am = math.radians(-90 + 0.1 * sec + 60); ah = math.radians(-90 + 300)
    c.drawLine(x, y, x + r * 0.45 * math.cos(ah), y + r * 0.45 * math.sin(ah), P(NAVY, 255, 7))
    c.drawLine(x, y, x + r * 0.68 * math.cos(am), y + r * 0.68 * math.sin(am), P(NAVY, 255, 5))
    c.drawLine(x - r * 0.15 * math.cos(a), y - r * 0.15 * math.sin(a), x + r * 0.78 * math.cos(a), y + r * 0.78 * math.sin(a), P(CORAL, 255, 3))
    c.drawCircle(x, y, 5, P(CORAL))


def pendant_lamp(c, x, y_top, length, s=1.0, col=CORAL, on=True):
    """ceiling lamp swaying gently; glow when on"""
    a = math.radians(2.2 * osc(0.23, x))
    bx, by = x + length * math.sin(a), y_top + length * math.cos(a)
    c.drawLine(x, y_top, bx, by, P(NAVY, 255, 4))
    if on: glow(c, bx, by + 40 * s, 260 * s, '#FFF3B0', 110)
    c.save(); c.translate(bx, by); c.rotate(-math.degrees(a))
    sh = skia.Path(); sh.moveTo(-18 * s, 0); sh.lineTo(18 * s, 0); sh.lineTo(70 * s, 60 * s); sh.lineTo(-70 * s, 60 * s); sh.close()
    shaded_path(c, sh, col, 5, 0.82, light=(-1, 0), shift=0.2)
    c.drawOval(skia.Rect.MakeLTRB(-26 * s, 50 * s, 26 * s, 76 * s), P('#FFF7C2' if on else '#C9CED8'))
    c.drawOval(skia.Rect.MakeLTRB(-26 * s, 50 * s, 26 * s, 76 * s), P(NAVY, 255, 3))
    c.restore()


def motes(c, x0, y0, x1, y1, n=16, seed=0, col='#FFFFFF', a=170, size=4.0, rise=14):
    """floating dust motes / pollen in a region (seamless drift + twinkle)"""
    hgt = y1 - y0
    for k in range(n):
        bx = x0 + rnd(k, seed) * (x1 - x0); ph = rnd(k, seed + 5) * 6.28
        yy = y1 - (rnd(k, seed + 2) * hgt + loop_drift(rise * (0.5 + rnd(k, seed + 3)), hgt)) % hgt
        xx = bx + 22 * osc(0.09 + 0.05 * rnd(k, seed + 4), ph)
        tw = 0.55 + 0.45 * osc(0.6 + rnd(k, seed + 6), ph)
        r = size * (0.6 + rnd(k, seed + 7))
        c.drawCircle(xx, yy, r * 2.4, P(col, a * 0.18 * tw))
        c.drawCircle(xx, yy, r, P(col, a * tw))


def sparkle(c, x, y, r, col='#FFFFFF', a=255, rot=0.0):
    pth = skia.Path()
    for q in range(8):
        rr = r if q % 2 == 0 else r * 0.28; ang = math.radians(rot + q * 45 - 90)
        (pth.moveTo if q == 0 else pth.lineTo)(x + rr * math.cos(ang), y + rr * math.sin(ang))
    pth.close(); c.drawPath(pth, P(col, a))


def sparkles(c, x0, y0, x1, y1, n=8, seed=0, col=YEL, size=16, outline=True):
    """twinkling 4-point stars scattered in a region"""
    for k in range(n):
        x = x0 + rnd(k, seed) * (x1 - x0); y = y0 + rnd(k, seed + 1) * (y1 - y0)
        tw = max(0.0, osc(0.35 + 0.3 * rnd(k, seed + 2), rnd(k, seed + 3) * 6.28))
        if tw <= 0.05: continue
        r = size * (0.6 + 0.6 * rnd(k, seed + 4)) * tw
        if outline: sparkle(c, x, y, r + 3, NAVY, 255 * min(1, tw * 2))
        sparkle(c, x, y, r, col, 255 * min(1, tw * 2))


def steam(c, x, y, s=1.0, n=3, col='#FFFFFF', a=150):
    """rising wavy steam wisps above (x, y)"""
    for k in range(n):
        ph = k * 2.1
        u = (loop_drift(0.55, 1.0) + k / n) % 1.0
        pth = skia.Path(); x0 = x + (k - (n - 1) / 2) * 22 * s
        pth.moveTo(x0, y - u * 30 * s)
        for q in range(1, 6):
            yy = y - (u * 30 + q * 22) * s
            pth.lineTo(x0 + 10 * s * math.sin(q * 1.3 + ph + NOW * 3), yy)
        c.drawPath(pth, P(col, a * (1 - u) * 0.9, 7 * s))


def speed_lines(c, x0, y0, x1, y1, n=8, seed=0, a=110, col=NAVY, dirx=-1):
    """horizontal motion streaks (use behind something moving fast)"""
    for k in range(n):
        y = y0 + rnd(k, seed) * (y1 - y0); L = 60 + rnd(k, seed + 1) * 160
        x = x0 + ((rnd(k, seed + 2) * (x1 - x0)) + loop_drift(900, x1 - x0) * -dirx) % (x1 - x0)
        c.drawLine(x, y, x + L * -dirx, y, P(col, a, 5))


def dust_puff(c, x, y, u, s=1.0, col='#FFFFFF'):
    """small puff clouds for landings / footsteps; u = 0..1"""
    if u <= 0 or u >= 1: return
    for k, sg in enumerate((-1, 1, -0.4, 0.5)):
        d = 30 + 70 * eout(u); r = (16 + 8 * k % 2) * (1 - u * 0.6) * s
        c.drawCircle(x + sg * d * s, y - 10 * s - 18 * u * s * (k % 2 + 1), r, P(col, 230 * (1 - u)))
        c.drawCircle(x + sg * d * s, y - 10 * s - 18 * u * s * (k % 2 + 1), r, P(NAVY, 120 * (1 - u), 3))


# ---------------------------------------------------------------- reusable props (engine v2)
def desk_top(c, col='#E0AE78', y0=-300, y1=H + 300):
    """top-down wooden desk surface filling the frame (for infographic scenes)"""
    bg(c, tint(col, 1.04), tint(col, 0.93), y0, y1)
    for k in range(int((y1 - y0) / 120) + 1):
        y = y0 + 40 + k * 120; pth = skia.Path(); pth.moveTo(-20, y)
        for q in range(1, 13): pth.lineTo(q * 100 - 20, y + 10 * math.sin(q * 1.1 + k * 2.3))
        c.drawPath(pth, P(tint(col, 0.88), 110, 3))
    for k in range(int((y1 - y0) / 480) + 1):
        y = y0 + 300 + k * 480; c.drawLine(0, y, W, y, P(tint(col, 0.8), 200, 5))
        c.drawLine(0, y + 4, W, y + 4, P(tint(col, 1.1), 160, 2))
    for q in range(3):  # knots
        x, y = 140 + q * 390, y0 + 220 + (q * 530) % max(1, (y1 - y0 - 200))
        c.drawOval(skia.Rect.MakeXYWH(x, y, 60, 22), P(tint(col, 0.85), 140, 3))


def mug(c, x, y, s=1.0, col=CORAL, top=True):
    """coffee mug seen from above (top=True) with steam, or from the side"""
    if top:
        c.drawCircle(x + 8 * s, y + 14 * s, 62 * s, blurred(NAVY, 60, 10 * s))
        rrect(c, x + 44 * s, y - 16 * s, x + 96 * s, y + 16 * s, 14 * s, P(col)); rrect(c, x + 44 * s, y - 16 * s, x + 96 * s, y + 16 * s, 14 * s, P(NAVY, 255, 5 * s))
        shaded_circle(c, x, y, 58 * s, col, 6 * s, 0.86)
        c.drawCircle(x, y, 44 * s, P('#7A4A2A')); c.drawCircle(x, y, 44 * s, P(NAVY, 255, 4 * s))
        c.drawOval(skia.Rect.MakeXYWH(x - 26 * s, y - 24 * s, 30 * s, 14 * s), P('#FFFFFF', 70))
        steam(c, x, y - 30 * s, s)
    else:
        contact_shadow(c, x, y, 130 * s, 18 * s)
        rrect(c, x + 34 * s, y - 92 * s, x + 74 * s, y - 40 * s, 18 * s, P(NAVY, 255, 10 * s))
        shaded_rrect(c, x - 46 * s, y - 110 * s, x + 46 * s, y, 14 * s, col, 6 * s)
        steam(c, x, y - 120 * s, s)


def pencil(c, x0, y0, x1, y1, w=26, col=YEL):
    L = math.hypot(x1 - x0, y1 - y0); a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    c.save(); c.translate(x0, y0); c.rotate(a)
    rrect(c, 6, -w / 2 + 12, L + 6, w / 2 + 12, 6, blurred(NAVY, 60, 6))
    rrect(c, 0, -w / 2, 34, w / 2, 6, P('#FF9AA8')); c.drawRect(skia.Rect.MakeLTRB(30, -w / 2, 52, w / 2), P(GREY))
    shaded_rrect(c, 50, -w / 2, L - 50, w / 2, 3, col, 0, 0.85, side='b')
    tip = skia.Path(); tip.moveTo(L - 50, -w / 2); tip.lineTo(L, 0); tip.lineTo(L - 50, w / 2); tip.close(); c.drawPath(tip, P('#F3D2A2'))
    tp = skia.Path(); tp.moveTo(L - 16, -w * 0.16); tp.lineTo(L, 0); tp.lineTo(L - 16, w * 0.16); tp.close(); c.drawPath(tp, P(NAVY))
    rrect(c, 0, -w / 2, L - 50, w / 2, 6, P(NAVY, 255, 4)); c.drawPath(tip, P(NAVY, 255, 4))
    c.restore()


def sticky_note(c, x, y, txt='', col=YEL, size=150, rot=-6, fsize=48):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawRect(skia.Rect.MakeLTRB(-size / 2 + 6, -size / 2 + 12, size / 2 + 6, size / 2 + 12), blurred(NAVY, 55, 8))
    c.drawRect(skia.Rect.MakeLTRB(-size / 2, -size / 2, size / 2, size / 2), P(col))
    c.drawRect(skia.Rect.MakeLTRB(-size / 2, -size / 2, size / 2, -size / 2 + size * 0.16), P(tint(col, 0.92)))
    fold = skia.Path(); fold.moveTo(size / 2 - 30, size / 2); fold.lineTo(size / 2, size / 2 - 30); fold.lineTo(size / 2 - 26, size / 2 - 26); fold.close()
    c.drawPath(fold, P(tint(col, 0.85)))
    c.drawRect(skia.Rect.MakeLTRB(-size / 2, -size / 2, size / 2, size / 2), P(NAVY, 255, 4))
    if txt:
        f = skia.Font(F_CAP, fsize); w = f.measureText(txt); c.drawString(txt, -w / 2, fsize * 0.4, f, P(NAVY))
    c.restore()


def backpack(c, x, y, s=1.0, col=SKY):
    """(x, y) = bottom centre on the floor"""
    contact_shadow(c, x, y, 190 * s, 28 * s)
    rrect(c, x - 40 * s, y - 196 * s, x + 40 * s, y - 150 * s, 22 * s, P(NAVY, 255, 10 * s))
    shaded_rrect(c, x - 80 * s, y - 175 * s, x + 80 * s, y, 40 * s, col, 6 * s)
    shaded_rrect(c, x - 56 * s, y - 80 * s, x + 56 * s, y - 14 * s, 18 * s, tint(col, 0.92), 5 * s, 0.86)
    c.drawLine(x - 40 * s, y - 80 * s, x + 40 * s, y - 80 * s, P(YEL, 255, 6 * s))


def sneakers(c, x, y, s=1.0, col='#FFFFFF', stripe=CORAL):
    for k, dx in enumerate((-48, 40)):
        xx = x + dx * s; yy = y + (k * 10) * s
        contact_shadow(c, xx, yy, 120 * s, 18 * s, a=55)
        pth = skia.Path(); pth.moveTo(xx - 54 * s, yy); pth.lineTo(xx - 54 * s, yy - 34 * s); pth.quadTo(xx - 30 * s, yy - 50 * s, xx - 4 * s, yy - 40 * s)
        pth.quadTo(xx + 30 * s, yy - 26 * s, xx + 56 * s, yy - 14 * s); pth.lineTo(xx + 56 * s, yy); pth.close()
        shaded_path(c, pth, col, 5 * s, 0.88)
        c.drawLine(xx - 54 * s, yy - 8 * s, xx + 56 * s, yy - 8 * s, P(GREY, 255, 5 * s))
        c.drawLine(xx - 30 * s, yy - 30 * s, xx + 10 * s, yy - 18 * s, P(stripe, 255, 7 * s))


def stopwatch(c, x, y, r, t_run, col='#FFFFFF'):
    """stopwatch whose hand sweeps with t_run seconds"""
    c.drawCircle(x + 6, y + 14, r, blurred(NAVY, 70, 10))
    shaded_rrect(c, x - 22, y - r - 34, x + 22, y - r + 4, 8, CORAL, 5)
    c.save(); c.translate(x, y); c.rotate(40); shaded_rrect(c, -12, -r - 22, 12, -r + 6, 6, GREY, 4); c.restore()
    shaded_circle(c, x, y, r, col, 8, 0.86)
    c.drawCircle(x, y, r * 0.84, P(NAVY, 60, 3))
    for k in range(12):
        a = math.radians(k * 30); c.drawLine(x + r * 0.7 * math.cos(a), y + r * 0.7 * math.sin(a), x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a), P(NAVY, 255, 4 if k % 3 else 6))
    a = math.radians(-90 + t_run * 240)
    c.drawLine(x, y, x + r * 0.72 * math.cos(a), y + r * 0.72 * math.sin(a), P(CORAL, 255, 9))
    c.drawCircle(x, y, 11, P(NAVY))


def front_door(c, x, y, s=1.0, col='#E9A15B', open_k=0.0, frame='#FFFFFF', mat=True, number=None):
    """front view door with casing, panels, knob, doormat; (x, y) = bottom centre"""
    contact_shadow(c, x, y + 4 * s, 380 * s, 30 * s, a=50)
    shaded_rrect(c, x - 165 * s, y - 540 * s, x + 165 * s, y + 4 * s, 10 * s, frame, 7 * s, 0.88)
    # the next room behind the door: warm lit interior
    bg(c, '#FFE7B0', '#F6C98A', y - 495 * s, y, x - 125 * s, x + 125 * s)
    c.drawRect(skia.Rect.MakeLTRB(x - 125 * s, y - 60 * s, x + 125 * s, y), P('#E8B877'))
    c.drawRect(skia.Rect.MakeLTRB(x - 125 * s, y - 495 * s, x + 125 * s, y), P(NAVY, 255, 3 * s))
    w = 250 * s * (1 - 0.8 * open_k)
    p = skia.Path(); x0 = x - 125 * s
    p.moveTo(x0, y - 495 * s); p.lineTo(x0 + w, y - 495 * s - 30 * s * open_k); p.lineTo(x0 + w, y + 30 * s * open_k); p.lineTo(x0, y); p.close()
    shaded_path(c, p, col, 6 * s, 0.86, light=(-1, -0.3), shift=0.1)
    if open_k < 0.5:
        for yy in (-450, -250):
            rrect(c, x0 + 30 * s, y + yy * s, x0 + w - 30 * s, y + (yy + 160) * s, 10 * s, P(tint(col, 0.9)))
            rrect(c, x0 + 30 * s, y + yy * s, x0 + w - 30 * s, y + (yy + 160) * s, 10 * s, P(NAVY, 120, 4 * s))
            c.drawLine(x0 + 36 * s, y + (yy + 8) * s, x0 + w - 36 * s, y + (yy + 8) * s, P('#FFFFFF', 70, 4 * s))
        shaded_circle(c, x0 + w - 32 * s, y - 250 * s, 15 * s, YEL, 4 * s, 0.8)
        if number:
            f = skia.Font(F_OST, 34 * s); tw = f.measureText(number)
            shaded_rrect(c, x - tw / 2 - 16 * s, y - 470 * s, x + tw / 2 + 16 * s, y - 420 * s, 8 * s, '#FFFFFF', 3 * s)
            c.drawString(number, x - tw / 2, y - 433 * s, f, P(NAVY))
    if mat:
        mp = skia.Path(); mp.moveTo(x - 150 * s, y + 12 * s); mp.lineTo(x + 150 * s, y + 12 * s); mp.lineTo(x + 190 * s, y + 70 * s); mp.lineTo(x - 190 * s, y + 70 * s); mp.close()
        c.save(); c.translate(0, 8); c.drawPath(mp, blurred(NAVY, 50, 6)); c.restore()
        shaded_path(c, mp, CORAL, 5 * s, 0.85, light=(0, -1), shift=0.15)
        for q in range(-3, 4):
            c.drawLine(x + q * 40 * s, y + 20 * s, x + q * 50 * s, y + 62 * s, P(tint(CORAL, 0.82), 255, 3 * s))


# ---------------------------------------------------------------- illustrated containers
@contextmanager
def card(c, x0, y0, x1, y1, kind='paper', k=1.0, rot=0.0, title=None, title_bg=CORAL, title_fg='#FFFFFF', sk=None):
    """illustrated container for charts/infographics. kind: paper | whiteboard | phone | clipboard | blueprint | screen.
    usage:  with card(c, 120, 460, 960, 1240, 'whiteboard', k=pop) as (ix0, iy0, ix1, iy1): ...draw content...
    content is clipped to the inner area; k / sk scale the card around its centre for pop-ins."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sx, sy = sk if sk else (k, k)
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(max(sx, 1e-3), max(sy, 1e-3)); c.translate(-cx, -cy)
    r = 26
    if kind == 'whiteboard':
        box_shadow(c, x0, y0, x1, y1, 16, dy=18, blur=18, a=70)
        shaded_rrect(c, x0, y0, x1, y1, 16, '#C9D1DD', 7, 0.84)
        ix0, iy0, ix1, iy1 = x0 + 22, y0 + 22, x1 - 22, y1 - 22
        bg(c, '#FFFFFF', '#F1F4F8', iy0, iy1, ix0, ix1)
        for q in range(4):  # faint smudges
            c.drawOval(skia.Rect.MakeXYWH(ix0 + rnd(q, 2) * (ix1 - ix0) * 0.8, iy0 + rnd(q, 3) * (iy1 - iy0) * 0.8, 160, 50), P('#D8DEE8', 60))
        ir = 6
    elif kind == 'phone':
        box_shadow(c, x0, y0, x1, y1, 60, dy=20, blur=20, a=80)
        shaded_rrect(c, x0, y0, x1, y1, 62, NAVY, 7, 0.75)
        ix0, iy0, ix1, iy1 = x0 + 22, y0 + 26, x1 - 22, y1 - 26
        bg(c, '#FFFFFF', '#EAF4FB', iy0, iy1, ix0, ix1)
        ir = 42
    elif kind == 'clipboard':
        box_shadow(c, x0, y0, x1, y1, 20, dy=16, blur=16, a=70)
        shaded_rrect(c, x0, y0, x1, y1, 20, WOOD, 7, 0.82)
        ix0, iy0, ix1, iy1 = x0 + 26, y0 + 70, x1 - 26, y1 - 26
        c.drawRect(skia.Rect.MakeLTRB(ix0 + 6, iy0 + 8, ix1 + 6, iy1 + 6), P(NAVY, 40))
        c.drawRect(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), P('#FFFFFF'))
        ir = 2
    elif kind == 'blueprint':
        box_shadow(c, x0, y0, x1, y1, 8, dy=16, blur=16, a=70)
        ix0, iy0, ix1, iy1 = x0, y0, x1, y1
        bg(c, '#3D86C6', '#2F6FAE', y0, y1, x0, x1)
        for gx in range(int(x0), int(x1), 40): c.drawLine(gx, y0, gx, y1, P('#FFFFFF', 28, 2))
        for gy in range(int(y0), int(y1), 40): c.drawLine(x0, gy, x1, gy, P('#FFFFFF', 28, 2))
        ir = 8
    elif kind == 'screen':
        box_shadow(c, x0, y0, x1, y1, 22, dy=18, blur=18, a=70)
        shaded_rrect(c, x0, y0, x1, y1, 22, '#2B3A60', 7, 0.8)
        ix0, iy0, ix1, iy1 = x0 + 20, y0 + 20, x1 - 20, y1 - 20
        bg(c, '#FFFFFF', '#EEF3F9', iy0, iy1, ix0, ix1)
        ir = 8
    else:  # paper
        box_shadow(c, x0, y0, x1, y1, r, dy=16, blur=16, a=65)
        rrect(c, x0, y0, x1, y1, r, P('#FFFFFF'))
        ix0, iy0, ix1, iy1 = x0, y0, x1, y1
        ir = r
    if title:
        tb = 96
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), ir, ir), True)
        bg(c, tint(title_bg, 1.06), tint(title_bg, 0.92), iy0, iy0 + tb, ix0, ix1)
        c.drawLine(ix0, iy0 + tb, ix1, iy0 + tb, P(NAVY, 255, 6))
        f = skia.Font(F_OST, 50); tw = f.measureText(title)
        c.drawString(title, (ix0 + ix1) / 2 - tw / 2, iy0 + tb / 2 + 18, f, P(title_fg))
        c.restore()
        iy0 += tb
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), ir, ir), True)
    try:
        yield (ix0, iy0, ix1, iy1)
    finally:
        c.restore()
        if kind == 'paper':
            rrect(c, x0, y0, x1, y1, r, P(NAVY, 255, 7))
            for tx, rot_ in ((x0 + 60, -8), (x1 - 60, 7)):
                c.save(); c.translate(tx, y0 + 4); c.rotate(rot_)
                c.drawRect(skia.Rect.MakeLTRB(-50, -18, 50, 18), P('#FFE69A', 200)); c.restore()
            fold = skia.Path(); fold.moveTo(x1 - 50, y1); fold.lineTo(x1, y1 - 50); fold.lineTo(x1 - 44, y1 - 44); fold.close()
            c.drawPath(fold, P('#E8E2D6')); c.drawPath(fold, P(NAVY, 255, 4))
        elif kind == 'whiteboard':
            c.drawRect(skia.Rect.MakeLTRB(ix0, iy0 - (96 if title else 0), ix1, iy1), P(NAVY, 255, 4))
            ty = y1 - 6
            shaded_rrect(c, x0 + 60, ty, x1 - 60, ty + 26, 8, '#C9D1DD', 5, 0.82)
            for q, mc in enumerate((CORAL, SKY, NAVY)):
                mx = x0 + 160 + q * 90
                rrect(c, mx, ty - 14, mx + 70, ty + 4, 6, P(mc)); rrect(c, mx, ty - 14, mx + 70, ty + 4, 6, P(NAVY, 255, 3))
            for mx, my, mc in ((x0 + 40, y0 + 40, CORAL), (x1 - 40, y0 + 40, SKY)):
                shaded_circle(c, mx, my, 16, mc, 4, 0.8)
        elif kind == 'phone':
            rrect(c, ix0, iy0, ix1, iy1, ir, P(NAVY, 255, 4))
            rrect(c, cx - 70, y0 + 34, cx + 70, y0 + 62, 14, P(NAVY))
            f = skia.Font(F_CAP, 26); c.drawString("9:41", ix0 + 34, y0 + 60, f, P(NAVY))
            rrect(c, ix1 - 76, y0 + 40, ix1 - 34, y0 + 60, 5, P(NAVY, 255, 3)); rrect(c, ix1 - 72, y0 + 44, ix1 - 48, y0 + 56, 3, P(NAVY))
            gl = skia.Path(); gl.moveTo(ix1 - (ix1 - ix0) * 0.4, iy0); gl.lineTo(ix1, iy0); gl.lineTo(ix1, iy0 + (iy1 - iy0) * 0.25); gl.close()
            c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), ir, ir), True); c.drawPath(gl, P('#FFFFFF', 40)); c.restore()
        elif kind == 'clipboard':
            c.drawRect(skia.Rect.MakeLTRB(ix0, iy0, ix1, iy1), P(NAVY, 255, 4))
            shaded_rrect(c, cx - 110, y0 - 20, cx + 110, y0 + 56, 16, '#B9C3D1', 6, 0.8)
            c.drawCircle(cx, y0 + 6, 12, P(NAVY))
        elif kind in ('blueprint', 'screen'):
            rrect(c, ix0, iy0 - (96 if title else 0), ix1, iy1, ir, P(NAVY, 255, 6 if kind == 'blueprint' else 4))
        c.restore()


# ---------------------------------------------------------------- legacy environments (episode 001)
def classroom_bg(c):
    c.drawColor(C(CREAM))
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), P(FLOOR))
    c.drawLine(0, 1250, W, 1250, P(NAVY, 255, 6))
    rrect(c, 170, 560, 910, 860, 18, P(WOOD)); rrect(c, 190, 578, 890, 842, 10, P('#2E5A55'))
    rrect(c, 170, 560, 910, 860, 18, P(NAVY, 255, 6))
    c.drawLine(240, 640, 420, 640, P('#FFFFFF', 140, 7)); c.drawLine(240, 690, 360, 690, P('#FFFFFF', 140, 7))
    c.drawCircle(690, 700, 50, P('#FFFFFF', 120, 6)); c.drawLine(660, 760, 760, 640, P('#FFFFFF', 120, 6))
    c.drawCircle(960, 470, 46, P('#FFFFFF')); c.drawCircle(960, 470, 46, P(NAVY, 255, 6))
    c.drawLine(960, 470, 960, 444, P(NAVY, 255, 5)); c.drawLine(960, 470, 980, 478, P(NAVY, 255, 5))


SEATED = [(140, 0), (330, 1), (750, 2), (940, 3)]


def classmates_desks(c, look_fn):
    for x, k in SEATED:
        lx, ly = look_fn(x)
        bust(c, x, 1240, 0.8, HOODS[k], SKINS[k], HAIRS[k], look=(lx, ly), eyes='big' if (lx or ly) else 'dot')
    for x, k in SEATED:
        rrect(c, x - 105, 1195, x + 105, 1330, 12, P(WOOD)); rrect(c, x - 105, 1195, x + 105, 1330, 12, P(NAVY, 255, 6))
        rrect(c, x - 115, 1182, x + 115, 1210, 10, P('#E0A465')); rrect(c, x - 115, 1182, x + 115, 1210, 10, P(NAVY, 255, 5))



def popstar_print(c, x, y, s):
    for dx, dy, r, col in ((-46, -36, 40, '#9B6BD6'), (46, -36, 40, '#9B6BD6'), (0, -60, 46, '#B98AE6'), (-58, 6, 30, '#9B6BD6'), (58, 6, 30, '#9B6BD6')):
        c.drawCircle(x + dx * s, y + dy * s, r * s, P(col))
    c.drawCircle(x, y, 44 * s, P('#F5C6A5')); c.drawCircle(x, y, 44 * s, P(NAVY, 255, 4 * s))
    rrect(c, x - 36 * s, y - 14 * s, x - 4 * s, y + 4 * s, 6 * s, P(NAVY)); rrect(c, x + 4 * s, y - 14 * s, x + 36 * s, y + 4 * s, 6 * s, P(NAVY))
    c.drawLine(x - 4 * s, y - 8 * s, x + 4 * s, y - 8 * s, P(NAVY, 255, 3 * s))
    m = skia.Path(); m.moveTo(x - 20 * s, y + 18 * s); m.quadTo(x, y + 36 * s, x + 20 * s, y + 18 * s); m.close()
    c.drawPath(m, P('#FFFFFF')); c.drawPath(m, P(NAVY, 255, 3 * s))
    for dx, dy, r in ((-80, -70, 12), (84, -64, 10), (-78, 50, 9), (82, 52, 13)):
        st = skia.Path(); cx, cy = x + dx * s, y + dy * s
        for k in range(8):
            rr = r * s if k % 2 == 0 else r * s * 0.38; a = math.radians(k * 45 - 90)
            (st.moveTo if k == 0 else st.lineTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
        st.close(); c.drawPath(st, P(YEL)); c.drawPath(st, P(NAVY, 255, 2 * s))



GRID = [(x, y) for y in (650, 905, 1160) for x in (165, 395, 625, 855)]


def room(c, lit, glow_t=None, shake=0.0):
    c.drawColor(C('#E6F2F8'))
    for k, (x, y) in enumerate(GRID):
        rrect(c, x - 110, y - 8, x + 110, y + 70, 12, P(WOOD))
        rrect(c, x - 110, y - 8, x + 110, y + 70, 12, P(NAVY, 255, 5))
    for k, (x, y) in enumerate(GRID):
        L = lit.get(k, 0.0)
        hood = CORAL if L > 0.5 else GREY
        bust(c, x, y, 0.82, hood, SKINS[k % 5], HAIRS[(k * 3) % 5], look=(0, 0.3), glow=L,
             mood='o' if L > 0.5 else 'neutral')
        rrect(c, x - 118, y - 4, x + 118, y + 22, 10, P('#E0A465')); rrect(c, x - 118, y - 4, x + 118, y + 22, 10, P(NAVY, 255, 5))



def mini_mika(c, x, y, s):
    rrect(c, x - 34 * s, y + 10 * s, x + 34 * s, y + 70 * s, 22 * s, P(MUSTARD))
    c.drawCircle(x, y - 14 * s, 28 * s, P('#F5C6A5'))
    a = skia.Path(); a.addArc(skia.Rect.MakeLTRB(x - 28 * s, y - 42 * s, x + 28 * s, y + 14 * s), 190, 160); a.close(); c.drawPath(a, P('#2A2233'))
    c.drawCircle(x - 9 * s, y - 10 * s, 3.5 * s, P(NAVY)); c.drawCircle(x + 9 * s, y - 10 * s, 3.5 * s, P(NAVY))



def icon_splat(c, x, y, s):
    p = skia.Path()
    for k in range(16):
        rr = (34 if k % 2 == 0 else 22) * s; a = math.radians(k * 22.5)
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); c.drawPath(p, P(CORAL)); c.drawPath(p, P(NAVY, 255, 4 * s))


def icon_x(c, x, y, s):
    c.drawCircle(x, y, 34 * s, P('#FFFFFF')); c.drawCircle(x, y, 34 * s, P(NAVY, 255, 4 * s))
    c.drawLine(x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s, P(CORAL, 255, 9 * s)); c.drawLine(x + 14 * s, y - 14 * s, x - 14 * s, y + 14 * s, P(CORAL, 255, 9 * s))


def icon_trip(c, x, y, s):
    c.drawCircle(x, y, 34 * s, P(YEL)); c.drawCircle(x, y, 34 * s, P(NAVY, 255, 4 * s))
    c.drawLine(x, y - 18 * s, x, y + 4 * s, P(NAVY, 255, 8 * s)); c.drawCircle(x, y + 17 * s, 5 * s, P(NAVY))



def stage(c, figs, lit, zoom=1.0, focus=(540, 960), seats=True, beamboost=0.0):
    c.drawColor(C('#24304F'))
    # back wall gradient
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 300), skia.Point(0, 1300)], [C('#2B3A60'), C('#1A2340')]))
    c.drawRect(skia.Rect.MakeWH(W, H), g)
    fy = figs[0][1]
    fl = skia.Path(); fl.moveTo(-200, fy - 40); fl.lineTo(W + 200, fy - 40); fl.lineTo(W + 400, fy + 160); fl.lineTo(-400, fy + 160); fl.close()
    c.drawPath(fl, P(WOOD)); c.drawPath(fl, P(NAVY, 255, 6))
    for k in range(-3, 10):
        c.drawLine(140 * k, fy - 40, 140 * k + (140 * k - 540) * 0.35, fy + 160, P(NAVY, 70, 4))
    # curtains
    for side in (-1, 1):
        cp = skia.Path(); xe = 0 if side < 0 else W; xi = 190 if side < 0 else W - 190
        cp.moveTo(xe, 150); cp.lineTo(xi, 150); cp.quadTo(xi - side * 60, 700, xi + side * 30, fy - 40); cp.lineTo(xe, fy - 40); cp.close()
        c.drawPath(cp, P(CORAL)); c.drawPath(cp, P(NAVY, 255, 6))
        for k in range(1, 4):
            xx = xe + (xi - xe) * k / 4
            c.drawLine(xx, 160, xx - side * 10, fy - 50, P('#D9503F', 255, 6))
    rrect(c, -20, 120, W + 20, 240, 20, P('#E0564A')); rrect(c, -20, 120, W + 20, 240, 20, P(NAVY, 255, 6))
    for i, (x, y, s) in enumerate(figs):
        person(c, x, y, s, MUSTARD if i == 0 else HOODS[i], SKINS[i % 5] if i else '#F5C6A5', '#2A2233' if i == 0 else HAIRS[i % 5],
               tuft=(i == 0), lamp=True, lamp_on=lit.get(i, 0) > 0.5, look=(0, 0.2), mood='smile' if lit.get(i, 0) > 0.5 else 'neutral')
    dim(c, 120)
    for i, (x, y, s) in enumerate(figs):
        L = lit.get(i, 0)
        if L <= 0: continue
        lx, ly = x + 58 * s - 16 * s, y - 520 * s + 18 * s
        beam(c, lx, ly, 26 * s, x, y, 330 * s, a=min(1, L + beamboost))
        person(c, x, y, s, MUSTARD if i == 0 else HOODS[i], SKINS[i % 5] if i else '#F5C6A5', '#2A2233' if i == 0 else HAIRS[i % 5],
               tuft=(i == 0), lamp=True, lamp_on=True, look=(0, 0.2), mood='smile')
    if seats:
        for r, yy in enumerate((fy + 260, fy + 400, fy + 540)):
            for k in range(-1, 9):
                x = 70 + k * 130 + (65 if r % 2 else 0)
                rrect(c, x - 52, yy, x + 52, yy + 120, 26, P(SKY)); rrect(c, x - 52, yy, x + 52, yy + 120, 26, P(NAVY, 255, 6))


