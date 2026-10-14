"""One CPU2/GPU0 exact native PTS audit of the eight retained gameplay scenes."""
from pathlib import Path
import json,hashlib,subprocess,datetime,re,os
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sp=R/'selected-native-execution-v1.json';assert not sp.exists(),'Resume actual worker instead of repeating extraction'
review=read(R/'source-clarity-direct-review-v1.json');assert review['actualOuterExitCode']==0
baseline=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'serve-native-review|9253|train_multiview|phase1_train|queue|gpu-handoff|unpublished-teaching') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf8')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True)
write(R/'selected-native-resource-v1.json',{'observedAt':now(),'cim':json.loads(cim),'gpu':gpu.strip(),'cpuThreads':2,'gpuJobs':0,'foreignProcessesModified':0})
me=psutil.Process();st={'startedAt':now(),'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT),'status':'preparing','sessionId':None,'cpuThreads':2,'gpuJobs':0,'actualOuterExitCode':None,'allSelectedPixelsRead':False};write(sp,st)
out=R/'selected-native-v1';out.mkdir(exist_ok=True)
source=ROOT/'shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4'
assert sha(source)=='469df1da0e7fce4b5480064e43a2982e1121f9e1adb899acdbbd8f464371fd66'
cuts=read(ROOT/'projects/game-math-orientation-matrices/sources/gameplay-cuts.json')['cuts']
windows=[];targetFrames=set()
for cut in cuts:
 for index,seg in enumerate(cut['segments']):
  start=round(seg['in']*60);end=start+seg['frames']
  frames=sorted(set(range(start,end,60))|{start,(start+end-1)//2,end-1})
  windows.append({'scene':cut['scene'],'segment':index,'startNativeFrame':start,'endNativeFrameExclusive':end,'startPts':start*256,'endPtsExclusive':end*256,'seconds':seg['frames']/60,'focus':cut['focus'],'claim':cut['claim'],'targetNativeFrames':frames,'allSamplesDirectlyRead':False,'wholeFramesApproved':False})
  targetFrames.update(frames)
targets=sorted(targetFrames);reused={x['sourceFrame']:x for x in read(R/'local-audit-pixels-v2/ncr/manifest.json')['samples'] if x['sourceFrame'] in targetFrames}
assert all(sha(ROOT/x['path'])==x['sha256'] for x in reused.values())
fresh=[x for x in targets if x not in reused]
select='+'.join(f'eq(pts,{f*256})' for f in fresh)
cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f"select='{select}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(fresh)),'-threads','2','-compression_level','3',str(out/'sample-%04d.png')]
write(out/'plan.json',{'source':rel(source),'sourceSha256':sha(source),'timeBase':'1/15360','nativeFramePtsStep':256,'windows':windows,'targetFrames':targets,'reusedFrames':sorted(reused),'freshFrames':fresh,'command':cmd,'browserTimeNotUsedForInOut':True})
try:
 with (out/'extract.log').open('w',encoding='utf8') as log:
  p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT);st.update({'status':'extracting','ffmpegPid':p.pid,'ffmpegCreateTime':psutil.Process(p.pid).create_time(),'log':rel(out/'extract.log'),'requestedSamples':len(targets),'freshSamples':len(fresh),'reusedSamples':len(reused)});write(sp,st);rc=p.wait()
 observed=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',(out/'extract.log').read_text(encoding='utf8'))]
 files=sorted(out.glob('sample-*.png'));assert rc==0 and observed==[f*256 for f in fresh] and len(files)==len(fresh),(rc,len(observed),len(files))
 samples={f:{'path':rel(p),'pts':f*256,'sourceFrame':f,'seconds':f/60,'sha256':sha(p),'reused':False} for f,p in zip(fresh,files)}
 samples.update({f:{**row,'reused':True} for f,row in reused.items()})
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for win in windows:
  ws=[samples[f] for f in win['targetNativeFrames']]
  for offset in range(0,len(ws),6):
   group=ws[offset:offset+6];im=Image.new('RGB',(1280,1176),'#181818');draw=ImageDraw.Draw(im)
   for j,row in enumerate(group):
    x=j%2*640;y=j//2*392
    with Image.open(ROOT/row['path']) as frame:im.paste(frame.resize((640,360)),(x,y))
    draw.text((x+6,y+365),f'{win["scene"]}/{win["segment"]} f{row["sourceFrame"]} PTS{row["pts"]} {row["seconds"]:.3f}s',font=font,fill='white')
   bp=out/f'scene-{win["scene"]}-segment-{win["segment"]}-board-{offset//6+1:03d}.png';im.save(bp);boards.append({'path':rel(bp),'sha256':sha(bp),'scene':win['scene'],'segment':win['segment'],'samples':[x['path'] for x in group]})
 manifest={'source':rel(source),'sourceSha256':sha(source),'actualFfmpegExitCode':rc,'timeBase':'1/15360','actualPtsMatch':True,'windows':windows,'samples':[samples[f] for f in targets],'boards':boards,'allSamplesDirectlyRead':False,'nativeWholeFramesApproved':False,'annotationApproved':False,'publicRightsApproved':False};write(out/'manifest.json',manifest)
 st.update({'status':'completed-awaiting-direct-read','workerExitCode':0,'completedAt':now(),'manifest':rel(out/'manifest.json'),'samples':len(samples),'boards':len(boards)});write(sp,st);print(json.dumps({'samples':len(samples),'boards':len(boards),'reused':len(reused),'workerExitCode':0}))
except BaseException as e:
 st.update({'status':'failed','workerExitCode':1,'error':repr(e)});write(sp,st);raise
