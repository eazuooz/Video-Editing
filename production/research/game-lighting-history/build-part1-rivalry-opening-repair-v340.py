"""Replace only two missing input frames with their original source frames; preserve PCM/time."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageStat,ImageDraw
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP);visual=m.read(P/'part1-final-visual-build-v332.json')
c=next(x for x in plan['cuts'] if x['id']=='rivalry-surface-observation:native');old=next(x for x in visual['cuts'] if x['id']==c['id'])
assert c['frames']==old['frames']==1006 and c['fromFrame']==old['fromFrame']==82995 and c['proposedCuts']==[{'inFrame':30,'outFrame':1036}]
source=ROOT/c['video']['path'];nativeOld=ROOT/old['path'];assert m.sha(source)==c['video']['sha256'] and m.sha(nativeOld)==old['sha256']
openingPath=P/'part1-rivalry-opening-board-v338b.json';opening=m.read(openingPath)
assert opening['source']['sha256']==m.sha(source) and opening['input']['sha256']==m.sha(nativeOld)
for x in opening['frames']:assert m.sha(ROOT/x['path'])==x['sha256']
assert m.sha(ROOT/opening['board']['path'])==opening['board']['sha256']
means={}
for x in opening['frames']:
 im=Image.open(ROOT/x['path']).convert('L');w,h=im.size
 means[(x['type'],x['frame'])]=ImageStat.Stat(im.crop((w//8,h//6,7*w//8,5*h//6))).mean[0]
assert means[('input',0)]<1 and means[('input',1)]<1 and all(means[('source',i)]>10 for i in [30,31,32]) and means[('input',2)]>10
proposal=dict(reviewedAt=m.stamp(),id=c['id'],frames=1006,fromFrame=82995,toFrame=84001,openingProof=dict(path=m.rel(openingPath),sha256=m.sha(openingPath)),allSixConstituentFramesDirectlyRead=True,
 actualObservation='Original source frames30/31/32 all depict the lit tiled corridor and floor reflections; retained input frames0/1 are black except identity label, input2 depicts the original corridor. This is an input defect, not an original fade. Replace input0/1 with original30/31; retain decoded input2–1005 and all fixed timing/audio/captions.',
 centralLuma=[dict(type=k[0],frame=k[1],mean=v) for k,v in means.items()],replacementOriginalFrames=[30,31],retainedInputFramesExclusive=[2,1006],newTts=0,newAudioMix=0,newGitImages=0,allFinalPixelsReviewed=False)
assert not (P/'part1-rivalry-opening-repair-proposal-v339.json').exists();m.save(P/'part1-rivalry-opening-repair-proposal-v339.json',proposal)
settings=m.read(P/'part1-final-mix-settings-v310.json');mix=ROOT/settings['wav'];layout=m.read(P/'part1-caption-layout-v309.json');ass=ROOT/layout['ass']['path']
assert m.sha(mix)==settings['wavSha256'] and m.sha(ass)==layout['ass']['sha256']
OUT=R/'local/part1-rivalry-opening-repair-v340';SP=P/'part1-rivalry-opening-repair-execution-v340.json'
assert not OUT.exists() and not SP.exists();resources=m.resources();OUT.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],resourceObservation=resources,cpuThreads=2,gpuJobs=0,newTts=0,newAudioMix=0,newGitImages=0,allPixelsReviewed=False,qaApproved=False,uploaded=False)
m.save(SP,state)
def checkpoint():
 cp=R/'checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp();j['episode04Part1RivalryOpeningV340']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],finalApproved=False)
 j['ownedActiveWork']=dict(type='two-original-frame-native-repair',execution=m.rel(SP),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Direct current input opening and full1006-frame interval, then update only reviewed input in final pair') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Direct corrected input then final-pair pixels')
 m.save(cp,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
try:
 text=OUT/'identity.txt';text.write_text(c['identityLabel'],'utf8')
 label=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(text)}':expansion=none:x=32:y=22:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
 vf=f'[0:v]trim=start_frame=30:end_frame=32,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,{label}[head];[1:v]trim=start_frame=2:end_frame=1006,setpts=PTS-STARTPTS,setsar=1[tail];[head][tail]concat=n=2:v=1:a=0,settb=1/90000,setpts=N*1500[v]'
 native=OUT/'rivalry-surface.native.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',source,'-threads','2','-i',nativeOld,'-filter_complex_threads','2','-filter_complex',vf,'-map','[v]','-frames:v','1006','-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',native],'two-original-frame-repair')
 technical=m.verify_video(native,1006,state,SP,OUT,'native')
 preview=OUT/'rivalry-surface.captioned-preview.mp4';start=c['fromFrame']/60
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',native,'-ss',f'{start:.9f}','-i',mix,'-filter_threads','2','-vf',f"setpts=PTS+{start}/TB,ass='{m.rel(ass)}',setpts=PTS-STARTPTS,setsar=1",'-map','0:v:0','-map','1:a:0','-frames:v','1006','-t',f'{1006/60:.9f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1:90000','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',preview],'captioned-preview')
 run([m.FF,'-v','error','-threads','2','-i',preview,'-f','null','NUL'],'preview-decode')
 run([m.FF,'-n','-v','error','-threads','2','-i',preview,'-vf',"select='eq(n,0)+eq(n,1)+eq(n,2)+eq(n,3)+eq(n,15)+eq(n,60)'",'-frames:v','6','-fps_mode','passthrough','-threads','2',OUT/'opening-%02d.png'],'opening-pixels')
 board=Image.new('RGB',(3840,1130*3),'#151515');d=ImageDraw.Draw(board);images=[]
 for k,frame in enumerate([0,1,2,3,15,60],1):
  p=OUT/f'opening-{k:02d}.png';im=Image.open(p).convert('RGB');assert im.size==(1920,1080)
  x=((k-1)%2)*1920;y=((k-1)//2)*1130;board.paste(im,(x,y+50));d.text((x+10,y+12),f'corrected opening frame {frame} / final {82995+frame}',fill='white');images.append(dict(path=m.rel(p),sha256=m.sha(p),localFrame=frame))
 bp=OUT/'opening-board.png';board.save(bp)
 state['results'].append(dict(id=c['id'],frames=1006,native=dict(path=m.rel(native),sha256=m.sha(native)),preview=dict(path=m.rel(preview),sha256=m.sha(preview)),technical=technical,sourcePieces=c['proposedCuts'],replacementOriginalFrames=[30,31],retainedInputFramesExclusive=[2,1006],images=images,board=dict(path=m.rel(bp),sha256=m.sha(bp)),allPixelsApproved=False))
 state.update(status='complete-awaiting-direct-review',exitCode=0,completedAt=m.stamp());m.save(SP,state);checkpoint();print(json.dumps(dict(status=state['status'],frames=1006,approved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
