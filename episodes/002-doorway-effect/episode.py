"""Episode 002 – The Doorway Effect (EN). Hook type: relatable moment."""
import math, skia
from lib import *

META = {
    "id": "002-doorway-effect",
    "topic": "Doorway effect – walking through a door makes you forget why you came",
    "source": "Radvansky, Krawietz & Tamplin (2011), Quarterly Journal of Experimental Psychology 64(8); caveat: McFadyen et al. (2021), BMC Psychology",
    "youtube_title": "Why you forget why you walked into a room #shorts",
    "youtube_description": "The doorway effect: walking through a door can wipe what you came for. In a study with 55 virtual rooms, memory mistakes roughly doubled right after a doorway (about 10% vs 20%) compared to walking the same distance inside one room (Radvansky, Krawietz & Tamplin, 2011, Quarterly Journal of Experimental Psychology). Your brain treats the door as an event boundary and files the old scene away. A 2021 replication found it mostly when the mind is busy (McFadyen et al., BMC Psychology). Send this to someone who always forgets why they walked into the kitchen. #psychology #doorwayeffect #memory #shorts",
    "fact_comment": "📚 The facts: In Radvansky, Krawietz & Tamplin (2011, Quarterly Journal of Experimental Psychology), people moving through 55 virtual rooms made about twice as many memory errors right after a doorway (~20%) as after walking the same distance in one room (~10%); in a real-room experiment the gap was smaller (~28% vs ~23%). A 2021 replication (McFadyen et al., BMC Psychology) mostly found the effect only when people were also mentally busy, so treat it as a 'busy mind + doorway' effect, not a guarantee.",
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

# engine v2 options
TRANSITIONS = ['zoom', 'whip', 'wipe', 'whipv', 'zoom', 'wipe', 'whip', 'zoom', 'whip', 'wipe', 'whip']
AMBIENCE = ['room', 'room', 'hum', 'clock', 'room', 'cafe', 'cafe', 'projector', 'room', 'clock', 'cafe', 'room']


# ---------------------------------------------------------------- helpers / props
def R(x0, y0, x1, y1):
    return skia.Rect.MakeLTRB(x0, y0, x1, y1)


def text(c, s, x, y, size, col=NAVY, tf=None, align='c'):
    f = skia.Font(tf or F_OST, size); w = f.measureText(s)
    xx = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    c.drawString(s, xx, y + size * 0.36, f, P(col))
    return w


def pk(t, t0, d=0.28):
    """squash&stretch pair for a pop starting at t0 (None before)"""
    return squash((t - t0) / d) if t >= t0 else (0.0, 0.0)


def burst(c, x, y, u, r=90, col=YEL, n=10):
    """radial pop lines, u in 0..1"""
    if u <= 0 or u >= 1: return
    for k in range(n):
        a = math.radians(k * 360 / n + 9)
        r0, r1 = r * (0.4 + 0.8 * u), r * (0.7 + 1.0 * u)
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(NAVY, 255 * (1 - u), 13))
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), P(col, 255 * (1 - u), 7))


def icon_charger(c, x, y, s):
    cab = skia.Path(); cab.moveTo(x, y + 30 * s); cab.cubicTo(x, y + 80 * s, x + 60 * s, y + 40 * s, x + 50 * s, y + 70 * s)
    c.drawPath(cab, P(NAVY, 255, 14 * s)); c.drawPath(cab, P('#FFFFFF', 255, 7 * s))
    for dx in (-13, 13):
        rrect(c, x + (dx - 5) * s, y - 56 * s, x + (dx + 5) * s, y - 26 * s, 3 * s, P(GREY)); rrect(c, x + (dx - 5) * s, y - 56 * s, x + (dx + 5) * s, y - 26 * s, 3 * s, P(NAVY, 255, 3 * s))
    shaded_rrect(c, x - 32 * s, y - 30 * s, x + 32 * s, y + 34 * s, 12 * s, '#FFFFFF', 5 * s, 0.86)
    bolt = skia.Path(); bolt.moveTo(x + 4 * s, y - 18 * s); bolt.lineTo(x - 10 * s, y + 6 * s); bolt.lineTo(x + 2 * s, y + 6 * s); bolt.lineTo(x - 4 * s, y + 24 * s)
    bolt.lineTo(x + 12 * s, y - 2 * s); bolt.lineTo(x, y - 2 * s); bolt.close(); c.drawPath(bolt, P(YEL)); c.drawPath(bolt, P(NAVY, 255, 2.5 * s))


def icon_homework(c, x, y, s):
    c.save(); c.translate(x, y); c.rotate(-6)
    rrect(c, -40 * s, -48 * s, 56 * s, 72 * s, 6 * s, blurred(NAVY, 60, 8 * s))
    rrect(c, -40 * s, -56 * s, 56 * s, 64 * s, 6 * s, P('#F1EDE4')); rrect(c, -40 * s, -56 * s, 56 * s, 64 * s, 6 * s, P(NAVY, 255, 4 * s))
    rrect(c, -48 * s, -60 * s, 48 * s, 60 * s, 6 * s, P('#FFFFFF')); rrect(c, -48 * s, -60 * s, 48 * s, 60 * s, 6 * s, P(NAVY, 255, 5 * s))
    c.drawLine(-30 * s, -60 * s, -30 * s, 60 * s, P(CORAL, 120, 3 * s))
    f = skia.Font(F_OST, 20 * s); w = f.measureText("MATH"); c.drawString("MATH", -w / 2 + 6 * s, -34 * s, f, P(CORAL))
    for k in range(4):
        c.drawLine(-22 * s, (-14 + k * 18) * s, (32 - (k % 2) * 18) * s, (-14 + k * 18) * s, P(SKY, 255, 5 * s))
    c.drawCircle(30 * s, 40 * s, 12 * s, P(CORAL, 255, 3 * s))
    c.restore()


def icon_q(c, x, y, s, col=CORAL):
    f = skia.Font(F_OST, 120 * s); w = f.measureText("?")
    c.drawString("?", x - w / 2 + 5 * s, y + 52 * s, f, blurred(NAVY, 70, 5 * s))
    c.drawString("?", x - w / 2, y + 44 * s, f, P(NAVY, 255, 12 * s))
    c.drawString("?", x - w / 2, y + 44 * s, f, P(col))
    c.drawString("?", x - w / 2, y + 44 * s, f, P('#FFFFFF', 0))


def thought(c, x, y, k, icon, s=1.0, tail=(-80, 130)):
    """shaded thought cloud centred at (x,y); tail points toward the head"""
    if k <= 0: return
    c.save(); c.translate(x, y + 4 * osc(0.6)); c.scale(k * s, k * s)
    tx, ty = tail
    for f, r in ((0.55, 16), (0.85, 11)):
        c.drawCircle(tx * f, ty * f, r, P('#FFFFFF')); c.drawCircle(tx * f, ty * f, r, P(NAVY, 255, 5))
    cl = skia.Path()
    for dx, dy, r in ((-58, 8, 52), (0, -22, 62), (58, 6, 52), (0, 34, 50)):
        cl.addCircle(dx, dy, r)
    cl.setFillType(skia.PathFillType.kWinding)
    c.save(); c.translate(6, 14); c.drawPath(cl, blurred(NAVY, 60, 10)); c.restore()
    c.drawPath(cl, P(NAVY, 255, 10))
    shaded_path(c, cl, '#FFFFFF', 0, 0.9, light=(-0.5, -1), shift=0.07)
    if icon: icon(c, 0, 4, 0.82)
    c.restore()


def bed(c, x, y):
    """bed, (x,y) = left foot on floor"""
    contact_shadow(c, x + 160, y + 4, 380, 30)
    shaded_rrect(c, x + 300, y - 260, x + 330, y, 10, WOOD, 5, 0.8)
    shaded_rrect(c, x, y - 120, x + 320, y - 50, 14, '#FFFFFF', 5, 0.86)
    shaded_rrect(c, x - 10, y - 140, x + 220, y - 60, 22, SKY, 5, 0.84)
    for q in range(3): c.drawLine(x + 30 + q * 60, y - 132, x + 50 + q * 60, y - 70, P('#FFFFFF', 90, 4))
    shaded_rrect(c, x + 222, y - 160, x + 296, y - 116, 18, '#FFFFFF', 4, 0.88)
    for dx in (14, 300):
        c.drawLine(x + dx, y - 50, x + dx, y, P(NAVY, 255, 10))


def jacket(c, x, y):
    """jacket hanging from a hook at (x, y)"""
    c.save(); c.translate(x, y); c.rotate(2.5 * osc(0.2, 3))
    j = skia.Path(); j.moveTo(-20, 0); j.lineTo(20, 0); j.lineTo(62, 40); j.lineTo(66, 200); j.lineTo(-66, 200); j.lineTo(-62, 40); j.close()
    shaded_path(c, j, CORAL, 5, 0.84)
    c.drawLine(0, 10, 0, 196, P(NAVY, 255, 4))
    for sg in (-1, 1):
        sl = skia.Path(); sl.moveTo(sg * 58, 44); sl.lineTo(sg * 80, 170); sl.lineTo(sg * 60, 176); sl.lineTo(sg * 46, 70); sl.close()
        shaded_path(c, sl, tint(CORAL, 0.92), 4, 0.86)
    c.drawCircle(0, -4, 9, P(NAVY))
    c.restore()


def nightstand(c, x, y):
    contact_shadow(c, x, y + 2, 150, 20)
    shaded_rrect(c, x - 60, y - 120, x + 60, y, 10, WOOD, 5, 0.82)
    c.drawLine(x - 60, y - 62, x + 60, y - 62, P(NAVY, 255, 4)); c.drawCircle(x, y - 92, 6, P(NAVY)); c.drawCircle(x, y - 32, 6, P(NAVY))
    # lamp
    c.drawLine(x, y - 120, x, y - 190, P(NAVY, 255, 6))
    glow(c, x, y - 205, 120, '#FFF3B0', 120)
    sh = skia.Path(); sh.moveTo(x - 26, y - 230); sh.lineTo(x + 26, y - 230); sh.lineTo(x + 44, y - 186); sh.lineTo(x - 44, y - 186); sh.close()
    shaded_path(c, sh, YEL, 5, 0.85)
    shaded_rrect(c, x - 28, y - 132, x + 28, y - 118, 6, NAVY, 3, 0.8)


