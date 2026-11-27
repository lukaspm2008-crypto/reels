"""Episode 001 – The Spotlight Effect (EN). Reference episode: copy its structure for new episodes."""
import math, skia
from lib import *

META = {
    "id": "001-spotlight-effect",
    "topic": "Spotlight effect – people notice your embarrassing moments far less than you think",
    "source": "Gilovich, Medvec & Savitsky (2000), JPSP",
    "youtube_title": "Nobody's watching you as much as you think #shorts",
    "youtube_description": "The spotlight effect: you think everyone saw your embarrassing moment, but in studies only about 1 in 4 people actually noticed (Gilovich et al., 2000). Send this to someone who's still cringing about yesterday. #psychology #spotlighteffect #mindset #shorts",
    "tiktok_caption": "Nobody's watching you as much as you think. The spotlight effect: in a study, only about 1 in 4 people noticed the embarrassing shirt (Gilovich et al., 2000). Send this to someone who's still cringing about yesterday. #psychology #spotlighteffect #mindset #fyp",
}
VOICE, SPEED = "af_heart", 1.1

# one spoken line per scene (12 scenes); last line must flow back into line 1 (loop)
LINES = [
"There's an invisible spotlight following you everywhere. And only you can see it.",
"Psychologists call it the spotlight effect. It makes you feel like everyone is staring at you.",
"And scientists actually measured how wrong that is.",
"They made students wear an embarrassing T-shirt, with a cheesy pop singer's face on it.",
"Then they sent them into a full room.",
"The students guessed half the room noticed.",
"The real number? Only about one in four.",
"Why? Your brain lives every second from your point of view, and assumes everyone else does too.",
"The stain. The wrong answer. Tripping on the stairs. You replay it over and over. Everyone else? Not even once.",
"Because nobody's actually in the audience.",
"They're all on stage too.",
"And every single one of them is thinking the same thing:",
]
# caption blocks per scene (2-4 words, *highlight*)
CAPS = [
    ["There's an *invisible*", "*spotlight* following you", "everywhere.", "And only *you*", "can see it."],
    ["Psychologists call it", "the *spotlight effect*.", "It makes you feel", "like *everyone*", "is staring at you."],
    ["And scientists actually", "*measured*", "how wrong that is."],
    ["They made students wear", "an *embarrassing T-shirt*", "with a cheesy", "pop singer's face on it."],
    ["Then they sent them", "into a full room."],
    ["The students guessed", "*half the room*", "noticed."],
    ["The real number?", "Only about", "*one in four*."],
    ["Why?", "Your brain lives", "every second", "from *your* point of view", "and assumes", "everyone else", "does too."],
    ["The stain.", "The wrong answer.", "Tripping on the stairs.", "You replay it", "*over and over*.", "Everyone else?", "*Not even once*."],
    ["Because nobody's", "actually", "in the audience."],
    ["They're all", "on stage *too*."],
    ["And every single", "one of them", "is thinking the same thing:"],
]
TAIL = [0.22, 0.22, 0.32, 0.2, 0.22, 0.22, 0.5, 0.22, 0.3, 0.22, 0.2, 0.45]
# scenes below were timed for these durations; engine rescales time to the real VO durations
DESIGN_DUR = [3.824, 4.586, 2.094, 4.978, 1.696, 2.295, 2.565, 6.325, 6.423, 2.217, 1.742, 2.471]

