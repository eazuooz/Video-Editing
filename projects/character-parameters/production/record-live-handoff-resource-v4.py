"""Read actual identities and protected inputs; never manipulate research."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(BASE/'narration-tts-execution-v2.json');assert state['exitCode'] is None
request=read(BASE/'narration-tts-request-v1.json')
protected=[]
for x in request['protectedInputs']:
 assert sha(ROOT/x['path'])==x['sha256'];protected.append(x)
history=read(ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json")
assert history['state']=='tts_running' and history['token']==state['leaseToken']
def identity(pid,expected=None):
 p=psutil.Process(pid)
 if expected is not None:assert abs(p.create_time()-expected)<.01
 return dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),exe=p.exe(),alive=p.is_running())
voice=identity(state['actualPid'],state['createTime']);coordinator=identity(history['coordinator']['pid'],history['coordinator']['createTime'])
servers=[identity(56464,1791583480.4185524),identity(27140),identity(63080)]
assert 'character-parameters.black-preflight-v1.config.ts' in ' '.join(servers[0]['commandLine'])
assert 'serve-native-review-v1.py' in ' '.join(servers[1]['commandLine'])
assert 'presenting-game-scores.black-preflight-v1.config.ts' in ' '.join(servers[2]['commandLine'])
active_ffmpeg=[p.info for p in psutil.process_iter(['pid','name','cmdline','create_time']) if (p.info.get('name') or '').lower()=='ffmpeg.exe' and 'character-parameters' in ' '.join(p.info.get('cmdline') or [])]
assert not active_ffmpeg
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,name,memory.used,utilization.gpu','--format=csv,noheader'],text=True).strip()
proof=dict(schemaVersion=4,observedAt=datetime.now(timezone.utc).isoformat(),voiceProcess=voice,coordinatorProcess=coordinator,sessionId=59763,leaseToken=state['leaseToken'],actualVoiceStage=state['stage'],completedCandidateChunks=len(state['results']),totalRequestedChunks=12,generationComplete=False,actualOuterExitCode=None,protectedInputs=protected,allTenProtectedInputsMatched=True,researchBoundaryEvidence=history['completedJobEvidence'],researchBoundaryStatus=history['boundaryStatus'],researchRestorationVerified=False,originalResearchCommand=history['queueOwner'],servers=servers,ownStructuralFfmpegJobs=active_ffmpeg,gpu=gpu,structuralPrototypeReview='projects/character-parameters/production/black-structural-direct-review-v3.json',prototypeStructuralPixelReviewApproved=True,measuredVoiceApproval=False,wholeAndContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsApproved=False,collected=False,uploaded=False,actualId=None,scheduled=False,imagesGitAdded=0,mediaGitAdded=0,processOrPauseControlsChangedByVerifier=0,nextAction='Read actual live TTS state/session. Wait for actual session59763 exit before verifying owned restoration and launching prepared CPU2 whole/current contexts ASR; never duplicate TTS.')
(BASE/'prepared-handoff-resource-verification-v4.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(voice=voice,stage=state['stage'],candidateChunks=len(state['results']),protectedInputs=10,prototypeApprovedOnly=True,actualOuterExit=None,researchResumeVerified=False),ensure_ascii=False))
