"""Read only selected retained action windows for new semantic annotation anchors."""
from pathlib import Path
import json,hashlib,datetime,subprocess,os
from PIL import Image,ImageDraw,ImageFont
import psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/retained-annotation-preflight-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not OUT.exists();OUT.mkdir(parents=True)
specs=[('01','002',599,300,'Aim-mode nozzle/reticle motion versus background edge; paragraph2.'),
 ('03','005',0,300,'Nozzle points left/right while staircase and tree briefly remain; paragraph1.'),
 ('05','009',0,300,'Nearby post and farther tree/fence shift during player relocation; paragraph1.'),
 ('07','016',514,252,'Different Talos excerpt: wall/laser orientation, never uninterrupted gameplay; paragraph2.'),
 ('09','024',0,360,'Find the sprayed surface as view turns around slide; paragraph1.'),
 ('11','030',1155,300,'Look upward toward crossbar; separate view change and local tool action; paragraph3.')]
state=dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),
 createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cwd=os.getcwd(),
 cpuThreads=2,gpuJobs=0,stage='extracting-new-annotation-anchor-windows',windows=[],
 existingSceneOrPcmMutations=0,foreignProcessesChanged=0,newGitImages=0,allFinalPixelsApproved=False)
save(R/'retained-annotation-preflight-execution-v1.json',state)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
for sid,cut,local,n,purpose in specs:
 src=ROOT/f'projects/motion-sickness-games/production/final-v1/cut-{cut}.mp4'
 probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts:stream=nb_frames,time_base,r_frame_rate','-show_streams','-of','json',str(src)]))
 assert len(probe['frames'])>=n
 step=round(1/float(eval(probe['streams'][0]['time_base']))/60)
 assert all(int(probe['frames'][f]['pts'])==f*step for f in range(n))
 folder=OUT/f'scene{sid}';folder.mkdir()
 cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(src),'-frames:v',str(n),'-an','-threads','1','-vsync','0','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 rows=[];points=sorted(set(range(0,n,15))|{n-1});allframes=[]
 with (folder/'decode.stderr.log').open('wb') as log:
  proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log)
  for f in range(n):
   raw=bytearray()
   while len(raw)<1920*1080*3:
    b=proc.stdout.read(1920*1080*3-len(raw));assert b;raw.extend(b)
   allframes.append(dict(frame=f,decodedRgbSha256=hashlib.sha256(raw).hexdigest()))
   if f in points:
    p=folder/f'frame-{f:04d}.png';Image.frombytes('RGB',(1920,1080),bytes(raw)).save(p)
    rows.append(dict(frame=f,sceneLocalFrame=local+f,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
  assert proc.stdout.read(1)==b'';exitcode=proc.wait();assert exitcode==0
 boards=[]
 for j in range(0,len(rows),6):
  im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
  for k,row in enumerate(rows[j:j+6]):
   x=k%3*640;y=k//3*390
   im.paste(Image.open(ROOT/row['path']).resize((640,360)),(x,y+30))
   d.text((x+5,y+4),f"scene{sid} cut{cut} f{row['frame']} local{row['sceneLocalFrame']}",font=font,fill='white')
  p=folder/f'board-{j//6+1:02d}.png';im.save(p);boards.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
 save(folder/'all-frame-hashes.json',allframes)
 state['windows'].append(dict(scene=sid,cut=cut,source=src.relative_to(ROOT).as_posix(),sourceSha256=sha(src),
  sceneLocalStart=local,frames=n,sourcePtsStep=step,purpose=purpose,actualDecodeExitCode=exitcode,
  sourceSpeed=1,sourceAudioUsed=False,samples=rows,boards=boards,
  allSelectedSamplesDirectlyRead=False,semanticAnchorsApproved=False,finalCaptionedPixelsApproved=False))
 save(R/'retained-annotation-preflight-execution-v1.json',state)
state.update(stage='source-window-direct-review-pending',actualOuterExitCode=0,
 samples=sum(len(w['samples']) for w in state['windows']),boards=sum(len(w['boards']) for w in state['windows']))
save(R/'retained-annotation-preflight-execution-v1.json',state)
print(json.dumps({'exitCode':0,'windows':len(state['windows']),'frames':sum(w['frames'] for w in state['windows']),'samples':state['samples'],'boards':state['boards']}))
