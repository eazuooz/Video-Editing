"""Finite selected-project voice job; wait without touching other applications."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess,sys,time
import psutil

ROOT=Path(__file__).resolve().parents[3]
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--manifest');ap.add_argument('--wait-hours',type=float,default=6);a=ap.parse_args()
    control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert a.project in control['projectSlugs'] and control['productionAllowedNow']
    manifest=(ROOT/a.manifest).resolve() if a.manifest else ROOT/'projects'/a.project/'production/tts-manifest.json'
    assert manifest.is_relative_to(ROOT/'projects'/a.project/'production')
    folder=(ROOT/read(manifest)['tts']['outputDir']).resolve();assert folder.is_relative_to(ROOT/'projects'/a.project/'production/local');folder.mkdir(parents=True,exist_ok=True)
    statefile=folder/'finite-worker.json'
    if statefile.exists():
        old=read(statefile)
        try:
            p=psutil.Process(old['pid'])
            assert abs(p.create_time()-old['createTime'])>.1,'Same finite voice job is already running'
        except psutil.NoSuchProcess:pass
    state={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'project':a.project,'status':'waiting-for-resource-boundary','startedAt':now(),'automationCreated':False,'nextProject':False,'newTtsStarted':False}
    cmd=[str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'production/batches/game-math-remaining-20261104/render-voice.py'),'--project',a.project,'--allow-idle-editors']
    if a.manifest:cmd+=['--manifest',str(manifest)]
    started=time.monotonic()
    try:
        while True:
            control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
            assert control['productionAllowedNow'] and a.project in control['projectSlugs']
            result=subprocess.run(cmd+['--check-resources'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            state['checkedAt']=now();state['resourceReturnCode']=result.returncode
            state['resourceResult']=(result.stdout+result.stderr)[-6000:];save(statefile,state)
            if result.returncode==0:break
            if time.monotonic()-started>a.wait_hours*3600:raise RuntimeError('Bounded resource wait ended; all other apps preserved')
            time.sleep(30)
        state.update(status='synthesizing',newTtsStarted=True);save(statefile,state)
        with (folder/'finite-synthesis.stdout.log').open('w',encoding='utf-8') as out,(folder/'finite-synthesis.stderr.log').open('w',encoding='utf-8') as err:
            p=subprocess.Popen(cmd+['--synthesize'],cwd=ROOT,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            state['voicePid']=p.pid;save(statefile,state);code=p.wait()
        if code:raise RuntimeError('Voice worker failed; preserve logs/raw takes for diagnosis')
        state.update(status='voice-generated-review-pending',finishedAt=now(),exitCode=0);save(statefile,state)
    except BaseException as exc:
        state.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,state);raise
if __name__=='__main__':main()
