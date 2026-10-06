"""Direct whole read followed by byte-exact complete ending and changed join."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
whole_path=BASE/'guide12-room-whole-asr-v2/12-whole.json';whole=read(whole_path)
review_path=BASE/'guide12-room-whole-direct-review-v2.json';assert not review_path.exists()
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),wholeEvidence=rel(whole_path),wholeEvidenceSha256=sha(whole_path),
 currentAudioPath=whole['sourcePath'],currentAudioSha256=whole['sourceSha256'],wholeDirectReview=True,
 allThreeExpectedKoAndIndependentEnSentencesRead=True,actualEntireTextAndAll18WordTimestampsRead=True,
 observation='Current recognizer returns all3sentences once, including corrected방에서,계단/높은쪽 and the complete따라가보세요ending. Last word8.18–8.54 within current8.560041667PCM. No extra greeting/full-sentence loss/repetition observed in this whole read.',
 sentenceRanges=[[0,2.22],[2.46,5.7],[5.9,8.54]],expectedWasRecognizerPrompt=False,
 independentContextReview=False,changedJoinReview=False,automaticEndingApproval=False,
 humanWholeListening='pending',pronunciation='pending',asrApproved=False,narrationApproved=False,finalMixedAsrApproved=False)
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
out=ROOT/'shared/output/familiar-game-rules/research/guide12-room-contexts-v2';assert not out.exists();out.mkdir(parents=True)
def pcm_slice(path,a,b):
 with wave.open(str(path),'rb') as w:
  assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
  assert 0<=a<b<=w.getnframes();w.setpos(a);return w.readframes(b-a)
def wav_save(path,pcm):
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
 with wave.open(str(path),'rb') as w:assert w.readframes(w.getnframes())==pcm
 return dict(sourcePath=rel(path),sourceSha256=sha(path),seconds=len(pcm)/48000,exactSourceSampleBytesMatched=True)
new_path=ROOT/whole['sourcePath'];assert sha(new_path)==whole['sourceSha256']
ending_start=56160;ending_end=205441
ending=pcm_slice(new_path,ending_start,ending_end);p=out/'12-complete-ending.wav';ending_meta=wav_save(p,ending)
ending_meta.update(id='12-complete-ending',originalAudioPath=whole['sourcePath'],originalAudioSha256=whole['sourceSha256'],
 startSample=ending_start,endSample=ending_end,startSeconds=2.34,
 expectedKo='다음 계단 컷에서는 높은 쪽으로 화면을 돌리죠. 대상의 높이와 방향 잡기를 함께 따라가 보세요.',
 boundaryBasis='Current whole words end2.22/start2.46; midpoint2.34 selects two complete sentences through exact PCM ending.')
old=read(BASE/'guide-join-context-plan-v1.json')['contexts'][0];assert old['scene']=='12'
pieces=[];cursor=0;joined=b''
for component in old['sourceComponents']:
 if component['role']=='new-guide':
  src=new_path;a=0;b=205441;pcm=pcm_slice(src,a,b)
 elif component['sourcePath']:
  src=ROOT/component['sourcePath'];a=component['sourceStartSample'];b=component['sourceEndSample'];pcm=pcm_slice(src,a,b)
  assert hashlib.sha256(pcm).hexdigest()==component['pcmSha256']
 else:src=None;a=b=None;pcm=bytes((component['endSample']-component['startSample'])*2)
 pieces.append(dict(role=component['role'],sourcePath=rel(src) if src else None,sourceStartSample=a,sourceEndSample=b,
  startSample=cursor,endSample=cursor+len(pcm)//2,pcmSha256=hashlib.sha256(pcm).hexdigest()))
 joined+=pcm;cursor+=len(pcm)//2
join_path=out/'12-complete-join.wav';join_meta=wav_save(join_path,joined)
join_meta.update(id='12-complete-join',sourceComponents=pieces,
 expectedKo=old['expectedKo'].replace('분홍색 문 앞의 대상을 겨눕니다.','분홍색 방에서 대상을 겨눕니다.'),
 allOriginalBeforeAfterBytesUnchanged=True,addedSilenceSeconds=.24,finalTimelineAdopted=False)
plan=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),wholeReview=rel(review_path),wholeReviewSha256=sha(review_path),
 contexts=[ending_meta,join_meta],contextCount=2,allContextsCompleteSentences=True,onlyChangedGuide12=True,
 old8JoinsRepeated=False,allOtherAudioPreserved=True,finalTimingApproved=False,finalTimelineAdopted=False,newGitImages=0)
p=BASE/'guide12-room-context-plan-v2.json';assert not p.exists();p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contexts=2,endingSeconds=ending_meta['seconds'],joinSeconds=join_meta['seconds'],wholeDirectReview=True,approved=False)))
