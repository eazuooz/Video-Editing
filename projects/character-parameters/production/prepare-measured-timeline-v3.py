"""Prepare exact sample-preserving current editorial timing, pending pixels.

Every game interval is unique and runs normally. Observation pauses stay on
the action just introduced by the narration. This candidate is not final QA.
"""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import hashlib,json,os,subprocess,time,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.resolve().relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,o):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
target=BASE/'measured-timeline-candidate-v3.json';assert not target.exists()
selection_path=BASE/'current-voice-selection-v2.json';selection=read(selection_path)
assert selection['currentCompleteVoiceReadyForMeasuredPlanning']
bank_path=ROOT/'production/batches/sakurai-planning-game-design/proof-character-parameters/source-action-bank-v2.json'
assert sha(bank_path)=='132f983db79c1827a8f585c4ba2e22dcd54abec095fb60032a933d7f5c50f9ed'
bank=read(bank_path);sources={s['sourceKey']:s for s in bank['sources']};windows={w['key']:w for w in bank['windows']}
voices={s['id']:s for s in selection['scenes']}
ko=read(ROOT/selection['currentKoScript']);en=read(ROOT/selection['currentEnScript'])
assert len(ko['scenes'])==len(en['scenes'])==12
for s in sources.values():
 assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
 assert (ROOT/s['nativePtsPath']).exists()
arrays={}
for sid,v in voices.items():
 assert sha(ROOT/v['path'])==v['sha256']
 with wave.open(str(ROOT/v['path']),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())==(24000,1,2,v['samples'])
  arrays[sid]=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
boundary_review=read(BASE/'measured-paragraph-boundary-direct-review-v2.json')
paragraph_starts={r['id']:r['paragraphStarts'] for r in boundary_review['rows']}
paragraph_starts['08-resources-and-actions']=[0,9.57,19.96]
paragraph_starts['09-condition-and-time']=[0,9.97,19.29]
segments=[];chapters=[];placements=[];cursor=120
def segment(role,frames,chapter,**extra):
 global cursor
 assert frames>0
 s=dict(id=f"{chapter}-{len(segments)+1:02d}-{role}",role=role,frames=frames,
        startFrame=cursor,endFrameExclusive=cursor+frames,startSeconds=cursor/60,
        durationSeconds=frames/60,chapter=chapter,**extra)
 segments.append(s);cursor+=frames;return s
def game(key,chapter,start=None,end=None):
 w=windows[key];s=sources[w['sourceKey']]
 start=w['startFrame'] if start is None else start;end=w['endFrameExclusive'] if end is None else end
 assert w['startFrame']<=start<end<=w['endFrameExclusive']
 fps=Fraction(s['nativeVideo']['r_frame_rate']);tb=Fraction(s['nativeVideo']['time_base'])
 d=Fraction(end-start,1)/fps;frames=round(d*60)
 framing='rivals-native-hud-relocation-v4' if w['sourceKey']=='gBbKFYZYvbc' else ('dungeons-inventory-relocation-v5' if w['sourceKey']=='a8nwpiCqyTQ' else 'official-short-fullwidth-nearest-v1')
 return segment('actual-existing-game',frames,chapter,sourceBankWindow=key,
  sourceKey=w['sourceKey'],sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],
  sourceStartFrame=start,sourceEndFrameExclusive=end,nativeFps=str(fps),nativeTimebase=str(tb),
  nativeStartPts=int(Fraction(start,1)/fps/tb),nativeEndPtsExclusive=int(Fraction(end,1)/fps/tb),
  nativePtsEvidence=s['nativePtsPath'],nativePtsEvidenceSha256=sha(ROOT/s['nativePtsPath']),
  sourceDurationSeconds=float(d),resamplingFrameError=float(frames-d*60),
  visibleAction=w['visibleAction'],viewerFocus=w['viewerFocus'],diagramConnection=w['diagramConnection'],
  observation=w['observation'],framing=framing,captionMaxLines=1,captionMaximumMeasuredTextWidthPx=880,
  normalSpeed=True,normalPlaybackRate=1,sourceAudio=False,loop=False,slowdown=False,
  standard60fpsSamplingOnly=True,finalCuePixelsReviewed=False,
  exactNewInternalBoundaryReviewPending=start!=w['startFrame'] or end!=w['endFrameExclusive'])