# ---------------------------------------------------------------- scenes
def s1(c, t, D):
    mx = -150 + (540 + 150) * eout(t / 0.75)
    walking = t < 0.75
    on = t >= 0.4
    z = 1.0 + 0.04 * clamp(t / 1.8)
    if t >= 1.8: z = 1.04 + 0.26 * eout((t - 1.8) / 0.14)
    c.save(); cam(c, z, 540, 1000 if t >= 1.8 else 960)
    classroom_bg(c)

    def look(x):
        if t < 1.2: return (0, 0)
        k = eout((t - 1.2) / 0.15); d = mx - x
        return (clamp(d / 250, -1, 1) * k, -0.3 * k)
    classmates_desks(c, look)
    if on:
        dim(c, 120 * eout((t - 0.4) / 0.08))
        lx, ly = mx + 58 - 16, 1300 - 520 + 18
        beam(c, lx, ly, 26, mx, 1300, 330, a=1.0)
    mika(c, mx, 1300, 1.0, walk=t * 14 if walking else 0, lamp=True, lamp_on=on,
         look=(0.6, -0.2) if t > 1.3 else (0.4, 0), sweat=t > 1.3, mood='worried' if t > 1.3 else 'neutral')
    if t >= 2.4:
        k = eback((t - 2.4) / 0.25)
        lx, ly = mx + 58, 1300 - 520
        c.drawCircle(lx - 5, ly, 78 * k, P(CORAL, 255, 9))
        for a in range(0, 360, 45):
            r0, r1 = 92 * k, 120 * k
            ra = math.radians(a)
            c.drawLine(lx - 5 + r0 * math.cos(ra), ly + r0 * math.sin(ra), lx - 5 + r1 * math.cos(ra), ly + r1 * math.sin(ra), P(CORAL, 255, 7))
    c.restore()
    if on and t < 0.52:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#FFFFFF', 170 * (1 - (t - 0.4) / 0.12)))
    ost(c, "ONLY *YOU* SEE IT", t, 2.2)


EYES = [(-170, -120, 52), (20, -190, 60), (190, -90, 48), (-60, -20, 66), (120, 60, 50), (-210, 60, 44), (230, 120, 40),
        (-120, 150, 54), (40, 200, 46), (-10, -110, 38), (250, -10, 36), (-260, -40, 34), (110, -60, 42)]


def s2(c, t, D):
    z = 1.3 - 0.3 * eout(t / 0.5)
    c.save(); cam(c, z, 540, 960)
    c.drawColor(C(CREAM))
    c.drawRect(skia.Rect.MakeLTRB(0, 1360, W, H), P(FLOOR)); c.drawLine(0, 1360, W, 1360, P(NAVY, 255, 6))
    bx, by, br = 540, 720, 300
    for (dx, dy, r) in ((610, 1035, 22), (650, 975, 32)):
        c.drawCircle(dx, dy, r, P('#FFFFFF')); c.drawCircle(dx, dy, r, P(NAVY, 255, 6))
    c.drawCircle(bx, by, br, P('#FFFFFF')); c.drawCircle(bx, by, br, P(NAVY, 255, 7))
    n = len(EYES)
    for i, (dx, dy, r) in enumerate(EYES):
        t0 = 0.35 + i * (2.6 / n)
        if t < t0: continue
        k = eback((t - t0) / 0.18)
        ex, ey = bx + dx, by + dy
        c.save(); c.translate(ex, ey); c.scale(k, k)
        c.drawOval(skia.Rect.MakeXYWH(-r, -r * 0.72, 2 * r, 1.44 * r), P('#FFFFFF'))
        c.drawOval(skia.Rect.MakeXYWH(-r, -r * 0.72, 2 * r, 1.44 * r), P(NAVY, 255, 5))
        vx, vy = (540 - ex), (1120 - ey); L = math.hypot(vx, vy) or 1
        c.drawCircle(vx / L * r * 0.35, vy / L * r * 0.3, r * 0.42, P(CORAL if i % 4 == 0 else SKY))
        c.drawCircle(vx / L * r * 0.35, vy / L * r * 0.3, r * 0.2, P(NAVY))
        c.restore()
    mika(c, 540, 1360, 0.8, look=(0.2, -1), sweat=t > 1.5, mood='worried')
    c.restore()
    ost(c, "*SPOTLIGHT* EFFECT", t, 0.5)


