"""EVO LABS — motor de audio: música electrónica cinematográfica original + SFX + mezcla."""
import os, subprocess, sys, math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg

SR = cfg.SR
FF = cfg.FF
N = int(cfg.TOTAL * SR) + SR
rng = np.random.default_rng(7)


# ------------------------------------------------------------------ utilidades
def zeros(sec):
    return np.zeros(int(sec * SR), dtype=np.float32)


def tarr(sec):
    return np.arange(int(sec * SR), dtype=np.float32) / SR


def add(buf, sig, start, gain=1.0, pan=0.0):
    """buf: (2,N) float32; sig: mono"""
    i0 = int(start * SR)
    if i0 >= buf.shape[1] or len(sig) == 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), buf.shape[1] - i0)
    if n <= 0:
        return
    gl = gain * math.sqrt((1 - pan) / 2 + 0.5) * (1 - max(0, pan) * 0.0)
    gl = gain * (1.0 - max(0.0, pan) * 0.55)
    gr = gain * (1.0 - max(0.0, -pan) * 0.55)
    buf[0, i0:i0 + n] += sig[:n] * gl / math.sqrt(2)
    buf[1, i0:i0 + n] += sig[:n] * gr / math.sqrt(2)


def boxfilt(x, k):
    """FIR de media móvil (lowpass) vía suma acumulada."""
    k = max(1, int(k))
    if k == 1:
        return x
    c = np.cumsum(x, dtype=np.float64)
    c = np.concatenate(([0.0], c))
    y = (c[k:] - c[:-k]) / k
    pad = np.full(k - 1, y[0] if len(y) else 0.0)
    return np.concatenate((pad, y)).astype(np.float32)[:len(x)]


def highpass(x, k):
    return (x - boxfilt(x, k)).astype(np.float32)


def env_ad(n, a, d, curve=3.0):
    e = np.ones(n, dtype=np.float32)
    na = max(1, int(a * SR))
    nd = max(1, int(d * SR))
    if na < n:
        e[:na] = np.linspace(0, 1, na) ** 0.7
    if nd < n:
        e[-nd:] *= np.linspace(1, 0, nd) ** curve
    return e


def adsr(n, a, d, s, r):
    a, d, r = max(1, int(a * SR)), max(1, int(d * SR)), max(1, int(r * SR))
    e = np.zeros(n, dtype=np.float32)
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a)
    dd = min(d, max(0, n - a))
    if dd:
        e[a:a + dd] = np.linspace(1, s, dd)
    if n > a + dd:
        rest = n - a - dd
        e[a + dd:] = s
        rr = min(r, rest)
        e[n - rr:] *= np.linspace(1, 0, rr) ** 1.5
    return e


def saw(freq, n, harm=12, detune=0.0, phase=0.0):
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, dtype=np.float32)
    for k in range(1, harm + 1):
        f = freq * k * (1 + detune * (k % 3 - 1) * 0.5)
        if f > 15000:
            break
        out += (np.sin(2 * np.pi * f * t + phase * k) / k).astype(np.float32)
    return out * (2 / np.pi)


def supersaw(freq, n, harm=10, spread=0.004):
    return (saw(freq * (1 - spread), n, harm) + saw(freq, n, harm) +
            saw(freq * (1 + spread), n, harm)) / 3.0


def noise(n):
    return rng.standard_normal(n).astype(np.float32)


def spectral_sweep(dur, f0, f1, q=2.0, env=None, seed=1):
    """Ruido filtrado con banda que barre de f0 a f1 (overlap-add con FFT)."""
    n = int(dur * SR)
    blk, hop = 2048, 1024
    win = np.hanning(blk).astype(np.float32)
    out = np.zeros(n + 3 * blk, dtype=np.float32)
    r = np.random.default_rng(seed)
    nb = int(np.ceil(n / hop)) + 1
    freqs = np.fft.rfftfreq(blk, 1 / SR)
    for b in range(nb):
        p = b / max(1, nb - 1)
        fc = f0 * (f1 / f0) ** p
        w = np.exp(-0.5 * (np.log2(np.maximum(freqs, 20) / fc) * q) ** 2).astype(np.float32)
        seg = r.standard_normal(blk).astype(np.float32) * win
        spec = np.fft.rfft(seg)
        y = np.fft.irfft(spec * w).astype(np.float32) * win
        i = b * hop
        out[i:i + blk] += y
    out = out[:n]
    if env is not None:
        out *= env
    return out.astype(np.float32)


