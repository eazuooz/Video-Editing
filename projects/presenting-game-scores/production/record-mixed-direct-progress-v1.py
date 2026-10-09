"""Persist only windows whose full expected/actual text and words were read."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent/'final-v1';D=W/'mixed-asr-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--through',type=int,required=True);a=ap.parse_args()
data=read(D/'asr.json');assert 1<=a.through<=len(data['results'])
notes={
 'whole-03':'At chunk boundary, final guide tail and p3 repeated in text; timestamps regress from29.80 to20.00. Independent03p3 has one complete conclusion. Await full guide12 context and PCM correlation; do not infer an actual audio repetition.',
 'whole-06':'All numeric clauses recognized27/14096/17016/2920/141. Preserve 왼쪽의/왼쪽에 and 경기 중의/중에 minor particle ambiguity for human pronunciation; no final-victory claim.',
 'whole-08':'Important unresolved recognition alternatives 기여/기어 and 읽게/잃게. Await current independent08p3; older unmixed recognition is not a current mixed approval.',
 'whole-09':'Preserve 개별 행동의/행동에 particle uncertainty; content order and complete closing text observed.',
 'whole-10':'Preserve 경기 중의/중에 particle uncertainty. Original coaching conclusion fully present; independent10p3 pending.',
 'context-01-overview-complete':'Independent 지훈줄수 versus whole 지운 줄수. Same current PCM interval plus0.6sec zero padding; retain actual differing recognition and human pronunciation pending.',
 'context-03-complete-p3':'One full intended closing sentence, without repetition or extra greeting; does not by itself approve all whole03 content.',
 'context-04-complete-p3':'배점표 complete and ending present; preserve 점수의/점수 particle difference from exact whole recognition.'}
rows=[]
for x in data['results'][:a.through]:
 path=D/(x['label']+'.json');actual=read(path)
 assert actual['text']==x['text'] and actual['expectedKo']==x['expectedKo']
 assert actual['exactStereoMixSampleBytesMatched'] and not actual['expectedWasRecognizerPrompt']
 assert sha(ROOT/actual['windowPath'])==actual['windowSha256']
 rows.append(dict(label=x['label'],path=path.relative_to(ROOT).as_posix(),sha256=sha(path),directlyCompared=True,
  fullExpectedAndActualTextRead=True,allWordTimestampsRead=True,
  observation=notes.get(x['label'],'Complete intended content and ending directly read; spacing/punctuation alternatives do not rewrite the supplied script. Human pronunciation/listening remain pending.'),
  fromSample=x['fromSample'],toSample=x['toSample'],padSamplesEachSide=x['padSamplesEachSide']))
progress=dict(recordedAt=datetime.now(timezone.utc).isoformat(),currentMixedAudioSha256=data['mixSha256'],
 currentAacSha256=data['aacSha256'],planSha256=data['planSha256'],windows=rows,directlyRead=a.through,total=31,
 all31WindowsDirectlyCompared=False,technicallyApproved=False,finalMixedAsrApproved=False,
 unresolvedContentQuestions=['Whole03 chunk repetition/timestamp reversal correlation','Current08 기여/읽게 independent-context comparison'] if a.through<31 else ['Direct resolution proof required before approval'],
 humanWholeListening='pending',humanPronunciation='pending',endingHeuristicUsedForApproval=False,
 allFinalPixels=False,qa=False,collected=False,private=False,imagesGitAdded=0)
(W/'mixed-asr-direct-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(directlyCompared=a.through,total=31,finalMixedAsrApproved=False)))
