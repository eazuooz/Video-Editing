"""Loopback-only byte-range preview of preserved official MP4s."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / 'shared/assets/presenting-game-scores/raw'

class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(MEDIA), **kwargs)

    def send_head(self):
        self.byte_range = None
        p = Path(self.translate_path(self.path))
        request_range = self.headers.get('Range')
        if p.is_file() and request_range:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', request_range)
            if match and (match[1] or match[2]):
                total = p.stat().st_size
                if match[1]:
                    start = int(match[1]); end = int(match[2]) if match[2] else total - 1
                else:
                    start = max(0, total - int(match[2])); end = total - 1
                end = min(end, total - 1)
                if start > end or start >= total:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{total}')
                    self.end_headers()
                    return None
                stream = p.open('rb')
                stream.seek(start)
                self.byte_range = end - start + 1
                self.send_response(206)
                self.send_header('Content-Type', self.guess_type(str(p)))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{total}')
                self.send_header('Content-Length', str(self.byte_range))
                self.end_headers()
                return stream
        return super().send_head()

    def copyfile(self, source, output):
        remaining = self.byte_range
        if remaining is None:
            return super().copyfile(source, output)
        while remaining:
            block = source.read(min(65536, remaining))
            if not block:
                break
            output.write(block)
            remaining -= len(block)

if __name__ == '__main__':
    print(f'Native source preview: {MEDIA}; loopback9250; byte ranges enabled', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 9250), PreviewHandler).serve_forever()