def door_leaf(c, x, y0, y1, k, col='#E9A15B', side=-1):
    """door seen in cut-away, hinged at x, swung toward the viewer by k (0 closed .. 1 open)"""
    w = 150 * k
    p = skia.Path(); p.moveTo(x, y0); p.lineTo(x + side * w, y0 - 20 * k); p.lineTo(x + side * w, y1 + 26 * k); p.lineTo(x, y1); p.close()
    shaded_path(c, p, col, 6, 0.84, light=(1, -0.3), shift=0.12)
    if k > 0.3:
        for f0, f1 in ((0.08, 0.42), (0.52, 0.9)):
            q = skia.Path()
            xa, xb = x + side * w * 0.22, x + side * w * 0.8
            q.moveTo(xa, y0 + (y1 - y0) * f0 - 4 * k); q.lineTo(xb, y0 + (y1 - y0) * f0 - 14 * k); q.lineTo(xb, y0 + (y1 - y0) * f1 + 10 * k); q.lineTo(xa, y0 + (y1 - y0) * f1 + 4 * k); q.close()
            c.drawPath(q, P(NAVY, 70, 4))
    if k > 0.2:
        shaded_circle(c, x + side * w * 0.86, (y0 + y1) / 2 + 10, 10, YEL, 3, 0.8)


def two_rooms(c, door=1.0, flash=0.0, charger=True):
    # hallway
    wall(c, -300, -200, WX, FY, HALL, 'panel')
    picture(c, 110, 600, 320, 770, kind=0)
    shaded_rrect(c, 150, 896, 330, 914, 5, WOOD, 4, 0.8)
    for hx in (200, 280): c.drawLine(hx, 905, hx, 930, P(NAVY, 255, 7))
    c.drawCircle(280, 936, 9, P(NAVY))
    jacket(c, 200, 930)
    # bedroom
    wall(c, WX, -200, W + 300, FY, BED, 'dots')
    window(c, 720, 560, 960, 780, curtains=SKY)
    picture(c, 590, 640, 660, 730, kind=3, frame='#FFFFFF')
    light_patch(c, [(560, 1010), (650, 1000), (650, 1240), (560, 1250)], a=0)
    # floors (tiles in the hall, wood in the bedroom) + their detail down to the bottom
    floor(c, FY, '#E5DED2', 'tiles', x0=-300, x1=WX, plank=120)
    floor(c, FY, FLOOR, 'wood', x0=WX, x1=W + 300)
    light_patch(c, [(700, FY + 12), (960, FY + 12), (900, 1790), (520, 1790)], a=55)
    rug(c, 850, 1640, 420, 120, CORAL)
    motes(c, 560, 600, 1000, 1700, n=14, seed=2, col='#FFFFFF', a=200)
    plant(c, 80, FY + 10, 0.95)
    sneakers(c, 250, 1640, 1.1)
    backpack(c, 110, 1820, 1.2, SKY)
    nightstand(c, 640, FY)
    bed(c, 730, FY)
    if charger:
        cx, cy = 905, FY - 152
        cab = skia.Path(); cab.moveTo(cx, cy); cab.cubicTo(cx + 40, cy + 30, cx + 70, cy - 10, cx + 110, cy + 10)
        c.drawPath(cab, P(NAVY, 255, 7))
        shaded_rrect(c, cx - 22, cy - 16, cx + 6, cy + 12, 6, '#FFFFFF', 4)
    # dividing wall (section) + door frame
    shaded_rrect(c, WX - 24, -60, WX + 24, DOOR_TOP, 6, '#E8D3B5', 6, 0.84)
    shaded_rrect(c, WX - 34, DOOR_TOP - 6, WX + 34, DOOR_TOP + 18, 6, WOOD, 5, 0.8)
    shaded_rrect(c, WX - 46, FY - 6, WX + 46, FY + 10, 5, WOOD, 4, 0.8)
    if flash > 0:
        g = skia.Paint(AntiAlias=True)
        g.setShader(skia.GradientShader.MakeLinear([skia.Point(WX - 140, 0), skia.Point(WX + 140, 0)],
                    [C(YEL, 0), C('#FFF6C8', int(230 * flash)), C(YEL, 0)], [0.0, 0.5, 1.0]))
        c.drawRect(R(WX - 140, DOOR_TOP + 18, WX + 140, FY), g)
        sparkles(c, WX - 120, DOOR_TOP + 40, WX + 120, FY - 40, n=6, seed=4, col='#FFFFFF', size=18 * flash)
    door_leaf(c, WX - 24, DOOR_TOP + 18, FY, door)


def mika_box(c, x, y, s, **kw):
    mika(c, x, y, s, **kw)
    shaded_rrect(c, x - 62 * s, y - 196 * s, x + 62 * s, y - 92 * s, 8 * s, '#E0A465', 5 * s, 0.84)
    c.drawLine(x - 62 * s, y - 168 * s, x + 62 * s, y - 168 * s, P(NAVY, 255, 4 * s))
    c.drawLine(x, y - 196 * s, x, y - 168 * s, P('#F6E7C6', 255, 6 * s))


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
            if u < 1:
                c.drawCircle(mx + 120 + d * math.cos(a), hy - 190 + d * math.sin(a), 18 * (1 - u), P(NAVY))
                c.drawCircle(mx + 120 + d * math.cos(a), hy - 190 + d * math.sin(a), 14 * (1 - u), P('#FFFFFF'))
    if t >= 1.05:
        sx, sy = squash((t - 1.05) / 0.3)
        c.save(); c.translate(hx + 10, hy - 150); c.rotate(8 * math.sin(t * 6)); c.scale(sx, sy); icon_q(c, 0, 0, 1.15); c.restore()
    c.restore()
    ost(c, "WHY AM I *HERE*?", t, 1.05)


