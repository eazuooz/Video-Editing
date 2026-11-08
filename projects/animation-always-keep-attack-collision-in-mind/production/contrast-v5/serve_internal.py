"""Internal A16 playback check, loopback only. Not the user's combined delivery."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import re,mimetypes,json,datetime
ROOT=Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review/A16')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def do_POST(self):
  if self.path!='/events':self.send_error(404);return
  try:
   v=json.loads(self.rfile.read(min(int(self.headers.get('Content-Length','0')),12000)))
   v['receivedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
   with (ROOT/'internal-browser-events.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(v,ensure_ascii=False)+'\n')
   self.send_response(204);self.end_headers()
  except Exception:self.send_error(400)
 def do_GET(self):
  p=Path(self.translate_path(self.path));rng=self.headers.get('Range')
  if rng and p.is_file():
   m=re.fullmatch(r'bytes=(\d+)-(\d*)',rng)
   if not m:self.send_error(416);return
   n=p.stat().st_size;a=int(m[1]);b=min(int(m[2])if m[2]else n-1,n-1)
   if a>b:self.send_error(416);return
   self.send_response(206);self.send_header('Content-Type',mimetypes.guess_type(p)[0]or'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {a}-{b}/{n}');self.send_header('Content-Length',str(b-a+1));self.end_headers()
   try:
    with p.open('rb')as f:
     f.seek(a);left=b-a+1
     while left:
      chunk=f.read(min(left,1<<20));self.wfile.write(chunk);left-=len(chunk)
   except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
   return
  super().do_GET()
 def log_message(self,*a):pass
ThreadingHTTPServer(('127.0.0.1',9295),Handler).serve_forever()
