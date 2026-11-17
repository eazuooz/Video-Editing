"""Loopback-only review server with single-byte-range support for MP4 seeking."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import argparse,re,os
ROOT=Path(__file__).resolve().parent/'local/full-video-v2/final'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def end_headers(self):
        self.send_header('Accept-Ranges','bytes')
        super().end_headers()
    def send_head(self):
        self.remaining=None
        value=self.headers.get('Range')
        if not value:return super().send_head()
        path=Path(self.translate_path(self.path))
        if not path.is_file():return super().send_head()
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',value)
        size=path.stat().st_size
        if not match or not any(match.groups()):return self.invalid_range(size)
        a,b=match.groups()
        start=int(a) if a else max(0,size-int(b));end=min(size-1,int(b)) if a and b else size-1
        if start>=size or start>end:return self.invalid_range(size)
        stream=path.open('rb');stream.seek(start);self.remaining=end-start+1
        self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length',str(self.remaining));self.send_header('Last-Modified',self.date_time_string(os.fstat(stream.fileno()).st_mtime));self.end_headers()
        return stream
    def invalid_range(self,size):
        self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
    def copyfile(self,source,output):
        if self.remaining is None:return super().copyfile(source,output)
        while self.remaining:
            data=source.read(min(65536,self.remaining))
            if not data:break
            output.write(data);self.remaining-=len(data)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=9327);args=parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