def phone_prop(c, x, y, k, rot, t, fade=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    rrect(c, -78, -136, 92, 164, 26, blurred(NAVY, 70, 12))
    shaded_rrect(c, -85, -150, 85, 150, 26, NAVY, 6, 0.75)
    bg(c, '#FFFFFF', '#EAF4FB', -125, 125, -70, 70)
    rrect(c, -70, -125, 70, 125, 12, P(NAVY, 255, 3))
    rrect(c, -26, -142, 26, -132, 5, P('#3A4A70'))
    blink = 1 if int(t * 5) % 2 == 0 else 0.35
    shaded_rrect(c, -40, -70, 34, -20, 8, '#FFFFFF', 5, 0.9); rrect(c, 34, -55, 44, -35, 3, P(NAVY))
    rrect(c, -34, -64, -24, -26, 4, P(CORAL, 255 * blink))
    f = skia.Font(F_OST, 64); w = f.measureText("1 %"); c.drawString("1 %", -w / 2, 60, f, P(CORAL))
    gl = skia.Path(); gl.moveTo(10, -125); gl.lineTo(70, -125); gl.lineTo(70, -40); gl.close(); c.drawPath(gl, P('#FFFFFF', 60))
    c.restore()
    if fade < 1: pass


def tumbleweed(c, x, y, rot):
    c.save(); c.translate(x, y); c.rotate(rot)
    for r, a in ((60, 255), (44, 255), (26, 255)):
        c.drawCircle(0, 0, r, P(NAVY, a, 11)); c.drawCircle(0, 0, r, P('#C49A5B', a, 6))
    for q in range(4):
        c.save(); c.rotate(q * 45)
        c.drawLine(-60, 0, 60, 0, P(NAVY, 255, 10)); c.drawLine(-60, 0, 60, 0, P('#C49A5B', 255, 5)); c.restore()
    c.restore()


def bedroom_close(c):
    wall(c, -200, -200, W + 200, 1350, BED, 'dots')
    window(c, 640, 560, 940, 830, curtains=SKY)
    picture(c, 70, 560, 260, 720, kind=1)
    shelf(c, 30, 1190, 330, seed=3)
    floor(c, 1350, FLOOR, 'wood')
    light_patch(c, [(640, 1362), (940, 1362), (900, 1800), (480, 1800)], a=50)
    rug(c, 540, 1420, 620, 120, CORAL)
    motes(c, 600, 620, 1000, 1500, n=12, seed=6, a=190)
    sneakers(c, 860, 1700, 1.15, stripe=SKY)
    # crumpled paper balls
    for x, y in ((170, 1640), (300, 1790)):
        contact_shadow(c, x, y + 26, 80, 14); shaded_circle(c, x, y, 30, '#FFFFFF', 4, 0.86)
        c.drawLine(x - 14, y - 8, x + 10, y + 4, P(GREY, 255, 3)); c.drawLine(x - 4, y + 12, x + 16, y - 10, P(GREY, 255, 3))


def s2(c, t, D):
    z = 1.08 + 0.1 * (t / D)
    c.save(); cam(c, z, 540, 1000)
    bedroom_close(c)
    blank = t >= 1.55
    mika(c, 540, 1350, 1.05, look=(0, -0.1) if not blank else (0, 0), mood='neutral', sweat=blank)
    if blank and t >= 2.13:
        u = (t - 2.13) / (D - 2.13)
        tx = -120 + 1300 * u; hop = abs(math.sin(u * 9)); ty = 1330 - hop * 70
        contact_shadow(c, tx, 1392, 120 * (1 - 0.4 * hop), 20, a=60)
        if hop < 0.15: dust_puff(c, tx, 1392, (u * 9 / math.pi) % 1, 0.8)
        tumbleweed(c, tx, ty, u * 900)
    c.restore()
    fade = 1 - clamp((t - 1.55) / 0.35)
    # phone with 1 % battery
    if t >= 0.1 and fade > 0:
        sx, sy = pk(t, 0.1)
        c.saveLayer(None, P('#FFFFFF', 255 * fade))
        c.save(); c.translate(250, 760 - 60 * (1 - fade)); c.scale(sx * (0.7 + 0.3 * fade), sy * (0.7 + 0.3 * fade))
        phone_prop(c, 0, 0, 1.0, -8, t)
        c.restore(); c.restore()
    if t >= 0.81 and fade > 0:
        sx, sy = pk(t, 0.81)
        c.save(); c.translate(830, 1010 - 60 * (1 - fade)); c.scale(sx * 1.5, sy * 1.5)
        c.saveLayer(None, P('#FFFFFF', 255 * fade)); icon_homework(c, 0, 0, 1.0); c.restore()
        c.restore()
        if t < 1.1: sparkles(c, 700, 880, 960, 1140, n=5, seed=8, col=YEL, size=20)
    if blank:
        sx, sy = pk(t, 1.55, 0.25)
        secs = int(clamp((t - 2.13) / (D - 2.3)) * 7) if t >= 2.13 else 0
        c.save(); c.translate(250, 700); c.scale(sx, sy)
        stopwatch(c, 0, 0, 105, t - 1.55)
        c.restore()
        sticker(c, f"0:0{secs}", 250, 880, 54, '#FFFFFF', NAVY, sk=pk(t, 1.7), rot=-4)
        # "..." dots above Mika's head
        for q in range(3):
            if t >= 1.75 + q * 0.18:
                kk = eback((t - 1.75 - q * 0.18) / 0.2)
                c.drawCircle(500 + q * 40, 830 + 4 * math.sin(t * 6 + q), 11 * kk, P(NAVY))
    ost(c, "TOTAL *BLANK*" if blank else "YOU *HAD* A PLAN", t, 0.1 if not blank else 1.55)


def brain(c, x, y, s, col='#F7A8B8', stem=True):
    p = skia.Path()
    for dx, dy, r in ((-90, -30, 80), (-20, -70, 85), (70, -50, 82), (110, 30, 70), (30, 50, 80), (-70, 50, 75)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p.setFillType(skia.PathFillType.kWinding)
    if stem:
        c.drawLine(x + 0, y + 120 * s, x + 10 * s, y + 200 * s, P(NAVY, 255, 26 * s)); c.drawLine(x + 0, y + 120 * s, x + 10 * s, y + 200 * s, P('#E98FA3', 255, 16 * s))
    c.drawPath(p, P(NAVY, 255, 14 * s))
    shaded_path(c, p, col, 0, 0.88, light=(-1, -1), shift=0.08)
    for (ax, ay, bx, by, cx2, cy2) in ((-120, -20, -60, -80, -20, -20), (0, -110, 30, -40, 90, -80), (40, 10, 90, 60, 140, 20), (-110, 60, -50, 20, 0, 80)):
        q = skia.Path(); q.moveTo(x + ax * s, y + ay * s); q.quadTo(x + bx * s, y + by * s, x + cx2 * s, y + cy2 * s)
        c.drawPath(q, P('#D9768B', 255, 9 * s))
    c.drawOval(skia.Rect.MakeXYWH(x - 120 * s, y - 120 * s, 70 * s, 34 * s), P('#FFFFFF', 90))


def brain_face(c, x, y, s, mood='smile', look=(0, 0)):
    bl = blink_amt(7.0)
    for k in (-1, 1):
        ex, ey = x + k * 70 * s + look[0] * 8 * s, y - 20 * s + look[1] * 8 * s
        if bl > 0.45: c.drawLine(ex - 14 * s, ey, ex + 14 * s, ey, P(NAVY, 255, 7 * s))
        else:
            c.drawCircle(ex, ey, 16 * s, P(NAVY)); c.drawCircle(ex + 5 * s, ey - 5 * s, 5 * s, P('#FFFFFF'))
    for k in (-1, 1): c.drawOval(skia.Rect.MakeXYWH(x + k * 100 * s - 18 * s, y + 10 * s, 36 * s, 16 * s), P('#FF8FA3', 200))
    sm = skia.Path()
    if mood == 'smile': sm.moveTo(x - 40 * s, y + 30 * s); sm.quadTo(x, y + 62 * s, x + 40 * s, y + 30 * s)
    else: sm.moveTo(x - 30 * s, y + 50 * s); sm.quadTo(x, y + 34 * s, x + 30 * s, y + 50 * s)
    c.drawPath(sm, P(NAVY, 255, 8 * s))


def dumbbell(c, x, y, rot=0, col=SKY):
    contact_shadow(c, x, y + 40, 220, 26)
    c.save(); c.translate(x, y); c.rotate(rot)
    shaded_rrect(c, -80, -8, 80, 8, 4, GREY, 4, 0.8)
    for sg in (-1, 1):
        shaded_rrect(c, sg * 70 - 22, -46, sg * 70 + 22, 46, 12, col, 5, 0.82)
        shaded_rrect(c, sg * 104 - 12, -32, sg * 104 + 12, 32, 8, col, 5, 0.82)
    c.restore()


def bottle(c, x, y):
    contact_shadow(c, x, y, 120, 20)
    shaded_rrect(c, x - 22, y - 200, x + 22, y - 160, 8, NAVY, 4, 0.8)
    shaded_rrect(c, x - 44, y - 170, x + 44, y, 22, '#CDEFFB', 5, 0.86)
    c.drawRect(R(x - 42, y - 110, x + 42, y - 60), P(CORAL)); c.drawLine(x - 44, y - 110, x + 44, y - 110, P(NAVY, 255, 3)); c.drawLine(x - 44, y - 60, x + 44, y - 60, P(NAVY, 255, 3))


def check_mark(c, x, y, s, col='#FFFFFF'):
    p = skia.Path(); p.moveTo(x - 22 * s, y); p.lineTo(x - 6 * s, y + 16 * s); p.lineTo(x + 24 * s, y - 18 * s)
    c.drawPath(p, P(NAVY, 255, 16 * s)); c.drawPath(p, P(col, 255, 9 * s))


def s3(c, t, D):
    wt = 1.33
    if t < wt:
        radial_bg(c, '#FFF7EC', '#F9D9D2', cy=820)
        sunburst(c, 540, 860, '#FFFFFF', a=70, n=18, rot=t * 14)
        # studio floor + spotlight pool
        floor(c, 1330, '#F4D3CB', 'concrete', skirt=False)
        glow(c, 540, 1360, 380, '#FFF6D8', 200)
        z = 1.15 - 0.15 * eout(t / 0.4)
        c.save(); cam(c, z, 540, 900)
        bob = 10 * math.sin(t * 5)
        contact_shadow(c, 540, 1300, 360 * (1 - bob / 80), 40, a=70)
        brain(c, 540, 860 + bob, 1.6, stem=False)
        brain_face(c, 540, 900 + bob, 1.0)
        sparkles(c, 200, 520, 880, 1180, n=9, seed=3, col=YEL, size=22)
        c.restore()
        dumbbell(c, 210, 1700, -8); dumbbell(c, 330, 1800, 6, CORAL)
        bottle(c, 880, 1760)
        rug(c, 540, 1560, 520, 60, YEL)
        if t >= 0.51:
            sx, sy = pk(t, 0.51, 0.25)
            fill = clamp((t - 0.51) / 0.5)
            with card(c, 190, 1180, 890, 1300, 'screen', sk=(sx, sy)) as (ix0, iy0, ix1, iy1):
                rrect(c, ix0 + 10, iy0 + 12, ix1 - 10, iy1 - 12, 30, P('#E3E8EF'))
                w = (ix1 - ix0 - 20) * fill
                if w > 10:
                    g = skia.Paint(AntiAlias=True)
                    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, iy0), skia.Point(0, iy1)], [C('#9EDCA8'), C('#62B672')]))
                    rrect(c, ix0 + 10, iy0 + 12, ix0 + 10 + w, iy1 - 12, 30, g)
                    rrect(c, ix0 + 22, iy0 + 18, ix0 + max(24, w - 10), iy0 + 30, 6, P('#FFFFFF', 110))
                text(c, f"MEMORY {int(count(t, 0.51, 0.5, 0, 100))} %", 540, (iy0 + iy1) / 2, 44, NAVY)
        if t >= 0.95:
            sticker(c, "OK", 840, 660, 70, '#7FCB8A', '#FFFFFF', sk=pk(t, 0.95), rot=10, shape='circle')
            if t >= 1.0:
                kk = eback((t - 1.0) / 0.2)
                c.save(); c.translate(905, 600); c.scale(kk, kk); check_mark(c, 0, 0, 1.3, '#7FCB8A'); c.restore()
        ost(c, "NOT YOUR *BRAIN*", t, 0.1)
    else:
        u = t - wt
        sl = 1 - eout(u / 0.22)
        c.save(); c.translate(900 * sl, 0)
        bg(c, '#EEF2F8', '#DCE3EE', 0, 1340)
        for k in range(8):
            yy = 560 + k * 100
            c.drawLine(80, yy, 1000, yy, P(NAVY, 70 if k % 2 else 110, 4 if k % 2 else 6))
        for k, lab in enumerate(("7 FT", "6 FT", "5 FT", "4 FT")):
            text(c, lab, 110, 560 + k * 200 - 24, 32, '#8B95A8')
        # overhead lamp cone
        lp = skia.Path(); lp.moveTo(470, 380); lp.lineTo(610, 380); lp.lineTo(900, 1340); lp.lineTo(180, 1340); lp.close()
        g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 380), skia.Point(0, 1340)], [C('#FFF6C8', 120), C('#FFF6C8', 20)]))
        c.drawPath(lp, g)
        floor(c, 1340, '#C9D2DE', 'concrete', skirt=False)
        glow(c, 540, 1380, 420, '#FFF6C8', 120)
        # tape marks + evidence marker
        c.drawLine(140, 1420, 940, 1420, P(YEL, 255, 10)); c.drawLine(80, 1600, 1000, 1600, P(YEL, 200, 12))
        zz = 1.0 + 0.06 * eout((u - 0.7) / 0.3) if u > 0.7 else 1.0
        c.save(); cam(c, zz, 540, 1000)
        front_door(c, 540, 1340, 1.25, open_k=0.0, mat=False)
        c.restore()
        mk = skia.Path(); mk.moveTo(820, 1760); mk.lineTo(880, 1640); mk.lineTo(940, 1760); mk.close()
        contact_shadow(c, 880, 1764, 150, 22); shaded_path(c, mk, YEL, 6, 0.84)
        text(c, "1", 880, 1722, 50, NAVY)
        motes(c, 220, 420, 860, 1300, n=12, seed=9, a=170)
        c.restore()
        if u < 0.2:
            c.drawRect(R(0, 0, W, H), P('#FFFFFF', 200 * (1 - u / 0.2)))   # camera flash
        if u > 0.05:
            burst(c, 540, 1000, (u - 0.05) / 0.35, r=260, col=YEL, n=14)
        if t >= 2.07:
            sticker(c, "SUSPECT", 540, 1210, 72, CORAL, '#FFFFFF', sk=pk(t, 2.07), rot=-6)
            k = eback((t - 2.07) / 0.22)
            ax = 870 + 20 * math.sin(t * 12)
            p = skia.Path(); p.moveTo(ax, 900); p.lineTo(ax + 70, 850); p.lineTo(ax + 70, 880); p.lineTo(ax + 150, 880); p.lineTo(ax + 150, 920); p.lineTo(ax + 70, 920); p.lineTo(ax + 70, 950); p.close()
            c.save(); c.translate(ax, 900); c.scale(k, k); c.translate(-ax, -900)
            c.save(); c.translate(5, 10); c.drawPath(p, blurred(NAVY, 70, 6)); c.restore()
            shaded_path(c, p, CORAL, 6, 0.84); c.restore()
        ost(c, "BLAME THE *DOOR*", t, wt + 0.05)


