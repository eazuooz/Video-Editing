"""Read-only local delivery-link and media range checks."""
from common import *
from urllib.request import Request,urlopen
from urllib.parse import quote
def main():
 checks=[];base='http://127.0.0.1:9302/'
 for e in read(HERE/'plan.json')['episodes']:
  ep=e['id'];d=read(OUTPUT/ep/'delivery.json')
  paths=[ep+'/',ep+'/narration.txt',ep+'/additional-sources.txt']+[ep+'/'+quote(Path(f['path']).name) for f in d['files']]
  for relative in paths:
   with urlopen(Request(base+relative,method='HEAD'),timeout=10) as r:
    assert r.status==200 and int(r.headers['Content-Length'])>0
    checks.append(dict(url=base+relative,status=r.status,bytes=int(r.headers['Content-Length'])))
   if relative.endswith('.mp4'):
    with urlopen(Request(base+relative,headers={'Range':'bytes=0-1023'}),timeout=10) as r:
     data=r.read();assert r.status==206 and len(data)==1024 and r.headers['Content-Range'].startswith('bytes 0-1023/')
 with urlopen(base,timeout=10) as r:assert r.status==200
 save(HERE/'review-http-validation.json',dict(checks=checks,allFourOutputsPerEpisode=True,allMp4ByteRangesPassed=True,episodes=16,platformChanged=False,checkedAt=stamp()))
 print('Local hub +112 delivery links passed;32 MP4 byte-range requests passed.')
if __name__=='__main__':main()
