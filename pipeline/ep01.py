"""EP.01 — Optimización real de Windows: datos del episodio (guion, planos, tiempos)."""
import os

OUT_VIDEO = 'EVO_LABS_EP01_Optimizacion_Windows_1080p60.mp4'
WORK = 'work_ep01'
ANIM_MOUTH = False          # sin animación de boca, a pedido del canal

VO_FILE = {f's{i}': f'ep_v2_b{i}.mp3' for i in range(1, 11)}

VO_TEXT = {
    's1': 'Bienvenidos a EVO Labs, Laboratorio de Software. En el capítulo de hoy nos toca hablar de optimización real de Windows y, por sobre todas las cosas, con pruebas contundentes.',
    's2': 'Estoy cansado de ver videos que prometen con el título que te van a optimizar la PC y que va a volar, o que es la optimización definitiva, 999 FPS. Acá vamos a hablar con fundamentos y pruebas, y por sobre todas las cosas te lo voy a explicar paso a paso.',
    's3': 'Lo que sí te prometo es que no hay otro video como este de optimización, aunque busques horas y horas, porque acá hay años de pruebas.',
    's4': 'Uno: tengo que aclararte algo. Cada computadora es distinta, y el secreto de la optimización es que sea adaptativa. Esa es la fórmula que vamos a utilizar en este método. Y aclaro: no es solo un método con simples pasos, son una serie de etapas que debés seguir para obtener el límite real y la estabilidad de tu PC. Y te prometo que va a mejorar.',
    's5': 'Acá hacemos milagros, pero los comprobamos.',
    's6': 'No te vamos a decir: este proceso está consumiendo tanta memoria y no lo sabés, para que veas el video, te comas ocho minutos y no ganes nada de rendimiento.',
    's7': 'Si querés dejar tu PC un lujo, quedate. Si no, bajate WinUtil y dale plata al boludo de Chris Titus. Demasiada fama le hacen, porque les bajó un veinte por ciento de memoria eliminando telemetría, debloat y cosas que ni idea tenés. O quizás sí, pero acá hay más que un simple PowerShell. No digo que no haya servido en su momento, pero eso quedó desactualizado y le falta bastante para llevar al límite tu PC.',
    's8': 'También quiero aclararte algo: todos los cambios que vamos a hacer te los explico para que los entiendas. Si querés, los descargás, los ejecutás, los probás, y después me contás a ver con cuál te quedás.',
    's9': 'Y no es una competencia: es hora de que alguien, de una vez, desenmascare el verdadero potencial de Windows. Y que deje de vender humo y de dejar pelotudeces que sirven para recopilar datos o para romperte soberanamente las bolas.',
    's10': 'La hice larga porque, aparte de una introducción, es un descargo. Ahora sí: bienvenidos al laboratorio donde tu PC va a notar la diferencia. Voy a comenzar por lo más básico y terminar en lo más pro. Así que si te creés que te las sabés todas, adelantá el video: algo vas a encontrar. Y si no, bajate WinUtil. ¡Comenzamos de una vez!',
}

VO_DUR = {'s1': 11.72, 's2': 21.12, 's3': 9.48, 's4': 24.40, 's5': 4.72,
          's6': 12.68, 's7': 29.92, 's8': 13.20, 's9': 16.68, 's10': 23.92}

CHAPTERS = {
    's1': ('01', 'APERTURA'),
    's2': ('02', 'EL DESCARGO'),
    's3': ('03', 'LA PROMESA'),
    's4': ('04', 'EL MÉTODO'),
    's5': ('05', 'MILAGROS COMPROBADOS'),
    's6': ('06', 'SIN HUMO'),
    's7': ('07', 'WINUTIL Y CIA.'),
    's8': ('08', 'TRANSPARENCIA'),
    's9': ('09', 'DESENMASCARAR'),
    's10': ('10', 'COMENCEMOS'),
}

