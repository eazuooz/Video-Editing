"""One serial CPU job for an observed official 2024 developer play chapter."""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path('D:/Github/Video-Editing')
LOCAL=ROOT/'shared/output/player-customization/research/dante-demo-v1'
STATE=ROOT/'projects/player-customization/production/dante-demo-execution-v1.json'
FFMPEG='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FFPROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
source=LOCAL/'vy_vtGx8vq8-dante-2530-3155.mp4'
if STATE.exists() or source.exists():raise SystemExit('Existing job checkpoint: inspect it, do not repeat.')
resource=json.loads((ROOT/'shared/output/player-customization/research/resources-before-dante-v1.json').read_text('utf-8-sig'))
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
contexts=json.loads((ROOT/'projects/player-customization/production/current-contexts-asr-execution-v1.json').read_text('utf-8-sig'))
assert contexts['actualExitObserved'] and contexts['exitCode']==0
LOCAL.mkdir(parents=True,exist_ok=True)
if os.name=='nt':
 import ctypes
 ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
now=lambda:datetime.now(timezone.utc).isoformat()
state=dict(schemaVersion=1,status='running',startedAt=now(),wrapperPid=os.getpid(),
 commandLine=[sys.executable,*sys.argv],sourceUrl='https://www.youtube.com/watch?v=vy_vtGx8vq8',
 requestedSourceRangeSeconds=[2530,3155],officialOwner='PlayWarframe / @Warframe',sourceDate='2024-02-24 Korean YouTube UI',
 chapter='Dante Gameplay',variant='2024 work-in-progress developer demonstration; not current 2026 build guarantees',
 beforeNarrationObservation='CUA42:13/42:35 cast and44:49 Final Verse observed. Presenter lower left; no intervening continuous approval or final crop approval.',
 pageEvidence='shared/output/player-customization/preflight/devstream-177-finalverse-initial.ax.txt',
 resourceEvidence='shared/output/player-customization/research/resources-before-dante-v1.json',
 singleJob=True,cpuThreads=2,gpu=0,sourceAudioUsed=False,allMediaLocalOnly=True,operations=[],
 directPixelsReviewed=False,continuousActionsReviewed=False,footageQuotaApproved=False,narrationWritten=False,ttsStarted=False)
def atomic(path,data):
 temp=path.with_name(path.name+f'.{os.getpid()}.writing')
 temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
 import time
 for retry in range(40):
  try:os.replace(temp,path);return
  except OSError:
   if retry==39:raise
   time.sleep(.15)
def save():
 atomic(STATE,state)
 session_path=STATE.with_name(STATE.stem+'.session.json')
 launch=json.loads(session_path.read_text('utf-8-sig')) if session_path.exists() else {}
 job=dict(status=state['status'],pid=os.getpid(),commandLine=state['commandLine'],
  sessionId=launch.get('sessionId'),processIdentity=launch.get('processIdentity'),
  state=STATE.relative_to(ROOT).as_posix(),logDirectory=LOCAL.relative_to(ROOT).as_posix(),
  startedAt=state['startedAt'],cpuThreads=2,gpu=0,singleJob=True,
  operations=state['operations'],exitCode=state.get('exitCode'),next='All native boards and exact continuous presenter-free crop/action/caption review before observation-guide narration.')
 cp_path=ROOT/'projects/player-customization/production/latest-checkpoint.json'
 cp=json.loads(cp_path.read_text('utf-8-sig'))
 cp.update(recordedAt=now(),stage='official-dante-native-acquisition-and-inspection',ownedJob=job,nextAction=job['next'])
 atomic(cp_path,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 q=json.loads(qp.read_text('utf-8-sig'));item=next(x for x in q['items'] if x['slug']=='player-customization')
 item.update(stage=cp['stage'],currentExecution=job,nextAction=job['next'])
 q['updatedAt']=now();q['lastProgressAt']=now();atomic(qp,q)
def run(name,command):
 op=dict(name=name,commandLine=command,startedAt=now());state['operations'].append(op);save()
 with (LOCAL/(name+'.log')).open('w',encoding='utf-8') as log:
  child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);op['pid']=child.pid;save();code=child.wait()
 op.update(exitCode=code,finishedAt=now());save()
 if code:raise RuntimeError(name+' failed; inspect local log')
