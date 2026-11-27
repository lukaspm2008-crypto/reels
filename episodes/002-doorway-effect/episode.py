"""Episode 002 – The Doorway Effect (EN). Hook type: relatable moment."""
import math, skia
from lib import *

META = {
    "id": "002-doorway-effect",
    "topic": "Doorway effect – walking through a door makes you forget why you came",
    "source": "Radvansky, Krawietz & Tamplin (2011), Quarterly Journal of Experimental Psychology 64(8); caveat: McFadyen et al. (2021), BMC Psychology",
    "youtube_title": "Why you forget why you walked into a room #shorts",
    "youtube_description": "The doorway effect: walking through a door can wipe what you came for. In a study with 55 virtual rooms, memory mistakes roughly doubled right after a doorway (about 10% vs 20%) compared to walking the same distance inside one room (Radvansky, Krawietz & Tamplin, 2011, Quarterly Journal of Experimental Psychology). Your brain treats the door as an event boundary and files the old scene away. A 2021 replication found it mostly when the mind is busy (McFadyen et al., BMC Psychology). Send this to someone who always forgets why they walked into the kitchen. #psychology #doorwayeffect #memory #shorts",
    "tiktok_caption": "You walk into a room… and forget why. It's the door: memory mistakes roughly doubled right after a doorway (about 10% vs 20%) in Radvansky, Krawietz & Tamplin, 2011 (Quarterly Journal of Experimental Psychology). Send this to someone who always forgets why they walked into the kitchen. #psychology #doorwayeffect #memory #fyp",
}
VOICE, SPEED = "af_heart", 1.1

# one spoken line per scene (12 scenes); last line flows back into line 1 (loop)
LINES = [
"You walk into a room… and forget why you came.",
"Your charger. Your homework. Now you're just… standing there.",
"It's not bad memory. Scientists blame the door.",
"Researchers had people carry objects from room to room.",
"Sometimes through a doorway. Sometimes the same distance in one big room.",
"Then: quick quiz. What are you holding?",
"In one room, about one in ten got it wrong. After a doorway? One in five.",
"Why? Your brain doesn't record one long video. It cuts life into scenes.",
"A doorway is a scene cut. New room, new chapter.",
"So your brain files the old scene away… with your reason inside.",
"It's worst when your mind is busy. Like texting while walking.",
"And that's exactly what happens every time…",
]
CAPS = [
    ["You walk", "into a *room*…", "and *forget*", "why you came."],
    ["Your *charger*.", "Your *homework*.", "Now you're just…", "*standing there*."],
    ["It's not", "*bad memory*.", "Scientists blame", "the *door*."],
    ["Researchers had people", "carry *objects*", "from room to room."],
    ["Sometimes through", "a *doorway*.", "Sometimes", "the *same distance*", "in one big room."],
    ["Then:", "*quick quiz*.", "What are you", "*holding*?"],
    ["In one room,", "about *one in ten*", "got it wrong.", "After a *doorway*?", "*One in five*."],
    ["Why?", "Your brain doesn't record", "*one long video*.", "It cuts life", "into *scenes*."],
    ["A *doorway*", "is a *scene cut*.", "New room,", "*new chapter*."],
    ["So your brain", "files the old scene", "*away*…", "with your *reason*", "inside."],
    ["It's *worst*", "when your mind", "is *busy*.", "Like *texting*", "while walking."],
    ["And that's", "*exactly* what happens", "every time…"],
]
TAIL = [0.22, 0.22, 0.25, 0.2, 0.22, 0.3, 0.45, 0.22, 0.25, 0.25, 0.22, 0.5]

HALL, BED = '#DCEFF8', '#FDE3D2'
FY = 1330          # floor line in the two-room view
WX = 540           # dividing wall x
DOOR_TOP = 880


# ---------------------------------------------------------------- helpers / props
def R(x0, y0, x1, y1):
    return skia.Rect.MakeLTRB(x0, y0, x1, y1)


def text(c, s, x, y, size, col=NAVY, tf=None, align='c'):
    f = skia.Font(tf or F_OST, size); w = f.measureText(s)
    xx = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    c.drawString(s, xx, y + size * 0.36, f, P(col))
    return w


def tag(c, s, x, y, size, bg, fg='#FFFFFF', k=1.0, rot=0):
    if k <= 0: return
    f = skia.Font(F_OST, size); w = f.measureText(s)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    rrect(c, -w / 2 - 22, -size * 0.66, w / 2 + 22, size * 0.62, 18, P(bg))
    rrect(c, -w / 2 - 22, -size * 0.66, w / 2 + 22, size * 0.62, 18, P(NAVY, 255, 5))
    c.drawString(s, -w / 2, size * 0.34, f, P(fg))
    c.restore()


def burst(c, x, y, u, r=90, col=YEL, n=10):
    """radial pop lines, u in 0..1"""
    if u <= 0 or u >= 1: return
    for k in range(n):
        a = math.radians(k * 360 / n + 9)
        r0, r1 = r * (0.4 + 0.8 * u), r * (0.7 + 1.0 * u)
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(col, 255 * (1 - u), 9))
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(NAVY, 255 * (1 - u), 3))


def icon_charger(c, x, y, s):
    cab = skia.Path(); cab.moveTo(x, y + 30 * s); cab.cubicTo(x, y + 80 * s, x + 60 * s, y + 40 * s, x + 50 * s, y + 70 * s)
    c.drawPath(cab, P(NAVY, 255, 14 * s)); c.drawPath(cab, P('#FFFFFF', 255, 7 * s))
    for dx in (-13, 13):
        rrect(c, x + (dx - 5) * s, y - 56 * s, x + (dx + 5) * s, y - 26 * s, 3 * s, P(GREY)); rrect(c, x + (dx - 5) * s, y - 56 * s, x + (dx + 5) * s, y - 26 * s, 3 * s, P(NAVY, 255, 3 * s))
    rrect(c, x - 32 * s, y - 30 * s, x + 32 * s, y + 34 * s, 12 * s, P('#FFFFFF')); rrect(c, x - 32 * s, y - 30 * s, x + 32 * s, y + 34 * s, 12 * s, P(NAVY, 255, 5 * s))
    bolt = skia.Path(); bolt.moveTo(x + 4 * s, y - 18 * s); bolt.lineTo(x - 10 * s, y + 6 * s); bolt.lineTo(x + 2 * s, y + 6 * s); bolt.lineTo(x - 4 * s, y + 24 * s)
    bolt.lineTo(x + 12 * s, y - 2 * s); bolt.lineTo(x, y - 2 * s); bolt.close(); c.drawPath(bolt, P(YEL)); c.drawPath(bolt, P(NAVY, 255, 2.5 * s))


def icon_homework(c, x, y, s):
    c.save(); c.translate(x, y); c.rotate(-6)
    rrect(c, -48 * s, -60 * s, 48 * s, 60 * s, 6 * s, P('#FFFFFF')); rrect(c, -48 * s, -60 * s, 48 * s, 60 * s, 6 * s, P(NAVY, 255, 5 * s))
    f = skia.Font(F_OST, 20 * s); w = f.measureText("MATH"); c.drawString("MATH", -w / 2, -34 * s, f, P(CORAL))
    for k in range(4):
        c.drawLine(-32 * s, (-14 + k * 18) * s, (32 - (k % 2) * 18) * s, (-14 + k * 18) * s, P(SKY, 255, 5 * s))
    c.restore()


def icon_q(c, x, y, s, col=CORAL):
    f = skia.Font(F_OST, 120 * s); w = f.measureText("?")
    c.drawString("?", x - w / 2, y + 44 * s, f, P(col))


