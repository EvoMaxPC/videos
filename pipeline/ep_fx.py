"""Motion graphics del EP.01 (optimización real de Windows)."""
import os, sys, math, functools
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg
import overlays as O

W, H = cfg.W, cfg.H
C = cfg.C


def fnt(size, mono=False):
    return O.font(cfg.F_MONO if mono else cfg.F_BOLD, size)


def txt(d, xy, s, size=30, fill=None, stroke=4, mono=False, tracking=0, anchor=None):
    f = fnt(size, mono)
    if tracking:
        O.draw_tracked(d, xy, s, f, fill or C['white'], tracking=tracking,
                       anchor_center=(anchor == 'c'), stroke=stroke, stroke_fill=(5, 8, 14))
    else:
        d.text(xy, s, font=f, fill=fill or C['white'], stroke_width=stroke,
               stroke_fill=(5, 8, 14), anchor=anchor)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(p):
    p = clamp(p)
    return (1 - math.cos(math.pi * p)) / 2


def fade(t, t0, t1, fin=0.3, fout=0.3):
    if t < t0 or t > t1:
        return 0.0
    a = 1.0
    if t - t0 < fin:
        a = min(a, (t - t0) / fin)
    if t1 - t < fout:
        a = min(a, (t1 - t) / fout)
    return clamp(a)


