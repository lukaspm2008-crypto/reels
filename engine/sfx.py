"""Reel engine: synthesized sound effects + music bed (48 kHz mono numpy arrays)."""
import numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
rng = np.random.default_rng(7)


def T(n): return np.arange(n) / SR


def put(buf, t, x, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += g * x



def lp(x, f):
    return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)


def hp(x, f):
    return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def bp(x, f0, f1):
    return sosfilt(butter(2, [f0, f1], 'band', fs=SR, output='sos'), x)


def clack():
    t = T(int(.35 * SR)); n = rng.standard_normal(len(t))
    return 0.9 * bp(n, 800, 5000) * np.exp(-t / .012) + 0.8 * np.sin(2 * np.pi * 95 * t) * np.exp(-t / .09)


def subhit():
    t = T(int(1.2 * SR)); f = 38 + 30 * np.exp(-t / .08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .45)


def whoosh(d=.4, f0=300, f1=3000):
    t = T(int(d * SR)); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    return bp(n, f0, f1) * env * 0.8


def pop(f=700):
    t = T(int(.09 * SR)); fr = f + 500 * t / .09
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .025) * 0.6


def click():
    t = T(int(.04 * SR)); return (np.sin(2 * np.pi * 2200 * t) * np.exp(-t / .006) + 0.4 * rng.standard_normal(len(t)) * np.exp(-t / .002)) * 0.5


def ratsch(d=.45):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 30)):
        put(out, k / 30, click(), 0.6)
    return out


def cringe():
    t = T(int(.9 * SR)); f = 330 * (1 - 0.35 * t / .9) * (1 + 0.04 * np.sin(2 * np.pi * 6 * t))
    ph = np.cumsum(f) / SR; saw = 2 * (ph % 1) - 1
    return lp(saw, 1400) * np.minimum(1, t / .03) * np.exp(-t / .5) * 0.35


def thud():
    t = T(int(.5 * SR)); return np.sin(2 * np.pi * 62 * t) * np.exp(-t / .16) + 0.3 * lp(rng.standard_normal(len(t)), 300) * np.exp(-t / .05)


def murmur(d=1.6):
    t = T(int(d * SR)); n = bp(rng.standard_normal(len(t)), 250, 900)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 3.3 * t) * np.sin(2 * np.pi * 1.7 * t)
    return n * am * np.minimum(1, np.minimum(t / .2, (d - t) / .4)) * 0.25


def projector(d=2.0):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 18)): put(out, k / 18, click(), 0.25)
    t = T(len(out)); out += 0.05 * bp(rng.standard_normal(len(out)), 100, 400)
    return out * np.minimum(1, np.minimum(t / .2, (d - t) / .3))


def rewind(d=1.2):
    t = T(int(d * SR)); f = 1800 - 1200 * ((t * 4) % 1)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.12 * np.minimum(1, (d - t) / .05)


def riser(d=2.0):
    t = T(int(d * SR)); f = 200 * (6 ** (t / d))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + 0.6 * hp(rng.standard_normal(len(t)), 2000) * (t / d)
    return s * (t / d) ** 2


def chime():
    t = T(int(.6 * SR)); return (np.sin(2 * np.pi * 1320 * t) + .5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t / .15) * 0.3


# ---------------------------------------------------------------- engine v2: softer, more musical one-shots
PENTA = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]


def note_hz(m): return 440 * 2 ** ((m - 69) / 12)


def swoosh(d=.35, f0=300, f1=4000, rise=True):
    """whoosh whose band sweeps (low->high if rise) - airier than whoosh()"""
    n = int(d * SR); t = T(n); x = rng.standard_normal(n)
    out = np.zeros(n); bands = 7
    for k in range(bands):
        fa = f0 * (f1 / f0) ** (k / bands); fb = f0 * (f1 / f0) ** ((k + 1) / bands)
        c = (k + 0.5) / bands if rise else 1 - (k + 0.5) / bands
        env = np.exp(-((t / d - c * 0.8 - 0.1) ** 2) / 0.03)
        out += bp(x, fa, min(fb, SR / 2 - 100)) * env
    return out * np.sin(np.pi * t / d) ** 1.5 * 0.9


def transition_whoosh(kind='whip'):
    if kind == 'zoom':
        return 0.8 * swoosh(.42, 150, 3500, True) + 0.25 * subhit()[:int(.42 * SR)] * np.linspace(0, 1, int(.42 * SR)) ** 4
    if kind == 'wipe':
        return swoosh(.34, 400, 6000, False) + paper_pad(.34)
    return swoosh(.3, 300, 6500, True)


