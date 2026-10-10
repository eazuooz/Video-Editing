"""Print whole actual comparison data; never approve it automatically."""
from pathlib import Path
import argparse,json
b=Path(__file__).resolve().parent/'final-v1';a=argparse.ArgumentParser();a.add_argument('--start',type=int,default=1);a.add_argument('--count',type=int,default=5);v=a.parse_args()
d=json.loads((b/'mixed-asr-v1/asr.json').read_text('utf-8-sig'))
print(json.dumps(dict(completed=len(d['results']),complete=d['complete'])))
for idx,r in enumerate(d['results'][v.start-1:v.start-1+v.count],v.start):
 print(json.dumps(dict(index=idx,label=r['label'],expectedKo=r['expectedKo'],actualText=r['text'],actualAllWords=r['words'],windowPath=r['windowPath'],windowSha256=r['windowSha256'],fullPcmSliceVerified=r['exactStereoMixSampleBytesMatched']),ensure_ascii=False))