def thought(c, x, y, k, icon, s=1.0, tail=(-80, 130)):
    """thought cloud centred at (x,y); tail points toward the head"""
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k * s, k * s)
    tx, ty = tail
    for f, r in ((0.55, 16), (0.85, 11)):
        c.drawCircle(tx * f, ty * f, r, P('#FFFFFF')); c.drawCircle(tx * f, ty * f, r, P(NAVY, 255, 5))
    cl = skia.Path()
    for dx, dy, r in ((-58, 8, 52), (0, -22, 62), (58, 6, 52), (0, 34, 50)):
        cl.addCircle(dx, dy, r)
    cl.setFillType(skia.PathFillType.kWinding)
    c.drawPath(cl, P(NAVY, 255, 10)); c.drawPath(cl, P('#FFFFFF'))
    if icon: icon(c, 0, 4, 0.82)
    c.restore()


def bed(c, x, y):
    """bed, (x,y) = left foot on floor"""
    rrect(c, x + 300, y - 260, x + 330, y, 10, P(WOOD)); rrect(c, x + 300, y - 260, x + 330, y, 10, P(NAVY, 255, 5))
    rrect(c, x, y - 120, x + 320, y - 50, 14, P('#FFFFFF')); rrect(c, x, y - 120, x + 320, y - 50, 14, P(NAVY, 255, 5))
    rrect(c, x - 10, y - 140, x + 220, y - 60, 22, P(SKY)); rrect(c, x - 10, y - 140, x + 220, y - 60, 22, P(NAVY, 255, 5))
    rrect(c, x + 222, y - 160, x + 296, y - 116, 18, P('#FFFFFF')); rrect(c, x + 222, y - 160, x + 296, y - 116, 18, P(NAVY, 255, 4))
    for dx in (14, 300):
        c.drawLine(x + dx, y - 50, x + dx, y, P(NAVY, 255, 10))


def door_leaf(c, x, y0, y1, k, col='#E9A15B', side=-1):
    """door seen in cut-away, hinged at x, swung toward the viewer by k (0 closed .. 1 open)"""
    w = 150 * k
    p = skia.Path(); p.moveTo(x, y0); p.lineTo(x + side * w, y0 - 20 * k); p.lineTo(x + side * w, y1 + 26 * k); p.lineTo(x, y1); p.close()
    c.drawPath(p, P(col)); c.drawPath(p, P(NAVY, 255, 6))
    if k > 0.2:
        c.drawCircle(x + side * w * 0.8, (y0 + y1) / 2 + 10, 9, P(YEL)); c.drawCircle(x + side * w * 0.8, (y0 + y1) / 2 + 10, 9, P(NAVY, 255, 3))


def two_rooms(c, door=1.0, flash=0.0, charger=True):
    c.drawColor(C(HALL))
    c.drawRect(R(WX, 0, W, H), P(BED))
    # hallway decor: frame + coat hooks + stripe
    c.drawRect(R(0, 1060, WX, 1080), P('#BFE0EF'))
    rrect(c, 130, 640, 330, 800, 10, P('#FFFFFF')); rrect(c, 130, 640, 330, 800, 10, P(NAVY, 255, 6))
    mt = skia.Path(); mt.moveTo(150, 785); mt.lineTo(215, 700); mt.lineTo(260, 760); mt.lineTo(285, 730); mt.lineTo(312, 785); mt.close(); c.drawPath(mt, P('#7FB7A4'))
    c.drawCircle(275, 680, 18, P(YEL))
    for hx in (390, 460):
        c.drawLine(hx, 905, hx, 930, P(NAVY, 255, 8)); c.drawCircle(hx, 935, 9, P(NAVY))
    # bedroom decor: window + bed + desk
    rrect(c, 700, 560, 960, 790, 12, P('#BFE7F7')); rrect(c, 700, 560, 960, 790, 12, P(NAVY, 255, 7))
    c.drawLine(830, 560, 830, 790, P(NAVY, 255, 6)); c.drawLine(700, 675, 960, 675, P(NAVY, 255, 6))
    bed(c, 730, FY)
    if charger:
        cx, cy = 905, FY - 152
        cab = skia.Path(); cab.moveTo(cx, cy); cab.cubicTo(cx + 40, cy + 30, cx + 70, cy - 10, cx + 110, cy + 10)
        c.drawPath(cab, P(NAVY, 255, 7))
        rrect(c, cx - 22, cy - 16, cx + 6, cy + 12, 6, P('#FFFFFF')); rrect(c, cx - 22, cy - 16, cx + 6, cy + 12, 6, P(NAVY, 255, 4))
    # floor
    c.drawRect(R(0, FY, W, H), P(FLOOR)); c.drawLine(0, FY, W, FY, P(NAVY, 255, 6))
    # dividing wall with doorway
    rrect(c, WX - 24, -40, WX + 24, DOOR_TOP, 6, P('#E8D3B5')); rrect(c, WX - 24, -40, WX + 24, DOOR_TOP, 6, P(NAVY, 255, 6))
    rrect(c, WX - 34, DOOR_TOP - 6, WX + 34, DOOR_TOP + 18, 6, P(WOOD)); rrect(c, WX - 34, DOOR_TOP - 6, WX + 34, DOOR_TOP + 18, 6, P(NAVY, 255, 5))
    if flash > 0:
        g = skia.Paint(AntiAlias=True)
        g.setShader(skia.GradientShader.MakeLinear([skia.Point(WX - 140, 0), skia.Point(WX + 140, 0)],
                    [C(YEL, 0), C('#FFF6C8', int(230 * flash)), C(YEL, 0)], [0.0, 0.5, 1.0]))
        c.drawRect(R(WX - 140, DOOR_TOP + 18, WX + 140, FY), g)
    door_leaf(c, WX - 24, DOOR_TOP + 18, FY, door)


def mika_box(c, x, y, s, **kw):
    mika(c, x, y, s, **kw)
    rrect(c, x - 62 * s, y - 196 * s, x + 62 * s, y - 92 * s, 8 * s, P('#E0A465'))
    rrect(c, x - 62 * s, y - 196 * s, x + 62 * s, y - 92 * s, 8 * s, P(NAVY, 255, 5 * s))
    c.drawLine(x - 62 * s, y - 168 * s, x + 62 * s, y - 168 * s, P(NAVY, 255, 4 * s))


# ---------------------------------------------------------------- scenes
S1_V = 600 * (math.pi / 2) / 1.4    # entry speed of Mika in s1 (px/s), used for the loop lead-in in s12


def s1_mx(t):
    if t < 0: return 160 + S1_V * t
    return 160 + 600 * math.sin(math.pi / 2 * clamp(t / 1.4))


def s1(c, t, D):
    mx = s1_mx(t)
    walking = t < 1.4
    zt = 1.55
    k = eout((t - zt) / 0.18) if t >= zt else 0.0
    z = 1.1 + 0.35 * k
    c.save(); cam(c, z, 540 + (mx - 540) * k, 1010 + 10 * k)
    wob = 0.0
    if 0.45 < t < 1.3: wob = 0.12 * math.sin((t - 0.45) * 22) * math.exp(-(t - 0.45) * 4)
    two_rooms(c, door=0.85 + wob, flash=clamp(1 - abs(t - 0.6) / 0.25))
    pop_t = 0.6
    look = (0.5, 0)
    if t >= 1.05:
        look = (math.sin((t - 1.05) * 9) * 0.9, -0.2)
    mika(c, mx, FY, 0.95, walk=t * 13 if walking else 0, look=look, mood='o' if t >= 1.05 else 'neutral',
         sweat=t > 1.3)
    hx, hy = mx, FY - 310 * 0.95
    if t < pop_t:
        thought(c, mx + 120, hy - 190, 1.0, icon_charger, s=0.95)
    else:
        u = (t - pop_t) / 0.3
        burst(c, mx + 120, hy - 190, u, r=110, col='#FFFFFF')
        for k in range(6):
            a = math.radians(k * 60 + 20); d = 40 + 160 * eout(u)
            if u < 1: c.drawCircle(mx + 120 + d * math.cos(a), hy - 190 + d * math.sin(a), 16 * (1 - u), P('#FFFFFF'))
    if t >= 1.05:
        k = eback((t - 1.05) / 0.25)
        c.save(); c.translate(hx + 10, hy - 150); c.scale(k, k); c.rotate(8 * math.sin(t * 6)); icon_q(c, 0, 0, 1.15); c.restore()
    c.restore()
    ost(c, "WHY AM I *HERE*?", t, 1.05)


