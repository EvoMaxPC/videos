"""Pass B: motion graphics, subtítulos, lab-sync y transiciones sobre el base 1080p60."""
import os, sys, math, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg
import overlays as O

FF = cfg.FF
W, H, FPS = cfg.W, cfg.H, cfg.FPS
C = cfg.C
MONO_S, MONO_M, MONO_L = cfg.F_MONO, cfg.F_MONO, cfg.F_MONO


def fnt(path, size):
    return O.font(path, size)


def ease(p):
    p = max(0.0, min(1.0, p))
    return (1 - math.cos(math.pi * p)) / 2


def clamp(v, a, b):
    return max(a, min(b, v))


def fade(t, t0, t1, fin=0.28, fout=0.28):
    if t < t0 or t > t1:
        return 0.0
    a = 1.0
    if t - t0 < fin:
        a = min(a, (t - t0) / fin)
    if t1 - t < fout:
        a = min(a, (t1 - t) / fout)
    return clamp(a, 0, 1)


def text(d, xy, s, size=32, fill=None, stroke=4, stroke_fill=(5, 8, 14), mono=False,
         tracking=0, anchor=None, bold=True):
    f = fnt(MONO_M if mono else (cfg.F_BOLD if bold else cfg.F_REG), size)
    if tracking:
        O.draw_tracked(d, xy, s, f, fill or C['white'], tracking=tracking,
                       anchor_center=(anchor == 'c'), stroke=stroke, stroke_fill=stroke_fill)
    else:
        d.text(xy, s, font=f, fill=fill or C['white'], stroke_width=stroke, stroke_fill=stroke_fill,
               anchor=anchor)


def tw(d, s, size=32, mono=False, tracking=0):
    f = fnt(MONO_M if mono else cfg.F_BOLD, size)
    return O.text_size(d, s, f, tracking)[0]


# ------------------------------------------------------------------ subtítulos
CAPTIONS = []


def build_captions():
    CAPTIONS.clear()
    for sc in cfg.SCENES:
        k = sc['key']
        words = O.word_times(cfg.VO_TEXT[k], sc['vo_start'], cfg.VO_DUR[k])
        for ch in O.chunks(words):
            txt = ' '.join(O.clean(w[0]) for w in ch)
            CAPTIONS.append(dict(t0=ch[0][1], t1=ch[-1][2], words=[w[0] for w in ch],
                                 text=txt, key=k))
    CAPTIONS.sort(key=lambda c: c['t0'])


def active_caption(t):
    for c in CAPTIONS:
        if c['t0'] - 0.05 <= t <= c['t1'] + 0.16:
            return c
    return None


