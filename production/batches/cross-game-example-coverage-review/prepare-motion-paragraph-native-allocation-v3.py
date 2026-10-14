"""Measure retained narration against unique source actions; no media render."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,math
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'paragraph-native-allocation-v3.json';assert not out.exists()
old=read(ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1/measured-additive-plan-v1.json')
bank=read(R/'sources/source-action-bank-v1.json');source={s['key']:s for s in bank['sources']}
voice={
'07b':('shared/output/narration/motion-sickness-games/cross-game-four-repaired-v1/chunks/07b-scene.wav',[0,8.32,17.66,26.28,29.11,34.66,42.33,48.6975]),
'08b':('shared/output/narration/motion-sickness-games/cross-game-four-additions-v1/chunks/08b-scene.wav',[0,8.68,17.32,25.70,32.60,40.24]),
'11b':('shared/output/narration/motion-sickness-games/cross-game-four-additions-v1/chunks/11b-scene.wav',[0,33.28])}
for sid,(path,bounds) in voice.items():
 assert (ROOT/path).exists(),path
 with wave.open(str(ROOT/path),'rb') as w:
  assert w.getframerate()==24000 and w.getnchannels()==1
  assert abs(w.getnframes()/24000-bounds[-1])<1/24000
def ex(sid,frames,path,pcm0,pcm1,purpose):return dict(id=sid,classification='explanation',frames=frames,reuseVideo=path,voiceIn=pcm0,voiceOut=pcm1,purpose=purpose)
def act(sid,key,n0,n1,frames,purpose,voice_in=None,voice_out=None,voice_offset=0,source_offset=0):
 s=source[key]
 return dict(id=sid,classification='actual-existing-game-action',sourceKey=key,sourcePath=s['path'],sourceSha256=s['sha256'],nativeInFrame=n0,nativeOutFrameExclusive=n1,
  nativeTimeBase=s['video']['time_base'],nativePtsStep=1001,nativeFps=s['video']['avg_frame_rate'],normalSpeed=1,loop=False,slowdown=False,frames=frames,
  sourceOutputStartFrame=source_offset,voiceIn=voice_in,voiceOut=voice_out,voiceOffsetFrame=voice_offset,purpose=purpose,
  transitionLabel='독립 시연 구간 · 실제 관찰',sourceAudioUsed=False,allNarrationTimedPixelsApproved=False)
E='shared/output/cross-game-example-coverage/motion/narration-timed-comparisons-v1/'
parts7=[
 act('07b-prerequisite-and-cube-room','portal2',480,1199,1439,'P1 introduces the puzzle and its two goals. Unique laser/view/portal actions continue during the search instruction; P2 begins at output1039/source33.35s so red-cube words coincide with source38.7s. No portal travel claim.',0,8.32),
 act('07b-cube-room-prefix','portal2',1289,1739,161,'Complete P2 over the next independent held-cube/room view at43–45.7s. Cyan room cue words are spoken here; markers hide around uncertain putdown.',8.32,17.66,source_offset=0),
 ex('07b-role',518,E+'scene-07b-role.mp4',17.66,26.28,'Retained timed projected comparison: held cube versus earlier independently aimed tool.'),
 act('07b-cube-room-observe','portal2',1289,1739,739,'Continue remaining unique source45.7–58s: putdown, portal placement, pickup, redirected beam. Observe held object versus changed room after the spoken comparison.',source_offset=161),
 act('07b-laser-target','portal2',2098,2458,720,'First observe cube/room aiming70–77s. Speak the independent laser-to-device sentence at77–79.85s while the blue-X/yellow-check result is visible; then retain the result/stairs endpoint.',26.28,29.11,420),
 act('07b-cube-button','portal2',2518,2968,900,'Before/action/result: stairs/button84–86, floor portal87–90, emerging cube91–93, held cube94–99 and blue-to-yellow result. Speak the second independent-example sentence only after9.45s setup.',29.11,34.66,567),
 act('07b-room-reacquire','portal2',1739,1859,240,'P5 uses an explicitly separate room/beam view to read direction after change.',34.66,38.66),
 act('07b-device-reacquire','portal2',1919,2038,238,'Continue P5 over the visible wall device64–68s; omit unclear ceiling views. Retain final17f as observation.',38.66,42.33),
 ex('07b-limit',383,E+'scene-07b-limit.mp4',42.33,48.6975,'Retained causal limitation: manipulation/view relationships, not portal-travel or personal comfort testing.')]
# The first long piece carries P1, a prompted search, then the first400f of P2.
parts7[0]['voiceSegments']=[dict(inSeconds=0,outSeconds=8.32,offsetFrame=0),dict(inSeconds=8.32,outSeconds=14.986666666666666,offsetFrame=1039)]
parts7[0]['voiceIn']=parts7[0]['voiceOut']=None
parts7[1]['voiceIn']=14.986666666666666
pw=read(R/'narration-led-cut-allocation-proposal-v2.json')['cuts'][1]
parts8=[
 ex('08b-intro',521,E+'scene-08b-intro.mp4',0,8.68,'VR prerequisite and choose/move overview before using the game UI.'),
 ex('08b-arrival',519,E+'scene-08b-arrival.mp4',8.68,17.32,'Yellow destination and arrival direction in narrated order; then observe the actual game without slowing or freezing.'),
 act('08b-destination-observe','alyx',2938,3117,179,'Unique49–52s destination feet then viewpoint change. Hide destination marker3063–3069 transition bracket; no invented travel trajectory.'),
 act('08b-board-removal','alyx',3237,4136,899,'P3 introduces the board-removal task over54–62.4s before hands finish removing boards60–65; retain unique result/clear path/destination67–69.',17.32,25.70),
 dict(id='08b-tool-and-common-question',classification='actual-existing-game-action',frames=781,sourceKey='powerwash',sourcePath=pw['path'],sourceSha256=pw['sha256'],nativeInFrame=14040,nativeOutFrameExclusive=14821,nativeTimeBase='1/15360',nativePtsStep=256,nativeFps='60/1',sourceOutputStartFrame=0,normalSpeed=1,loop=False,slowdown=False,voiceIn=25.70,voiceOut=32.60,voiceOffsetFrame=0,
 purpose='P4 explicitly compares previously seen tool/cube/hand roles. Unique234–247s action shows tool body moving against small-house reference; continue the instructed comparison after the voice. Tool body is not nozzle tip or world axis.',transitionLabel='다른 게임의 비교 · 독립 시연 구간',sourceAudioUsed=False,allNarrationTimedPixelsApproved=False),
 act('08b-locker-orientation','alyx',6534,6834,300,'Explicit independent109–114s arrival/locker/room comparison under the common-question instruction. Visible context change; no unspoken claim of touching locker or comfort improvement.'),
 ex('08b-limit',459,E+'scene-08b-limit.mp4',32.60,40.24,'Separate visible orientation reading from individual comfort.')]
parts11=[ex('11b-summary',1997,'shared/output/cross-game-example-coverage/motion/narration-timed-summary-v1/scene-11b.mp4',0,33.28,'Four-game common question, differences and return to retained conclusion.')]
# Verify reusable video names against execution rather than guessing paths.
summary=read(R/'narration-timed-summary-render-execution-v1.json')
def find_video(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ('path','output','outputFile') and isinstance(x,str) and x.endswith('.mp4') and (ROOT/x).exists():return x
   q=find_video(x)
   if q:return q
 if isinstance(v,list):
  for x in v:
   q=find_video(x)
   if q:return q
parts11[0]['reuseVideo']=find_video(summary)
assert parts11[0]['reuseVideo']
for parts in [parts7,parts8,parts11]:
 cursor=0
 for p in parts:
  p.update(localStartFrame=cursor,localEndFrame=cursor+p['frames']);cursor+=p['frames']
  if p['classification']=='explanation':
   assert (ROOT/p['reuseVideo']).exists(),p['reuseVideo'];p['videoSha256']=sha(ROOT/p['reuseVideo'])
  else:assert sha(ROOT/p['sourcePath'])==p['sourceSha256']
 actual=sum(p['frames'] for p in parts if p['classification'].startswith('actual'))
print('actual/ex',[(sum(p['frames'] for p in x if p['classification'].startswith('actual')),sum(p['frames'] for p in x if p['classification']=='explanation')) for x in [parts7,parts8,parts11]])
allp=parts7+parts8+parts11;actf=sum(p['frames'] for p in allp if p['classification'].startswith('actual'));exf=sum(p['frames'] for p in allp if p['classification']=='explanation')
assert actf==6596 and exf==4397
proof=dict(schemaVersion=3,preparedAt=datetime.now(timezone.utc).isoformat(),status='paragraph-native-allocation-prepared-for-narration-timed-render',
 previousConditionalPlan='narration-led-cut-allocation-proposal-v2.json',currentPcmMeasured=True,currentPcmRegenerated=False,
 voices={k:dict(path=v[0],sha256=sha(ROOT/v[0]),paragraphAndSentenceBoundaries=v[1]) for k,v in voice.items()},
 newScenes=[dict(id=k,insertAfter=a,parts=p,frames=sum(x['frames'] for x in p)) for k,a,p in [('07b','07',parts7),('08b','08',parts8),('11b','11',parts11)]],
 retainedBaselineBodyFrames=old['bodyFrames'],retainedBaselineActualFrames=old['actualFrames'],retainedBaselineExplanationFrames=old['explanationFrames'],
 newActualFrames=actf,newExplanationFrames=exf,newBodyFrames=actf+exf,totalBodyFrames=old['bodyFrames']+actf+exf,totalActualFrames=old['actualFrames']+actf,
 ratioErrorFrames=(old['actualFrames']+actf)-(old['bodyFrames']+actf+exf)*.6,
 all14BaselinePcmRetained=True,all20BaselineSilentPiecesRetained=True,gameTitles=['PowerWash Simulator','The Talos Principle 2','Portal 2','Half-Life: Alyx'],
 sourceFrameWindowsUnique=True,notes=['Portal43–58 is split into161+739 output frames with no duplicated source playback; frame-rate conversion still normal1x.',
 'Source time labels distinguish independent clips. Observations retain unique related manipulations and their visible results, not unrelated idle/loops.',
 'Current whisper word landmarks are approximate and contain recognized alternatives; audio bytes and full expected text reviews are preserved.',
 'Some clause splits are at observed quiet/sentence landmarks; final mixed seams and every caption must still be inspected.'],
 voiceAndNativeTimingPreparedOnly=True,allNarrationTimedMovingPixelsApproved=False,currentMixedAudioApproved=False,finalRatioApproved=False,
 newVideoId=None,scheduleReplaced=False,oldUploadDeleted=False)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=out.name,actual=actf,explanation=exf,ratioError=proof['ratioErrorFrames'],rendered=False)))