def s2(c, t, D):
    z = 1.08 + 0.1 * (t / D)
    c.save(); cam(c, z, 540, 1000)
    c.drawColor(C(BED))
    rrect(c, 640, 560, 940, 830, 12, P('#BFE7F7')); rrect(c, 640, 560, 940, 830, 12, P(NAVY, 255, 7))
    c.drawLine(790, 560, 790, 830, P(NAVY, 255, 6)); c.drawLine(640, 695, 940, 695, P(NAVY, 255, 6))
    c.drawRect(R(0, 1350, W, H), P(FLOOR)); c.drawLine(0, 1350, W, 1350, P(NAVY, 255, 6))
    blank = t >= 1.55
    mika(c, 540, 1350, 1.05, look=(0, -0.1) if not blank else (0, 0), mood='neutral', sweat=blank)
    c.restore()
    fade = 1 - clamp((t - 1.55) / 0.35)
    # phone with 1 % battery
    if t >= 0.1 and fade > 0:
        k = eback((t - 0.1) / 0.22) * (0.7 + 0.3 * fade)
        c.save(); c.translate(250, 760 - 60 * (1 - fade)); c.scale(k, k); c.rotate(-8)
        rrect(c, -85, -150, 85, 150, 26, P(NAVY)); rrect(c, -70, -125, 70, 125, 12, P('#FFFFFF', 255 * fade))
        blink = 1 if int(t * 5) % 2 == 0 else 0.35
        rrect(c, -40, -70, 34, -20, 8, P(NAVY, 255 * fade, 5)); rrect(c, 34, -55, 44, -35, 3, P(NAVY, 255 * fade))
        rrect(c, -34, -64, -24, -26, 4, P(CORAL, 255 * blink * fade))
        f = skia.Font(F_OST, 64); w = f.measureText("1 %"); c.drawString("1 %", -w / 2, 60, f, P(CORAL, 255 * fade))
        c.restore()
    if t >= 0.81 and fade > 0:
        k = eback((t - 0.81) / 0.22) * (0.7 + 0.3 * fade)
        c.save(); c.translate(830, 1010 - 60 * (1 - fade)); c.scale(k * 1.5, k * 1.5)
        c.saveLayer(None, P('#FFFFFF', 255 * fade)); icon_homework(c, 0, 0, 1.0); c.restore()
        c.restore()
    if blank:
        # ticking timer + tumbleweed
        k = eback((t - 1.55) / 0.2)
        secs = int(clamp((t - 2.13) / (D - 2.3)) * 7) if t >= 2.13 else 0
        c.save(); c.translate(250, 700); c.scale(k, k)
        c.drawCircle(0, 0, 105, P('#FFFFFF')); c.drawCircle(0, 0, 105, P(NAVY, 255, 8))
        a = math.radians(-90 + (t - 1.55) * 240)
        c.drawLine(0, 0, 78 * math.cos(a), 78 * math.sin(a), P(CORAL, 255, 10)); c.drawCircle(0, 0, 12, P(NAVY))
        text(c, f"0:0{secs}", 0, 165, 64, NAVY)
        c.restore()
        if t >= 2.13:
            u = (t - 2.13) / (D - 2.13)
            tx = -120 + 1300 * u; ty = 1312 - abs(math.sin(u * 9)) * 70
            c.save(); c.translate(tx, ty); c.rotate(u * 900)
            for r in (60, 42, 24):
                c.drawCircle(0, 0, r, P('#A9824B', 255, 7))
            c.drawLine(-60, 0, 60, 0, P('#A9824B', 255, 6)); c.drawLine(0, -60, 0, 60, P('#A9824B', 255, 6))
            c.restore()
    ost(c, "TOTAL *BLANK*" if blank else "YOU *HAD* A PLAN", t, 0.1 if not blank else 1.55)


def brain(c, x, y, s, col='#F7A8B8'):
    p = skia.Path()
    for dx, dy, r in ((-90, -30, 80), (-20, -70, 85), (70, -50, 82), (110, 30, 70), (30, 50, 80), (-70, 50, 75)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p.setFillType(skia.PathFillType.kWinding)
    c.drawPath(p, P(NAVY, 255, 14 * s)); c.drawPath(p, P(col))
    for (ax, ay, bx, by, cx2, cy2) in ((-120, -20, -60, -80, -20, -20), (0, -110, 30, -40, 90, -80), (40, 10, 90, 60, 140, 20), (-110, 60, -50, 20, 0, 80)):
        q = skia.Path(); q.moveTo(x + ax * s, y + ay * s); q.quadTo(x + bx * s, y + by * s, x + cx2 * s, y + cy2 * s)
        c.drawPath(q, P('#D9768B', 255, 9 * s))
    c.drawLine(x + 0, y + 120 * s, x + 10 * s, y + 200 * s, P(NAVY, 255, 26 * s)); c.drawLine(x + 0, y + 120 * s, x + 10 * s, y + 200 * s, P('#F7A8B8', 255, 16 * s))


def front_door(c, x, y, s, col='#E9A15B', open_k=0.0):
    """front view door, (x,y)=bottom centre"""
    rrect(c, x - 150 * s, y - 520 * s, x + 150 * s, y, 8 * s, P(WOOD)); rrect(c, x - 150 * s, y - 520 * s, x + 150 * s, y, 8 * s, P(NAVY, 255, 7 * s))
    c.drawRect(R(x - 125 * s, y - 495 * s, x + 125 * s, y), P('#2B3A60'))
    w = 250 * s * (1 - 0.8 * open_k)
    p = skia.Path(); x0 = x - 125 * s
    p.moveTo(x0, y - 495 * s); p.lineTo(x0 + w, y - 495 * s - 30 * s * open_k); p.lineTo(x0 + w, y + 30 * s * open_k); p.lineTo(x0, y); p.close()
    c.drawPath(p, P(col)); c.drawPath(p, P(NAVY, 255, 6 * s))
    if open_k < 0.5:
        for yy in (-450, -250):
            rrect(c, x0 + 30 * s, y + yy * s, x0 + w - 30 * s, y + (yy + 160) * s, 10 * s, P(NAVY, 50))
        c.drawCircle(x0 + w - 32 * s, y - 250 * s, 14 * s, P(YEL)); c.drawCircle(x0 + w - 32 * s, y - 250 * s, 14 * s, P(NAVY, 255, 4 * s))


def s3(c, t, D):
    wt = 1.33
    if t < wt:
        c.drawColor(C(CREAM))
        z = 1.15 - 0.15 * eout(t / 0.4)
        c.save(); cam(c, z, 540, 900)
        bob = 10 * math.sin(t * 5)
        brain(c, 540, 900 + bob, 1.6)
        for k in range(2):
            c.drawCircle(470 + k * 140, 880 + bob, 16, P(NAVY))
        sm = skia.Path(); sm.moveTo(500, 950 + bob); sm.quadTo(540, 980 + bob, 580, 950 + bob); c.drawPath(sm, P(NAVY, 255, 8))
        c.restore()
        if t >= 0.51:
            k = eback((t - 0.51) / 0.2)
            # health bar 100 %
            c.save(); c.translate(540, 1270); c.scale(k, k)
            rrect(c, -300, -46, 300, 46, 24, P('#FFFFFF')); rrect(c, -300, -46, 300, 46, 24, P(NAVY, 255, 7))
            fill = clamp((t - 0.51) / 0.5)
            rrect(c, -288, -34, -288 + 576 * fill, 34, 18, P('#7FCB8A'))
            text(c, f"MEMORY {int(100 * fill)} %", 0, 0, 44, NAVY)
            c.restore()
        if t >= 0.95:
            k = eback((t - 0.95) / 0.18)
            tag(c, "OK ✓".replace("✓", ""), 800, 650, 70, '#7FCB8A', k=k, rot=10)
        ost(c, "NOT YOUR *BRAIN*", t, 0.1)
    else:
        u = t - wt
        sl = 1 - eout(u / 0.22)
        c.save(); c.translate(900 * sl, 0)
        c.drawColor(C('#E9EEF5'))
        for k in range(8):
            yy = 560 + k * 100
            c.drawLine(80, yy, 1000, yy, P(NAVY, 90, 4))
            text(c, f"{7 - k * 0.5:.1f}".rstrip('0').rstrip('.') if False else "", 60, yy, 30)
        for k, lab in enumerate(("7 FT", "6 FT", "5 FT", "4 FT")):
            text(c, lab, 110, 560 + k * 200, 34, '#8B95A8')
        c.drawRect(R(0, 1340, W, H), P('#C9D2DE')); c.drawLine(0, 1340, W, 1340, P(NAVY, 255, 6))
        zz = 1.0 + 0.06 * eout((u - 0.7) / 0.3) if u > 0.7 else 1.0
        c.save(); cam(c, zz, 540, 1000)
        front_door(c, 540, 1340, 1.25, open_k=0.0)
        c.restore()
        c.restore()
        if u > 0.05:
            burst(c, 540, 1000, (u - 0.05) / 0.35, r=260, col=YEL, n=14)
        if t >= 2.07:
            k = eback((t - 2.07) / 0.22)
            tag(c, "SUSPECT", 540, 1210, 72, CORAL, k=k, rot=-6)
            ax = 870 + 20 * math.sin(t * 12)
            p = skia.Path(); p.moveTo(ax, 900); p.lineTo(ax + 70, 850); p.lineTo(ax + 70, 880); p.lineTo(ax + 150, 880); p.lineTo(ax + 150, 920); p.lineTo(ax + 70, 920); p.lineTo(ax + 70, 950); p.close()
            c.save(); c.translate(ax, 900); c.scale(k, k); c.translate(-ax, -900)
            c.drawPath(p, P(CORAL)); c.drawPath(p, P(NAVY, 255, 6)); c.restore()
        ost(c, "BLAME THE *DOOR*", t, wt + 0.05)


# floor-plan path through 4x4 rooms (serpentine)
PLAN_X0, PLAN_Y0, CW, CH = 140, 470, 200, 205
PATH = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3), (2, 3), (1, 3), (0, 3)]
OBJ_COLS = [CORAL, SKY, YEL, '#7FB7A4', '#B98AE6']


