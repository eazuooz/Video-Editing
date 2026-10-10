"""Review only the two new silent MC scenes; no baseline scene/audio mutation."""
from pathlib import Path
import subprocess, json, hashlib, datetime, os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,choices=[1,2,3],default=1)
VERSION=ap.parse_args().version
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
SRC = ROOT / f'shared/output/unpublished-teaching-clarity-revision/motion/explanation-additions-v{VERSION}/explanation-project.mp4'
OUT = ROOT / f'shared/output/unpublished-teaching-clarity-revision/motion/additive-mc-qa-v{VERSION}'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
assert not OUT.exists(), 'Preserve existing QA rather than overwrite it'
OUT.mkdir(parents=True)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
probe = subprocess.run([FP,'-v','error','-select_streams','v:0','-show_frames','-show_streams','-show_entries','frame=pts,pkt_duration,best_effort_timestamp,color_range,color_space:stream=width,height,nb_frames,time_base,r_frame_rate,duration','-of','json',str(SRC)],capture_output=True,text=True,check=True)
p = json.loads(probe.stdout)
save(OUT/'probe.json',p)
frames = p['frames']; n = len(frames)
assert n == (403 if VERSION==3 else 886), n
assert p['streams'][0]['time_base'] == '1/90000'
assert all(int(f['pts']) == i*1500 for i,f in enumerate(frames))
sample = sorted(set(range(0,n,15)) | {n-1} | (set(range(0,5)) | set(range(n-5,n)) if VERSION==3 else set(range(477,487)) | set(range(880,886))))
state = {'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'cpuThreads':2,'gpuJobs':0,'source':str(SRC.relative_to(ROOT)).replace('\\','/'),'sourceSha256':sha(SRC),'expectedFrames':n,'sampleFrames':sample,'stage':'decoding'}
save(R/f'additive-mc-qa-execution-v{VERSION}.json',state)
log = open(OUT/'decode.stderr.log','wb')
cmd = [FF,'-hide_banner','-v','warning','-threads','2','-i',str(SRC),'-map','0:v:0','-an','-threads','2','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log)
rows=[]; samples=[]
size=1920*1080*3
for i in range(n):
    data=bytearray()
    while len(data)<size:
        block=proc.stdout.read(size-len(data))
        assert block, (i,len(data))
        data.extend(block)
    a=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
    # Empty narration-caption area is a pixel property, not inferred from JSX.
    band=a[910:]
    dark=int(np.any(band<235,axis=2).sum())
    rows.append({'frame':i,'pts':i*1500,'nonWhitePixelsBelow910':dark,'decodedRgbSha256':hashlib.sha256(data).hexdigest()})
    if i in sample:
        path=OUT/f'frame-{i:04d}.png'
        Image.fromarray(a).save(path)
        samples.append({'frame':i,'pts':i*1500,'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path)})
assert proc.stdout.read(1)==b''
code=proc.wait();log.close();assert code==0,code
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
boards=[]
for bi in range(0,len(samples),6):
    subset=samples[bi:bi+6]
    board=Image.new('RGB',(1440,1296),(30,30,30)); d=ImageDraw.Draw(board)
    for k,s in enumerate(subset):
        x=(k%2)*720;y=(k//2)*432
        im=Image.open(ROOT/s['path']).resize((720,405))
        board.paste(im,(x,y)); d.text((x+8,y+406),f"f{s['frame']} PTS{s['pts']}",fill='white',font=font)
    path=OUT/f'board-{bi//6+1:02d}.png';board.save(path)
    boards.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'frames':[s['frame'] for s in subset]})
save(OUT/'frames.json',rows)
result={**state,'stage':'sample-review-pending','actualDecodeExitCode':code,'probeExitCode':probe.returncode,'actualFrames':n,'allFramePtsExact':True,'sampleCount':len(samples),'boardCount':len(boards),'samples':samples,'boards':boards,'maxNonWhitePixelsBelow910':max(r['nonWhitePixelsBelow910'] for r in rows),'allSamplePixelsDirectlyReviewed':False,'continuousAnimationApproved':False,'actualMCRenderFfmpegExitCode':None,'finalCaptionedPixelsApproved':False,'newMediaGitAdded':0}
save(R/f'additive-mc-qa-v{VERSION}.json',result)
save(R/f'additive-mc-qa-execution-v{VERSION}.json',{**state,'stage':'finished','actualDecodeExitCode':code,'samples':len(samples),'boards':len(boards)})
print(json.dumps({k:result[k] for k in ['actualFrames','actualDecodeExitCode','allFramePtsExact','sampleCount','boardCount','maxNonWhitePixelsBelow910']}),flush=True)
