"""Actual render samples around spoken beats; extraction is not pixel approval."""
from pathlib import Path
import json,subprocess,math,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
D=O/'explanation-motion-pixels';D.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
records=[]
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
    timeline=json.loads((ROOT/f'projects/{slug}/production/timeline.json').read_text(encoding='utf8'))
    for slot in timeline['scenes']:
        if slot['preservedOriginal'] or slot['classification']!='explanation':continue
        ident=slot['id'];video=O/f'caption-safe-v2/videos/interpolation_additions/1080p60/{ident}.mp4'
        times=[.2,*[min(slot['seconds']-.05,t+.25) for t in slot['lineStarts'][1:]],*[min(slot['seconds']-.05,t+1.65) for t in slot['lineStarts'][1:]],slot['seconds']-.15]
        if ident in ['IP04','IP08']:times.extend(min(slot['seconds']-.05,c['start']+.25) for c in slot['sentenceCues'])
        times=sorted({round(t,3) for t in times if 0<=t<slot['seconds']})
        frames=[]
        for i,t in enumerate(times):
            path=D/f'{ident}-{i:02}.jpg'
            subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=960:540','-q:v','2',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
            frames.append({'time':t,'frame':path.relative_to(ROOT).as_posix()})
        for page in range(math.ceil(len(frames)/4)):
            sheet=Image.new('RGB',(1920,1120),'white');draw=ImageDraw.Draw(sheet)
            for i,frame in enumerate(frames[page*4:page*4+4]):
                x=(i%2)*960;y=(i//2)*560;sheet.paste(Image.open(ROOT/frame['frame']),(x,y+20));draw.text((x+5,y),f'{ident} t{frame["time"]:.3f}',font=font,fill='black')
            sheet.save(D/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
        records.append({'scene':ident,'sourceSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'samples':frames,'directPixelApproval':False,'captionAndVoiceReview':'separate final pixels required'})
        print('Extracted actual explanation beats',ident,flush=True)
(D/'extraction.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