def cell_c(i, j):
    return PLAN_X0 + CW * i + CW / 2, PLAN_Y0 + CH * j + CH / 2


def s4(c, t, D):
    z = 1.25 - 0.25 * eout(t / 0.5)
    c.save(); cam(c, z, 540, 880)
    c.drawColor(C(CREAM))
    for n, (i, j) in enumerate(PATH):
        tt = n * 0.03
        if t < tt: continue
        x0, y0 = PLAN_X0 + CW * i, PLAN_Y0 + CH * j
        c.drawRect(R(x0, y0, x0 + CW, y0 + CH), P(HALL if (i + j) % 2 else BED))
    # walls with door gaps along the path
    gaps = set()
    for a, b in zip(PATH, PATH[1:]): gaps.add(tuple(sorted((a, b))))
    wp = P(NAVY, 255, 12)
    for i in range(4):
        for j in range(4):
            x0, y0 = PLAN_X0 + CW * i, PLAN_Y0 + CH * j
            if i < 3:
                xx = x0 + CW
                if ((i, j), (i + 1, j)) in gaps:
                    c.drawLine(xx, y0, xx, y0 + CH * 0.3, wp); c.drawLine(xx, y0 + CH * 0.7, xx, y0 + CH, wp)
                else: c.drawLine(xx, y0, xx, y0 + CH, wp)
            if j < 3:
                yy = y0 + CH
                if ((i, j), (i, j + 1)) in gaps:
                    c.drawLine(x0, yy, x0 + CW * 0.3, yy, wp); c.drawLine(x0 + CW * 0.7, yy, x0 + CW, yy, wp)
                else: c.drawLine(x0, yy, x0 + CW, yy, wp)
    c.drawRect(R(PLAN_X0, PLAN_Y0, PLAN_X0 + 4 * CW, PLAN_Y0 + 4 * CH), P(NAVY, 255, 14))
    # tables with objects
    hl = t >= 1.2
    for n, (i, j) in enumerate(PATH):
        x, y = cell_c(i, j)
        tx, ty = x + 48, y - 48
        rrect(c, tx - 34, ty - 26, tx + 34, ty + 26, 8, P(WOOD)); rrect(c, tx - 34, ty - 26, tx + 34, ty + 26, 8, P(NAVY, 255, 4))
        k = 1.0
        if hl:
            k = 1 + 0.5 * math.sin(clamp((t - 1.2 - n * 0.03) / 0.25) * math.pi)
        c.drawCircle(tx, ty, 13 * k, P(OBJ_COLS[n % 5])); c.drawCircle(tx, ty, 13 * k, P(NAVY, 255, 3))
    # walker: progress along path
    prog = clamp((t - 0.15) / (D - 0.35)) * (len(PATH) - 1)
    k0 = int(prog); f = prog - k0
    a = cell_c(*PATH[min(k0, len(PATH) - 1)]); b = cell_c(*PATH[min(k0 + 1, len(PATH) - 1)])
    wx, wy = a[0] + (b[0] - a[0]) * einout(f), a[1] + (b[1] - a[1]) * einout(f)
    # trail
    pp = P(CORAL, 255, 7); pp.setPathEffect(skia.DashPathEffect.Make([16, 14], 0))
    tr = skia.Path(); tr.moveTo(*cell_c(*PATH[0]))
    for n in range(1, k0 + 1): tr.lineTo(*cell_c(*PATH[n]))
    tr.lineTo(wx, wy); c.drawPath(tr, pp)
    c.drawCircle(wx, wy, 40, P(MUSTARD)); c.drawCircle(wx, wy, 40, P(NAVY, 255, 6))
    c.drawCircle(wx, wy, 24, P('#2A2233'))
    rrect(c, wx + 20, wy - 22, wx + 56, wy + 14, 5, P('#E0A465')); rrect(c, wx + 20, wy - 22, wx + 56, wy + 14, 5, P(NAVY, 255, 4))
    c.restore()
    if t >= 1.89:
        k = eback((t - 1.89) / 0.22)
        tag(c, "55 ROOMS", 760, 1300, 74, CORAL, k=k, rot=-5)
    ost(c, "THE *EXPERIMENT*", t, 0.1)


def lane_a(c, t):
    """top lane: two rooms + doorway"""
    y0, y1, fl = 440, 900, 852
    c.save(); c.clipRect(R(60, y0, 1020, y1))
    c.drawColor(C(HALL)); c.drawRect(R(540, y0, 1020, y1), P(BED))
    c.drawRect(R(60, fl, 1020, y1), P(FLOOR)); c.drawLine(60, fl, 1020, fl, P(NAVY, 255, 5))
    rrect(c, 524, y0 - 10, 556, 640, 4, P('#E8D3B5')); rrect(c, 524, y0 - 10, 556, 640, 4, P(NAVY, 255, 5))
    pass_k = clamp(1 - abs(t - 1.0) / 0.25)
    if pass_k > 0:
        c.drawRect(R(450, 650, 630, fl), P('#FFF6C8', 220 * pass_k))
    door_leaf(c, 524, 652, fl, 0.6)
    u = clamp((t - 0.1) / 1.7)
    mx = 160 + 760 * u
    mika_box(c, mx, fl, 0.55, walk=t * 13 if 0.1 < t < 1.8 else 0, look=(0.6, 0))
    c.restore()
    rrect(c, 60, y0, 1020, y1, 18, P(NAVY, 255, 8))
    tag(c, "A · DOORWAY", 230, y0 + 50, 44, CORAL)


