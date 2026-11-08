from pathlib import Path
import shutil,json,datetime
P=Path(__file__).resolve().parents[1];L=P/'production/local';B=L/'visual/preflight-revisions/word-cues-v2';B.mkdir(exist_ok=True)
files=[L/'visual'/f'scene-{id}{suffix}' for id in ['15','27','28'] for suffix in ['.mp4','.mp4.json']]
files+=[L/'final'/f'{P.name}.{kind}.mp4' for kind in ['clean','captioned']]
files+=[P/'production/technical-qa.json']
for f in files:
 assert f.resolve().is_relative_to(P.resolve()) and not (B/f.name).exists()
 shutil.move(f,B/f.name)
(P/'production/visual-cue-refinement.json').write_text(json.dumps({'scope':['15','27','28'],'reason':'Use actual word timestamps, not the earlier clause start, for expansion, Point/PPU and frame stepping. Step one actual atlas frame at a time at2Hz; retain native playback first. Earlier time increment skipped6frames and was corrected before delivery.','audioUnchanged':True,'earlierMastersPreserved':str(B),'requiresNewEncodedReview':True},indent=2)+'\n','utf-8')
print(B)
