"""Compare decoded review pixels after the approved six-cut-only correction."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import audio_pipeline as a
H=Path(__file__).resolve().parent
DELTA={'c025','c026','c027','c028','c030','c032'}
def main():
 old=a.read(H/'edit-plan.before-contrast-v2.json');new=a.read(H/'edit-plan.contrast-v2.json')
 before=a.read(a.repo_path(old['outputDir'])/'qa/v2/evidence.json')
 after=a.read(a.repo_path(new['outputDir'])/'qa/v1/evidence.json')
 assert before['allCaptionCuesCovered'] and after['allCaptionCuesCovered']
 records=[];seen=set()
 for cut in new['cuts']:
  if cut['id'] in DELTA:continue
  prior={f['frame']:f for f in before['cuts'][cut['id']]['nativeFrames']}
  for row in after['cuts'][cut['id']]['nativeFrames']:
   f=row['frame']
   # The adjacent frame belongs to another cut and may intentionally change.
   if not cut['startFrame']<=f<cut['endFrame'] or f in seen:continue
   seen.add(f);left=a.repo_path(prior[f]['path']);right=a.repo_path(row['path'])
   b=np.asarray(Image.open(left)).astype(np.int16);c=np.asarray(Image.open(right)).astype(np.int16)
   diff=np.abs(b-c);mae=float(diff.mean());maximum=int(diff.max());identical=maximum==0
   records.append({'cutId':cut['id'],'frame':f,'prior':prior[f]['path'],'current':row['path'],'identicalDecodedPixels':identical,'meanAbsolute8bitDifference':mae,'maxAbsolute8bitDifference':maximum})
 result={'status':'computed-not-review-substitute','oldMaster':before['captionedMp4'],'newMaster':after['captionedMp4'],'unchangedCutIds':[c['id'] for c in new['cuts'] if c['id'] not in DELTA],'approvedDeltaCutIds':sorted(DELTA),'sampledFrames':len(records),'identicalFrames':sum(r['identicalDecodedPixels'] for r in records),'maximumMeanDifference':max(r['meanAbsolute8bitDifference'] for r in records),'records':records,'interpretation':'Exact decoded n and identical JPEG extraction parameters. Identical pixels transfer the previous direct review for that state; any non-identical state requires bounded review rather than an assumed pass.'}
 a.save(H/'final-frame-preservation.json',result)
 print(json.dumps({k:result[k] for k in ['sampledFrames','identicalFrames','maximumMeanDifference']}))
if __name__=='__main__':main()
