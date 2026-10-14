from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
state=read(R/'alyx-annotation-pilot-execution-v1.json')
assert state['exitCode']==0 and all(state[k]==0 for k in ['actualDecodeExitCode','actualEncodeExitCode','wholeDecodeExitCode','extractionExitCode'])
assert not psutil.pid_exists(state['pid'])
assert sha(ROOT/state['path'])==state['sha256']
for s in state['samples']:assert sha(ROOT/s['path'])==s['sha256']
waiting=read(R/'narration-tts-waiting-v4.json')
for s in waiting['protectedInputs']:assert sha(ROOT/s['path'])==s['sha256'],s['path']
req=read(R/'narration-tts-request-v1.json');assert not any((ROOT/s['path']).exists() for s in req['scenes'])
now=datetime.now(timezone.utc).isoformat()
proof=dict(schemaVersion=1,reviewedAt=now,actualShellChunk='020843',actualShellExitCode=0,actualSessionId=None,
    actualWorkerPid=state['pid'],actualWorkerCreateTime=state['createTime'],actualWorkerAbsent=True,
    frames=state['frames'],seconds=state['seconds'],wholeDecodeExitCode=0,all11SampleSha256Matched=True,
    directPixelReview=dict(sampleCount=11,samples=state['samples'],observations=[
    'Samples01–06: red oval encloses both visible yellow destination feet; destination UI and oval remain above fixed caption. Source credit and role label readable.',
    'Sample07: destination is still visible but all added markers hidden within the uncertain transition bracket. Sample08: original black transition has no added geometric marker.',
    'Samples09–11: cyan leader points to visible wall beside the door. No destination oval persists after viewpoint change; no trajectory is interpolated across the transition.',
    'All11 sampled fixed captions remain readable at960970. The 180px upward source framing preserves visible role objects in these samples.']),
    playback=dict(tabId='87',url='http://127.0.0.1:9250/motion-alyx-annotation-pilot-v1.html',
    domPath='alyx-pilot-playback-v1.dom.txt',domSha256=sha(R/'alyx-pilot-playback-v1.dom.txt'),
    initialTime=0,runningTime=.003688,runningPaused=False,endTime=.716667,ended=True,paused=True,rate=1,muted=True,endpointScreenshotDirectlyRead=True),
    selectedMovingSampleGeometryApproved=True,normalSpeedStartEndVerified=True,
    allIntermediateFramesDirectlyRead=False,wholeContinuousPlaybackDirectReviewApproved=False,
    nativeMapping='nativeFrameEstimate is a timing estimate; exact encoded sample PTS is frame*1500. Do not claim exact original native mapping for every encoded frame.',
    narrationTimed=False,allFinalCuesApproved=False,finalVideoApproved=False,sourceAudioAdopted=False,gitImagesAdded=0)
p=R/'alyx-annotation-pilot-direct-review-v1.json';assert not p.exists();save(p,proof)
state.update(actualExitObserved=True,actualShellChunk='020843',actualShellExitCode=0,status='bounded-moving-samples-and-normal-speed-endpoints-reviewed',directReview=p.name)
save(R/'alyx-annotation-pilot-execution-v1.json',state)
rows=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','name']):
    try:
        cmd=' '.join(proc.info['cmdline'] or [])
        if proc.info['name'] and proc.info['name'].lower() in ['python.exe','ffmpeg.exe']:
            rows.append(dict(pid=proc.pid,createTime=proc.info['create_time'],command=proc.info['cmdline'],cwd=proc.cwd()))
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
lp=ROOT/'shared/output/GPU_HANDOFF.json'
resource=dict(observedAt=now,cpuPercent=psutil.cpu_percent(interval=1),freeRamKiB=psutil.virtual_memory().available//1024,
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip(),
    pythonAndFfmpeg=rows,currentLease=read(lp) if lp.exists() else None,
    currentResearchStatus=read(Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')),
    processOrResearchControlMutations=0,all68ProtectedInputsMatched=True,newPcmCount=0)
rp=R/'resource-and-annotation-handoff-v5.json';assert not rp.exists();save(rp,resource)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='bounded-portal-and-alyx-moving-pilots-reviewed-awaiting-safe-voice-resource',
    failedOwnedSession=66238,alyxPilotReview=p.name,alyxStaticReview='alyx-annotation-static-direct-review-v2.json',
    currentHandoff=rp.name,preparedVoiceVersion=5,preparedVoiceRequestStarted=False,
    currentOwnedVoiceWorkerAlive=False,currentOwnedGpuJobs=0,newPcmCount=0,
    next='Preserve completed PortalV2/AlyxV1 pilot and source reviews. ResourceV6 stable GPU idle false: V5 voice request/ASRv4 prepared only. Before next single new request, verify current foreign handoff/restoration and stable GPU resources, refresh current duplicate full-content/Studio review if changed. Measure actual3PCM and directly compare ASR before final timing/mix. Keep Oct12 baseline schedule until reviewed replacement.')
save(R/'latest-checkpoint.json',cp)
qp=Path(__file__).parent/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
q['currentMotionReview'].update(status=cp['stage'],alyxPilotReview=p.relative_to(ROOT).as_posix(),currentHandoff=rp.relative_to(ROOT).as_posix(),next=cp['next'])
assert qp.read_text('utf-8-sig')==raw;save(qp,q)
print(json.dumps({k:resource[k] for k in ['gpu','cpuPercent','freeRamKiB','newPcmCount']},ensure_ascii=False))
print('Sealed11pixels/43f/silent/bounded playback; protected68 retained; final approval false.')