# floor-plan path through 4x4 rooms (serpentine)
PLAN_X0, PLAN_Y0, CW, CH = 140, 470, 200, 205
PATH = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3), (2, 3), (1, 3), (0, 3)]
OBJ_COLS = [CORAL, SKY, YEL, '#7FB7A4', '#B98AE6']
ROOM_COLS = [HALL, BED, '#E5F5E8', '#FFF0D4']


def cell_c(i, j):
    return PLAN_X0 + CW * i + CW / 2, PLAN_Y0 + CH * j + CH / 2


def desk_props(c, mugx=930, mugy=1650):
    pencil(c, 40, 1830, 430, 1690)
    sticky_note(c, 180, 1580, "rooms?", YEL, 170, -7, 36)
    mug(c, mugx, mugy, 1.0, SKY)
    for x, y, r in ((560, 1830, 18), (640, 1800, -30)):  # paper clips
        c.save(); c.translate(x, y); c.rotate(r)
        rrect(c, -30, -10, 30, 10, 10, P(GREY, 255, 5)); rrect(c, -20, -5, 22, 5, 5, P(GREY, 255, 4)); c.restore()


def mini_walker(c, wx, wy, ang=0.0):
    """top-down Mika carrying a box"""
    c.drawCircle(wx + 6, wy + 10, 46, blurred(NAVY, 70, 8))
    c.save(); c.translate(wx, wy); c.rotate(ang)
    c.drawOval(R(-48, -30, 48, 30), P(MUSTARD)); c.drawOval(R(-48, -30, 48, 30), P(NAVY, 255, 6))
    c.drawCircle(0, 0, 25, P('#2A2233')); c.drawCircle(-6, -7, 7, P('#FFFFFF', 60))
    shaded_rrect(c, 26, -20, 62, 16, 5, '#E0A465', 4)
    c.restore()


def s4(c, t, D):
    z = 1.25 - 0.25 * eout(t / 0.5)
    c.save(); cam(c, z, 540, 880)
    desk_top(c)
    desk_props(c)
    with card(c, 110, 440, 970, 1320, 'paper', rot=-1.2):
        for n, (i, j) in enumerate(PATH):
            if t < n * 0.03: continue
            x0, y0 = PLAN_X0 + CW * i, PLAN_Y0 + CH * j
            col = ROOM_COLS[(i + 2 * j) % 4]
            c.drawRect(R(x0, y0, x0 + CW, y0 + CH), P(col))
            for q in range(1, 5): c.drawLine(x0, y0 + q * CH / 5, x0 + CW, y0 + q * CH / 5, P(tint(col, 0.9), 120, 2))
        gaps = set()
        for a, b in zip(PATH, PATH[1:]): gaps.add(tuple(sorted((a, b))))
        segs = []
        for i in range(4):
            for j in range(4):
                x0, y0 = PLAN_X0 + CW * i, PLAN_Y0 + CH * j
                if i < 3:
                    xx = x0 + CW
                    if ((i, j), (i + 1, j)) in gaps: segs += [(xx, y0, xx, y0 + CH * 0.3), (xx, y0 + CH * 0.7, xx, y0 + CH)]
                    else: segs.append((xx, y0, xx, y0 + CH))
                if j < 3:
                    yy = y0 + CH
                    if ((i, j), (i, j + 1)) in gaps: segs += [(x0, yy, x0 + CW * 0.3, yy), (x0 + CW * 0.7, yy, x0 + CW, yy)]
                    else: segs.append((x0, yy, x0 + CW, yy))
        sh = blurred(NAVY, 60, 4)
        sh.setStyle(skia.Paint.kStroke_Style); sh.setStrokeWidth(12)
        for s_ in segs: c.drawLine(s_[0] + 4, s_[1] + 6, s_[2] + 4, s_[3] + 6, sh)
        for s_ in segs: c.drawLine(*s_, P(NAVY, 255, 12))
        c.drawRect(R(PLAN_X0, PLAN_Y0, PLAN_X0 + 4 * CW, PLAN_Y0 + 4 * CH), P(NAVY, 255, 14))
        hl = t >= 1.2
        for n, (i, j) in enumerate(PATH):
            x, y = cell_c(i, j)
            tx, ty = x + 48, y - 48
            shaded_rrect(c, tx - 34, ty - 26, tx + 34, ty + 26, 8, WOOD, 4, 0.8)
            k = 1.0
            if hl: k = 1 + 0.5 * math.sin(clamp((t - 1.2 - n * 0.03) / 0.25) * math.pi)
            shaded_circle(c, tx, ty - 4, 13 * k, OBJ_COLS[n % 5], 3, 0.8)
        prog = clamp((t - 0.15) / (D - 0.35)) * (len(PATH) - 1)
        k0 = int(prog); f = prog - k0
        a = cell_c(*PATH[min(k0, len(PATH) - 1)]); b = cell_c(*PATH[min(k0 + 1, len(PATH) - 1)])
        wx, wy = a[0] + (b[0] - a[0]) * einout(f), a[1] + (b[1] - a[1]) * einout(f)
        pp = P(CORAL, 255, 8); pp.setPathEffect(skia.DashPathEffect.Make([16, 14], -t * 40))
        tr = skia.Path(); tr.moveTo(*cell_c(*PATH[0]))
        for n in range(1, k0 + 1): tr.lineTo(*cell_c(*PATH[n]))
        tr.lineTo(wx, wy); c.drawPath(tr, pp)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) if a != b else 0
        mini_walker(c, wx, wy, ang)
    c.restore()
    if t >= 1.89:
        n = int(count(t, 1.95, 0.6, 0, 55))
        sticker(c, f"{n} ROOMS", 760, 1300, 74, CORAL, '#FFFFFF', sk=pk(t, 1.89), rot=-5, shape='burst')
    ost(c, "THE *EXPERIMENT*", t, 0.1)


def lane_room_a(c, t, y0, y1, fl):
    wall(c, 60, y0, 540, fl, HALL, 'panel'); wall(c, 540, y0, 1020, fl, BED, 'dots')
    picture(c, 180, y0 + 90, 300, y0 + 190, kind=0)
    window(c, 760, y0 + 90, 900, y0 + 210, curtains=None, sill=False)
    floor(c, fl, FLOOR, 'wood', x0=60, x1=1020, y1=y1, skirt=True)
    shaded_rrect(c, 524, y0 - 10, 556, 640, 4, '#E8D3B5', 5, 0.84)
    pass_k = clamp(1 - abs(t - 1.0) / 0.25)
    if pass_k > 0: c.drawRect(R(450, 650, 630, fl), P('#FFF6C8', 220 * pass_k))
    door_leaf(c, 524, 652, fl, 0.6)
    u = clamp((t - 0.1) / 1.7)
    mika_box(c, 160 + 760 * u, fl, 0.55, walk=t * 13 if 0.1 < t < 1.8 else 0, look=(0.6, 0))


def lane_room_b(c, t, y0, y1, fl):
    wall(c, 60, y0, 1020, fl, BED, 'dots')
    window(c, 640, 1040, 860, 1200, curtains=None, sill=True)
    picture(c, 250, 1040, 360, 1140, kind=2)
    floor(c, fl, FLOOR, 'wood', x0=60, x1=1020, y1=y1, skirt=True)
    plant(c, 960, fl, 0.5)
    u = clamp((t - 1.8) / 1.7)
    mika_box(c, 160 + 760 * u, fl, 0.55, walk=t * 13 if 1.8 < t < 3.5 else 0, look=(0.6, 0))


def tape_measure(c, y, k):
    if k <= 0: return
    x0, x1 = 160, 160 + 760 * k
    rrect(c, x0 + 4, y - 14 + 8, x1 + 4, y + 14 + 8, 4, blurred(NAVY, 70, 5))
    shaded_rrect(c, x0, y - 15, x1, y + 15, 4, YEL, 4, 0.85, side='b')
    for q in range(0, int(x1 - x0), 19):
        c.drawLine(x0 + q, y - 15, x0 + q, y - (2 if q % 95 else -6), P(NAVY, 255, 3))
    shaded_rrect(c, x1 - 4, y - 24, x1 + 10, y + 24, 3, GREY, 4)
    shaded_rrect(c, x0 - 70, y - 40, x0 + 6, y + 40, 18, CORAL, 5)
    c.drawCircle(x0 - 32, y, 14, P(NAVY))


def s5(c, t, D):
    desk_top(c)
    desk_props(c, 940, 1690)
    with card(c, 40, 420, 1040, 920, 'paper', rot=-0.8) as _:
        lane_room_a(c, t, 440, 900, 852)
    sticker(c, "A · DOORWAY", 230, 470, 42, CORAL, '#FFFFFF', rot=-3)
    if t >= 1.75:
        k = eout((t - 1.75) / 0.3)
        c.save(); c.translate(0, 600 * (1 - k)); c.rotate(0.0)
        with card(c, 40, 920, 1040, 1380, 'paper', rot=0.8) as _:
            lane_room_b(c, t, 940, 1360, 1312)
        sticker(c, "B · ONE ROOM", 240, 950, 42, SKY, NAVY, rot=3)
        c.restore()
    rk = eout((t - 3.4) / 0.35) if t >= 3.4 else 0
    tape_measure(c, 878, rk); tape_measure(c, 1338, rk)
    if t >= 3.75:
        sticker(c, "=", 540, 915, 80, YEL, NAVY, sk=pk(t, 3.75), shape='circle')
    ost(c, "SAME *DISTANCE*", t, 0.1)


