"""Episode 003 – The Cocktail Party Effect (EN). Hook type: hard number ("1 in 3")."""
import math, skia
from lib import *

META = {
    "id": "003-cocktail-party-effect",
    "topic": "Cocktail party effect – only about 1 in 3 people notice their own name in a voice they're ignoring; fewer with high working memory",
    "source": "Moray (1959), Quarterly Journal of Experimental Psychology 11; Wood & Cowan (1995), Journal of Experimental Psychology: Learning, Memory, and Cognition 21; Conway, Cowan & Bunting (2001), Psychonomic Bulletin & Review 8(2); Röer & Cowan (2021), JEP: LMC (preregistered replication); background: Cherry (1953), Journal of the Acoustical Society of America 25",
    "youtube_title": "Only 1 in 3 people notice their name when not listening #shorts",
    "youtube_description": "The cocktail party effect: your name seems to cut through any noise – but in the lab, only about 1 in 3 people notice it. People repeated a voice in one ear and ignored a voice in the other; when the ignored voice said their name, 33% noticed (Moray, 1959, Quarterly Journal of Experimental Psychology), 35% in Wood & Cowan (1995, Journal of Experimental Psychology: Learning, Memory, and Cognition) and 29% in a preregistered replication (Röer & Cowan, 2021, same journal). The twist: 65% of people with low working memory capacity noticed their name vs. just 20% with high capacity (Conway, Cowan & Bunting, 2001, Psychonomic Bulletin & Review) – strong focus filters more out. The 'cocktail party problem' goes back to Cherry (1953, Journal of the Acoustical Society of America). Send this to someone who never hears you calling their name. #psychology #cocktailpartyeffect #brain #shorts",
    "tiktok_caption": "Only 1 in 3 people notice their own name in a voice they're ignoring (Moray, 1959; Wood & Cowan, 1995). And people with stronger focus noticed it LESS: 20% vs 65% (Conway, Cowan & Bunting, 2001, Psychonomic Bulletin & Review). Send this to someone who never hears you calling their name. #psychology #cocktailpartyeffect #brain #fyp",
}
VOICE, SPEED = "af_heart", 1.1

# one spoken line per scene (12 scenes); last line flows back into line 1 (loop)
LINES = [
"Only one in three people notice their name when they're not listening.",
"Loud cafeteria. You're tuning out every voice.",
"Then someone says your name… and your head snaps around. Right?",
"Not for most people. And who misses it is surprising.",
"To test the cocktail party effect, scientists used two voices, one per ear.",
"Repeat the right ear. Ignore the left. Then the left says your name.",
"About one in three noticed. Two thirds never did.",
"The twist? People with stronger focus noticed it less.",
"Low working memory: sixty-five percent noticed. High: just twenty.",
"Your brain quietly checks ignored voices for one word: your name.",
"Tight focus blocks it out. A wandering mind lets it through.",
"So next time the cafeteria's roaring, remember:",
]
CAPS = [
    ["Only *one in three*", "people notice", "their *name*", "when they're", "*not listening*."],
    ["Loud *cafeteria*.", "You're tuning out", "*every voice*."],
    ["Then someone", "says your *name*…", "and your head", "*snaps around*.", "Right?"],
    ["*Not* for", "most people.", "And *who misses it*", "is *surprising*."],
    ["To test the", "*cocktail party effect*,", "scientists used", "*two voices*,", "one per *ear*."],
    ["Repeat the", "*right* ear.", "*Ignore* the left.", "Then the left", "says your *name*."],
    ["About", "*one in three*", "noticed.", "*Two thirds*", "never did."],
    ["The *twist*?", "People with", "*stronger focus*", "noticed it *less*."],
    ["Low working memory:", "*65%* noticed.", "High:", "just *20%*."],
    ["Your brain", "*quietly checks*", "ignored voices", "for one word:", "your *name*."],
    ["*Tight focus*", "blocks it out.", "A *wandering mind*", "lets it *through*."],
    ["So next time", "the cafeteria's", "*roaring*,", "remember:"],
]
TAIL = [0.22, 0.22, 0.25, 0.22, 0.22, 0.25, 0.4, 0.22, 0.4, 0.22, 0.22, 0.45]

MSKIN, MHAIR = '#F5C6A5', '#2A2233'
CAFE, TILE, TILE_L = '#FFE6D2', '#FBD3B8', '#F2BE9C'
LAB, LAB_L = '#E4F2FA', '#CFE6F3'
MINT = '#7FCB8A'


# ---------------------------------------------------------------- helpers
def R(x0, y0, x1, y1):
    return skia.Rect.MakeLTRB(x0, y0, x1, y1)


def text(c, s, x, y, size, col=NAVY, tf=None, align='c', a=255):
    f = skia.Font(tf or F_OST, size); w = f.measureText(s)
    xx = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    c.drawString(s, xx, y + size * 0.36, f, P(col, a))
    return w


def tag(c, s, x, y, size, bg, fg='#FFFFFF', k=1.0, rot=0, a=255):
    if k <= 0: return
    f = skia.Font(F_OST, size); w = f.measureText(s)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    rrect(c, -w / 2 - 22, -size * 0.66, w / 2 + 22, size * 0.62, 18, P(bg, a))
    rrect(c, -w / 2 - 22, -size * 0.66, w / 2 + 22, size * 0.62, 18, P(NAVY, a, 5))
    c.drawString(s, -w / 2, size * 0.34, f, P(fg, a))
    c.restore()


def burst(c, x, y, u, r=90, col=YEL, n=10):
    if u <= 0 or u >= 1: return
    for k in range(n):
        a = math.radians(k * 360 / n + 9)
        r0, r1 = r * (0.4 + 0.8 * u), r * (0.7 + 1.0 * u)
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(col, 255 * (1 - u), 9))
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(NAVY, 255 * (1 - u), 3))


def rings(c, x, y, t, r0=40, gap=60, n=3, col=YEL, period=0.6, w=8):
    """expanding sound rings"""
    for k in range(n):
        u = ((t / period) + k / n) % 1.0
        c.drawCircle(x, y, r0 + gap * n * u, P(col, 255 * (1 - u), w * (1 - 0.5 * u)))


def lerp_col(a, b, u):
    u = clamp(u)
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{int(ca[i] + (cb[i] - ca[i]) * u):02X}' for i in range(3))


def gib_bubble(c, x, y, s, kind=0, grey=0.0, a=255):
    """chatter speech bubble (centre x,y)"""
    bg = lerp_col('#FFFFFF', '#E3E1DD', grey); ink = lerp_col([CORAL, SKY, '#7FB7A4', '#B98AE6', CORAL][kind % 5], '#B9B4AC', grey)
    w, h = 76 * s, 46 * s
    tl = skia.Path(); sd = -1 if kind % 2 else 1
    tl.moveTo(x + sd * 10 * s, y + h - 6 * s); tl.lineTo(x + sd * 36 * s, y + h + 22 * s); tl.lineTo(x + sd * 34 * s, y + h - 6 * s); tl.close()
    c.drawPath(tl, P(bg, a)); c.drawPath(tl, P(NAVY, a * (1 - 0.5 * grey), 4 * s))
    rrect(c, x - w, y - h, x + w, y + h, 30 * s, P(bg, a)); rrect(c, x - w, y - h, x + w, y + h, 30 * s, P(NAVY, a * (1 - 0.5 * grey), 4.5 * s))
    k = kind % 4
    if k == 0:
        f = skia.Font(F_OST, 34 * s); ww = f.measureText("BLA BLA"); c.drawString("BLA BLA", x - ww / 2, y + 12 * s, f, P(ink, a))
    elif k == 1:
        for d in (-1, 0, 1): c.drawCircle(x + d * 28 * s, y, 9 * s, P(ink, a))
    elif k == 2:
        f = skia.Font(F_OST, 36 * s); ww = f.measureText("HAHA"); c.drawString("HAHA", x - ww / 2, y + 13 * s, f, P(ink, a))
    else:
        zz = skia.Path(); zz.moveTo(x - 50 * s, y)
        for q in range(1, 9): zz.lineTo(x - 50 * s + q * 12.5 * s, y + (14 if q % 2 else -14) * s)
        c.drawPath(zz, P(ink, a, 6 * s))


def name_bubble(c, x, y, s, k=1.0, rot=0, label="MIKA!"):
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k * s, k * s)
    f = skia.Font(F_OST, 62); w = f.measureText(label)
    tl = skia.Path(); tl.moveTo(-30, 40); tl.lineTo(-70, 92); tl.lineTo(10, 44); tl.close()
    c.drawPath(tl, P(YEL)); c.drawPath(tl, P(NAVY, 255, 6))
    rrect(c, -w / 2 - 34, -52, w / 2 + 34, 52, 40, P(YEL)); rrect(c, -w / 2 - 34, -52, w / 2 + 34, 52, 40, P(NAVY, 255, 7))
    c.drawString(label, -w / 2, 22, f, P(NAVY))
    c.restore()


