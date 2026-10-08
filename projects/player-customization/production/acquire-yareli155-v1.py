"""Acquire one fresh already-observed official gameplay chapter, video only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, json, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/research/yareli-devstream155-v1'
STATE=BASE/'yareli155-acquisition-execution-v1.json';SESSION=STATE.with_name(STATE.stem+'.session.json')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();resource=read(ROOT/args.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert not STATE.exists() and not OUT.exists(),'Read actual checkpoint; never repeat acquisition.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True)
cmd=['D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-m','yt_dlp','--no-playlist','--write-info-json','--no-write-thumbnail','--no-overwrites','--retries','2','--fragment-retries','2','--socket-timeout','30','--js-runtimes','node:C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','--ffmpeg-location','C:/ProgramData/HP/LCDDisplayHelper/bin','-f','bv[height<=1080][ext=mp4][vcodec^=avc]/bv[height<=1080][ext=mp4]/bv[height<=1080]','--download-sections','*00:45:21-00:51:27','--downloader-args','ffmpeg:-threads 2','-o',str(OUT/'8eUfnQ8mWXs-yareli-2721-3087.%(ext)s'),'https://www.youtube.com/watch?v=8eUfnQ8mWXs']
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),status='acquiring-fresh-yareli-official-gameplay',resourceEvidence=args.resource,cpuThreads=2,gpu=0,singleJob=True,downloadCommandLine=cmd,sourceVideoId='8eUfnQ8mWXs',sourceOffsetSeconds=2721,requestedSeconds=366,publicPlayerObserved=True,rightsStatus='conditional-DE-policy-required-notice-preserved-human-public-rights-pending',operations=[],exitCode=None,sourceAudioUsed=False,rawMediaLocalOnly=True,nativeActionApproved=False,finalRatioApproved=False)
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
def checkpoint():
 if SESSION.exists():
  launch=read(SESSION)
  if launch['pid']==os.getpid():s.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
 s['updatedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),commandLine=s['commandLine'],sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),state=STATE.relative_to(ROOT).as_posix(),cpuThreads=2,gpu=0,singleJob=True,exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None,downloadPid=s.get('downloadPid'))
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),nextAction='After this single download exits, probe/decode and inspect exact native source pixels. Fresh source is not final allocation approval. Preserve all64 paragraphs and current voice/white assets.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction'],actionCapacityReview='projects/player-customization/planning/action-capacity-review-v3.json');q['updatedAt']=now();save(qp,q)
checkpoint()
with (OUT/'download.log').open('w',encoding='utf-8') as log:
 child=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);s['downloadPid']=child.pid;checkpoint();print(json.dumps({'pid':os.getpid(),'downloadPid':child.pid}),flush=True);code=child.wait()
s.update(exitCode=code,finishedAt=now(),status='fresh-yareli-download-complete-native-review-pending' if code==0 else 'fresh-yareli-download-failed',downloadedFiles=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size) for p in OUT.iterdir() if p.suffix.lower() in ['.mp4','.webm']]);checkpoint();print(json.dumps({'exitCode':code,'files':s['downloadedFiles']}),flush=True);raise SystemExit(code)
