"""Fetch two public developer-supplied press assets, without account credentials."""
from common import *
import urllib.request
O=R/'shared/output/private-math-concept-fit-20261023/sources/escape-simulator-official';O.mkdir(parents=True,exist_ok=True)
items=[('1kBroCcuJ24P7dHbf-FvEZDeWOWW1-ln-','ES_LevelEditor_v3.mp4'),('1fBy6C2b4KQ-DKC4DxL7R1zhE_GZwp9sx','DaVinciTrailer1.mp4')]
for ident,name in items:
 dst=O/name
 if not dst.exists():
  with urllib.request.urlopen('https://drive.usercontent.google.com/download?id='+ident+'&export=download&confirm=t',timeout=45) as response:
   assert 'text/html' not in response.headers.get('content-type',''),'Public media unavailable'
   with dst.with_suffix('.part').open('wb') as f:
    while chunk:=response.read(2**20):f.write(chunk)
  dst.with_suffix('.part').replace(dst)
 meta=probe(dst);video=next(x for x in meta['streams'] if x['codec_type']=='video')
 save(O/(dst.stem+'.json'),dict(path=rel(dst),sha256=sha(dst),bytes=dst.stat().st_size,width=video['width'],height=video['height'],fps=video['avg_frame_rate'],duration=float(meta['format']['duration']),sourceUrl='https://drive.google.com/file/d/'+ident+'/view',officialPressPage='https://docs.escapesimulator.com/docs/press',officialFolder='https://drive.google.com/drive/folders/1hAasj716_Wk-zxzpI1lPIHGSWgZKR5U8',role='candidate-only',rightsBasis='Pine Studio public press kit, for contextual game coverage; not public domain. Audio and source suitability must be reviewed before adoption.',actualActionReview='pending',downloadedAt=now()))
 print(name,video['width'],video['height'],meta['format']['duration'],flush=True)