def lane_b(c, t, k):
    y0, y1, fl = 940, 1360, 1312
    c.save(); c.translate(0, 500 * (1 - k))
    c.save(); c.clipRect(R(60, y0, 1020, y1))
    c.drawColor(C(BED))
    c.drawRect(R(60, fl, 1020, y1), P(FLOOR)); c.drawLine(60, fl, 1020, fl, P(NAVY, 255, 5))
    rrect(c, 640, 1040, 860, 1200, 10, P('#BFE7F7')); rrect(c, 640, 1040, 860, 1200, 10, P(NAVY, 255, 6))
    c.drawLine(750, 1040, 750, 1200, P(NAVY, 255, 5))
    u = clamp((t - 1.8) / 1.7)
    mx = 160 + 760 * u
    mika_box(c, mx, fl, 0.55, walk=t * 13 if 1.8 < t < 3.5 else 0, look=(0.6, 0))
    c.restore()
    rrect(c, 60, y0, 1020, y1, 18, P(NAVY, 255, 8))
    tag(c, "B · ONE ROOM", 240, y0 + 50, 44, SKY)
    c.restore()


def ruler(c, y, k):
    if k <= 0: return
    x0, x1 = 160, 160 + 760 * k
    c.drawLine(x0, y, x1, y, P(YEL, 255, 14)); c.drawLine(x0, y, x1, y, P(NAVY, 255, 4))
    for x in (x0, x1):
        c.drawLine(x, y - 22, x, y + 22, P(NAVY, 255, 7))


def s5(c, t, D):
    c.drawColor(C(CREAM))
    lane_a(c, t)
    if t >= 1.75:
        lane_b(c, t, eout((t - 1.75) / 0.3))
    rk = eout((t - 3.4) / 0.35) if t >= 3.4 else 0
    ruler(c, 878, rk); ruler(c, 1338, rk)
    if t >= 3.75:
        k = eback((t - 3.75) / 0.2)
        c.save(); c.translate(540, 920); c.scale(k, k)
        c.drawCircle(0, 0, 50, P(YEL)); c.drawCircle(0, 0, 50, P(NAVY, 255, 6)); text(c, "=", 0, -4, 80, NAVY)
        c.restore()
    ost(c, "SAME *DISTANCE*", t, 0.1)


def s6(c, t, D):
    c.drawColor(C('#E3F3FB'))
    sh = 0
    if 1.52 <= t < 1.75: sh = 10 * math.sin(t * 80) * (1 - (t - 1.52) / 0.23)
    # quiz card
    flip = eout(t / 0.25)
    c.save(); c.translate(540, 780); c.scale(max(0.02, flip), 1)
    rrect(c, -400, -280, 400, 300, 36, P('#FFFFFF')); rrect(c, -400, -280, 400, 300, 36, P(NAVY, 255, 9))
    rrect(c, -400, -280, 400, -170, 36, P(CORAL)); c.drawRect(R(-400, -210, 400, -170), P(CORAL))
    c.drawLine(-400, -170, 400, -170, P(NAVY, 255, 7))
    text(c, "QUIZ TIME!", 0, -228, 62, '#FFFFFF')
    text(c, "What are you holding?", 0, -100, 50, NAVY, F_CAP)
    # options
    for n, (ox, lab) in enumerate(((-200, "A"), (200, "B"))):
        tt = 1.1 + n * 0.18
        if t < tt: continue
        k = eback((t - tt) / 0.2)
        c.save(); c.translate(ox, 80); c.scale(k, k)
        rrect(c, -150, -110, 150, 150, 26, P('#FFF4E0')); rrect(c, -150, -110, 150, 150, 26, P(NAVY, 255, 6))
        if n == 0:
            rrect(c, -50, -40, 50, 70, 14, P(SKY)); rrect(c, -50, -40, 50, 70, 14, P(NAVY, 255, 6))
            c.drawArc(R(30, -10, 90, 50), -90, 180, False, P(NAVY, 255, 10))
        else:
            st = skia.Path()
            for q in range(10):
                rr = 70 if q % 2 == 0 else 30; a = math.radians(q * 36 - 90)
                (st.moveTo if q == 0 else st.lineTo)(rr * math.cos(a), 15 + rr * math.sin(a))
            st.close(); c.drawPath(st, P(YEL)); c.drawPath(st, P(NAVY, 255, 6))
        tag(c, lab, -110, -90, 40, NAVY)
        c.restore()
    # timer bar
    if t >= 0.51:
        u = clamp((t - 0.51) / (D - 0.6))
        rrect(c, -340, 220, 340, 262, 20, P('#E6E9F0'))
        rrect(c, -340, 220, -340 + 680 * (1 - u), 262, 20, P(CORAL if u > 0.6 else YEL))
        rrect(c, -340, 220, 340, 262, 20, P(NAVY, 255, 5))
    c.restore()
    # Mika with closed box, bottom
    c.save(); c.translate(sh, 0)
    mika(c, 540, 1360, 0.72, look=(0, -0.4), mood='worried' if t > 1.52 else 'neutral', sweat=t > 1.52)
    x, y, s = 540, 1360, 0.72
    rrect(c, x - 80, y - 200, x + 80, y - 70, 10, P('#E0A465')); rrect(c, x - 80, y - 200, x + 80, y - 70, 10, P(NAVY, 255, 5))
    c.drawLine(x - 80, y - 168, x + 80, y - 168, P(NAVY, 255, 4))
    if t >= 1.52:
        k = eback((t - 1.52) / 0.2)
        c.save(); c.translate(x, y - 120); c.scale(k, k); icon_q(c, 0, 0, 0.6, NAVY); c.restore()
    c.restore()
    if t >= 0.51:
        n = 3 - min(2, int((t - 0.51) / ((D - 0.6) / 3)))
        k = eback(((t - 0.51) % ((D - 0.6) / 3)) / 0.15)
        c.save(); c.translate(900, 1130); c.scale(k, k)
        c.drawCircle(0, 0, 70, P(CORAL)); c.drawCircle(0, 0, 70, P(NAVY, 255, 7)); text(c, str(n), 0, -2, 90, '#FFFFFF')
        c.restore()
    ost(c, "QUICK *QUIZ*", t, 0.1)


def mini_person(c, x, y, s, bad):
    col = CORAL if bad else GREY
    rrect(c, x - 34 * s, y - 10 * s, x + 34 * s, y + 70 * s, 26 * s, P(col)); rrect(c, x - 34 * s, y - 10 * s, x + 34 * s, y + 70 * s, 26 * s, P(NAVY, 255, 5 * s))
    c.drawCircle(x, y - 40 * s, 30 * s, P('#F5C6A5' if not bad else '#F5C6A5')); c.drawCircle(x, y - 40 * s, 30 * s, P(NAVY, 255, 5 * s))
    if bad:
        for dx in (-10, 10):
            c.drawLine(x + (dx - 5) * s, y - 46 * s, x + (dx + 5) * s, y - 36 * s, P(NAVY, 255, 3.5 * s))
            c.drawLine(x + (dx + 5) * s, y - 46 * s, x + (dx - 5) * s, y - 36 * s, P(NAVY, 255, 3.5 * s))
    else:
        for dx in (-10, 10): c.drawCircle(x + dx * s, y - 40 * s, 4 * s, P(NAVY))


def people_row(c, y, nbad, t_bad, t, t0):
    for k in range(10):
        tt = t0 + k * 0.04
        if t < tt: continue
        kk = eback((t - tt) / 0.18)
        x = 135 + k * 90
        bad = k < nbad and t >= t_bad + k * 0.18
        c.save(); c.translate(x, y); s = kk * (1.15 if bad else 1.0); c.scale(s, s)
        mini_person(c, 0, 0, 1.0, bad)
        c.restore()