def word_chip(c, s, x, y, size, bg, fg=NAVY, a=255, k=1.0):
    if k <= 0 or a <= 0: return
    f = skia.Font(F_OST, size); w = f.measureText(s)
    c.save(); c.translate(x, y); c.scale(k, k)
    rrect(c, -w / 2 - 18, -size * 0.62, w / 2 + 18, size * 0.6, 16, P(bg, a))
    rrect(c, -w / 2 - 18, -size * 0.62, w / 2 + 18, size * 0.6, 16, P(NAVY, a, 4))
    c.drawString(s, -w / 2, size * 0.34, f, P(fg, a))
    c.restore()


# chatter spots for the cafeteria: (x, y, kind, period, phase, scale)
SPOTS = [(150, 540, 0, 1.7, 0.0, 1.0), (930, 560, 2, 1.9, 0.6, 1.0), (300, 735, 1, 1.5, 1.1, 0.9), (790, 720, 3, 1.6, 0.3, 0.95),
         (540, 700, 2, 2.1, 1.5, 0.85), (110, 820, 3, 1.8, 0.9, 0.85), (980, 840, 0, 1.75, 1.4, 0.8), (430, 840, 0, 2.0, 0.2, 0.8),
         (680, 860, 1, 1.65, 0.75, 0.8)]
EXTRA = [(220, 640, 2, 1.3, 0.4, 0.8), (870, 640, 1, 1.4, 0.1, 0.8), (600, 560, 3, 1.2, 0.9, 0.75), (360, 600, 1, 1.35, 0.5, 0.75),
         (60, 680, 0, 1.25, 0.2, 0.7), (1010, 700, 2, 1.45, 0.8, 0.7)]


def chatter(c, t, spots, grey=0.0, amp=1.0, a_mul=1.0):
    for (x, y, kind, per, ph, s) in spots:
        u = ((t + ph) % per) / per
        lt = u * per
        k = eback(lt / 0.18) * amp
        a = 255 * clamp((1 - u) / 0.25) * a_mul
        if a <= 0 or k <= 0: continue
        gib_bubble(c, x, y - 34 * u, s * k, kind, grey, a)


def cafe_bg(c, t):
    c.drawColor(C(CAFE))
    c.drawRect(R(0, 700, W, 1010), P(TILE))
    for x in range(0, W + 1, 90): c.drawLine(x, 700, x, 1010, P(TILE_L, 255, 3))
    for y in (778, 856, 934): c.drawLine(0, y, W, y, P(TILE_L, 255, 3))
    c.drawLine(0, 700, W, 700, P(NAVY, 255, 5))
    # menu board (no brands)
    rrect(c, 300, 470, 780, 655, 18, P(NAVY)); rrect(c, 314, 484, 766, 641, 12, P('#2B3A60'))
    text(c, "MENU", 540, 508, 30, YEL)
    for k, (ix, price) in enumerate(((380, "1.50"), (540, "2.00"), (700, "0.80"))):
        iy = 568
        if k == 0:
            c.drawCircle(ix, iy, 30, P(CORAL)); c.drawCircle(ix, iy, 30, P(NAVY, 255, 4)); c.drawLine(ix, iy - 30, ix + 8, iy - 44, P('#7FB7A4', 255, 7))
        elif k == 1:
            p = skia.Path(); p.moveTo(ix - 34, iy - 26); p.lineTo(ix + 34, iy - 26); p.lineTo(ix, iy + 34); p.close()
            c.drawPath(p, P(YEL)); c.drawPath(p, P(NAVY, 255, 4))
            for dx, dy in ((-10, -12), (10, -10), (0, 6)): c.drawCircle(ix + dx, iy + dy, 6, P(CORAL))
        else:
            rrect(c, ix - 22, iy - 30, ix + 22, iy + 32, 5, P('#FFFFFF')); rrect(c, ix - 22, iy - 30, ix + 22, iy + 32, 5, P(NAVY, 255, 4))
            c.drawRect(R(ix - 22, iy - 4, ix + 22, iy + 10), P(SKY))
        text(c, price, ix, 618, 24, '#FFFFFF')
    # pendant lamps
    for lx in (110, 970):
        c.drawLine(lx, 0, lx, 380, P(NAVY, 255, 5))
        sh = skia.Path(); sh.addArc(R(lx - 60, 350, lx + 60, 470), 180, 180); sh.close()
        c.drawPath(sh, P(YEL)); c.drawPath(sh, P(NAVY, 255, 5))
    c.drawRect(R(0, 1340, W, H), P(FLOOR)); c.drawLine(0, 1340, W, 1340, P(NAVY, 255, 6))


BACK_XS = [95, 250, 410, 670, 830, 985]


def crowd_row(c, t, y, s, xs, seed=0, grey=0.0):
    for n, x in enumerate(xs):
        k = (n + seed) % 5
        bob = 5 * math.sin(t * 7 + n * 1.7)
        talking = int((t * 4 + n * 0.7)) % 2 == 0
        hood = lerp_col(HOODS[k], '#C9CDD6', grey)
        bust(c, x, y + bob, s, hood, SKINS[k], HAIRS[(k * 3) % 5], look=(math.sin(n * 2.1) * 0.6, 0), mood='o' if talking else 'smile')
    rrect(c, -30, y - 36, W + 30, y + 30, 12, P(WOOD)); rrect(c, -30, y - 36, W + 30, y + 30, 12, P(NAVY, 255, 5))
    rrect(c, -30, y - 50, W + 30, y - 26, 10, P('#E0A465')); rrect(c, -30, y - 50, W + 30, y - 26, 10, P(NAVY, 255, 5))


def mika_bust(c, x, y, s, look=(0, 0), eyes='dot', mood='neutral', glow=0.0, rot=0.0, sweat=False, blush=False):
    c.save(); c.translate(x, y); c.rotate(rot); c.translate(-x, -y)
    if glow > 0:
        g = skia.Paint(AntiAlias=True)
        g.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y - 110 * s), 210 * s, [C(YEL, int(230 * glow)), C(YEL, 0)]))
        c.drawCircle(x, y - 110 * s, 210 * s, g)
    pth = skia.Path(); pth.moveTo(x - 95 * s, y); pth.cubicTo(x - 95 * s, y - 110 * s, x + 95 * s, y - 110 * s, x + 95 * s, y); pth.close()
    c.drawPath(pth, P(MUSTARD)); c.drawPath(pth, P(NAVY, 255, 6 * s))
    c.drawLine(x - 14 * s, y - 70 * s, x - 16 * s, y - 34 * s, P('#FFFFFF', 230, 5 * s)); c.drawLine(x + 14 * s, y - 70 * s, x + 16 * s, y - 34 * s, P('#FFFFFF', 230, 5 * s))
    head(c, x, y - 140 * s, 58 * s, MSKIN, MHAIR, look, eyes, blush=blush, sweat=sweat, mood=mood, tuft=True)
    c.restore()


