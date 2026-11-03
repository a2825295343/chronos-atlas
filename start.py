"""Run the built desktop-local atlas. Python standard library only."""
import argparse
import functools
import http.server
import pathlib
import threading
import re
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent
TERRAIN_REQUESTS = threading.BoundedSemaphore(6)
TERRAIN_LOCK = threading.Lock()
TILE_LOCKS = {}

def terrain_tile(z, x, y):
    """Return a locally cached, authentic Terrarium tile; never upsample fake detail."""
    bundled = ROOT / 'public' / 'data' / 'dem' / str(z) / str(x) / f'{y}.png'
    if bundled.is_file(): return bundled.read_bytes()
    cached = ROOT / '.local' / 'terrain' / str(z) / str(x) / f'{y}.png'
    with TERRAIN_LOCK:
        lock = TILE_LOCKS.setdefault((z, x, y), threading.Lock())
    with lock:
        if cached.is_file(): return cached.read_bytes()
        with TERRAIN_REQUESTS:
            request = urllib.request.Request(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png', headers={'User-Agent':'GuanlanAtlas/1.1'})
            with urllib.request.urlopen(request, timeout=12) as response:
                data = response.read(4 * 1024 * 1024)
            if not data.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Invalid elevation image')
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(data)
            return data

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.geojson':'application/geo+json','.ttf':'font/ttf'}
    def log_message(self, *_): pass
    def end_headers(self):
        # Local data files keep stable URLs across builds; always validate them.
        path=urllib.parse.urlparse(self.path).path
        if path=='/' or path.endswith(('.html','.json','.geojson')):
            self.send_header('Cache-Control','no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == '/api/map-capabilities':
            data = b'{"terrainProxy":true,"offlineMaxZoom":5,"onlineMaxZoom":12}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        match = re.fullmatch(r'/terrain/(\d{1,2})/(\d{1,5})/(\d{1,5})\.png',path)
        if match:
            z,x,y = map(int,match.groups())
            if not (0 <= z <= 12 and 0 <= x < 2**z and 0 <= y < 2**z):
                self.send_error(404); return
            try:
                data = terrain_tile(z,x,y)
            except (OSError,ValueError,urllib.error.URLError):
                self.send_error(503,'Detailed terrain unavailable. Bundled lower zooms remain available.');return
            self.send_response(200)
            self.send_header('Content-Type','image/png')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','public, max-age=31536000, immutable')
            self.end_headers()
            try:self.wfile.write(data)
            except (ConnectionError,OSError):pass
            return
        super().do_GET()

def main():
    parser=argparse.ArgumentParser(description='Guanlan local historical atlas')
    parser.add_argument('--port',type=int,default=8877)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    if not (ROOT/'dist'/'index.html').exists():
        raise SystemExit('Build missing. Run npm install and npm run build first.')
    handler=functools.partial(Handler,directory=str(ROOT/'dist'))
    for port in range(args.port,args.port+10):
        try:
            server=http.server.ThreadingHTTPServer(('127.0.0.1',port),handler)
            break
        except OSError:
            if port==args.port+9:raise
    url=f'http://127.0.0.1:{server.server_port}/'
    print(f'Guanlan / CHRONOS is running: {url}\nPress Ctrl+C to stop.',flush=True)
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
