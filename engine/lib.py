"""Reel engine: shared drawing library (style-lock, characters, props, text).
Episodes do `from lib import *` and define their own scene functions."""
import skia, math, os
W, H, FPS = 1080, 1920, 30
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ---------------------------------------------------------------- style
def C(h, a=255):
    return skia.Color(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), int(max(0, min(255, a))))


CREAM, CORAL, SKY, YEL, NAVY = '#FFF4E0', '#FF6B5B', '#4FC3F7', '#FFD54F', '#1E2A47'
MUSTARD, FLOOR, WOOD, GREY = '#F2B630', '#F6E3C4', '#C98B4E', '#B7C0CF'
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


def rrect(c, x0, y0, x1, y1, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r), paint)


def outlined(draw, fill, sw):
    draw(P(fill)); draw(P(NAVY, 255, sw))


def cam(c, z, fx, fy, cx=540, cy=960):
    c.translate(cx, cy); c.scale(z, z); c.translate(-fx, -fy)


# ---------------------------------------------------------------- characters
def head(c, x, y, r, skin, hair, look=(0, 0), eyes='dot', blush=False, sweat=False, mood='neutral', tuft=False):
    s = r / 60
    outlined(lambda p: c.drawCircle(x, y, r, p), skin, 6 * s)
    # hair cap
    if hair:
        path = skia.Path()
        path.addArc(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), 190, 160)
        path.close()
        c.drawPath(path, P(hair))
        if tuft:
            t = skia.Path(); t.moveTo(x - 8 * s, y - r + 4 * s); t.quadTo(x + 5 * s, y - r - 34 * s, x + 30 * s, y - r - 22 * s)
            t.quadTo(x + 18 * s, y - r - 4 * s, x + 22 * s, y - r + 8 * s); t.close(); c.drawPath(t, P(hair))
        c.drawCircle(x, y, r, P(NAVY, 255, 6 * s))
    lx, ly = look
    if eyes == 'dot':
        for dx in (-21, 21):
            c.drawCircle(x + (dx + lx * 7) * s, y + (6 + ly * 6) * s, 7.5 * s, P(NAVY))
    else:  # big staring eyes
        for dx in (-23, 23):
            c.drawCircle(x + dx * s, y + 4 * s, 17 * s, P('#FFFFFF'))
            c.drawCircle(x + dx * s, y + 4 * s, 17 * s, P(NAVY, 255, 4 * s))
            c.drawCircle(x + (dx + lx * 8) * s, y + (4 + ly * 8) * s, 8 * s, P(NAVY))
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
        d = skia.Path(); sx, sy = x + r * 0.78, y - r * 0.25
        d.moveTo(sx, sy - 18 * s); d.quadTo(sx + 12 * s, sy + 2 * s, sx, sy + 8 * s); d.quadTo(sx - 12 * s, sy + 2 * s, sx, sy - 18 * s)
        c.drawPath(d, P(SKY)); c.drawPath(d, P(NAVY, 255, 3 * s))


