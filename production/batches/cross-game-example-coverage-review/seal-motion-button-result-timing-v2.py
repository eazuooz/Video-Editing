"""Correct one cross-source native-frame collision; preserve the held V1 board."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'button-result-timing-corrected-evidence-v2.json';assert not out.exists()
old=read(R/'button-result-timing-execution-v1.json');assert old['extractionExitCode']==0
try:
 p=psutil.Process(old['pid']);assert abs(p.create_time()-old['createTime'])>.01
except psutil.NoSuchProcess:pass
rows=[]
for w in read(R/'native-preflight-execution-v1.json')['windows']:
 if w['sourceKey']=='portal2':rows+=w['samples']
reuse={r['nativeFrame']:r for r in rows}
corrected=[]
for r in old['samples']:
 if r['reused']:
  ref=reuse[r['nativeFrame']];r=dict(r,path=ref['path'],sha256=ref['sha256'],sourceKey='portal2')
 else:r=dict(r,sourceKey='portal2')
 assert sha(ROOT/r['path'])==r['sha256'];corrected.append(r)
folder=ROOT/'shared/output/cross-game-example-coverage/motion/button-result-timing-v2';assert not folder.exists();folder.mkdir()
im=Image.new('RGB',(1920,1600),'#e8e8e8');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for k,r in enumerate(corrected[:12]):
 x=k%3*640;y=k//3*400;im.paste(Image.open(ROOT/r['path']).resize((640,360)),(x,y+40));d.text((x+8,y+8),f"Portal2 native{r['nativeFrame']} {r['pts']/30000:.6f}s",font=font,fill='black')
p=folder/'board-01-corrected.png';im.save(p)
proof=dict(schemaVersion=2,recordedAt=datetime.now(timezone.utc).isoformat(),priorExecution='button-result-timing-execution-v1.json',
 actualOuterCompletion='080fb7',actualOuterExitCode=0,actualWorkerAlive=False,
 heldV1Error='Native frame key omitted source identity and selected Alyx2938 as a Portal reuse. No final adoption occurred. All52 fresh decoded samples are Portal2 and retained unchanged; exact Portal2938 reference now substituted.',
 correctionDecodedNewFrames=0,correctedSamples=corrected,correctedFirstBoard=dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)),
 retainedUnaffectedBoards=old['boards'][1:],all54CurrentNativeFramesDirectlyReviewed=False,
 observedColorChange=dict(lastBlueNativeFrame=2947,firstYellowNativeFrame=2948,firstYellowPts=2948*1001,timeBase='1/30000',seconds=2948*1001/30000),
 eligibleTailNativeWindow=[2968,2992],eligibleTailHasYellowResultAndDoorDirection=True,promotionalMaterialObserved=False,
 finalNarrationTimingApproved=False,finalMovingPixelsApproved=False,mediaRegenerated=0,localOnly=True)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(correctedBoard=p.relative_to(ROOT).as_posix(),newDecodedSamples=0,reviewPending=True)))
