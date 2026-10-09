"""Observe closed UI renderer then verify the new silent input, not final media."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
statep=BASE/'measured-black-render-execution-v8.json';s=read(statep)
try:
 p=psutil.Process(s['actualPid']);alive=abs(p.create_time()-s['createTime'])<.02 and p.is_running()
except psutil.NoSuchProcess:alive=False
assert not alive,'Do not decode a running renderer'
video=ROOT/s['output'];assert video.exists()
dest=BASE/'measured-black-input-verification-v8.json';assert not dest.exists()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
proc=psutil.Process();identity=dict(pid=proc.pid,createTime=proc.create_time(),command=proc.cmdline(),cwd=proc.cwd())
probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(video)],text=True));stream=probe['streams'][0]
assert len(probe['streams'])==1
assert (stream['width'],stream['height'],stream['r_frame_rate'],stream['time_base'])==(1920,1080,'60/1','1/90000')
assert int(stream['nb_frames']) in (7333,7334),stream['nb_frames']
frames=json.loads(subprocess.check_output([PROBE,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(video)],text=True))['frames']
assert [int(x['best_effort_timestamp']) for x in frames]==list(range(0,len(frames)*1500,1500))
run=subprocess.run([FF,'-v','error','-threads','2','-i',str(video),'-f','null','-'],capture_output=True,text=True)
log=video.with_suffix('.decode-v8.log');log.write_text(run.stderr,'utf-8');assert run.returncode==0,run.stderr
proof=dict(schemaVersion=8,verifiedAt=datetime.now(timezone.utc).isoformat(),videoPath=s['output'],videoSha256=sha(video),probe=probe,frames=len(frames),allFramePtsVerified=True,ptsStep=1500,timebase='1/90000',plannedSegmentFrames=7333,inclusiveTerminalExtraFrames=len(frames)-7333,wholeDecodeExitCode=run.returncode,decodeLog=log.relative_to(ROOT).as_posix(),processIdentity=identity,encoderIdentity=s,actualEncoderAlive=False,encoderExitCodeDirectlyObserved=None,uiAbortReturnedToRenderObserved=True,selectedInputCaptionPixelsReviewed=False,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,qa=False,collected=False,private=False,imagesGitAdded=0)
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
s.update(alive=False,status='closed-render-input-verified-pixel-review-pending',uiRenderCompletionObserved=True,outputSha256=sha(video),inputVerification=dest.relative_to(ROOT).as_posix(),actualExitObserved=False,exitCode=None,closedObservedAt=proof['verifiedAt'])
statep.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(frames=len(frames),plannedFrames=7333,decodeExitCode=run.returncode,exactPts=True,encoderExitDirectlyObserved=None)))
