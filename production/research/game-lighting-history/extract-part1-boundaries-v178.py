"""Small CPU1 source boundary/framing samples; no final-pixel approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,psutil
root=Path(__file__).resolve().parents[3];folder=root/'projects/game-lighting-history-04/production/local/part1-boundaries-v178';statepath=folder/'execution.json'
if statepath.exists():raise RuntimeError('Preserve existing extraction')
sources={
 'wheel':('production/research/game-lighting-history/local/episode04-additional-action-v47/vsm-initial-editor-goldcoast2024.mp4','d6b2cc2f1a45490b08f1c7834a4bfb20fc19f1be30a62e5b0ee09d834b6ba210'),
 'man':('production/research/game-lighting-history/local/episode04-tsr-browser-v3/mannequin-low-resolution.mp4','6eb1d0f1f506c9ef8902f62e69bcc1e3bdaeeec9006fc5520fd2013dd020b53f'),
 'fan':('production/research/game-lighting-history/local/episode04-tsr-browser-v3/fan-motion-vectors.mp4','fb21a81c1bcdcc337c39c1756622a07c8ffed1c5c783736b575f7d4d378b92a8'),
 'mobile':('production/research/game-lighting-history/local/episode04-additional-action-v44/mobile-profile-shader-editor2024.mp4','507fa8459952670bbb0b298f4b251b5acd6877e32f877f412d50a51b58cec80e')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,(p,digest) in sources.items():
 if sha(root/p)!=digest:raise RuntimeError('Changed source '+name)
rows=[]
for source,times in [('wheel',[112,112.5,113,185.8]),('man',[37,37.5,38]),('fan',[32,32.5,33]),('mobile',[263,264,265,266])]:
 for t in times:rows.append(dict(id=source+'-'+str(t).replace('.','-'),source=source,seconds=t,crop=None))
for ident,t in [('profile',40),('lod',80),('console',100)]:rows.append(dict(id=ident+'-crop',source='mobile',seconds=t,crop=[500,312,1008,567]))
folder.mkdir(parents=True,exist_ok=True);me=psutil.Process()
state=dict(startedAt=datetime.now(timezone.utc).isoformat(),identity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),cpuThreads=1,gpuJobs=0,sources={k:dict(path=v[0],sha256=v[1]) for k,v in sources.items()},results=[],allFinalPixelsReviewed=False,localOnly=True,exactSourceOffsetCertified=False)
def save():
 tmp=statepath.with_name(statepath.name+'.writing-'+str(me.pid));tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,statepath)
save()
try:
 for row in rows:
  source=root/sources[row['source']][0];out=folder/(row['id']+'.png')
  vf='scale=960:-2,setsar=1'
  if row['crop']:
   x,y,w,h=row['crop'];vf=f'crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1'
  cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','1','-ss',str(row['seconds']),'-i',str(source),'-vf',vf,'-filter_threads','1','-frames:v','1','-an','-threads','1','-n',str(out)]
  r=subprocess.run(cmd,cwd=root,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
  if r.returncode:raise RuntimeError(r.stderr)
  state['results'].append({**row,'path':out.relative_to(root).as_posix(),'sha256':sha(out),'exitCode':0,'command':cmd,'directlyRead':False});save()
 state.update(status='17-source-boundary-and-framing-samples-only',endedAt=datetime.now(timezone.utc).isoformat(),exitCode=0);save();print('17 local-only source samples; no final or all-moving approval.')
except BaseException as e:
 state.update(status='failed-preserve-samples',error=repr(e),endedAt=datetime.now(timezone.utc).isoformat(),exitCode=1);save();raise
