"""Prepare one guarded voice batch; no model, GPU request or media execution."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=read(ROOT/'production/preflight/game-math-orientation-matrices.json')
assert inv['verdict']=='distinct' and len(inv['inputFiles'])==509
out=O/'duplicate-current-check-verification-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(verifiedAt=datetime.now(timezone.utc).isoformat(),actualDecision='eb2f6e exit0',actualCheck='c512ff exit0',currentCheckPassed=True,inventoryDigest=inv['inputsDigest'],projectCount=88,inputCount=509,evidence=[dict(path='production/preflight/game-math-orientation-matrices.json',sha256=sha(ROOT/'production/preflight/game-math-orientation-matrices.json')),dict(path=(O/'duplicate-content-and-studio-direct-review-v1.json').relative_to(ROOT).as_posix(),sha256=sha(O/'duplicate-content-and-studio-direct-review-v1.json'))]),ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'render-motion-four-additions-v7.py').read_text('utf-8')
src=src.replace('projects/motion-sickness-games/production/revision-cross-game-four-v1','projects/game-math-orientation-matrices/revision-teaching-clarity-v1').replace('motion-sickness-games','game-math-orientation-matrices')
src=src.replace('narration-tts-execution-v7.json','narration-cross-game-repair-execution-v1.json').replace('narration-tts-request-v1.json','narration-cross-game-repair-request-v1.json').replace('narration-tts-session-v7.json','narration-cross-game-repair-session-v1.json').replace('narration-tts-waiting-v7.json','narration-cross-game-repair-waiting-v1.json')
src=src.replace("'game-math-orientation-matrices','--check'","'game-math-orientation-matrices','--candidate-file','projects/game-math-orientation-matrices/revision-teaching-clarity-v1/duplicate-candidate-v1.json','--check'")
a=src.index("failed=read(");b=src.index('# Initial request needs',a)
src=src[:a]+"retry=read(R/'resource-before-cross-game-repair-voice-v1.json')\nassert retry['protectedShaMatched']\nif not args.dry_run: assert retry['voiceEligibleAtObservation'] and retry['stableGpuIdle20SecondsVerified']\n"+src[b:]
src=src.replace("early_lease['updatedAt']","early_lease.get('updatedAt',early_lease.get('requestedAt'))")
src=src.replace("else:\n    assert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240", "elif not args.dry_run:\n    assert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240")
src=src.replace("request['total']==3 and request['paragraphs']==15","request['total']==5 and request['paragraphs']==19")
a=src.index("bank=read(");b=src.index('assert not STATE.exists()',a)
src=src[:a]+"source_review=read(ROOT/request['sourceReview'])\nassert source_review['sourcePlanningMayProceed']\n"+src[b:]
a=src.index("protected=request['protectedInputs']+");b=src.index("for k in ['OMP_NUM_THREADS'",a)
src=src[:a]+"protected=request['protectedInputs']+[dict(path=rel(p),sha256=sha(p)) for p in [REQUEST,R/'duplicate-current-check-verification-v1.json',R/'cross-game-plan-review-flag-transition-v1.json']]\n"+src[b:]
src=src.replace('Prepared3newcomparisons/15pairedparagraphs;14approvedPCM preserved.','Prepared5items/19pairedparagraphs;24original+6additivePCM preserved.')
src=src.replace("stage='serialized-three-comparisons-request-before-model'","stage='serialized-five-items-request-before-model'")
needle="lease=read(leasePath)\nstate=dict("
extra="""lease=read(leasePath)
# The completed research queue is not restarted. Idle ownership still needs
# continuous20s low utilization, with the unchanged600s maximum, before loading.
if lease.get('idleGpu'):
    deadline=time.monotonic()+600;stable=None;samples=[]
    while True:
        assert read(leasePath)['token']==lease['token']
        raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
        free,util=map(int,raw.splitlines()[0].replace(' ','').split(','));stamp=time.monotonic()
        samples.append(dict(observedAt=now(),freeMiB=free,utilization=util))
        if free>=18000 and util<15:
            if stable is None:stable=stamp
            if stamp-stable>=20:break
        else:stable=None
        if stamp>=deadline:raise RuntimeError('600s stableGPU idle guard expired before model load')
        time.sleep(2)
    save(R/'cross-game-repair-owned-idle-guard-v1.json',dict(verifiedAt=now(),leaseToken=lease['token'],continuousIdleSeconds=stamp-stable,samples=samples,stable20SecondsVerified=True,researchRestarted=False))
else:
    assert lease['state']=='tts_running' and time.time()-lease['updatedAt']<240
    assert lease['gpuBeforeTts']['freeMiB']>=18000 and lease['gpuBeforeTts']['utilization']<15
state=dict("""
assert needle in src;src=src.replace(needle,extra)
src=src.replace('total=3,results=[]','total=5,results=[]').replace('original14PcmRegenerated=0','original24PcmRegenerated=0,existing6PcmRegenerated=0').replace('total=3,exitCode','total=5,exitCode').replace("state['results'])==3","state['results'])==5")
src=src.replace('three-comparisons-measured-awaiting-whole-current-ASR-and-research-resume','five-items-measured-awaiting-current-ASR-and-owned-closure')
src=src.replace('Three comparisons measured; original14PCM preserved.','Five items measured; original24+6PCM preserved.')
src=src.replace('After actual outer exit verify own lease history and original research resume; then directly compare three whole current-PCM ASR texts and complete independent contexts.', 'After actual outer exit verify owned lease closure and completed research preservation, or exact original queue resume if it was active; compare allfive currentwhole PCM and19independent contexts.')
dst=B/'render-orientation-cross-game-repair-v1.py';assert not dst.exists();dst.write_text(src,'utf-8')
compile(src,str(dst),'exec')
print(json.dumps(dict(wrapper=dst.relative_to(ROOT).as_posix(),preparedOnly=True,items=5,paragraphs=19,model=0,requests=0)))