def audience(c, t, y=1800):
    """out-of-focus foreground audience heads (parallax layer)"""
    with defocus(c, 9, (0, y - 260, W, H)):
        for k in range(7):
            x = -40 + k * 190 + 12 * osc(0.3, k); yy = y + 40 * (k % 2) + 6 * osc(0.5, k * 2)
            c.drawCircle(x, yy - 120, 72, P(tint(HOODS[k % 5], 0.7)))
            rrect(c, x - 120, yy - 60, x + 120, yy + 300, 90, P(tint(HOODS[(k + 2) % 5], 0.7)))


def s6(c, t, D):
    radial_bg(c, '#D6F0FC', '#86CBEF', cy=760)
    sunburst(c, 540, 780, '#FFFFFF', a=55, n=18, rot=t * 10)
    floor(c, 1360, '#F3D7A8', 'wood', skirt=False)
    glow(c, 540, 1380, 330, '#FFF6D8', 210)
    for side in (-1, 1):  # sweeping spotlights
        a = math.radians(90 + side * (24 + 10 * math.sin(t * 1.6 + side)))
        x0 = 540 - side * 620; ex = x0 + 1500 * math.cos(a) * -side * -1
        bp_ = skia.Path(); bp_.moveTo(x0, -40); bp_.lineTo(x0 + 40, -40)
        tx = 540 + side * 140 * math.sin(t * 1.3 + side)
        bp_.lineTo(tx + 160, 1400); bp_.lineTo(tx - 160, 1400); bp_.close()
        g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1400)], [C('#FFFFFF', 90), C('#FFFFFF', 10)]))
        c.drawPath(bp_, g)
    sh = 0
    if 1.52 <= t < 1.75: sh = 10 * math.sin(t * 80) * (1 - (t - 1.52) / 0.23)
    flip = eout(t / 0.25)
    with card(c, 140, 500, 940, 1080, 'screen', sk=(max(0.02, flip), 1.0), title="QUIZ TIME!", title_bg=CORAL):
        text(c, "What are you holding?", 540, 662, 50, NAVY, F_CAP)
        for n, (ox, lab) in enumerate(((340, "A"), (740, "B"))):
            tt = 1.1 + n * 0.18
            if t < tt: continue
            sx, sy = pk(t, tt, 0.25)
            c.save(); c.translate(ox, 860); c.scale(sx, sy)
            shaded_rrect(c, -150, -110, 150, 120, 26, '#FFF4E0', 6, 0.9, shadow=True)
            if n == 0:
                shaded_rrect(c, -50, -40, 50, 70, 14, SKY, 6)
                c.drawArc(R(30, -10, 90, 50), -90, 180, False, P(NAVY, 255, 14)); c.drawArc(R(30, -10, 90, 50), -90, 180, False, P(SKY, 255, 6))
                steam(c, 0, -50, 0.8, col=GREY, a=200)
            else:
                st = skia.Path()
                for q in range(10):
                    rr = 70 if q % 2 == 0 else 30; a = math.radians(q * 36 - 90)
                    (st.moveTo if q == 0 else st.lineTo)(rr * math.cos(a), 15 + rr * math.sin(a))
                st.close(); shaded_path(c, st, YEL, 6, 0.85)
            sticker(c, lab, -112, -86, 38, NAVY, '#FFFFFF', shape='circle')
            c.restore()
        if t >= 0.51:
            u = clamp((t - 0.51) / (D - 0.6))
            rrect(c, 200, 1015, 880, 1052, 18, P('#E6E9F0'))
            if u < 1: rrect(c, 200, 1015, 200 + 680 * (1 - u), 1052, 18, P(CORAL if u > 0.6 else YEL))
            rrect(c, 200, 1015, 880, 1052, 18, P(NAVY, 255, 5))
    c.save(); c.translate(sh, 0)
    x, y = 540, 1370
    mika(c, x, y, 0.72, look=(0, -0.4), mood='worried' if t > 1.52 else 'neutral', sweat=t > 1.52)
    shaded_rrect(c, x - 80, y - 168, x + 80, y - 52, 10, '#E0A465', 5, 0.84)
    c.drawLine(x - 80, y - 138, x + 80, y - 138, P(NAVY, 255, 4))
    if t >= 1.52:
        sx, sy = pk(t, 1.52, 0.25)
        c.save(); c.translate(x, y - 96); c.scale(sx, sy); icon_q(c, 0, 0, 0.55, NAVY); c.restore()
    c.restore()
    if t >= 0.51:
        per = (D - 0.6) / 3
        n = 3 - min(2, int((t - 0.51) / per))
        tt = 0.51 + (3 - n) * per
        sticker(c, str(n), 900, 1150, 84, CORAL, '#FFFFFF', sk=pk(t, tt, 0.22), shape='circle')
    audience(c, t)
    ost(c, "QUICK *QUIZ*", t, 0.1)


def mini_person(c, x, y, s, bad, seed=0):
    col = CORAL if bad else GREY
    contact_shadow(c, x, y + 72 * s, 90 * s, 14 * s, a=60)
    br = (osc(0.3, seed) + 1) * 1.5
    shaded_rrect(c, x - 34 * s, y - 10 * s - br, x + 34 * s, y + 70 * s, 26 * s, col, 5 * s)
    hx, hy = x, y - 40 * s - br * 1.2
    shaded_circle(c, hx, hy, 30 * s, '#F5C6A5', 5 * s, 0.88, hi=False)
    if bad:
        for dx in (-10, 10):
            c.drawLine(hx + (dx - 5) * s, hy - 6 * s, hx + (dx + 5) * s, hy + 4 * s, P(NAVY, 255, 3.5 * s))
            c.drawLine(hx + (dx + 5) * s, hy - 6 * s, hx + (dx - 5) * s, hy + 4 * s, P(NAVY, 255, 3.5 * s))
    else:
        if blink_amt(seed) > 0.45:
            for dx in (-10, 10): c.drawLine(hx + (dx - 5) * s, hy, hx + (dx + 5) * s, hy, P(NAVY, 255, 3 * s))
        else:
            for dx in (-10, 10): c.drawCircle(hx + dx * s, hy, 4 * s, P(NAVY))


def people_row(c, y, nbad, t_bad, t, t0, seed=0):
    for k in range(10):
        tt = t0 + k * 0.04
        if t < tt: continue
        sx, sy = squash((t - tt) / 0.22)
        x = 135 + k * 90
        bad = k < nbad and t >= t_bad + k * 0.18
        if bad:
            gb = clamp((t - t_bad - k * 0.18) / 0.2)
            sx, sy = sx * (1 + 0.15 * gb), sy * (1 + 0.15 * gb)
        c.save(); c.translate(x, y); c.scale(sx, sy)
        mini_person(c, 0, 0, 1.0, bad, seed + k)
        c.restore()


def mini_door(c, x, y, s=1.0):
    shaded_rrect(c, x - 26 * s, y - 44 * s, x + 26 * s, y + 44 * s, 4 * s, '#E9A15B', 4 * s, 0.84)
    c.drawCircle(x + 14 * s, y, 4 * s, P(NAVY))


def s7(c, t, D):
    wall(c, -50, -50, W + 50, 1330, '#EAF2F8', 'panel')
    floor(c, 1330, '#E3D3BC', 'tiles')
    for x in (180, 900):   # whiteboard stand
        c.drawLine(x, 1290, x - 40, 1420, P(NAVY, 255, 16)); c.drawLine(x, 1290, x - 40, 1420, P(GREY, 255, 8))
        contact_shadow(c, x - 40, 1424, 90, 14)
    plant(c, 90, 1880, 1.3)
    # waste bin with paper
    contact_shadow(c, 960, 1860, 190, 26)
    bn = skia.Path(); bn.moveTo(870, 1660); bn.lineTo(1050, 1660); bn.lineTo(1030, 1860); bn.lineTo(890, 1860); bn.close()
    for x, y in ((925, 1650), (985, 1640)): shaded_circle(c, x, y, 34, '#FFFFFF', 4, 0.86)
    shaded_path(c, bn, SKY, 6, 0.84)
    for q in range(4): c.drawLine(900 + q * 40, 1680, 905 + q * 38, 1840, P(tint(SKY, 0.8), 255, 4))
    with card(c, 60, 400, 1020, 1300, 'whiteboard'):
        # row A
        c.drawRect(R(90, 590, 990, 760), P('#F3F6FA'))
        text(c, "ONE ROOM", 100, 500, 52, NAVY, align='l')
        people_row(c, 660, 1, 0.95, t, 0.1, seed=0)
        if t >= 0.95:
            sticker(c, f"~{int(count(t, 0.95, 0.45, 0, 10))} %", 845, 505, 62, CORAL, '#FFFFFF', sk=pk(t, 0.95), rot=-3)
        if t >= 2.43:
            k = eout((t - 2.43) / 0.2)
            pd = P(NAVY, 120, 5); pd.setPathEffect(skia.DashPathEffect.Make([20, 14], 0))
            c.drawLine(100, 810, 100 + 880 * k, 810, pd)
            c.save(); c.translate(-300 * (1 - k), 0)
            mini_door(c, 120, 880, 0.9)
            text(c, "AFTER A DOOR", 165, 880, 52, NAVY, align='l')
            c.restore()
            c.drawRect(R(90, 950, 990, 1110), P('#FDF1E6', 255 * k))
            people_row(c, 1020, 2, 3.44, t, 2.45, seed=20)
            if t >= 3.5:
                sticker(c, f"~{int(count(t, 3.5, 0.45, 0, 20))} %", 865, 880, 62, CORAL, '#FFFFFF', sk=pk(t, 3.5), rot=3)
        if t >= 3.95:
            burst(c, 540, 1192, (t - 3.95) / 0.4, r=140, col=YEL, n=14)
            sticker(c, "2× MISTAKES", 540, 1192, 60, YEL, NAVY, sk=pk(t, 3.95, 0.3), rot=-4)
    ost(c, "WHO *FORGOT*?", t, 0.1)


SCENE_ICONS = [HALL, BED, '#E5F5E8', '#FDEBD3', HALL, BED, '#E5F5E8', '#FDEBD3']