def paper(d=.25):
    """paper rustle / flick"""
    n = int(d * SR); t = T(n); x = hp(rng.standard_normal(n), 1500)
    am = np.abs(np.sin(2 * np.pi * 23 * t + 3 * np.sin(2 * np.pi * 7 * t))) ** 3
    return x * am * np.exp(-t / (d * 0.5)) * 0.5


def paper_pad(d):
    p = paper(min(d, .25)); out = np.zeros(int(d * SR)); out[:len(p)] += p * 0.4; return out


def popm(step=0, base=72, soft=True):
    """musical bubble pop tuned to a pentatonic step (use step=k for ascending series)"""
    f = note_hz(base + PENTA[step % len(PENTA)])
    d = .16; t = T(int(d * SR))
    fr = f * (0.75 + 0.25 * (1 - np.exp(-t / .012)))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) + 0.25 * np.sin(2 * ph)
    env = np.minimum(1, t / .002) * np.exp(-t / (.05 if soft else .03))
    click_ = lp(rng.standard_normal(len(t)), 4000) * np.exp(-t / .002) * 0.15
    return (s * env + click_) * 0.55


def tick(hi=False):
    """woodblock tick for counters / clocks"""
    t = T(int(.06 * SR)); f = 2600 if hi else 2100
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / .008) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t) * np.exp(-t / .005)
    return (s + 0.3 * bp(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t / .002)) * 0.35


def ding(m=84):
    """small bell (inharmonic partials)"""
    t = T(int(1.2 * SR)); f = note_hz(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / dcy) for r, a, dcy in ((1, 1, .5), (2.76, .4, .2), (5.4, .2, .09), (0.5, .15, .6)))
    return s * np.minimum(1, t / .002) * 0.28


def sparkle_fx(n=5, base=84):
    out = np.zeros(int(.7 * SR))
    for k in range(n):
        f = note_hz(base + PENTA[(k * 2) % len(PENTA)]); t = T(int(.3 * SR))
        put(out, k * .06, np.sin(2 * np.pi * f * t) * np.exp(-t / .07) * 0.18)
    return out


def step(soft=True):
    """footstep"""
    t = T(int(.15 * SR)); n = rng.standard_normal(len(t))
    return (lp(n, 600 if soft else 1200) * np.exp(-t / .03) + 0.6 * np.sin(2 * np.pi * 85 * t) * np.exp(-t / .04)) * 0.5


def footsteps(n, gap=.32, soft=True):
    out = np.zeros(int((n * gap + .3) * SR))
    for k in range(n): put(out, k * gap, step(soft), 0.8 + 0.2 * (k % 2))
    return out


def tap():
    """phone screen tap"""
    t = T(int(.03 * SR)); return (bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t / .004)) * 0.5


def typing(d=1.0, rate=7):
    out = np.zeros(int(d * SR))
    for k in range(int(d * rate)): put(out, k / rate + rng.uniform(0, .04), tap(), rng.uniform(.6, 1))
    return out


def crickets(d=1.5):
    """'awkward silence' crickets"""
    out = np.zeros(int(d * SR)); t = T(int(.18 * SR))
    chirp = np.sin(2 * np.pi * 4300 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 45 * t)) * np.sin(np.pi * t / .18)
    for k in range(int(d / .6) + 1):
        put(out, k * .6, chirp * 0.12); put(out, k * .6 + .22, chirp * 0.1)
    return out


def drawer(d=.45):
    """sliding drawer / box scrape"""
    t = T(int(d * SR)); n = rng.standard_normal(len(t))
    return bp(n, 200, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t)) * np.sin(np.pi * t / d) * 0.5


def camera_flash():
    t = T(int(.35 * SR))
    return (hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / .02) * 0.5 + np.sin(2 * np.pi * (3000 + 4000 * t) * t) * np.exp(-t / .1) * 0.08)


def boing(f=220):
    t = T(int(.4 * SR)); fr = f * (1 + 0.5 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / .12))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .15) * 0.4


# ---------------------------------------------------------------- ambience beds
def _pink(n):
    w = rng.standard_normal(n); X = np.fft.rfft(w); f = np.arange(len(X)); f[0] = 1
    return np.fft.irfft(X / np.sqrt(f), n) * 8


def room_tone(d):
    n = int(d * SR); t = T(n)
    return lp(_pink(n), 400) * 0.25 + 0.02 * np.sin(2 * np.pi * 100 * t) + 0.012 * np.sin(2 * np.pi * 50 * t)


