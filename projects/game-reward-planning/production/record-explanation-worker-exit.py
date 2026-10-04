"""Record actual process exit without discarding successfully generated PCM."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
base=Path(__file__).resolve().parent
root=base.parents[2]
now=datetime.now(timezone.utc).isoformat()
def save(p,v):
    temp=p.with_suffix(p.suffix+'.writing')
    temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(p)
p=base/'explanation-tts-execution.json'
state=json.loads(p.read_text(encoding='utf-8'))
for m in state['measurements']:
    if hashlib.sha256((root/m['path']).read_bytes()).hexdigest()!=m['sha256']:
        raise RuntimeError('PCM changed: '+m['scene'])
state['historicalRunnerDeclaredExitCode']=state.get('exitCode')
state['exitCode']=1
state['generationCompleted']=True
state['workerCompletionObservation']={
    'observedAt':now,'sessionId':6178,'pid':55404,'actualProcessExitCode':1,
    'finalGenerationMessage':'finished-awaiting-full-asr-review; explanationSpeechSeconds162.0',
    'shutdownOutput':'Exception ignored in: Exception ignored in sys.unraisablehook',
    'interpretation':'Seven generated PCM files match measured hashes. The runner left stdout/stderr pointing to the Tee after closing its log; stream restoration was added for future runs. This likely explains the shutdown exception; the actual process exit remains1.',
    'rerunPerformed':False,'humanListening':'pending','fullNarrationComplete':False}
state['updatedAt']=now
save(p,state);save(base/'explanation-speech-measurements.json',state)
save(base/'explanation-worker-exit-observation.json',state['workerCompletionObservation'])
save(base/'latest-checkpoint.json',state)
qpath=root/'production/batches/sakurai-planning-game-design/queue.json'
q=json.loads(qpath.read_text(encoding='utf-8'))
item=next(i for i in q['items'] if i['slug']=='game-reward-planning')
item.setdefault('executionHistory',[]).append(dict(item.get('execution',{})))
item['execution']={
    'phase':'current-explanation-asr-and-extra-actions', 'status':'cpu-asr-running',
    'pid':12208,'launcherPid':25700,'sessionId':18299,'gpuJobs':0,
    'activeTasks':[{'kind':'current-hash-explanation-asr','pid':12208,'launcherPid':25700,'sessionId':18299,'device':'cpu','scenes':['07','09','11','13']}],
    'noTts':False,'noNewScript':False,'noNewProject':False,'updatedAt':now,
    'completedExplanationWorker':state['workerCompletionObservation']}
item['nextAction']='Compare full current-hash ASR for seven explanations and secure additional actual actions. Preserve completed explanation PCM; do not re-run the closed worker.'
item['updatedAt']=now;q['updatedAt']=now;save(qpath,q)
print(json.dumps({'actualWorkerExitCode':1,'preservedExplanationFiles':7,'cpuAsrPid':12208,'cpuAsrSession':18299}))
