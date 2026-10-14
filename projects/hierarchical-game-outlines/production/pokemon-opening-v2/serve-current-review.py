from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import os,json,datetime,psutil
P=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(P),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',9250),Handler)
me=psutil.Process()
(P/'review-server-local.json').write_text(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),bind='127.0.0.1:9250',directory=str(P)),indent=2)+'\n',encoding='utf-8')
server.serve_forever()