def s7(c, t, D):
    c.drawColor(C(CREAM))
    c.drawRect(R(0, 820, W, 1160), P('#FDEBD3', 255 if t >= 2.43 else 0))
    # row A
    text(c, "ONE ROOM", 95, 520, 54, NAVY, align='l')
    people_row(c, 660, 1, 0.95, t, 0.1)
    if t >= 0.95:
        k = eback((t - 0.95) / 0.2)
        c.save(); c.translate(860, 520); c.scale(k, k); text(c, "≈10 %".replace("≈", "~"), 0, 0, 84, CORAL); c.restore()
    if t >= 2.43:
        k = eout((t - 2.43) / 0.2)
        c.save(); c.translate(-300 * (1 - k), 0)
        text(c, "AFTER A DOOR", 95, 880, 54, NAVY, align='l')
        c.restore()
        people_row(c, 1020, 2, 3.44, t, 2.45)
        if t >= 3.5:
            k = eback((t - 3.5) / 0.2)
            c.save(); c.translate(880, 880); c.scale(k, k); text(c, "~20 %", 0, 0, 84, CORAL); c.restore()
    if t >= 3.95:
        k = eback((t - 3.95) / 0.22)
        c.save(); c.translate(540, 1265); c.rotate(-6); c.scale(k, k)
        rrect(c, -260, -70, 260, 70, 30, P(CORAL)); rrect(c, -260, -70, 260, 70, 30, P(NAVY, 255, 8))
        text(c, "2× MISTAKES", 0, -4, 70, '#FFFFFF')
        c.restore()
    ost(c, "WHO *FORGOT*?", t, 0.1)


SCENE_ICONS = [HALL, BED, '#E5F5E8', '#FDEBD3', HALL, BED, '#E5F5E8', '#FDEBD3']


def frame_pic(c, x0, y0, x1, y1, kind):
    c.drawRect(R(x0, y0, x1, y1), P(SCENE_ICONS[kind % 4]))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = kind % 4
    if k == 0:   # hallway door
        rrect(c, cx - 30, cy - 60, cx + 30, y1 - 8, 4, P('#E9A15B')); rrect(c, cx - 30, cy - 60, cx + 30, y1 - 8, 4, P(NAVY, 255, 4))
    elif k == 1:  # bed
        rrect(c, cx - 70, cy + 10, cx + 70, cy + 50, 8, P(SKY)); rrect(c, cx - 70, cy + 10, cx + 70, cy + 50, 8, P(NAVY, 255, 4))
    elif k == 2:  # kitchen fridge
        rrect(c, cx - 32, cy - 64, cx + 32, y1 - 8, 8, P('#FFFFFF')); rrect(c, cx - 32, cy - 64, cx + 32, y1 - 8, 8, P(NAVY, 255, 4))
        c.drawLine(cx - 32, cy - 10, cx + 32, cy - 10, P(NAVY, 255, 4))
    else:        # classroom board
        rrect(c, cx - 70, cy - 50, cx + 70, cy + 30, 6, P('#2E5A55')); rrect(c, cx - 70, cy - 50, cx + 70, cy + 30, 6, P(NAVY, 255, 4))
    c.drawCircle(cx + (40 if k != 1 else -20), y1 - 40, 16, P(MUSTARD)); c.drawCircle(cx + (40 if k != 1 else -20), y1 - 56, 12, P('#F5C6A5'))


def strip(c, x, y, n, fw=240, fh=200, start_kind=0):
    """film strip starting at x, n frames"""
    w = n * fw
    c.drawRect(R(x, y - fh / 2 - 34, x + w, y + fh / 2 + 34), P(NAVY))
    for k in range(n):
        fx = x + k * fw
        frame_pic(c, fx + 14, y - fh / 2, fx + fw - 14, y + fh / 2, start_kind + k)
        for hx in range(4):
            rrect(c, fx + 18 + hx * 58, y - fh / 2 - 26, fx + 50 + hx * 58, y - fh / 2 - 10, 4, P(CREAM))
            rrect(c, fx + 18 + hx * 58, y + fh / 2 + 10, fx + 50 + hx * 58, y + fh / 2 + 26, 4, P(CREAM))


def s8(c, t, D):
    c.drawColor(C('#F3ECFA'))
    cut = 2.82
    # brain recorder
    bk = eback((t - 0.1) / 0.25)
    c.save(); c.translate(540, 1150); c.scale(bk * 0.75, bk * 0.75); c.translate(-540, -1150)
    brain(c, 540, 1150, 1.0)
    c.restore()
    if t >= 0.1:
        on = int(t * 3) % 2 == 0
        rrect(c, 700, 1000, 880, 1060, 16, P('#FFFFFF')); rrect(c, 700, 1000, 880, 1060, 16, P(NAVY, 255, 5))
        c.drawCircle(735, 1030, 14, P(CORAL if on else '#F3B7B0')); text(c, "REC", 800, 1028, 38, NAVY)
    if t < cut:
        if t >= 0.65:
            k = eout((t - 0.65) / 0.3)
            off = -((t - 0.65) * 320) % 240
            c.save(); c.translate(1100 * (1 - k), 0)
            strip(c, -240 + off, 700, 7)
            c.restore()
        if t >= 1.8:
            k = eback((t - 1.8) / 0.2)
            tag(c, "1 LONG VIDEO?", 540, 900, 52, SKY, k=k, rot=-3)
    else:
        u = t - cut
        off = -((cut - 0.65) * 320) % 240
        # pieces separate
        sep = eout(u / 0.35)
        for k in range(3):
            fx = 60 + k * 330
            c.save()
            dx = (k - 1) * 30 * sep; rot = (k - 1) * 6 * sep; dy = -20 * sep * (1 if k != 1 else -0.5)
            c.translate(fx + 150 + dx, 700 + dy); c.rotate(rot); c.translate(-(fx + 150), -700)
            c.drawRect(R(fx, 700 - 134, fx + 300, 700 + 134), P(NAVY))
            frame_pic(c, fx + 14, 600, fx + 286, 800, k)
            for hx in range(5):
                rrect(c, fx + 14 + hx * 58, 700 - 126, fx + 46 + hx * 58, 700 - 110, 4, P(CREAM))
                rrect(c, fx + 14 + hx * 58, 700 + 110, fx + 46 + hx * 58, 700 + 126, 4, P(CREAM))
            if t >= 3.42 + k * 0.15:
                kk = eback((t - 3.42 - k * 0.15) / 0.2)
                tag(c, f"SCENE {k + 1}", fx + 150, 880, 40, YEL, fg=NAVY, k=kk)
            c.restore()
        # scissors snap
        if u < 0.45:
            sx = 390 + 330 * clamp(u / 0.3)
            a = 25 * (1 - abs(math.sin(u * 20)))
            for sg in (-1, 1):
                c.save(); c.translate(sx, 700); c.rotate(sg * a)
                rrect(c, -10, -8, 150, 8, 8, P(GREY)); rrect(c, -10, -8, 150, 8, 8, P(NAVY, 255, 4))
                c.drawCircle(-50, sg * 26, 30, P(CORAL, 255, 14)); c.drawCircle(-50, sg * 26, 30, P(NAVY, 255, 4))
                c.restore()
        for xx in (390, 720):
            burst(c, xx, 700, (u - 0.05) / 0.3, r=80, col=YEL, n=8)
    ost(c, "LIFE IN *SCENES*" if t >= cut else "YOUR *BRAIN*", t, cut if t >= cut else 0.1)


def clapper(c, x, y, s, open_a, label):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -150, 0, 150, 170, 12, P(NAVY)); rrect(c, -150, 0, 150, 170, 12, P(NAVY, 255, 6))
    f = skia.Font(F_OST, 52); w = f.measureText(label); c.drawString(label, -w / 2, 110, f, P('#FFFFFF'))
    c.save(); c.translate(-150, 0); c.rotate(-open_a)
    rrect(c, 0, -46, 300, 0, 6, P('#FFFFFF')); rrect(c, 0, -46, 300, 0, 6, P(NAVY, 255, 5))
    for k in range(5):
        p = skia.Path(); x0 = 10 + k * 60; p.moveTo(x0, -46); p.lineTo(x0 + 30, -46); p.lineTo(x0 + 10, 0); p.lineTo(x0 - 20, 0); p.close()
        c.drawPath(p, P(NAVY))
    c.restore()
    c.restore()


