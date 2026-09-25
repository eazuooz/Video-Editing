"""Full master media checks and one actual rendered frame per source page."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/renderformer-explained/production/body-review'
OUT=BASE/'video-qa'
OUT.mkdir(exist_ok=True)
def run(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True,encoding='utf-8')
timing=json.loads((BASE/'timing.json').read_text(encoding='utf-8'))
reports=[]
for variant in ['clean','captioned']:
    file=BASE/f'renderformer-{variant}-review.mp4'
    if not file.exists():raise FileNotFoundError(file)
    p=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)).stdout)
    v=next(s for s in p['streams'] if s['codec_type']=='video')
    a=next(s for s in p['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',timing['totalFrames'])
    assert abs(float(p['format']['duration'])-timing['duration'])<.08
    composition=BASE/'caption-composition.json'
    already_decoded=(variant=='captioned' and composition.exists() and composition.stat().st_mtime>=file.stat().st_mtime
        and json.loads(composition.read_text(encoding='utf-8')).get('fullDecodePassed') is True)
    if not already_decoded:run('ffmpeg','-v','error','-i',str(file),'-f','null','-')
    audio_hash=run('ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-').stdout.strip()
    reports.append({'variant':variant,'frames':int(v['nb_frames']),'duration':float(p['format']['duration']),
                    'bytes':int(p['format']['size']),'video':v['codec_name'],'audio':a['codec_name'],
                    'audioHash':audio_hash,'fullDecodePassed':True,
                    'decodeEvidence':'caption-composition.json' if already_decoded else 'verify_body.py'})
assert reports[0]['audioHash']==reports[1]['audioHash']
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for s in timing['scenes']:
    cue=s['cues'][min(1,len(s['cues'])-1)]
    t=s['firstFrame']/60+(cue['start']+cue['end'])/2
    frame=OUT/f'page-{s["sourcePage"]:02}.png'
    run('ffmpeg','-v','error','-y','-ss',str(t),'-i',str(BASE/'renderformer-captioned-review.mp4'),'-frames:v','1',str(frame))
for start in range(1,89,8):
    contact=Image.new('RGB',(1280,4*390),'#eceff2');d=ImageDraw.Draw(contact)
    for i,p in enumerate(range(start,min(start+8,89))):
        im=Image.open(OUT/f'page-{p:02}.png').convert('RGB');im.thumbnail((640,360))
        x=(i%2)*640;y=(i//2)*390
        contact.paste(im,(x,y));d.text((x+12,y+362),f'Page {p}',font=font,fill='#202020')
    contact.save(OUT/f'contact-{start:02}.jpg',quality=93)
result={'pages':88,'cues':len(timing['captions']),'reports':reports,'audioStreamsIdentical':True,
        'bgmIncluded':False,'membershipOutroIncluded':False,'publishReady':False,'humanListeningApproved':False}
(BASE/'media-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result),flush=True)
