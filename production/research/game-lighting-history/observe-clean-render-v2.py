from pathlib import Path
from datetime import datetime,timezone
import json,os,psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-03/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,x):
    tmp=p.with_name(p.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
plan=read(BASE/'retained-clean-render-plan-v2.json')
jobs=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
    if p.info['name'].lower()!='ffmpeg.exe':continue
    cmd=' '.join(p.info['cmdline'] or [])
    if 'retained-clean-' not in cmd:continue
    jobs.append(dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),cpuThreads=2,gpuJobs=0,uiTab=17))
assert len(jobs)<=1,'Single owned media job required'
results=[]
for c in plan['chapters']:
    p=ROOT/'production/research/game-lighting-history/local/episode03-chapter-render-v4/renders'/(c['name']+'.verification.json')
    if p.exists():
        r=read(p);assert r['observedFrames']==c['frames'] and r['allPresentationPtsContinuous'] and r['wholeDecode']['exitCode']==0
        results.append(dict(scene=c['scene'],frames=c['frames'],verification=p.relative_to(ROOT).as_posix(),pixelsReviewed=False))
stamp=datetime.now(timezone.utc).isoformat()
record=dict(schemaVersion=1,observedAt=stamp,stage='retained-clean-14-scenes-CPU2-rendering',active=jobs,verified=results,completed=len(results),total=14,allFinalPixelsReviewed=False,finalMixedAsrApproved=False,collected=False,uploaded=False,next='Complete one render at a time; exact90000 PTS/full decode then directly inspect spatial motion and all final caption pixels.')
save(BASE/'retained-clean-render-execution-v2.json',record)
cp=read(ROOT/'production/research/game-lighting-history/checkpoint.json');cp.update(updatedAt=stamp,stage=record['stage'],ownedActiveWork=jobs[0] if jobs else None,ownedJobsRunning=jobs,episode03CleanRenderV2=record);save(ROOT/'production/research/game-lighting-history/checkpoint.json',cp)
print(json.dumps(dict(active=jobs,completed=len(results),total=14),ensure_ascii=False))