def back_mika(c, x, y, r, phones=None, cupL=CORAL, cupR=SKY, glowL=0.0, glowR=0.0):
    """Mika seen from behind; (x,y) = head centre, r = head radius. phones = vertical offset of headphones (None = none)"""
    sh = skia.Path(); sh.moveTo(x - 1.45 * r, y + 2.55 * r); sh.cubicTo(x - 1.45 * r, y + 0.85 * r, x + 1.45 * r, y + 0.85 * r, x + 1.45 * r, y + 2.55 * r); sh.close()
    c.drawPath(sh, P(MUSTARD)); c.drawPath(sh, P(NAVY, 255, 0.1 * r))
    hood = skia.Path(); hood.moveTo(x - 0.75 * r, y + 1.0 * r); hood.quadTo(x, y + 1.9 * r, x + 0.75 * r, y + 1.0 * r)
    c.drawPath(hood, P('#D99A1E', 255, 0.09 * r))
    rrect(c, x - 0.32 * r, y + 0.6 * r, x + 0.32 * r, y + 1.15 * r, 0.12 * r, P(MSKIN)); rrect(c, x - 0.32 * r, y + 0.6 * r, x + 0.32 * r, y + 1.15 * r, 0.12 * r, P(NAVY, 255, 0.07 * r))
    for sd in (-1, 1):
        c.drawCircle(x + sd * 0.98 * r, y + 0.12 * r, 0.22 * r, P(MSKIN)); c.drawCircle(x + sd * 0.98 * r, y + 0.12 * r, 0.22 * r, P(NAVY, 255, 0.06 * r))
    c.drawCircle(x, y, r, P(MSKIN))
    c.save(); c.clipRect(R(x - r - 20, y - r - 80, x + r + 20, y + 0.62 * r))
    c.drawCircle(x, y, r, P(MHAIR)); c.restore()
    tf = skia.Path(); tf.moveTo(x - 0.15 * r, y - 0.95 * r); tf.quadTo(x + 0.1 * r, y - 1.5 * r, x + 0.5 * r, y - 1.32 * r); tf.quadTo(x + 0.3 * r, y - 1.05 * r, x + 0.35 * r, y - 0.85 * r); tf.close()
    c.drawPath(tf, P(MHAIR))
    c.drawCircle(x, y, r, P(NAVY, 255, 0.1 * r))
    for gl, sd in ((glowL, -1), (glowR, 1)):
        if gl > 0:
            g = skia.Paint(AntiAlias=True); gx = x + sd * 1.05 * r; gy = y + 0.12 * r
            g.setShader(skia.GradientShader.MakeRadial(skia.Point(gx, gy), 0.9 * r, [C(YEL, int(240 * gl)), C(YEL, 0)]))
            c.drawCircle(gx, gy, 0.9 * r, g)
    if phones is not None:
        dy = phones
        band = skia.Path(); band.addArc(R(x - 1.08 * r, y - 1.22 * r + dy, x + 1.08 * r, y + 1.0 * r + dy), 180, 180)
        c.drawPath(band, P(NAVY, 255, 0.24 * r)); c.drawPath(band, P('#5A6478', 255, 0.13 * r))
        for sd, col in ((-1, cupL), (1, cupR)):
            cx = x + sd * 1.06 * r; cy = y + 0.12 * r + dy
            rrect(c, cx - 0.2 * r, cy - 0.36 * r, cx + 0.2 * r, cy + 0.36 * r, 0.16 * r, P(col)); rrect(c, cx - 0.2 * r, cy - 0.36 * r, cx + 0.2 * r, cy + 0.36 * r, 0.16 * r, P(NAVY, 255, 0.07 * r))


def lab_bg(c):
    c.drawColor(C(LAB))
    for x in range(0, W + 1, 60): c.drawLine(x, 0, x, H, P(LAB_L, 255, 2))
    for y in range(0, H + 1, 60): c.drawLine(0, y, W, y, P(LAB_L, 255, 2))
    c.drawRect(R(0, 1330, W, H), P('#C9D7E6')); c.drawLine(0, 1330, W, 1330, P(NAVY, 255, 6))


def mini_person(c, x, y, s, col, face=MSKIN, mark=None):
    rrect(c, x - 34 * s, y - 10 * s, x + 34 * s, y + 66 * s, 26 * s, P(col)); rrect(c, x - 34 * s, y - 10 * s, x + 34 * s, y + 66 * s, 26 * s, P(NAVY, 255, 5 * s))
    c.drawCircle(x, y - 40 * s, 30 * s, P(face)); c.drawCircle(x, y - 40 * s, 30 * s, P(NAVY, 255, 5 * s))
    if mark == 'x':
        for dx in (-10, 10):
            c.drawLine(x + (dx - 5) * s, y - 46 * s, x + (dx + 5) * s, y - 36 * s, P(NAVY, 255, 3.5 * s))
            c.drawLine(x + (dx + 5) * s, y - 46 * s, x + (dx - 5) * s, y - 36 * s, P(NAVY, 255, 3.5 * s))
    elif mark == 'o':
        for dx in (-10, 10): c.drawCircle(x + dx * s, y - 42 * s, 5 * s, P(NAVY))
        c.drawOval(R(x - 5 * s, y - 32 * s, x + 5 * s, y - 20 * s), P(NAVY))
    else:
        for dx in (-10, 10): c.drawCircle(x + dx * s, y - 40 * s, 4 * s, P(NAVY))


