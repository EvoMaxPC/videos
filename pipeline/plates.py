"""Genera las láminas especiales (logo, promesa, split, outro) a 3840x2160."""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg
from overlays import logo_image

SW, SH = 3840, 2160
OUT = os.path.join(cfg.DIR_SCENES)


def radial_bg(color=(255, 175, 40), power=0.9, base=(4, 6, 12)):
    y, x = np.mgrid[0:SH, 0:SW].astype(np.float32)
    cx, cy = SW * 0.5, SH * 0.52
    r = np.sqrt(((x - cx) / (SW * 0.55)) ** 2 + ((y - cy) / (SH * 0.62)) ** 2)
    g = np.clip(1 - r, 0, 1) ** 2.2 * power
    img = np.zeros((SH, SW, 3), np.float32)
    for i in range(3):
        img[..., i] = base[i] + g * color[i]
    return np.clip(img, 0, 255).astype(np.uint8)


def add_grid(img, step=140, color=(30, 60, 80), alpha=0.25):
    d = ImageDraw.Draw(img, 'RGBA')
    for x in range(0, SW, step):
        d.line([(x, 0), (x, SH)], fill=color + (int(255 * alpha),), width=2)
    for y in range(0, SH, step):
        d.line([(0, y), (SW, y)], fill=color + (int(255 * alpha),), width=2)
    return img


def vignette(img, strength=0.75):
    y, x = np.mgrid[0:SH, 0:SW].astype(np.float32)
    cx, cy = SW / 2, SH / 2
    r = np.sqrt(((x - cx) / (SW * 0.62)) ** 2 + ((y - cy) / (SH * 0.62)) ** 2)
    v = np.clip(1 - (r ** 2.2) * strength, 0.05, 1)
    a = np.asarray(img).astype(np.float32) * v[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def make_logo_plate():
    img = Image.fromarray(radial_bg((255, 168, 30), 0.42))
    img = add_grid(img, 160, (24, 54, 74), 0.16)
    # destello diagonal
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(70):
        a = int(3 * (1 - i / 70))
        d.line([(-200 + i * 6, SH + 100), (SW * 0.55 + i * 6, -100)], fill=(255, 210, 140, a), width=10)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    img = vignette(img, 0.9)
    return img


def make_promise_plate():
    img = Image.fromarray(radial_bg((255, 150, 30), 0.55))
    # humo
    rng = np.random.default_rng(11)
    smoke = rng.normal(0, 1, (SH // 8, SW // 8)).astype(np.float32)
    sm = Image.fromarray(np.clip(128 + smoke * 90, 0, 255).astype(np.uint8), 'L').resize((SW, SH), Image.BICUBIC)
    sm = sm.filter(ImageFilter.GaussianBlur(40))
    a = np.asarray(img).astype(np.float32)
    s = (np.asarray(sm).astype(np.float32) - 128) / 128 * 16
    a += s[..., None] * np.array([1.0, 0.75, 0.5], np.float32)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    img = vignette(img, 1.0)
    return img


def crop_to(path, box_w, box_h, out_w, out_h, zoom=1.0):
    im = Image.open(os.path.join(OUT, path)).convert('RGB')
    w, h = im.size
    cw, ch = w * zoom, h * zoom
    im = im.resize((int(cw), int(ch)), Image.LANCZOS)
    w, h = im.size
    tw, th = out_w * 1.0, out_h * 1.0
    s = max(tw / w, th / h)
    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    w, h = im.size
    x0 = int((w - out_w) / 2)
    y0 = int((h - out_h) / 2)
    return im.crop((x0, y0, x0 + out_w, y0 + out_h))


def make_split_plate():
    hw = SW // 2
    left = crop_to('s07_fake.png', 688, 768, hw, SH, 1.15)
    right = crop_to('s07_real.png', 688, 768, hw, SH, 1.05)
    img = Image.new('RGB', (SW, SH))
    img.paste(left, (0, 0))
    img.paste(right, (hw, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([hw - 5, 0, hw + 5, SH], fill=(255, 192, 30, 255))
    d.rectangle([hw - 14, 0, hw + 14, SH], fill=(255, 192, 30, 45))
    # leve desaturación del lado falso
    a = np.asarray(img).astype(np.float32)
    g = a[..., :3].mean(axis=2, keepdims=True)
    a[:, :hw, :3] = a[:, :hw, :3] * 0.55 + g[:, :hw] * 0.45
    a[:, :hw, :3] *= np.array([1.05, 0.92, 1.02], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def make_outro_plate():
    im = Image.open(os.path.join(OUT, 's08_labwide.png')).convert('RGB')
    s = max(SW / im.size[0], SH / im.size[1])
    im = im.resize((int(im.size[0] * s) + 2, int(im.size[1] * s) + 2), Image.LANCZOS)
    x0 = (im.size[0] - SW) // 2
    y0 = (im.size[1] - SH) // 2
    im = im.crop((x0, y0, x0 + SW, y0 + SH)).filter(ImageFilter.GaussianBlur(6))
    a = np.asarray(im).astype(np.float32) * 0.30 + np.array([6, 8, 16], np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return vignette(im, 1.1)


if __name__ == '__main__':
    jobs = {
        'plate_logo.png': make_logo_plate,
        'plate_promise.png': make_promise_plate,
        'plate_split.png': make_split_plate,
        'plate_outro.png': make_outro_plate,
    }
    for name, fn in jobs.items():
        im = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
