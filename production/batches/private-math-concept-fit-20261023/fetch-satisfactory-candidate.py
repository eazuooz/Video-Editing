"""Download the public official press-kit master; no user cookies or credentials."""
from common import *
import urllib.request
source='https://drive.usercontent.google.com/download?id=1BylogVwrSRxlwGJm0fva3HW4eOPDoHs_&export=download&confirm=t'
O=R/'shared/output/private-math-concept-fit-20261023/sources/satisfactory-official';O.mkdir(parents=True,exist_ok=True)
dst=O/'SATISFACTORY_1.2_LAUNCHTRAILER_MASTER.mp4'
if not dst.exists():
 with urllib.request.urlopen(source,timeout=45) as response:
  assert 'text/html' not in response.headers.get('content-type',''),'No media response; do not save HTML as video'
  with dst.with_suffix('.part').open('wb') as f:
   while chunk:=response.read(2**20):f.write(chunk)
 dst.with_suffix('.part').replace(dst)
meta=probe(dst);video=next(x for x in meta['streams'] if x['codec_type']=='video');assert video['width']>=1920 and video['height']>=1080
save(O/'source.json',dict(file=rel(dst),sha256=sha(dst),bytes=dst.stat().st_size,width=video['width'],height=video['height'],fps=video['avg_frame_rate'],duration=float(meta['format']['duration']),sourceUrl='https://drive.google.com/file/d/1BylogVwrSRxlwGJm0fva3HW4eOPDoHs_/view',officialPressPage='https://www.satisfactorygame.com/press/',officialFolder='https://drive.google.com/drive/u/0/folders/1z5STGEvaRW3zKlVZFjyDIva95RhLwJ4i',role='candidate-only',actionReview='pending',rightsBasis='Official press/content-creator page directly provides public presskit including this master; contextual game coverage only, not public domain. Inspect audio and any third-party restrictions before adoption.',downloadedAt=now()))
print(json.dumps(dict(bytes=dst.stat().st_size,width=video['width'],height=video['height'],seconds=meta['format']['duration'])))