def cafe(d):
    """cafeteria / school hallway murmur with occasional cutlery clinks"""
    n = int(d * SR); t = T(n); out = np.zeros(n)
    for k in range(5):
        v = bp(rng.standard_normal(n), 200 + 80 * k, 900 + 150 * k)
        am = np.clip(np.sin(2 * np.pi * (2.5 + 0.7 * k) * t + k) * np.sin(2 * np.pi * (0.6 + 0.2 * k) * t + 2 * k), 0, 1)
        out += v * am * 0.22
    for k in range(int(d * 1.3)):
        tt = T(int(.25 * SR)); f = rng.uniform(2500, 4200)
        put(out, rng.uniform(0, d), np.sin(2 * np.pi * f * tt) * np.exp(-tt / .05) * 0.06)
    return out + room_tone(d) * 0.5


def birds(d):
    """outdoor: soft air + bird chirps"""
    n = int(d * SR); out = lp(_pink(n), 1200) * 0.08
    for k in range(int(d * 1.6)):
        L = rng.uniform(.06, .14); tt = T(int(L * SR)); f0 = rng.uniform(2800, 4200)
        fr = f0 + rng.uniform(-1, 1) * 1500 * tt / L + 300 * np.sin(2 * np.pi * 30 * tt)
        ch = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tt / L)
        t0 = rng.uniform(0, max(.01, d - .5))
        for r in range(rng.integers(1, 4)): put(out, t0 + r * (L + .04), ch * 0.08)
    return out


def hum(d):
    """fluorescent / fridge hum (office, archive, lab)"""
    n = int(d * SR); t = T(n)
    return room_tone(d) * 0.6 + 0.03 * np.sin(2 * np.pi * 120 * t) + 0.015 * np.sin(2 * np.pi * 240 * t) + 0.01 * bp(rng.standard_normal(n), 2000, 5000)


def clockroom(d):
    out = room_tone(d) * 0.8
    for k in range(int(d) + 1): put(out, k + .1, tick(k % 2 == 0), 0.18)
    return out


def projector_bed(d):
    out = room_tone(d) * 0.6
    for k in range(int(d * 18)): put(out, k / 18, click(), 0.08)
    return out


AMBIENCES = {'room': room_tone, 'cafe': cafe, 'birds': birds, 'hum': hum, 'clock': clockroom, 'projector': projector_bed}


def ambience(name, d, seed=0):
    x = AMBIENCES[name](d + 0.05)[:int(d * SR)]
    return x / max(1e-9, np.sqrt(np.mean(x ** 2))) * 0.05    # RMS-normalised beds


def music_bed(dur, seed_progression=0, bpm=112):
    """light electronic loop (kick, offbeat hat, triangle pluck arpeggio, sub pad). seed_progression rotates chords for variety."""
    N = int(dur * SR); mus = np.zeros(N)
    beat = 60 / bpm
    progs = [[[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],
             [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]],
             [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]]]
    chords = progs[seed_progression % len(progs)]
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    for b in range(int(dur / beat) + 2):
        t0 = b * beat
        tk = T(int(.3 * SR)); fk = 50 + 90 * np.exp(-tk / .03)
        put(mus, t0, np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tk / .12), .55)
        th = T(int(.06 * SR)); put(mus, t0 + beat / 2, hp(rng.standard_normal(len(th)), 7000) * np.exp(-th / .015), .12)
        ch = chords[(b // 4) % 4]
        for h in range(2):
            m = ch[(b * 2 + h) % 3] + 12
            tp = T(int(.35 * SR)); f = midi(m)
            tri = 2 * np.abs(2 * ((f * tp) % 1) - 1) - 1
            put(mus, t0 + h * beat / 2, tri * np.exp(-tp / .12), .13)
        if b % 4 == 0:
            tb = T(int(4 * beat * SR)); f = midi(ch[0] - 12)
            put(mus, t0, np.sin(2 * np.pi * f * tb) * np.minimum(1, tb / .05) * np.exp(-tb / 1.5), .2)
    fi = int(.08 * SR); mus[:fi] *= np.linspace(0, 1, fi)
    return mus


def duck(mus, vo, depth=0.45):
    env = np.abs(vo); win = int(.12 * SR)
    env = np.convolve(env, np.ones(win) / win, 'same')
    return mus * (1 - depth * np.clip(env / 0.05, 0, 1))
