"""Seal the six directly read texts without inventing human listening/pronunciation approval."""
from pathlib import Path
from datetime import datetime,timezone
import array,hashlib,json,math,os,wave,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
state=read(BASE/'fresh-guides-asr-execution-v4.json');assert state['completed']==6 and state['exitCode']==0
try:assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01,'ASR worker still alive'
except psutil.NoSuchProcess:pass
state['actualExitObserved']=True;state['sessionId']=65000;save(BASE/'fresh-guides-asr-execution-v4.json',state)
session=read(BASE/'fresh-guides-asr-session-v4.json');session.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False);save(BASE/'fresh-guides-asr-session-v4.json',session)
data=read(BASE/'fresh-guides-asr-v4/asr.json');assert data['complete'] and len(data['results'])==6
rows=[];notes={
 '23-mining-and-pursuit':'All two complete clauses, mineral approach/disappearing pieces, pursuing enemies and spatial conclusion retained in both windows. Only punctuation/spacing differences.',
 '24-destination-and-danger':'Both windows retain marked-circle approach, nearby enemies after entry and continuing destination/risk observation. No omission, repetition or extra greeting.',
 '25-gap-during-pursuit':'Both windows retain rock gap, green pursuer, observation of usable space and terrain-reading conclusion. ASR writes 사이의/행동의 for scripted 사이에/행동에; this agreement is not proof of spoken vowel correctness. Human pronunciation remains pending. Independent final timestamp13.08 exceeds padded speech tail expectation; timestamps are recognition estimates, not PCM authority.'}
for r in data['results']:
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256']
 if r['mode']=='complete-independent':
  assert r['exactSourceSampleBytesMatched'] and sha(ROOT/r['contextPath'])==r['contextSha256']
 rows.append(dict(id=r['id'],resultPath='projects/similar-game-design/production/fresh-guides-asr-v4/'+r['id']+'.json',
  resultSha256=sha(BASE/'fresh-guides-asr-v4'/f"{r['id']}.json"),expectedKo=r['expectedKo'],actualCompleteText=r['text'],
  allWordsAndEndsDirectlyRead=True,note=notes[r['sceneId']],unexpectedGreetingObserved=False,contentOmissionOrRepetitionObserved=False,
  spokenParticleCorrectness='pending-human-pronunciation' if r['sceneId'].startswith('25-') else 'not-human-approved'))
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),results=rows,wholeWindows=3,independentCompleteWindows=3,
 allExpectedActualCompleteTextsAndWordEndsDirectlyCompared=True,allSourceHashesMatched=True,allIndependentPcmBytesMatched=True,
 automatedContentIntegrityReviewComplete=True,automaticRecognizerApproval=False,endingHeuristicIsApproval=False,
 original21AsrRepeated=False,humanListening='pending',humanPronunciation='pending',finalMixedAsrApproved=False)
out=BASE/'fresh-guides-asr-direct-review-v4.json';assert not out.exists();save(out,review)
tts=read(BASE/'fresh-guides-tts-execution-v4.json');script=read(ROOT/'projects/similar-game-design/script/fresh-observation-guides.ko.v4.json')
boundaries={ '23-mining-and-pursuit':6.03,'24-destination-and-danger':6.035,'25-gap-during-pursuit':6.4875 }
measured=[]
for s in script['scenes']:
 m=next(x for x in tts['results'] if x['id']==s['id']);source=ROOT/m['path'];assert sha(source)==m['sha256']
 with wave.open(str(source),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);samples=w.getnframes();raw=w.readframes(samples);pcm=array.array('h',raw)
 split=round(boundaries[s['id']]*24000);energy=math.sqrt(sum(v*v for v in pcm[split-120:split+120])/240)/32768
 assert energy<.001
 measured.append(dict(id=s['id'],path=m['path'],sha256=m['sha256'],sampleRate=24000,totalSamples=samples,seconds=samples/24000,
  splitSample=split,splitSeconds=split/24000,normalizedRms=energy,allSourceSamplesRetained=True,pcmSha256=hashlib.sha256(raw).hexdigest(),
  paragraphs=[dict(paragraph=i+1,expectedKo=s['lines'][i],sourceInSample=a,sourceOutSample=b,seconds=(b-a)/24000) for i,(a,b) in enumerate([(0,split),(split,samples)])],
  method='Whole and0.4s padded complete words directly compared; quiet current PCM gap. Historical provisional valley is not used as approval.'))
timing=dict(schemaVersion=1,measuredAt=datetime.now(timezone.utc).isoformat(),scenes=measured,totalSeconds=sum(x['seconds'] for x in measured),
 asrReview='projects/similar-game-design/production/fresh-guides-asr-direct-review-v4.json',asrReviewSha256=sha(out),directWordPcmBoundariesCompared=True,
 provisional23Valley5Point6425Rejected=True,provisional25Valley6Point1925Rejected=True,allSamplesPreserved=True,finalTimelineApproved=False,bodyRatioApproved=False)
save(BASE/'fresh-guides-paragraph-timing-v4.json',timing)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=review['reviewedAt'],stage='current24-73paragraphs-605Point540041667PCM-measured-awaiting-final-source-allocation',
 freshGuideAsrReview='projects/similar-game-design/production/fresh-guides-asr-direct-review-v4.json',freshGuideParagraphTiming='projects/similar-game-design/production/fresh-guides-paragraph-timing-v4.json',
 freshGuideAutomatedContentIntegrityReviewComplete=True,humanListening='pending',humanPronunciation='pending',finalMixedAsrApproved=False,
 ownedJob=dict(sessionId=65000,status='closed-new-six-window-ASR',exitCode=0,actualExitObserved=True,workerExpectedRunning=False),
 nextAction='Finish exact unique primary-source/cut allocation and60:40 without cutting any current PCM. Then measured24 independent spatial scenes/captions, mixed ASR, final pair pixels/decode/PTS/AAC/collection/private/Git.');save(BASE/'latest-checkpoint.json',cp)
print(json.dumps(dict(sixWindowsDirectlyCompared=True,totalNewPcmSeconds=timing['totalSeconds'],boundaries=[(x['id'],x['splitSeconds']) for x in measured],humanPronunciation='pending')))
