# EVO LABS — Intro oficial (Laboratorio de Software)

Intro cinematográfica para el canal [@EvoLabsSoftware](https://www.youtube.com/@EvoLabsSoftware),
protagonizada por el avatar oficial del canal y construida en un pipeline 100 % reproducible
desde este repositorio.

## Entregables

| Archivo | Descripción |
|---|---|
| `EVO_LABS_intro_1080p60.mp4` | Intro final: **1920×1080 · 60 fps · 97,5 s · H.264 High + AAC 256 kbps** |
| `EVO_LABS_thumbnail.jpg` | Miniatura 1280×720 para YouTube |
| `EVO_LABS_intro.srt` | Subtítulos sincronizados (mismos textos que los quemados en imagen) |
| `assets/scenes/` | Láminas maestras del universo EVO (arte de cada plano) |
| `assets/audio/` | Líneas de voz en off (español rioplatense) |
| `refs/` | Referencias de marca del canal (avatar, poses, banner) |


## EP.01 — Optimización real de Windows (entrega principal)

| Archivo | Descripción |
|---|---|
| `EVO_LABS_EP01_Optimizacion_Windows_1080p60.mp4` | **1920×1080 · 60 fps · 3:02** · voz de locutor rioplatense, sin animación de boca |
| `EVO_LABS_EP01_thumbnail.jpg` | Miniatura 1280×720 del episodio |
| `EVO_LABS_EP01_Optimizacion_Windows_1080p60.srt` | Subtítulos sincronizados |

Guion completo del descargo, sin recortes: apertura y presentación del tema, el descargo contra los
títulos de "999 FPS", la promesa editorial (años de pruebas), el método adaptativo por etapas,
"acá hacemos milagros, pero los comprobamos", el anti-humo de los 8 minutos perdidos, la crítica a
WinUtil / Chris Titus (con el reconocimiento de que sirvió en su momento), la aclaración de que todo
se explica para que lo entiendas y puedas ejecutarlo, el "desenmascarar el verdadero potencial de
Windows" y el cierre "COMENCEMOS DE UNA VEZ".

Capítulos: 01 Apertura · 02 El descargo · 03 La promesa · 04 El método · 05 Milagros comprobados ·
06 Sin humo · 07 WinUtil y cía. · 08 Transparencia · 09 Desenmascarar · 10 Comencemos.

Motion graphics propios del episodio: terminal con comandos reales de PowerShell
(`powercfg /list`, `Get-CimInstance Win32_StartupCommand`, `Get-Service`, `dism /analyzecomponentstore`,
`Measure-Command`), panel de servicios reales de Windows (SysMain, WSearch, DiagTrack, Xbox Game Bar,
Windows Update) con estado ON/OFF, medidor de telemetría en vivo, comparativa A/B ("sin cambios" vs
"optimizado", mismo hardware), diagrama del método en 4 etapas y placa de la regla Nº1.

```bash
EVO_EP=ep01 python3 pipeline/audio.py     # música + SFX + mezcla del episodio
EVO_EP=ep01 python3 pipeline/segments.py  # cámara y grading -> build/work_ep01/base.mp4
EVO_EP=ep01 python3 pipeline/compose.py   # HUD, subtítulos, end card -> MP4 final
python3 pipeline/serve.py 8000            # reproductor local con Range (adelantar/retroceder)
```

La configuración vive en `pipeline/ep01.py` (guion, tiempos, planos, cámaras y capítulos). El motor
de `pipeline/audio.py`, `segments.py` y `compose.py` es el mismo para cualquier episodio.

### Notas del episodio

- **Voz v2 (locutor profesional)**: lectura con más énfasis, pausas marcadas y acento rioplatense;
  cadena de audio de locución (presencia, compresión 3:1, saturación suave) y *ducking* más profundo
  de la música para que la voz quede siempre al frente.
- **Sin animación de boca**, como se pidió: el personaje se mueve por cámara, glow reactivo a la voz
  y partículas; la boca queda tal cual el arte original.
- No se muestran porcentajes ni FPS inventados. El "999 FPS" aparece únicamente como recurso gráfico
  satírico del título que se critica. Las etiquetas de rendimiento son cualitativas (A/B, PASS, EN VIVO).
- Se respetó el tono: humor y código argentino, críticas frontales, sin volverlo corporativo.

## Intro general del canal (1:37)

Guion y estructura (timeline real)

| # | Capítulo | In | Out | Voz en off |
|---|---|---|---|---|
| 01 | Apertura (encendido de sistemas → logo → avatar) | 00:00 | 00:14,7 | 7,5 s |
| 02 | Universo EVO | 00:14,7 | 00:24,7 | 15,0 s |
| 03 | Ring de agentes | 00:24,7 | 00:32,3 | 25,0 s |
| 04 | Experimentación (PC, juegos, FPS) | 00:32,3 | 00:42,5 | 32,6 s |
| 05 | Nuestra promesa | 00:42,5 | 00:52,7 | 42,9 s |
| 06 | IA & oportunidades | 00:52,7 | 01:07,7 | 53,0 s |
| 07 | Diferenciación (humo vs. resultados) | 01:07,7 | 01:19,1 | 68,0 s |
| 08 | Gran final + end card | 01:19,1 | 01:37,5 | 79,4 s |

Todo el guion original está presente, sin recortes: apertura, universo, ring, experimentación,
promesa, IA y oportunidades, diferenciación y final con llamado a la suscripción.

## Dirección de arte

- **Identidad:** negro profundo `#0A0E1A`, amarillo EVO `#FFC01E`, naranja de marca `#F26522`,
  blanco, cian `#22D3EE`; verde `#34D366` para resultados, rojo `#EF4444` para alertas.
- **Avatar:** el personaje oficial (pelo blanco en punta, antiparras con lentes cian, guardapolvo
  crema con franjas naranjas, remera cian) se mantiene idéntico en todos los planos; las láminas se
  generaron usando `refs/` como referencia de identidad.
- **Cámara:** cada plano tiene movimiento propio (zoom + desplazamiento con easing), grading,
  viñeta, grano y aberración cromática leve. No hay imágenes estáticas.
- **Motion graphics:** logo EVO construido en código, HUD de laboratorio, callouts sobre las
  holografías, marcador del ring, banco de pruebas, placas de promesa, split-screen comparativo,
  end card con botón de suscripción y cursor.
- **Audio:** música electrónica cinematográfica **original** sintetizada muestra por muestra
  (numpy), efectos sincronizados y *ducking* automático bajo la voz. Normalizado a ≈ −14 dBFS
  de media, pico limitado.

## Pipeline (reproducible)

```bash
pip install imageio-ffmpeg pillow numpy     # ffmpeg incluido en el paquete

python3 pipeline/plates.py      # 1. láminas procedurales (logo, promesa, split, outro)
python3 pipeline/segments.py    # 2. pass A: movimiento de cámara + grading  -> build/work/base.mp4
python3 pipeline/audio.py       # 3. música original + SFX + mezcla + envolvente de lab-sync
python3 pipeline/compose.py     # 4. pass B: HUD, subtítulos, partículas, hitos -> MP4 final
python3 pipeline/poster.py      # 5. miniatura 1280x720
python3 pipeline/qc.py 44 88    # opcional: frames de control en build/qc/
```

`pipeline/cfg.py` es la única fuente de verdad: paleta, timeline, textos de voz, coordenadas de
boca, cámaras y capítulos. Cambiar ahí recalcula audio, video y subtítulos de forma consistente.

Los archivos intermedios se generan en `build/` (ignorado por git).

## Notas técnicas honestas

- La animación del personaje es 2D: **apertura de boca sincronizada con la envolvente real de la
  voz** (60 muestras/s), más desplazamientos de cámara, glow reactivo y partículas. No es
  captura de performance ni renderizado 3D del avatar.
- La música y los efectos son síntesis procedural original: no hay samples de terceros, así que
  no hay riesgo de reclamos de derechos.
- No se muestran cifras de benchmark ni resultados inventados: los HUD usan etiquetas y barras
  cualitativas (TEST, PASS, ALERTA, MEDIDO · REPETIBLE).
- El guion menciona marcas (Claude Sonnet, Ollama) tal como lo escribió el canal, criticando
  promesas sin pruebas; en pantalla no se afirma nada verificable sobre ellas.