@functools.lru_cache(maxsize=64)
def layer_text(s, size, color, stroke=5, tracking=0):
    probe = ImageDraw.Draw(Image.new('L', (10, 10)))
    f = fnt(size)
    w, h = O.text_size(probe, s, f, tracking)
    img = Image.new('RGBA', (int(w) + stroke * 2 + 8, int(h) + stroke * 2 + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tracking:
        O.draw_tracked(d, (stroke + 4, stroke), s, f, color + (255,), tracking=tracking,
                       stroke=stroke, stroke_fill=(5, 8, 14, 255))
    else:
        d.text((stroke + 4, stroke), s, font=f, fill=color + (255,),
               stroke_width=stroke, stroke_fill=(5, 8, 14, 255))
    return img


def panel(fr, box, alpha=0.55, color=(6, 10, 18), radius=10):
    lay = Image.new('RGBA', (int(box[2] - box[0]), int(box[3] - box[1])), color + (int(255 * alpha),))
    mask = Image.new('L', lay.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, lay.size[0] - 1, lay.size[1] - 1], radius=radius, fill=255)
    fr.paste(lay, (int(box[0]), int(box[1])), mask)


def pill(d, x, y, label, on=True, color=None):
    color = color or (C['green'] if on else (110, 120, 136))
    d.rounded_rectangle([x, y, x + 62, y + 26], radius=13, fill=(14, 20, 32), outline=color, width=2)
    d.ellipse([x + (34 if on else 4), y + 5, x + (58 if on else 28), y + 21], fill=color)


# ---------------------------------------------------------------- capas
def fx_boot(fr, d, t, sh):
    p = t - sh['start']
    lines = [f'$ evo@lab ~ run ep01 --windows-optimization',
             '> cargando módulo /bench ......... ok',
             '> montando /telemetry ............ ok',
             '> verificando pruebas ............ ok',
             '> listo para medir']
    shown = p / 0.26
    for i, ln in enumerate(lines):
        if i > shown:
            break
        out = ln if i < int(shown) else ln[:max(1, int(len(ln) * (shown - i)))]
        txt(d, (86, 150 + i * 38), out, 23, C['cyan'] if i % 2 else (150, 230, 245), 3, mono=True)
    bp = clamp(p / 2.2)
    bx, by = 86, 150 + 5 * 38 + 20
    d.rounded_rectangle([bx, by, bx + 420, by + 7], radius=4, fill=(28, 42, 60))
    d.rounded_rectangle([bx, by, bx + 420 * bp, by + 7], radius=4, fill=C['amber'])
    ch = O.chip_layer('EP.01 · OPTIMIZACIÓN REAL', C['amber'], 21)
    O.paste(fr, ch, (86, by + 34), clamp(p * 1.4))


def fx_logo(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = clamp((p - 0.03) * 6)
    scale = 1.09 - 0.09 * ease(clamp(p * 2.6))
    gl = O.logo_image(1500)
    gw, gh = int(gl.size[0] * scale), int(gl.size[1] * scale)
    key = ('ep_logo', gw // 6)
    g2 = O._scaled(gl, gw, gh, key) if hasattr(O, '_scaled') else gl.resize((gw, gh), Image.LANCZOS)
    g = O.glow_layer(C['amber'], 900, 1.0)
    O.paste(fr, g, (W / 2 - 450, H / 2 - 470), 0.45 * a)
    O.paste(fr, g2, ((W - gw) / 2, (H - gh) / 2 - 60), a)
    ch = O.chip_layer('EP.01 · OPTIMIZACIÓN REAL DE WINDOWS', C['amber'], 24)
    O.paste(fr, ch, ((W - ch.size[0]) / 2, H / 2 + 190), clamp((p - 0.25) * 4))
    sx = ease(p) * (W + 300) - 150
    d.line([(sx, 0), (sx + 110, H)], fill=(255, 238, 200), width=3)


def fx_talk(fr, d, t, sh, env):
    a = 0.045 + 0.10 * clamp(env * 1.3)
    g = O.glow_layer(C['amber'], 820, 1.2)
    O.paste(fr, g, (-520, H - 860), a)
    O.paste(fr, g, (W - 300, -320), a * 0.9)
    if env > 0.06:
        for i in range(9):
            h = 10 + 52 * env * abs(math.sin(t * 7 + i * 0.9))
            x = 108 + i * 16
            d.rounded_rectangle([x, H - 212 - h, x + 8, H - 212], radius=4,
                                fill=C['amber'] if i % 3 else C['cyan'])


def fx_fake(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'], sh['end'] - 0.04, 0.16, 0.22)
    red = Image.new('RGB', (W, H), (72, 6, 10))
    fr.paste(Image.blend(fr, red, 0.26 * a), (0, 0))
    d = ImageDraw.Draw(fr)
    for i in range(5):
        yy = int((math.sin(t * 8.5 + i * 2.1) * 0.5 + 0.5) * H)
        hh = int(6 + 12 * abs(math.sin(t * 12 + i)))
        d.rectangle([0, yy, W, yy + hh], fill=[(10, 60, 70), (86, 10, 16), (12, 14, 22)][i % 3])
    # sello 999 FPS tachado
    lay = layer_text('999 FPS', 92, C['red'], 7)
    O.paste(fr, lay, ((W - lay.size[0]) / 2, 210), a)
    d.line([(W / 2 - lay.size[0] * 0.42, 268), (W / 2 + lay.size[0] * 0.42, 268)],
           fill=C['red'], width=10)
    c1 = O.chip_layer('TÍTULO QUE PROMETE', C['red'], 22)
    O.paste(fr, c1, (110, H - 250), a)
    c2 = O.chip_layer('SIN PRUEBAS', C['red'], 20)
    O.paste(fr, c2, (110, H - 190), a)


def fx_ab(fr, d, t, sh):
    a = fade(t, sh['start'] + 0.15, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    ch = O.chip_layer('A · SIN CAMBIOS', (150, 160, 180), 22)
    O.paste(fr, ch, (110, 170), a)
    ch2 = O.chip_layer('B · OPTIMIZADO', C['amber'], 22)
    O.paste(fr, ch2, (W - 110 - ch2.size[0], 170), a)
    ch3 = O.chip_layer('MISMO HARDWARE · MISMAS PRUEBAS', C['cyan'], 19)
    O.paste(fr, ch3, ((W - ch3.size[0]) / 2, H - 260), a)
    # frametime
    for side, col, off in ((0, (150, 160, 180), 150), (1, C['green'], W / 2 + 110)):
        pts = []
        for k in range(120):
            x = off + k * 3.2
            y = H - 360 + math.sin(k * 0.13 + t * 1.6 + side) * (16 if side == 0 else 7)
            pts.append((x, y))
        d.line(pts, fill=col, width=2)


def fx_formula(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    stages = ['01 · LECTURA', '02 · AJUSTE', '03 · PRUEBA', '04 · ESTABILIDAD']
    for i, s in enumerate(stages):
        ga = clamp(p * 4.2 - i * 0.9)
        if ga <= 0.02:
            continue
        x = 210 + i * 400
        y = 150
        ch = O.chip_layer(s, C['amber'] if i % 2 == 0 else C['cyan'], 21)
        O.paste(fr, ch, (x, y), ga)
        if i < 3:
            x0 = x + ch.size[0] + 12
            d.line([(x0, y + 20), (x0 + 60 * ease(ga), y + 20)], fill=C['amber'], width=3)
            d.polygon([(x0 + 60 * ease(ga), y + 20), (x0 + 48 * ease(ga), y + 14),
                       (x0 + 48 * ease(ga), y + 26)], fill=C['amber'])
    et = O.chip_layer('MÉTODO ADAPTATIVO · NO SON PASOS SUELTOS', C['green'], 20)
    O.paste(fr, et, ((W - et.size[0]) / 2, H - 250), fade(t, sh['start'] + 0.3, sh['end'] - 0.1, .4, .3))


def fx_quote(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a1 = clamp((p - 0.02) * 5)
    a2 = clamp((p - 0.22) * 5)
    ch = O.chip_layer('REGLA Nº1 DE EVO LABS', C['amber'], 21)
    O.paste(fr, ch, ((W - ch.size[0]) / 2, 300), clamp(p * 6))
    l1 = layer_text('ACÁ HACEMOS MILAGROS,', 76, (242, 246, 252), 7)
    O.paste(fr, l1, ((W - l1.size[0]) / 2, 420), a1)
    l2 = layer_text('PERO LOS COMPROBAMOS.', 84, C['amber'], 8)
    sc = 0.95 + 0.05 * ease(a2)
    l2s = l2.resize((int(l2.size[0] * sc), int(l2.size[1] * sc)), Image.LANCZOS)
    O.paste(fr, l2s, ((W - l2s.size[0]) / 2, 540), a2)
    uw = int(l2.size[0] * ease(a2))
    d.rounded_rectangle([(W - uw) / 2, 668, (W + uw) / 2, 675], radius=3, fill=C['amber'])


CMDS = ['$ powercfg /list',
        '$ Get-CimInstance Win32_StartupCommand',
        '$ Get-Service DiagTrack, SysMain, WSearch',
        '$ dism /online /cleanup-image /analyzecomponentstore',
        '$ Measure-Command { .\\bench.ps1 }']


def fx_term(fr, d, t, sh):
    p = t - sh['start']
    a = fade(t, sh['start'] + 0.05, sh['end'] - 0.08, 0.25, 0.25)
    if a <= 0.02:
        return
    box = (150, 210, W - 150, 620)
    panel(fr, box, 0.72, (5, 9, 16), 12)
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([box[0], box[1], box[2], box[1] + 44], radius=12, fill=(16, 24, 38))
    for i, col in enumerate([(239, 68, 68), (255, 192, 30), (52, 211, 110)]):
        d.ellipse([box[0] + 18 + i * 26, box[1] + 16, box[0] + 32 + i * 26, box[1] + 30], fill=col)
    txt(d, (box[0] + 110, box[1] + 11), 'powershell — evo lab', 20, (150, 190, 205), 0, mono=True)
    shown = p / 0.42
    for i, cmd in enumerate(CMDS):
        if i > shown:
            break
        out = cmd if i < int(shown) else cmd[:max(1, int(len(cmd) * (shown - i)))]
        y = box[1] + 70 + i * 46
        txt(d, (box[0] + 34, y), out, 25, C['cyan'] if i % 2 == 0 else (168, 235, 245), 2, mono=True)
    ch = O.chip_layer('EJEMPLO REAL · SIN MAGIA', C['green'], 20)
    O.paste(fr, ch, (box[0], box[3] + 22), a)


def fx_meter(fr, d, t, sh):
    a = fade(t, sh['start'] + 0.1, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    x, y, w, h = 110, 170, 470, 300
    panel(fr, (x, y, x + w, y + h), 0.62, (6, 10, 18), 12)
    d.rectangle([x, y, x + w, y + 40], fill=(14, 22, 36))
    txt(d, (x + 18, y + 9), 'TELEMETRÍA · EN VIVO', 19, C['cyan'], 2, mono=True)
    d.ellipse([x + w - 32, y + 15, x + w - 20, y + 27], fill=C['red'])
    rows = [('CPU', 0.42, C['cyan']), ('RAM', 0.55, C['amber']), ('GPU', 0.38, C['cyan']),
            ('TEMP', 0.61, C['green'])]
    for i, (lb, base, col) in enumerate(rows):
        yy = y + 62 + i * 56
        txt(d, (x + 18, yy), lb, 20, (210, 220, 235), 2, mono=True)
        val = clamp(base + 0.18 * math.sin(t * 1.7 + i * 1.3))
        d.rounded_rectangle([x + 88, yy + 4, x + 88 + 320, yy + 18], radius=6, fill=(24, 34, 50))
        d.rounded_rectangle([x + 88, yy + 4, x + 88 + 320 * val, yy + 18], radius=6, fill=col)
        for k in range(8):
            xx = x + 88 + k * 40
            d.line([(xx, yy + 4), (xx, yy + 18)], fill=(10, 14, 22), width=2)
    txt(d, (x + 18, y + h - 26), 'sin datos inventados: se mide, se repite, se compara', 15,
        (140, 165, 185), 0, mono=True)
    pts = [(W - 620 + k * 4.0, H - 300 + math.sin(k * 0.22 + t * 2) * 26) for k in range(120)]
    d.line(pts, fill=C['green'], width=2)


SERVICES = [('SysMain', 0.35, True), ('Search (WSearch)', 0.62, False),
            ('DiagTrack · telemetría', 0.95, False), ('Xbox Game Bar', 0.55, True),
            ('Windows Update', 0.72, True)]


def fx_services(fr, d, t, sh):
    a = fade(t, sh['start'] + 0.1, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    x, y, w = 96, 190, 640
    panel(fr, (x, y, x + w, y + 400), 0.66, (5, 9, 16), 12)
    d.rectangle([x, y, x + w, y + 42], fill=(14, 22, 36))
    txt(d, (x + 18, y + 10), 'SERVICIOS · ESTADO HONESTO', 19, C['amber'], 2, mono=True)
    for i, (name, load, on) in enumerate(SERVICES):
        yy = y + 62 + i * 58
        txt(d, (x + 18, yy), name, 21, (232, 238, 248), 3)
        d.rounded_rectangle([x + 300, yy + 4, x + 300 + 200, yy + 12], radius=4, fill=(24, 34, 50))
        d.rounded_rectangle([x + 300, yy + 4, x + 300 + 200 * load, yy + 12], radius=4,
                            fill=C['red'] if not on else C['green'])
        pill(d, x + 540, yy - 2, '', on=on)
    txt(d, (x + 18, y + 372), 'nada se apaga sin medir el efecto', 16, (140, 165, 185), 0, mono=True)


def fx_win(fr, d, t, sh):
    a = fade(t, sh['start'] + 0.1, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    for i, (lb, col) in enumerate([('CONFIGURACIÓN', C['cyan']), ('ENERGÍA', C['amber']),
                                   ('ARRANQUE', C['cyan']), ('MEMORIA', C['green'])]):
        ch = O.chip_layer(lb, col, 21)
        O.paste(fr, ch, (110 + (i % 2) * 20, 170 + i * 56), a * clamp(t * 3 - i * 0.4))
    for i in range(3):
        ph = (t * 0.6 + i * 0.33) % 1.0
        rr = 90
        cx, cy = W - 260, 250 + i * 190
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 140, 140 + 260 * ph, fill=C['cyan'], width=7)
    ch = O.chip_layer('WINDOWS 10 / 11 · MISMO MÉTODO', C['amber'], 19)
    O.paste(fr, ch, (110, H - 240), a)


def fx_tool(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'] + 0.1, sh['end'] - 0.1, 0.3, 0.3)
    if a <= 0.02:
        return
    ch = O.chip_layer('UN CLIC', (150, 160, 180), 24)
    O.paste(fr, ch, (150, 180), a)
    ch2 = O.chip_layer('POR ETAPAS', C['amber'], 24)
    O.paste(fr, ch2, (W - 150 - ch2.size[0], 180), a)
    ch3 = O.chip_layer('MÁS QUE UN POWERSHELL', C['cyan'], 21)
    O.paste(fr, ch3, ((W - ch3.size[0]) / 2, H - 210), a * clamp(p * 3))
    # marca de desactualizado a la izquierda
    if p > 0.3:
        k = clamp((p - 0.3) * 4)
        cx, cy, r = 330, H - 330, 60
        d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360 * k, fill=(150, 160, 180), width=6)
        txt(d, (cx, cy - 12), 'OLD', 26, (150, 160, 180), 3, anchor='mm')


def fx_unmask(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = fade(t, sh['start'], sh['end'] - 0.06, 0.2, 0.25)
    d = ImageDraw.Draw(fr)
    for i in range(4):
        yy = int((p * 1.3 + i * 0.22) % 1.0 * H)
        d.rectangle([0, yy, W, yy + 4], fill=(255, 255, 255))
    lay = layer_text('VERDADERO POTENCIAL', 74, C['amber'], 8, 4)
    O.paste(fr, lay, ((W - lay.size[0]) / 2, 300), a * clamp(p * 2.2))
    l2 = layer_text('DE WINDOWS', 58, (238, 244, 252), 6, 6)
    O.paste(fr, l2, ((W - l2.size[0]) / 2, 400), a * clamp(p * 2.2 - 0.4))
    ch = O.chip_layer('FIN DEL HUMO', C['green'], 22)
    O.paste(fr, ch, ((W - ch.size[0]) / 2, 470), a * clamp(p * 2.4 - 0.9))


def fx_cta(fr, d, t, sh):
    p = (t - sh['start']) / sh['dur']
    a = clamp(p * 3.2)
    gl = O.logo_image(1060)
    O.paste(fr, gl, ((W - gl.size[0]) / 2, 108), a)
    l1 = layer_text('COMENCEMOS DE UNA VEZ', 62, C['amber'], 7, 3)
    O.paste(fr, l1, ((W - l1.size[0]) / 2, 430), clamp((p - 0.10) * 4))
    ch = O.chip_layer('EP.01 · OPTIMIZACIÓN REAL DE WINDOWS', C['cyan'], 21)
    O.paste(fr, ch, ((W - ch.size[0]) / 2, 512), clamp((p - 0.2) * 4))
    bw, bh = 400, 96
    bx, by = W / 2 - bw / 2, 596
    pulse = 0.5 + 0.5 * math.sin(t * 3.4)
    d.rounded_rectangle([bx - 6 - pulse * 6, by - 6 - pulse * 6, bx + bw + 6 + pulse * 6,
                         by + bh + 6 + pulse * 6], radius=22, outline=(255, 60, 60), width=2)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(214, 40, 40),
                        outline=(255, 255, 255), width=3)
    d.polygon([(bx + 54, by + 30), (bx + 54, by + 74), (bx + 96, by + 52)], fill=(255, 255, 255))
    txt(d, (bx + 116, by + 18), 'SUSCRIBITE', 40, (255, 255, 255), 2)
    txt(d, (W / 2, by + bh + 56), 'ACTIVÁ LAS NOTIFICACIONES', 26, (235, 240, 250), 3,
        mono=True, tracking=5, anchor='mm')


FX = {
    'ep_boot': fx_boot, 'ep_logo': fx_logo, 'ep_talk': fx_talk, 'ep_fake': fx_fake,
    'ep_ab': fx_ab, 'ep_formula': fx_formula, 'ep_quote': fx_quote, 'ep_term': fx_term,
    'ep_meter': fx_meter, 'ep_services': fx_services, 'ep_win': fx_win, 'ep_tool': fx_tool,
    'ep_unmask': fx_unmask, 'ep_cta': fx_cta,
}


def render(name, fr, d, t, sh, env=0.0):
    fn = FX.get(name)
    if fn is None:
        return
    if name == 'ep_talk':
        fn(fr, d, t, sh, env)
    else:
        fn(fr, d, t, sh)