def frame_pic(c, x0, y0, x1, y1, kind):
    bg(c, SCENE_ICONS[kind % 4], tint(SCENE_ICONS[kind % 4], 0.94), y0, y1, x0, x1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = kind % 4
    c.drawRect(R(x0, y1 - 30, x1, y1), P(FLOOR))
    if k == 0:   # hallway door
        shaded_rrect(c, cx - 30, cy - 60, cx + 30, y1 - 30, 4, '#E9A15B', 4)
    elif k == 1:  # bed
        shaded_rrect(c, cx - 70, cy + 10, cx + 70, cy + 50, 8, SKY, 4)
    elif k == 2:  # kitchen fridge
        shaded_rrect(c, cx - 32, cy - 64, cx + 32, y1 - 30, 8, '#FFFFFF', 4)
        c.drawLine(cx - 32, cy - 10, cx + 32, cy - 10, P(NAVY, 255, 4))
    else:        # classroom board
        shaded_rrect(c, cx - 70, cy - 50, cx + 70, cy + 30, 6, '#2E5A55', 4)
    mx = cx + (40 if k != 1 else -20)
    c.drawCircle(mx, y1 - 52, 18, P(MUSTARD)); c.drawCircle(mx, y1 - 52, 18, P(NAVY, 255, 3))
    c.drawCircle(mx, y1 - 74, 13, P('#F5C6A5')); c.drawCircle(mx, y1 - 74, 13, P(NAVY, 255, 3))


def strip(c, x, y, n, fw=240, fh=200, start_kind=0):
    """film strip starting at x, n frames"""
    w = n * fw
    c.drawRect(R(x + 6, y - fh / 2 - 34 + 16, x + w + 6, y + fh / 2 + 34 + 16), blurred(NAVY, 70, 10))
    c.drawRect(R(x, y - fh / 2 - 34, x + w, y + fh / 2 + 34), P(NAVY))
    c.drawRect(R(x, y - fh / 2 - 34, x + w, y - fh / 2 - 26), P('#3A4A70'))
    for k in range(n):
        fx = x + k * fw
        frame_pic(c, fx + 14, y - fh / 2, fx + fw - 14, y + fh / 2, start_kind + k)
        for hx in range(4):
            rrect(c, fx + 18 + hx * 58, y - fh / 2 - 26, fx + 50 + hx * 58, y - fh / 2 - 10, 4, P(CREAM))
            rrect(c, fx + 18 + hx * 58, y + fh / 2 + 10, fx + 50 + hx * 58, y + fh / 2 + 26, 4, P(CREAM))


def film_reel(c, x, y, r, rot, col=GREY):
    c.drawCircle(x + 8, y + 14, r, blurred(NAVY, 70, 10))
    shaded_circle(c, x, y, r, col, 7, 0.84)
    c.drawCircle(x, y, r * 0.78, P(NAVY, 255 * 0.85))
    c.drawCircle(x, y, r * 0.78, P('#3A4A70', 255, 6))
    for q in range(5):
        a = math.radians(rot + q * 72)
        c.drawCircle(x + r * 0.45 * math.cos(a), y + r * 0.45 * math.sin(a), r * 0.17, P(col))
        c.drawCircle(x + r * 0.45 * math.cos(a), y + r * 0.45 * math.sin(a), r * 0.17, P(NAVY, 255, 4))
    shaded_circle(c, x, y, r * 0.14, CORAL, 4, 0.8)


def s8(c, t, D):
    bg(c, '#F6F0FC', '#E4D9F3', 0, 1380)
    # projector beam + dust
    bm = skia.Path(); bm.moveTo(-60, 120); bm.lineTo(60, 60); bm.lineTo(1140, 560); bm.lineTo(1140, 980); bm.close()
    g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 100), skia.Point(1100, 700)], [C('#FFF6C8', 150), C('#FFF6C8', 20)]))
    c.drawPath(bm, g)
    motes(c, 60, 200, 1040, 960, n=18, seed=12, a=210)
    floor(c, 1380, '#D9CCE8', 'wood', skirt=True)
    film_reel(c, 140, 1650, 120, t * 120, GREY)
    film_reel(c, 960, 1760, 90, -t * 160, CORAL)
    lf = skia.Path(); lf.moveTo(250, 1690); lf.cubicTo(420, 1820, 600, 1600, 880, 1760)
    c.drawPath(lf, P(NAVY, 255, 34)); c.drawPath(lf, P('#3A4A70', 255, 26))
    cut = 2.82
    # brain recorder on a pedestal
    contact_shadow(c, 540, 1384, 300, 34)
    shaded_rrect(c, 430, 1280, 650, 1384, 14, '#FFFFFF', 6, 0.86)
    bk = eback((t - 0.1) / 0.25)
    c.save(); c.translate(540, 1150); c.scale(bk * 0.75, bk * 0.75); c.translate(-540, -1150)
    brain(c, 540, 1110, 1.0)
    brain_face(c, 540, 1130, 0.7, look=(0, -0.6))
    c.restore()
    if t >= 0.1:
        on = int(t * 3) % 2 == 0
        sticker(c, "   REC", 790, 1020, 40, '#FFFFFF', NAVY, sk=pk(t, 0.2))
        if t >= 0.35: c.drawCircle(744, 1020, 14, P(CORAL if on else '#F3B7B0'))
    if t < cut:
        if t >= 0.65:
            k = eout((t - 0.65) / 0.3)
            off = -((t - 0.65) * 320) % 240
            c.save(); c.translate(1100 * (1 - k), 0)
            strip(c, -240 + off, 700, 7)
            c.restore()
        if t >= 1.8:
            sticker(c, "1 LONG VIDEO?", 540, 905, 52, SKY, NAVY, sk=pk(t, 1.8), rot=-3)
    else:
        u = t - cut
        sep = eout(u / 0.35)
        for k in range(3):
            fx = 60 + k * 330
            c.save()
            dx = (k - 1) * 30 * sep; rot = (k - 1) * 6 * sep; dy = -20 * sep * (1 if k != 1 else -0.5)
            c.translate(fx + 150 + dx, 700 + dy); c.rotate(rot); c.translate(-(fx + 150), -700)
            c.drawRect(R(fx + 6, 700 - 134 + 16, fx + 306, 700 + 150), blurred(NAVY, 70, 10))
            c.drawRect(R(fx, 700 - 134, fx + 300, 700 + 134), P(NAVY))
            frame_pic(c, fx + 14, 600, fx + 286, 800, k)
            for hx in range(5):
                rrect(c, fx + 14 + hx * 58, 700 - 126, fx + 46 + hx * 58, 700 - 110, 4, P(CREAM))
                rrect(c, fx + 14 + hx * 58, 700 + 110, fx + 46 + hx * 58, 700 + 126, 4, P(CREAM))
            if t >= 3.42 + k * 0.15:
                sticker(c, f"SCENE {k + 1}", fx + 150, 885, 40, YEL, NAVY, sk=pk(t, 3.42 + k * 0.15), rot=(k - 1) * 4)
            c.restore()
        if u < 0.45:
            sx = 390 + 330 * clamp(u / 0.3)
            a = 25 * (1 - abs(math.sin(u * 20)))
            for sg in (-1, 1):
                c.save(); c.translate(sx, 700); c.rotate(sg * a)
                shaded_rrect(c, -10, -9, 150, 9, 8, '#DDE3EC', 4, 0.8)
                c.drawCircle(-50, sg * 26, 30, P(NAVY, 255, 20)); c.drawCircle(-50, sg * 26, 30, P(CORAL, 255, 12))
                c.restore()
            c.drawCircle(sx, 700, 7, P(NAVY))
        for xx in (390, 720):
            burst(c, xx, 700, (u - 0.05) / 0.3, r=80, col=YEL, n=8)
    ost(c, "LIFE IN *SCENES*" if t >= cut else "YOUR *BRAIN*", t, cut if t >= cut else 0.1)


def clapper(c, x, y, s, open_a, label):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -144, 16, 156, 186, 12, blurred(NAVY, 80, 10))
    shaded_rrect(c, -150, 0, 150, 170, 12, NAVY, 6, 0.75)
    for q in range(3): c.drawLine(-120, 40 + q * 0, 120, 40, P('#FFFFFF', 40, 3))
    f = skia.Font(F_OST, 52); w = f.measureText(label); c.drawString(label, -w / 2, 120, f, P('#FFFFFF'))
    c.save(); c.translate(-150, 0); c.rotate(-open_a)
    rrect(c, 0, -46, 300, 0, 6, P('#FFFFFF')); rrect(c, 0, -46, 300, 0, 6, P(NAVY, 255, 5))
    for k in range(5):
        p = skia.Path(); x0 = 10 + k * 60; p.moveTo(x0, -46); p.lineTo(x0 + 30, -46); p.lineTo(x0 + 10, 0); p.lineTo(x0 - 20, 0); p.close()
        c.drawPath(p, P(NAVY))
    c.restore()
    c.drawCircle(-150, 0, 10, P(GREY)); c.drawCircle(-150, 0, 10, P(NAVY, 255, 4))
    c.restore()


def s9(c, t, D):
    z = 1.0 + 0.05 * (t / D)
    c.save(); cam(c, z, 540, 1000)
    mx = 200 + 600 * clamp(t / 1.3)
    two_rooms(c, door=0.85, flash=clamp(1 - abs(t - 0.55) / 0.2))
    mika(c, mx, FY, 0.95, walk=t * 13 if t < 1.3 else 0, look=(0.5, 0))
    if t >= 1.42:
        sticker(c, "CHAPTER 1", 270, 520, 48, '#FFFFFF', NAVY, sk=pk(t, 1.42), rot=-3)
    if t >= 1.98:
        sticker(c, "CHAPTER 2", 810, 520, 48, YEL, NAVY, sk=pk(t, 1.98), rot=3)
    c.restore()
    if t >= 0.15:
        drop = 1 - eout((t - 0.15) / 0.25)
        a = 28 if t < 0.55 else 28 * (1 - clamp((t - 0.55) / 0.06))
        clapper(c, 540, 690 - 500 * drop, 0.9, a, "CUT!")
    if 0.55 <= t < 0.8:
        u = (t - 0.55) / 0.25
        hh = 160 * math.sin(u * math.pi)
        c.drawRect(R(0, 0, W, hh), P(NAVY)); c.drawRect(R(0, H - hh, W, H), P(NAVY))
        c.drawRect(R(0, 0, W, H), P('#FFFFFF', 120 * (1 - u)))
    ost(c, "DOOR = *CUT*", t, 0.6)