def s3(c, t, D):
    off = 800 * (1 - eout(t / 0.22))
    c.drawColor(C(CREAM))
    c.save(); c.translate(off, 0)
    cx, cy, r = 540, 1080, 340
    for a0, a1, col in ((180, 240, SKY), (240, 300, YEL), (300, 360, CORAL)):
        p = P(col, 255, 70); p.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), a0, a1 - a0, False, p)
    c.drawArc(skia.Rect.MakeLTRB(cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40), 180, 180, False, P(NAVY, 255, 7))
    c.drawArc(skia.Rect.MakeLTRB(cx - r + 40, cy - r + 40, cx + r - 40, cy + r - 40), 180, 180, False, P(NAVY, 255, 7))
    for a in range(180, 361, 15):
        ra = math.radians(a)
        c.drawLine(cx + (r - 70) * math.cos(ra), cy + (r - 70) * math.sin(ra), cx + (r - 100) * math.cos(ra), cy + (r - 100) * math.sin(ra), P(NAVY, 255, 6))
    c.drawLine(cx - r - 60, cy, cx + r + 60, cy, P(NAVY, 255, 7))
    u = max(0, t - 0.3)
    ang = 192 + 158 * (1 - math.exp(-5 * u) * math.cos(13 * u))
    ra = math.radians(ang)
    c.drawLine(cx, cy, cx + (r - 40) * math.cos(ra), cy + (r - 40) * math.sin(ra), P(NAVY, 255, 16))
    c.drawCircle(cx, cy, 34, P(CORAL)); c.drawCircle(cx, cy, 34, P(NAVY, 255, 7))
    # measuring tape at bottom
    rrect(c, 140, 1240, 940, 1310, 10, P(YEL)); rrect(c, 140, 1240, 940, 1310, 10, P(NAVY, 255, 6))
    shift = (u * 260) % 40
    x = 150 - shift
    while x < 935:
        if x > 145: c.drawLine(x, 1244, x, 1270 if int((x + shift) / 40) % 2 else 1285, P(NAVY, 255, 4))
        x += 20
    c.restore()
    if t < 0.22:
        for i in range(9):
            y = 500 + i * 110
            c.drawLine(80 + (i * 97) % 300, y, 700 + (i * 53) % 300, y, P(NAVY, 90 * (1 - t / 0.22), 10))
    ost(c, "MEASURED.", t, 0.3)



def s4(c, t, D):
    tz = 0.62 * D
    z = 1.0 if t < tz else 1.0 + 0.75 * eout((t - tz) / 0.16)
    s = 1.5; fx, fy = 540, 1400
    c.save(); cam(c, z, 540, 960 if t < tz else 960 + 0 * 1)
    if t >= tz:
        c.restore(); c.save(); cam(c, z, 540, fy - 166 * s)
    c.drawColor(C('#FDEBD3'))
    c.drawRect(skia.Rect.MakeLTRB(0, 1400, W, H), P(FLOOR)); c.drawLine(0, 1400, W, 1400, P(NAVY, 255, 6))
    landed = t >= 0.75
    drop = (1 - ebounce((t - 0.25) / 0.55)) * -1100 if t < 0.8 else 0
    person(c, fx, fy, s, HOODS[0], SKINS[1], HAIRS[0], shirt=CORAL if landed else None,
           blush=landed, sweat=landed and t > 1.0, mood='worried' if landed else 'neutral', look=(0, 1) if landed else (0, 0))
    if landed:
        popstar_print(c, fx, fy - 168 * s, 0.95)
    else:
        if t > 0.2:
            yy = drop
            rrect(c, fx - 92 * s, fy - 262 * s + yy, fx + 92 * s, fy - 76 * s + yy, 46 * s, P(CORAL))
            rrect(c, fx - 92 * s, fy - 262 * s + yy, fx + 92 * s, fy - 76 * s + yy, 46 * s, P(NAVY, 255, 9))
            popstar_print(c, fx, fy - 168 * s + yy, 0.95)
    c.restore()
    ost(c, "CRINGE *SHIRT*", t, 0.45)



def s5(c, t, D):
    z = 1.0 + 0.55 * einout(t / D)
    c.save(); cam(c, z, 540, 930)
    c.drawColor(C(CREAM))
    c.drawRect(skia.Rect.MakeLTRB(0, 1380, W, H), P(FLOOR)); c.drawLine(0, 1380, W, 1380, P(NAVY, 255, 6))
    x0, y0, x1, y1 = 290, 500, 790, 1380
    c.save(); c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.save(); c.translate(540, 900); c.scale(0.5, 0.5); c.translate(-540, -905); room(c, {}); c.restore()
    c.restore()
    open_k = einout((t - 0.08) / 0.5)
    dw = (x1 - x0) * (1 - 0.86 * open_k)
    pth = skia.Path(); skew = 60 * open_k
    pth.moveTo(x0, y0); pth.lineTo(x0 + dw, y0 - skew); pth.lineTo(x0 + dw, y1 + skew); pth.lineTo(x0, y1); pth.close()
    c.drawPath(pth, P(WOOD)); c.drawPath(pth, P(NAVY, 255, 7))
    if open_k < 0.7:
        c.drawCircle(x0 + dw - 45 * (1 - open_k), 950, 16, P(YEL)); c.drawCircle(x0 + dw - 45 * (1 - open_k), 950, 16, P(NAVY, 255, 5))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P(NAVY, 255, 14))
    c.restore()
    ost(c, "FULL *ROOM*", t, 0.12)


