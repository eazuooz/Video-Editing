from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil,argparse
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/presenting-game-scores/black-structural-preview-v1'
ap=argparse.ArgumentParser();ap.add_argument('--revision',type=int,choices=[1,2,3],default=1);args=ap.parse_args();REV=args.revision
VIDEO=OUT/{1:'presenting-game-scores-structural-preview.mp4',2:'presenting-game-scores-structural-preview-v2.mp4',3:'presenting-game-scores-event-label-preview-v3.mp4'}[REV]
QA=OUT/('qa' if REV==1 else f'qa-v{REV}');QA.mkdir(exist_ok=True)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
if (BASE/f'black-structural-qa-v{REV}.json').exists():raise RuntimeError('Existing extraction evidence; inspect and reuse rather than regenerate')
proc=psutil.Process()
execution=dict(schemaVersion=1,pid=proc.pid,createTime=proc.create_time(),commandLine=proc.cmdline(),startedAt=datetime.now(timezone.utc).isoformat(),cpuThreads=2,gpu=0,imagesGitAdded=0,status='running')
save(BASE/f'black-structural-qa-execution-v{REV}.json',execution)
probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(VIDEO)],text=True))
stream=probe['streams'][0];assert (stream['width'],stream['height'],stream['r_frame_rate'],stream['time_base'])==(1920,1080,'60/1','1/90000')
assert len(probe['streams'])==1,'Structural preview must be silent'
expectedFrames=721 if REV==3 else 7201
assert int(stream['nb_frames'])==expectedFrames,stream
decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(VIDEO),'-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
(OUT/f'whole-decode-v{REV}.log').write_text(decode.stderr,'utf-8');assert decode.returncode==0,decode.stderr
scenes=json.loads((BASE.parent/'script/narration.ko.json').read_text('utf-8-sig'))['scenes']
if REV==3:scenes=[s for s in scenes if s['id']=='05-events-and-total']
samples=[]
for i,s in enumerate(scenes):
 for j,local in enumerate([12,120,264,360,510,702]):samples.append(dict(index=len(samples),scene=s['id'],paragraphIndex=j//2,localFrame=local,frame=i*720+local,expectedPts=(i*720+local)*1500))
if REV==2:
 for local in [486,498,522,534,546,558]:samples.append(dict(index=len(samples),scene='06-relative-gap',paragraphIndex=2,localFrame=local,frame=3600+local,expectedPts=(3600+local)*1500,scope='Observe old text disappear completely before new numeric observation'))
if REV==3:
 for local in [270,285,300,330,420,450]:samples.append(dict(index=len(samples),scene='05-events-and-total',paragraphIndex=1,localFrame=local,frame=local,expectedPts=local*1500,scope='Inspect moving contribution token and stationary retained-value label spacing'))
selection='+'.join(f'eq(n\\,{x["frame"]})' for x in samples)
cmd=[FF,'-v','info','-threads','2','-i',str(VIDEO),'-vf',f'select={selection},showinfo','-fps_mode','vfr','-threads','2',str(QA/'sample-%03d.png')]
r=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
(OUT/f'extraction-v{REV}.log').write_text(r.stderr,'utf-8');assert r.returncode==0,r.stderr[-1000:]
import re
pts=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',r.stderr)]
assert pts==sorted(x['expectedPts'] for x in samples),(len(pts),len(samples))
orderedFiles=sorted(QA.glob('sample-*.png'));assert len(orderedFiles)==len(samples),len(orderedFiles)
filesByPts=dict(zip(pts,orderedFiles))
files=[filesByPts[x['expectedPts']] for x in samples]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
boards=[]
for i,scene in enumerate(scenes+([{'id':'06-relative-gap-transition'}] if REV==2 else [{'id':'05-events-and-total-motion'}] if REV==3 else [])):
 board=Image.new('RGB',(1920,1758),(18,18,18));draw=ImageDraw.Draw(board)
 for j in range(6):
  k=i*6+j;p=files[k];im=Image.open(p).convert('RGB');arr=np.asarray(im)
  sample=samples[k];sample.update(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),captionReservePixelsAboveThreshold=int(np.count_nonzero(np.max(arr[910:,:,:],axis=2)>12)))
  # Structural frames have no narration captions; examine the reserved area
  # and preserve that distinction from final burned-caption cue review.
  board.paste(im.resize((960,540)),((j%2)*960,(j//2)*586+40))
  draw.text(((j%2)*960+12,(j//2)*586+8),f'{scene["id"]} p{sample["paragraphIndex"]+1}  f{sample["frame"]} PTS{sample["expectedPts"]}',font=font,fill='white')
 path=QA/f'board-{i+1:02}.jpg';board.save(path,quality=94)
 boards.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),scene=scene['id'],samples=list(range(i*6,i*6+6))))
proof=dict(schemaVersion=1,completedAt=datetime.now(timezone.utc).isoformat(),videoPath=VIDEO.relative_to(ROOT).as_posix(),videoSha256=sha(VIDEO),probe=probe,decodeExitCode=decode.returncode,extractionExitCode=r.returncode,
 frames=expectedFrames,timebase='1/90000',samplePtsDirectlyVerified=True,samples=samples,boards=boards,allBoardsDirectlyRead=False,actualAnimationContinuousReview=False,
 timingMeasured=False,finalCaptionCuePixelsReviewed=False,finalMediaApproved=False,localOnly=True,imagesGitAdded=0)
save(BASE/f'black-structural-qa-v{REV}.json',proof)
execution.update(status='completed',exitCode=0,completedAt=proof['completedAt'],framesExtracted=len(samples),boardsCreated=len(boards))
save(BASE/f'black-structural-qa-execution-v{REV}.json',execution)
print(f'Structural decode0 and exact{len(samples)} frame PTS; {len(boards)} boards local-only, direct review pending.')
