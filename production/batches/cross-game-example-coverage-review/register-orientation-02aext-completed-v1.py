"""Preserve late live-registration failure; register observed completed session."""
from pathlib import Path
from datetime import datetime,timezone
import json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
s=json.loads((O/'02aext-tracked-render-execution-v1.json').read_text('utf-8-sig'))
observed=[]
for pid,created in [(s['pid'],s['createTime']),(s['decodePid'],s['decodeCreateTime']),(s['encodePid'],s['encodeCreateTime'])]:
 try:
  p=psutil.Process(pid);assert abs(p.create_time()-created)>.001;observed.append(dict(pid=pid,oldCreateTime=created,currentCreateTime=p.create_time(),exactIdentityAlive=False,pidReused=True))
 except psutil.NoSuchProcess:observed.append(dict(pid=pid,oldCreateTime=created,exactIdentityAlive=False,pidAbsent=True))
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process | Where-Object {{$_.ProcessId -in @({s['pid']},{s['decodePid']},{s['encodePid']})}} | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json"],text=True,encoding='utf-8',errors='replace')
p=O/'02aext-tracked-render-execution-v1.session.json';assert not p.exists()
p.write_text(json.dumps(dict(registeredAt=datetime.now(timezone.utc).isoformat(),actualSession=58002,initialChunk='e1d11b',completion='4e165f',actualOuterExitCode=0,registeredAfterCompletion=True,liveRegistrationFailed=dict(chunk='77d95e',exitCode=1,reason='Worker52100 already ended before live registration; no write or relaunch occurred.'),pid=s['pid'],createTime=s['createTime'],command=s['commandLine'],cwd=s['cwd'],exactIdentityObservations=observed,cimActual=cim),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualSession=58002,outerExit=0,exactWorkerDead=True,lateLiveFailurePreserved=True)))
