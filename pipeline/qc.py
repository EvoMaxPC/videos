import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import cfg, compose
FF = compose.FF
env = np.load(os.path.join(cfg.BUILD,'env.npz'))['env']
os.makedirs(os.path.join(cfg.BUILD,'qc'), exist_ok=True)
times = [float(x) for x in sys.argv[1:]] or [1.4, 6.4, 9.0, 16.0, 22.0, 26.5, 30.0, 34.0, 37.0, 44.0, 50.5, 55.0, 60.0, 65.0, 70.0, 73.5, 77.0, 80.5, 85.0, 88.0, 92.0, 94.5]
compose.build_captions()
for t in times:
    p = subprocess.run([FF,'-v','error','-ss',f'{t:.3f}','-i',os.path.join(cfg.BUILD,'base.mp4'),
                        '-frames:v','1','-f','image2pipe','-vcodec','png','-'], capture_output=True)
    import io
    fr = Image.open(io.BytesIO(p.stdout)).convert('RGB')
    i = int(t*cfg.FPS)
    e = float(env[min(i, len(env)-1)])
    fr = compose.process_frame(fr, t, e)
    fr.save(os.path.join(cfg.BUILD,'qc', f'q_{t:06.2f}.png'))
print('qc ok', len(times))