def s9(c, t, D):
    z = 1.0 + 0.05 * (t / D)
    c.save(); cam(c, z, 540, 1000)
    mx = 200 + 600 * clamp(t / 1.3)
    two_rooms(c, door=0.85, flash=clamp(1 - abs(t - 0.55) / 0.2))
    mika(c, mx, FY, 0.95, walk=t * 13 if t < 1.3 else 0, look=(0.5, 0))
    # chapter tags
    if t >= 1.42:
        tag(c, "CHAPTER 1", 270, 520, 50, GREY, fg=NAVY, k=eback((t - 1.42) / 0.2), rot=-3)
    if t >= 1.98:
        tag(c, "CHAPTER 2", 810, 520, 50, YEL, fg=NAVY, k=eback((t - 1.98) / 0.2), rot=3)
    c.restore()
    # clapper over the doorway
    if t >= 0.15:
        drop = 1 - eout((t - 0.15) / 0.25)
        a = 28 if t < 0.55 else 28 * (1 - clamp((t - 0.55) / 0.06))
        clapper(c, 540, 690 - 500 * drop, 0.9, a, "CUT!")
    # film-cut letterbox flash
    if 0.55 <= t < 0.8:
        u = (t - 0.55) / 0.25
        hh = 160 * math.sin(u * math.pi)
        c.drawRect(R(0, 0, W, hh), P(NAVY)); c.drawRect(R(0, H - hh, W, H), P(NAVY))
        c.drawRect(R(0, 0, W, H), P('#FFFFFF', 120 * (1 - u)))
    ost(c, "DOOR = *CUT*", t, 0.6)


def cabinet(c, x, y, drawer_out, xray=0.0):
    """(x,y) = bottom centre of a 3-drawer file cabinet"""
    w, h = 320, 600
    rrect(c, x - w / 2, y - h, x + w / 2, y, 14, P('#9FB2C8')); rrect(c, x - w / 2, y - h, x + w / 2, y, 14, P(NAVY, 255, 8))
    for k in range(3):
        y0 = y - h + 20 + k * 193
        if k == 0: continue
        rrect(c, x - w / 2 + 18, y0, x + w / 2 - 18, y0 + 175, 10, P('#B9C9DB')); rrect(c, x - w / 2 + 18, y0, x + w / 2 - 18, y0 + 175, 10, P(NAVY, 255, 6))
        rrect(c, x - 50, y0 + 70, x + 50, y0 + 98, 12, P(NAVY))
    # top drawer (animated)
    y0 = y - h + 20; d = 120 * drawer_out
    rrect(c, x - w / 2 + 18 - d * 0.25, y0 - d * 0.5, x + w / 2 - 18 + d * 0.25, y0 + 175 + d * 0.15, 10, P('#C9D7E6'))
    rrect(c, x - w / 2 + 18 - d * 0.25, y0 - d * 0.5, x + w / 2 - 18 + d * 0.25, y0 + 175 + d * 0.15, 10, P(NAVY, 255, 6))
    rrect(c, x - 50, y0 + 70, x + 50, y0 + 98, 12, P(NAVY))
    rrect(c, x - 70, y0 + 24, x + 70, y0 + 58, 6, P('#FFFFFF')); text(c, "OLD SCENES", x, y0 + 41, 22, NAVY)
    if xray > 0:
        c.saveLayer(None, P('#FFFFFF', 255 * xray))
        rrect(c, x - w / 2 + 30, y0 + 12, x + w / 2 - 30, y0 + 165, 8, P('#1E2A47', 220))
        rrect(c, x - 110, y0 + 40, x + 60, y0 + 160, 8, P(YEL)); rrect(c, x - 110, y0 + 40, x + 60, y0 + 160, 8, P(NAVY, 255, 4))
        icon_charger(c, x - 25, y0 + 100, 0.7)
        c.restore()


def s10(c, t, D):
    c.drawColor(C('#EAF4EC'))
    c.drawRect(R(0, 1340, W, H), P(FLOOR)); c.drawLine(0, 1340, W, 1340, P(NAVY, 255, 6))
    sh = 0
    if 1.65 <= t < 1.9: sh = 12 * math.sin(t * 90) * (1 - (t - 1.65) / 0.25)
    c.save(); c.translate(sh, 0)
    cx, cy = 420, 1340
    drawer = clamp((t - 0.2) / 0.3) if t < 1.55 else 1 - clamp((t - 1.55) / 0.1)
    xr = clamp((t - 1.96) / 0.25)
    cabinet(c, cx, cy, eout(drawer), xr)
    # folder flies into the drawer
    if 0.1 <= t < 1.6:
        u = clamp((t - 0.6) / 0.85)
        fx = 820 - 400 * einout(u); fy = 600 + 140 * einout(u) - 160 * math.sin(u * math.pi)
        sc = 1.0 - 0.5 * u
        k = eback((t - 0.1) / 0.2)
        c.save(); c.translate(fx, fy); c.rotate(-12 + 20 * u); c.scale(k * sc, k * sc)
        rrect(c, -150, -110, -40, -80, 8, P(YEL)); rrect(c, -150, -100, 150, 110, 12, P(YEL)); rrect(c, -150, -100, 150, 110, 12, P(NAVY, 255, 6))
        text(c, "SCENE 1", 0, -60, 40, NAVY)
        icon_charger(c, 0, 30, 0.8)
        c.restore()
    if t >= 1.65:
        burst(c, cx, cy - 500, (t - 1.65) / 0.3, r=160, col='#FFFFFF', n=10)
    c.restore()
    # Mika, puzzled
    mika(c, 860, 1340, 0.75, look=(-0.7, -0.2), mood='o' if t > 1.96 else 'neutral', sweat=t > 1.96)
    if t >= 1.96:
        k = eback((t - 1.96) / 0.2)
        c.save(); c.translate(880, 990); c.scale(k, k); icon_q(c, 0, 0, 0.8); c.restore()
    if t >= 2.73:
        tag(c, "ARCHIVED", 420, 640, 70, CORAL, k=eback((t - 2.73) / 0.2), rot=-8)
    ost(c, "FILED *AWAY*", t, 0.1)


def s11(c, t, D):
    c.drawColor(C(HALL))
    off = (t * 420)
    # scrolling wall stripes + doors
    c.drawRect(R(0, 1060, W, 1080), P('#BFE0EF'))
    for k in range(-1, 6):
        x = k * 300 - off % 300
        c.drawLine(x, 400, x, 1330, P('#C9E4F1', 255, 6))
    dx = 1250 - (t - 1.6) * 900 if t >= 1.6 else 2000
    if dx < 1400:
        rrect(c, dx - 130, 860, dx + 130, 1330, 8, P(WOOD)); rrect(c, dx - 110, 880, dx + 110, 1330, 4, P('#2B3A60'))
        rrect(c, dx - 130, 860, dx + 130, 1330, 8, P(NAVY, 255, 7))
    c.drawRect(R(0, 1330, W, H), P(FLOOR)); c.drawLine(0, 1330, W, 1330, P(NAVY, 255, 6))
    for k in range(8):
        x = k * 160 - (off * 1.0) % 160
        c.drawLine(x, 1345, x + 60, 1345, P(NAVY, 60, 5))
    x, y, s = 560, 1330, 0.95
    mika(c, x, y, s, walk=t * 12, look=(0.6, 0.9))
    # phone raised in right hand
    px, py = x + 70 * s, y - 175 * s
    rrect(c, px - 28, py - 50, px + 28, py + 50, 10, P(NAVY)); rrect(c, px - 20, py - 40, px + 20, py + 38, 5, P('#BFE7F7'))
    # chat bubbles
    for n, tt in enumerate((0.3, 0.75, 1.2, 1.65, 2.1)):
        if t < tt: continue
        k = eback((t - tt) / 0.18)
        bx = 700 + (n % 2) * 140; by = 800 - (t - tt) * 120
        a = clamp(1 - (t - tt - 0.9) / 0.4)
        if a <= 0: continue
        c.save(); c.translate(bx, by); c.scale(k, k)
        rrect(c, -80, -40, 80, 40, 28, P('#FFFFFF', 255 * a)); rrect(c, -80, -40, 80, 40, 28, P(NAVY, 255 * a, 5))
        for d in range(3): c.drawCircle(-34 + d * 34, 0, 9, P(SKY if n % 2 else CORAL, 255 * a))
        c.restore()
    # thought bubble pops when passing the door
    if t < 2.35:
        thought(c, 400, 820, eback(t / 0.2), icon_charger, s=0.85, tail=(110, 140))
    else:
        burst(c, 400, 820, (t - 2.35) / 0.3, r=100, col='#FFFFFF')
    # brain load meter
    fill = clamp((t - 0.1) / 1.05)
    mx0, my0, my1 = 110, 520, 1180
    rrect(c, mx0 - 44, my0, mx0 + 44, my1, 40, P('#FFFFFF')); rrect(c, mx0 - 44, my0, mx0 + 44, my1, 40, P(NAVY, 255, 7))
    top = my1 - 12 - (my1 - my0 - 24) * eout(fill)
    rrect(c, mx0 - 32, top, mx0 + 32, my1 - 12, 30, P(CORAL if fill > 0.7 else YEL))
    text(c, f"{int(100 * eout(fill))} %", mx0 + 10, my0 - 50, 50, CORAL if fill > 0.7 else NAVY, align='c')
    text(c, "LOAD", mx0, my1 + 50, 40, NAVY)
    ost(c, "BUSY MIND = *WORSE*", t, 0.1)