def brain(c, x, y, s, col='#F7A8B8'):
    p = skia.Path()
    for dx, dy, r in ((-90, -30, 80), (-20, -70, 85), (70, -50, 82), (110, 30, 70), (30, 50, 80), (-70, 50, 75)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p.setFillType(skia.PathFillType.kWinding)
    c.drawPath(p, P(NAVY, 255, 14 * s)); c.drawPath(p, P(col))
    for (ax, ay, bx, by, cx2, cy2) in ((-120, -20, -60, -80, -20, -20), (0, -110, 30, -40, 90, -80), (40, 10, 90, 60, 140, 20), (-110, 60, -50, 20, 0, 80)):
        q = skia.Path(); q.moveTo(x + ax * s, y + ay * s); q.quadTo(x + bx * s, y + by * s, x + cx2 * s, y + cy2 * s)
        c.drawPath(q, P('#D9768B', 255, 9 * s))


# ---------------------------------------------------------------- scenes
FRONT = [(230, 0), (540, -1), (850, 3)]     # (x, hood index; -1 = Mika)


def s1(c, t, D):
    """hook: three students, only one hears the name. Valid for t < 0 (s12 runs into it)."""
    hear = 1.52
    z = 1.0
    if t >= 2.04: z = 1.0 + 0.12 * eout((t - 2.04) / 0.2)
    c.save(); cam(c, z, 540, 1147, cx=540, cy=1147)
    cafe_bg(c, t)
    crowd_row(c, t, 1010, 0.62, BACK_XS)
    g = clamp((t - hear) / 0.3) if t > hear else 0.0
    chatter(c, t, SPOTS, grey=g)
    for n, (x, k) in enumerate(FRONT):
        bob = 4 * math.sin(t * 5 + n * 2.0)
        if k < 0:
            lit = t >= hear + 0.1
            mika_bust(c, x, 1350 + bob, 1.45, look=(0.8, -0.7) if lit else (0, 0.35), eyes='big' if lit else 'dot',
                      mood='o' if lit else 'neutral', glow=eout((t - hear - 0.1) / 0.25) if lit else 0.0,
                      rot=-6 * eout((t - hear - 0.1) / 0.15) if lit else 0)
        else:
            bust(c, x, 1350 + bob, 1.45, HOODS[k], SKINS[k + 1], HAIRS[k], look=(0, 0.45), mood='neutral')
    # front table + trays
    rrect(c, -30, 1334, W + 30, 1378, 14, P(WOOD)); rrect(c, -30, 1334, W + 30, 1378, 14, P(NAVY, 255, 6))
    rrect(c, -30, 1316, W + 30, 1344, 12, P('#E0A465')); rrect(c, -30, 1316, W + 30, 1344, 12, P(NAVY, 255, 5))
    for x, _ in FRONT:
        rrect(c, x - 100, 1292, x + 100, 1326, 10, P('#9FB2C8')); rrect(c, x - 100, 1292, x + 100, 1326, 10, P(NAVY, 255, 4))
        c.drawCircle(x - 45, 1296, 18, P(CORAL)); rrect(c, x + 10, 1280, x + 66, 1306, 8, P(YEL))
    # name bubble flies in
    if t >= hear - 0.3:
        u = eout((t - hear + 0.3) / 0.3)
        bx = 1180 + (800 - 1180) * u; by = 520 + (850 - 520) * u
        if t >= hear: rings(c, 800, 850, t - hear, r0=60, gap=55, n=3, col=YEL, period=0.7)
        name_bubble(c, bx, by, 1.0, k=1.0, rot=-8 + 3 * math.sin(t * 8))
        burst(c, 800, 850, (t - hear) / 0.35, r=130, col=YEL, n=12)
    c.restore()
    # counter badges 1 / 2 / 3, then verdict tags
    verdict = 2.64
    for n, (x, k) in enumerate(FRONT):
        tt = 0.3 + n * 0.16
        if t < tt: continue
        if t < verdict:
            kk = eback((t - tt) / 0.2)
            c.save(); c.translate(x, 985); c.scale(kk, kk)
            c.drawCircle(0, 0, 46, P(NAVY)); text(c, str(n + 1), 0, -2, 58, '#FFFFFF'); c.restore()
        else:
            kk = eback((t - verdict - n * 0.06) / 0.2)
            if k < 0: tag(c, "HEARD IT", x, 985, 46, YEL, fg=NAVY, k=kk, rot=-4)
            else: tag(c, "MISSED", x, 985, 42, GREY, fg=NAVY, k=kk, rot=3 if n else -3)
    ost(c, "ONLY *1 IN 3*", t, 0.12)


def s2(c, t, D):
    tune, every = 1.08, 1.85
    z = 1.18 - 0.18 * eout(t / 0.45)
    c.save(); cam(c, z, 540, 900)
    cafe_bg(c, t)
    crowd_row(c, t, 1010, 0.62, BACK_XS, seed=2)
    crowd_row(c, t + 0.3, 1190, 0.78, [80, 300, 780, 1000], seed=4)
    n_amp = clamp(t / 0.6)
    grey = eout((t - every) / 0.3) if t >= every else 0.0
    chatter(c, t, SPOTS, grey=grey, amp=n_amp)
    chatter(c, t + 0.5, EXTRA, grey=grey, amp=n_amp)
    # Mika front centre
    if t >= tune:
        k = eback((t - tune) / 0.3)
        c.drawCircle(540, 1150, 285 * k, P(SKY, 70)); c.drawCircle(540, 1150, 285 * k, P(SKY, 255, 8))
    bs = 1.5; hs = 58 * bs / 60; hc = 1378 - 140 * bs
    mika_bust(c, 540, 1378, bs, look=(0, 0), mood='smile' if t >= tune else 'neutral')
    if t >= tune:
        # closed-eye lines over the dots (calm)
        for dx in (-21, 21):
            xx = 540 + dx * hs; yy = hc + 6 * hs
            c.drawCircle(xx, yy, 11 * hs, P(MSKIN)); c.drawLine(xx - 10 * hs, yy, xx + 10 * hs, yy, P(NAVY, 255, 5 * hs))
    c.restore()
    # noise meter (left)
    lvl = 0.55 + 0.4 * abs(math.sin(t * 9)) * clamp(t / 0.5)
    if t >= every: lvl = lvl * (1 - 0.0)
    x0, y0, y1 = 60, 520, 980
    rrect(c, x0, y0, x0 + 70, y1, 22, P('#FFFFFF')); rrect(c, x0, y0, x0 + 70, y1, 22, P(NAVY, 255, 6))
    nseg = 10
    for q in range(nseg):
        if q / nseg > lvl: break
        yy = y1 - 16 - (q + 1) * (y1 - y0 - 28) / nseg
        col = MINT if q < 5 else (YEL if q < 8 else CORAL)
        rrect(c, x0 + 12, yy + 4, x0 + 58, yy + (y1 - y0 - 28) / nseg - 2, 8, P(col))
    text(c, "NOISE", x0 + 35, y1 + 40, 32, NAVY)
    # mute icon
    if t >= tune:
        k = eback((t - tune - 0.1) / 0.22)
        c.save(); c.translate(900, 1010); c.scale(k, k)
        c.drawCircle(0, 0, 66, P('#FFFFFF')); c.drawCircle(0, 0, 66, P(NAVY, 255, 6))
        sp = skia.Path(); sp.moveTo(-38, -14); sp.lineTo(-20, -14); sp.lineTo(4, -34); sp.lineTo(4, 34); sp.lineTo(-20, 14); sp.lineTo(-38, 14); sp.close()
        c.drawPath(sp, P(NAVY))
        c.drawLine(16, -16, 40, 16, P(CORAL, 255, 8)); c.drawLine(40, -16, 16, 16, P(CORAL, 255, 8))
        c.restore()
    if t >= every:
        tag(c, "ALL VOICES: OFF", 560, 830, 48, NAVY, fg=YEL, k=eback((t - every) / 0.2), rot=-3)
    ost(c, "TUNED *OUT*" if t >= tune else "LOUD *CAFETERIA*", t, tune if t >= tune else 0.1)


def s3(c, t, D):
    call, snap, right = 0.64, 1.86, 2.71
    sh = 0.0
    if snap <= t < snap + 0.3: sh = 14 * math.sin((t - snap) * 70) * (1 - (t - snap) / 0.3)
    z = 1.0 + 0.04 * clamp(t / 1.8)
    if t >= snap: z = 1.04 + 0.1 * eout((t - snap) / 0.18)
    c.save(); c.translate(sh, 0); cam(c, z, 540, 1093, cx=540, cy=1093)
    cafe_bg(c, t)
    crowd_row(c, t, 1010, 0.62, BACK_XS, seed=1, grey=0.6)
    c.drawRect(R(0, 0, W, H), P(CAFE, 120))
    chatter(c, t, SPOTS[:6], grey=0.8 if t >= call else 0.3)
    snapped = t >= snap
    look = (-0.5, 0.4) if not snapped else (0.95, -0.4)
    rot = 0 if not snapped else -7 * eback((t - snap) / 0.16)
    mika_bust(c, 470, 1380, 2.05, look=look, eyes='big' if snapped else 'dot', mood='o' if snapped else 'neutral', rot=rot,
              glow=0.6 * eout((t - snap) / 0.2) if snapped else 0)
    if snapped and t < snap + 0.45:
        u = (t - snap) / 0.45
        for k in range(4):
            yy = 860 + k * 70
            c.drawLine(150 - 60 * u, yy, 260 - 30 * u, yy - 20, P(NAVY, 255 * (1 - u), 9))
    c.restore()
    if t >= call:
        u = eout((t - call) / 0.28)
        bx = 1250 + (790 - 1250) * u
        rings(c, bx, 600, t - call, r0=70, gap=60, n=3, col=YEL, period=0.6, w=10)
        name_bubble(c, bx, 600, 1.35, rot=-6 + 4 * math.sin(t * 9))
        burst(c, 790, 600, (t - call - 0.2) / 0.35, r=170, col=YEL, n=12)
    if t >= right:
        u = (t - right)
        c.drawRect(R(0, 0, W, H), P(NAVY, 60 * clamp(u / 0.1)))
        k = eback(u / 0.2)
        c.save(); c.translate(860, 1120); c.rotate(12); c.scale(k, k)
        f = skia.Font(F_OST, 260); w = f.measureText("?")
        c.drawString("?", -w / 2 + 8, 98, f, P(NAVY)); c.drawString("?", -w / 2, 90, f, P(CORAL))
        c.restore()
    ost(c, "*RIGHT?*" if t >= right else "YOUR *NAME*", t, right if t >= right else call)


def silhouette(c, x, y, s, a=255):
    person(c, x, y, s, '#33415F', '#33415F', '#26324D', look=(0, 0))


def s4(c, t, D):
    stamp, most, who, surp = 0.1, 0.45, 1.26, 1.99
    c.drawColor(C('#FFF0E4'))
    # radial rays
    for k in range(18):
        a0 = k * 20 + t * 8
        c.drawArc(R(540 - 1400, 900 - 1400, 540 + 1400, 900 + 1400), a0, 10, True, P('#FFE2CC'))
    c.drawRect(R(0, 1300, W, H), P(FLOOR)); c.drawLine(0, 1300, W, 1300, P(NAVY, 255, 6))
    XS = [150, 345, 540, 735, 930]
    for n, x in enumerate(XS):
        tt = most + n * 0.07
        if t < tt: continue
        k = eback((t - tt) / 0.22)
        jit = 6 * math.sin(t * 40 + n) if t >= surp and t < surp + 0.4 else 0
        c.save(); c.translate(x + jit, 1300); c.scale(k, k); c.translate(-x, -1300)
        silhouette(c, x, 1300, 0.72)
        f = skia.Font(F_OST, 70); w = f.measureText("?")
        c.drawString("?", x - w / 2, 1300 - 310 * 0.72 + 26, f, P('#FFFFFF'))
        c.restore()
    # magnifier sweep
    if t >= who:
        u = einout((t - who) / 0.75)
        mx = 120 + 820 * u if t < surp else 740 + 10 * math.sin(t * 6)
        my = 1076 + 18 * math.sin(u * 9)
        k = eback((t - who) / 0.2)
        c.save(); c.translate(mx, my); c.scale(k, k)
        c.drawLine(70, 70, 150, 150, P(NAVY, 255, 34)); c.drawLine(70, 70, 150, 150, P(WOOD, 255, 22))
        c.drawCircle(0, 0, 100, P('#FFFFFF', 70)); c.drawCircle(0, 0, 100, P(NAVY, 255, 14)); c.drawCircle(0, 0, 100, P(SKY, 255, 6))
        c.restore()
    if t >= surp:
        k = eback((t - surp) / 0.22)
        burst(c, 780, 680, (t - surp) / 0.4, r=150, col=YEL, n=12)
        c.save(); c.translate(780, 690); c.rotate(-8); c.scale(k, k)
        c.drawCircle(0, 0, 105, P(YEL)); c.drawCircle(0, 0, 105, P(NAVY, 255, 8)); text(c, "?!", 0, -4, 110, NAVY)
        c.restore()
    # NOT stamp
    if t >= stamp:
        u = t - stamp
        k = 2.2 - 1.2 * eout(u / 0.16)
        out = clamp((u - (most - stamp) - 0.05) / 0.2)
        if out < 1:
            sx, sy = 540 + (300 - 540) * eout(out), 760 + (620 - 760) * eout(out)
            kk = k * (1 - 0.55 * eout(out))
            c.save(); c.translate(sx, sy); c.rotate(-10); c.scale(kk, kk)
            rrect(c, -230, -95, 230, 95, 26, P(CORAL)); rrect(c, -230, -95, 230, 95, 26, P(NAVY, 255, 10))
            rrect(c, -210, -75, 210, 75, 18, P('#FFFFFF', 255, 5))
            text(c, "NOT!", 0, -4, 120, '#FFFFFF')
            c.restore()
    if t < who:
        ost(c, "MOST *MISS* IT", t, most)
    else:
        ost(c, "BUT *WHO*?", t, who)


def party_glass(c, x, y, s, col=CORAL):
    p = skia.Path(); p.moveTo(x - 60 * s, y - 70 * s); p.lineTo(x + 60 * s, y - 70 * s); p.lineTo(x, y); p.close()
    c.drawPath(p, P(col)); c.drawPath(p, P(NAVY, 255, 6 * s))
    c.drawLine(x, y, x, y + 70 * s, P(NAVY, 255, 7 * s)); c.drawLine(x - 30 * s, y + 70 * s, x + 30 * s, y + 70 * s, P(NAVY, 255, 7 * s))
    c.drawLine(x + 20 * s, y - 50 * s, x + 50 * s, y - 110 * s, P(SKY, 255, 8 * s))
    c.drawCircle(x - 30 * s, y - 70 * s, 16 * s, P(YEL)); c.drawCircle(x - 30 * s, y - 70 * s, 16 * s, P(NAVY, 255, 4 * s))


def wave_stream(c, x0, x1, y, t, col, a=255, amp=34, speed=9.0):
    """animated sound wave from x0 to x1"""
    p = skia.Path(); n = 40
    for q in range(n + 1):
        u = q / n; x = x0 + (x1 - x0) * u
        env = math.sin(math.pi * u) ** 0.6
        yy = y + amp * env * math.sin(u * 18 - t * speed) * (0.6 + 0.4 * math.sin(u * 5 + t * 3))
        (p.moveTo if q == 0 else p.lineTo)(x, yy)
    c.drawPath(p, P(NAVY, a, 16)); c.drawPath(p, P(col, a, 9))


def speaker(c, x, y, s, col, flip=1, k=1.0):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k * s * flip, k * s)
    rrect(c, -60, -90, 60, 90, 20, P(NAVY)); c.drawCircle(0, 28, 38, P(col)); c.drawCircle(0, 28, 38, P('#FFFFFF', 255, 5)); c.drawCircle(0, -48, 16, P(col))
    c.restore()


