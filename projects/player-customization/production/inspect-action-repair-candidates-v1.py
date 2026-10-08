"""Inspect fresh, bounded native candidates for the five recorded mismatches.

Only local QA samples; no allocation, audio, final render or upload approval.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/research/action-repair-candidates-v1'
STATE=BASE/'action-repair-candidate-execution-v1.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
review=read(BASE/'selected-pixels-direct-review-v1.json')
assert review['allBoardsDirectlyRead'] and len(review['unresolvedDefects'])==5
assert not OUT.exists() and not STATE.exists(),'Preserve completed candidate inspection.'
plan=read(ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v3.json')
sources={x['key']:x for x in plan['sources']}
# Unselected gaps/extensions. Selected intervals are not silently approved again.
windows=[('gauss',18.4,21.5),('yareli155',150.35,150.5166667),
         ('yareli',64.6166667,65),('yareli',66.5,69.5),
         ('yareli',54,61),('jadeYareli',515,524)]
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
OUT.mkdir(parents=True)
s=dict(schemaVersion=1,pid=os.getpid(),commandLine=[sys.executable,*sys.argv],startedAt=now(),
 resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,status='inspect-fresh-action-repair-candidates',
 operations=[],samples=[],boards=[],exitCode=None,sourceAllocationApproved=False,allFinalPixels=False,
 collected=False,uploaded=False,imagesLocalOnly=True,newGitImages=0)
def save():
 s['observedAt']=now();t=STATE.with_name(STATE.name+f'.{os.getpid()}.writing')
 t.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,STATE)
try:
 for wi,(key,start,end) in enumerate(windows,1):
  src=sources[key];path=ROOT/src['path'];assert sha(path)==src['sha256']
  pts=read(ROOT/src['ptsPath'])['frames']
  first=round(start*60);last=round(end*60)-1
  indices=sorted(set([first,last,*range(first,last+1,15)]));folder=OUT/f'window-{wi:02d}';folder.mkdir()
  x,y,w,h=src['cropCandidate'];expr='+'.join(f'eq(n,{n})' for n in indices)
  cmd=[FF,'-nostdin','-v','error','-threads','2','-i',str(path),'-an','-filter_threads','1',
       '-vf',f"select='{expr}',crop={w}:{h}:{x}:{y}",'-fps_mode','vfr','-threads','2',str(folder/'frame-%03d.png')]
  log=folder/'extract.log';op=dict(window=wi,source=key,commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
  with log.open('w') as f:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   op['pid']=p.pid;s['activeTask']=op;save();code=p.wait()
  op.update(exitCode=code,endedAt=now());s['activeTask']=None;assert code==0,log.read_text()
  assert len(list(folder.glob('frame-*.png')))==len(indices)
  for i,n in enumerate(indices,1):
   p=folder/f'frame-{i:03d}.png';s['samples'].append(dict(window=wi,sourceKey=key,sourcePath=src['path'],
    sourceSha256=src['sha256'],nativeFrame=n,nativePts=int(pts[n]['best_effort_timestamp']),
    nativeSeconds=float(pts[n]['best_effort_timestamp_time']),path=rel(p),sha256=sha(p),directlyRead=False))
  save()
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for start in range(0,len(s['samples']),6):
  entries=s['samples'][start:start+6];im=Image.new('RGB',(2880,1240),'white');d=ImageDraw.Draw(im)
  for i,e in enumerate(entries):
   x=i%3*960;y=i//3*620
   d.text((x+5,y+5),f"repair window{e['window']} {e['sourceKey']} native{e['nativeSeconds']:.4f}s n{e['nativeFrame']}",fill='black',font=font)
   with Image.open(ROOT/e['path']) as source:im.paste(source.convert('RGB').resize((960,540)),(x,y+65))
  path=OUT/f'board-{start//6+1:02d}.png';im.save(path)
  s['boards'].append(dict(index=start//6+1,path=rel(path),sha256=sha(path),entries=entries,directlyRead=False))
 s.update(status='closed-fresh-action-repair-candidates-await-direct-review',exitCode=0,endedAt=now(),sampleCount=len(s['samples']),boardCount=len(s['boards']))
 save();print(json.dumps(dict(exitCode=0,samples=s['sampleCount'],boards=s['boardCount'],approved=False)),flush=True)
except BaseException:
 s.update(status='closed-action-repair-candidates-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());save();raise
