"""Inspect public official ZIP central directories with bounded HTTP byte ranges."""
from common import *
import io,urllib.request,zipfile
class RemoteZip(io.RawIOBase):
 def __init__(self,url):
  self.url=url;self.pos=0;self.size=int(urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30).headers['Content-Length']);self.bytes=0
 def seekable(self):return True
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  n=min(n,self.size-self.pos)
  if not n:return b''
  assert n<8*1024*1024,'Bounded directory inspection only'
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={self.pos}-{self.pos+n-1}'})
  with urllib.request.urlopen(req,timeout=30) as r:
   assert r.status==206,'No range support; do not fetch entire archive';data=r.read(n)
  self.pos+=len(data);self.bytes+=len(data);return data
if __name__=='__main__':
 out=[]
 for url in ['https://mirror.keenswh.com/PressKits/Space-Engineers.zip','https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip']:
  r=RemoteZip(url)
  with zipfile.ZipFile(r) as z:items=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size) for i in z.infolist()]
  out.append(dict(url=url,archiveBytes=r.size,downloadedBytes=r.bytes,items=items));print(json.dumps(dict(url=url,downloadedBytes=r.bytes,files=len(items)),ensure_ascii=False))
 save(B/'keen-presskit-inventory.json',dict(checkedAt=now(),archives=out))
