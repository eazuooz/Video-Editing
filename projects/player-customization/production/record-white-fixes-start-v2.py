from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
cmd="Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'player-customization-white-fixes-v2.mp4' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
identity=json.loads(subprocess.check_output(['pwsh','-NoProfile','-Command',cmd],encoding='utf-8-sig'));assert identity['ParentProcessId']==52892
now=datetime.now(timezone.utc).isoformat()
job={'status':'running-scoped01-05-white-fixes-render','pid':identity['ProcessId'],'processIdentity':identity,'commandLine':identity['CommandLine'],
 'sessionId':37374,'sessionIsViteProxy':True,'cpuThreads':2,'gpu':0,'singleJob':True,'state':'projects/player-customization/production/white-fixes-render-execution-v2.json',
 'resourceEvidence':'shared/output/player-customization/research/resources-before-white-fixes-render-v2.json',
 'plannedFrames':3001,'renderExitCode':None,'encoderExitCodeObserved':False,'previewEndFrame3001Observed':True,
 'next':'Verify actual returned CUA render, exact3001 display-order frames/PTS/decode, and directly read24 narration-timed samples of only the two fixes.'}
save(BASE/'white-fixes-render-execution-v2.json',dict(schemaVersion=1,slug='player-customization',startedAt=now,**job))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now,stage=job['status'],ownedJob=job,nextAction=job['next']);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,nextAction=job['next']);q['updatedAt']=now;save(qp,q)
print(json.dumps({'encoder':identity['ProcessId'],'proxy':37374,'plannedFrames':3001}))
