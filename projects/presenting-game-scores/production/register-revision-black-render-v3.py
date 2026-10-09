"""Record the actual UI-started encoder; never start another renderer."""
from pathlib import Path
from datetime import datetime,timezone
import json,psutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2'
name='presenting-game-scores-balatro60-black-v3.mp4'
rows=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','name','ppid']):
 try:
  cmd=proc.info['cmdline'] or []
  if (proc.info['name'] or '').lower()=='ffmpeg.exe' and any(name in x for x in cmd):rows.append(proc)
 except(psutil.AccessDenied,psutil.NoSuchProcess):pass
assert len(rows)==1
proc=rows[0];cmd=proc.cmdline();assert proc.ppid()==63080 and '-threads' in cmd and cmd[cmd.index('-threads')+1]=='2'
r=json.loads((B/'resources-before-black-render-v3.json').read_text('utf-8-sig'))
assert r['ownHeavyJobs']==0 and (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
dest=B/'measured-black-render-execution-v3.json';assert not dest.exists()
output=Path(cmd[-1]);assert output.name==name
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId = {proc.pid}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace')
j=dict(schemaVersion=3,observedAt=datetime.now(timezone.utc).isoformat(),slug='presenting-game-scores',stage='revision-measured-black-input-render-running',
 actualPid=proc.pid,createTime=proc.create_time(),command=cmd,cwd=proc.cwd(),parentPid=proc.ppid(),cimIdentity=json.loads(cim),
 viteSessionId=31622,encoderSessionId=None,encoderStartedThroughCua=True,uiTabId='136',uiRenderProject='presenting-game-scores-balatro60-black-v3',
 uiPlannedDurationFrames=7707,uiRenderFps=60,width=1920,height=1080,cpuThreads=2,filterThreads=1,ffmpegHardwareEncoder=False,
 exitCode=None,exitDirectlyObserved=False,alive=True,output=output.relative_to(ROOT).as_posix(),
 resourceProof=(B/'resources-before-black-render-v3.json').relative_to(ROOT).as_posix(),preparation=(B/'measured-mc-preparation-v3.json').relative_to(ROOT).as_posix(),
 baselineMeasuredSourcesAndRendersPreserved=True,serverRestarted=False,actualCuaRenderAction='RENDER became ABORT with elapsed/ETA',
 finalTimingApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,qaApproved=False,collected=False,private=False)
dest.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=json.loads((P/'latest-checkpoint.json').read_text('utf-8-sig'));cp.update(stage=j['stage'],recordedAt=j['observedAt'],
 revisionBlackRender=dest.relative_to(ROOT).as_posix(),activeRevisionJob=j,allInputSegmentCaptionPixelsReviewed=False)
cp['revisionCheckpoints'].update(voice=True,voiceAsr=True,measuredTiming=False,gameMixRatio=False,bodyRatio=False)
(P/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=json.loads(qp.read_text('utf-8-sig'));item=next(x for x in q['items']if x['slug']=='presenting-game-scores')
item.update(stage=j['stage'],currentExecution=j,nextAction='Verify new black render7707 planned frames/PTS/decode after actual encoder ends. Then all current31input cue/cut/spatial/credit pixels; final mix/pair/QA/private remain false.')
q['updatedAt']=j['observedAt'];qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualPid=proc.pid,createTime=proc.create_time(),alive=True,output=j['output'],cpuThreads=2)))