def person(c, x, y, s, hood, skin, hair, look=(0, 0), eyes='dot', walk=0.0, blush=False, sweat=False,
           mood='neutral', tuft=False, lamp=False, lamp_on=False, shirt=None):
    """standing figure, (x,y) = feet baseline centre"""
    sw = 6 * s
    # legs
    for i, dx in enumerate((-30, 30)):
        lift = max(0, math.sin(walk + i * math.pi)) * 18 * s
        sh = math.sin(walk + i * math.pi) * 14 * s
        rrect(c, x + dx * s - 19 * s + sh, y - 95 * s - lift, x + dx * s + 19 * s + sh, y - lift - 8 * s, 18 * s, P(NAVY))
        c.drawOval(skia.Rect.MakeLTRB(x + dx * s - 30 * s + sh, y - 26 * s - lift, x + dx * s + 30 * s + sh, y - lift), P('#FFFFFF'))
        c.drawOval(skia.Rect.MakeLTRB(x + dx * s - 30 * s + sh, y - 26 * s - lift, x + dx * s + 30 * s + sh, y - lift), P(NAVY, 255, 4 * s))
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
        sway = math.sin(walk + (0 if sg < 0 else math.pi)) * 12 * s
        c.drawLine(x + dx * s * 0.85, y - 225 * s, x + dx * s + sway, y - 120 * s, P(NAVY, 255, 38 * s))
        c.drawLine(x + dx * s * 0.85, y - 225 * s, x + dx * s + sway, y - 120 * s, P(armc, 255, 26 * s))
        c.drawCircle(x + dx * s + sway, y - 112 * s, 14 * s, P(skin)); c.drawCircle(x + dx * s + sway, y - 112 * s, 14 * s, P(NAVY, 255, 4 * s))
    # body
    bc = hood if shirt is None else shirt
    rrect(c, x - 78 * s, y - 250 * s, x + 78 * s, y - 82 * s, 46 * s, P(bc))
    rrect(c, x - 78 * s, y - 250 * s, x + 78 * s, y - 82 * s, 46 * s, P(NAVY, 255, sw))
    if shirt is None:  # hoodie pocket + strings
        rrect(c, x - 40 * s, y - 150 * s, x + 40 * s, y - 108 * s, 14 * s, P(NAVY, 60))
        c.drawLine(x - 14 * s, y - 238 * s, x - 16 * s, y - 200 * s, P('#FFFFFF', 230, 5 * s))
        c.drawLine(x + 14 * s, y - 238 * s, x + 16 * s, y - 200 * s, P('#FFFFFF', 230, 5 * s))
    head(c, x, y - 310 * s, 62 * s, skin, hair, look, eyes, blush, sweat, mood, tuft)


def mika(c, x, y, s, **kw):
    kw.setdefault('tuft', True)
    person(c, x, y, s, MUSTARD, '#F5C6A5', '#2A2233', **kw)


def bust(c, x, y, s, hood, skin, hair, look=(0, 0), eyes='dot', mood='neutral', glow=0.0):
    """head + shoulders; (x,y) = shoulder base"""
    if glow > 0:
        g = skia.Paint(AntiAlias=True)
        g.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y - 110 * s), 190 * s,
                    [C(YEL, int(200 * glow)), C(YEL, 0)]))
        c.drawCircle(x, y - 110 * s, 190 * s, g)
    pth = skia.Path(); pth.moveTo(x - 95 * s, y); pth.cubicTo(x - 95 * s, y - 110 * s, x + 95 * s, y - 110 * s, x + 95 * s, y); pth.close()
    c.drawPath(pth, P(hood)); c.drawPath(pth, P(NAVY, 255, 6 * s))
    head(c, x, y - 140 * s, 58 * s, skin, hair, look, eyes, mood=mood)


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


def ost(c, text, t, t0=0.12):
    """on-screen headline: navy plate, white text, pop-in"""
    if t < t0: return
    k = eback((t - t0) / 0.22)
    font, parts, x, y, wtot, size = draw_rich(c, text, 540, 300, 92, F_OST, '#FFFFFF', YEL, max_w=900)
    c.save(); c.translate(540, 300); c.scale(k, k); c.rotate(-2.0); c.translate(-540, -300)
    pad = 34
    rrect(c, x - pad, 300 - size * 0.62 - 14, x + wtot + pad, 300 + size * 0.62 + 6, 26, P(NAVY))
    for p, hl in parts:
        c.drawString(p, x, y, font, P(YEL if hl else '#FFFFFF'))
        x += font.measureText(p)
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
    rrect(c, x - 30, 1470 - 58, x + wtot + 30, 1470 + 52, 30, P(NAVY, 238))
    for p, hl in parts:
        c.drawString(p, x, y, font, P(YEL if hl else '#FFFFFF'))
        x += font.measureText(p)
    c.restore()


# ---------------------------------------------------------------- environments
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