S6_ORDER = [0, 6, 3, 9, 5, 10]
S7_KEEP = [6, 9, 3]


def s6(c, t, D):
    lit = {}
    for i, k in enumerate(S6_ORDER):
        t0 = 0.25 + i * 0.27
        if t >= t0: lit[k] = eout((t - t0) / 0.1)
    z = 1.04 - 0.04 * eout(t / 0.2)
    c.save(); cam(c, z, 540, 960); room(c, lit); c.restore()
    ost(c, "GUESS: *50 %*", t, 0.12)


def s7(c, t, D):
    snap = 1.02
    lit = {k: 1.0 for k in S6_ORDER} if t < snap else {k: 1.0 for k in S7_KEEP}
    sx = sy = 0
    if snap <= t < snap + 0.18:
        a = 14 * (1 - (t - snap) / 0.18); sx = a * math.sin(t * 90); sy = a * math.cos(t * 70)
    c.save(); c.translate(sx, sy); room(c, lit)
    if t >= snap:
        dim(c, 55)
        for k in S7_KEEP:
            x, y = GRID[k]
            bust(c, x, y, 0.82, CORAL, SKINS[k % 5], HAIRS[(k * 3) % 5], look=(0, 0.3), glow=1.0, mood='o')
    c.restore()
    ost(c, "REALITY: *~25 %*", t, 0.12)



def s8(c, t, D):
    z = 1.0 + 0.12 * (t / D)
    c.save(); cam(c, z, 540, 930)
    c.drawColor(C(CREAM))
    hx, hy, hr = 540, 930, 400
    c.drawCircle(hx, hy, hr, P('#F5C6A5'))
    hp = skia.Path(); hp.addArc(skia.Rect.MakeLTRB(hx - hr, hy - hr, hx + hr, hy + hr), 196, 148); hp.close(); c.drawPath(hp, P('#2A2233'))
    tf = skia.Path(); tf.moveTo(hx - 40, hy - hr + 20); tf.quadTo(hx + 30, hy - hr - 150, hx + 160, hy - hr - 90); tf.quadTo(hx + 90, hy - hr - 20, hx + 110, hy - hr + 40); tf.close(); c.drawPath(tf, P('#2A2233'))
    c.drawCircle(hx, hy, hr, P(NAVY, 255, 12))
    wx0, wy0, wx1, wy1 = 250, 640, 830, 1070
    rrect(c, wx0, wy0, wx1, wy1, 40, P(NAVY))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), 40, 40), doAntiAlias=True)
    fl = 0.85 + 0.15 * math.sin(t * 23)
    pr = skia.Path(); pr.moveTo(760, 1040); pr.lineTo(330, 690); pr.lineTo(330, 880); pr.close()
    c.drawPath(pr, P('#FFF6C8', 60 * fl))
    rrect(c, 300, 680, 640, 890, 14, P('#FFF6C8', 255 * fl))
    mini_mika(c, 470, 770, 1.6 + 0.05 * math.sin(t * 8))
    for sx0, sy0 in ((665, 690), (665, 800)):
        rrect(c, sx0, sy0, sx0 + 130, sy0 + 90, 10, P('#FFF6C8', 230 * fl)); mini_mika(c, sx0 + 65, sy0 + 38, 0.62)
    for row, yy in enumerate((960, 1015)):
        for k in range(7):
            rrect(c, 290 + k * 75, yy, 345 + k * 75, yy + 40, 14, P(CORAL if row == 0 else '#E0564A'))
    c.drawCircle(780, 1040, 22, P(GREY))
    c.restore()
    rrect(c, wx0, wy0, wx1, wy1, 40, P(NAVY, 255, 10))
    for dx in (-80, 80):
        c.drawCircle(hx + dx, 1150, 20, P(NAVY))
    m = skia.Path(); m.moveTo(hx - 40, 1220); m.quadTo(hx, 1250, hx + 40, 1220); c.drawPath(m, P(NAVY, 255, 10))
    # projected onto others
    others = [(120, 560), (960, 560), (110, 1250), (970, 1250)]
    for i, (ox, oy) in enumerate(others):
        t0 = 3.4 + i * 0.18
        if t < t0: continue
        k = eback((t - t0) / 0.2)
        ex, ey = hx + (ox - hx) * 0.62, hy + (oy - hy) * 0.62
        pp = P(CORAL, 255, 8); pp.setPathEffect(skia.DashPathEffect.Make([18, 16], -t * 80))
        c.drawLine(hx + (ox - hx) * 0.42, hy + (oy - hy) * 0.42, ex + (ox - ex) * k * 0.7, ey + (oy - ey) * k * 0.7, pp)
        c.save(); c.translate(ox, oy); c.scale(k, k)
        head(c, 0, 0, 52, SKINS[i + 1], HAIRS[i + 1])
        rrect(c, -52, -150, 52, -78, 10, P('#FFFFFF')); rrect(c, -52, -150, 52, -78, 10, P(NAVY, 255, 5)); mini_mika(c, 0, -120, 0.55)
        c.restore()
    c.restore()
    ost(c, "ONLY *YOUR* VIEW", t, 0.12)



