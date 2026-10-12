"""Encode only four local review inputs, with current unchanged mix/captions."""
from pathlib import Path
import importlib.util,json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
proposalPath=P/'part1-mobile-native-repair-proposal-v319.json';proposal=m.read(proposalPath)
OUT=R/'production/research/game-lighting-history/local/mobile-native-previews-v320'
SP=P/'part1-mobile-native-preview-execution-v320.json';assert not OUT.exists() and not SP.exists()
mixSettings=m.read(P/'part1-final-mix-settings-v310.json');mix=R/mixSettings['wav']
layout=m.read(P/'part1-caption-layout-v309.json');ass=R/layout['ass']['path']
assert m.sha(mix)==mixSettings['wavSha256'] and m.sha(ass)==layout['ass']['sha256']
resources=m.resources();OUT.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],proposalSha256=m.sha(proposalPath),resources=resources,cpuThreads=2,gpuJobs=0,allPixelsApproved=False,uploaded=False,newTts=0,newGitImages=0)
def checkpoint():
 j=m.read(R/'production/research/game-lighting-history/checkpoint.json');j['episode04Part1MobileNativePreviewV320']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],completedInputs=len(state['results']),approved=False)
 j['ownedActiveWork']=dict(type='four-mobile-native-review-inputs',execution=m.rel(SP),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Direct normal-speed four corrected input pixels') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Direct normal-speed four corrected input pixels')
 j['updatedAt']=m.stamp();m.save(R/'production/research/game-lighting-history/checkpoint.json',j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def label(text,name,x,y,size):
 p=OUT/(name+'.txt');p.write_text(text,'utf8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(p)}':expansion=none:x={x}:y={y}:fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
m.save(SP,state);checkpoint()
try:
 for ident,change in proposal['changes'].items():
  c=change['input'];source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256']
  slug=ident.split(':')[0];pieces=change['pieces'];base=change['baseFrame'];graph=[]
  graph.append(f'[0:v]fps=60,setpts=PTS-STARTPTS,split={len(pieces)}'+''.join(f'[s{k}]' for k in range(len(pieces)))) if len(pieces)>1 else graph.append('[0:v]fps=60,setpts=PTS-STARTPTS[s0]')
  for k,p in enumerate(pieces):
   x,y,w,h=p['cropRect'];a=p['inFrame']-base;b=p['outFrame']-base
   graph.append(f'[s{k}]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale=1920:900:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:black,setsar=1[v{k}]')
  if len(pieces)>1:graph.append(''.join(f'[v{k}]' for k in range(len(pieces)))+f'concat=n={len(pieces)}:v=1:a=0[whole]')
  else:graph.append('[v0]null[whole]')
  identityX=620 if slug.startswith('fortnite') else 32
  extra=[label(change['identity'],slug+'-identity',identityX,22,28),label(change['qualifier'],slug+'-conditions',identityX,64,24)]
  if slug=='fortnite-mobile-test':extra.append('drawbox=x=12:y=0:w=520:h=470:color=red:t=4')
  graph.append('[whole]'+','.join(extra)+f',trim=end_frame={c["frames"]},settb=1/90000,setpts=N*1500[out]')
  native=OUT/(slug+'.native.mp4')
  run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-ss',f'{base/60:.9f}','-i',source,'-filter_complex_threads','2','-filter_complex',';'.join(graph),'-map','[out]','-frames:v',str(c['frames']),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',native],slug+'-native')
  proof=m.verify_video(native,c['frames'],state,SP,OUT,slug+'-native')
  preview=OUT/(slug+'.captioned-preview.mp4');start=c['fromFrame']/60
  vf=f"setpts=PTS+{start}/TB,ass='{m.rel(ass)}',setpts=PTS-STARTPTS,setsar=1"
  run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',native,'-ss',f'{start:.9f}','-i',mix,'-filter_threads','2','-vf',vf,'-map','0:v:0','-map','1:a:0','-frames:v',str(c['frames']),'-t',f'{c["frames"]/60:.9f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1:90000','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',preview],slug+'-captioned-preview')
  run([m.FF,'-v','error','-threads','2','-i',preview,'-f','null','NUL'],slug+'-preview-decode')
  state['results'].append(dict(id=ident,native=dict(path=m.rel(native),sha256=m.sha(native)),preview=dict(path=m.rel(preview),sha256=m.sha(preview)),technical=proof,frames=c['frames'],sourcePieces=pieces,fullNormalSpeedDirectlyReviewed=False,allPixelsApproved=False));m.save(SP,state);checkpoint()
 state.update(status='complete-awaiting-direct-review',exitCode=0,active=None,completedAt=m.stamp());m.save(SP,state);checkpoint();print(json.dumps(dict(status=state['status'],inputs=len(state['results']),approved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