def s5(c, t, D):
    name_t, sci, two, ear = 0.69, 1.95, 2.72, 3.49
    sl = 1 - eout(t / 0.25)
    c.save(); c.translate(W * 0.9 * sl, 0)
    lab_bg(c)
    hx, hy, r = 540, 880, 150
    if t >= sci:
        u = clamp((t - sci) / 0.35); ph = -420 * (1 - ebounce(u))
    else:
        ph = None
    gl = 0.0
    back_mika(c, hx, hy, r, phones=ph)
    # glasses (cocktail party icons) then year chips
    if name_t <= t < sci + 0.2:
        out = clamp((t - sci) / 0.2)
        for n, (gx, col) in enumerate(((165, CORAL), (915, SKY))):
            k = eback((t - name_t - n * 0.1) / 0.25) * (1 - out)
            if k > 0:
                c.save(); c.translate(gx, 600); c.rotate(-10 if n == 0 else 10); c.scale(k, k); party_glass(c, 0, 0, 1.1, col); c.restore()
        for q in range(14):
            u = (t - name_t) / 0.8
            if 0 < u < 1:
                a = math.radians(q * 26); d = 80 + 340 * eout(u)
                cx, cy = 540 + d * math.cos(a), 560 + d * math.sin(a) * 0.6 + 120 * u * u
                c.drawRect(R(cx - 9, cy - 5, cx + 9, cy + 5), P([CORAL, SKY, YEL, MINT][q % 4], 255 * (1 - u)))
    if t >= sci + 0.15:
        for n, yr in enumerate(("1959", "1995", "2001")):
            k = eback((t - sci - 0.15 - n * 0.12) / 0.2)
            tag(c, yr, 270 + n * 270, 545, 54, '#FFFFFF', fg=NAVY, k=k, rot=(-4, 3, -2)[n])
        if t >= sci + 0.55:
            text(c, "LAB STUDIES", 540, 640, 34, '#5A6478', a=255 * clamp((t - sci - 0.55) / 0.2))
    if t >= two:
        k = eout((t - two) / 0.25)
        speaker(c, 85, 940, 0.9, CORAL, k=k); speaker(c, 995, 940, 0.9, SKY, flip=-1, k=k)
        wa = 255 * k
        wave_stream(c, 150, hx - 1.25 * r, 900, t, CORAL, wa)
        wave_stream(c, hx + 1.25 * r, 930, 900, t + 0.4, SKY, wa)
        word_chip(c, "VOICE A", 230, 1110, 36, CORAL, '#FFFFFF', k=eback((t - two - 0.1) / 0.2))
        word_chip(c, "VOICE B", 850, 1110, 36, SKY, NAVY, k=eback((t - two - 0.2) / 0.2))
    if t >= ear:
        for n, (lx, lab, col) in enumerate(((hx - 1.06 * r, "L", CORAL), (hx + 1.06 * r, "R", SKY))):
            k = eback((t - ear - n * 0.1) / 0.2)
            c.save(); c.translate(lx, hy - 130); c.scale(k, k)
            c.drawCircle(0, 0, 48, P(NAVY)); text(c, lab, 0, -2, 60, col); c.restore()
    c.restore()
    ost(c, "*COCKTAIL PARTY* EFFECT" if t >= name_t else "THE *TEST*", t, name_t if t >= name_t else 0.1)


R_WORDS = ["CAT", "SUN", "BOX", "PEN", "MAP", "CUP", "HAT"]
L_WORDS = ["DOG", "RUN", "TOP", "BED", "FIG", "JAM", "LOG"]


def stream_words(c, words, t, p0, p1, period, col, fg, a=255, offset=0.0, nvis=3):
    """word chips travelling along p0 -> p1 (nvis visible at a time)"""
    n = len(words)
    for q in range(nvis):
        ph = (t + offset) / period - q / nvis
        u = ph % 1.0
        idx = (int(math.floor(ph)) * nvis + q) % n
        x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u + 14 * math.sin(u * 7 + q)
        aa = a * clamp(u / 0.12) * clamp((1 - u) / 0.12)
        word_chip(c, words[idx], x, y, 38, col, fg, a=aa)


def s6(c, t, D):
    rt, ig, then, nm = 0.51, 1.17, 2.03, 2.54
    lab_bg(c)
    hx, hy, r = 540, 1000, 130
    z = 1.0 + 0.08 * eout((t - nm) / 0.2) if t >= nm else 1.0
    c.save(); cam(c, z, 400, 1000, cx=400, cy=1000)
    lit_r = t >= rt
    back_mika(c, hx, hy, r, phones=0, glowR=0.8 if lit_r else 0.0, glowL=eout((t - nm) / 0.15) if t >= nm else 0.0)
    RP0, RP1 = (1000, 600), (hx + 1.3 * r, hy - 10)
    LP0, LP1 = (80, 600), (hx - 1.3 * r, hy - 10)
    # right stream (attended)
    stream_words(c, R_WORDS, t, RP0, RP1, 2.1, SKY, NAVY, a=255 if lit_r else 170)
    # left stream (ignored)
    la = 255 if t < ig else 130
    lcol = '#FFFFFF' if t < ig else '#E3E1DD'
    if t < nm - 0.3:
        stream_words(c, L_WORDS, t, LP0, LP1, 2.3, lcol, NAVY, a=la, offset=0.5)
    else:
        u = eout((t - nm + 0.3) / 0.3)
        stream_words(c, L_WORDS, t, LP0, LP1, 2.3, lcol, NAVY, a=la * (1 - u), offset=0.5)
        nx = LP0[0] + (LP1[0] - LP0[0] - 30) * u; ny = LP0[1] + (LP1[1] - LP0[1] - 70) * u
        rings(c, nx, ny, t - nm, r0=50, gap=40, n=3, col=YEL, period=0.5)
        word_chip(c, "MIKA", nx, ny, 64, YEL, NAVY, k=1.0)
        burst(c, hx - 1.06 * r, hy + 10, (t - nm - 0.05) / 0.35, r=110, col=YEL, n=10)
    # echo bubble above head: Mika repeats the right-ear word
    if lit_r:
        per = 0.55
        k = eback(((t - rt) % per) / 0.15)
        idx = int((t - rt) / per) % len(R_WORDS)
        c.save(); c.translate(hx + 30, hy - 250); c.scale(k, k)
        rrect(c, -110, -50, 110, 50, 34, P('#FFFFFF')); rrect(c, -110, -50, 110, 50, 34, P(NAVY, 255, 6))
        tl = skia.Path(); tl.moveTo(-30, 46); tl.lineTo(-60, 90); tl.lineTo(6, 48); tl.close(); c.drawPath(tl, P('#FFFFFF')); c.drawPath(tl, P(NAVY, 255, 6))
        rrect(c, -40, 40, 30, 54, 4, P('#FFFFFF'))
        text(c, R_WORDS[idx] + "!", 0, -4, 50, NAVY)
        c.restore()
    c.restore()
    if t >= rt:
        tag(c, "REPEAT", 890, 1190, 54, SKY, fg=NAVY, k=eback((t - rt) / 0.2), rot=4)
    if t >= ig:
        k = eback((t - ig) / 0.2)
        tag(c, "IGNORE", 190, 1190, 54, CORAL, k=k, rot=-4)
        if k > 0.9: c.drawLine(52, 1196, 328, 1186, P(NAVY, 255, 8))
    # time-lapse clock
    mins = clamp(t / nm) * 4.0
    kc = eback((t - 0.1) / 0.2)
    c.save(); c.translate(540, 480); c.scale(kc, kc)
    rrect(c, -150, -46, 150, 46, 24, P(NAVY))
    text(c, f"{int(mins)}:{int((mins % 1) * 60):02d} MIN", 0, -2, 46, YEL if t >= nm else '#FFFFFF')
    c.restore()
    ost(c, "YOUR *NAME*!" if t >= nm else ("*IGNORE* LEFT" if t >= ig else "*REPEAT* RIGHT"), t,
        nm if t >= nm else (ig if t >= ig else 0.1))


