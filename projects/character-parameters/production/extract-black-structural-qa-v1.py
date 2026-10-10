"""One CPU2 structural-prototype decode and exact-PTS sample extraction."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil, re, ctypes
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/character-parameters/black-structural-preview-v1'
VIDEO=OUT/'character-parameters-black-structural-v1.mp4'; QA=OUT/'qa-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'; PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not QA.exists() and not (BASE/'black-structural-qa-v1.json').exists(), 'Reuse completed QA rather than extract again.'
resource=read(BASE/'resource-before-structural-qa-v1.json')
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
me=psutil.Process(); execution=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),startedAt=now(),status='running',cpuThreads=2,gpu=0,exitCode=None)
save(BASE/'black-structural-qa-execution-v1.json',execution); QA.mkdir()
probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(VIDEO)],text=True))
v=probe['streams'][0]
assert len(probe['streams'])==1 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_frames']))==(1920,1080,'60/1','1/90000',8641)
decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(VIDEO),'-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
(OUT/'whole-decode-v1.log').write_text(decode.stderr,'utf-8'); assert decode.returncode==0,decode.stderr
scenes=read(BASE.parent/'script/narration.ko.json')['scenes']; samples=[]; groups=[]
for i,s in enumerate(scenes):
    starts=[0,180,360,540] if len(s['lines'])==4 else [0,240,480]
    step=180 if len(starts)==4 else 240; indices=[]
    for j,a in enumerate(starts):
        for local in [a+30,a+step-18]:
            indices.append(len(samples)); samples.append(dict(index=len(samples),scene=s['id'],paragraphIndex=j,localFrame=local,frame=i*720+local,expectedPts=(i*720+local)*1500))
    groups.append((s['id'],indices))
selection='+'.join(f'eq(n\\,{x["frame"]})' for x in samples)
r=subprocess.run([FF,'-v','info','-threads','2','-i',str(VIDEO),'-filter_threads','1','-vf',f'select={selection},showinfo','-fps_mode','vfr','-threads','2',str(QA/'sample-%03d.png')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
(OUT/'extraction-v1.log').write_text(r.stderr,'utf-8'); assert r.returncode==0,r.stderr[-2000:]
pts=[int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',r.stderr)]
files=sorted(QA.glob('sample-*.png')); assert pts==[x['expectedPts'] for x in samples] and len(files)==len(samples)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22); boards=[]
for sample,p in zip(samples,files):
    arr=np.asarray(Image.open(p).convert('RGB'))
    sample.update(path=rel(p),sha256=sha(p),captionReservePixelsAboveThreshold=int(np.count_nonzero(np.max(arr[910:,:,:],axis=2)>12)))
for scene,indices in groups:
    for start in range(0,len(indices),6):
        subset=indices[start:start+6]; board=Image.new('RGB',(1920,1758),(18,18,18)); d=ImageDraw.Draw(board)
        for j,k in enumerate(subset):
            x=j%2*960; y=j//2*586; row=samples[k]
            board.paste(Image.open(ROOT/row['path']).convert('RGB').resize((960,540)),(x,y+40))
            d.text((x+12,y+8),f'{scene} p{row["paragraphIndex"]+1} f{row["frame"]} PTS{row["expectedPts"]}',font=font,fill='white')
        p=QA/f'board-{len(boards)+1:02}.jpg'; board.save(p,quality=94)
        boards.append(dict(path=rel(p),sha256=sha(p),scene=scene,samples=subset))
proof=dict(schemaVersion=1,completedAt=now(),videoPath=rel(VIDEO),videoSha256=sha(VIDEO),probe=probe,decodeExitCode=decode.returncode,extractionExitCode=r.returncode,frames=8641,samplePtsDirectlyVerified=True,samples=samples,boards=boards,allBoardsDirectlyRead=False,actualAnimationContinuousReview=False,timingMeasured=False,finalCaptionCuePixelsReviewed=False,finalMediaApproved=False,localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-qa-v1.json',proof)
execution.update(status='completed',exitCode=0,completedAt=now(),framesExtracted=len(samples),boardsCreated=len(boards)); save(BASE/'black-structural-qa-execution-v1.json',execution)
print(f'Prototype whole decode0, {len(samples)} exactPTS samples/{len(boards)} boards. Direct review pending.',flush=True)