def s9(c, t, D):
    c.drawColor(C('#FFF0D4'))
    c.drawRect(skia.Rect.MakeLTRB(540, 0, W, H), P('#E3F3FB'))
    # left
    lx = 270
    font = skia.Font(F_OST, 64)
    for txt, x in (("YOU", lx), ("THEM", 810)):
        w = font.measureText(txt); c.drawString(txt, x - w / 2, 470, font, P(NAVY))
    inf_t = D - 1.6
    if t < inf_t:
        n = max(1, int(math.exp(1.05 * max(t - 0.15, 0))))
        num = str(n)
    else:
        num = "∞"
    nf = skia.Font(F_OST, 210 if num != "∞" else 260)
    w = nf.measureText(num); c.drawString(num, lx - w / 2, 760 if num != "∞" else 790, nf, P(CORAL))
    rot = t * 400
    c.save(); c.translate(lx, 700); c.rotate(-rot)
    ap = P(NAVY, 255, 10); c.drawArc(skia.Rect.MakeLTRB(-165, -165, 165, 165), 20, 300, False, ap)
    ah = skia.Path(); ah.moveTo(185 * math.cos(math.radians(20)) + 22, 185 * math.sin(math.radians(20)) - 10); ah.lineTo(150, 40); ah.lineTo(205, 95); ah.close()
    c.restore()
    for i, (fn, tt) in enumerate(((icon_splat, 0.15), (icon_x, 0.65), (icon_trip, 1.2))):
        if t >= tt:
            k = eback((t - tt) / 0.18); c.save(); c.translate(130 + i * 140, 940); c.scale(k, k); fn(c, 0, 0, 1.2); c.restore()
    mika(c, lx, 1380, 0.72, sweat=True, mood='worried', blush=True, look=(0, -0.8))
    # right
    right_on = t >= 4.0
    for k, (x, sc) in enumerate(((720, 0.55), (900, 0.55), (810, 0.6))):
        person(c, x, 1380 if k < 2 else 1400, sc, HOODS[k + 1], SKINS[k + 2], HAIRS[k + 1], look=(-0.5 if k == 1 else 0.5, 0), mood='smile')
    if right_on:
        k = eback((t - 4.0) / 0.2)
        nf = skia.Font(F_OST, 230); w = nf.measureText("0")
        c.save(); c.translate(810, 690); c.scale(k, k); c.drawString("0", -w / 2, 80, nf, P(NAVY)); c.restore()
        zf = skia.Font(F_CAP, 54)
        for i in range(3):
            ph = (t * 0.8 + i * 0.33) % 1
            c.drawString("z", 880 + i * 30 + ph * 30, 1000 - ph * 140, zf, P(NAVY, 255 * (1 - ph)))
    else:
        c.drawRect(skia.Rect.MakeLTRB(540, 0, W, H), P(NAVY, 70))
    c.drawLine(540, 420, 540, 1400, P(NAVY, 255, 8))



def s10(c, t, D):
    z = 1.6 - 0.6 * eout(t / (D * 0.9))
    c.save(); cam(c, z, 540, 900 + 60 * (1 - eout(t / D)))
    stage(c, [(540, 900, 0.42)], {0: 1.0})
    c.restore()
    ost(c, "NO *AUDIENCE*", t, 0.12)


