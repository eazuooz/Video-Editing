"""Adapt the reviewed CPU current-AAC worker to orientation; no model run."""
from pathlib import Path
import py_compile
B=Path(__file__).resolve().parent
p=B/'review-motion-current17-mix-v3.py';q=B/'review-orientation-current34-mix-v1.py';assert not q.exists()
t=p.read_text('utf-8-sig')
changes={
"R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'":"R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'",
"current17":"current34",
"whole17":"whole34",
"independent81":"independent180",
"-asr-v3":"-asr-v1",
"-asr-execution-v3":"-asr-execution-v1",
"ownHeavyCpuJobs":"ownHeavyJobs",
"mix=read(R/'current-mix-execution-v2.json');ms=read(R/'current-mix-execution-v2.session.json')":"mix=read(R/'current34-mix-execution-v2.json')",
"assert mix['actualExitCode']==ms['actualOuterExitCode']==0 and ms['workerCurrentlyAlive']==False":"assert mix['actualExitCode']==mix['actualOuterExitCode']==0 and mix['workerDead'] and mix['actualExitObserved']",
"all17RawPcmPlacementsExact":"all34RawPcmPlacementsExact",
"all71ProtectedInputsUnchanged":"all79ProtectedInputsUnchanged",
"plan=read(R/'measured-current34-plan-v2.json');assert sha(R/'measured-current34-plan-v2.json')==mix['planSha256']":"plan=read(R/'current34-measured-timing-plan-v1.json');assert sha(R/'current34-measured-timing-plan-v1.json')==mix['planSha256']",
"s['startFrame']":"s['frameIn']",
"s['endFrame']":"s['frameOut']",
"s['audioSha256']":"s['voiceSha256']",
"assert len(inputs)==17":"assert len(inputs)==34",
"current34-mixed-independent-context-plan-v2.json":"current34-mixed-independent-context-plan-v1.json",
"all17WholeTextsDirectlyCompared":"all34WholeTextsDirectlyCompared",
"assert len(inputs)==81":"assert len(inputs)==180",
"shared/output/cross-game-example-coverage/motion/":"shared/output/unpublished-teaching-clarity-revision/orientation/",
"endswith('revision-cross-game-four-v1/latest-checkpoint.json')":"endswith('revision-teaching-clarity-v1/latest-checkpoint.json')",
"prepare/review complete independent81":"prepare/review complete independent180",
"whole17 current":"whole34 current"
}
for a,b in changes.items():t=t.replace(a,b)
old="subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)"
new="subprocess.run([NODE,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(R/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)"
assert old in t;t=t.replace(old,new)
start=t.index(" adds={x['id']:x['lines']")
end=t.index('else:\n context=',start)
t=t[:start]+" scripts={x['id']:x['lines'] for x in read(R/'script/current34-combined-v1.ko.json')['scenes']}\n for s in plan['scenes']:\n  expected=scripts[s['id']];assert expected\n  inputs.append(dict(id=s['id'],scene=s['id'],sourcePath=rel(source),sourceSha256=sha(source),startSample=s['frameIn']*800,endSample=s['frameOut']*800,zeroPaddingSamplesEachSide=14400,expectedKo=expected,sourceOriginalPcmSha256=s['voiceSha256']))\n assert len(inputs)==34\n"+t[end:]
old=" for v in q.values():\n  if isinstance(v,dict) and str(v.get('currentCheckpoint','')).endswith('revision-teaching-clarity-v1/latest-checkpoint.json'):v.update(activeOwnedWorkers=cp['activeOwnedWorkers'],currentMixedAsrExecution=rel(sp))\n q.update(recordedAt=now(),next=cp['next']);assert qp.read_text('utf-8-sig')==raw;save(qp,q)"
new=" q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],currentMixedAsrExecution=rel(sp),next=cp['next'])\n q.update(updatedAt=now());assert qp.read_text('utf-8-sig')==raw;save(qp,q)"
assert old in t;t=t.replace(old,new)
t=t.replace('independent81','independent180').replace('whole17','whole34')
q.write_text(t,'utf-8');py_compile.compile(str(q),doraise=True)
print('Prepared one CPU2 whole34/independent180 worker; no model or ASR run.')
