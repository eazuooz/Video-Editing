"""Prepare and measure a complete mobile review copy; keep archival masters intact."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,subprocess
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SLUG='ai-game-development-human-craft'
O=ROOT/'shared/output'/SLUG
parser=argparse.ArgumentParser();parser.add_argument('--compact',action='store_true');parser.add_argument('--resume-compact',action='store_true');options=parser.parse_args()
Q=O/('drive-mobile-compact' if options.compact else 'drive-mobile-review');Q.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,name,cwd=Q):
    with (Q/name).open('wb') as log:
        subprocess.run(args,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert read(ROOT/'shared/publishing/video-production-control.json')['selectedVideo']==SLUG
source=ROOT/f'shared/output/motion-canvas/{SLUG}-subtitled.mp4'
sourceQA=read(O/'encoded-integrity.json')['outputs'][1]
assert sha(source)==sourceQA['sha256']
target=Q/'ai-game-development-human-craft-mobile-review.mp4'
recipe={'sourcePath':source.relative_to(ROOT).as_posix(),'sourceSha256':sourceQA['sha256'],
        'localPath':target.relative_to(ROOT).as_posix(),'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reason':'Transfer fallback: connector downstream explicitly limits downloads to100MiB; web uploads fail or stall. Full720p30 mobile review copy; archival masters unchanged.',
        'resolution':[1280,720],'fps':30,'sourceFrames':88732,'expectedFrames':44366,'humanListening':'pending'}
args=['ffmpeg','-hide_banner','-v','warning','-n','-i',str(source),'-map','0:v:0','-map','0:a:0',
      '-vf','fps=30:start_time=0,scale=1280:720:flags=lanczos','-c:v','h264_nvenc','-preset','p7','-tune','hq',
      '-rc','vbr','-multipass','fullres','-b:v','340k' if options.compact else '700k','-maxrate','4M','-bufsize','8M','-rc-lookahead','32',
      '-spatial-aq','1','-temporal-aq','1','-aq-strength','8','-bf','3','-b_ref_mode','middle',
      '-c:a','copy','-movflags','+faststart','-progress',str(Q/'encode-progress.txt'),str(target)]
if options.resume_compact:
    assert options.compact and target.exists() and not (Q/'review.json').exists()
    previous=read(Q/'recipe.json');assert previous['sourceSha256']==recipe['sourceSha256']
    recipe=previous
else:
    assert not target.exists(),'Do not repeat an existing encode without inspecting its receipt.'
    recipe['args']=args;write(Q/'recipe.json',recipe)
    run(args,'encode.log')
if options.compact and target.stat().st_size>=100*1024*1024:
    preserved=Q/'oversized-video-identical.mp4';assert not preserved.exists()
    target.rename(preserved)
    repair=['ffmpeg','-v','error','-n','-i',str(preserved),'-map','0:v:0','-map','0:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(target)]
    run(repair,'audio-size-adjustment.log')
    recipe['audioSizeAdjustment']={'args':repair,'preservedPath':preserved.relative_to(ROOT).as_posix(),'preservedSha256':sha(preserved),'videoStreamCopied':True}
recipe.update(localSha256=sha(target),sizeBytes=target.stat().st_size)
assert recipe['sizeBytes']<(100 if options.compact else 192)*1024*1024
write(Q/'recipe.json',recipe)
run(['ffmpeg','-v','error','-xerror','-i',str(target),'-map','0:v:0','-map','0:a:0','-f','null','-'],'decode.log')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1280,720,'30/1',44366)
assert abs(float(v['duration'])-sourceQA['duration'])<1/30
pts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(target)]).decode().splitlines()
times=[float(x.split(',')[0]) for x in pts if x and re.match(r'^\d',x)]
assert len(times)==44366 and all(abs(t-i/30)<0.000002 for i,t in enumerate(times))
audio=Q/'audio.aac';run(['ffmpeg','-v','error','-n','-i',str(target),'-map','0:a:0','-c:a','copy','-f','adts',str(audio)],'audio.log')
sameAAC=sha(audio)==sourceQA['aacAdtsSha256'];audioComparison=None
if not sameAAC:
    assert options.compact and recipe.get('audioSizeAdjustment')
    def pcm(path):
        return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','16000','-f','f32le','-']),dtype=np.float32)
    original=pcm(source);current=pcm(target);n=min(len(original),len(current))
    assert abs(len(original)-len(current))<1600
    correlation=float(np.corrcoef(original[:n],current[:n])[0,1]);assert correlation>.995
    def levels(x):
        sums=np.r_[0,np.cumsum(x[:n].astype(np.float64)**2)]
        starts=np.arange(0,n-6400+1,1600)
        return 10*np.log10(np.maximum((sums[starts+6400]-sums[starts])/6400,1e-12))
    before=levels(original);after=levels(current);diff=(after-before)[before>-40]
    audioComparison={'status':'pass','method':'All decoded16kHz mono samples correlated and400ms windows/100ms hop compared; active windows above-40dBFS. Same source mix, AAC160kbps encoding only. No new TTS or mixing.',
                     'correlation':correlation,'activeWindows':len(diff),'medianGainChangeDb':float(np.median(diff)),
                     'p999AbsGainChangeDb':float(np.percentile(np.abs(diff),99.9)),'maxAbsGainChangeDb':float(np.max(np.abs(diff))),
                     'sourceAACSha256':sourceQA['aacAdtsSha256'],'currentAACSha256':sha(audio),'sampleCountDelta':len(current)-len(original)}
    assert audioComparison['p999AbsGainChangeDb']<.3 and abs(audioComparison['medianGainChangeDb'])<.05
run(['ffmpeg','-v','info','-i',str(source),'-i',str(target),'-filter_complex',
     '[0:v]fps=30:start_time=0,scale=1280:720:flags=lanczos,setpts=PTS-STARTPTS,split=2[s][sc];[1:v]setpts=PTS-STARTPTS,split=2[m][mc];[s][m]ssim=stats_file=frames.txt:shortest=1[f];[sc]crop=1280:140:0:580[sc2];[mc]crop=1280:140:0:580[mc2];[sc2][mc2]ssim=stats_file=captions.txt:shortest=1[c]',
     '-map','[f]','-map','[c]','-an','-f','null','-'],'comparison.log')
def values(name):
    rows=(Q/name).read_text().splitlines()
    assert len(rows)==44366
    return [float(re.search(r'All:([\d.]+)',line)[1]) for line in rows]
full=values('frames.txt');captions=values('captions.txt')
data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
selected=set(sorted(range(len(full)),key=lambda i:full[i])[:8]+sorted(range(len(captions)),key=lambda i:captions[i])[:8])
scenes=[]
for s in data['scenes']:
    a=60+round(s['start']*30);b=a+round(s['duration']*30)
    w=min(range(a,b),key=lambda i:full[i]);selected.add(w)
    scenes.append({'scene':s['id'],'firstFrame':a,'endFrame':b,'worstFrame':w,'minSsim':full[w]})
selected.update([0,59,60,44065,44066,44365]);selected=sorted(selected)
def expr(xs):
    if len(xs)==1:return f'eq(n,{xs[0]})'
    m=len(xs)//2;return '('+expr(xs[:m])+'+'+expr(xs[m:])+')'
(Q/'frames').mkdir(exist_ok=True)
run(['ffmpeg','-v','error','-i',str(target),'-vf',"select='"+expr(selected)+"',scale=640:360",'-fps_mode','passthrough',str(Q/'frames/%04d.png')],'frames.log')
pages=[]
for start in range(0,len(selected),9):
    page=Image.new('RGB',(1920,1140),(24,24,24));draw=ImageDraw.Draw(page)
    for j,f in enumerate(selected[start:start+9]):
        x=j%3*640;y=j//3*380;page.paste(Image.open(Q/f'frames/{start+j+1:04d}.png'),(x,y))
        draw.text((x+5,y+362),f'{f/30:.3f}s full={full[f]:.5f} caption={captions[f]:.5f}',fill='white')
    p=Q/f'contact-{start//9+1:02d}.jpg';page.save(p,quality=94);pages.append(p.relative_to(ROOT).as_posix())
layout=read(O/'caption-overlays/layout.json')['layout'];cues=[]
for cue in layout:
    a=(cue['startFrame']+1)//2;b=(cue['endFrame']+1)//2
    assert b>a
    cues.append({'cue':cue['cue'],'frames':b-a,'meanCaptionSsim':sum(captions[a:b])/(b-a),'minCaptionSsim':min(captions[a:b])})
result={**recipe,'status':'technical-pass-visual-review-pending','fullVideoAudioDecode':'pass','pts':'pass','frames':44366,
        'durationSeconds':float(v['duration']),'identicalAAC':sameAAC,'aacAdtsSha256':sha(audio),'audioEncodingContinuity':audioComparison,
        'allFramesCompared':len(full),'meanSsim':sum(full)/len(full),'minSsim':min(full),
        'allCaptionFramesCompared':len(captions),'meanCaptionSsim':sum(captions)/len(captions),'minCaptionSsim':min(captions),
        'cues':cues,'scenes':scenes,'selectedFrames':selected,'pages':pages,
        'comparisonScope':'Every mobile frame against the same fps/scale transform of the reviewed1080p60 master; all340cue intervals covered. Metric is evidence, not semantic or human listening approval.'}
write(Q/'review.json',result)
print(json.dumps({k:result[k] for k in ['status','localSha256','sizeBytes','frames','meanSsim','minSsim','meanCaptionSsim','pages']}))
