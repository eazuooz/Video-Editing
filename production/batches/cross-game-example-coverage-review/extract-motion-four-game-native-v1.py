"""Single CPU2/GPU0 native-PTS candidate extraction. All outputs are local-only."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import hashlib,json,os,subprocess,traceback
os.environ['OMP_NUM_THREADS']='2'
from PIL import Image,ImageDraw,ImageFont
import psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/native-preflight-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
 report=R/'native-preflight-execution-v1.json';assert not report.exists(),'Read completed/current report instead of duplicating extraction'
 pre=json.loads((R/'source-preflight-v1.json').read_text('utf-8'));assert all(sha(ROOT/x['path'])==x['sha256'] for x in pre['protectedBaseline'])
 own=psutil.Process();resource=dict(observedAt=now(),pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd(),pythonProcesses=[dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline()) for p in psutil.process_iter() if p.name().lower().startswith('python')],gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout.strip(),cpuThreads=2,gpuWorker=False,researchManipulation=False)
 save(R/'native-preflight-resource-v1.json',resource)
 state=dict(status='running',startedAt=now(),pid=own.pid,createTime=own.create_time(),windows=[],wholeFinalApproval=False,exitCode=None);save(report,state)
 OUT.mkdir(parents=True,exist_ok=True)
 try:
  frames={}
  for src in pre['sources']:
   assert sha(ROOT/src['path'])==src['sha256']
   z=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=pts,best_effort_timestamp','-of','json',str(ROOT/src['path'])]))
   pts=[int(f.get('pts',f['best_effort_timestamp'])) for f in z['frames']];assert len(pts)==len(set(pts)) and all(b>a for a,b in zip(pts,pts[1:]));frames[src['key']]=pts
   save(OUT/(src['key']+'-native-pts.json'),dict(source=src,pts=pts))
  windows=[('portal-aim','portal2',16,40),('portal-traverse','portal2',58,82),('portal-cube','portal2',84,99),('alyx-platform','alyx',48,69),('alyx-hand','alyx',108,124),('alyx-locomotion','alyx',164,180)]
  font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
  for name,key,start,end in windows:
   src=next(s for s in pre['sources'] if s['key']==key);tb=Fraction(src['video']['time_base']);pts=frames[key]
   idx=[]
   import bisect
   for t in range(start,end+1):idx.append(bisect.bisect_left(pts,Fraction(t)/tb))
   idx=list(dict.fromkeys(idx));assert idx[-1]<len(pts)
   folder=OUT/name;folder.mkdir(exist_ok=True)
   select='+'.join('eq(n\\,%d)'%n for n in idx)
   cmd=[FF,'-v','error','-threads','2','-i',str(ROOT/src['path']),'-vf',f'select={select},scale=1280:-2','-filter_threads','2','-fps_mode','vfr','-frames:v',str(len(idx)),'-threads','2',str(folder/'sample-%03d.png')]
   with (folder/'ffmpeg-command.json').open('w',encoding='utf-8') as f:json.dump(cmd,f,indent=2)
   run=subprocess.run(cmd,capture_output=True,text=True);(folder/'ffmpeg.log').write_text(run.stderr,'utf-8');assert run.returncode==0,run.stderr
   samples=[]
   for i,n in enumerate(idx,1):
    p=folder/f'sample-{i:03d}.png';assert p.is_file();samples.append(dict(path=rel(p),sha256=sha(p),nativeFrame=n,pts=pts[n],timeBase=str(tb),seconds=float(pts[n]*tb)))
   sheets=[]
   for first in range(0,len(samples),6):
    subset=samples[first:first+6];sheet=Image.new('RGB',(1920,780),(245,245,245));d=ImageDraw.Draw(sheet)
    for j,item in enumerate(subset):
     x=(j%3)*640;y=(j//3)*390
     with Image.open(ROOT/item['path']) as im:sheet.paste(im.resize((640,360)),(x,y))
     d.text((x+5,y+363),f"{name} f{item['nativeFrame']} PTS{item['pts']} {item['seconds']:.6f}s",font=font,fill=(0,0,0))
    p=folder/f'sheet-{first//6+1:02d}.png';sheet.save(p);sheets.append(dict(path=rel(p),sha256=sha(p),sampleCount=len(subset)))
   row=dict(name=name,sourceKey=key,nominalWindow=[start,end],nativeInFrame=idx[0],nativeOutFrameExclusive=idx[-1],inPts=pts[idx[0]],outPts=pts[idx[-1]],timeBase=str(tb),samples=samples,sheets=sheets,ffmpegExit=run.returncode,allSamplesDirectlyRead=False,footageAdopted=False)
   state['windows'].append(row);save(report,state);print(json.dumps(dict(window=name,samples=len(samples),sheets=len(sheets)),ensure_ascii=False),flush=True)
  assert all(sha(ROOT/x['path'])==x['sha256'] for x in pre['protectedBaseline'])
  state.update(status='complete-awaiting-direct-review',finishedAt=now(),exitCode=0,protectedBaselineUnchanged=True,totalSamples=sum(len(x['samples']) for x in state['windows']),totalSheets=sum(len(x['sheets']) for x in state['windows']));save(report,state)
 except Exception:
  state.update(status='failed-preserve-history',finishedAt=now(),exitCode=1,error=traceback.format_exc());save(report,state);raise
if __name__=='__main__':main()