def ov_caption(fr, d, t):
    c = active_caption(t)
    if not c:
        return
    if shot_at(t)[1]['fx'] in ('ep_cta', 'outro'):
        return
    words = [O.clean(w) for w in c['words']]
    hl = 0
    for i, w in enumerate(words):
        pass
    # índice resaltado según tiempo aproximado
    span = max(0.05, (c['t1'] - c['t0']))
    prog = clamp((t - c['t0']) / span, 0, 1)
    hl = min(len(words) - 1, int(prog * len(words)))
    layer = O.subtitle_layer(' '.join(words), hl)
    if layer.size[0] > W - 200:
        k = (W - 200) / layer.size[0]
        layer = layer.resize((int(layer.size[0] * k), int(layer.size[1] * k)), Image.LANCZOS)
    a = min(1.0, (t - c['t0'] + 0.05) * 6)
    y = H - 118 - layer.size[1] + int((1 - min(1.0, (t - c['t0']) * 5)) * 16)
    O.paste(fr, layer, ((W - layer.size[0]) // 2, y), a)
    # barrita ámbar
    d = ImageDraw.Draw(fr)
    x0 = (W - layer.size[0]) // 2 - 26
    d.rounded_rectangle([x0, y + 30, x0 + 6, y + layer.size[1] - 34], radius=3, fill=C['amber'])


# ------------------------------------------------------------------ capítulos
def ov_chapter(fr, d, t, scene):
    a = fade(t, scene['start'] + 0.15, scene['start'] + 3.6, 0.35, 0.6)
    if a <= 0.01:
        return
    num, title = cfg.CHAPTERS[scene['key']]
    x, y = 92, 78
    f1 = fnt(cfg.F_MONO, 30)
    d.text((x, y), num, font=f1, fill=C['amber'] + (255,), stroke_width=3, stroke_fill=(6, 9, 16))
    d.rounded_rectangle([x + 58, y + 15, x + 128, y + 18], radius=2,
                        fill=(255, 192, 30) if a > 0.6 else (110, 84, 20))
    f2 = fnt(cfg.F_BOLD, 30)
    O.draw_tracked(d, (x + 144, y - 2), title, f2, (240, 244, 252), tracking=3,
                   stroke=3, stroke_fill=(6, 9, 16))


def ov_brand(fr, d, t):
    a = 0.32
    f = fnt(cfg.F_MONO, 20)
    s = 'EVO LABS'
    d.text((W - 92 - tw(d, s, 20, mono=True), H - 58), s, font=f,
           fill=(190, 200, 215), stroke_width=2, stroke_fill=(6, 9, 16))
    d.ellipse([W - 74, H - 52, W - 64, H - 42], fill=C['amber'])


# ------------------------------------------------------------------ FX por plano
def ov_boot(fr, d, t, sh):
    p = t - sh['start']
    lines = ['$ evo@lab ~ init --mode cinematic',
             '> montando /agents ................ ok',
             '> cargando /ai-tools .............. ok',
             '> abriendo /bench ................. ok',
             '> ring --prepare .................. ok',
             '> sistemas en línea']
    shown = p / 0.30
    for i, ln in enumerate(lines):
        if i > shown:
            break
        txt = ln if i < int(shown) else ln[:max(1, int(len(ln) * ((shown - i))))]
        d.text((88, 168 + i * 40), txt, font=fnt(cfg.F_MONO, 24),
               fill=C['cyan'] if i % 2 else (150, 230, 245),
               stroke_width=3, stroke_fill=(4, 8, 14))
    # barra de arranque
    bp = clamp(p / 5.0, 0, 1)
    bx, by, bw = 88, 168 + 6 * 40 + 22, 520
    d.rounded_rectangle([bx, by, bx + bw, by + 8], radius=4, fill=(30, 44, 62))
    d.rounded_rectangle([bx, by, bx + bw * bp, by + 8], radius=4, fill=C['amber'])
    d.text((bx + bw + 18, by - 12), f'{int(bp * 100):03d}', font=fnt(cfg.F_MONO, 26),
           fill=C['amber'], stroke_width=3, stroke_fill=(4, 8, 14))
    if p > 3.4:
        ch = O.chip_layer('SISTEMAS EN LÍNEA', C['green'], 22)
        O.paste(fr, ch, (bx, by + 34), clamp((p - 3.4) * 2.2, 0, 1))


def ov_logo(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = clamp((p - 0.04) * 6, 0, 1)
    scale = 1.10 - 0.10 * ease(clamp(p * 2.6, 0, 1))
    gl = O.logo_image(1500)
    gw = int(gl.size[0] * scale)
    gh = int(gl.size[1] * scale)
    key = ('logo_scaled', int(gw / 6))
    gl2 = _scaled(gl, gw, gh, key)
    g = O.glow_layer(C['amber'], 900, 1.0)
    O.paste(fr, g, (W / 2 - 450, H / 2 - 470), 0.45 * a)
    O.paste(fr, gl2, ((W - gw) / 2, (H - gh) / 2 - 40), a)
    # barrido de scanline
    sxp = ease(p) * (W + 400) - 200
    d.line([(sxp, 0), (sxp + 120, H)], fill=(255, 235, 190), width=3)


_SCALED_CACHE = {}


def _scaled(img, w, h, key):
    k = (key, w, h)
    if k not in _SCALED_CACHE:
        _SCALED_CACHE[k] = img.resize((w, h), Image.LANCZOS)
    return _SCALED_CACHE[k]


def ov_hud(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.2, sh['end'] - 0.15, 0.3, 0.3)
    if a <= 0.02:
        return
    O.bracket(d, (74, 132, W - 74, H - 152), (34, 211, 238), 46, 3)
    # retícula
    cx, cy, r = W - 250, 300, 92
    for i in range(3):
        rr = r - i * 18
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 200 + 120 * math.sin(t * 1.3 + i),
              330 + 120 * math.sin(t * 1.1 + i), fill=(34, 211, 238), width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=C['amber'])
    # scanline horizontal
    sy = 150 + (math.sin(t * 0.9) * 0.5 + 0.5) * (H - 320)
    d.line([(90, sy), (W - 90, sy)], fill=(30, 120, 140), width=2)
    labels = ['AGENTES', 'IA LIBRE', 'BENCH', 'OPORTUNIDADES']
    for i, lb in enumerate(labels):
        ch = O.chip_layer(lb, [C['cyan'], C['amber'], C['green'], C['cyan']][i], 22)
        x = 110 + (i % 2) * 300
        y = H - 300 + (i // 2) * 62 + i * 10
        O.paste(fr, ch, (x, y), a * clamp((p * 6) - i * 0.8, 0, 1))


def ov_panels(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.15, sh['end'] - 0.1, 0.32, 0.3)
    if a <= 0.02:
        return
    if sh['id'].startswith('s6'):
        items = [((0.42, 0.30), 'MÉTODOS REALES', 'left'),
                 ((0.55, 0.62), 'AGENTES POTENTES', 'left'),
                 ((0.30, 0.78), 'SIN HUMO', 'right')]
    else:
        items = [((0.66, 0.26), 'AGENTES AUTÓNOMOS', 'right'),
                 ((0.74, 0.55), 'SOFTWARE LIBRE', 'right'),
                 ((0.55, 0.80), 'EXPERIMENTOS', 'left')]
    for i, ((nx, ny), label, side) in enumerate(items):
        ga = clamp((p * 5.5) - i * 1.1, 0, 1) * a
        if ga <= 0.02:
            continue
        px, py = int(nx * W), int(ny * H)
        ln = int(120 * ease(ga))
        if side == 'right':
            x0, y0 = px + 10, py
            d.line([(x0, y0), (x0 + ln, y0)], fill=C['amber'], width=2)
            d.line([(x0 + ln, y0), (x0 + ln + 22, y0 - 26)], fill=C['amber'], width=2)
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=C['amber'])
            ch = O.chip_layer(label, C['amber'], 22)
            O.paste(fr, ch, (x0 + ln + 26, y0 - 48), ga)
        else:
            x0, y0 = px - 10, py
            d.line([(x0, y0), (x0 - ln, y0)], fill=C['amber'], width=2)
            d.line([(x0 - ln, y0), (x0 - ln - 22, y0 - 26)], fill=C['amber'], width=2)
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=C['amber'])
            ch = O.chip_layer(label, C['amber'], 22)
            O.paste(fr, ch, (x0 - ln - 26 - ch.size[0], y0 - 48), ga)


def ov_ring(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.2, sh['end'] - 0.12, 0.3, 0.3)
    if a <= 0.02:
        return
    # marcador superior
    x0, y0, w0, h0 = W // 2 - 330, 120, 660, 208
    O.bracket(d, (x0, y0, x0 + w0, y0 + h0), (34, 211, 238), 30, 2)
    text(d, (x0 + 24, y0 + 14), 'RING DE AGENTES', 24, C['cyan'], tracking=3, mono=True)
    agents = ['AGENTE A', 'AGENTE B', 'AGENTE C', 'AGENTE D']
    for i, ag in enumerate(agents):
        yy = y0 + 58 + i * 34
        text(d, (x0 + 24, yy - 12), ag, 22, (225, 232, 242), mono=True, tracking=1)
        prog = 0.35 + 0.55 * abs(math.sin(t * 1.7 + i * 1.3)) * (0.6 + 0.4 * p)
        bw = 250
        d.rounded_rectangle([x0 + 190, yy - 8, x0 + 190 + bw, yy], radius=3, fill=(24, 34, 48))
        col = C['green'] if (i + int(t * 2)) % 3 else C['amber']
        d.rounded_rectangle([x0 + 190, yy - 8, x0 + 190 + bw * prog, yy], radius=3, fill=col)
    if p > 0.35:
        ch = O.chip_layer('MISMO OBJETIVO', C['amber'], 20)
        O.paste(fr, ch, (W // 2 - ch.size[0] // 2, y0 + h0 + 16), a)
    # chip de estado
    st = O.chip_layer('PASS' if math.sin(t * 3) > 0 else 'ALERTA',
                      C['green'] if math.sin(t * 3) > 0 else C['red'], 20)
    O.paste(fr, st, (W - 96 - st.size[0], 150), a)


def ov_bench(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.2, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    # gauge circular
    cx, cy, r = W - 300, H - 320, 110
    d.arc([cx - r, cy - r, cx + r, cy + r], 135, 405, fill=(40, 56, 74), width=12)
    val = 0.55 + 0.35 * math.sin(t * 0.9) * ease(p)
    d.arc([cx - r, cy - r, cx + r, cy + r], 135, 135 + 270 * val, fill=C['green'], width=12)
    text(d, (cx, cy - 16), 'OPTIMIZACIÓN', 20, (228, 234, 244), anchor='mm', mono=True, tracking=1)
    text(d, (cx, cy + 18), 'ESTABLE', 26, C['green'], anchor='mm')
    for i, lb in enumerate(['TEST REAL', 'PASS', 'SIN HUMO']):
        ch = O.chip_layer(lb, [C['cyan'], C['green'], C['amber']][i], 20)
        O.paste(fr, ch, (96, H - 430 + i * 58), a * clamp((p * 5) - i * 0.7, 0, 1))
    # osciloscopio
    x0, y0 = 96, H - 470
    pts = []
    for k in range(140):
        xx = x0 + k * 3.0
        yy = y0 + math.sin(k * 0.18 + t * 6) * 14 * (0.6 + 0.4 * math.sin(t))
        pts.append((xx, yy))
    d.line(pts, fill=C['cyan'], width=2)


def ov_talk(fr, d, t, sh, env):
    # glow ámbar reactivo a la voz
    a = 0.05 + 0.11 * clamp(env * 1.3, 0, 1)
    g = O.glow_layer(C['amber'], 820, 1.2)
    O.paste(fr, g, (-520, H - 860), a)
    O.paste(fr, g, (W - 300, -320), a * 0.9)
    # ecualizador mínimo
    if env > 0.06:
        for i in range(9):
            h = 10 + 54 * env * abs(math.sin(t * 7 + i * 0.9))
            x = 108 + i * 16
            d.rounded_rectangle([x, H - 210 - h, x + 8, H - 210], radius=4,
                                fill=C['amber'] if i % 3 else C['cyan'])


def ov_promise(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a1 = clamp((p - 0.02) * 5, 0, 1)
    a2 = clamp((p - 0.24) * 5, 0, 1)
    ch = O.chip_layer('PROMESA EVO LABS', C['amber'], 22)
    O.paste(fr, ch, (W // 2 - ch.size[0] // 2, 300), clamp(p * 6, 0, 1))
    f1 = fnt(cfg.F_BOLD, 78)
    s1 = 'NO VENDEMOS HUMO.'
    w1 = O.text_size(d, s1, f1, 4)[0]
    d.text((W / 2, 470), s1, font=f1, fill=(240, 244, 252), anchor='mm',
           stroke_width=7, stroke_fill=(6, 9, 16))
    # barrido rojo tachando "HUMO"
    if a2 > 0:
        hw = O.text_size(d, 'HUMO.', fnt(cfg.F_BOLD, 78))[0]
        x1 = W / 2 + w1 / 2
        d.line([(x1 - hw - 6, 470), (x1 - hw - 6 + hw * ease(a2), 470)], fill=C['red'], width=9)
    f2 = fnt(cfg.F_BOLD, 92)
    s2 = 'DEMOSTRAMOS RESULTADOS.'
    w2 = O.text_size(d, s2, f2, 3)[0]
    sc = 0.94 + 0.06 * ease(a2)
    if a2 > 0.02:
        layer = _text_layer(s2, f2, C['amber'], 8)
        lw, lh = int(layer.size[0] * sc), int(layer.size[1] * sc)
        l2 = _scaled(layer, lw, lh, ('promise2', lw // 8, lh // 8))
        O.paste(fr, l2, ((W - lw) / 2, 620 - lh / 2), a2)
        uw = int(w2 * ease(a2))
        d.rounded_rectangle([W / 2 - uw / 2, 700, W / 2 + uw / 2, 707], radius=3, fill=C['amber'])


@functools.lru_cache(maxsize=64)
def _text_spaced(s, f, color, stroke, tracking=3):
    tmp = Image.new('RGBA', (10, 10))
    d = ImageDraw.Draw(tmp)
    w, h = O.text_size(d, s, f, tracking)
    img = Image.new('RGBA', (int(w) + stroke * 2 + 6, int(h) + stroke * 2 + 10), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    O.draw_tracked(dd, (stroke + 3, stroke), s, f, color + (255,), tracking=tracking,
                   stroke=stroke, stroke_fill=(6, 9, 16, 255))
    return img


@functools.lru_cache(maxsize=64)
def _text_layer(s, f, color, stroke):
    tmp = Image.new('RGBA', (10, 10))
    d = ImageDraw.Draw(tmp)
    w, h = O.text_size(d, s, f)
    img = Image.new('RGBA', (int(w) + stroke * 2 + 6, int(h) + stroke * 2 + 10), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    dd.text((stroke + 3, stroke), s, font=f, fill=color + (255,), stroke_width=stroke,
            stroke_fill=(6, 9, 16, 255))
    return img


def ov_split(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.1, sh['end'] - 0.1, 0.3, 0.3)
    ch = O.chip_layer('PROMESA FÁCIL', C['red'], 22)
    O.paste(fr, ch, (120, 300), a * clamp(p * 5, 0, 1))
    ch2 = O.chip_layer('RESULTADO REAL', C['green'], 22)
    O.paste(fr, ch2, (W - 120 - ch2.size[0], 300), a * clamp(p * 5 - 0.8, 0, 1))
    # VS
    r = 66 + 6 * math.sin(t * 4)
    d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=C['amber'], width=4)
    text(d, (W / 2, H / 2), 'VS', 46, C['amber'], anchor='mm', stroke=5)
    # línea divisoria animada
    y0 = 200
    y1 = 200 + (H - 400) * ease(clamp(p * 2.2, 0, 1))
    d.line([(W / 2, y0), (W / 2, y1)], fill=C['amber'], width=3)


def ov_fake(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'], sh['end'] - 0.05, 0.15, 0.2)
    # tinte rojo
    red = Image.new('RGB', (W, H), (70, 6, 10))
    fr.paste(Image.blend(fr, red, 0.28 * a), (0, 0))
    d = ImageDraw.Draw(fr)
    # glitch bars
    for i in range(6):
        yy = int((math.sin(t * 9 + i * 2.1) * 0.5 + 0.5) * H)
        hh = int(6 + 14 * abs(math.sin(t * 13 + i)))
        d.rectangle([0, yy, W, yy + hh], fill=[(10, 60, 70), (80, 12, 18), (12, 14, 22)][i % 3])
    # X roja
    cx, cy, r = W - 400, 380, 150
    for k in range(2):
        s = -1 if k else 1
        d.line([(cx - r, cy - s * r), (cx + r, cy + s * r)], fill=C['red'], width=26)
    ch = O.chip_layer('HUMO', C['red'], 26)
    O.paste(fr, ch, (96, H - 250), a)
    ch2 = O.chip_layer('SIN PRUEBAS', C['red'], 20)
    O.paste(fr, ch2, (96, H - 190), a)


def ov_real(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'], sh['end'] - 0.05, 0.2, 0.3)
    gr = O.chip_layer('MEDIDO · REPETIBLE', C['green'], 22)
    O.paste(fr, gr, (96, H - 250), a)
    # check verde
    cx, cy, r = W - 330, 300, 74
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C['green'], width=6)
    d.line([(cx - 30, cy + 2), (cx - 8, cy + 26), (cx + 34, cy - 26)], fill=C['green'], width=10)
    # barras honestas
    x0, y0 = 130, H - 330
    for i in range(6):
        hh = 30 + 90 * abs(math.sin(t * 0.8 + i * 0.6))
        d.rounded_rectangle([x0 + i * 34, y0 - hh, x0 + i * 34 + 22, y0], radius=4,
                            fill=C['green'] if i % 3 else C['cyan'])


def ov_final(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    # rayos de luz
    for i in range(9):
        ang = -0.9 + i * 0.22 + math.sin(t * 0.6 + i) * 0.02
        x2 = W / 2 + math.tan(ang) * H * 1.1
        d.line([(W / 2, H * 0.62), (x2, -H * 0.1)], fill=(255, 210, 120), width=2)
    g = O.glow_layer(C['amber'], 900, 1.0)
    O.paste(fr, g, (W / 2 - 450, H / 2 - 480), 0.35 + 0.25 * math.sin(t * 2))


def ov_outro(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = clamp(p * 3.2, 0, 1)
    gl = O.logo_image(1120)
    O.paste(fr, gl, ((W - gl.size[0]) / 2, 120), a)
    # tagline
    f = fnt(cfg.F_BOLD, 58)
    s2 = 'NO LO CREAS. COMPROBALO.'
    layer = _text_spaced(s2, f, C['amber'], 6, 3)
    O.paste(fr, layer, ((W - layer.size[0]) / 2, 452), clamp((p - 0.12) * 4, 0, 1))
    # botón de suscripción
    bw, bh = 400, 96
    bx, by = W / 2 - bw / 2, 588
    pulse = 0.5 + 0.5 * math.sin(t * 3.4)
    d.rounded_rectangle([bx - 6 - pulse * 6, by - 6 - pulse * 6, bx + bw + 6 + pulse * 6, by + bh + 6 + pulse * 6],
                        radius=22, outline=(255, 60, 60), width=2)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(214, 40, 40),
                        outline=(255, 255, 255), width=3)
    # play icon
    d.polygon([(bx + 54, by + 30), (bx + 54, by + 74), (bx + 96, by + 52)], fill=(255, 255, 255))
    text(d, (bx + 116, by + 18), 'SUSCRIBITE', 40, (255, 255, 255), stroke=2)
    # cursor
    ca = clamp((p - 0.30) * 6, 0, 1)
    if ca > 0:
        px = bx + bw * 0.62 + math.sin(t * 2) * 6
        py = by + bh * 0.55 + math.cos(t * 2.4) * 5
        click = clamp((p - 0.52) * 8, 0, 1) * clamp((0.75 - p) * 8, 0, 1)
        if click > 0:
            r = 30 + 40 * click
            d.arc([px - r, py - r, px + r, py + r], 0, 360, fill=(255, 235, 170), width=3)
        cur = [(px, py), (px + 4, py + 34), (px + 12, py + 26), (px + 18, py + 42),
               (px + 26, py + 38), (px + 20, py + 22), (px + 30, py + 20)]
        d.polygon(cur, fill=(255, 255, 255), outline=(10, 12, 20))
    # línea inferior
    text(d, (W / 2, by + bh + 56), 'ACTIVÁ LAS NOTIFICACIONES', 26,
         (235, 240, 250), anchor='mm', tracking=5, mono=True, stroke=3)


# ------------------------------------------------------------------ partículas
@functools.lru_cache(maxsize=4)
def mote(color=(255, 200, 110), size=26):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(8, 0, -1):
        r = size * 0.5 * i / 8
        a = int(70 / i)
        d.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], fill=color + (a,))
    return img.filter(ImageFilter.GaussianBlur(1.5))


def ov_particles(fr, t, sh):
    rng = np.random.default_rng(abs(hash(sh['id'])) % 9999)
    n = 26
    for i in range(n):
        bx = rng.uniform(0, 1)
        by = rng.uniform(0, 1)
        sp = rng.uniform(0.01, 0.05)
        ph = rng.uniform(0, 6.28)
        x = (bx * W + math.sin(t * 0.6 + ph) * 40) % W
        y = (by * H - (t - sh['start']) * sp * H * 0.6) % H
        a = 0.35 + 0.35 * math.sin(t * 2 + ph)
        col = (255, 205, 120) if i % 3 else (90, 225, 245)
        m = mote(col)
        O.paste(fr, m, (x, y), clamp(a, 0, 1) * 0.5)


# ------------------------------------------------------------------ transiciones
CUTS = []        # [(frame_inicio, tipo, nframes)]
CUT_F = {}       # frame_inicio -> (tipo, nframes)


def build_cuts():
    """Cortes en frames reales: misma acumulación que segments.py."""
    CUTS.clear(); CUT_F.clear()
    cum = 0
    for j, sh in enumerate(cfg.SHOTS):
        dur = sh.get('end', sh['start'] + sh['dur']) - sh.get('start', 0.0)
        nf = max(2, int(round(dur * FPS)))
        if j > 0:
            kind, tn = cfg.TRANSITIONS.get(sh['id'], ('dissolve', 6))
            if kind != 'none' and tn > 0 and nf > tn + 2:
                CUTS.append((cum, kind, int(tn)))
                CUT_F[cum] = (kind, int(tn))
        cum += nf
    return CUTS


def _punch(fr, k, amt=0.035):
    s = 1.0 + amt * (1 - k) ** 1.5
    if s <= 1.001:
        return fr
    w, h = int(W * s), int(H * s)
    im = fr.resize((w, h), Image.BILINEAR)
    x0, y0 = (w - W) // 2, (h - H) // 2
    return im.crop((x0, y0, x0 + W, y0 + H))


def _shift(fr, dx):
    return fr.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, 0), resample=Image.BILINEAR)


def _whip(fr, k, last_pre=None):
    dz = (1 - k) ** 1.3
    dx = dz * 0.085 * W
    in_img = _shift(fr, dx * 0.55)
    out_img = _shift(last_pre, -dx * 0.55) if last_pre is not None else _shift(fr, -dx * 0.55)
    res = Image.blend(out_img, in_img, 0.18 + 0.82 * k)
    if dx > 4:
        res = Image.blend(res, _shift(in_img, -dx * 0.25), 0.30 * dz)
    return res


def _glitch(fr, k):
    r, g, b = fr.split()
    sh = 10 * k
    r = r.transform((W, H), Image.AFFINE, (1, 0, -sh, 0, 1, 0), resample=Image.BILINEAR)
    b = b.transform((W, H), Image.AFFINE, (1, 0, sh, 0, 1, 0), resample=Image.BILINEAR)
    fr = Image.merge('RGB', (r, g, b))
    for i in range(3):
        yy = int((0.18 + 0.26 * i) * H + 30 * math.sin(k * 18 + i * 2))
        hh = int(12 + 26 * abs(math.sin(k * 9 + i)))
        yy = max(0, min(H - hh - 1, yy))
        dx = int(70 * k * (1 if i % 2 else -1))
        band = fr.crop((0, yy, W, yy + hh)).transform((W, hh), Image.AFFINE, (1, 0, -dx, 0, 1, 0))
        fr.paste(band, (0, yy))
    return fr


def apply_transition(fr, i, last_pre):
    for (f0, kind, nf) in CUTS:
        if f0 <= i < f0 + nf:
            k = (i - f0) / nf
            if kind == 'dissolve':
                if last_pre is not None:
                    fr = Image.blend(last_pre, fr, 0.18 + 0.82 * k)
            elif kind == 'flash':
                if last_pre is not None:
                    fr = Image.blend(last_pre, fr, 0.25 + 0.75 * k)
                fr = _punch(fr, k, 0.030)
                fr = Image.blend(fr, Image.new('RGB', (W, H), (255, 238, 208)), (1 - k) ** 2 * 0.34)
            elif kind == 'whip':
                pre = _punch(fr, 0.0, 0.16)
                lp = _punch(last_pre, 0.0, 0.16) if last_pre is not None else None
                fr = _whip(pre, k, lp)
            elif kind == 'glitch':
                fr = _glitch(fr, k)
            return fr
    return fr


def ov_cut(fr, d, t):
    best = None
    for i, sh in enumerate(cfg.SHOTS):
        if i == 0:
            continue
        dt = t - sh['start']
        if -0.16 < dt < 0.16:
            best = (sh, dt)
            break
    if not best:
        return
    sh, dt = best
    k = 1 - abs(dt) / 0.16
    if sh['fx'] in ('ring', 'fake', 'real', 'split'):
        for i in range(4):
            yy = int(((math.sin(dt * 60 + i * 1.7) * 0.5 + 0.5)) * H)
            d.rectangle([0, yy, W, yy + 3], fill=(255, 255, 255))
        fr.paste(Image.blend(fr, Image.new('RGB', (W, H), (200, 230, 255)), 0.18 * k), (0, 0))
    else:
        fr.paste(Image.blend(fr, Image.new('RGB', (W, H), (255, 235, 200)), 0.55 * k), (0, 0))


# ------------------------------------------------------------------ mouth / lab-sync
@functools.lru_cache(maxsize=64)
def mouth_masks(rx, ry):
    Wm, Hm = rx * 2, ry * 2
    m = Image.new('L', (Wm, Hm), 0)
    ImageDraw.Draw(m).ellipse([0, 0, Wm - 1, Hm - 1], fill=255)
    return m.filter(ImageFilter.GaussianBlur(max(2, rx * 0.16)))


_MOUTH_CACHE = {}


def mouth_sprite(mw2, oh2, openness):
    mw2 = max(6, int(mw2))
    oh2 = max(4, int(oh2))
    key = (mw2, oh2, int(openness * 8))
    if key in _MOUTH_CACHE:
        return _MOUTH_CACHE[key]
    w = mw2 * 2 + 6
    h = int(oh2 * 1.55) + 6
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = [3, 3, w - 4, h - 4]
    d.ellipse(box, fill=(24, 30, 48, 255), outline=(24, 30, 48, 255), width=3)
    cav = img.getchannel('A')
    # dientes
    teeth = Image.new('L', (w, h), 0)
    if openness > 0.20:
        ImageDraw.Draw(teeth).ellipse([box[0] + mw2 * 0.16, box[1] + oh2 * 0.02,
                                       box[2] - mw2 * 0.16, box[1] + oh2 * 0.40], fill=255)
    import PIL.ImageChops as IC
    tm = IC.multiply(teeth, cav)
    img.paste(Image.new('RGBA', (w, h), (250, 248, 242, 255)), (0, 0), tm)
    # lengua
    if openness > 0.35:
        t = Image.new('L', (w, h), 0)
        ImageDraw.Draw(t).ellipse([box[0] + mw2 * 0.34, box[3] - oh2 * 0.34,
                                   box[2] - mw2 * 0.34, box[3] + oh2 * 0.22], fill=255)
        tm2 = IC.multiply(t, cav)
        img.paste(Image.new('RGBA', (w, h), (190, 80, 92, 255)), (0, 0), tm2)
    _MOUTH_CACHE[key] = img
    return img


def apply_mouth(fr, sh, z, X, Y, env):
    """Abre la boca por debajo de la línea de la sonrisa existente."""
    mouth = sh.get('mouth')
    if not mouth:
        return
    mx, my, mw, mh = mouth
    s = 2160.0 / 768.0
    sx = mx * s - 15.0
    sy = my * s
    ox = (sx - X) * 0.5 * z
    oy = (sy - Y) * 0.5 * z
    ow = mw * s * 0.5 * z
    if ow < 10:
        return
    openness = clamp(env * 1.05, 0, 0.95)
    if openness < 0.06:
        return
    mw2 = ow * 0.44
    oh2 = ow * 0.02 + openness * ow * 0.225
    spr = mouth_sprite(mw2, oh2, openness)
    fr.paste(spr, (int(ox - spr.size[0] / 2), int(oy - oh2 * 0.22)), spr)


# ------------------------------------------------------------------ render
def cam_state(sh, t):
    p = clamp((t - sh['start']) / sh['dur'], 0, 1)
    e = ease(p)
    z0, z1, (fx0, fy0), (fx1, fy1) = sh['cam']
    z = z0 + (z1 - z0) * e
    fx = fx0 + (fx1 - fx0) * e
    fy = fy0 + (fy1 - fy0) * e
    iw, ih = 3840.0, 2160.0
    X = clamp(fx * iw - iw / (2 * z), 0, iw - iw / z)
    Y = clamp(fy * ih - ih / (2 * z), 0, ih - ih / z)
    return z, X, Y


def shot_at(t):
    for i, sh in enumerate(cfg.SHOTS):
        if sh['start'] <= t < sh['end']:
            return i, sh
    return len(cfg.SHOTS) - 1, cfg.SHOTS[-1]


def scene_at(t):
    for sc in cfg.SCENES:
        if sc['start'] <= t < sc['end']:
            return sc
    return cfg.SCENES[-1]


def process_frame(fr, t, e):
    shi, sh = shot_at(t)
    sc = scene_at(t)
    z, X, Y = cam_state(sh, t)
    d = ImageDraw.Draw(fr)
    if sh.get('mouth') and cfg.ANIM_MOUTH:
        apply_mouth(fr, sh, z, X, Y, e)
    if sh['fx'] not in ('logo', 'promise', 'outro', 'split'):
        ov_particles(fr, t, sh)
        d = ImageDraw.Draw(fr)
    fx = sh['fx']
    if fx == 'boot':
        ov_boot(fr, d, t, sh)
    elif fx == 'logo':
        ov_logo(fr, d, t, sh)
    elif fx == 'hud':
        ov_hud(fr, d, t, sh)
    elif fx == 'panels':
        ov_panels(fr, d, t, sh)
    elif fx == 'ring':
        ov_ring(fr, d, t, sh)
    elif fx == 'bench':
        ov_bench(fr, d, t, sh)
    elif fx == 'talk':
        ov_talk(fr, d, t, sh, e)
    elif fx == 'promise':
        ov_promise(fr, d, t, sh)
    elif fx == 'split':
        ov_split(fr, d, t, sh)
    elif fx == 'fake':
        ov_fake(fr, d, t, sh)
        d = ImageDraw.Draw(fr)
    elif fx == 'real':
        ov_real(fr, d, t, sh)
    elif fx == 'final':
        ov_final(fr, d, t, sh)
    elif fx == 'outro':
        ov_outro(fr, d, t, sh)
    elif fx.startswith('ep_'):
        import ep_fx
        ep_fx.render(fx, fr, d, t, sh, e)
    ov_chapter(fr, d, t, sc)
    ov_brand(fr, d, t)
    if not CUTS:
        ov_cut(fr, d, t)
    ov_caption(fr, d, t)
    if t < 1.7:
        if t < 0.25:
            fr = ImageEnhance.Brightness(fr).enhance(t / 0.25 * 0.15)
        elif t < 1.1:
            k = 0.15 + 0.85 * ease((t - 0.25) / 0.85)
            flick = 1.0 if (math.sin(t * 47) > -0.3) else 0.55
            fr = ImageEnhance.Brightness(fr).enhance(k * flick)
        else:
            fr = ImageEnhance.Brightness(fr).enhance(1.0 - 0.1 * (1.7 - t) / 0.6)
    if t > cfg.TOTAL - 1.5:
        fr = ImageEnhance.Brightness(fr).enhance(max(0.0, (cfg.TOTAL - t) / 1.5))
    return fr


def render(out_path, limit=None, start=0.0, t_to=None):
    build_captions()
    env = np.load(os.path.join(cfg.BUILD, 'env.npz'))['env']
    base = os.path.join(cfg.BUILD, 'base.mp4')
    i0 = int(start * FPS)
    nframes = int((t_to if t_to else cfg.TOTAL) * FPS)
    if limit:
        nframes = min(nframes, limit)
    dec = subprocess.Popen([FF, '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-r', str(FPS), '-'], stdout=subprocess.PIPE, bufsize=10 ** 8)
    mix = os.path.join(cfg.BUILD, 'mix.wav')
    enc = subprocess.Popen([FF, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{i0 / FPS:.3f}', '-i', mix,
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '25',
                            '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '120',
                            '-af', 'volume=2.4dB,alimiter=limit=0.79:attack=1:release=80:level=false',
                            '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                            '-movflags', '+faststart', '-shortest', '-t', f'{(nframes - i0) / FPS:.3f}', out_path],
                           stdin=subprocess.PIPE, bufsize=10 ** 8)
    size = W * H * 3
    build_cuts()
    last_pre = None
    for i in range(nframes):
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        if i < i0:
            continue
        t = i / FPS
        fr = Image.frombytes('RGB', (W, H), buf)
        if (i + 1) in CUT_F:
            last_pre = fr.copy()
        fr = apply_transition(fr, i, last_pre)
        e = float(env[min(i, len(env) - 1)])
        fr = process_frame(fr, t, e)
        enc.stdin.write(fr.tobytes())
        if (i - i0) % 600 == 0:
            print(f'  frame {i}/{nframes} t={t:.1f}s', flush=True)
    dec.stdout.close()
    dec.wait()
    enc.stdin.close()
    enc.wait()
    print('render ok:', out_path)


def write_srt(path):
    build_captions()
    def fmt(x):
        hh = int(x // 3600); mm = int(x % 3600 // 60); ss = int(x % 60)
        ms = int(round((x - int(x)) * 1000))
        return f'{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}'
    with open(path, 'w', encoding='utf-8') as f:
        for i, c in enumerate(CAPTIONS, 1):
            end = c['t1'] + 0.10
            if i < len(CAPTIONS):
                end = min(end, CAPTIONS[i]['t0'] - 0.02)
            f.write(f'{i}\n{fmt(c["t0"])} --> {fmt(max(end, c["t0"] + 0.4))}\n{c["text"]}\n\n')


if __name__ == '__main__':
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    out = os.path.join(cfg.ROOT, cfg.OUT_VIDEO)
    t_from = float(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 0.0
    t_to = float(sys.argv[sys.argv.index('--to') + 1]) if '--to' in sys.argv else None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    render(out, limit, t_from, t_to)
    if '--out' in sys.argv:
        sys.exit(0)
    write_srt(os.path.join(cfg.ROOT, cfg.OUT_VIDEO.replace('.mp4', '.srt')))
