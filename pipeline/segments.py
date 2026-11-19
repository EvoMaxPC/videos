"""Pass A: convierte cada lámina en un clip cinematográfico 1080p60 con movimiento de cámara."""
import os, sys, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfg

FF = cfg.FF
IW, IH = 3840, 2160
SEGDIR = os.path.join(cfg.BUILD, 'seg')

SPECIAL = {'logo': 'plate_logo.png', 'promise': 'plate_promise.png',
           'split': 'plate_split.png', 'outro': 'plate_outro.png'}


def plate_of(shot):
    if shot['img']:
        return os.path.join(cfg.DIR_SCENES, shot['img'])
    return os.path.join(cfg.DIR_SCENES, SPECIAL[shot['fx']])


def ease_expr(nf):
    return f"((1-cos(PI*on/{nf}))/2)"


def build_segment(shot, force=False):
    out = os.path.join(SEGDIR, shot['id'] + '.mp4')
    if os.path.exists(out) and not force:
        return out
    nf = max(2, int(round(shot['dur'] * cfg.FPS)))
    z0, z1, (fx0, fy0), (fx1, fy1) = shot['cam']
    e = ease_expr(nf)
    z = f"{z0}+({z1}-{z0})*{e}"
    fxe = f"{fx0}+({fx1}-{fx0})*{e}"
    fye = f"{fy0}+({fy1}-{fy0})*{e}"
    x = f"clip(({fxe})*iw-iw/(2*({z})),0,iw-iw/({z}))"
    y = f"clip(({fye})*ih-ih/(2*({z})),0,ih-ih/({z}))"
    vf = (
        "scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=3840:2160,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={nf}:s=1920x1080:fps={cfg.FPS},"
        "eq=contrast=1.055:saturation=1.07:gamma=0.99,"
        "unsharp=5:5:0.35:5:5:0.0,"
        "vignette=angle=PI/4.8,"
        "noise=alls=4:allf=t+u,"
        "rgbashift=rh=1:bh=-1,"
        "format=yuv420p"
    )
    cmd = [FF, '-y', '-v', 'error', '-i', plate_of(shot), '-filter_complex', vf,
           '-frames:v', str(nf), '-r', str(cfg.FPS), '-c:v', 'libx264',
           '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', '-an', out]
    subprocess.run(cmd, check=True)
    return out


def build_all(force=False):
    os.makedirs(SEGDIR, exist_ok=True)
    paths = []
    for shot in cfg.SHOTS:
        p = build_segment(shot, force)
        paths.append(p)
        print('segmento', shot['id'], shot['img'] or shot['fx'], f"{shot['dur']:.2f}s")
    lst = os.path.join(cfg.BUILD, 'concat.txt')
    with open(lst, 'w') as f:
        for p in paths:
            f.write("file '%s'\n" % p)
    base = os.path.join(cfg.BUILD, 'base.mp4')
    subprocess.run([FF, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c', 'copy', base], check=True)
    print('base:', base)
    return base


if __name__ == '__main__':
    build_all(force='-f' in sys.argv)
