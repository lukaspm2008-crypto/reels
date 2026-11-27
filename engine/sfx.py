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
