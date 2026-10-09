from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;BASE=P/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=BASE/'voice-runtime-failure-restoration-v1.json';assert not proof.exists()
s=read(BASE/'narration-tts-execution-v1.json');assert s['exitCode']==1 and s['results']==[] and 'No module named' in s['error']
l=read(BASE/'narration-tts-session-v1.json');assert l['sessionId']==39486
def live(i):
 try:return abs(psutil.Process(i['pid']).create_time()-i['createTime'])<.01
 except psutil.NoSuchProcess:return False
assert not live(l['actualOuterIdentity']) and not live(dict(pid=s['actualPid'],createTime=s['createTime']))
hp=ROOT/'shared/output/gpu-handoff'/f"{s['leaseToken']}.json";h=read(hp)
assert h['state']=='research_resume_verified' and h['ttsExitCode']==1 and not live(h['coordinator'])
res=h['resumedQueue'];assert live(res) and res['command']==h['queueOwner']['command'] and Path(res['cwd']).resolve()==Path(h['queueOwner']['cwd']).resolve()
p=psutil.Process(res['pid']);assert p.cmdline()==res['command'] and Path(p.cwd()).resolve()==Path(res['cwd']).resolve()
status=read(Path(h['queueDir'])/'status.json');assert status['owner_pid']==res['pid'] and status['status'] in ['running','waiting_for_resources']
child=None
if status.get('child_pid') and psutil.pid_exists(status['child_pid']):
 c=psutil.Process(status['child_pid']);child=dict(pid=c.pid,createTime=c.create_time(),command=c.cmdline(),cwd=c.cwd())
lp=ROOT/'shared/output/GPU_HANDOFF.json';current=read(lp) if lp.exists() else None;assert not current or current['token']!=s['leaseToken']
for x in h['ownedFiles']:
 f=Path(x);assert not f.exists() or read(f).get('token')!=s['leaseToken']
save(proof,dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=39486,actualOuterExitCode=1,historyPath=hp.relative_to(ROOT).as_posix(),historySha256=sha(hp),restorationVerified=True,observedResumedIdentity=res,currentResearchStatus=status,observedChild=child,allOwnedControlsReleased=True,processOrControlChangesByVerifier=0,generatedVoiceItems=0,modelLoaded=False,cause='Research Python lacks soundfile; failure happened during dependency import before model/generation. Use existing qwen3-tts/.venv without package installation.',foreignLeasePreserved=current))
l.update(workerExpectedRunning=False,actualOuterExitCode=1,actualExitObservedAt=datetime.now(timezone.utc).isoformat());save(BASE/'narration-tts-session-v1.json',l)
s.update(actualExitObserved=True,actualOuterExitCode=1,researchResumeVerified=True,failureRestorationProof=proof.relative_to(ROOT).as_posix());save(BASE/'narration-tts-execution-v1.json',s)
src=P/'render-balatro60-revision-voice-v1.py';target=P/'render-balatro60-revision-voice-v2.py';assert not target.exists()
text=src.read_text('utf-8').replace('narration-tts-execution-v1.json','narration-tts-execution-v2.json').replace('narration-tts-session-v1.json','narration-tts-session-v2.json').replace('narration-tts-waiting-v1.json','narration-tts-waiting-v2.json').replace('voice-resource-before-v1.json','voice-resource-before-v2.json')
text=text.replace("request=read(REQUEST);", "import importlib.util\nassert Path(sys.prefix).resolve()==(ROOT/'qwen3-tts/.venv').resolve(),'Use the verified dedicated TTS environment before any GPU handoff'\nfor package in ['soundfile','torch','qwen_tts','psutil']:assert importlib.util.find_spec(package),package\nrequest=read(REQUEST);")
target.write_text(text,'utf-8')
src=P/'verify-revision-voice-research-resume-v1.py';target=P/'verify-revision-voice-research-resume-v2.py';assert not target.exists()
target.write_text(src.read_text('utf-8').replace('narration-tts-session-v1.json','narration-tts-session-v2.json').replace('narration-tts-execution-v1.json','narration-tts-execution-v2.json').replace('research-handoff-verification-v1.json','research-handoff-verification-v2.json'),'utf-8')
p=P/'review-revision-voice-v1.py';text=p.read_text('utf-8').replace('narration-tts-execution-v1.json','narration-tts-execution-v2.json').replace('research-handoff-verification-v1.json','research-handoff-verification-v2.json');p.write_text(text,'utf-8')
print('Actual failed outer1/zero voice and original research running inference verified; prepared v2 dedicated runtime, old execution preserved.')