def black(frames,chapter,note):
 return segment('explanation',frames,chapter,diagram=chapter,style='research-black-v1',
                captionMaxLines=2,narrationConnection=note,finalAnimatedPixelsReviewed=False)
def chapter(sid):
 s=next(s for s in ko['scenes'] if s['id']==sid)
 chapters.append(dict(id=sid,title=s['title'],startFrame=cursor,narrationParagraphStarts=paragraph_starts[sid]))
 return cursor*400
def audio(sid,output_sample,a=0,b=None):
 v=voices[sid];b=v['samples'] if b is None else b
 assert 0<=a<b<=v['samples']
 p=dict(id=f"{sid}-pcm-{len(placements)+1:02d}",voiceId=sid,sourcePath=v['path'],sourceSha256=v['sha256'],
  sourceStartSample=a,sourceEndSampleExclusive=b,samples=b-a,startSample=output_sample,
  endSampleExclusive=output_sample+b-a,startSeconds=output_sample/24000,
  durationSeconds=(b-a)/24000,exactPcmBytesMustMatch=True,speechTrimmed=False)
 placements.append(p);return p['endSampleExclusive']
def finish():
 c=chapters[-1];c.update(endFrameExclusive=cursor,frames=cursor-c['startFrame'])
 assert max(p['endSampleExclusive'] for p in placements if p['voiceId']==c['id'])<=cursor*400

sid='01-overview';t=chapter(sid)
black(234,sid,'Full central question on the black overview; ordered actual example introduction continues over shared movement.')
game('rivals-match-01',sid);audio(sid,t);finish()

sid='02-common-baseline';t=chapter(sid)
game('rivals-match-02',sid,end=966)
black(370,sid,'Common action baseline and necessary minimum capability; p2 starts8.19s beside the cut8.20s.')
game('rivals-match-02',sid,start=966);audio(sid,t);finish()

sid='03-rule-not-scale';t=chapter(sid)
for key in ['zetterburn-gameplay1','zetterburn-gameplay2','orcane-gameplay1','orcane-gameplay2']:game(key,sid)
black(418,sid,'State/space/available-action design clause begins23.24s; illustrative spatial comparison follows the distinct official fire/water examples.')
audio(sid,t);finish()

sid='04-information-rule';t=chapter(sid)
game('forsburn-gameplay1',sid);game('forsburn-gameplay2',sid)
black(933,sid,'Smoke world plane actually occludes rear figure; appearance/judgment/counterplay remain separate. No invulnerability inference.')
audio(sid,t);finish()

sid='05-useful-strength';t=chapter(sid)
game('rivals-match-03',sid);game('rivals-match-04',sid,end=2880)
b=black(641,sid,'Complete p3 narrated close-pressure design example; projected access/height/next-choice comparison.')
n=round(18.20*24000);audio(sid,t,0,n);audio(sid,b['startFrame']*400,n);finish()

sid='06-role-and-limitation';t=chapter(sid)
game('rivals-match-05',sid)
black(898,sid,'Complete original enemy/corridor example starts28.73s. Explicit hypothetical placement needs real playtesting; no source match proves that experiment.')
audio(sid,t);finish()

sid='07-state-not-base';t=chapter(sid)
game('rivals-match-06',sid,end=5780)
black(550,sid,'Separate fixed base pillar/current damage token/player-choice token. No current tier or numeric armor claim.')
game('rivals-match-06',sid,start=5780,end=6300)
n=round(19.59*24000);end=audio(sid,t,0,n);audio(sid,end+round(5.67*24000),n);finish()