def s7(c, t, D):
    sweep, noticed, two, never = 0.38, 0.95, 1.64, 2.12
    c.drawColor(C(CREAM))
    cx, cy, rr, sw = 540, 860, 255, 110
    k0 = eback(t / 0.25)
    c.save(); c.translate(cx, cy); c.scale(k0, k0); c.translate(-cx, -cy)
    rect = R(cx - rr, cy - rr, cx + rr, cy + rr)
    c.drawCircle(cx, cy, rr, P(NAVY, 255, sw + 14)); c.drawCircle(cx, cy, rr, P('#E3E1DD', 255, sw))
    if t >= two:
        u = eout((t - two) / 0.45)
        pa = P(CORAL, 255, sw); pa.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawArc(rect, -90 + 120, 240 * u, False, pa)
    if t >= sweep:
        u = eout((t - sweep) / 0.45)
        pa = P(YEL, 255, sw); pa.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawArc(rect, -90, 120 * u, False, pa)
        for a in (-90, -90 + 120 * u):
            ra = math.radians(a)
            c.drawLine(cx + (rr - sw / 2) * math.cos(ra), cy + (rr - sw / 2) * math.sin(ra), cx + (rr + sw / 2) * math.cos(ra), cy + (rr + sw / 2) * math.sin(ra), P(NAVY, 255, 7))
    c.drawCircle(cx, cy, rr - sw / 2, P(NAVY, 255, 7)); c.drawCircle(cx, cy, rr + sw / 2, P(NAVY, 255, 7))
    c.restore()
    # centre label
    if t >= sweep:
        if t < two:
            k = eback((t - sweep) / 0.2)
            c.save(); c.translate(cx, cy); c.scale(k, k); text(c, "1 IN 3", 0, -10, 92, NAVY); text(c, "NOTICED", 0, 66, 40, '#8A8F9C'); c.restore()
        else:
            k = eback((t - two) / 0.2)
            c.save(); c.translate(cx, cy); c.scale(k, k); text(c, "2 / 3", 0, -10, 100, CORAL); text(c, "MISSED IT", 0, 66, 40, '#8A8F9C'); c.restore()
    if t >= noticed:
        tag(c, "~33%", 830, 590, 60, YEL, fg=NAVY, k=eback((t - noticed) / 0.2), rot=6)
    if t >= two + 0.2:
        tag(c, "~67%", 250, 1080, 60, CORAL, k=eback((t - two - 0.2) / 0.2), rot=-5)
    if t >= never:
        for n, (yr, pc) in enumerate((("1959", "33%"), ("1995", "35%"), ("2021", "29%"))):
            k = eback((t - never - n * 0.13) / 0.2)
            x = 210 + n * 330
            if k <= 0: continue
            c.save(); c.translate(x, 1260); c.scale(k, k)
            rrect(c, -140, -50, 140, 50, 22, P('#FFFFFF')); rrect(c, -140, -50, 140, 50, 22, P(NAVY, 255, 5))
            text(c, yr, -62, -2, 36, '#8A8F9C'); text(c, pc, 62, -2, 46, NAVY)
            c.restore()
    ost(c, "WHO *NOTICED*?", t, 0.1)


def s8(c, t, D):
    focus, less = 1.37, 2.0
    spin = 1 - eout(t / 0.35)
    c.save(); c.translate(540, 900); c.rotate(-140 * spin); s = 1 - 0.6 * spin; c.scale(s, s); c.translate(-540, -900)
    c.drawColor(C('#EEEAFB'))
    for k in range(12):
        a = k * 30 + t * 20
        c.drawArc(R(540 - 1500, 900 - 1500, 540 + 1500, 900 + 1500), a, 12, True, P('#E2DCF7'))
    c.restore()
    base, top = 1250, 560
    bars = ((330, "FOCUS", SKY), (750, "NOTICED NAME", YEL))
    for n, (x, lab, col) in enumerate(bars):
        tt = 0.85 + n * 0.12
        if t < tt: continue
        k = eback((t - tt) / 0.22)
        lvl = 0.5
        if n == 0 and t >= focus: lvl = 0.5 + 0.45 * eback((t - focus) / 0.3)
        if n == 1 and t >= less: lvl = 0.5 - 0.32 * eout((t - less) / 0.3)
        h = (base - top) * lvl * k
        rrect(c, x - 110, top - 10, x + 110, base, 30, P('#FFFFFF', 200)); rrect(c, x - 110, top - 10, x + 110, base, 30, P(NAVY, 120, 5))
        rrect(c, x - 96, base - h, x + 96, base - 8, 24, P(col)); rrect(c, x - 96, base - h, x + 96, base - 8, 24, P(NAVY, 255, 6))
        text(c, lab, x, base + 46, 40 if n == 0 else 34, NAVY)
        if n == 0 and t >= focus:
            kk = eback((t - focus) / 0.2)
            c.save(); c.translate(x, base - h - 70); c.scale(kk, kk)
            for rr_, col2 in ((52, CORAL), (34, '#FFFFFF'), (16, CORAL)):
                c.drawCircle(0, 0, rr_, P(col2)); c.drawCircle(0, 0, rr_, P(NAVY, 255, 5))
            c.restore()
            ar = skia.Path(); ax = x + 160; ay = 760
            ar.moveTo(ax, ay - 70); ar.lineTo(ax + 50, ay); ar.lineTo(ax + 18, ay); ar.lineTo(ax + 18, ay + 70); ar.lineTo(ax - 18, ay + 70); ar.lineTo(ax - 18, ay); ar.lineTo(ax - 50, ay); ar.close()
            c.save(); c.translate(ax, ay); c.scale(kk, kk); c.translate(-ax, -ay); c.drawPath(ar, P(MINT)); c.drawPath(ar, P(NAVY, 255, 5)); c.restore()
        if n == 1 and t >= less:
            kk = eback((t - less) / 0.2)
            ar = skia.Path(); ax = x + 170; ay = 980
            ar.moveTo(ax, ay + 70); ar.lineTo(ax + 50, ay); ar.lineTo(ax + 18, ay); ar.lineTo(ax + 18, ay - 70); ar.lineTo(ax - 18, ay - 70); ar.lineTo(ax - 18, ay); ar.lineTo(ax - 50, ay); ar.close()
            c.save(); c.translate(ax, ay); c.scale(kk, kk); c.translate(-ax, -ay); c.drawPath(ar, P(CORAL)); c.drawPath(ar, P(NAVY, 255, 5)); c.restore()
            if t < less + 0.5: burst(c, x, base - h, (t - less) / 0.5, r=120, col=CORAL, n=10)
    ost(c, "*LESS*, NOT MORE" if t >= less else "THE *TWIST*", t, less if t >= less else 0.1)


def grid20(c, t, x0, y0, t_in, t_lit, n_lit, col):
    for q in range(20):
        i, j = q % 10, q // 10
        x = x0 + i * 86; y = y0 + j * 110
        tt = t_in + q * 0.02
        if t < tt: continue
        k = eback((t - tt) / 0.18)
        lit = q < n_lit and t >= t_lit + q * 0.05
        if lit: k *= 1.0 + 0.15 * math.sin(clamp((t - t_lit - q * 0.05) / 0.2) * math.pi)
        c.save(); c.translate(x, y); c.scale(k * 0.85, k * 0.85)
        if lit:
            g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeRadial(skia.Point(0, -20), 70, [C(YEL, 200), C(YEL, 0)]))
            c.drawCircle(0, -20, 70, g)
        mini_person(c, 0, 0, 1.0, col if lit else GREY, mark='o' if lit else None)
        c.restore()


