"""Servidor mínimo para previsualizar la intro (soporta Range para poder adelantar)."""
import os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = 'EVO_LABS_intro_1080p60.mp4'
VIDEO2 = 'EVO_LABS_EP01_Optimizacion_Windows_1080p60.mp4'
THUMB = 'EVO_LABS_thumbnail.jpg'

PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EVO LABS — Intro oficial</title>
<style>
  :root{color-scheme:dark}
  body{margin:0;background:#07090F;color:#E8EEF7;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  .wrap{max-width:1240px;margin:0 auto;padding:26px 18px 48px}
  h1{font-size:clamp(20px,3vw,30px);margin:0 0 4px;letter-spacing:.5px}
  h1 span{color:#FFC01E}
  p.sub{margin:0 0 18px;color:#8FA6BC;font-size:14px;letter-spacing:.14em;text-transform:uppercase}
  video{width:100%;border-radius:14px;background:#000;box-shadow:0 24px 70px rgba(0,0,0,.65);outline:1px solid #1B2436}
  .bar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:16px;font-size:14px;color:#9FB3C8}
  a.btn{display:inline-block;padding:10px 18px;border-radius:10px;text-decoration:none;font-weight:700;
    background:#FFC01E;color:#111;letter-spacing:.4px}
  a.ghost{background:transparent;color:#FFC01E;border:1px solid #3A2F12}
  code{background:#111826;padding:2px 7px;border-radius:6px;color:#7FE3F0}
</style></head><body><div class="wrap">
<h1>EVO LABS <span>|</span> Laboratorio de Software</h1>
<p class="sub">EP.01 — Optimización real de Windows · 1920×1080 · 60 fps · 3:02</p>
<video src="/ep01.mp4" controls autoplay preload="metadata" playsinline></video>
<div class="bar">
  <a class="btn" href="/ep01.mp4" download>Descargar EP.01</a>
  <a class="btn ghost" href="/subtitles-ep01.srt">Subtítulos .srt</a>
  <span>Sin animación de boca · voz de locutor · montaje al ritmo de la voz · transiciones (dissolve / flash / whip / glitch) · SFX en cada corte · subtítulos con palabras clave en <code>amarillo EVO</code></span>
</div>
<h1 style="margin-top:44px;font-size:22px">Intro general del canal <span>·</span> 1:37</h1>
<video src="/video.mp4" poster="/thumb.jpg" controls preload="none" playsinline style="margin-top:8px"></video>
<div class="bar">
  <a class="btn ghost" href="/video.mp4" download>Descargar intro</a>
</div>
</div></body></html>
"""


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def _send(self, code, ctype, body, extra=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-store')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            body = PAGE.encode()
            return self._send(200, 'text/html; charset=utf-8', b'' if head else body)
        mapping = {'/video.mp4': (VIDEO, 'video/mp4'), '/thumb.jpg': (THUMB, 'image/jpeg'),
                   '/subtitles.srt': ('EVO_LABS_intro.srt', 'application/x-subrip'),
                   '/ep01.mp4': (VIDEO2, 'video/mp4'),
                   '/subtitles-ep01.srt': ('EVO_LABS_EP01_Optimizacion_Windows_1080p60.srt',
                                           'application/x-subrip')}
        if path not in mapping:
            return self._send(404, 'text/plain; charset=utf-8', b'not found')
        name, ctype = mapping[path]
        fp = os.path.join(ROOT, name)
        if not os.path.exists(fp):
            return self._send(404, 'text/plain; charset=utf-8', b'not found')
        size = os.path.getsize(fp)
        rng = self.headers.get('Range')
        if rng:
            m = re.match(r'bytes=(\d*)-(\d*)', rng)
            start = int(m.group(1)) if m and m.group(1) else 0
            end = int(m.group(2)) if m and m.group(2) else size - 1
            end = min(end, size - 1)
            length = max(0, end - start + 1)
            self.send_response(206)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.send_header('Content-Length', str(length))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            if head:
                return
            with open(fp, 'rb') as f:
                f.seek(start)
                left = length
                while left > 0:
                    chunk = f.read(min(262144, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            return
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(size))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        if head:
            return
        with open(fp, 'rb') as f:
            while True:
                chunk = f.read(262144)
                if not chunk:
                    break
                self.wfile.write(chunk)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    ThreadingHTTPServer(('0.0.0.0', port), H).serve_forever()
