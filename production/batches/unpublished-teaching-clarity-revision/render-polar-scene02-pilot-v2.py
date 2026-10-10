"""One owned CPU pilot: actual moving annotation, original audio/caption timing.

This is one revised gameplay scene only, never approval of the whole video.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, json, subprocess, importlib.util, re
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_NUM_THREADS']='2'
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/scene02-moving-pilot-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
spec=importlib.util.spec_from_file_location('polar_annotation',Path(__file__).with_name('prepare-polar-scene02-annotations-v3.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=module.sha;rel=module.rel
def main():
 LOCAL.mkdir(parents=True,exist_ok=True)
 statefile=OUT/'scene02-moving-pilot-execution-v2.json';assert not statefile.exists()
 planfile=OUT/'scene02-editorial-annotations-v3.json';plan=json.loads(planfile.read_text(encoding='utf-8'))
 source=ROOT/plan['source'];assert sha(source)==plan['sourceSha256']
 snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8'))
 assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
 state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','stage':'annotated-clean-pilot','sourceSha256':sha(source),'planSha256':sha(planfile),'globalStartFrame':1669,'frames':3403,'narrationChanged':False,'baselineMutations':0,'currentMovingPixelReviewApproved':False,'wholeVideoApproved':False}
 def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 def run(cmd,name):
  state['currentCommand']=cmd;save()
  with (LOCAL/name).open('wb') as log:result=subprocess.run(cmd,stdout=log,stderr=log,check=True,cwd=ROOT)
  return result.returncode
 save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime']}),flush=True)
 clean=LOCAL/'scene02.annotated.clean.mp4';captioned=LOCAL/'scene02.annotated.captioned.mp4'
 assert not clean.exists() and not captioned.exists()
 try:
  dec=[FF,'-hide_banner','-nostdin','-loglevel','error','-threads','1','-filter_threads','1','-i',str(source),'-f','rawvideo','-pix_fmt','rgb24','pipe:1']
  enc=[FF,'-hide_banner','-nostdin','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','3403','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(clean)]
  state.update(decodeCommand=dec,encodeCommand=enc);save()
  with (LOCAL/'source-decode.log').open('wb') as dl,(LOCAL/'annotated-encode.log').open('wb') as el:
   decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl)
   encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el)
   for frame in range(3403):
    raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,(frame,len(raw))
    im=Image.frombytes('RGB',(1920,1080),raw)
    encoder.stdin.write(module.annotate(im,frame,plan).tobytes())
    if frame%600==0:
     state['writtenFrames']=frame+1;save();print(json.dumps({'writtenFrames':frame+1}),flush=True)
   assert decoder.stdout.read(1)==b''
   encoder.stdin.close();decoder.stdout.close()
   dx=decoder.wait();ex=encoder.wait();assert dx==ex==0,(dx,ex)
  state.update(writtenFrames=3403,sourceReframe=plan['sourceReframe'],sourceDecodeExitCode=dx,annotationEncodeExitCode=ex,stage='original-audio-and-fixed-caption-pilot');save()
  baseline=ROOT/'shared/output/motion-canvas/game-math-polar-3d.mp4'
  vf='setpts=PTS+1669/60/TB,ass=projects/game-math-polar-3d/script/final.ko.ass,setpts=PTS-STARTPTS'
  cmd=[FF,'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-filter_complex_threads','1','-i',str(clean),'-i',str(baseline),'-filter_complex','[1:a]atrim=start=27.8166666666667:end=84.5333333333333,asetpts=PTS-STARTPTS[a]','-map','0:v','-map','[a]','-vf',vf,'-frames:v','3403','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',str(captioned)]
  state['captionEncodeExitCode']=run(cmd,'caption-encode.log')
  state['pilotAudioNote']='Decoded interval from the original final AAC, re-encoded only for this playback pilot. Final whole-video delivery must preserve and verify the original whole AAC.'
  state['stage']='pilot-technical-check-and-pixel-extraction';save()
  for p in [clean,captioned]:
   code=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(p),'-f','null','-'],p.stem+'-whole-decode.log')
   data=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(p)]))
   assert [int(f['pts']) for f in data['frames']]==list(range(0,3403*1500,1500))
   state[p.stem]={'path':rel(p),'sha256':sha(p),'wholeDecodeExitCode':code,'frames':3403,'allPts1500Verified':True}
   save()
  points=set(range(0,3403,15))|{0,659,660,2086,2087,2776,2777,3402}
  # Include every caption transition +/-1 frame and every annotation stage.
  def secs(value):
   a,b,c=value.split(':');return int(a)*3600+int(b)*60+float(c)
  for line in (ROOT/'projects/game-math-polar-3d/script/final.ko.ass').read_text(encoding='utf-8').splitlines():
   if not line.startswith('Dialogue:'):continue
   fields=line.split(',',9)
   for stamp in fields[1:3]:
    f=round(secs(stamp)*60)-1669
    if 0<=f<3403:points.update(v for v in [f-1,f,f+1] if 0<=v<3403)
  for s in plan['stagesSeconds']:
   f=round(s*60);points.update(v for v in [f-1,f,f+1] if 0<=v<3403)
  points=sorted(points)
  vf='select='+ '+'.join(f'eq(pts\\,{f*1500})' for f in points)
  state['extractionExitCode']=run([FF,'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(captioned),'-vf',vf,'-frames:v',str(len(points)),'-fps_mode','passthrough',str(LOCAL/'sample-%04d.png')],'extraction.log')
  files=sorted(LOCAL.glob('sample-*.png'));assert len(files)==len(points)
  records=[{'frame':f,'pts':f*1500,'path':rel(p),'sha256':sha(p)} for f,p in zip(points,files)];boards=[]
  font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
  for n in range(0,len(records),6):
   board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
   for j,r in enumerate(records[n:n+6]):
    x=j%3*640;y=j//3*390
    with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
    d.text((x+8,y+5),f"pilot f{r['frame']} / {r['frame']/60:.3f}s",fill='white',font=font)
   b=LOCAL/f'board-{n//6+1:03d}.png';board.save(b);boards.append({'path':rel(b),'sha256':sha(b)})
  assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
  state.update(status='completed',exitCode=0,finishedAt=datetime.now(timezone.utc).isoformat(),samples=records,boards=boards,protectedBaselineUnchanged=True)
  save();print(json.dumps({'exitCode':0,'frames':3403,'samples':len(records),'boards':len(boards)}),flush=True)
 except Exception as e:
  state.update(status='failed',exitCode=1,exception=str(e));save();raise
if __name__=='__main__':main()
