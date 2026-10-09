"""Measured editorial candidate from exact current PCM; never a render approval.

All ten approved longplay actions are used once, plus two distinct official shots.
Move the six-second early Tetris passage to the concluding audit, without replay.
"""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig')); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
dest=BASE/'measured-editorial-candidate-v2.json';assert not dest.exists()
vp=BASE/'preserved-pcm-complete-joins-v1.json'; voice=read(vp)
for s in voice['scenes']:assert sha(ROOT/s['path'])==s['sha256']
for s in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:assert sha(ROOT/s['path'])==s['sha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
bankp=ROOT/'production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json';bank=read(bankp)
sources={s['name']:s for s in bank['sources']}; cuts={s['cutId']:s for s in bank['cuts']}
adoptp=BASE/'source-content-adoption-v7.json';adopt=read(adoptp); assert adopt['footageAdoptedForScript'] and adopt['nativePtsBoundsVerified']
newcuts={s['id']:s for s in adopt['compositionReview']['cuts']}
v={s['id']:s for s in voice['scenes']}; bounds={s['id']:s['paragraphBoundariesSamples'] for s in voice['scenes']}
segments=[];chapters=[];placements=[];cursor=120
def segment(ident,role,frames,ch,**kw):
 global cursor
 assert frames>0
 s=dict(id=ident,role=role,startFrame=cursor,endFrameExclusive=cursor+frames,frames=frames,startSeconds=cursor/60,durationSeconds=frames/60,chapter=ch,**kw)
 segments.append(s);cursor+=frames;return s
def oldgame(cid,ch,start=None,end=None,frames=None,suffix=''):
 c=cuts[cid];src=sources[c['source']];start=c['startFrame'] if start is None else start;end=c['endFrameExclusive'] if end is None else end
 fps=Fraction(src['nativeFps']);dur=Fraction(end-start,1)/fps;frames=round(dur*60) if frames is None else frames
 assert abs(frames-float(dur*60))<=1,(cid,frames,dur)
 return segment(cid+suffix,'actual-existing-game',frames,ch,game='Balatro' if src['name']=='balatro' else 'Tetris Effect: Connected',source=src['name'],sourcePath=src['rawPath'],sourceSha256=src['sha256'],sourceStartFrame=start,sourceEndFrameExclusive=end,nativeFps=src['nativeFps'],nativeTimebase=src['timebase'],nativeStartPts=int(Fraction(start,1)/fps/Fraction(src['timebase'])),sourceDurationSeconds=float(dur),nativePtsEvidence=src['ptsPath'],nativePtsEvidenceSha256=src['ptsSha256'],framing=c['framing'],captionMaxLines=c['captionMaxLines'],visibleAction=c['visibleAction'],diagramConnection=c['diagramConnection'],sourceBankCutId=cid,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,finalCuePixelsReviewed=False)
def bal(cid,ch):
 c=newcuts[cid]
 return segment('bal-longplay-'+cid,'actual-existing-game',c['frames'],ch,game='Balatro',source='balatro-longplay',sourcePath=str(ROOT/adopt['sourcePath']),sourceSha256=adopt['sourceSha256'],sourceStartFrame=c['sourceStartFrame'],sourceEndFrameExclusive=c['sourceEndFrameExclusive'],nativeFps='60/1',nativeTimebase='1/15360',nativeStartPts=c['sourceFirstPts'],sourceDurationSeconds=c['seconds'],nativePtsEvidence=c['nativePtsEvidence'],nativePtsEvidenceSha256=c['nativePtsEvidenceSha256'],framing='full-source-fit1600x900-at160x0-same-frame-blur-fill-credit-left',videoRect=[160,0,1600,900],captionMaxLines=2,onscreenCredit='Footage: Squeaky Whale Gameplay Archive',creditOutsideGameplay=True,visibleAction=c['observations'],diagramConnection=c['claim'],sourceBankCutId=cid,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,finalCuePixelsReviewed=False)
def black(ident,frames,ch,diagram,phases,note):
 return segment(ident,'explanation',frames,ch,style='research-black-v1',diagram=diagram,paragraphMotionStarts=phases,narrationConnection=note,measured=True,captionMaxLines=2,finalAnimatedPixelsReviewed=False)
def audio(sid,start,a=0,b=None,note='Whole exact reviewed PCM'):
 r=v[sid];b=r['samples'] if b is None else b; assert 0<=a<b<=r['samples']
 p=dict(id=f'{sid}-part-{len(placements)+1:02d}',voiceId=sid,sourcePath=r['path'],sourceSha256=r['sha256'],sourceStartSample=a,sourceEndSampleExclusive=b,samples=b-a,startSample=start,endSampleExclusive=start+b-a,startSeconds=start/24000,durationSeconds=(b-a)/24000,exactPcmBytesMustMatch=True,speechTrimmed=False,purpose=note)
 placements.append(p);return p['endSampleExclusive']
def chapter(n,title):chapters.append(dict(id=n,title=title,startFrame=cursor));return cursor*400
def close():chapters[-1].update(endFrameExclusive=cursor,frames=cursor-chapters[-1]['startFrame'])
t=chapter('01','점수는 무엇을 말해 줄까?')
black('black-01-overview',1320,'01','01-overview',[0,4.6,13.3],'Complete new measured22s overview; quantity/evaluation, card-to-score, criteria/feedback order.');audio('01-overview',t);close()
t=chapter('02','진행량과 평가는 다르다');oldgame('classic-01','02')
e=black('black-02-separate-metrics',420,'02','02-score-and-lines',[0,.35,2.2],'Preserve original projected metrics and full concluding paragraph.')
n=bounds['02-score-and-lines'][2];end=audio('02-score-and-lines',t,0,n);audio('11-observe-separate-updates',end);audio('02-score-and-lines',e['startFrame']*400,n);close()
t=chapter('03','같은 양, 다른 점수');oldgame('classic-02','03',start=1625,frames=1140,suffix='-equality-remainder')
e=black('black-03-equal-counts',420,'03','03-same-count',[0,.2,2.4],'Preserve complete question/claim/conclusion; native equality f2057 occurs17.28s after this unique remainder starts.')
n=bounds['03-same-count'][2];end=audio('03-same-count',t,0,n);audio('12-observe-equal-quantity',end);audio('03-same-count',e['startFrame']*400,n);close()
t=chapter('04','무엇을 높게 평가할까?');bal('three-kind-extra-card','04');bal('enhanced-two-pair','04')
e=black('black-04-event-evaluation',481,'04','04-evaluation-weights',[0,.3,2.0],'Guide7/3/6 over its exact hand first; entire retained p1/p3 and new p2 continue in order. Expanded8.0167s retains all old7.5s explanation and full speech.')
end=audio('13-observe-action-label',t);audio('04-evaluation-weights',end+2880);close()
t=chapter('05','이번 행동과 누적 결과');bal('round-accumulate','05');bal('decimal-mult','05')
e=black('black-05-event-and-record',461,'05','05-events-and-total',[0,.15,1.0650416667],'Two distinct observed contributions:767+560=1327 and1104+595=1699. Full original conclusion remains; no single continuous run claimed.')
n=bounds['05-events-and-total'][1];end=audio('05-events-and-total',t,0,n);end=audio('14-observe-notice-and-record',end);audio('05-events-and-total',end,n);close()
t=chapter('06','누구와 비교한 숫자일까?');oldgame('modern-03','06',frames=839)
first=black('black-06-observed-2920',720,'06','06-observed-2920',[0,6.24,9.5],'Exact previously observed27-lines14096/17016, difference2920; separate snapshot, never frozen live gameplay.')
split06=195480;audio('06-relative-gap',t,0,bounds['06-relative-gap'][1]);end=audio('15-observe-equal-lines-gap',first['startFrame']*400);audio('06-relative-gap',end,bounds['06-relative-gap'][1],split06)
oldgame('modern-04','06',end=3456,frames=318,suffix='-through-observation')
second=black('black-06-observed-141',690,'06','06-observed-141',[0,7.04,9.0],'Separate later29/19919 versus32/19778,+141; full guide and retained later sentence.')
end=audio('16-observe-later-point-lead',second['startFrame']*400);audio('06-relative-gap',end,split06,bounds['06-relative-gap'][2])
tail=oldgame('modern-04','06',start=3456,end=3780,frames=648,suffix='-changing-lead-after-observation');audio('06-relative-gap',tail['startFrame']*400,bounds['06-relative-gap'][2]);close()
t=chapter('07','이름과 단위를 붙이기');bal('full-house','07')
e=black('black-07-names-units',807,'07','07-name-and-unit',[0,.2,5.275],'Named hand/round/target over observed hand, then projected labelled quantities; entire original p3 onset 어떤 retained at source268800.')
n=bounds['07-name-and-unit'][1];end=audio('07-name-and-unit',t,0,n);end=audio('24-observe-named-fields-clear-start',end);audio('07-name-and-unit',end,n);close()
t=chapter('08','계산을 읽는 순간');bal('diamond-full-house','08')
e=black('black-08-read-inputs',240,'08','08-scoring-feedback',[0,.5,3.3],'Distinct full-frame hand59×13=767 then its conceptual labels; remaining original p2 begins in diagram.')
black('black-08-contribution-result',909,'08','08-scoring-feedback',[0,.4,3.985],'Preserve full original15.15s spatial illustration and original independent scoring narration; not copied source formula.')
n=bounds['08-scoring-feedback'][1];audio('08-scoring-feedback',t,0,n);audio('08-scoring-feedback',e['startFrame']*400,n);close()
t=chapter('09','남아 있는 숫자와 지나가는 알림');bal('enhanced-704','09');bal('straight-400','09');oldgame('balatro-countup','09')
e=black('black-09-stable-and-transient',446,'09','09-feedback-hierarchy',[0,.15,4.0],'Stable704/target1200 guide begins late in its actual calculation;400 later contribution and a separate official montage are distinct, never one continuity claim.')
split09=bounds['09-feedback-hierarchy'][1]+128160 #New p2 exact inspected quiet5.34s after its start.
end=audio('09-feedback-hierarchy',t,0,split09);end=audio('18-observe-stable-reading',end);audio('09-feedback-hierarchy',end,split09);close()
t=chapter('10','세 가지 질문으로 점검하기');oldgame('classic-02','10',end=1625,frames=360,suffix='-early-audit-prefix')
e=black('black-10-tetris-recap',276,'10','10-audit-and-close',[0,.2,2.8],'Complete Tetris recap sentence on independent projected audit gates; original total13.2167s explanation split without deletion.')
n=bounds['10-audit-and-close'][1];audio('10-audit-and-close',t,0,n);split10=n+109920;audio('10-audit-and-close',e['startFrame']*400,n,split10)
b=bal('debuff-diamond','10');bal('pair','10');oldgame('balatro-hand','10')
end=audio('10-audit-and-close',b['startFrame']*400,split10,bounds['10-audit-and-close'][2]);audio('19-observe-reading-audit',end)
e=black('black-10-three-audit-gates',517,'10','10-audit-and-close',[0,2.8,7.0],'Entire original coaching conclusion over projected three-question audit, preserving the remaining8.6167s from original explanation.')
audio('10-audit-and-close',e['startFrame']*400,bounds['10-audit-and-close'][2]);close()
bodyEnd=cursor;memberStart=cursor;cursor+=600
actual=sum(s['frames'] for s in segments if s['role']=='actual-existing-game');white=sum(s['frames'] for s in segments if s['role']=='explanation')
balFrames=sum(s['frames'] for s in segments if s.get('game')=='Balatro');tetFrames=actual-balFrames
assert (actual,white,balFrames,tetFrames,bodyEnd-120,cursor)==(11561,7707,6936,4625,19268,19988)
assert abs(actual-(bodyEnd-120)*.6)<=1 and abs(balFrames-actual*.6)<=1
assert len([s for s in segments if s.get('source')=='balatro-longplay'])==10
coverage=[]
for sid,r in v.items():
 p=sorted([x for x in placements if x['voiceId']==sid],key=lambda x:x['sourceStartSample']);pos=0
 for x in p:assert x['sourceStartSample']==pos;pos=x['sourceEndSampleExclusive']
 assert pos==r['samples'];coverage.append(dict(id=sid,exactSamples=pos,removedSamples=0,repeatedSamples=0))
last=48000
for p in sorted(placements,key=lambda x:x['startSample']):
 assert p['startSample']>=last,(p['id'],last,p['startSample']);last=p['endSampleExclusive'];assert last<=memberStart*400
for ch in chapters:
 pp=[p for p in placements if p['voiceId'][:2] in ([ch['id']] if ch['id'] not in ['02','03','04','05','06','07','09','10'] else {'02':['02','11'],'03':['03','12'],'04':['04','13'],'05':['05','14'],'06':['06','15','16'],'07':['07','24'],'09':['09','18'],'10':['10','19']}[ch['id']])]
 assert all(ch['startFrame']*400<=p['startSample']<p['endSampleExclusive']<=ch['endFrameExclusive']*400 for p in pp),(ch['id'],pp)
for source in {s['sourcePath'] for s in segments if s['role']=='actual-existing-game'}:
 rr=sorted([s for s in segments if s.get('sourcePath')==source],key=lambda x:x['sourceStartFrame'])
 assert all(a['sourceEndFrameExclusive']<=b['sourceStartFrame'] for a,b in zip(rr,rr[1:])),source
baselineBlack=sum(s['frames'] for s in read(ROOT/'projects/presenting-game-scores/production/final-v1/plan.json')['segments'] if s['role']=='explanation')
j=dict(schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),slug='presenting-game-scores',voiceSelection=rel(vp),voiceSelectionSha256=sha(vp),bank=rel(bankp),bankSha256=sha(bankp),sourceContentAdoption=rel(adoptp),sourceContentAdoptionSha256=sha(adoptp),fps=60,width=1920,height=1080,timebase='1/90000',ptsStep=1500,narrationSampleRate=24000,currentPcmSeconds=voice['totalNarrationSeconds'],introFrames=120,memberFrames=600,bodyFrames=19268,actualFrames=actual,explanationFrames=white,baselineExplanationFrames=baselineBlack,allGoodExplanationDurationPreserved=True,balatroFrames=balFrames,tetrisFrames=tetFrames,bodyRatioFrameError=actual-19268*.6,gameRatioFrameError=balFrames-actual*.6,finalFrames=cursor,durationSeconds=cursor/60,segments=segments,chapters=chapters,voicePlacements=placements,paragraphBoundaries=bounds,completeSentence06BoundarySample=split06,completeSentence09BoundarySample=split09,completeSentence10BoundarySample=split10,exactPcmCoverage=coverage,allOriginalAndSelectedSamplesRetained=True,speechTrimmed=False,loop=False,slowdown=False,sourceAudio=False,actualSourceAcquisitionRepeated=False,captionStyle='boxed-white-forest-v1',captionCenterPx=[960,970],captionMaxLines=2,mathRatioVerified=True,currentCompleteVoiceApproved=False,finalPlanAdopted=False,finalTimingApproved=False,allInputSegmentCaptionPixelsReviewed=False,allFinalPixels=False,finalMixedAsrApproved=False,pairRendered=False,qaApproved=False,collected=False,privateUploaded=False,actualId=None,preparedOnly=True,newImagesGitAdded=0,humanListening='pending',humanPronunciation='pending',publicRights='pending')
dest.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualFrames=actual,explanationFrames=white,balatroFrames=balFrames,tetrisFrames=tetFrames,bodyRatioFrameError=j['bodyRatioFrameError'],gameRatioFrameError=j['gameRatioFrameError'],finalFrames=cursor,durationSeconds=cursor/60,allVoiceSamplesRetained=True,preparedOnly=True)))