def cabinet(c, x, y, drawer_out, xray=0.0):
    """(x,y) = bottom centre of a 3-drawer file cabinet"""
    w, h = 320, 600
    contact_shadow(c, x, y + 4, 420, 40, a=80)
    shaded_rrect(c, x - w / 2, y - h, x + w / 2, y, 14, '#9FB2C8', 8, 0.82)
    for k in range(1, 3):
        y0 = y - h + 20 + k * 193
        shaded_rrect(c, x - w / 2 + 18, y0, x + w / 2 - 18, y0 + 175, 10, '#B9C9DB', 6, 0.86)
        shaded_rrect(c, x - 50, y0 + 70, x + 50, y0 + 98, 12, NAVY, 0, 0.7)
        rrect(c, x - 44, y0 + 28, x + 44, y0 + 56, 4, P('#FFFFFF')); rrect(c, x - 44, y0 + 28, x + 44, y0 + 56, 4, P(NAVY, 255, 3))
    y0 = y - h + 20; d = 120 * drawer_out
    if d > 4:   # dark drawer cavity
        rrect(c, x - w / 2 + 22, y0 - d * 0.5, x + w / 2 - 22, y0 + 30, 8, P('#2B3A60'))
        for q in range(4): rrect(c, x - 110 + q * 50, y0 - d * 0.5 - 20, x - 70 + q * 50, y0 + 10, 4, P([YEL, CREAM, SKY, CREAM][q]))
    shaded_rrect(c, x - w / 2 + 18 - d * 0.25, y0 - d * 0.5 + d * 0.6, x + w / 2 - 18 + d * 0.25, y0 + 175 + d * 0.15, 10, '#C9D7E6', 6, 0.86)
    yy = y0 + d * 0.6 - d * 0.5
    shaded_rrect(c, x - 50, yy + 80, x + 50, yy + 108, 12, NAVY, 0, 0.7)
    rrect(c, x - 70, yy + 26, x + 70, yy + 62, 6, P('#FFFFFF')); rrect(c, x - 70, yy + 26, x + 70, yy + 62, 6, P(NAVY, 255, 3))
    text(c, "OLD SCENES", x, yy + 44, 22, NAVY)
    if xray > 0:
        c.saveLayer(None, P('#FFFFFF', 255 * xray))
        rrect(c, x - w / 2 + 30, y0 + 12, x + w / 2 - 30, y0 + 165, 8, P('#1E2A47', 220))
        glow(c, x - 25, y0 + 100, 140, SKY, 120)
        shaded_rrect(c, x - 110, y0 + 40, x + 60, y0 + 160, 8, YEL, 4)
        icon_charger(c, x - 25, y0 + 100, 0.7)
        c.restore()


def s10(c, t, D):
    wall(c, -50, -50, W + 50, 1340, '#EAF4EC', 'panel')
    shelf(c, 640, 770, 1040, seed=5, deco=True)
    wall_clock(c, 160, 560, 64)
    pendant_lamp(c, 820, -40, 480, 1.0, CORAL)
    floor(c, 1340, '#DCD3C3', 'tiles')
    for x, y, s_ in ((150, 1740, 1.0), (300, 1820, 0.8)):   # archive boxes
        contact_shadow(c, x, y + 4, 230 * s_, 30 * s_)
        shaded_rrect(c, x - 100 * s_, y - 140 * s_, x + 100 * s_, y, 8, '#D9A86C', 6, 0.82)
        rrect(c, x - 40 * s_, y - 100 * s_, x + 40 * s_, y - 66 * s_, 4, P('#FFFFFF')); rrect(c, x - 40 * s_, y - 100 * s_, x + 40 * s_, y - 66 * s_, 4, P(NAVY, 255, 3))
    plant(c, 960, 1880, 1.25, seed=4)
    sh = 0
    if 1.65 <= t < 1.9: sh = 12 * math.sin(t * 90) * (1 - (t - 1.65) / 0.25)
    c.save(); c.translate(sh, 0)
    cx, cy = 420, 1340
    drawer = clamp((t - 0.2) / 0.3) if t < 1.55 else 1 - clamp((t - 1.55) / 0.1)
    xr = clamp((t - 1.96) / 0.25)
    cabinet(c, cx, cy, eout(drawer), xr)
    if 0.1 <= t < 1.6:
        u = clamp((t - 0.6) / 0.85)
        fx = 820 - 400 * einout(u); fy = 600 + 140 * einout(u) - 160 * math.sin(u * math.pi)
        sc = 1.0 - 0.5 * u
        k = eback((t - 0.1) / 0.2)
        if 0.05 < u < 0.95:
            for q in range(4):
                c.drawLine(fx + 120 + q * 10, fy - 40 + q * 26, fx + 220 + q * 30, fy - 60 + q * 26, P(NAVY, 120, 5))
        c.save(); c.translate(fx, fy); c.rotate(-12 + 20 * u); c.scale(k * sc, k * sc)
        rrect(c, -142, -88, 158, 128, 12, blurred(NAVY, 70, 10))
        shaded_rrect(c, -150, -110, -40, -80, 8, YEL, 0, 0.88)
        shaded_rrect(c, -150, -100, 150, 110, 12, YEL, 6, 0.88)
        text(c, "SCENE 1", 0, -60, 40, NAVY)
        icon_charger(c, 0, 30, 0.8)
        c.restore()
    if t >= 1.65:
        burst(c, cx, cy - 500, (t - 1.65) / 0.3, r=160, col='#FFFFFF', n=10)
        dust_puff(c, cx, cy - 600, (t - 1.65) / 0.5, 1.2)
    c.restore()
    mika(c, 860, 1340, 0.75, look=(-0.7, -0.2), mood='o' if t > 1.96 else 'neutral', sweat=t > 1.96)
    if t >= 1.96:
        sx, sy = pk(t, 1.96, 0.25)
        c.save(); c.translate(880, 990); c.scale(sx, sy); icon_q(c, 0, 0, 0.8); c.restore()
    if t >= 2.73:
        sticker(c, "ARCHIVED", 420, 640, 70, CORAL, '#FFFFFF', sk=pk(t, 2.73, 0.25), rot=-8)
    ost(c, "FILED *AWAY*", t, 0.1)


def hall_door(c, dx):
    contact_shadow(c, dx, 1334, 300, 24, a=50)
    shaded_rrect(c, dx - 140, 850, dx + 140, 1334, 8, '#FFFFFF', 7, 0.88)
    bg(c, '#FFE7B0', '#F6C98A', 874, 1334, dx - 116, dx + 116)
    c.drawRect(R(dx - 116, 1270, dx + 116, 1334), P('#E8B877'))
    c.drawRect(R(dx - 116, 874, dx + 116, 1334), P(NAVY, 255, 3))
    shaded_rrect(c, dx - 150, 836, dx + 150, 858, 6, WOOD, 5, 0.8)


def s11(c, t, D):
    off = t * 420
    wall(c, -50, -50, W + 50, 1330, HALL)
    # scrolling wainscot + pictures (parallax 1.0)
    yp = 1060
    c.drawRect(R(0, yp, W, 1330), P(tint(HALL, 0.94)))
    c.drawRect(R(0, yp - 10, W, yp + 8), P(tint(HALL, 1.12))); c.drawLine(0, yp + 8, W, yp + 8, P(NAVY, 60, 3))
    for k in range(-1, 8):
        x = k * 170 - off % 170
        rrect(c, x + 25, yp + 40, x + 145, 1290, 8, P(tint(HALL, 0.88), 255, 4))
    for k in range(-1, 4):
        base = k * 560 - off % 560
        picture(c, base + 120, 560, base + 300, 720, kind=(k + int(off // 560)) % 4)
    dx = 1250 - (t - 1.6) * 900 if t >= 1.6 else 2000
    if dx < 1400: hall_door(c, dx)
    floor(c, 1330, FLOOR, 'wood', scroll=off)
    x, y, s = 560, 1330, 0.95
    mika(c, x, y, s, walk=t * 12, look=(0.6, 0.9))
    px, py = x + 70 * s, y - 175 * s
    glow(c, px, py - 20, 90, SKY, 120)
    shaded_rrect(c, px - 28, py - 50, px + 28, py + 50, 10, NAVY, 4, 0.75)
    rrect(c, px - 20, py - 40, px + 20, py + 38, 5, P('#BFE7F7'))
    for q in range(3): rrect(c, px - 14, py - 30 + q * 22, px + (10 if q % 2 else 4), py - 18 + q * 22, 4, P('#FFFFFF'))
    for n, tt in enumerate((0.3, 0.75, 1.2, 1.65, 2.1)):
        if t < tt: continue
        sx, sy = squash((t - tt) / 0.22)
        bx = 700 + (n % 2) * 140; by = 800 - (t - tt) * 120
        a = clamp(1 - (t - tt - 0.9) / 0.4)
        if a <= 0: continue
        c.saveLayer(None, P('#FFFFFF', 255 * a))
        c.save(); c.translate(bx, by); c.scale(sx, sy)
        rrect(c, -74, -30, 86, 52, 28, blurred(NAVY, 60, 8))
        shaded_rrect(c, -80, -40, 80, 40, 28, '#FFFFFF', 5, 0.9)
        tl_ = skia.Path(); tl_.moveTo(-40 if n % 2 else 40, 36); tl_.lineTo(-60 if n % 2 else 60, 62); tl_.lineTo(-14 if n % 2 else 14, 38); c.drawPath(tl_, P('#FFFFFF')); c.drawPath(tl_, P(NAVY, 255, 5))
        for d in range(3): c.drawCircle(-34 + d * 34, -2 + 4 * math.sin(t * 10 + d), 9, P(SKY if n % 2 else CORAL))
        c.restore(); c.restore()
    if t < 2.35:
        thought(c, 400, 820, eback(t / 0.2), icon_charger, s=0.85, tail=(110, 140))
    else:
        burst(c, 400, 820, (t - 2.35) / 0.3, r=100, col='#FFFFFF')
        dust_puff(c, 400, 860, (t - 2.35) / 0.45, 1.3)
    # brain load gauge (illustrated thermometer)
    fill = clamp((t - 0.1) / 1.05)
    mx0, my0, my1 = 110, 520, 1180
    rrect(c, mx0 - 50, my0 + 10, mx0 + 54, my1 + 20, 44, blurred(NAVY, 70, 10))
    shaded_rrect(c, mx0 - 46, my0, mx0 + 46, my1, 42, '#FFFFFF', 7, 0.88)
    top = my1 - 14 - (my1 - my0 - 28) * eout(fill)
    g = skia.Paint(AntiAlias=True); g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, my1), skia.Point(0, my0)], [C(YEL), C(CORAL)]))
    if my1 - 14 - top > 8: rrect(c, mx0 - 32, top, mx0 + 32, my1 - 14, 30, g)
    for q in range(1, 5): c.drawLine(mx0 + 18, my0 + q * (my1 - my0) / 5, mx0 + 34, my0 + q * (my1 - my0) / 5, P(NAVY, 160, 4))
    c.drawLine(mx0 - 22, my0 + 40, mx0 - 22, my1 - 60, P('#FFFFFF', 120, 8))
    pct = int(count(t, 0.1, 1.05, 0, 100))
    sticker(c, f"{pct} %", mx0 + 40, my0 - 46, 44, CORAL if fill > 0.7 else '#FFFFFF', '#FFFFFF' if fill > 0.7 else NAVY, rot=-4)
    sticker(c, "LOAD", mx0, my1 + 56, 34, NAVY, '#FFFFFF')
    # out-of-focus foreground plant passing faster (parallax 1.8)
    fxp = 1500 - (t * 760) % 2200
    if -300 < fxp < 1400:
        with defocus(c, 12, (fxp - 400, 900, fxp + 400, H)):
            plant(c, fxp, 2050, 2.6, pot=CORAL)
    ost(c, "BUSY MIND = *WORSE*", t, 0.1)


