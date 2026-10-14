"""Inspect only newly needed button-result timing and tail, reusing exact samples."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/button-result-timing-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=R/'button-result-timing-execution-v1.json';assert not sp.exists() and not OUT.exists()
cpu=psutil.cpu_percent(interval=1);ram=psutil.virtual_memory().available//1024;assert cpu<85 and ram>8000000
cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],capture_output=True,text=True,check=True).stdout
(R/'button-result-timing-current-cim-v1.json').write_text(cim,'utf-8')
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
for p in psutil.process_iter(['pid','cmdline']):
 c=p.info['cmdline'] or []
 if p.pid!=os.getpid() and c and c[0].lower().endswith(('python.exe','node.exe')):
  assert not any(v in ' '.join(c) for v in ['render-motion-extra-annotation-pieces-v','extract-motion-button-result-timing-v1.py'])
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
for x in protected:assert sha(ROOT/x['path'])==x['sha256']
src=read(R/'sources/source-action-bank-v1.json')['sources'][0];assert sha(ROOT/src['path'])==src['sha256']
allrows=[]
for w in read(R/'native-preflight-execution-v1.json')['windows']:allrows+=w['samples']
reuse={r['nativeFrame']:r for r in allrows if 2938<=r['nativeFrame']<2992}
frames=list(range(2938,2992));fresh=[n for n in frames if n not in reuse]
OUT.mkdir();(OUT/'samples').mkdir()
state=dict(schemaVersion=1,pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=psutil.Process().cmdline(),cwd=str(ROOT),startedAt=datetime.now(timezone.utc).isoformat(),cpuThreads=2,gpuJobs=0,
 resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu),protected71ShaMatched=True,source=src,frames=frames,status='running',actualOuterExitCode=None,samples=[],boards=[])
save=lambda:sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');save()
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(activeOwnedWorkers=1,ownedJob=dict(active=True,pid=state['pid'],createTime=state['createTime'],command=Path(__file__).name,sessionId=None,state=sp.relative_to(ROOT).as_posix()),next='Reuse this narrow button-result timing worker; on exit directly inspect all54 native frames and exclude any tail promo. Existing QA is retained, not re-extracted.');cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
sel='+'.join(f'eq(n\\,{n})' for n in fresh)
cmd=[FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/src['path']),'-vf','select='+sel,'-fps_mode','passthrough','-an',str(OUT/'samples/frame-%03d.png')]
run=subprocess.run(cmd,capture_output=True,text=True);assert run.returncode==0,run.stderr
newfiles=iter(sorted((OUT/'samples').glob('frame-*.png')))
for n in frames:
 if n in reuse:
  r=reuse[n];p=ROOT/r['path'];assert sha(p)==r['sha256'];reused=True
 else:p=next(newfiles);reused=False
 state['samples'].append(dict(nativeFrame=n,pts=n*1001,timeBase='1/30000',path=p.relative_to(ROOT).as_posix(),sha256=sha(p),reused=reused))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for start in range(0,len(frames),12):
 rows=state['samples'][start:start+12];im=Image.new('RGB',(1920,1600),'#e8e8e8');d=ImageDraw.Draw(im)
 for k,r in enumerate(rows):
  x=(k%3)*640;y=(k//3)*400;im.paste(Image.open(ROOT/r['path']).resize((640,360)),(x,y+40));d.text((x+8,y+8),f"native{r['nativeFrame']} {r['pts']/30000:.6f}s",font=font,fill='black')
 p=OUT/f'board-{len(state["boards"])+1:02d}.png';im.save(p);state['boards'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=rows))
state.update(status='completed-awaiting-direct-result-frame-review',exitCode=0,extractionExitCode=0,freshCount=len(fresh),reuseCount=len(reuse),finishedAt=datetime.now(timezone.utc).isoformat());save()
print(json.dumps(dict(samples=len(frames),fresh=len(fresh),reuse=len(reuse),boards=len(state['boards']),extractionExitCode=0)))
