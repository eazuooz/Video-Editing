"""New bounded source probes; reuse all matching sealed native samples."""
from pathlib import Path
import json,hashlib,subprocess,datetime,re,os
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
sp=R/'repair-candidate-execution-v1.json';assert not sp.exists(),'Read actual running/completed worker; do not repeat.'
review=read(R/'selected-native-direct-review-v1.json');assert review['actualOuterExitCode']==0
baseline=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'serve-native-review|9253|train_multiview|phase1_train|queue|gpu-handoff|unpublished-teaching') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf8')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True)
write(R/'repair-candidate-resource-v1.json',{'observedAt':now(),'cim':json.loads(cim),'gpu':gpu.strip(),'cpuThreads':2,'gpuJobs':0,'foreignProcessesModified':0})
me=psutil.Process();st={'startedAt':now(),'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT),'status':'preparing','sessionId':None,'cpuThreads':2,'gpuJobs':0,'actualOuterExitCode':None};write(sp,st)
source=ROOT/'shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4'
assert sha(source)=='469df1da0e7fce4b5480064e43a2982e1121f9e1adb899acdbbd8f464371fd66'
# Sparse event probes narrow a transition; their labels are actual native PTS,
# but no boundary or every-frame approval is inferred from adjacent samples.
defs=[('event02',51.5,54.1,6),('event11',364,365.2,6),('event14a',515,518,6),('event14b',525,528,6),('event14c',537,540,6),
      ('unused83',83,143,60),('unused403',403,504,60),('unused871',871,922,60),('extend19',19,22,30),('extend350',350,351,30)]
windows=[];target=set()
for name,a,b,step in defs:
 start=round(a*60);end=round(b*60);frames=sorted(set(range(start,end,step))|{start,end-1})
 windows.append({'name':name,'startNativeFrame':start,'endNativeFrameExclusive':end,'sourcePtsIn':start*256,'sourcePtsOutExclusive':end*256,'targetNativeFrames':frames,'stepNativeFrames':step,'wholeContinuityApproved':False,'exactEventBoundaryApproved':False})
 target.update(frames)
prior=read(R/'selected-native-v1/manifest.json')['samples']
reused={x['sourceFrame']:x for x in prior if x['sourceFrame'] in target}
assert all(sha(ROOT/x['path'])==x['sha256'] for x in reused.values())
fresh=sorted(target-set(reused));out=R/'repair-candidate-native-v1';out.mkdir(exist_ok=True)
select='+'.join(f'eq(pts,{f*256})' for f in fresh)
cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f"select='{select}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(fresh)),'-threads','2','-compression_level','3',str(out/'sample-%04d.png')]
write(out/'plan.json',{'source':rel(source),'sourceSha256':sha(source),'timeBase':'1/15360','nativeFramePtsStep':256,'windows':windows,'freshFrames':fresh,'reusedFrames':sorted(reused),'command':cmd,'newMediaAdopted':False})
try:
 with (out/'extract.log').open('w',encoding='utf8') as log:
  p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT);st.update({'status':'extracting','ffmpegPid':p.pid,'ffmpegCreateTime':psutil.Process(p.pid).create_time(),'log':rel(out/'extract.log'),'requestedSamples':len(target),'freshSamples':len(fresh),'reusedSamples':len(reused)});write(sp,st);rc=p.wait()
 observed=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',(out/'extract.log').read_text(encoding='utf8'))]
 files=sorted(out.glob('sample-*.png'));assert rc==0 and observed==[f*256 for f in fresh] and len(files)==len(fresh),(rc,len(observed),len(files))
 samples={f:{'path':rel(p),'sha256':sha(p),'sourceFrame':f,'pts':f*256,'seconds':f/60,'reused':False} for f,p in zip(fresh,files)}
 samples.update({f:{**x,'reused':True} for f,x in reused.items()})
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);boards=[]
 for w in windows:
  rows=[samples[f] for f in w['targetNativeFrames']]
  for offset in range(0,len(rows),6):
   group=rows[offset:offset+6];im=Image.new('RGB',(1280,1176),'#181818');draw=ImageDraw.Draw(im)
   for j,x in enumerate(group):
    px=j%2*640;py=j//2*392
    with Image.open(ROOT/x['path']) as frame:im.paste(frame.resize((640,360)),(px,py))
    draw.text((px+6,py+365),f'{w["name"]} f{x["sourceFrame"]} PTS{x["pts"]} {x["seconds"]:.3f}s',font=font,fill='white')
   bp=out/f'{w["name"]}-board-{offset//6+1:03d}.png';im.save(bp);boards.append({'path':rel(bp),'sha256':sha(bp),'window':w['name'],'samples':[x['path'] for x in group]})
 manifest={'source':rel(source),'sourceSha256':sha(source),'actualFfmpegExitCode':rc,'actualPtsMatch':True,'timeBase':'1/15360','windows':windows,'samples':[samples[f] for f in sorted(target)],'boards':boards,'allSamplesDirectlyRead':False,'allIntermediateFramesRead':False,'sourceAdoptionApproved':False,'finalNarrationApproved':False};write(out/'manifest.json',manifest)
 st.update({'status':'completed-awaiting-direct-read','workerExitCode':0,'completedAt':now(),'samples':len(samples),'boards':len(boards),'manifest':rel(out/'manifest.json')});write(sp,st)
 print(json.dumps({'samples':len(samples),'fresh':len(fresh),'reused':len(reused),'boards':len(boards),'workerExitCode':0}))
except BaseException as e:
 st.update({'status':'failed','workerExitCode':1,'error':repr(e)});write(sp,st);raise
