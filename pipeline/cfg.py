"""EVO LABS — configuración de producción: paleta, tipografías, timeline, guion."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_ff():
    import shutil
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    for c in ('ffmpeg', '/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg'):
        w = shutil.which(c) or (c if os.path.exists(c) else None)
        if w:
            return w
    raise RuntimeError('ffmpeg no encontrado')


FF = get_ff()
DIR_SCENES = os.path.join(ROOT, 'assets', 'scenes')
DIR_AUDIO = os.path.join(ROOT, 'assets', 'audio')
BUILD = os.path.join(ROOT, 'build', 'work')
WORK = 'work'
OUT_VIDEO = 'EVO_LABS_intro_1080p60.mp4'
VO_FILE = {}
ANIM_MOUTH = True

W, H = 1920, 1080
FPS = 60
SR = 44100

# ---------------------------------------------------------------- paleta EVO
C = dict(
    amber=(255, 192, 30),      # amarillo EVO
    amber_hi=(255, 224, 130),
    orange=(242, 101, 34),
    cyan=(34, 211, 238),
    cyan_dim=(16, 122, 140),
    white=(255, 255, 255),
    ink=(10, 14, 26),
    ink2=(16, 22, 38),
    green=(52, 211, 110),
    red=(239, 68, 68),
    grey=(150, 160, 180),
)

F_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F_MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

# ---------------------------------------------------------------- voz en off
VO_TEXT = {
    's1': '¡Bienvenidos a EVO LABS, Laboratorio de Software! Te preguntarás qué encontrarás aquí y te lo responderé rápido.',
    's2': 'Herramientas de IA locas y potentes, innovación en software libre creado con inteligencia artificial gratuita y mejoras de IA gratuita.',
    's3': 'Bancos de prueba y un ring donde lucharán los mejores agentes para lograr el mismo objetivo.',
    's4': 'Personalizaciones, regalos de aplicaciones para usuarios, lo mejor en mejoras de PC, creación de videojuegos y optimización de FPS real.',
    's5': 'Y nunca, pero nunca, daremos un título que te haga perder el tiempo. Te lo prometemos.',
    's6': 'También encontrarás hacking ético, promociones y software con ofertas para aprovechar. Y algo más: tengo métodos reales para aprovechar los agentes de IA más potentes, incluso gratuitamente. Voy a enseñarte mis descubrimientos y experimentos.',
    's7': 'Acá nos tomamos el tiempo de responder. No vendemos humo como quienes prometen Claude Sonnet gratis y sin límites y después te hacen instalar Ollama. ¡Basta de farsas!',
    's8': 'Unite a EVO LABS, el laboratorio donde descubrimos métodos y fórmulas reales. He dedicado mucho tiempo a esto y te prometo que vas a aprender de verdad. Queda en tus manos elegir qué hacer.',
}

VO_DUR = {'s1': 6.39, 's2': 7.99, 's3': 5.11, 's4': 8.63,
          's5': 5.11, 's6': 14.07, 's7': 10.23, 's8': 10.87}

# palabras que se resaltan en amarillo EVO dentro de los subtítulos
KEYWORDS = set('''EVO LABS IA SOFTWARE AGENTES RING BANCOS INTELIGENCIA ARTIFICIAL
LIBRE GRATUITA PC VIDEOJUEGOS FPS REAL HUMO RESULTADOS PROMETEMOS VERDAD
HACKING ÉTICO OFERTAS MÉTODOS POTENTES GRATUITAMENTE EXPERIMENTOS FARSAS
CLAUDE SONNET OLLAMA LÍMITES INSTALAR TIEMPO TÍTULO APRENDER ELEGIR
LABORATORIO PRUEBA OBJETIVO APLICACIONES USUARIOS PERSONALIZACIONES MEJORAS
CREACIÓN OPTIMIZACIÓN DESARROLLO INNOVACIÓN HERRAMIENTAS LOCAS PROMOCIONES
APROVECHAR DESCUBRIMIENTOS MISMOS MÉTODO FÓRMULAS UNITE'''.split())

# ---------------------------------------------------------------- capítulos
CHAPTERS = {
    's1': ('01', 'APERTURA'),
    's2': ('02', 'UNIVERSO EVO'),
    's3': ('03', 'RING DE AGENTES'),
    's4': ('04', 'EXPERIMENTACIÓN'),
    's5': ('05', 'NUESTRA PROMESA'),
    's6': ('06', 'IA & OPORTUNIDADES'),
    's7': ('07', 'DIFERENCIACIÓN'),
    's8': ('08', 'GRAN FINAL'),
}

# ---------------------------------------------------------------- planos
# cam = (z0, z1, (fx0, fy0), (fx1, fy1))  -> zoom y foco normalizados
# mouth = (cx, cy, w, h) en coordenadas de la lámina original (1376x768)
S = [
    # ---- 01 APERTURA
    dict(id='s1a', img='s01_systems.jpg', dur=5.6,
         cam=(1.00, 1.14, (0.50, 0.52), (0.52, 0.50)), fx='boot', voice=False),
    dict(id='s1b', img=None, dur=1.9,
         cam=(1.0, 1.04, (0.5, 0.5), (0.5, 0.5)), fx='logo', voice=False),
    dict(id='s1c', img='s01_char_master.jpg', dur=7.2,
         cam=(1.10, 1.00, (0.47, 0.42), (0.47, 0.44)), fx='talk',
         mouth=(660, 484, 140, 20)),
    # ---- 02 UNIVERSO EVO
    dict(id='s2a', img='s02_universe.jpg', dur=3.6,
         cam=(1.00, 1.16, (0.50, 0.50), (0.50, 0.46)), fx='hud'),
    dict(id='s2b', img='s02_char_gesture.jpg', dur=6.4,
         cam=(1.14, 1.02, (0.42, 0.45), (0.36, 0.47)), fx='panels'),
    # ---- 03 RING
    dict(id='s3a', img='s03_ring.jpg', dur=3.4,
         cam=(1.18, 1.02, (0.50, 0.55), (0.50, 0.50)), fx='ring'),
    dict(id='s3b', img='s03_char_ringmaster.jpg', dur=4.2,
         cam=(1.02, 1.14, (0.55, 0.50), (0.50, 0.46)), fx='ring'),
    # ---- 04 EXPERIMENTACIÓN
    dict(id='s4a', img='s04_workbench.jpg', dur=3.4,
         cam=(1.16, 1.02, (0.45, 0.55), (0.52, 0.46)), fx='bench'),
    dict(id='s4b', img='s04_game.jpg', dur=3.2,
         cam=(1.02, 1.16, (0.60, 0.45), (0.55, 0.50)), fx='bench'),
    dict(id='s4c', img='s01_char_master.jpg', dur=3.6,
         cam=(1.20, 1.06, (0.47, 0.44), (0.44, 0.46)), fx='talk',
         mouth=(660, 484, 140, 20)),
    # ---- 05 PROMESA
    dict(id='s5a', img='s05_char_serious.jpg', dur=6.6,
         cam=(1.02, 1.16, (0.47, 0.45), (0.47, 0.44)), fx='talk',
         mouth=(662, 479, 142, 20)),
    dict(id='s5b', img=None, dur=3.6,
         cam=(1.0, 1.03, (0.5, 0.5), (0.5, 0.5)), fx='promise'),
    # ---- 06 IA & OPORTUNIDADES
    dict(id='s6a', img='s06_research.jpg', dur=5.2,
         cam=(1.16, 1.02, (0.75, 0.45), (0.80, 0.48)), fx='panels'),
    dict(id='s6b', img='s02_universe.jpg', dur=4.2,
         cam=(1.16, 1.02, (0.62, 0.46), (0.42, 0.52)), fx='hud'),
    dict(id='s6c', img='s06_research.jpg', dur=5.6,
         cam=(1.02, 1.12, (0.82, 0.50), (0.78, 0.46)), fx='panels'),
    # ---- 07 DIFERENCIACIÓN
    dict(id='s7a', img=None, dur=4.6,
         cam=(1.0, 1.06, (0.5, 0.5), (0.5, 0.5)), fx='split'),
    dict(id='s7b', img='s07_fake.jpg', dur=2.6,
         cam=(1.05, 1.18, (0.50, 0.45), (0.60, 0.50)), fx='fake'),
    dict(id='s7c', img='s07_real.jpg', dur=4.2,
         cam=(1.16, 1.02, (0.62, 0.48), (0.50, 0.50)), fx='real'),
    # ---- 08 GRAN FINAL
    dict(id='s8a', img='s08_labwide.jpg', dur=3.2,
         cam=(1.06, 1.22, (0.50, 0.58), (0.50, 0.50)), fx='final'),
    dict(id='s8b', img='s08_char_wink.jpg', dur=8.2,
         cam=(1.14, 1.02, (0.46, 0.45), (0.44, 0.48)), fx='talk',
         mouth=None),
    dict(id='s8c', img=None, dur=7.0,
         cam=(1.0, 1.02, (0.5, 0.5), (0.5, 0.5)), fx='outro'),
]

# qué escena acompaña cada plano (para capítulos y voz)
SCENE_OF = {'s1a': 's1', 's1b': 's1', 's1c': 's1',
            's2a': 's2', 's2b': 's2',
            's3a': 's3', 's3b': 's3',
            's4a': 's4', 's4b': 's4', 's4c': 's4',
            's5a': 's5', 's5b': 's5',
            's6a': 's6', 's6b': 's6', 's6c': 's6',
            's7a': 's7', 's7b': 's7', 's7c': 's7',
            's8a': 's8', 's8b': 's8', 's8c': 's8'}

# primera escena de cada grupo ocupa los planos en orden
SCENE_SHOTS = {
    's1': ['s1a', 's1b', 's1c'],
    's2': ['s2a', 's2b'],
    's3': ['s3a', 's3b'],
    's4': ['s4a', 's4b', 's4c'],
    's5': ['s5a', 's5b'],
    's6': ['s6a', 's6b', 's6c'],
    's7': ['s7a', 's7b', 's7c'],
    's8': ['s8a', 's8b', 's8c'],
}

# offset de la voz dentro de la escena y cola de silencio
VO_OFFSET = {'s1': 7.50, 's2': 0.35, 's3': 0.30, 's4': 0.30,
             's5': 0.40, 's6': 0.30, 's7': 0.30, 's8': 0.30}
VO_TAIL = {'s1': 0.50, 's2': 0.50, 's3': 0.50, 's4': 0.50,
           's5': 0.30, 's6': 0.50, 's7': 0.50, 's8': 2.50}


def build_timeline():
    """Devuelve (shots con start/end absolutos, escenas con start/vo_start/vo_end, duración total)."""
    shots, scenes = [], []
    t = 0.0
    for skey in list(SCENE_SHOTS.keys()):
        ids = SCENE_SHOTS[skey]
        dur_shots = sum(x['dur'] for x in S if x['id'] in ids)
        scene_start = t
        vo_start = scene_start + VO_OFFSET[skey]
        vo_end = vo_start + VO_DUR[skey]
        scene_len = max(dur_shots, VO_OFFSET[skey] + VO_DUR[skey] + VO_TAIL[skey])
        cur = scene_start
        scene_shots = [x for x in S if x['id'] in ids]
        for i, x in enumerate(scene_shots):
            sd = dict(x)
            sd['start'] = cur
            pad = (scene_len - dur_shots) if i == len(scene_shots) - 1 else 0.0
            sd['end'] = cur + x['dur'] + pad
            shots.append(sd)
            cur = sd['end']
        scenes.append(dict(key=skey, start=scene_start, end=scene_start + scene_len,
                           vo_start=vo_start, vo_end=vo_end))
        t = scene_start + scene_len
    return shots, scenes, t


SHOTS, SCENES, TOTAL = build_timeline()

# ---------------------------------------------------------------- episodios
_EP = os.environ.get('EVO_EP')
if _EP:
    import importlib
    _m = importlib.import_module(_EP)
    VO_TEXT = _m.VO_TEXT
    VO_DUR = _m.VO_DUR
    CHAPTERS = _m.CHAPTERS
    S = _m.S
    SCENE_SHOTS = _m.SCENE_SHOTS
    VO_OFFSET = _m.VO_OFFSET
    VO_TAIL = _m.VO_TAIL
    VO_FILE = getattr(_m, 'VO_FILE', {})
    OUT_VIDEO = getattr(_m, 'OUT_VIDEO', OUT_VIDEO)
    WORK = getattr(_m, 'WORK', WORK)
    ANIM_MOUTH = getattr(_m, 'ANIM_MOUTH', False)
    BUILD = os.path.join(ROOT, 'build', WORK)
    SHOTS, SCENES, TOTAL = build_timeline()
