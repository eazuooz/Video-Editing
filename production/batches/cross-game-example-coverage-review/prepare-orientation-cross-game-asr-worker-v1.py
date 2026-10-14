"""Prepare CPU2 whole/context ASR; current PCM is reviewed only after execution."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
src=(ROOT/'production/batches/unpublished-teaching-clarity-revision/review-orientation-additive-voice-v2.py').read_text('utf-8')
src=src.replace('additions-', 'cross-game-').replace('script/additions.ko.json','script/cross-game-repair-batch.ko.json').replace('script/additions.en.json','script/cross-game-repair-batch.en.json')
src=src.replace('narration-tts-execution-v2.json','narration-cross-game-repair-execution-v1.json').replace('research-handoff-verification-v2.json','cross-game-repair-voice-closure-verification-v1.json').replace('narration-tts-session-v2.json','narration-cross-game-repair-session-v1.json')
src=src.replace("resource['ownHeavyCpuJobs']","resource['ownHeavyJobs']").replace("len(tts['results'])==6","len(tts['results'])==5").replace("resume['ttsLeaseToken']","resume['leaseToken']")
src=src.replace("len(script['scenes'])==6 and sum(len(x['lines']) for x in script['scenes'])==22","len(script['scenes'])==5 and sum(len(x['lines']) for x in script['scenes'])==19").replace("len(plan['contexts'])==22","len(plan['contexts'])==19")
src=src.replace('shared/output/unpublished-teaching-clarity-revision/orientation/additive-contexts-v1','shared/output/cross-game-example-coverage-review/orientation/cross-game-contexts-v1')
a=src.index("    item=next(x for x in q['items']");b=src.index('class Tee:',a)
src=src[:a]+"    q['currentOrientationReview'].update(stage=cp['stage'],ownedJob=cp['ownedJob'],activeOwnedWorkers=1 if state['cpuJobs'] else 0,next=cp['next'])\n    q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw,'Preserve a concurrent queue update.';save(qp,q)\n"+src[b:]
src=src.replace("f'additive-{args.mode}-current-CPU-ASR'","f'cross-game-{args.mode}-current-CPU-ASR'")
src=src.replace("currentUnmixedAsrApproved=False,", "currentUnmixedAsrApproved=False,activeOwnedWorkers=state['cpuJobs'],")
dst=B/'review-orientation-cross-game-voice-v1.py';assert not dst.exists();dst.write_text(src,'utf-8');compile(src,str(dst),'exec')
print('Prepared CPU2/GPU0 whole5 and context19 worker; execution/model0.')
