"""Record human-agent full-text/word comparison after the actual outer exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--exit-chunk',required=True);args=ap.parse_args()
assert args.outer_exit_code==0
sp=R/'current-mixed-whole-asr-execution-v1.json';s=read(sp)
assert s['pid']==33428 and s['createTime']==1791660485.5867407 and s['exitCode']==0 and s['completed']==s['total']==14
assert not psutil.pid_exists(s['pid']),'Observe actual identity; do not wait on a reused PID.'
session=read(sp.with_name(sp.stem+'.session.json'));assert session['sessionId']==15590 and session['pid']==s['pid']
dest=R/'current-mixed-whole-asr-direct-review-v1.json';assert not dest.exists()
notes={
 '00a':['Complete4paragraphs and every sentence ending; spacing 빨간선/빨간 선, 연결해 보죠/연결해보죠.'],
 '01':['Complete6paragraphs; p4 expected 이동이 / whole 이동에; independent complete p4 still pending. 이천이십이/2022 numerical normalization.'],
 '02':['Complete4paragraphs and every ending; spacing 생각해 보세요/생각해보세요.'],
 '03':['Complete6paragraphs and every ending; spacing 에임 모드/에임모드, 남아 있습니다/남아있습니다, 보여 주는/보여주는.'],
 '04':['Complete4paragraphs and endings; 조절 값/조절값 spacing.'],
 '05':['Complete6paragraphs; p6 expected 아니므로 / 아님으로 requires independent p6; other differences spacing only.'],
 '06':['Full4paragraphs read; p3 설계 제안입니다 / 제한입니다입니다, 앞의/앞에, 들어 있다는/들어있다는; apparent duplicated 입니다 and words around30s require complete p3 context. No ending heuristic or historic unmixed approval used.'],
 '06b':['Complete2paragraphs and all endings. Last whole word timestamp extends into zero padding; raw full voice remains exact.'],
 '07':['Full6paragraphs read; 투/2 numeral normalization; p3 컷이므로/컷임으로 and 읽지는/잊지는; p5 앞의/앞에 require independent complete contexts.'],
 '08':['Complete4paragraphs and every ending; spacing/punctuation only.'],
 '09':['Complete6paragraphs and final 있습니다 in actual full words; timestamp warning preserved. Do not use ending presence alone as approval.'],
 '10':['Complete4paragraphs; p4 다르므로/다름으로 requires independent context; 알려 주는/알려주는 spacing.'],
 '11':['All6paragraphs present in full text; p2 뒤의/뒤에 and 에임 모드/aim mode. p5 is repeated in whole ASR with timestamps reverting from49.98 to40s and duplicating40–49s. This overlap is preserved as a recognition finding, not assumed actual audio repetition; independent complete p5 and p6 must resolve it.'],
 '12':['Complete4paragraphs; p1 시점 이동/시점, 이동 punctuation; p4 마지막의/마지막에 requires independent p4. 한 가지/한가지 and 시작해 보세요/시작해보세요 spacing. Actual final 확인해주세요 present in full words; raw tail and independent full p4 remain required.']
}
rows=[]
for v in s['results']:
    p=R/f'current-mixed-whole-asr-v1/{v["id"]}.json';current=read(p);assert current==v
    rows.append(dict(scene=v['id'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
      expectedWhole=v['expectedKo'],recognizedWhole=v['text'],allFullTextsAndWordsDirectlyRead=True,
      notes=notes[v['id']],independentContextPending=True,humanPronunciationApproved=False))
session.update(actualOuterExitCode=0,actualExitToolChunk=args.exit_chunk,workerCurrentlyAlive=False,
  observedAt=datetime.now(timezone.utc).isoformat())
save(sp.with_name(sp.stem+'.session.json'),session)
s.update(actualOuterExitCode=0,actualExitObserved=True,actualExitToolChunk=args.exit_chunk);save(sp,s)
save(dest,dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),actualSession=15590,
  actualOuterExitCode=0,actualExitToolChunk=args.exit_chunk,workerCurrentlyAlive=False,
  sourceExecution=sp.relative_to(ROOT).as_posix(),sourceExecutionSha256=sha(sp),rows=rows,
  all14WholeTextsDirectlyCompared=True,all66IndependentContextsDirectlyCompared=False,
  finalMixedContentReviewPassed=False,mixAacSha256=s['mixAacSha256'],decodedAacSha256=s['decodedAacSha256'],
  humanListeningApproved=False,humanPronunciationApproved=False,allFinalPixelsApproved=False,
  originalPcmRegenerated=0,researchManipulations=0))
print(json.dumps(dict(wholeTextsDirectlyCompared=14,independentContextsPending=66,finalApproval=False)))
