"""Extract six previously unobserved native anchors for the two held tracks only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/held-role-anchors-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stamp=lambda:datetime.now(timezone.utc).isoformat()
sp=R/'held-role-anchors-execution-v2.json';assert not sp.exists() and not OUT.exists()
cpu=psutil.cpu_percent(interval=1);ram=psutil.virtual_memory().available//1024;assert cpu<85 and ram>8000000,(cpu,ram)
for p in psutil.process_iter(['pid','cmdline']):
 c=p.info['cmdline'] or []
 if p.pid!=os.getpid() and c and c[0].lower().endswith(('python.exe','node.exe')):assert not any(x in ' '.join(c) for x in ['render-motion-remaining-action-roles-v','extract-motion-held-role-anchors-v'])
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
for row in protected:assert sha(ROOT/row['path'])==row['sha256']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],text=True)
(R/'held-role-anchors-current-cim-v2.json').write_text(cim,'utf-8')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
old=read(R/'remaining-action-annotation-anchors-v1.json');sources={p['sourceKey']:p for p in read(R/'paragraph-native-allocation-v4.json')['newScenes'][0]['parts'] if 'sourceKey' in p}
for sc in read(R/'paragraph-native-allocation-v4.json')['newScenes'][1:]:
 for p in sc['parts']:
  if 'sourceKey' in p:sources[p['sourceKey']]=p
state=dict(schemaVersion=1,startedAt=stamp(),pid=os.getpid(),createTime=psutil.Process().create_time(),cpuThreads=2,gpuJobs=0,resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu),protected71ShaMatched=True,status='running',windows=[],actualOuterExitCode=None)
save=lambda:sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
OUT.mkdir();save()
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(activeOwnedWorkers=1,ownedJob=dict(active=True,pid=state['pid'],createTime=state['createTime'],command=Path(__file__).name,sessionId=None,state=sp.relative_to(ROOT).as_posix()),next='Reuse narrow six-anchor extraction once. Read every new exact native sample, prepare corrected wall-status/plank anchors, then render only two held pieces.');cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
for key,frames in [('portal2',[2352,2383,2413]),('alyx',[3387,3447,3507])]:
 source=sources[key];assert sha(ROOT/source['sourcePath'])==source['sourceSha256']
 folder=OUT/key;folder.mkdir();sel='+'.join(f'eq(n\\,{n})' for n in frames)
 command=[FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/source['sourcePath']),'-vf',f'select={sel},scale=1280:720','-fps_mode','passthrough','-an',str(folder/'sample-%03d.png')]
 run=subprocess.run(command,capture_output=True,text=True);assert run.returncode==0,run.stderr
 rows=[dict(sourceKey=key,nativeFrame=n,pts=n*1001,timeBase='1/30000' if key=='portal2' else '1/60000',path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for n,p in zip(frames,sorted(folder.glob('sample-*.png')))];assert len(rows)==3
 board=Image.new('RGB',(1920,400),'#eee');d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for k,row in enumerate(rows):board.paste(Image.open(ROOT/row['path']).resize((640,360)),(k*640,40));d.text((k*640+8,8),f'{key} native{row["nativeFrame"]}',font=font,fill='black')
 bp=folder/'board-01.png';board.save(bp)
 state['windows'].append(dict(sourceKey=key,sourcePath=source['sourcePath'],sourceSha256=source['sourceSha256'],samples=rows,boards=[dict(path=bp.relative_to(ROOT).as_posix(),sha256=sha(bp))],extractionExitCode=0));save()
state.update(status='completed-awaiting-six-native-direct-review',exitCode=0,finishedAt=stamp());save();print(json.dumps(dict(samples=6,boards=2,exitCode=0)))
