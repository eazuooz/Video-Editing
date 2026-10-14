"""Single CPU2/GPU0 exact-PTS samples for candidate and retained-pixel audit."""
from pathlib import Path
import json,hashlib,subprocess,datetime,re,os,sys
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]; R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
statepath=R/'audit-pixel-execution-v1.json';assert not statepath.exists(),'Resume existing execution instead'
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'serve-native-review|9253|train_multiview|phase1_train|queue|gpu-handoff|unpublished-teaching') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf8')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True)
write(R/'audit-extraction-resource-v1.json',{'observedAt':now(),'cim':json.loads(cim),'gpu':gpu.strip(),'cpuThreads':2,'gpuJobs':0,'foreignProcessesModified':0})
me=psutil.Process();st={'startedAt':now(),'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','actualOuterExitCode':None,'outputs':[],'allPixelsDirectlyRead':False};write(statepath,st)
root=R/'local-audit-pixels-v1';root.mkdir(exist_ok=True)
plans=[('ncr',ROOT/'shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4',[22,26,30,36,41,47,55,60]),('alternative',ROOT/'shared/output/game-math-part2-full-series/sources/FvSgGn941U0.mp4',[22,26,30,36,41,47,55,60]),('baseline',ROOT/'shared/output/motion-canvas/game-math-orientation-matrices-subtitled.mp4',[2,10,19,23,40,58,68,86,105,122,140,166,185,203,218,242,259,280,305,339,380,423,454,491,539,578,615,659,695,732,764,806,846,880])]
try:
 for key,source,times in plans:
  folder=root/key;folder.mkdir(exist_ok=True)
  probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,duration','-of','json',str(source)]))['streams'][0]
  assert probe['avg_frame_rate']=='60/1' and probe['time_base']=='1/15360',probe
  targets=[round(t*15360) for t in times];select='+'.join('eq(pts,%d)'%p for p in targets)
  cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f"select='{select}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(targets)),'-threads','2','-compression_level','3',str(folder/'sample-%04d.png')]
  write(folder/'extract-command.json',{'command':cmd,'requestedPts':targets,'timeBase':'1/15360','sourceSha256':sha(source),'probe':probe})
  log=folder/'extract.log'
  with log.open('w',encoding='utf8') as out:
   process=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,cwd=ROOT);st['currentJob']={'kind':key,'pid':process.pid,'createTime':psutil.Process(process.pid).create_time(),'log':rel(log)};write(statepath,st);rc=process.wait()
  observed=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',log.read_text(encoding='utf8'))]
  files=sorted(folder.glob('sample-*.png'));assert rc==0 and observed==targets and len(files)==len(targets),(key,rc,observed,targets,len(files))
  samples=[{'path':rel(p),'pts':pt,'sourceFrame':pt//256,'seconds':pt/15360,'sha256':sha(p)} for p,pt in zip(files,targets)]
  boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
  for offset in range(0,len(samples),6):
   group=samples[offset:offset+6];board=Image.new('RGB',(1280,1176),'#181818');draw=ImageDraw.Draw(board)
   for j,row in enumerate(group):
    x=(j%2)*640;y=(j//2)*392
    with Image.open(ROOT/row['path']) as im:board.paste(im.resize((640,360)),(x,y))
    draw.text((x+8,y+365),f'{key} source f{row["sourceFrame"]} / PTS{row["pts"]} / {row["seconds"]:.3f}s',font=font,fill='white')
   bp=folder/f'board-{offset//6+1:03d}.png';board.save(bp);boards.append({'path':rel(bp),'sha256':sha(bp),'samples':[x['path'] for x in group]})
  out={'kind':key,'source':rel(source),'sourceSha256':sha(source),'actualFfmpegExitCode':rc,'sourceTimeBase':'1/15360','actualPtsMatch':True,'samples':samples,'boards':boards,'allSamplesDirectlyRead':False,'nativeWholeFramesApproval':False,'fullListeningApproved':False};write(folder/'manifest.json',out);st['outputs'].append(out);write(statepath,st)
 st['status']='completed-awaiting-direct-pixel-read';st['workerExitCode']=0;st['completedAt']=now();st.pop('currentJob',None);write(statepath,st);print(json.dumps({'samples':sum(len(x['samples']) for x in st['outputs']),'boards':sum(len(x['boards']) for x in st['outputs']),'workerExitCode':0}))
except BaseException as e:
 st['status']='failed';st['error']=repr(e);st['workerExitCode']=1;write(statepath,st);raise
