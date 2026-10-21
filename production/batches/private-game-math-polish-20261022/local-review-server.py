"""Loopback-only review server with byte ranges for seeking final local MP4s."""
import http.server,mimetypes,re,sys
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[3]
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):self.serve(False)
 def do_HEAD(self):self.serve(True)
 def serve(self,head):
  p=(ROOT/unquote(urlsplit(self.path).path).lstrip('/')).resolve()
  if not p.is_relative_to(ROOT) or not p.is_file():self.send_error(404);return
  length=p.stat().st_size;start,end=0,length-1;partial=False
  header=self.headers.get('Range')
  if header:
   match=re.fullmatch(r'bytes=(\d+)-(\d*)',header)
   if not match:self.send_error(416);return
   start=int(match[1]);end=min(int(match[2]) if match[2] else end,end);partial=True
   if start>end:self.send_error(416);return
  self.send_response(206 if partial else 200);self.send_header('Content-Type',mimetypes.guess_type(p)[0] or 'application/octet-stream')
  self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{length}')
  self.end_headers()
  if head:return
  try:
   with p.open('rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     data=f.read(min(1024*1024,remaining))
     if not data:break
     self.wfile.write(data);remaining-=len(data)
  except (ConnectionAbortedError,ConnectionResetError,BrokenPipeError):pass
if __name__=='__main__':
 http.server.ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1])),Handler).serve_forever()