sid='08-resources-and-actions';t=chapter(sid)
black(384,sid,'Intro and REACT defense example; DEF change motion begins with actual REACT clause4.4s.')
game('hamir-react',sid)
black(71,sid,'REACT/current-state comparison returns before next independent example.')
game('slade-steal',sid)
black(74,sid,'Different battle/character; resource versus opponent-state comparison.')
game('artemis-stun',sid)
black(1018,sid,'Full separate-shot caution and current fixed-base wording. All three original/current complete paragraphs preserved.')
audio(sid,t);finish()

sid='09-condition-and-time';t=chapter(sid)
black(228,sid,'SNIPE condition/current versus next turn is explicit before normal action.')
game('fleet-snipe',sid)
black(363,sid,'Two3STA dice belong to next turn; never immediate+6 current STA.')
game('fleet-strike',sid)
black(973,sid,'Different boss STRIKE/current heart loss, then complete trigger/target/time program-behavior paragraph.')
audio(sid,t);finish()

sid='10-balance-preserves-role';t=chapter(sid)
game('rivals-match-07',sid)
b=black(507,sid,'Full original role-preserving adjustment paragraph and changing answer path; no balance approval from one historical result.')
n=round(19.32*24000);audio(sid,t,0,n);audio(sid,b['startFrame']*400,n);finish()

sid='11-cost-and-summary';t=chapter(sid)
game('rivals-match-08',sid,end=9588)
black(480,sid,'Independent state-transition graph and meaningful motion under fire/water/smoke rule-cost paragraph.')
game('rivals-match-08',sid,start=9588)
n=round(22.18*24000);end=audio(sid,t,0,n);audio(sid,end+round(5.65*24000),n);finish()

sid='12-conclusion';t=chapter(sid)
game('rivals-match-06',sid,start=6300)
game('rivals-match-09',sid)
black(929,sid,'Complete condition/current-state advice and role-first conclusion; three projected contributions and response path remain distinct.')
n=round(9.67*24000);end=audio(sid,t,0,n);audio(sid,end+round(5.37*24000),n);finish()

body_end=cursor;final_end=cursor+600
actual=sum(s['frames'] for s in segments if s['role']=='actual-existing-game')
explain=sum(s['frames'] for s in segments if s['role']=='explanation')
assert (actual,explain,body_end-120,final_end)==(13606,9071,22677,23397)
assert abs(actual-(actual+explain)*.6)<=1
coverage=[];quiet=[]
for sid,v in voices.items():
 parts=sorted((p for p in placements if p['voiceId']==sid),key=lambda p:p['sourceStartSample'])
 pos=0
 for p in parts:
  assert p['sourceStartSample']==pos;pos=p['sourceEndSampleExclusive']
  if p['sourceStartSample']:
   n=p['sourceStartSample'];a=arrays[sid][n-120:n+120].astype(float)
   rms=float(np.sqrt(np.mean(a*a)));peak=int(abs(a).max());assert rms<350 and peak<1600
   quiet.append(dict(id=sid,sample=n,seconds=n/24000,pcm10msRms=rms,pcm10msPeak=peak))
 assert pos==v['samples']
 coverage.append(dict(id=sid,currentWholeSamples=pos,exactCoverage=True,removedSamples=0,repeatedSamples=0))
last=120*400
for p in sorted(placements,key=lambda p:p['startSample']):
 assert last<=p['startSample'] and p['endSampleExclusive']<=body_end*400
 last=p['endSampleExclusive']
for sk in sources:
 used=sorted([s for s in segments if s.get('sourceKey')==sk],key=lambda s:s['sourceStartFrame'])
 for a,b in zip(used,used[1:]):assert a['sourceEndFrameExclusive']<=b['sourceStartFrame']
