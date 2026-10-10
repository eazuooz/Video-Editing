"""Direct moving-pixel draft from editable visible landmarks. No final QA claim."""
from pathlib import Path
import json,subprocess,bisect,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision'
d=json.loads((B/'gb05-landmarks.json').read_text(encoding='utf8'));w,h=d['coordinatePixels'];start,end=d['interval'];fps=30
frames=round((end-start)*fps);times=[p['t'] for p in d['keyframes']]
decoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(start),'-i',str(ROOT/d['sourceFile']),'-t',str(end-start),'-vf',f'scale={w}:{h},fps={fps}','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
target=O/'source-review/gb05-tracking-preview.mp4'
encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2',str(target)],stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',13)
sheet=Image.new('RGB',(1600,4*245),'white');sheet_draw=ImageDraw.Draw(sheet);samples=[round((i*.75+1.5)*fps) for i in range(16)];dense=[]
for i in range(frames):
    raw=decoder.stdout.read(w*h*3);assert len(raw)==w*h*3
    im=Image.frombytes('RGB',(w,h),raw);draw=ImageDraw.Draw(im);t=start+i/fps
    active=times[0]<=t<=times[-1];r={'sourceTime':t,'hidden':not active}
    if active:
        j=min(len(times)-2,max(0,bisect.bisect_right(times,t)-1));a,b=d['keyframes'][j:j+2];u=(t-a['t'])/(b['t']-a['t'])
        points={key:np.array(a[key])*(1-u)+np.array(b[key])*u for key in ['upper','lower','wheel']};r['points']={k:v.tolist() for k,v in points.items()}
        upper,lower,wheel=points['upper'],points['lower'],points['wheel'];delta=upper-lower;delta/=np.linalg.norm(delta);normal=np.array([-delta[1],delta[0]])
        if i/fps>=1.5:
            draw.line([tuple(lower),tuple(upper)],fill=d['colors']['torso'],width=4)
            draw.polygon([tuple(upper),tuple(upper-11*delta+4*normal),tuple(upper-11*delta-4*normal)],fill=d['colors']['torso'])
            draw.text((min(upper[0],lower[0])-100,min(upper[1],lower[1])-30),'몸체 방향',font=font,fill=d['colors']['torso'],stroke_width=1,stroke_fill='black')
        if i/fps>=3:
            draw.line([tuple(wheel[0]),tuple(wheel[1])],fill=d['colors']['wheel'],width=4)
            draw.text((wheel[0][0]+30,min(355,min(wheel[0][1],wheel[1][1])-38)),'보이는 바퀴 윤곽',font=font,fill=d['colors']['wheel'],stroke_width=1,stroke_fill='black')
        if i/fps>=4.5:
            for dy in range(-50,51,12):draw.line([(lower[0]+65,lower[1]+dy),(lower[0]+65,lower[1]+dy+6)],fill=d['colors']['screenReference'],width=3)
            draw.text((lower[0]+70,lower[1]-70),'화면 기준',font=font,fill=d['colors']['screenReference'],stroke_width=1,stroke_fill='black')
    draw.rectangle((175,90,620,120),fill='#171717');draw.text((183,97),'화면 투영선 · 몸체 방향 / 바퀴 윤곽 · 카메라도 이동',font=small,fill='white')
    encoder.stdin.write(np.asarray(im).tobytes());dense.append(r)
    if i in samples:
        k=samples.index(i);x=k%4*400;y=k//4*245;sheet.paste(im.resize((400,225)),(x,y));sheet_draw.text((x+6,y+228),f'{t:.2f}s / projected landmarks / hidden={not active}',fill='black')
decoder.stdout.read();assert decoder.wait()==0;encoder.stdin.close();assert encoder.wait()==0
sheet.save(O/'source-review/gb05-moving-pixels.jpg',quality=95)
(O/'gb05-tracking-dense.json').write_text(json.dumps({'frames':frames,'tracking':dense,'narrationTimed':False,'movingPixelApproval':False,'screenSpaceOnly':True},indent=2)+'\n',encoding='utf8')
(O/'source-review/gb05-review.html').write_text('''<!doctype html><meta charset="utf-8"><title>몸체 추적 검토</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>자전거: 움직이는 관찰선 검토</h1><button onclick="document.getElementById('GB05').play()">추적 재생</button><video id="GB05" muted controls src="gb05-tracking-preview.mp4"></video>''',encoding='utf8')
print(json.dumps({'frames':frames,'narrationTimed':False,'finalApproval':False}))
