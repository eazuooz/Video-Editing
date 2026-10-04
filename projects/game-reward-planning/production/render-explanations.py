"""Measure the seven reviewed explanations without assembling an incomplete video."""
import hashlib, json, os, re, subprocess, sys, traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
SLUG='game-reward-planning'
SCENES=['01','03','05','07','09','11','13']
STATE=BASE/'explanation-tts-execution.json'
LOG=BASE/'explanation-tts.log'
QUEUE=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    temp=p.with_suffix(p.suffix+'.writing')
    temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(p)

subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs',SLUG,'--check'],cwd=ROOT,check=True)
review=json.loads((BASE/'script-source-review.json').read_text(encoding='utf-8'))
for relative,digest in review['inputs'].items():
    if sha(BASE.parent/relative)!=digest:raise RuntimeError('Review is stale: '+relative)
if review['partialSynthesisScope']!=SCENES:raise RuntimeError('Unexpected synthesis scope')
manifest=json.loads((BASE.parent/'project.json').read_text(encoding='utf-8'))
if not manifest['editing']['openingOverview']['reviewedBeforeTts']:raise RuntimeError('Review overview promises first')
if manifest['tts']['model']!='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base':raise RuntimeError('Preserve approved model')
if manifest['tts']['reference']!='shared/voice-reference/reference-15-35s.wav':raise RuntimeError('Preserve approved voice')
if STATE.exists():
    previous=json.loads(STATE.read_text(encoding='utf-8'))
    if previous.get('status')=='finished-awaiting-full-asr-review':raise RuntimeError('Completed explanation PCM must be preserved; review it next')
    save(BASE/('explanation-tts-history-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'),previous)
state={'schemaVersion':1,'pid':os.getpid(),'startedAt':now(),'status':'loading-approved-qwen-model','scope':SCENES,'scriptInputs':review['inputs'],'referenceSha256':sha(ROOT/manifest['tts']['reference']),'referenceTextSha256':sha(ROOT/manifest['tts']['referenceText']),'model':manifest['tts']['model'],'device':'cuda:0','log':LOG.relative_to(ROOT).as_posix(),'renderedScenes':[],'gpuJobs':1,'finalVideoComplete':False,'fullNarrationComplete':False,'wholeAsrReview':False,'heuristicIsApproval':False,'nextAction':'Measure retained explanations, review every current-hash utterance by ASR, then secure enough related actual actions without shortening explanations.'}
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    save(BASE/'latest-checkpoint.json',state)
    q=json.loads(QUEUE.read_text(encoding='utf-8'))
    items=q.get('items',q.get('videos',[]))
    item=next(v for v in items if v.get('slug')==SLUG)
    item.setdefault('executionHistory',[])
    if item.get('execution',{}).get('pid')!=os.getpid():item['executionHistory'].append(item.get('execution',{}))
    item['stage']='retained-explanations-tts-and-supplementary-action-review'
    item['execution']={'phase':item['stage'],'status':state['status'],'pid':os.getpid(),'state':STATE.relative_to(ROOT).as_posix(),'log':state['log'],'activeTasks':[] if state['gpuJobs']==0 else [{'kind':'qwen-explanation-tts','pid':os.getpid(),'scenes':SCENES}],'gpuJobs':state['gpuJobs'],'noTts':False,'noNewScript':False,'noNewProject':False,'overviewRequired':True,'updatedAt':now()}
    item['scriptDraft']={'scenes':13,'paragraphs':46,'bilingualReview':(BASE/'script-source-review.json').relative_to(ROOT).as_posix(),'completeFinalTiming':False}
    item['checkpoints']['narration']=False
    item['nextAction']=state['nextAction'];item['updatedAt']=now()
    pf=json.loads((ROOT/'production/batches/sakurai-planning-game-design/preflight/game-reward-planning.json').read_text(encoding='utf-8'))
    item['preflight'].update(verdict=pf['verdict'],inputsDigest=pf['inputsDigest'],checkedAt=now(),proof='production/batches/sakurai-planning-game-design/proof-game-reward-planning/content-review-refresh-20261004T0854.json')
    save(QUEUE,q)
checkpoint()
original=sys.stdout
original_stderr=sys.stderr
class Tee:
    def __init__(self,file):self.file=file;self.buffer=''
    def write(self,text):
        original.write(text);original.flush();self.file.write(text);self.file.flush()
        self.buffer+=text
        while '\n' in self.buffer:
            line,self.buffer=self.buffer.split('\n',1)
            found=re.match(r'Rendered (\d+)-scene ',line)
            if found and found.group(1) not in state['renderedScenes']:
                state['renderedScenes'].append(found.group(1));checkpoint()
        return len(text)
    def flush(self):original.flush();self.file.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        sys.path.insert(0,str(ROOT/'qwen3-tts'))
        import render_narration as rn
        rn.configure_project(SLUG)
        rn.load_tts_dependencies()
        items=[i for i in rn.build_render_items(rn.load_jobs()) if i.key.split('-')[0] in SCENES]
        if len(items)!=7:raise RuntimeError('Expected seven independent explanations')
        state['status']='synthesizing-reviewed-explanations';checkpoint()
        rn.render_chunks(items,batch_size=1)
        measured=[]
        for item in items:
            audio,sr=rn._read_mono(item.path)
            measured.append({'scene':item.key.split('-')[0],'path':item.path.relative_to(ROOT).as_posix(),'sha256':sha(item.path),'frames':len(audio),'sampleRate':sr,'seconds':len(audio)/sr,'text':item.text,'tailRatio':rn._tail_ratio(audio,sr),'tailDecayMs':rn._tail_decay_ms(audio,sr),'fullAsrReview':False,'humanListening':'pending'})
        state.update(status='finished-awaiting-full-asr-review',endedAt=now(),gpuJobs=0,exitCode=0,measurements=measured,explanationSpeechSeconds=sum(x['seconds'] for x in measured),renderedScenes=SCENES)
        state['minimumRelatedActionSecondsAt60_40']=1.5*state['explanationSpeechSeconds']
        state['nextAction']='Directly compare full current-hash ASR for all seven explanations; preserve PCM. Expand source actions to cover measured explanation slots and inspect fixed captions before synthesizing actual commentary.'
        save(BASE/'explanation-speech-measurements.json',state)
        checkpoint();print(json.dumps({'status':state['status'],'explanationSpeechSeconds':state['explanationSpeechSeconds'],'minimumRelatedActionSeconds':state['minimumRelatedActionSecondsAt60_40']},ensure_ascii=False),flush=True)
    except BaseException:
        state.update(status='failed',endedAt=now(),gpuJobs=0,exitCode=1,error=traceback.format_exc())
        checkpoint();traceback.print_exc();raise
    finally:
        # Restore streams while the log is still open so interpreter shutdown
        # cannot flush a Tee whose file has already been closed.
        sys.stdout=original
        sys.stderr=original_stderr