S = [
    # 01 APERTURA
    dict(id='e1a', img='ep_telemetry.jpg', dur=2.4,
         cam=(1.00, 1.12, (0.50, 0.50), (0.52, 0.48)), fx='ep_boot'),
    dict(id='e1b', img=None, dur=1.9,
         cam=(1.0, 1.04, (0.5, 0.5), (0.5, 0.5)), fx='ep_logo'),
    dict(id='e1d', img='ep_win_desktop.jpg', dur=4.2,
         cam=(1.00, 1.12, (0.50, 0.50), (0.42, 0.52)), fx='ep_win'),
    dict(id='e1c', img='s01_char_master.jpg', dur=6.2,
         cam=(1.12, 1.00, (0.47, 0.42), (0.47, 0.45)), fx='ep_talk'),
    # 02 EL DESCARGO
    dict(id='e2a', img='s07_fake.jpg', dur=5.2,
         cam=(1.04, 1.16, (0.50, 0.45), (0.58, 0.50)), fx='ep_fake'),
    dict(id='e2b', img='s05_char_serious.jpg', dur=4.6,
         cam=(1.02, 1.14, (0.47, 0.45), (0.47, 0.44)), fx='ep_talk'),
    dict(id='e2c', img='s07_fake.jpg', dur=2.4,
         cam=(1.18, 1.06, (0.62, 0.52), (0.50, 0.46)), fx='ep_fake'),
    dict(id='e2e', img='s01_char_master.jpg', dur=3.0,
         cam=(1.00, 1.12, (0.48, 0.46), (0.44, 0.44)), fx='ep_talk'),
    dict(id='e2d', img='s01_char_master.jpg', dur=5.0,
         cam=(1.14, 1.02, (0.46, 0.44), (0.48, 0.42)), fx='ep_talk'),
    # 03 LA PROMESA
    dict(id='e3a', img='ep_bench_ab.jpg', dur=4.0,
         cam=(1.16, 1.02, (0.40, 0.50), (0.50, 0.48)), fx='ep_ab'),
    dict(id='e3b', img='ep_bench_ab.jpg', dur=3.8,
         cam=(1.02, 1.16, (0.62, 0.48), (0.50, 0.52)), fx='ep_ab'),
    # 04 EL MÉTODO
    dict(id='e4a', img='ep_formula.jpg', dur=5.4,
         cam=(1.00, 1.14, (0.50, 0.52), (0.50, 0.46)), fx='ep_formula'),
    dict(id='e4b', img='ep_formula.jpg', dur=4.4,
         cam=(1.16, 1.02, (0.50, 0.46), (0.50, 0.54)), fx='ep_formula'),
    dict(id='e4c', img='s02_char_gesture.jpg', dur=5.4,
         cam=(1.14, 1.02, (0.42, 0.45), (0.36, 0.47)), fx='ep_talk'),
    dict(id='e4d', img='ep_formula.jpg', dur=5.6,
         cam=(1.02, 1.14, (0.46, 0.50), (0.56, 0.46)), fx='ep_formula'),
    # 05 MILAGROS COMPROBADOS
    dict(id='e5a', img=None, dur=4.6,
         cam=(1.0, 1.05, (0.5, 0.5), (0.5, 0.5)), fx='ep_quote'),
    # 06 SIN HUMO
    dict(id='e6a', img='ep_terminal.jpg', dur=4.4,
         cam=(1.10, 1.02, (0.46, 0.50), (0.50, 0.48)), fx='ep_term'),
    dict(id='e6b', img='ep_telemetry.jpg', dur=5.4,
         cam=(1.02, 1.15, (0.52, 0.48), (0.46, 0.52)), fx='ep_meter'),
    # 07 WINUTIL Y CIA.
    dict(id='e7a', img='ep_tool_card.jpg', dur=6.2,
         cam=(1.02, 1.12, (0.50, 0.48), (0.42, 0.50)), fx='ep_tool'),
    dict(id='e7b', img='ep_tool_card.jpg', dur=4.2,
         cam=(1.14, 1.02, (0.62, 0.50), (0.50, 0.48)), fx='ep_tool'),
    dict(id='e7c', img='ep_win_desktop.jpg', dur=5.6,
         cam=(1.02, 1.16, (0.44, 0.50), (0.54, 0.46)), fx='ep_win'),
    dict(id='e7d', img='s05_char_serious.jpg', dur=4.4,
         cam=(1.16, 1.02, (0.47, 0.44), (0.47, 0.46)), fx='ep_talk'),
    dict(id='e7f', img='ep_tool_card.jpg', dur=4.0,
         cam=(1.02, 1.14, (0.42, 0.52), (0.56, 0.46)), fx='ep_tool'),
    dict(id='e7e', img='ep_win_desktop.jpg', dur=4.4,
         cam=(1.16, 1.04, (0.58, 0.46), (0.46, 0.52)), fx='ep_services'),
    # 08 TRANSPARENCIA
    dict(id='e8a', img='s02_char_gesture.jpg', dur=5.6,
         cam=(1.02, 1.14, (0.36, 0.47), (0.42, 0.45)), fx='ep_talk'),
    dict(id='e8b', img='ep_terminal.jpg', dur=6.2,
         cam=(1.16, 1.02, (0.50, 0.48), (0.44, 0.52)), fx='ep_term'),
    # 09 DESENMASCARAR
    dict(id='e9a', img='ep_telemetry.jpg', dur=4.6,
         cam=(1.14, 1.02, (0.46, 0.52), (0.52, 0.46)), fx='ep_meter'),
    dict(id='e9b', img='ep_win_desktop.jpg', dur=4.4,
         cam=(1.04, 1.18, (0.50, 0.46), (0.56, 0.52)), fx='ep_unmask'),
    dict(id='e9d', img='ep_telemetry.jpg', dur=3.2,
         cam=(1.04, 1.16, (0.54, 0.46), (0.44, 0.52)), fx='ep_meter'),
    dict(id='e9c', img='s03_char_ringmaster.jpg', dur=4.6,
         cam=(1.02, 1.14, (0.55, 0.50), (0.48, 0.46)), fx='ep_talk'),
    # 10 COMENCEMOS
    dict(id='e10a', img='ep_bench_ab.jpg', dur=3.6,
         cam=(1.18, 1.04, (0.50, 0.52), (0.50, 0.46)), fx='ep_ab'),
    dict(id='e10b', img='s08_char_wink.jpg', dur=8.4,
         cam=(1.14, 1.02, (0.46, 0.45), (0.44, 0.48)), fx='ep_talk'),
    dict(id='e10c', img=None, dur=8.6,
         cam=(1.0, 1.03, (0.5, 0.5), (0.5, 0.5)), fx='ep_cta'),
]

SCENE_SHOTS = {
    's1': ['e1a', 'e1b', 'e1d', 'e1c'],
    's2': ['e2a', 'e2b', 'e2c', 'e2e', 'e2d'],
    's3': ['e3a', 'e3b'],
    's4': ['e4a', 'e4b', 'e4c', 'e4d'],
    's5': ['e5a'],
    's6': ['e6a', 'e6b'],
    's7': ['e7a', 'e7b', 'e7c', 'e7f', 'e7d', 'e7e'],
    's8': ['e8a', 'e8b'],
    's9': ['e9a', 'e9d', 'e9b', 'e9c'],
    's10': ['e10a', 'e10b', 'e10c'],
}

VO_OFFSET = {'s1': 5.0, 's2': 0.35, 's3': 0.30, 's4': 0.30, 's5': 0.35,
             's6': 0.30, 's7': 0.30, 's8': 0.30, 's9': 0.30, 's10': 0.30}
VO_TAIL = {'s1': 0.40, 's2': 0.45, 's3': 0.45, 's4': 0.45, 's5': 1.60,
           's6': 0.45, 's7': 0.45, 's8': 0.45, 's9': 0.45, 's10': 2.20}
