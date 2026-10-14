"""Measure retained scenes and complete current PCM mapping; no media approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,wave
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'measured-current17-plan-v1.json';assert not out.exists()
base=read(OLD/'measured-additive-plan-v1.json');alloc=read(R/'paragraph-native-allocation-v4.json');pair=read(OLD/'final-pair-execution-v2.json')
assert len(base['scenes'])==14 and len(pair['pieces'])==20 and pair['exitCode']==0
for row in pair['pieces']:assert sha(ROOT/row['path'])==row['sha256']
for row in read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
retained=[copy.deepcopy(s) for s in base['scenes']];addition={s['insertAfter']:copy.deepcopy(s) for s in alloc['newScenes']}
scenes=[];placements=[];cursor=120;voice_map=[]
for old in retained:
 oldstart=old['startFrame'];old.update(startFrame=cursor,endFrame=cursor+old['frames'],retainedBaselineStartFrame=oldstart,retainedBaseline=True)
 assert sha(ROOT/old['voice'])==old['audioSha256']
 with wave.open(str(ROOT/old['voice']),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);n=w.getnframes()
 assert n<=old['frames']*400
 placements.append(dict(sceneId=old['id'],voice=old['voice'],sha256=old['audioSha256'],sourceStartSample=0,sourceEndSample=n,destinationStartSample=cursor*400,retainedOriginalWholePcm=True))
 scenes.append(old);cursor+=old['frames']
 if old['id'] not in addition:continue
 s=addition[old['id']];voice=alloc['voices'][s['id']];assert sha(ROOT/voice['path'])==voice['sha256']
 with wave.open(str(ROOT/voice['path']),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);ns=w.getnframes()
 s.update(startFrame=cursor,endFrame=cursor+s['frames'],voice=voice['path'],audioSha256=voice['sha256'],retainedBaseline=False)
 source_cursor=0;segments=[]
 for part in s['parts']:
  part['startFrame']=cursor+part['localStartFrame'];part['endFrame']=cursor+part['localEndFrame']
  vs=part.get('voiceSegments')
  if vs is None:vs=[] if part.get('voiceIn') is None else [dict(inSeconds=part['voiceIn'],outSeconds=part['voiceOut'],offsetFrame=part.get('voiceOffsetFrame',0))]
  for seg in vs:
   a=round(seg['inSeconds']*24000);b=round(seg['outSeconds']*24000);d=part['startFrame']*400+seg['offsetFrame']*400
   assert a==source_cursor,(s['id'],part['id'],a,source_cursor);source_cursor=b
   assert d+b-a<=part['endFrame']*400,(part['id'],d+b-a,part['endFrame']*400)
   entry=dict(sceneId=s['id'],partId=part['id'],voice=voice['path'],sha256=voice['sha256'],sourceStartSample=a,sourceEndSample=b,destinationStartSample=d,retainedOriginalWholePcm=False)
   placements.append(entry);segments.append(entry)
 assert source_cursor==ns,(s['id'],source_cursor,ns)
 s['currentPcmSamples']=ns;s['currentPcmSeconds']=ns/24000;s['voicePlacements']=segments
 boundaries=copy.deepcopy(voice['paragraphAndSentenceBoundaries'])
 if s['id']=='07b':boundaries[5]=34.56
 s['paragraphAndSentenceBoundaries']=boundaries
 # Correct stale explanatory prose without touching the historical allocation.
 if s['id']=='07b':
  s['parts'][0]['purpose']=s['parts'][0]['purpose'].replace('output1039/source33.35s','output991/source33.35s')
  s['parts'][7]['purpose']=s['parts'][7]['purpose'].replace('final17f','final11f')
 scenes.append(s);cursor+=s['frames']
assert len(scenes)==17
for a,b in zip(sorted(placements,key=lambda x:x['destinationStartSample']),sorted(placements,key=lambda x:x['destinationStartSample'])[1:]):assert a['destinationStartSample']+a['sourceEndSample']-a['sourceStartSample']<=b['destinationStartSample']
body=cursor-120;actual=base['actualFrames']+alloc['newActualFrames'];ex=base['explanationFrames']+alloc['newExplanationFrames']
assert body==actual+ex==50466 and actual==30280 and abs(actual-body*.6)<=1
plan=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),fps=60,baselinePlan=base,baselinePlanSha256=sha(OLD/'measured-additive-plan-v1.json'),
 allocation=alloc,allocationSha256=sha(R/'paragraph-native-allocation-v4.json'),scenes=scenes,voicePlacements=placements,retainedTwentySilentPieces=pair['pieces'],
 introFrames=120,outroFrames=600,bodyFrames=body,bodyEnd=cursor,totalFrames=cursor+600,seconds=(cursor+600)/60,actualFrames=actual,explanationFrames=ex,ratioErrorFrames=actual-body*.6,
 all14BaselineScenesAndPcmRetained=True,current3PcmAllSamplesMappedExactly=True,noSourcePcmDroppedOrTimeStretched=True,
 metadataCorrections=['07b current quiet clause boundary34.56 replaces historical voice metadata34.66; allocation part audio spans already use34.56.','Retained paragraph2 offset991 matches actual V4, not stale purpose1039.','Device ending observation11frames, not stale17.'],
 newGameTitles=alloc['gameTitles'],currentMixedAudioApproved=False,encodedFinalTimingApproved=False,finalRatioApproved=False,allFinalPixelsApproved=False,qaApproved=False,humanListeningApproved=False,publicRightsApproved=False)
out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=17,placements=len(placements),all3PcmSamplesMapped=True,body=body,total=cursor+600,actual=actual,explanation=ex,ratioError=plan['ratioErrorFrames'],mediaCreated=False)))