S11_FIGS = [(540, 1200, 0.6), (340, 1200, 0.6), (740, 1200, 0.6), (140, 1200, 0.6), (940, 1200, 0.6)]
S11_T = {0: -1, 1: 0.28, 2: 0.52, 3: 0.76, 4: 1.0}


def s11(c, t, D):
    lit = {i: (1.0 if t >= t0 else 0.0) for i, t0 in S11_T.items()}
    c.save(); cam(c, 1.04 - 0.04 * eout(t / 0.2), 540, 960)
    stage(c, S11_FIGS, lit, seats=False)
    c.restore()
    ost(c, "EVERYONE HAS *ONE*", t, 0.12)


_S1F0 = None


def s12(c, t, D):
    global _S1F0
    u = einout((t - 0.25) / (D - 0.7))
    z = 1.0 + 6.0 * ein(clamp((t - 0.25) / (D - 0.7)))
    x, y, s = S11_FIGS[2]
    fx = 540 + (x - 540) * u; fy = 960 + (y - 150 - 960) * u
    c.save(); cam(c, z, fx, fy)
    stage(c, S11_FIGS, {i: 1.0 for i in range(5)}, seats=False)
    c.restore()
    wash = clamp((t - (D - 1.0)) / 0.55)
    c.drawRect(skia.Rect.MakeWH(W, H), P('#FFF6C8', 255 * wash))
    fade = clamp((t - (D - 0.42)) / 0.38)
    if fade > 0:
        if _S1F0 is None:
            surf = skia.Surface(W, H); s1(surf.getCanvas(), 0.0, DESIGN_DUR[0]); _S1F0 = surf.makeImageSnapshot()
        p = skia.Paint(); p.setAlphaf(fade); c.drawImage(_S1F0, 0, 0, skia.SamplingOptions(), p)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]


def sfx_cues(put, S, K, D, fx):
    """put(t_seconds, signal, gain); S = scene starts, K[i] = real/design time factor, D = real scene durations, fx = sfx module"""
    q = lambda i, t: S[i] + t * K[i]
    put(q(0, 0.0), fx.whoosh(.45, 200, 2000), .35)
    put(q(0, 0.4), fx.clack(), .9); put(q(0, 0.4), fx.subhit(), .9)
    put(q(0, 1.8), fx.whoosh(.18, 800, 6000), .4)
    put(q(0, 2.4), fx.chime(), .8)
    put(q(1, 0.0), fx.whoosh(.3, 400, 4000), .4)
    for k in range(13): put(q(1, 0.35 + k * 2.6 / 13), fx.pop(600 + 40 * k), .5)
    put(q(2, 0.0), fx.whoosh(.25, 600, 7000), .55)
    put(q(2, 0.3), fx.ratsch(), .7)
    put(q(3, 0.75), fx.thud(), .5); put(q(3, 0.8), fx.cringe(), .9)
    put(q(3, 0.62 * DESIGN_DUR[3]), fx.whoosh(.16, 900, 6000), .45)
    put(q(4, 0.05), fx.whoosh(.5, 150, 1500), .55); put(q(4, 0.3), fx.murmur(1.7), .8)
    for k in range(6): put(q(5, 0.25 + k * 0.27), fx.click(), .9)
    put(q(6, 1.02), fx.thud(), .9); put(q(6, 1.02), fx.clack(), .5)
    put(q(7, 0.0), fx.whoosh(.3, 300, 3000), .4); put(q(7, 0.1), fx.projector(3.2), .8)
    for k in range(4): put(q(7, 3.4 + k * .18), fx.pop(900), .4)
    put(q(8, 0.15), fx.rewind(3.6), 1.0)
    put(q(8, 0.15), fx.pop(500), .5); put(q(8, .65), fx.pop(560), .5); put(q(8, 1.2), fx.pop(620), .5)
    put(q(8, 4.0), fx.click(), 1.0); put(q(8, 4.0), fx.thud(), .4)
    put(q(9, 0.0), fx.whoosh(.6, 120, 1200), .5)
    for tt in [0.28, 0.52, 0.76, 1.0]: put(q(10, tt), fx.clack(), .55)
    put(q(11, 0.3), fx.riser(D[11] - 0.3), .9)