DOOR_COLS = [('#E9A15B', '#FDE3D2'), ('#7FB7A4', '#E5F5E8'), ('#4FC3F7', '#FFF0D4')]
_S1F0 = None


def s12(c, t, D):
    global _S1F0
    seg = 1.55
    if t < seg:
        n = min(2, int(t / 0.5)); u = t - n * 0.5
        dcol, bg = DOOR_COLS[n]
        sl = 1 - eout(u / 0.16)
        c.drawColor(C(bg))
        c.save(); c.translate(1080 * sl, 0)
        c.drawRect(R(0, 1340, W, H), P(FLOOR)); c.drawLine(0, 1340, W, 1340, P(NAVY, 255, 6))
        front_door(c, 540, 1340, 1.25, col=dcol, open_k=clamp((u - 0.12) / 0.25))
        mika(c, 540, 1340, 0.7, look=(0, 0), mood='o', sweat=True)
        kq = eback((u - 0.2) / 0.18) if u >= 0.2 else 0
        if kq > 0:
            c.save(); c.translate(560, 840); c.scale(kq, kq); icon_q(c, 0, 0, 0.9); c.restore()
        c.restore()
        text(c, f"#{n + 1}", 920, 560, 90, CORAL)
        ost(c, "EVERY *TIME*", t, 0.1)
    else:
        u = t - seg
        span = D - seg
        tl = t - D          # negative: time before s1 frame 0
        z = 1.0 + 0.6 * (1 - einout(clamp(u / max(0.1, span - 0.45))))
        c.save(); cam(c, z, 540, 960 + 70 * (z - 1))
        s1(c, tl, 3.0)
        c.restore()
        if u < 0.12:
            c.drawRect(R(0, 0, W, H), P('#FFFFFF', 200 * (1 - u / 0.12)))
        # no crossfade needed: s1 is drawn at negative time, so the last frame here continues straight into s1 frame 0


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]


def sfx_cues(put, S, K, D, fx):
    """put(t_seconds, signal, gain); S = scene starts, K = time factor (1.0 without DESIGN_DUR), D = scene durations"""
    q = lambda i, t: S[i] + t * K[i]
    put(q(0, 0.0), fx.whoosh(.4, 200, 2000), .3)
    put(q(0, 0.58), fx.whoosh(.2, 900, 7000), .5); put(q(0, 0.6), fx.pop(500), .7)
    put(q(0, 1.05), fx.chime(), .7)
    put(q(0, 1.55), fx.subhit(), .7); put(q(0, 1.55), fx.whoosh(.16, 800, 6000), .4)
    put(q(1, 0.1), fx.pop(700), .6); put(q(1, 0.81), fx.pop(820), .6)
    put(q(1, 1.55), fx.whoosh(.35, 200, 1500), .4)
    put(q(1, 2.13), fx.ratsch(0.9), .5)
    put(q(2, 0.51), fx.ratsch(0.5), .5); put(q(2, 0.95), fx.chime(), .5)
    put(q(2, 1.28), fx.whoosh(.25, 600, 7000), .6); put(q(2, 1.36), fx.thud(), .8); put(q(2, 1.36), fx.clack(), .5)
    put(q(2, 2.07), fx.cringe(), .6)
    put(q(3, 0.0), fx.whoosh(.3, 400, 4000), .4)
    for k in range(5): put(q(3, 1.2 + k * 0.08), fx.pop(600 + 60 * k), .35)
    put(q(3, 1.89), fx.clack(), .7)
    put(q(4, 0.1), fx.whoosh(.3, 300, 3000), .35); put(q(4, 1.0), fx.chime(), .4)
    put(q(4, 1.75), fx.whoosh(.3, 300, 3000), .45)
    put(q(4, 3.4), fx.ratsch(0.35), .6); put(q(4, 3.75), fx.pop(900), .7)
    put(q(5, 0.0), fx.whoosh(.2, 900, 6000), .5); put(q(5, 0.05), fx.clack(), .5)
    for k in range(3): put(q(5, 0.51 + k * (D[5] - 0.6) / 3), fx.click(), 1.0)
    put(q(5, 1.1), fx.pop(700), .5); put(q(5, 1.28), fx.pop(800), .5)
    put(q(5, 1.52), fx.cringe(), .5)
    for k in range(10): put(q(6, 0.1 + k * 0.04), fx.click(), .4)
    put(q(6, 0.95), fx.thud(), .6)
    put(q(6, 2.43), fx.whoosh(.25, 500, 5000), .5)
    for k in range(2): put(q(6, 3.44 + k * 0.18), fx.thud(), .6)
    put(q(6, 3.95), fx.clack(), .8); put(q(6, 3.95), fx.subhit(), .7)
    put(q(7, 0.1), fx.pop(500), .5); put(q(7, 0.65), fx.projector(2.1), .7)
    put(q(7, 2.82), fx.clack(), .9); put(q(7, 2.9), fx.whoosh(.3, 600, 6000), .5)
    for k in range(3): put(q(7, 3.42 + k * 0.15), fx.pop(700 + 100 * k), .5)
    put(q(8, 0.15), fx.whoosh(.25, 300, 3000), .4); put(q(8, 0.55), fx.clack(), 1.0); put(q(8, 0.55), fx.subhit(), .6)
    put(q(8, 1.42), fx.pop(650), .5); put(q(8, 1.98), fx.pop(850), .5)
    put(q(9, 0.1), fx.pop(600), .4); put(q(9, 0.6), fx.whoosh(.8, 200, 2500), .5)
    put(q(9, 1.65), fx.thud(), 1.0); put(q(9, 1.65), fx.clack(), .6)
    put(q(9, 1.96), fx.chime(), .5); put(q(9, 2.73), fx.clack(), .7)
    put(q(10, 0.1), fx.riser(1.0), .4)
    for tt in (0.3, 0.75, 1.2, 1.65, 2.1): put(q(10, tt), fx.pop(900), .35)
    put(q(10, 2.35), fx.pop(450), .7); put(q(10, 2.35), fx.whoosh(.2, 800, 6000), .4)
    for k in range(3): put(q(11, k * 0.5), fx.whoosh(.18, 700, 6000), .5); put(q(11, k * 0.5 + 0.2), fx.pop(600 + 150 * k), .45)
    put(q(11, 1.55), fx.whoosh(.5, 150, 1500), .4)
    put(q(11, 1.7), fx.riser(D[11] - 1.7), .7)
