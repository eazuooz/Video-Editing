"""One official public-source acquisition followed by single CPU2 native review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess, sys, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[4]
PROOF=Path(__file__).resolve().parent
LOCAL=ROOT/'shared/output/character-parameters/preflight'
MEDIA=ROOT/'shared/assets/character-parameters/raw'
QA=LOCAL/'dungeons-coarse-v1'
STATE=PROOF/'dungeons-source-execution-v1.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
vid='a8nwpiCqyTQ'
recovery='--recovery-v2' in sys.argv
if recovery:
 STATE=PROOF/'dungeons-source-execution-v2.json'
 QA=LOCAL/'dungeons-coarse-v2'
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
if STATE.exists() or (MEDIA/f'{vid}.mp4').exists(): raise SystemExit('Existing source job/file; inspect rather than reacquire.')
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
QA.mkdir(parents=True,exist_ok=True)
prior=None
if recovery:
 prior_path=PROOF/'dungeons-source-execution-v1.json'
 prior=json.loads(prior_path.read_text(encoding='utf-8-sig'))
 assert prior['status']=='failed' and prior['children'][-1]['exitCode']==1
 initial_info=MEDIA/(vid+'.info.json')
 if initial_info.exists():shutil.copy2(initial_info,QA/'preserved-initial-failed.info.json')
state={'schemaVersion':1,'slug':'character-parameters','status':'initializing','startedAt':stamp(),
 'pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,
 'workingDirectory':str(ROOT),'sessionId':None,'cpuThreads':2,'gpuJobs':0,'children':[],
 'sourceUrl':f'https://www.youtube.com/watch?v={vid}','sourceVideoId':vid,
 'officialHomeUrl':'https://dungeonsofaether.com/','observedOfficialEmbed':f'https://www.youtube.com/embed/{vid}',
 'observedPublisher':'Aether Studios @RivalsofAetherOfficial','sourceAudioUse':False,
 'sourceAdoptionApproved':False,'directPixelReviewApproved':False,'newScriptTtsOrRender':False,'externalResearchChanges':0}
if recovery:
 state['recovery']={'priorExecution':str(prior_path.relative_to(ROOT)).replace('\\','/'),'priorOuterExitCode':1,
  'failureObserved':'HTTP403 while transferring unchunked VP9 source; no completed media obtained.',
  'changedMethod':'Use existing bundled Node JS runtime, avc/m4a selection and1MiB chunks from established acquisition workflow.',
  'priorPartialFilesPreserved':True,'repeatedCompletedAcquisition':False}
def save(status):
 state.update(status=status,updatedAt=stamp())
 sp=STATE.with_name(STATE.name+'.session.json')
 if sp.exists():
  s=json.loads(sp.read_text(encoding='utf-8-sig'))
  if s.get('pid')==os.getpid():state['sessionId']=s.get('sessionId')
 write(STATE,state)
def run(args,label,cwd=ROOT,output=None):
 lp=QA/(label+'.log')
 with lp.open('wb') as log:
  c=subprocess.Popen(args,cwd=cwd,stdout=subprocess.PIPE if output else log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
  rec={'pid':c.pid,'processCreateTime':psutil.Process(c.pid).create_time(),'commandLine':args,'workingDirectory':str(cwd),'label':label,'status':'running','log':str(lp.relative_to(ROOT)).replace('\\','/'),'startedAt':stamp()}
  state['children'].append(rec);save(label+'-running');data=c.communicate()[0]
  rec.update(status='exited',exitCode=c.returncode,endedAt=stamp());save(label+'-exited')
  if c.returncode:raise RuntimeError(f'{label} actual exit{c.returncode}')
  if output:output.write_bytes(data);return json.loads(data)
try:
 save('acquiring-official-public-source')
 run([sys.executable,'-X','utf8','-m','yt_dlp','--no-playlist','--no-overwrites','--write-info-json',
  '--http-chunk-size','1M','--retries','2','--fragment-retries','2','--socket-timeout','30','--js-runtimes','node:'+NODE,
  '--merge-output-format','mp4','--ffmpeg-location',str(Path(FF).parent),'-f','bv*[height<=1080][vcodec^=avc]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*[height<=1080]+ba',
  '-o',vid+'.%(ext)s',state['sourceUrl']],'official-download',cwd=MEDIA)
 p=MEDIA/(vid+'.mp4');ip=MEDIA/(vid+'.info.json');info=json.loads(ip.read_text(encoding='utf-8'))
 assert info['id']==vid and info['channel_id']=='UCjJe1z4OSKKav9MLVEvXWfA'
 assert p.is_file() and p.stat().st_size>0
 ign=ROOT/'.gitignore';before=ign.read_bytes();rule=f'/shared/assets/character-parameters/raw/{vid}.info.json'.encode()
 if rule not in before.splitlines():
  assert ign.read_bytes()==before
  with ign.open('ab') as f:
   if before and not before.endswith(b'\n'):f.write(b'\n')
   f.write(rule+b'\n')
 state['source']={'localPath':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size,
  'metadataLocalPath':str(ip.relative_to(ROOT)).replace('\\','/'),'metadataSha256':sha(ip),
  'title':info['title'],'channel':info['channel'],'channelId':info['channel_id'],'metadataUploadDate':info.get('upload_date'),'observedYouTubeLocalDate':'2023-04-01','adopted':False}
 meta=run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)],'probe',output=QA/'probe.json')
 video=next(v for v in meta['streams'] if v['codec_type']=='video')
 fd=run([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time,pkt_duration','-of','json',str(p)],'frame-pts',output=QA/'native-pts.json')
 frames=fd['frames'];pts=[int(f['best_effort_timestamp']) for f in frames]
 assert len(set(pts))==len(pts) and all(b>a for a,b in zip(pts,pts[1:]))
 run([FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-map','0:v:0','-an','-f','null','-'],'whole-decode')
 chosen=[];nt=0.0
 for i,f in enumerate(frames):
  tm=float(f['best_effort_timestamp_time'])
  if tm+1e-8>=nt:chosen.append({'nativeFrame':i,'pts':pts[i],'timeSeconds':tm});nt+=0.5
 if chosen[-1]['nativeFrame']!=len(frames)-1:chosen.append({'nativeFrame':len(frames)-1,'pts':pts[-1],'timeSeconds':float(frames[-1]['best_effort_timestamp_time'])})
 expr='+'.join(f"eq(pts,{s['pts']})" for s in chosen)
 run([FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-vf',"select='"+expr+"'",'-fps_mode','passthrough','-an','-threads','2',str(QA/'sample-%04d.png')],'coarse-extract')
 files=sorted(QA.glob('sample-*.png'));assert len(files)==len(chosen)
 for s,file in zip(chosen,files):s.update(path=str(file.relative_to(ROOT)).replace('\\','/'),sha256=sha(file))
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
 for off in range(0,len(files),6):
  board=Image.new('RGB',(1920,816),(24,24,24));draw=ImageDraw.Draw(board)
  for n,(file,s) in enumerate(zip(files[off:off+6],chosen[off:off+6])):
   x=(n%3)*640;y=(n//3)*408;im=Image.open(file).convert('RGB');im.thumbnail((640,360));board.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2))
   draw.text((x+6,y+3),vid+' #'+str(s['nativeFrame']),font=font,fill='white');draw.text((x+6,y+384),'PTS '+str(s['pts'])+'  t '+format(s['timeSeconds'],'.6f'),font=font,fill=(180,230,230))
  bp=QA/f'board-{off//6+1:03d}.jpg';board.save(bp,quality=92);boards.append({'path':str(bp.relative_to(ROOT)).replace('\\','/'),'sha256':sha(bp),'sampleRange':[off,min(off+6,len(files))]})
 state.update(video={k:video.get(k) for k in ('width','height','r_frame_rate','time_base','duration','nb_frames')},decodedFrames=len(frames),wholeDecodeExitCode=0,nativePtsMonotonic=True,samples=chosen,boards=boards,totalSamples=len(chosen),totalBoards=len(boards))
 save('coarse-extracted-awaiting-direct-review')
 print(json.dumps({k:state[k] for k in ('status','video','totalSamples','totalBoards')},ensure_ascii=False),flush=True)
except BaseException:
 state['error']=traceback.format_exc();save('failed');print(state['error'],flush=True);sys.exit(1)
