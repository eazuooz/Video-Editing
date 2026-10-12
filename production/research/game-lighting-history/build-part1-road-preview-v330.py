"""One corrected source interval with exact retained current audio/captions."""
from pathlib import Path
import importlib.util, json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
proposalPath=P/'part1-road-native-repair-proposal-v329.json';proposal=m.read(proposalPath)
assert proposal['sourceReview']['fullCandidateActuallyPlayed'] and proposal['sourceReview']['playbackRate']==1
c=proposal['input'];source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256']
assert c['frames']==1037 and c['proposedCuts']==[{'inFrame':2160,'outFrame':3197}]
mixSettings=m.read(P/'part1-final-mix-settings-v310.json');mix=R/mixSettings['wav']
layout=m.read(P/'part1-caption-layout-v309.json');ass=R/layout['ass']['path']
assert m.sha(mix)==mixSettings['wavSha256'] and m.sha(ass)==layout['ass']['sha256']
OUT=R/'production/research/game-lighting-history/local/part1-road-preview-v330'
SP=P/'part1-road-preview-execution-v330.json';assert not OUT.exists() and not SP.exists()
resources=m.resources();OUT.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],
 proposalSha256=m.sha(proposalPath),resources=resources,cpuThreads=2,gpuJobs=0,newTts=0,newAudioMix=0,newGitImages=0,
 allPixelsApproved=False,qaApproved=False,uploaded=False)
def checkpoint():
 cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1RoadPreviewV330']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],approved=False)
 j['ownedActiveWork']=dict(type='one-road-source-preview',execution=m.rel(SP),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,
  next='Direct complete1037-frame corrected input/cue204, then source-only current pair') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Direct complete corrected input/cue204 before master assembly')
 m.save(cp,j)
def run(args,label):
 checkpoint();result=m.run(args,label,state,SP,OUT);checkpoint();return result
m.save(SP,state);checkpoint()
try:
 text=OUT/'identity.txt';text.write_text(c['identityLabel'],'utf8')
 x,y,w,h=c['cropRect'];native=OUT/'geometry-road-mask.native.mp4'
 label=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(text)}':expansion=none:x=32:y=22:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
 vf=f'crop={w}:{h}:{x}:{y},scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=60,setpts=PTS-STARTPTS,trim=end_frame=1037,settb=1/90000,setpts=N*1500,'+label
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-ss','36.000000000','-i',source,'-filter_threads','2','-vf',vf,'-map','0:v:0','-frames:v','1037','-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',native],'road-native')
 technical=m.verify_video(native,1037,state,SP,OUT,'road-native')
 preview=OUT/'geometry-road-mask.captioned-preview.mp4';start=c['fromFrame']/60
 vf=f"setpts=PTS+{start}/TB,ass='{m.rel(ass)}',setpts=PTS-STARTPTS,setsar=1"
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',native,'-ss',f'{start:.9f}','-i',mix,'-filter_threads','2','-vf',vf,'-map','0:v:0','-map','1:a:0','-frames:v','1037','-t',f'{1037/60:.9f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1:90000','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',preview],'road-captioned-preview')
 run([m.FF,'-v','error','-threads','2','-i',preview,'-f','null','NUL'],'road-preview-decode')
 state['results'].append(dict(id=c['id'],frames=1037,native=dict(path=m.rel(native),sha256=m.sha(native)),preview=dict(path=m.rel(preview),sha256=m.sha(preview)),
  sourcePieces=c['proposedCuts'],technical=technical,allPixelsApproved=False,normalSpeedInputPixelsApproved=False))
 state.update(status='complete-awaiting-direct-review',exitCode=0,active=None,completedAt=m.stamp());m.save(SP,state);checkpoint()
 print(json.dumps(dict(status=state['status'],frames=1037,approved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
