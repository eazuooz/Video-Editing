from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
FINAL=BASE/'final-v1'
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(40):
        try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.1)
STOP={'slug':'familiar-game-rules','userEvidence':'논문 실험 먼저 진행해야 해서 이것까지만 완료되면 일단 정지해줘~','policy':'Finish only this current video through reviewed private settings and selective normal Git push, then PAUSE automation24. Do not start next queued item. Preserve GPU_TTS_HOLD and paper work.','nextQueuedStarted':False,'status':'requested-pause-after-current-delivery'}
def update_checkpoint(stage,action,state=None,**fields):
    stamp=now();qp=PROOF.parent/'queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='familiar-game-rules')
    i.update(stage=stage,updatedAt=stamp,nextAction=action,stopAfterCurrent=STOP,**fields)
    if state is not None:
        i['execution']={k:v for k,v in state.items() if k not in ['commands','cuts','white','segments']}
        i['execution'].update(alive='endedAt' not in state,cpuProductionJobs=int('endedAt' not in state),gpuSynthesisJobs=0,uploads=0)
    q.update(updatedAt=stamp,lastProgressAt=stamp,currentSlug='familiar-game-rules',stopAfterCurrent=STOP)
    write(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        cp=read(p);cp.update(stage=stage,updatedAt=stamp,nextAction=action,stopAfterCurrent=STOP,**fields)
        if state is not None:cp['execution']=i['execution']
        write(p,cp)
class Worker:
    def __init__(self,name,resource,action):
        r=read(ROOT/resource)
        assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85
        assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
        self.path=FINAL/(name+'-execution.json');assert not self.path.exists()
        self.name=name;self.action=action
        self.state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status=name+'-preparing',commandLine=[os.sys.executable,*os.sys.argv],resource=resource,cpuThreads=2,gpuJobs=0,newTts=0,commands=[],activeTasks=[],finalMixAsrApproved=False,allFinalCaptionPixelsReviewed=False)
    def checkpoint(self):
        sp=FINAL/(self.name+'-session.json')
        if sp.exists() and read(sp).get('pid')==os.getpid():self.state['sessionId']=read(sp)['sessionId']
        self.state['updatedAt']=now();write(self.path,self.state)
        update_checkpoint('current-final-'+self.name,self.action,self.state)
    def run(self,exe,args,kind,cwd=None):
        command=[str(exe),*map(str,args)];log=FINAL/f'{self.name}-{len(self.state["commands"])+1:03d}.log'
        with log.open('x',encoding='utf-8') as fh:
            p=subprocess.Popen(command,cwd=cwd or ROOT,stdout=fh,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            self.state.update(status=kind,activeTasks=[dict(kind=kind,pid=p.pid,commandLine=command,log=rel(log))]);self.checkpoint();code=p.wait()
        self.state['commands'].append(dict(commandLine=command,pid=p.pid,exitCode=code,log=rel(log)));self.state['activeTasks']=[];self.checkpoint()
        if code:raise RuntimeError(f'{kind} exit{code}: {log}')
        return log.read_text(encoding='utf-8')
    def ff(self,args,kind,cwd=None):return self.run(FF,['-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind,cwd)
    def close(self,status,code=0,error=None):
        self.state.update(status=status,endedAt=now(),exitCode=code,activeTasks=[])
        if error:self.state['error']=error
        self.checkpoint()
