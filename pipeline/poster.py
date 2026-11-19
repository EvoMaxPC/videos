"""Miniatura 1280x720 para YouTube a partir del plano final."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg
import overlays as O
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

W, H = 1280, 720
src = os.path.join(cfg.ROOT, 'EVO_LABS_intro_1080p60.mp4')
raw = subprocess.run([cfg.FF, '-v', 'error', '-ss', '88.2', '-i', src, '-frames:v', '1',
                      '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
import io
bg = Image.open(io.BytesIO(raw)).convert('RGB')
bg = bg.resize((W, int(W * bg.size[1] / bg.size[0])), Image.LANCZOS)
top = (bg.size[1] - H) // 2
bg = bg.crop((0, top, W, top + H))
bg = ImageEnhance.Contrast(bg).enhance(1.04)
# viñeta izquierda para el logo
grad = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(grad)
for x in range(W):
    d.line([(x, 0), (x, H)], fill=int(max(0, 200 - x * 0.40)))
dark = Image.new('RGB', (W, H), (4, 6, 12))
bg = Image.composite(bg, Image.composite(dark, bg, grad.point(lambda v: int(v * 0.55))), Image.new('L', (W, H), 0))
bg.paste(Image.composite(dark, bg, grad.point(lambda v: int(v * 0.45))), (0, 0))
# logo
lg = O.logo_image(520)
bg.paste(lg, (48, 44), lg)
# franja inferior de texto
d = ImageDraw.Draw(bg)
f1 = O.font(cfg.F_BOLD, 44)
f2 = O.font(cfg.F_BOLD, 28)
d.rectangle([0, H - 208, W, H], fill=(6, 8, 16))
d.rectangle([0, H - 208, W, H - 202], fill=cfg.C['amber'])
d.text((52, H - 186), 'NO VENDEMOS HUMO.', font=f1, fill=(245, 248, 255))
d.text((52, H - 130), 'DEMOSTRAMOS RESULTADOS.', font=f1, fill=cfg.C['amber'])
d.text((52, H - 62), 'IA · AGENTES · BENCH · OPTIMIZACIÓN DE PC', font=f2, fill=(150, 200, 215))
out = os.path.join(cfg.ROOT, 'EVO_LABS_thumbnail.jpg')
bg.save(out, quality=94, subsampling=1)
print(out, bg.size)
