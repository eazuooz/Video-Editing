"""Record bounded UI playback and preserve completed annotation work."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
proof_path=R/'extra-annotation-normal-playback-observation-v1.json'
assert not proof_path.exists()
proof=dict(schemaVersion=1,recordedAt=stamp,browserTab='96',url='http://127.0.0.1:9250/motion-extra-annotation-normal-review-v1.html',
 observedBy='CUA read-only video DOM and directly viewed start/end screenshots',
 observations=[dict(piece='PortalV2',start=.233281,end=15,duration=15,startedPaused=False,ended=True,rate=1,muted=True,source='motion-extra-portal-role-v2.mp4',endpoint='held cube at start; beam/portal room at end; uncertain markers hidden'),
 dict(piece='PowerWashV4',start=.255682,end=13.016667,duration=13.016667,startedPaused=False,ended=True,rate=1,muted=True,source='motion-extra-powerwash-role-v4.mp4',endpoint='red decorated tool-body anchor and cyan small-house cue readable; HUD and caption preview clear')],
 normalSpeedStartEndObserved=True,allIntermediateFramesHumanObserved=False,continuousListening=False,
 narrationTimedApproved=False,finalCaptionsApproved=False,finalVideoApproved=False,
 annotationInterpretation='Observed projected screen role points. Tool body is not nozzle tip, measured world axis, centroid or comfort evidence.')
proof_path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
prior=read(R/'resource-and-annotation-handoff-v16.json')
status_path=Path(prior['currentResearchStatusPath']);status=read(status_path)
assert status['status']=='complete_pending_visual_review' and status['completed']==status['total']==1088
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists()
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
assert len(protected)==71
for row in protected:assert sha(ROOT/row['path'])==row['sha256'],row['path']
for proc in psutil.process_iter(['pid','cmdline']):
 command=' '.join(proc.info['cmdline'] or [])
 assert not ('render-motion-extra-annotation-pieces-v' in command and 'python' in command.lower()),command
evidence=['extra-anchors-direct-review-v1.json','extra-annotation-pieces-sampled-direct-review-v2.json','extra-annotation-pieces-sampled-direct-review-v3.json','extra-annotation-pieces-sampled-direct-review-v4.json',proof_path.name]
next_step='Preserve current3PCM/repair/ASR and five timed comparisons+summary. Preserve PortalV2/PWashV4 silent annotation pieces: all84 source-aligned encoded samples reviewed and CUA normal1x start/end observed; V1 premedia failure and V2/V3 PWash misalignment remain held history. Tool-body label replaces unsupported nozzle-tip label. Derive paragraph/word-led unique actual before-action-result allocation from ten normal-speed native windows, then remaining narrated tracking,17mix/KOEN/chapters/end/currentmixedASR/allcuecutpixels/two decodes/four outputs/private settings/selectGit/current09replacement. Final/native allocation not yet approved. Pause after normal-transform-UV boundary; no six Sakurai starts.'
handoff=dict(prior,schemaVersion=1,recordedAt=stamp,previousHandoff='resource-and-annotation-handoff-v16.json',
 evidence=[dict(path=f,sha256=sha(R/f)) for f in evidence],activeOwnedWorkers=0,all71ProtectedHashesMatched=True,
 currentResearchStatus=status,currentResearchStatusSha256=sha(status_path),currentOriginalResearchAlive=False,
 extraPortalV2=dict(session=79352,completion='9db1a6',exitCode=0,frames=900,samples=31,boards=8),
 extraPowerWashV3Held=dict(session=96628,completion='3d276a',exitCode=0,samples=53,boards=14),
 extraPowerWashV4=dict(session=54367,completion='7dc1cb',exitCode=0,frames=781,samples=53,boards=14),
 boundedNormalSpeedPlaybackObserved=True,allNarrationTimedMovingPixelsApproved=False,next=next_step)
out=R/'resource-and-annotation-handoff-v17.json';assert not out.exists()
out.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=stamp,currentHandoff=out.name,stage='extra-annotations-sampled-and-normal-playback-reviewed-paragraph-native-allocation-pending',
 ownedJob=dict(status='completed',active=False,sessionId=54367,exitCode=0,completion='7dc1cb'),activeOwnedWorkers=0,
 extraAnnotationSampledReview=evidence[3],extraAnnotationNormalPlayback=proof_path.name,next=next_step)
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json';q=read(qp)
matches=[v for v in q.values() if isinstance(v,dict) and v.get('currentCheckpoint','').endswith('revision-cross-game-four-v1/latest-checkpoint.json')]
assert len(matches)==1
matches[0].update(currentHandoff=out.relative_to(ROOT).as_posix(),activeOwnedWorkers=0)
q.update(status='active',recordedAt=stamp,next=next_step)
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(handoff=out.name,protected=71,activeOwnedWorkers=0,finalVideoApproved=False)))
