"""One official presskit media member, streamed directly; no archive extraction/execution."""
from common import *
import urllib.request,zipfile,struct,importlib.util,zlib,sys
spec=importlib.util.spec_from_file_location('remotezip',B/'inspect-keen-presskit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
url='https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip'
launch='--launch' in sys.argv
member='Official Trailers/Space Engineers 2 Official Early Access Launch Trailer.mp4' if launch else 'Official Trailers/Space Engineers 2 - Official VS1.2 Trailer.mp4'
folder=R/'shared/output/private-math-concept-fit-20261023/sources/se2-official';folder.mkdir(parents=True,exist_ok=True)
stem='launch' if launch else 'vs1.2';dest=folder/(stem+'.mp4');part=folder/(stem+'.mp4.part')
r=m.RemoteZip(url)
with zipfile.ZipFile(r) as z:info=z.getinfo(member)
assert info.compress_type==0 and info.file_size<1400*1024**2
r.seek(info.header_offset);header=r.read(30);fields=struct.unpack('<4s5H3I2H',header);assert fields[0]==b'PK\x03\x04'
offset=info.header_offset+30+fields[-2]+fields[-1]
if not dest.exists():
 existing=part.stat().st_size if part.exists() else 0;assert existing<=info.file_size
 if existing<info.file_size:
  request=urllib.request.Request(url,headers={'Range':f'bytes={offset+existing}-{offset+info.file_size-1}'})
  with urllib.request.urlopen(request,timeout=60) as response,part.open('ab') as out:
   assert response.status==206
   while True:
    block=response.read(4*1024**2)
    if not block:break
    out.write(block)
  assert part.stat().st_size==info.file_size
 crc=0
 with part.open('rb') as f:
  for block in iter(lambda:f.read(4*1024**2),b''):crc=zlib.crc32(block,crc)
 assert crc==info.CRC
 part.rename(dest)
meta=probe(dest);video=next(s for s in meta['streams'] if s['codec_type']=='video');assert video['height']>=1080
save(folder/(stem+'-source.json'),dict(downloadedAt=now(),sourceUrl='https://www.keenswh.com/press/',archiveUrl=url,member=member,path=rel(dest),sha256=sha(dest),bytes=dest.stat().st_size,width=video['width'],height=video['height'],fps=video['avg_frame_rate'],duration=meta['format']['duration'],rights=dict(urls=['https://2.spaceengineersgame.com/eula/','https://www.keenswh.com/press/'],basis='Official publisher presskit; EULA section10 permits incorporation of official promotional videos and game visuals/audio in freely available media-site content with platform-ad monetization; publisher states game soundtracks owned.',constraints='No endorsement, standalone asset resale, or third-party copyrighted inclusions. Inspect actual excerpt and audio before adoption.'),status='candidate-not-adopted-awaiting-actual-viewing'))
print(json.dumps(dict(path=rel(dest),width=video['width'],height=video['height'],seconds=meta['format']['duration']),ensure_ascii=False),flush=True)