def s9(c, t, D):
    lo_t, lo_lit, hi_t, hi_lit = 0.1, 1.51, 2.57, 3.28
    c.drawColor(C('#FFF8EC'))
    for n, (y0, ti, tl_, nl, lab, pc, col) in enumerate(((470, lo_t, lo_lit, 13, "LOW WORKING MEMORY", 65, CORAL),
                                                       (900, hi_t, hi_lit, 4, "HIGH WORKING MEMORY", 20, SKY))):
        if t < ti: continue
        k = eout((t - ti) / 0.3)
        c.save(); c.translate(-W * (1 - k) * (1 if n == 0 else -1), 0)
        rrect(c, 40, y0, 1040, y0 + 400, 34, P('#FFFFFF')); rrect(c, 40, y0, 1040, y0 + 400, 34, P(NAVY, 255, 7))
        rrect(c, 40, y0, 1040, y0 + 88, 34, P(col)); c.drawRect(R(40, y0 + 50, 1040, y0 + 88), P(col)); c.drawLine(40, y0 + 88, 1040, y0 + 88, P(NAVY, 255, 6))
        text(c, lab, 80, y0 + 44, 42, '#FFFFFF' if n == 0 else NAVY, align='l')
        grid20(c, t, 153, y0 + 172, ti + 0.15, tl_, nl, YEL)
        # percent counter
        if t >= tl_:
            u = eout((t - tl_) / 0.5)
            val = int(round(pc * u))
            kk = eback((t - tl_) / 0.2)
            c.save(); c.translate(915, y0 + 44); c.scale(kk, kk)
            rrect(c, -110, -48, 110, 48, 24, P(NAVY)); text(c, f"{val}%", 0, -2, 64, YEL); c.restore()
            text(c, f"{int(round(nl * u))} OF 20", 540, y0 + 368, 32, '#8A8F9C')
        c.restore()
    if t >= 0.3:
        text(c, "Conway, Cowan & Bunting (2001)", 540, 1350, 30, '#8A8F9C', tf=F_CAP, a=255 * clamp((t - 0.3) / 0.3))
    ost(c, "WHO *HEARD* IT?", t, 0.1)


RADAR_WORDS = [(-30, 0.55, "SUN"), (40, 0.75, "BOX"), (110, 0.45, "CUP"), (165, 0.8, "DOG"), (220, 0.6, "HAT"), (290, 0.7, "PEN"), (330, 0.4, "JAM")]


def s10(c, t, D):
    checks, ign, one, nm = 0.6, 1.26, 1.92, 2.83
    c.drawColor(C('#E8F6EF'))
    z = 1.0 + 0.1 * eout((t - nm) / 0.2) if t >= nm else 1.0
    c.save(); cam(c, z, 540, 900)
    cx, cy, rr = 540, 900, 400
    k0 = eback(t / 0.3)
    c.save(); c.translate(cx, cy); c.scale(k0, k0); c.translate(-cx, -cy)
    c.drawCircle(cx, cy, rr + 16, P(NAVY)); c.drawCircle(cx, cy, rr, P('#1F3A4F'))
    for q in (0.33, 0.66, 1.0): c.drawCircle(cx, cy, rr * q, P(SKY, 110, 4))
    c.drawLine(cx - rr, cy, cx + rr, cy, P(SKY, 80, 3)); c.drawLine(cx, cy - rr, cx, cy + rr, P(SKY, 80, 3))
    # sweep angle: fast, slows down for "one word"
    if t < one: ang = t * 300
    else: ang = one * 300 + (t - one) * 90
    for q in range(14):
        a = ang - q * 3.5
        c.drawArc(R(cx - rr, cy - rr, cx + rr, cy + rr), a - 3.5, 3.6, True, P(MINT, 120 * (1 - q / 14)))
    ra = math.radians(ang); c.drawLine(cx, cy, cx + rr * math.cos(ra), cy + rr * math.sin(ra), P(MINT, 255, 6))
    # blips
    if t >= ign:
        dimw = 0.45 if t >= one else 1.0
        for n, (a, d, w) in enumerate(RADAR_WORDS):
            since = ((ang - a) % 360) / 300.0
            a_ = 255 * clamp(1 - since / 1.1) * clamp((t - ign - n * 0.05) / 0.15) * dimw
            x = cx + rr * d * math.cos(math.radians(a)); y = cy + rr * d * math.sin(math.radians(a))
            word_chip(c, w, x, y, 34, '#C9D2DE', NAVY, a=a_)
    c.restore()
    # brain in the centre
    bk = eback((t - 0.1) / 0.25)
    c.save(); c.translate(cx, cy); c.scale(bk * 0.42, bk * 0.42); brain(c, 0, 0, 1.0); c.restore()
    if t >= nm:
        nx, ny = cx + rr * 0.62 * math.cos(math.radians(-60)), cy + rr * 0.62 * math.sin(math.radians(-60))
        rings(c, nx, ny, t - nm, r0=40, gap=45, n=3, col=YEL, period=0.55, w=9)
        word_chip(c, "MIKA", nx, ny, 60, YEL, NAVY, k=eback((t - nm) / 0.2))
        burst(c, nx, ny, (t - nm) / 0.4, r=120, col=YEL, n=12)
    c.restore()
    if t >= checks and t < nm:
        if int(t * 4) % 2 == 0 or t < checks + 0.25:
            tag(c, "SCANNING…", 540, 1370 - 40, 44, NAVY, fg=MINT, k=eback((t - checks) / 0.2))
    if t >= nm:
        tag(c, "MATCH: YOUR NAME", 540, 1330, 46, YEL, fg=NAVY, k=eback((t - nm - 0.1) / 0.2), rot=-3)
    ost(c, "NAME *FOUND*" if t >= nm else "SILENT *SCANNER*", t, nm if t >= nm else 0.1)


FALL = [("SUN", -120, 0.0), ("BOX", 60, 0.22), ("MIKA", -10, 0.45), ("CUP", 130, 0.7), ("HAT", -150, 0.95)]


def falling(c, t, cx, t0, block, name_through):
    """words fall from y 440 onto a filter at y 880; block=True: everything bounces off"""
    for w, dx, d0 in FALL:
        tt = t - t0 - d0
        if tt <= 0: continue
        is_name = w == "MIKA"
        x = cx + dx * 0.9
        y_hit = 860
        y = 440 + 1400 * tt * tt
        a = 255
        if y >= y_hit:
            th = math.sqrt((y_hit - 440) / 1400)
            ta = tt - th
            if block or (not is_name and dx % 2 == 0):
                y = y_hit - 300 * ta + 1400 * ta * ta
                x += (dx / abs(dx) if dx else 1) * 220 * ta
                a = 255 * clamp(1 - ta / 0.5)
            else:
                y = y_hit + 500 * ta + 1400 * ta * ta
                a = 255 if is_name else 255 * clamp(1 - ta / 0.4)
        kk = 1.0
        if is_name and y > 1060:
            kk = clamp(1 - (y - 1060) / 110); y = min(y, 1170)
        if a <= 0 or kk <= 0: continue
        word_chip(c, w, x, y, 46 if is_name else 36, YEL if is_name else '#E3E1DD', NAVY, a=a, k=kk)


