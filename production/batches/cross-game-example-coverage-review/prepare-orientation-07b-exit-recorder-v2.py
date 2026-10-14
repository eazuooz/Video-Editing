"""Preserve V1 failure and check process identity rather than PID presence alone."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
out=B/'record-orientation-07b-worker-exit-v2.py';assert not out.exists()
s=(B/'record-orientation-07b-worker-exit-v1.py').read_text('utf-8')
s=s.replace("assert not psutil.pid_exists(s['pid'])", "identities=[]\ndef exact_dead(pid,created):\n try:\n  live=psutil.Process(pid);current=live.create_time();assert abs(current-created)>.001, f'Exact process still alive: {pid}'\n  identities.append(dict(pid=pid,oldCreateTime=created,currentCreateTime=current,currentCommand=live.cmdline(),exactIdentityAlive=False,pidReused=True))\n except psutil.NoSuchProcess:\n  identities.append(dict(pid=pid,oldCreateTime=created,exactIdentityAlive=False,pidAbsent=True))\nexact_dead(s['pid'],s['createTime'])")
s=s.replace("assert not psutil.pid_exists(s['encodePid'])", "exact_dead(s['encodePid'],s['encodeCreateTime'])")
s=s.replace("for x in s['decoders']:assert not psutil.pid_exists(x['pid'])", "for x in s['decoders']:exact_dead(x['pid'],x['createTime'])")
s=s.replace("assert not psutil.pid_exists(s['ffmpegPid'])", "exact_dead(s['ffmpegPid'],s['ffmpegCreateTime'])")
s=s.replace("workerDead=True,protectedShaMatched=True", "workerDead=True,exactProcessIdentityObservations=identities,exitRecorderVersion=2,priorRecorderFailure=dict(chunk='5724cd',actualExitCode=1,reason='V1 PID-only child absence assertion; no output or protected file mutation'),protectedShaMatched=True")
compile(s,str(out),'exec');out.write_text(s,'utf-8');print('07b exact-identity exit recorder V2 prepared.')