def reverb_ir(rt=2.0, pre=0.02, bright=0.55):
    n = int(rt * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-t * (5.5 / rt))
    ir = highpass(ir, int(SR / (4000 * bright)))
    ir = boxfilt(ir, 3)
    ir[: int(pre * SR)] *= np.linspace(0, 1, int(pre * SR)) ** 2
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    return ir


IR = reverb_ir(2.2, 0.025, 0.6)
IR_SHORT = reverb_ir(0.9, 0.01, 0.9)


def conv(x, ir):
    n = len(x) + len(ir) - 1
    nf = 1 << (n - 1).bit_length()
    Y = np.fft.rfft(x, nf) * np.fft.rfft(ir, nf)
    return np.fft.irfft(Y, nf)[:len(x)].astype(np.float32)


# ------------------------------------------------------------------ voz en off
def load_audio(path):
    p = subprocess.run([FF, '-v', 'quiet', '-i', path, '-f', 's16le', '-ac', '1',
                        '-ar', str(SR), '-'], capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def build_voice():
    vo = np.zeros(N, dtype=np.float32)
    for sc in cfg.SCENES:
        k = sc['key']
        fname = cfg.VO_FILE.get(k, f'vo_{k}.mp3')
        sig = load_audio(os.path.join(cfg.DIR_AUDIO, fname))
        # pequeño fade para evitar clicks
        f = int(0.008 * SR)
        sig[:f] *= np.linspace(0, 1, f)
        sig[-f:] *= np.linspace(1, 0, f)
        i0 = int(sc['vo_start'] * SR)
        vo[i0:i0 + len(sig)] = sig[:max(0, N - i0)]
    # procesado: HP, compresión suave, leve aire
    v = highpass(vo, int(SR / 70))
    lvl = np.abs(v)
    envf = boxfilt(boxfilt(lvl, int(0.010 * SR)), int(0.060 * SR))
    thr = 0.06
    g = np.where(envf > thr, (thr + (envf - thr) * 0.45) / np.maximum(envf, 1e-6), 1.0)
    g = boxfilt(g, int(0.006 * SR)).astype(np.float32)
    v = v * g
    v = np.tanh(v * 1.35) * 0.78
    peak = np.max(np.abs(v)) + 1e-9
    v *= 0.72 / peak
    return v


# ------------------------------------------------------------------ música
NOTE = {'A': 0, 'B': 2, 'C': 3, 'D': 5, 'E': 7, 'F': 8, 'G': 10}


def freq(name):
    """'A2' -> Hz"""
    p = NOTE[name[0]]
    if len(name) > 2 and name[1] in '#b':
        p += 1 if name[1] == '#' else -1
        name = name[0] + name[2:]
    octv = int(name[1])
    return 440.0 * 2 ** ((p + (octv - 4) * 12 - 9) / 12)


CHORDS = [  # (root, [notes])
    ('A2', ['A3', 'C4', 'E4']),
    ('F2', ['F3', 'A3', 'C4']),
    ('C3', ['C4', 'E4', 'G4']),
    ('G2', ['G3', 'B3', 'D4']),
]

ENERGY = {'s1': 0.42, 's2': 0.85, 's3': 1.0, 's4': 0.9,
          's5': 0.28, 's6': 0.8, 's7': 0.95, 's8': 1.0}

BPM = 96.0
BEAT = 60.0 / BPM
BAR = BEAT * 4


def energy_at(t):
    for sc in cfg.SCENES:
        if sc['start'] <= t < sc['end']:
            e = ENERGY.get(sc['key'], 0.82)
            # rampa suave al inicio de escena
            k = min(1.0, (t - sc['start']) / 1.2)
            prev = ENERGY.get(cfg.SCENES[max(0, cfg.SCENES.index(sc) - 1)]['key'], 0.82) if cfg.SCENES.index(sc) > 0 else e
            return prev + (e - prev) * k
    return 0.4


def build_music():
    drums = np.zeros((2, N), np.float32)
    bass = np.zeros((2, N), np.float32)
    arp = np.zeros((2, N), np.float32)
    pad = np.zeros((2, N), np.float32)
    lead = np.zeros((2, N), np.float32)

    # --- acordes / pad (toda la pieza)
    nb = int(cfg.TOTAL / (BAR * 2)) + 1
    for b in range(nb):
        t0 = b * BAR * 2
        root, notes = CHORDS[b % 4]
        e = energy_at(t0 + BAR)
        dur = BAR * 2
        for i, nt in enumerate(notes):
            n = int((dur + 0.6) * SR)
            s = supersaw(freq(nt), n, harm=9, spread=0.0035)
            s *= adsr(n, 0.25 if e < 0.5 else 0.12, 0.25, 0.75, 0.5)
            add(pad, s, t0, gain=0.052 * (0.75 + 0.45 * (1 - e)), pan=(i - 1) * 0.25)
        sub = np.sin(2 * np.pi * freq(root) / 2 * np.arange(int(dur * SR)) / SR).astype(np.float32)
        sub *= adsr(len(sub), 0.4, 0.4, 0.8, 0.6)
        add(pad, sub, t0, gain=0.10 * (0.7 + 0.5 * e))

    # --- groove
    t = 0.0
    step = BEAT / 4  # semicorchea
    i = 0
    typer = 0
    while t < cfg.TOTAL - 0.5:
        e = energy_at(t)
        bar_i = i // 16
        root, notes = CHORDS[bar_i % 4]
        pos = i % 16

        # kick
        if e > 0.62 and pos % 4 == 0:
            n = int(0.42 * SR)
            tt = np.arange(n) / SR
            f = 118 * np.exp(-tt * 24) + 46
            ph = 2 * np.pi * np.cumsum(f) / SR
            k = (np.sin(ph) * np.exp(-tt * 7.5)).astype(np.float32)
            k += highpass(noise(n), 8)[:n] * np.exp(-tt * 140) * 0.22
            add(drums, k, t, 0.62)
        # snare
        if e > 0.7 and pos in (4, 12):
            n = int(0.26 * SR)
            tt = np.arange(n) / SR
            s = highpass(noise(n), int(SR / 2600)) * np.exp(-tt * 22)
            s += 0.25 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 32)
            add(drums, s.astype(np.float32) * 0.85, t, 0.30, pan=0.05)
            add(drums, s.astype(np.float32) * 0.5, t + 0.012, 0.16, pan=-0.15)
        # hats
        if e > 0.5 and pos % 2 == 0:
            n = int(0.09 * SR)
            tt = np.arange(n) / SR
            h = highpass(noise(n), 3)[:n] * np.exp(-tt * 70)
            add(drums, h, t, 0.085 if pos % 4 else 0.13, pan=0.3 if pos % 8 else -0.3)
        # clap extra en escena ring
        if e > 0.95 and pos in (6, 14):
            n = int(0.12 * SR)
            tt = np.arange(n) / SR
            c = highpass(noise(n), 4) * np.exp(-tt * 42)
            add(drums, c, t, 0.06, pan=-0.3)
        # bajo en corcheas
        if e > 0.55 and pos % 4 in (0, 2):
            n = int(BEAT * 1.2 * SR)
            s = saw(freq(root) / 2, n, harm=7)
            s = boxfilt(s, int(SR / (900 * (0.6 + 0.5 * e))) * 2)
            s *= adsr(n, 0.006, 0.05, 0.55, 0.12)
            add(bass, s, t, 0.30)
        # arpegio
        if e > 0.68:
            nt = notes[(pos // 2) % 3]
            f = freq(nt) * 2
            n = int(step * 3 * SR)
            s = saw(f, n, harm=4) * adsr(n, 0.004, 0.04, 0.15, 0.09)
            s = boxfilt(s, 3)
            add(arp, s, t, 0.055, pan=0.45 if (pos // 2) % 2 else -0.45)
        # melodía temática en el ring y el final
        if e > 0.92 and pos in (0, 6, 10):
            mel = ['E5', 'D5', 'A4', 'C5', 'E5', 'G4'][(bar_i * 3 + pos // 2) % 6]
            n = int(BEAT * 0.9 * SR)
            s = (np.sin(2 * np.pi * freq(mel) * np.arange(n) / SR) * 0.7 +
                 saw(freq(mel), n, harm=3) * 0.3).astype(np.float32)
            s *= adsr(n, 0.01, 0.08, 0.2, 0.25)
            add(lead, s, t, 0.075, pan=-0.1)
        typer += 1
        i += 1
        t = i * step
    return drums, bass, arp, pad, lead


# ------------------------------------------------------------------ SFX
def sfx_impact(dur=2.4, big=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 95 * np.exp(-tt * 6.5) + 34
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6)
    sub = np.sin(2 * np.pi * 42 * tt) * np.exp(-tt * 1.9)
    hit = highpass(noise(n), 12) * np.exp(-tt * 26) * 0.5
    s = (body * 0.8 + sub * 0.55 + hit).astype(np.float32)
    return s * big


def sfx_riser(dur=2.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = (tt / dur) ** 2.2
    s = spectral_sweep(dur, 240, 7200, 2.6, env=env.astype(np.float32), seed=3)
    n2 = n
    sweep = saw(180, n2, harm=6) * env.astype(np.float32) * 0.25
    return (s * 0.9 + sweep).astype(np.float32)


def sfx_whoosh(dur=0.7, bright=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = np.sin(np.pi * (tt / dur)) ** 2
    s = spectral_sweep(dur, 400 * bright, 5200 * bright, 1.8, env=env.astype(np.float32), seed=int(10 * bright))
    return s * 0.9


def sfx_blip(f=1400, dur=0.09):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 34)).astype(np.float32)


def sfx_chime(dur=1.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for k, f in enumerate([1046.5, 1318.5, 1568.0]):
        s += np.sin(2 * np.pi * f * tt) * np.exp(-tt * (2.4 + k)) * (0.6 - 0.12 * k)
    return s.astype(np.float32)


def sfx_buzz(dur=0.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = (np.sign(np.sin(2 * np.pi * 130 * tt)) * 0.3 + noise(n) * 0.2)
    s = np.round(s * 6) / 6  # bitcrush
    return (s * np.exp(-tt * 3.2)).astype(np.float32)


def sfx_glitch(dur=0.35):
    n = int(dur * SR)
    s = noise(n)
    hold = 6
    s = np.repeat(s[::hold], hold)[:n]
    s = np.round(s * 4) / 4
    env = env_ad(n, 0.002, 0.3, 2.0)
    return (s * env).astype(np.float32)


def sfx_type(dur=0.05):
    n = int(dur * SR)
    s = highpass(noise(n), 2)
    return (s * np.exp(-np.arange(n) / SR * 120)).astype(np.float32)


def sfx_power(dur=3.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    e = (tt / dur) ** 1.5
    hum = (np.sin(2 * np.pi * 60 * tt) + 0.4 * np.sin(2 * np.pi * 120 * tt)).astype(np.float32)
    return (hum * e * 0.35 + spectral_sweep(dur, 90, 2400, 3.0, env=e.astype(np.float32), seed=9) * 0.6).astype(np.float32)


def build_sfx():
    fx = np.zeros((2, N), np.float32)
    shot_edges = [s['start'] for s in cfg.SHOTS if s['start'] > 0.1]
    for j, ts in enumerate(shot_edges):
        add(fx, sfx_whoosh(0.55, 0.8 + 0.5 * (j % 3)), ts - 0.28, 0.16, pan=0.4 if j % 2 else -0.4)
    # encendido
    add(fx, sfx_power(5.4), 0.15, 0.20)
    for k in range(int(4.6 / 0.11)):
        add(fx, sfx_type(0.04), 0.9 + k * 0.11 + rng.uniform(-0.02, 0.02),
            0.05 + 0.03 * rng.random(), pan=rng.uniform(-0.6, 0.6))
    # impactos de logo / escenas
    add(fx, sfx_impact(2.6, 0.9), 5.62, 0.62)
    add(fx, sfx_riser(2.0), 5.0, 0.24, pan=0.1)
    for key, g in [('s2', 0.34), ('s3', 0.46), ('s6', 0.40), ('s8', 0.62)]:
        sc = next(s for s in cfg.SCENES if s['key'] == key)
        add(fx, sfx_impact(2.4), max(0, sc['start'] - 0.02), g)
        add(fx, sfx_riser(2.4), max(0, sc['start'] - 2.4), 0.20)
    # ring: blips de competencia
    for k in range(10):
        add(fx, sfx_blip(900 + 260 * (k % 4), 0.07), 25.2 + k * 0.31, 0.055, pan=-0.5 + k * 0.1)
    # promesa: chime + impacto suave
    add(fx, sfx_impact(2.0, 0.6), 49.12, 0.30)
    add(fx, sfx_chime(2.0), 49.3, 0.16, pan=0.1)
    # comparativa: glitch + buzz (falso) y chime (real)
    add(fx, sfx_glitch(0.45), 72.32, 0.16, pan=-0.3)
    add(fx, sfx_buzz(0.55), 72.75, 0.14, pan=-0.2)
    add(fx, sfx_chime(1.8), 74.95, 0.16, pan=0.2)
    # final
    add(fx, sfx_impact(3.0, 1.0), 90.52, 0.42)
    add(fx, sfx_riser(2.2), 88.4, 0.14)
    return fx


# ------------------------------------------------------------------ mezcla
def build():
    os.makedirs(cfg.BUILD, exist_ok=True)
    print('voz...')
    vo = build_voice()
    print('música...')
    drums, bass, arp, pad, lead = build_music()
    print('sfx...')
    fx = build_sfx()

    # envíos a reverb
    def wet(bus, amount, ir=IR):
        m = bus.mean(axis=0)
        w = conv(m, ir)
        return np.stack([bus[0] + w * amount, bus[1] + w * amount])

    pad = wet(pad, 0.55)
    arp = wet(arp, 0.30, IR_SHORT)
    lead = wet(lead, 0.35, IR_SHORT)
    drums = wet(drums, 0.10, IR_SHORT)
    fxw = wet(fx, 0.45)

    music = drums * 1.0 + bass * 1.0 + arp * 1.0 + pad * 1.0 + lead * 1.0 + fxw * 1.0

    # normalizar música a un nivel objetivo
    mpeak = np.max(np.abs(music)) + 1e-9
    music *= 0.72 / mpeak

    # ducking por la voz
    lvl = np.abs(vo)
    denv = boxfilt(boxfilt(lvl, int(0.02 * SR)), int(0.12 * SR))
    denv = denv / (np.max(denv) + 1e-9)
    denv = np.clip(denv * 2.2, 0, 1)
    duck = 1.0 - 0.62 * denv
    duck = boxfilt(duck, int(0.05 * SR)).astype(np.float32)
    music *= duck

    mix = music + np.stack([vo * 0.92] * 2)
    # fades
    nf = int(0.4 * SR)
    mix[:, :nf] *= np.linspace(0, 1, nf) ** 1.2
    out_len = int(cfg.TOTAL * SR)
    mix = mix[:, :out_len]
    tail = int(1.6 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 1.6

    mix = np.tanh(mix * 1.05)
    mix *= 0.94 / (np.max(np.abs(mix)) + 1e-9)

    # guardar wav
    pcm = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open(os.path.join(cfg.BUILD, 'mix.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    # envelope de labios @60fps
    hop = 1.0 / cfg.FPS
    nf = int(cfg.TOTAL / hop)
    envl = np.zeros(nf, dtype=np.float32)
    wlen = int(0.045 * SR)
    for i in range(nf):
        c = int(i * hop * SR)
        seg = vo[max(0, c - wlen // 2): c + wlen // 2]
        envl[i] = np.mean(seg ** 2) ** 0.5 if len(seg) else 0.0
    envl = boxfilt(envl, 3)
    envl = envl / (np.percentile(envl[envl > 0.0005], 92) + 1e-9) if np.any(envl > 0.0005) else envl
    np.savez(os.path.join(cfg.BUILD, 'env.npz'), env=np.clip(envl, 0, 1.6), fps=cfg.FPS)

    # voz sola para referencia de sincronía
    np.save(os.path.join(cfg.BUILD, 'vo.npy'), vo)
    dur = len(mix[0]) / SR
    print('mezcla lista: %.2fs, pico %.2f' % (dur, np.max(np.abs(mix))))


if __name__ == '__main__':
    build()
