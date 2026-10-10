"""Preserve the failed environment attempt; verify research restoration first.

Only own preparation files are created. No process or pause file is changed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,psutil,py_compile
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(BASE/'narration-tts-execution-v1.json');session=read(BASE/'narration-tts-session-v1.json')
assert session['sessionId']==60672 and state['exitCode']==1 and not state['results']
assert 'ModuleNotFoundError' in state['error'] and 'soundfile' in state['error']
def alive(i):
    try:return abs(psutil.Process(i['pid']).create_time()-i['createTime'])<.01
    except psutil.NoSuchProcess:return False
history_path=ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json"
history=read(history_path)
assert history['ttsExitCode']==1 and history['state']=='research_resume_verified'
assert not alive(history['ttsOwner']) and not alive(history['coordinator'])
lease_path=ROOT/'shared/output/GPU_HANDOFF.json'
assert not lease_path.exists() or read(lease_path)['token']!=state['leaseToken']
original=history['queueOwner'];resumed=history['resumedQueue']
assert resumed['command']==original['command'] and Path(resumed['cwd']).resolve()==Path(original['cwd']).resolve()
assert alive(resumed)
p=psutil.Process(resumed['pid']);assert p.cmdline()==resumed['command'] and Path(p.cwd()).resolve()==Path(original['cwd']).resolve()
status=read(Path(history['queueDir'])/'status.json')
assert status['owner_pid']==resumed['pid'] and status['status'] in ['running','waiting_for_resources']
for path in history['ownedFiles']:
    f=Path(path);assert not f.exists() or read(f).get('token')!=state['leaseToken']
request=read(BASE/'narration-tts-request-v1.json')
assert not any((ROOT/s['path']).exists() for s in request['scenes'])
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
proof=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=60672,actualOuterExitCode=1,
    failure='Wrong interpreter lacked soundfile before any model or scene PCM was created.',
    currentPcmCreated=0,originalHistoryPath=history_path.relative_to(ROOT).as_posix(),originalHistorySha256=sha(history_path),
    originalToken=state['leaseToken'],ownedVoiceWorkerClosed=True,ownedCoordinatorClosed=True,
    exactOriginalResearchCommandAndCwdRestored=True,actualResumedResearchIdentity=resumed,currentStatus=status,
    allProtectedInputsMatched=True,processOrControlChangesByVerifier=0,voiceApproved=False)
proof_path=BASE/'failed-voice-research-restoration-v1.json';assert not proof_path.exists()
proof_path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
session.update(actualExitObserved=True,actualOuterExitCode=1,restorationProof=proof_path.relative_to(ROOT).as_posix())
(BASE/'narration-tts-session-v1.json').write_text(json.dumps(session,ensure_ascii=False,indent=2)+'\n','utf-8')
voice=BASE/'render-voice-v2.py';verifier=BASE/'verify-own-voice-research-resume-v2.py'
assert not voice.exists() and not verifier.exists()
code=(BASE/'render-voice-v1.py').read_text('utf-8')
for a,b in [('narration-tts-execution-v1','narration-tts-execution-v2'),('narration-tts-session-v1','narration-tts-session-v2'),('narration-tts-waiting-v1','narration-tts-waiting-v2')]:code=code.replace(a,b)
voice.write_text(code,'utf-8')
verify=(BASE/'verify-own-voice-research-resume-v1.py').read_text('utf-8')
for a,b in [('narration-tts-execution-v1','narration-tts-execution-v2'),('narration-tts-session-v1','narration-tts-session-v2'),('research-handoff-verification-v1','research-handoff-verification-v2')]:verify=verify.replace(a,b)
verifier.write_text(verify,'utf-8')
asr=BASE/'review-current-voice-v1.py';assert not asr.exists()
worker=(ROOT/'projects/presenting-game-scores/production/review-current-voice-v1.py').read_text('utf-8-sig')
worker=worker.replace('presenting-game-scores','character-parameters').replace('narration-tts-execution-v1','narration-tts-execution-v2').replace('research-handoff-verification-v1','research-handoff-verification-v2')
worker=worker.replace("len(tts['results']) == 10","len(tts['results']) == 12").replace("len(script['scenes']) == 10","len(script['scenes']) == 12").replace("for x in script['scenes']) == 30","for x in script['scenes']) == 37").replace("len(plan['contexts']) >= 10","len(plan['contexts']) >= 12").replace('current-ten-voice','current-twelve-voice')
asr.write_text(worker,'utf-8')
for f in [voice,verifier,asr]:py_compile.compile(str(f),doraise=True)
prepared=dict(preparedAt=datetime.now(timezone.utc).isoformat(),worker=asr.relative_to(ROOT).as_posix(),workerSha256=sha(asr),
    plannedWholeScenes=12,plannedMinimumIndependentCompleteContexts=12,expectedScriptIsRecognizerPrompt=False,cpuThreads=2,gpu=0,
    requiresObservedActualTtsExit=True,requiresOwnedResearchRestoration=True,requiresFreshResource=True,
    executed=False,modelLoaded=False,narrationApproved=False,finalMixedAsrApproved=False)
(BASE/'prepared-current-asr-v1.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Failed attempt preserved; exact original research command/cwd/current job verified. V2 TTS and CPU ASR prepared only.')
