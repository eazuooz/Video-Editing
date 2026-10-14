"""Select22 unchanged passed takes plus two stored-WAV-gated retakes.

No source media is overwritten. Selection is generation evidence only;
whole/context ASR, final mixed audio and human listening remain unapproved.
"""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
sys.path.insert(0,str(ROOT/'qwen3-tts'))
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def write(p,v):
 if p.exists():raise RuntimeError('Preserve existing '+str(p))
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def main():
 import soundfile as sf,numpy as np,render_narration
 # Tail metrics need only NumPy; do not load the synthesis model or GPU.
 render_narration.np=np
 original_path=BASE/'additive-tts-execution-v1.json';repair_path=BASE/'additive-tail-repair-execution-v2.json'
 original=read(original_path);repair=read(repair_path);request=read(BASE/'additive-tts-request-v3.json')
 scoped=read(BASE/'additive-tail-repair-request-v3.json')
 if original.get('exitCode')!=1 or len(original['results'])!=24:raise RuntimeError('Original observed24-take failure required')
 failed={x['id'] for x in original['results'] if not x['technicalTailGatePassed']}
 if failed!={'06-guide-tsr-reveal','10-guide-path-game'}:raise RuntimeError('Unexpected failed scope')
 if repair.get('exitCode')!=0 or not repair.get('generationComplete') or {x['id'] for x in repair['results']}!=failed:raise RuntimeError('Successful scoped two-take generation required')
 hpath=ROOT/'shared/output/gpu-handoff'/f"{repair['leaseToken']}.json";history=read(hpath)
 if history.get('state')!='research_resume_verified' or history.get('ttsExitCode')!=0:raise RuntimeError('Actual original research restoration required')
 refresh_path=ROOT/'production/research/game-lighting-history/episode04-current-duplicate-rereview-v10.json';refresh=read(refresh_path)
 if refresh.get('decision')!='distinct' or refresh.get('foreignFilesModified') is not False:raise RuntimeError('Direct current delta review required')
 for item in [scoped['sourceRequest'],scoped['sourceExecution'],*scoped['original24TakeFiles'],*scoped['protectedInputs']]:
  frozen=ROOT/refresh['historicalPreflight']['path'] if item['path']=='production/preflight/game-lighting-history-04.json' else ROOT/item['path']
  if sha(frozen)!=item['sha256']:raise RuntimeError('Reviewed/protected input changed '+item['path'])
 checked=subprocess.run(['node','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
 if checked.returncode:raise RuntimeError('Current distinctness check failed')
 selected=[]
 for r in original['results']:
  current=next(x for x in repair['results'] if x['id']==r['id']) if r['id'] in failed else r
  p=ROOT/current['path']
  if sha(p)!=current['sha256']:raise RuntimeError('Selected take changed '+r['id'])
  a,sr=sf.read(p,dtype='float32',always_2d=False)
  if sr!=24000 or a.ndim!=1 or len(a)!=current['samples']:raise RuntimeError('Stored PCM changed '+r['id'])
  t=render_narration._tail_ratio(a,sr);d=render_narration._tail_decay_ms(a,sr)
  if not render_narration._passes_quality(t,d):raise RuntimeError('Stored selected take fails gate '+r['id'])
  selected.append(dict(**{k:v for k,v in current.items() if k not in ['tailRatio','tailDecayMs','selection','asrDirectlyReviewed']},tailRatio=t,tailDecayMs=d,selection='scoped-retake' if r['id'] in failed else 'unchanged-original-addition',asrDirectlyReviewed=False))
 request['preparedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 request['protectedInputs']=[dict(path=x['path'],sha256=sha(ROOT/x['path'])) if x['path']=='production/preflight/game-lighting-history-04.json' else x for x in scoped['protectedInputs']]+[record(refresh_path),refresh['historicalPreflight']]
 request['duplicateEvidence']=record(refresh_path)['path']
 request['selectionEvidence']=[record(original_path),record(repair_path),record(hpath)]
 for s in request['scenes']:
  picked=next(x for x in selected if x['id']==s['id']);s['path']=picked['path'];s['sha256']=picked['sha256']
 request_path=BASE/'additive-asr-selected-request-v4.json';write(request_path,request)
 execution=dict(schemaVersion=1,selectedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceExecutions=[record(original_path),record(repair_path)],request=record(request_path),leaseToken=repair['leaseToken'],researchHandoff=record(hpath),researchRestoredVerified=True,retainedPassedTakes=22,retakenFailedTakes=2,results=selected,generationComplete=True,exitCode=0,original24TakeFilesPreserved=True,original87Regenerated=False,wholeNewAsrApproved=False,independentContextsApproved=False,finalMixedAsrApproved=False,humanWholeListeningApproved=False,finalVideoProduced=False)
 write(BASE/'additive-tts-selected-execution-v2.json',execution)
 print(json.dumps(dict(selected=24,retained=22,retakes=2,researchRestored=True,asrApproved=False)))
if __name__=='__main__':main()
