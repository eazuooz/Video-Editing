from common import *
import urllib.request
O=R/'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official';O.mkdir(parents=True,exist_ok=True)
ident='1x6qgtd5OjyFvaUszfdEUi1WHf_SgAfZJ';dst=O/'release-date-trailer.mp4'
if not dst.exists():
 with urllib.request.urlopen('https://drive.usercontent.google.com/download?id='+ident+'&export=download&confirm=t',timeout=45) as response:
  assert 'text/html' not in response.headers.get('content-type',''),'Public media unavailable'
  with dst.with_suffix('.part').open('wb') as f:
   while chunk:=response.read(2**20):f.write(chunk)
 dst.with_suffix('.part').replace(dst)
meta=probe(dst);v=next(x for x in meta['streams'] if x['codec_type']=='video')
save(O/'source.json',dict(path=rel(dst),sha256=sha(dst),bytes=dst.stat().st_size,width=v['width'],height=v['height'],fps=v['avg_frame_rate'],duration=float(meta['format']['duration']),sourceUrl='https://drive.google.com/file/d/'+ident+'/view',officialPressEntry='https://pouncelight.games/tiny-glade/',officialPressFolder='https://drive.google.com/drive/folders/1xXuQQ68mg5yMY_HDyQPzra_jEHvw9jJ_',officialTrailerFolder='https://drive.google.com/drive/folders/1ZeX4BDtIHvGpq0LGXyBNoPiv-mr0nvoE',rightsBasis='Official developer press-kit distribution for contextual game coverage; not public domain. Inspect actual action and source audio before adopting.',role='candidate-only',downloadedAt=now()))
print(v['width'],v['height'],meta['format']['duration'])
