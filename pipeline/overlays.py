"""EVO LABS — capas gráficas: logo, HUD, subtítulos, placas de texto."""
import os, sys, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg

C = cfg.C
W, H = cfg.W, cfg.H
_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


def text_size(draw, txt, f, tracking=0):
    if not txt:
        return (0, 0)
    b = draw.textbbox((0, 0), txt, font=f)
    w = b[2] - b[0]
    if tracking:
        w += tracking * (len(txt) - 1)
    return (w, b[3] - b[1])


def draw_tracked(draw, xy, txt, f, fill, tracking=0, anchor_center=False, stroke=0, stroke_fill=None):
    x, y = xy
    if anchor_center:
        w, _ = text_size(draw, txt, f, tracking)
        x -= w / 2
    for ch in txt:
        draw.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        w, _ = text_size(draw, ch, f)
        x += w + tracking


# ---------------------------------------------------------------- logo EVO
@functools.lru_cache(maxsize=8)
def logo_image(width=1400, subtitle=True):
    txt = 'EVO LABS'
    # tamaño de fuente para que el conjunto ocupe ~width
    fs = int(width * 0.30)
    probe = ImageDraw.Draw(Image.new('L', (10, 10)))
    f = ImageFont.truetype(cfg.F_BOLD, fs)
    bw = probe.textbbox((0, 0), txt, font=f)
    tw, th = bw[2] - bw[0], bw[3] - bw[1]
    fs = int(fs * (width * 0.94) / max(1, tw))
    f = ImageFont.truetype(cfg.F_BOLD, fs)
    bw = probe.textbbox((0, 0), txt, font=f)
    tw, th = bw[2] - bw[0], bw[3] - bw[1]
    pad = int(fs * 0.18)
    skew_w = int(0.22 * (th + pad * 2))

    def build(stroke_w):
        L = Image.new('L', (tw + pad * 2 + skew_w, th + pad * 2), 0)
        d = ImageDraw.Draw(L)
        d.text((pad - bw[0], pad - bw[1]), txt, font=f, fill=255,
               stroke_width=stroke_w, stroke_fill=255)
        L = L.transform(L.size, Image.AFFINE, (1, 0.20, 0, 0, 1, 0), resample=Image.BICUBIC)
        bb = L.getbbox()
        return L.crop(bb)

    mask = build(max(1, fs // 26))
    outline = build(max(5, fs // 9))
    tw2, th2 = mask.size
    ow, ohh = outline.size
    sub_h = int(width * 0.135) if subtitle else 0
    total_h = max(th2, ohh) + sub_h + int(width * 0.03)
    sf = ImageFont.truetype(cfg.F_BOLD, int(width * 0.050)) if subtitle else None
    sub = 'LABORATORIO DE SOFTWARE'
    tr = int(width * 0.0135)
    _p = ImageDraw.Draw(Image.new('L', (10, 10)))
    sw = text_size(_p, sub, sf, tr)[0] if subtitle else 0
    cw = int(max(tw2, ow, sw + width * 0.06))
    img = Image.new('RGBA', (cw, total_h), (0, 0, 0, 0))
    # contorno blanco
    white = Image.new('RGBA', (ow, ohh), (255, 255, 255, 255))
    img.paste(white, ((img.size[0] - ow) // 2, (max(th2, ohh) - ohh) // 2), outline)
    # relleno degradado ámbar -> naranja
    grad = Image.new('RGBA', (tw2, th2))
    gd = ImageDraw.Draw(grad)
    for y in range(th2):
        pp = y / max(1, th2 - 1)
        col = tuple(int(C['amber_hi'][i] * (1 - pp) ** 1.1 + C['orange'][i] * pp ** 1.15) for i in range(3))
        gd.line([(0, y), (tw2, y)], fill=col + (255,))
    img.paste(grad, ((img.size[0] - tw2) // 2, (max(th2, ohh) - th2) // 2), mask)
    if subtitle:
        dd = ImageDraw.Draw(img)
        y0 = total_h - sub_h + int(width * 0.008)
        draw_tracked(dd, ((img.size[0] - sw) / 2, y0), sub, sf, (245, 248, 255, 240),
                     tracking=tr, stroke=2, stroke_fill=(6, 8, 14, 235))
        dd.rounded_rectangle([(img.size[0] - sw) / 2 - 26, y0 + int(width * 0.062),
                              (img.size[0] + sw) / 2 + 26, y0 + int(width * 0.062) + 4],
                             radius=2, fill=C['amber'] + (225,))
    bb = img.getbbox()
    return img.crop(bb)


def stamp_glow(size=(W, H), color=(255, 192, 30), power=0.5, radius=0.42):
    img = Image.new('RGB', size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] * 0.5, size[1] * 0.5
    r = max(size) * radius
    for i in range(18, 0, -1):
        p = i / 18
        rr = r * p
        col = tuple(int(c * (1 - p) ** 2 * power * 255) for c in color)
        d.ellipse([cx - rr, cy - rr * 0.75, cx + rr, cy + rr * 0.75], fill=col)
    return img.filter(ImageFilter.GaussianBlur(int(max(size) * 0.03)))


# ---------------------------------------------------------------- subtítulos
def _syllable_weight(word):
    vowels = 'aeiouáéíóúüAEIOUÁÉÍÓÚÜ'
    n = sum(1 for ch in word if ch in vowels)
    return max(1.6, n * 1.0 + len(word) * 0.32)


def word_times(text, start, dur):
    words = text.split()
    wts = [_syllable_weight(w) for w in words]
    tot = sum(wts)
    out, t = [], start
    for w, wt in zip(words, wts):
        d = dur * wt / tot
        out.append((w, t, t + d))
        t += d
    return out


def chunks(words, max_words=3, max_chars=16):
    out, cur = [], []
    for w in words:
        cand = cur + [w]
        if len(cand) > max_words or sum(len(x[0]) + 1 for x in cand) > max_chars:
            if cur:
                out.append(cur)
            cur = [w]
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def clean(w):
    return w.strip('¡!¿?.,;:«»"').upper()


@functools.lru_cache(maxsize=512)
def subtitle_layer(text, hl_index, size=54, key_on=()):
    f = font(cfg.F_BOLD, size)
    pad = 26
    tmp = Image.new('RGBA', (10, 10))
    d = ImageDraw.Draw(tmp)
    parts = text.split(' ')
    ws = [text_size(d, p, f)[0] for p in parts]
    space = text_size(d, ' ', f)[0] + 12
    total = sum(ws) + space * (len(parts) - 1)
    img = Image.new('RGBA', (int(total) + pad * 2, size + pad * 2 + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for i, p in enumerate(parts):
        is_key = clean(p) in cfg.KEYWORDS
        if i == hl_index:
            col = C['amber_hi']
        elif is_key:
            col = C['amber']
        else:
            col = C['white']
        # sombra + contorno
        d.text((x + 3, pad + 5), p, font=f, fill=(0, 0, 0, 190), stroke_width=6, stroke_fill=(0, 0, 0, 190))
        d.text((x, pad), p, font=f, fill=col + (255,), stroke_width=5, stroke_fill=(8, 10, 18, 240))
        if i == hl_index:
            d.rounded_rectangle([x + 2, pad + size + 6, x + ws[i] - 2, pad + size + 11], radius=3,
                                fill=C['amber_hi'] + (230,))
        x += ws[i] + space
    return img


def caption_frames(all_words, start, end):
    """Devuelve lista de (t0,t1,chunk) para todo el video."""
    out = []
    for ch in chunks(all_words):
        out.append((ch[0][1], ch[-1][2], ch))
    return out


# ---------------------------------------------------------------- HUD helpers
def rounded(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def bracket(d, box, color, size=34, w=3):
    x0, y0, x1, y1 = box
    for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line([(cx, cy), (cx + dx * size, cy)], fill=color, width=w)
        d.line([(cx, cy), (cx, cy + dy * size)], fill=color, width=w)


@functools.lru_cache(maxsize=256)
def chip_layer(text, color=(34, 211, 238), size=24, fg=None):
    f = font(cfg.F_BOLD, size)
    tmp = Image.new('RGBA', (10, 10))
    d = ImageDraw.Draw(tmp)
    tw, th = text_size(d, text, f, 2)
    w, h = int(tw) + 34, size + 18
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(8, 12, 22, 190), outline=color + (255,), width=2)
    d.rounded_rectangle([8, h / 2 - 4, 16, h / 2 + 4], radius=3, fill=color + (255,))
    draw_tracked(d, (26, 8), text, f, (fg or color) + (255,), tracking=2)
    return img


def paste(fr, layer, xy, alpha=1.0):
    if alpha <= 0.004:
        return
    if alpha >= 0.999:
        fr.paste(layer, (int(xy[0]), int(xy[1])), layer)
    else:
        a = layer.getchannel('A').point(lambda v: int(v * alpha))
        fr.paste(layer, (int(xy[0]), int(xy[1])), a)


@functools.lru_cache(maxsize=64)
def glow_layer(color, size=520, radius=1.0):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(30, 0, -1):
        p = i / 30
        a = int(38 * (1 - p) ** 2.4)
        r = size * 0.5 * p * radius
        d.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], fill=color + (a,))
    return img.filter(ImageFilter.GaussianBlur(size * 0.05))


@functools.lru_cache(maxsize=8)
def vignette_layer(strength=190):
    x = np.linspace(-1, 1, W, dtype=np.float32)
    y = np.linspace(-1, 1, H, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx ** 2 * 0.85 + yy ** 2)
    a = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * strength
    img = Image.fromarray((a).astype(np.uint8), 'L')
    return img.filter(ImageFilter.GaussianBlur(24))


@functools.lru_cache(maxsize=8)
def grain_layer(seed=3, amount=9):
    r = np.random.default_rng(seed)
    n = r.normal(0, amount, (H // 2, W // 2)).astype(np.float32)
    img = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8), 'L').resize((W, H), Image.BILINEAR)
    return img