for c in chapters:
 c['actualParagraphStarts']=[]
 for seconds in paragraph_starts[c['id']]:
  n=round(seconds*24000)
  p=next(p for p in placements if p['voiceId']==c['id'] and p['sourceStartSample']<=n<p['sourceEndSampleExclusive'])
  c['actualParagraphStarts'].append((p['startSample']+n-p['sourceStartSample']-c['startFrame']*400)/24000)
 c['blackIntervals']=[dict(startFrame=s['startFrame']-c['startFrame'],frames=s['frames'],segmentId=s['id']) for s in segments if s['chapter']==c['id'] and s['role']=='explanation']
 c['motionParagraphStarts']=list(c['actualParagraphStarts'])
 if c['id']=='03-rule-not-scale':c['motionParagraphStarts'][2]=23.24
 if c['id']=='08-resources-and-actions':c['motionParagraphStarts'][0]=4.4
plan=dict(schemaVersion=3,preparedAt=now(),slug='character-parameters',currentVoiceSelection=rel(selection_path),
 currentVoiceSelectionSha256=sha(selection_path),currentKoScript=selection['currentKoScript'],
 currentKoScriptSha256=selection['currentKoScriptSha256'],currentEnScript=selection['currentEnScript'],currentEnScriptSha256=selection['currentEnScriptSha256'],
 bank=rel(bank_path),bankSha256=sha(bank_path),fps=60,width=1920,height=1080,timebase='1/90000',ptsStep=1500,
 narrationSampleRate=24000,currentPcmSeconds=selection['totalPcmSeconds'],currentScenes=12,currentParagraphs=37,
 introFrames=120,memberFrames=600,bodyFrames=22677,actualFrames=actual,explanationFrames=explain,
 finalFrames=final_end,durationSeconds=final_end/60,bodyRatioFrameError=actual-22677*.6,
 segments=segments,chapters=chapters,voicePlacements=placements,exactPcmCoverage=coverage,quietAudioSplitBoundaries=quiet,
 sourceWindows=20,actualCuts=sum(s['role']=='actual-existing-game' for s in segments),
 explanationCuts=sum(s['role']=='explanation' for s in segments),
 sourceUnusedIntervals=[dict(sourceBankWindow='rivals-match-04',startFrame=2880,endFrameExclusive=3240,reason='Remaining12s not needed for the related normal-speed example; no repeated footage quota.')],
 observationPauses='Brief normal action after narrated viewer focus: ledge/spacing, changing current damage, repeated choices and role conclusion. No idle, source loops, slow motion or fabricated evidence.',
 overviewMeasuredSeconds=15.680041666666666,overview20to30SecondsAchieved=False,overviewPolicy='Natural original three sentences retained; no padding to meet an approximate target.',
 allCurrentPcmSamplesPreserved=True,all35UnchangedParagraphsPreserved=True,speechTrimmed=False,sourceAudio=False,loop=False,slowdown=False,
 finalTimingApproved=False,finalPlanAdopted=False,allInputCaptionPixelsReviewed=False,allFinalPixelsApproved=False,
 mixedAsrApproved=False,qa=False,collected=False,uploaded=False,actualId=None,
 preparedOnly=True,humanListening='pending',humanPronunciation='pending',publicRights='pending',rasterGitAdditions=0,mediaGitAdditions=0)
save(target,plan)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='measured-current-PCM-and-unique-source-candidate-inputs-pending',
 measuredCandidate=rel(target),ownedJob=None,nextAction='Build singleCPU2 native clips and twelve measured independent MC scenes. Directly review all actual cue/cut/UI and meaningful black motion pixels before final plan adoption/Nimbus mix.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(i for i in q['items'] if i['slug']=='character-parameters')
 item.update(stage=cp['stage'],measuredCandidate=rel(target),currentExecution=None,nextAction=cp['nextAction']);q['updatedAt']=now()
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent queue write; preserve and inspect')
print(json.dumps(dict(actualFrames=actual,explanationFrames=explain,bodyFrames=22677,finalFrames=final_end,
 seconds=final_end/60,currentPcmSeconds=selection['totalPcmSeconds'],voicePlacements=len(placements),actualCuts=plan['actualCuts'],explanationCuts=plan['explanationCuts'],preparedOnly=True)))