DOOR_COLS = [('#E9A15B', '#FDE3D2', 'dots'), ('#7FB7A4', '#E5F5E8', 'stripes'), ('#4FC3F7', '#FFF0D4', 'panel')]


def s12(c, t, D):
    seg = 1.55
    if t < seg:
        n = min(2, int(t / 0.5)); u = t - n * 0.5
        dcol, bgc, pat = DOOR_COLS[n]
        sl = 1 - eout(u / 0.16)
        c.drawColor(C(bgc))
        c.save(); c.translate(1080 * sl, 0)
        wall(c, -100, -100, W + 100, 1340, bgc, pat)
        shaded_rrect(c, 820, 760, 870, 830, 10, YEL, 4)
        glow(c, 845, 800, 140, '#FFF3B0', 120)
        floor(c, 1340, FLOOR, 'wood')
        plant(c, 900, 1340, 0.9, seed=n)
        front_door(c, 540, 1340, 1.25, col=dcol, open_k=clamp((u - 0.12) / 0.25), number=f"{n + 1}0{n + 2}")
        mika(c, 540, 1360, 0.7, look=(0, 0), mood='o', sweat=True)
        if u >= 0.2:
            sx, sy = squash((u - 0.2) / 0.22)
            c.save(); c.translate(560, 840); c.scale(sx, sy); icon_q(c, 0, 0, 0.9); c.restore()
        c.restore()
        sticker(c, f"#{n + 1}", 920, 560, 80, CORAL, '#FFFFFF', sk=squash(u / 0.2), rot=6, shape='circle')
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
        # s1 is drawn at negative time, so the last frame here continues straight into s1 frame 0 (seamless loop)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]


def sfx_cues(put, S, K, D, fx):
    """put(t_seconds, signal, gain); S = scene starts, K = time factor (1.0 without DESIGN_DUR), D = scene durations.
    Transition whooshes are added automatically by the engine (TRANSITIONS)."""
    q = lambda i, t: S[i] + t * K[i]
    # s1: footsteps, thought pop, doorway shimmer, '?' ding, zoom hit
    put(q(0, 0.0), fx.footsteps(4, .3), .5)
    put(q(0, 0.5), fx.sparkle_fx(4, 88), .5)
    put(q(0, 0.58), fx.swoosh(.2, 900, 7000), .4); put(q(0, 0.6), fx.popm(4, 70), .9)
    put(q(0, 1.05), fx.ding(81), .8)
    put(q(0, 1.55), fx.subhit(), .6); put(q(0, 1.55), fx.swoosh(.16, 800, 6000), .35)
    # s2: phone + homework pops, blank, ticking + crickets + tumbleweed
    put(q(1, 0.1), fx.popm(2), .8); put(q(1, 0.81), fx.popm(4), .8); put(q(1, 0.85), fx.paper(.2), .6)
    put(q(1, 1.55), fx.swoosh(.35, 200, 1500, False), .4); put(q(1, 1.55), fx.popm(0, 60), .6)
    for k in range(7): put(q(1, 1.6 + k * 0.22), fx.tick(k % 2 == 0), .7)
    put(q(1, 1.75), fx.crickets(D[1] - 1.75), 1.0)
    put(q(1, 2.13), fx.swoosh(.6, 200, 1200), .25)
    # s3: memory bar count-up ticks, OK ding, flash + thud, suspect sting
    for tt in count_ticks(0.51, 0.5, 0, 100, min_gap=0.06): put(q(2, tt), fx.tick(), .5)
    put(q(2, 0.95), fx.popm(5), .7); put(q(2, 1.0), fx.ding(88), .5)
    put(q(2, 1.33), fx.camera_flash(), .8); put(q(2, 1.36), fx.thud(), .7)
    put(q(2, 2.07), fx.cringe(), .5); put(q(2, 2.07), fx.popm(1, 60), .6)
    # s4: plan builds, objects bounce, walker footsteps, 55 counter
    for k in range(6): put(q(3, 0.0 + k * 0.08), fx.tick(k % 2 == 0), .3)
    put(q(3, 0.15), fx.footsteps(9, .32, True), .25)
    for k in range(5): put(q(3, 1.2 + k * 0.08), fx.popm(k), .35)
    put(q(3, 1.89), fx.popm(6), .7)
    for tt in count_ticks(1.95, 0.6, 0, 55, min_gap=0.05): put(q(3, tt), fx.tick(True), .4)
    # s5: lane A walk + doorway shimmer, lane B slides in, tape measure, '='
    put(q(4, 0.1), fx.footsteps(6, .3), .3); put(q(4, 1.0), fx.sparkle_fx(4, 88), .45)
    put(q(4, 1.75), fx.paper(.25), .7); put(q(4, 1.8), fx.footsteps(6, .3), .3)
    put(q(4, 3.4), fx.ratsch(0.35), .6); put(q(4, 3.75), fx.ding(84), .5); put(q(4, 3.75), fx.popm(5), .6)
    # s6: card flip, countdown ticks, options pop, uh-oh
    put(q(5, 0.0), fx.paper(.2), .6)
    for k in range(3): put(q(5, 0.51 + k * (D[5] - 0.6) / 3), fx.tick(True), 1.0)
    put(q(5, 1.1), fx.popm(2), .6); put(q(5, 1.28), fx.popm(4), .6)
    put(q(5, 1.52), fx.cringe(), .5)
    # s7: people pop in, counters tick, 2x sting
    for k in range(10): put(q(6, 0.1 + k * 0.04), fx.popm(k % 5, 79), .22)
    put(q(6, 0.95), fx.boing(180), .6)
    for tt in count_ticks(0.95, 0.45, 0, 10): put(q(6, tt), fx.tick(), .5)
    put(q(6, 2.43), fx.paper(.25), .5)
    for k in range(10): put(q(6, 2.45 + k * 0.04), fx.popm(k % 5, 79), .22)
    for k in range(2): put(q(6, 3.44 + k * 0.18), fx.boing(160 + 30 * k), .6)
    for tt in count_ticks(3.5, 0.45, 0, 20, min_gap=0.035): put(q(6, tt), fx.tick(True), .5)
    put(q(6, 3.95), fx.subhit(), .6); put(q(6, 3.95), fx.ding(86), .6); put(q(6, 3.95), fx.sparkle_fx(5, 84), .6)
    # s8: brain pops up, projector rolls, scissors snip, scene stickers
    put(q(7, 0.1), fx.popm(3), .6); put(q(7, 0.65), fx.projector(2.1), .5)
    put(q(7, 1.8), fx.popm(5), .5)
    put(q(7, 2.82), fx.clack(), .8); put(q(7, 2.9), fx.swoosh(.3, 600, 6000), .4)
    for k in range(3): put(q(7, 3.42 + k * 0.15), fx.popm(2 + 2 * k), .55)
    # s9: clapper slam, footsteps, chapter stickers
    put(q(8, 0.15), fx.swoosh(.25, 300, 3000, False), .35); put(q(8, 0.55), fx.clack(), 1.0); put(q(8, 0.55), fx.subhit(), .5)
    put(q(8, 0.1), fx.footsteps(4, .3), .4)
    put(q(8, 1.42), fx.popm(2), .6); put(q(8, 1.98), fx.popm(5), .6)
    # s10: drawer, folder flies in, slam, x-ray, stamp
    put(q(9, 0.1), fx.popm(3), .5); put(q(9, 0.2), fx.drawer(.35), .7); put(q(9, 0.6), fx.swoosh(.8, 200, 2500), .45)
    put(q(9, 1.55), fx.drawer(.15), .6); put(q(9, 1.65), fx.thud(), 1.0); put(q(9, 1.65), fx.clack(), .5)
    put(q(9, 1.96), fx.sparkle_fx(4, 76), .5); put(q(9, 2.73), fx.clack(), .7); put(q(9, 2.73), fx.thud(), .4)
    # s11: walking + typing, chat pops, load ticks, thought pops
    put(q(10, 0.0), fx.footsteps(7, .42), .35); put(q(10, 0.1), fx.typing(2.2), .25)
    for tt in count_ticks(0.1, 1.05, 0, 100, min_gap=0.07): put(q(10, tt), fx.tick(), .3)
    for n, tt in enumerate((0.3, 0.75, 1.2, 1.65, 2.1)): put(q(10, tt), fx.popm(n + 3, 79), .4)
    put(q(10, 2.35), fx.popm(0, 60), .8); put(q(10, 2.35), fx.swoosh(.2, 800, 6000), .35)
    # s12: three doors, then the zoom back into s1
    for k in range(3):
        put(q(11, k * 0.5), fx.swoosh(.18, 700, 6000), .45); put(q(11, k * 0.5 + 0.12), fx.drawer(.15), .3)
        put(q(11, k * 0.5 + 0.2), fx.popm(2 + 2 * k), .5)
    put(q(11, 1.55), fx.swoosh(.5, 150, 1500), .35)
    put(q(11, 1.7), fx.riser(D[11] - 1.7), .5)