save()
try:
 gate=subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','player-customization','--check'],cwd=ROOT)
 if gate.returncode:raise RuntimeError('Current duplicate gate changed')
 run('download',['D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-m','yt_dlp',
  '--no-playlist','--write-info-json','--no-write-thumbnail','--no-overwrites','--retries','2','--fragment-retries','2','--socket-timeout','30',
  '--js-runtimes','node:C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
  '--ffmpeg-location','C:/ProgramData/HP/LCDDisplayHelper/bin','-f','bv[height<=1080][ext=mp4][vcodec^=avc]/bv[height<=1080][ext=mp4]/bv[height<=1080]',
  '--download-sections','*00:42:10-00:52:35','--downloader-args','ffmpeg:-threads 2','-o',str(LOCAL/'vy_vtGx8vq8-dante-2530-3155.%(ext)s'),state['sourceUrl']])
 with source.open('rb') as f:state['sourceSha256']=hashlib.file_digest(f,'sha256').hexdigest()
 state['sourceBytes']=source.stat().st_size
 result=subprocess.run([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(source)],capture_output=True,text=True,encoding='utf-8')
 if result.returncode:raise RuntimeError('probe failed')
 (LOCAL/'probe.json').write_text(result.stdout,encoding='utf-8');probe=json.loads(result.stdout)
 if any(s['codec_type']=='audio' for s in probe['streams']):raise RuntimeError('Unexpected audio')
 state['nativeProbe']=[{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate','time_base','start_time','duration','nb_frames']} for s in probe['streams']];save()
 run('whole-decode',[FFMPEG,'-nostdin','-v','error','-threads','2','-i',str(source),'-an','-f','null','-'])
 native=LOCAL/'native';native.mkdir(exist_ok=True)
 run('sample-5sec',[FFMPEG,'-nostdin','-v','error','-threads','2','-i',str(source),'-vf','fps=1/5','-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
 boards=LOCAL/'boards';boards.mkdir(exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);samples=sorted(native.glob('*.png'));rows=[]
 for first in range(0,len(samples),4):
  board=Image.new('RGB',(1920,1170),'white');draw=ImageDraw.Draw(board);entries=[]
  for j,path in enumerate(samples[first:first+4]):
   image=Image.open(path).convert('RGB');image.thumbnail((960,540));x=(j%2)*960;y=(j//2)*585;board.paste(image,(x,y+45))
   index=int(path.stem.split('-')[-1]);local=(index-1)*5;draw.text((x+12,y+8),f'{path.name} | nominal local {local}s / source {2530+local}s',font=font,fill='black')
   entries.append(dict(path=str(path.relative_to(ROOT)),nominalLocalSeconds=local,nominalSourceSeconds=2530+local))
  path=boards/f'board-{len(rows)+1:02d}.png';board.save(path);rows.append(dict(path=str(path.relative_to(ROOT)),entries=entries))
 state.update(status='native-decoded-samples-ready-direct-review-pending',finishedAt=now(),exitCode=0,nativeSampleCount=len(samples),boardCount=len(rows),boards=rows,
  next='Directly read all native boards; choose active ability/combat actions, exclude idles/menus/presenter/branding, then review exact continuous crop/caption boundaries.')
 save();print(json.dumps({k:state[k] for k in ['status','wrapperPid','sourceSha256','nativeSampleCount','boardCount','exitCode']},ensure_ascii=False),flush=True)
except Exception as error:
 state.update(status='failed',finishedAt=now(),exitCode=1,error=str(error));save();raise
