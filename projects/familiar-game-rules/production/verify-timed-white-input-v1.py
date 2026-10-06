"""Verify the completed silent input without granting final production approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, os
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
write=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
now=lambda:datetime.now(timezone.utc).isoformat()
resource=read(PROOF/'resource-observation-v32.json')
assert resource['ownHeavyJobs']==0
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['whiteEncoderAlive'] is False
output=ROOT/'shared/output/motion-canvas/familiar-game-rules-timed-white-v1.mp4'
plan=read(ROOT/'motion-canvas/src/projects/familiar-game-rules/timed-white-reel-plan-v1.json')
state_path=PROOF/'timed-white-input-render-execution-v1.json';state=read(state_path)
history={k:state.get(k) for k in ['pid','creationDate','commandLine','observedAt','status']}
ffmpeg=r'C:\ProgramData\HP\LCDDisplayHelper\bin\ffmpeg.exe'
ffprobe=r'C:\ProgramData\HP\LCDDisplayHelper\bin\ffprobe.exe'
state.update(status='verifying-completed-silent-input',alive=False,encoderTerminationObserved=True,
             guiRenderReturnedObserved=True,guiExitCodeObserved=False,verificationPid=os.getpid(),
             resourceObservation='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/resource-observation-v32.json')
write(state_path,state)
p=subprocess.run([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(output)],capture_output=True,text=True,check=True)
probe=json.loads(p.stdout);write(PROOF/'timed-white-input-probe-v1.json',probe)
v=next(x for x in probe['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'60/1',9140)
assert not any(x['codec_type']=='audio' for x in probe['streams'])
cmd=[ffmpeg,'-hide_banner','-v','error','-threads','2','-i',str(output),'-map','0:v:0','-an','-f','null','-']
with (PROOF/'timed-white-input-decode-v1.log').open('w',encoding='utf-8') as log:
    d=subprocess.run(cmd,stdout=log,stderr=log)
assert d.returncode==0
sha=hashlib.sha256(output.read_bytes()).hexdigest()
report=dict(schemaVersion=1,verifiedAt=now(),scope='silent-white-input-only',output=str(output.relative_to(ROOT)).replace('\\','/'),sha256=sha,bytes=output.stat().st_size,
            frames=9140,fps=60,seconds=9140/60,width=1920,height=1080,audioStreams=0,
            originalSixFrames=8835,extraIndependentGuideFrames=305,fullDecodeExitCode=d.returncode,
            probeExitCode=p.returncode,probeTimeBase=v['time_base'],guiRenderReturnedObserved=True,
            guiEncoderExitCodeObserved=False,encoderTerminationObserved=True,encoderHistory=history,
            independentRows=plan['rows'],allEncodedDiagramPixelsReviewed=False,
            allFinalCaptionPixelsReviewed=False,finalVideoApproved=False,newGitImages=0,newGitMedia=0)
write(PROOF/'timed-white-input-verification-v1.json',report)
state.update(status='silent-white-input-built-probed-decoded-pixels-pending',observedAt=now(),alive=False,
             verificationPid=None,sha256=sha,actualFrames=9140,fullDecodeExitCode=0,
             verification='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/timed-white-input-verification-v1.json')
write(state_path,state)
for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    j=read(path);j.update(updatedAt=now(),stage='encoded-white-and-source-word-motion-review-pending',timedWhiteInputRender=state,timedWhiteInputVerification=report,
                         nextAction='Review encoded white cue/animation pixels and source/caption words; resolve boss source internal cut. Final timing/mix/ASR/pair/QA/collection/private remain pending.');write(path,j)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath)
it=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
it.update(stage='encoded-white-and-source-word-motion-review-pending',timedWhiteInputRender=state,timedWhiteInputVerification=report);q['updatedAt']=now();write(qpath,q)
print(json.dumps(dict(frames=9140,sha256=sha,decodeExitCode=0,finalVideoApproved=False)))