def s11(c, t, D):
    tight, blk, wand, thr = 0.1, 0.63, 1.56, 2.29
    c.drawColor(C('#F4F0E8'))
    # left: tight focus = brick wall
    lk = eout((t - tight) / 0.25)
    dimL = clamp((t - wand) / 0.3) * 0.55
    c.save(); c.translate(-560 * (1 - lk), 0)
    rrect(c, 30, 420, 525, 1340, 30, P('#FFFFFF')); rrect(c, 30, 420, 525, 1340, 30, P(NAVY, 255, 6))
    c.save(); c.clipRect(R(36, 426, 519, 1334))
    for row in range(3):
        y = 860 + row * 44
        for q in range(-1, 8):
            x = 40 + q * 76 + (38 if row % 2 else 0)
            rrect(c, x, y, x + 72, y + 40, 6, P(CORAL)); rrect(c, x, y, x + 72, y + 40, 6, P(NAVY, 255, 4))
    falling(c, t, 278, tight + 0.1, True, False)
    mini_mika(c, 278, 1190, 1.6)
    c.restore()
    text(c, "TIGHT FOCUS", 278, 1290, 40, NAVY)
    if t >= blk + 0.12:
        tag(c, "BLOCKED", 278, 760, 50, NAVY, fg='#FFFFFF', k=eback((t - blk - 0.12) / 0.2), rot=-8)
    c.restore()
    if dimL > 0: c.drawRect(R(0, 400, 540, 1360), P('#F4F0E8', 255 * dimL))
    # right: wandering mind = leaky net
    if t >= wand:
        rk = eout((t - wand) / 0.25)
        c.save(); c.translate(560 * (1 - rk), 0)
        rrect(c, 555, 420, 1050, 1340, 30, P('#FFFFFF')); rrect(c, 555, 420, 1050, 1340, 30, P(NAVY, 255, 6))
        c.save(); c.clipRect(R(561, 426, 1044, 1334))
        net = skia.Path(); net.moveTo(560, 880)
        for q in range(1, 25): net.lineTo(560 + q * 20, 880 + 22 * math.sin(q * 0.9 + t * 4))
        c.drawPath(net, P(SKY, 255, 6))
        for q in range(0, 25, 3):
            if q % 6 == 3: continue
            xq = 560 + q * 20; c.drawLine(xq, 860, xq, 905, P(SKY, 255, 5))
        falling(c, t, 802, wand + 0.2, False, True)
        lit = t >= thr + 0.15
        if lit:
            g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeRadial(skia.Point(802, 1180), 150, [C(YEL, 230), C(YEL, 0)]))
            c.drawCircle(802, 1180, 150, g)
        mini_mika(c, 802, 1190, 1.6)
        if lit:
            kk = eback((t - thr - 0.15) / 0.2)
            c.save(); c.translate(900, 1090); c.scale(kk, kk); text(c, "!", 0, 0, 120, CORAL); c.restore()
            burst(c, 802, 1150, (t - thr - 0.15) / 0.4, r=110, col=YEL, n=10)
        c.restore()
        text(c, "WANDERING MIND", 802, 1290, 38, NAVY)
        c.restore()
    ost(c, "*WANDERING* MIND" if t >= wand else "*TIGHT* FOCUS", t, wand if t >= wand else 0.1)


S12_SEG = 1.7


def s12(c, t, D):
    if t < S12_SEG:
        sh = 6 * math.sin(t * 50) * clamp(t / 0.6)
        z = 1.0 + 0.08 * (t / S12_SEG)
        c.save(); c.translate(sh, 0); cam(c, z, 540, 860)
        cafe_bg(c, t)
        crowd_row(c, t, 1010, 0.62, BACK_XS, seed=3)
        crowd_row(c, t + 0.2, 1190, 0.78, [80, 300, 540, 780, 1000], seed=1)
        chatter(c, t, SPOTS, amp=1.1)
        chatter(c, t + 0.4, EXTRA, amp=1.1)
        c.restore()
        if t >= 1.29:
            tag(c, "MAX VOLUME", 540, 1290, 56, CORAL, k=eback((t - 1.29) / 0.2), rot=-4)
        ost(c, "NEXT *TIME*…", t, 0.1)
    else:
        u = (t - S12_SEG) / (D - S12_SEG)
        z = 1.0 + 0.3 * (1 - einout(u))
        c.save(); cam(c, z, 540, 960 + 150 * (z - 1) / 0.3)
        s1(c, t - D, 3.86)
        c.restore()
        if t - S12_SEG < 0.12:
            c.drawRect(R(0, 0, W, H), P('#FFFFFF', 200 * (1 - (t - S12_SEG) / 0.12)))


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]


def sfx_cues(put, S, K, D, fx):
    """put(t_seconds, signal, gain); S = scene starts, K = time factor, D = scene durations"""
    q = lambda i, t: S[i] + t * K[i]
    put(q(0, 0.0), fx.murmur(1.7), .9)
    put(q(0, 0.12), fx.pop(600), .5)
    for k in range(3): put(q(0, 0.3 + k * 0.16), fx.click(), .8)
    put(q(0, 1.22), fx.whoosh(.3, 600, 6000), .5); put(q(0, 1.52), fx.chime(), .9); put(q(0, 1.52), fx.subhit(), .6)
    put(q(0, 2.04), fx.whoosh(.16, 800, 6000), .4)
    put(q(0, 2.64), fx.pop(800), .5); put(q(0, 2.7), fx.cringe(), .35)
    put(q(1, 0.0), fx.murmur(2.0), 1.0); put(q(1, 0.0), fx.whoosh(.35, 200, 2000), .35)
    put(q(1, 1.08), fx.whoosh(.4, 150, 1200), .5); put(q(1, 1.18), fx.pop(500), .5)
    put(q(1, 1.85), fx.clack(), .6)
    put(q(2, 0.0), fx.murmur(0.7), .5)
    put(q(2, 0.5), fx.whoosh(.3, 700, 7000), .6); put(q(2, 0.64), fx.chime(), .9)
    put(q(2, 1.83), fx.whoosh(.15, 900, 8000), .7); put(q(2, 1.86), fx.thud(), .7)
    put(q(2, 2.71), fx.rewind(0.35), .8)
    put(q(3, 0.1), fx.thud(), 1.0); put(q(3, 0.1), fx.clack(), .7)
    for k in range(5): put(q(3, 0.45 + k * 0.07), fx.pop(500 + 60 * k), .4)
    put(q(3, 1.26), fx.whoosh(.7, 300, 3000), .45)
    put(q(3, 1.99), fx.cringe(), .5)
    put(q(4, 0.0), fx.whoosh(.3, 400, 4000), .5)
    put(q(4, 0.69), fx.pop(900), .5); put(q(4, 0.79), fx.pop(1000), .5); put(q(4, 0.69), fx.chime(), .5)
    put(q(4, 2.0), fx.whoosh(.3, 200, 2000), .4); put(q(4, 2.25), fx.thud(), .7)
    for k in range(3): put(q(4, 2.1 + k * 0.12), fx.click(), .7)
    put(q(4, 2.72), fx.riser(0.6), .3)
    put(q(4, 3.49), fx.pop(700), .5); put(q(4, 3.59), fx.pop(850), .5)
    put(q(5, 0.51), fx.pop(800), .5); put(q(5, 1.17), fx.clack(), .5)
    for k in range(int(D[5] / 0.31)): put(q(5, 0.6 + k * 0.31), fx.click(), .25)
    put(q(5, 2.3), fx.whoosh(.3, 600, 7000), .6); put(q(5, 2.54), fx.chime(), 1.0); put(q(5, 2.54), fx.subhit(), .6)
    put(q(6, 0.0), fx.whoosh(.25, 500, 5000), .45)
    put(q(6, 0.38), fx.ratsch(0.45), .6); put(q(6, 0.95), fx.pop(900), .6)
    put(q(6, 1.64), fx.ratsch(0.45), .6); put(q(6, 1.84), fx.thud(), .6)
    for k in range(3): put(q(6, 2.12 + k * 0.13), fx.pop(650 + 80 * k), .45)
    put(q(7, 0.0), fx.rewind(0.35), .7); put(q(7, 0.3), fx.clack(), .5)
    put(q(7, 0.85), fx.pop(600), .45); put(q(7, 0.97), fx.pop(700), .45)
    put(q(7, 1.37), fx.riser(0.35), .5); put(q(7, 1.6), fx.chime(), .45)
    put(q(7, 2.0), fx.cringe(), .6); put(q(7, 2.0), fx.thud(), .6)
    put(q(8, 0.1), fx.whoosh(.3, 300, 3000), .45)
    for k in range(13): put(q(8, 1.51 + k * 0.05), fx.click(), .5)
    put(q(8, 1.51), fx.pop(900), .4)
    put(q(8, 2.57), fx.whoosh(.3, 300, 3000), .45)
    for k in range(4): put(q(8, 3.28 + k * 0.05), fx.click(), .6)
    put(q(8, 3.28), fx.thud(), .5)
    put(q(9, 0.0), fx.whoosh(.3, 300, 3000), .4)
    for k in range(int(2.8 / 0.6)): put(q(9, 0.3 + k * 0.6), fx.click(), .4)
    put(q(9, 1.92), fx.whoosh(.5, 150, 900), .3)
    put(q(9, 2.83), fx.chime(), 1.0); put(q(9, 2.83), fx.subhit(), .7)
    put(q(10, 0.1), fx.whoosh(.25, 400, 4000), .4)
    put(q(10, 0.63), fx.thud(), .8); put(q(10, 0.75), fx.clack(), .6)
    put(q(10, 1.56), fx.whoosh(.25, 400, 4000), .45)
    put(q(10, 2.29), fx.whoosh(.2, 900, 7000), .4); put(q(10, 2.44), fx.chime(), .8)
    put(q(11, 0.0), fx.murmur(1.8), 1.2); put(q(11, 1.29), fx.clack(), .5)
    put(q(11, S12_SEG - 0.1), fx.whoosh(.3, 500, 6000), .5)
    put(q(11, S12_SEG), fx.riser(D[11] - S12_SEG), .5)
    put(q(11, S12_SEG + 0.1), fx.murmur(D[11] - S12_SEG), .7)
