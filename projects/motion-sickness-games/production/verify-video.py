"""Measure real final outputs and generate every cue/cut image for direct review."""
from pathlib import Path
import json,hashlib,subprocess,io,re,sys,concurrent.futures
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent/'final-v1'
manifest=json.loads((ROOT/'projects/motion-sickness-games/project.json').read_text(encoding='utf-8'));plan=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
def run(a):return subprocess.check_output(a,stderr=subprocess.STDOUT).decode('utf-8',errors='replace')
def snap(file,t,out,width=1920):
    subprocess.check_call(['ffmpeg','-v','error','-y','-threads','2','-ss',str(max(0,t)),'-i',str(file),'-frames:v','1','-vf',f'scale={width}:-2','-threads','1',str(out)])
def sheets(points,kind,columns=3,rows=4):
    dest=WORK/(kind+'-native');dest.mkdir(exist_ok=True);files=[]
    def capture(row):
        i,(file,t,label)=row;out=dest/f'{i+1:03d}.png';snap(file,t,out);return out
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(capture,enumerate(points)))
    cols=columns;w=1920//cols;h=round(w*1080/1920);pages=[]
    for i,(file,point) in enumerate(zip(files,points)):
        page=i//(cols*rows)
        if page==len(pages):pages.append(Image.new('RGB',(1920,(h+35)*rows),'white'))
        im=Image.open(file);im.thumbnail((w,h));x=i%cols*w;y=(i//cols%rows)*(h+35);pages[page].paste(im,(x,y));ImageDraw.Draw(pages[page]).text((x+8,y+h+3),f'{i+1:03d} {point[2]} / {point[1]:.3f}s',fill='black')
    for i,p in enumerate(pages):p.save(WORK/f'{kind}-{i+1:02d}.jpg',quality=92)
    return {'count':len(points),'pages':len(pages),'nativeDirectory':str(dest.relative_to(ROOT)).replace('\\','/'),'review':'pending','images':[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'label':pt[2],'seconds':pt[1],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f,pt in zip(files,points)]}
if '--cuts-only' in sys.argv:
    points=[]
    for c in plan['cuts']:
        for t,k in [(.08,'first'),(c['seconds']/2,'middle'),(c['seconds']-.08,'last')]:points.append((ROOT/c['video'],t,f"cut{c['id']} {c['sourceId']} {k}"))
    result=sheets(points,'selected-cuts',3,4);(WORK/'selected-cuts-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'{len(points)} actual selected first/middle/last images ready for direct review.');sys.exit(0)
results={}
for key in ['videoClean','videoBurnedCaptions']:
    file=ROOT/manifest['paths'][key];meta=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]));v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264',1920,1080,'60/1',plan['totalFrames']),(key,v)
    assert a['codec_name']=='aac' and abs(float(meta['format']['duration'])-plan['seconds'])<.06
    log=WORK/(key+'-decode.log')
    with log.open('w') as f:subprocess.check_call(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(file),'-f','null','-'],stdout=f,stderr=f)
    assert not log.read_text(encoding='utf-8').strip()
    results[key]={'frames':int(v['nb_frames']),'seconds':float(meta['format']['duration']),'fullDecodePassed':True,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'decodeLog':str(log.relative_to(ROOT)).replace('\\','/')}
audio={k:run(['ffmpeg','-v','error','-i',str(ROOT/manifest['paths'][k]),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip() for k in ['audioMix','videoClean','videoBurnedCaptions']};assert len(set(audio.values()))==1;results['sameCopiedAacAudio']=audio
def srts(p):return re.findall(r'(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})',(ROOT/p).read_text(encoding='utf-8'))
ko,en=srts(manifest['paths']['captionsKo']),srts(manifest['paths']['captionsEn']);assert ko==en and len(ko)==len(json.loads((WORK/'caption-alignment.json').read_text(encoding='utf-8'))['entries'])
layouts=json.loads((WORK/'caption-layout-qa.json').read_text(encoding='utf-8'))['cues'];assert all(e['end']>e['start'] and not e['overlap'] for e in layouts)
caption_points=[(ROOT/manifest['paths']['videoBurnedCaptions'],(e['start']+e['end'])/2,f"cue{e['cue']} {e['picture']}") for e in layouts]
results['captionImages']=sheets(caption_points,'caption-cues',3,4)
points=[(ROOT/manifest['paths']['videoBurnedCaptions'],1.65,'original cat intro')]
for s in plan['scenes']:
    if s['classification']=='explanation':
        for f in [.08,.5,.92]:points.append((ROOT/manifest['paths']['videoBurnedCaptions'],s['start']+s['seconds']*f,f"scene{s['id']} 2.5D {f}"))
points.append((ROOT/manifest['paths']['videoBurnedCaptions'],plan['bodyEnd']+5,'original member profiles/names/badges and logo'))
results['compositionImages']=sheets(points,'final-composition',3,4)
audio_scan=run(['ffmpeg','-hide_banner','-threads','2','-i',str(ROOT/manifest['paths']['audioMix']),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);measurement=json.JSONDecoder().raw_decode(audio_scan[audio_scan.rfind('{'):])[0];assert abs(float(measurement['input_i'])+16)<=.6 and float(measurement['input_tp'])<=-1.45;results['mixMeasurement']=measurement
assert abs(plan['actualFrames']-.6*plan['bodyFrames'])<=1
results.update({'totalSeconds':plan['seconds'],'bodySeconds':plan['bodySeconds'],'actualSeconds':plan['gameplaySeconds'],'explanationSeconds':plan['explanationSeconds'],'actualRatio':plan['gameplayShare'],'ratioErrorFrames':plan['ratioErrorFrames'],'cueCount':len(ko),'captionSegmentCount':len(layouts),'identicalKoEnTiming':True,'directVisualReview':'pending','fullMixAsrReview':'pending','humanListening':'pending','publicRights':'pending'})
(WORK/'qa.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Full decoding, frame/audio and caption checks passed; direct image and mixed-ASR review pending.')
