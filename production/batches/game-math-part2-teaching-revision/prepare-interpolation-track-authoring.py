"""Exact native coordinate frames for independent annotation authoring."""
from pathlib import Path
import argparse,json,subprocess,math,bisect
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-track-authoring';D.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
selected=set(args.only.split(',')) if args.only else None
jobs=[]
if args.baseline:
    for x in read(ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-baseline-review/records.json'):
        if selected and x['id'] not in selected:continue
        jobs.append({'name':'O'+x['id'],'source':ROOT/x['baselineClip'],'interval':[0,x['seconds']]})
else:
    for x in read(B/'interpolation-game-insertions.json')['scenes']:
        if selected and x['id'] not in selected:continue
        for i,interval in enumerate(x['intervals']):jobs.append({'name':x['id']+f'-{i+1}','source':ROOT/f"shared/output/game-math-part2-teaching-revision/sources/{x['sourceId']}.mp4",'interval':interval,'track':B/f"interpolation-tracks/{x['id'].lower()}-{i+1}-torso.json"})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
def point_at(track,t):
    if not track or len(track['keyframes'])<2:return None
    k=track['keyframes'];times=[x['t'] for x in k]
    if t<times[0] or t>times[-1] or any(a<=t<=b for a,b in track['hideIntervals']):return None
    j=min(len(k)-2,max(0,bisect.bisect_right(times,t)-1));a,b=k[j:j+2];u=(t-a['t'])/(b['t']-a['t'])
    return {key:np.array(a[key])*(1-u)+np.array(b[key])*u for key in ['upper','lower']}
for job in jobs:
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','json',str(job['source'])]))
    n,d=map(int,info['streams'][0]['r_frame_rate'].split('/'));fps=n/d;stride=round(fps*2)
    a,b=job['interval'];first=math.ceil(a*fps-1e-7);last=math.floor((b-.04)*fps);count=(last-first)//stride+1
    command=['ffmpeg','-v','error','-threads','1','-ss',str(first/fps),'-i',str(job['source']),'-t',str((last-first+stride)/fps),'-vf',f'scale=800:450,select=not(mod(n\\,{stride}))','-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    images=[];records=[];track=read(job['track']) if job.get('track') and job['track'].exists() else None
    folder=D/job['name'];folder.mkdir(exist_ok=True)
    for i in range(count):
        raw=proc.stdout.read(800*450*3);assert len(raw)==800*450*3
        im=Image.frombytes('RGB',(800,450),raw);t=(first+i*stride)/fps
        im.save(folder/f'{i:03}.png')
        draw=ImageDraw.Draw(im);p=point_at(track,t)
        if p:draw.line([tuple(p['lower']),tuple(p['upper'])],fill='#ef5350',width=4)
        # One crop for readable coordinates; saved originals stay untouched.
        im=im.crop((200,70,650,420));draw=ImageDraw.Draw(im)
        for x in range(250,650,50):draw.text((x-200,0),str(x),font=font,fill='white',stroke_width=1,stroke_fill='black')
        for y in range(100,420,50):draw.text((0,y-70),str(y),font=font,fill='white',stroke_width=1,stroke_fill='black')
        images.append(im);records.append({'i':i,'t':t,'nativeFrame':first+i*stride,'frame':(folder/f'{i:03}.png').relative_to(ROOT).as_posix(),'torso':{k:v.tolist() for k,v in p.items()} if p else None})
    proc.stdout.read();assert proc.wait()==0
    for page in range(math.ceil(len(images)/9)):
        sheet=Image.new('RGB',(1350,3*375),'white');draw=ImageDraw.Draw(sheet)
        for cell,(im,r) in enumerate(zip(images[page*9:(page+1)*9],records[page*9:(page+1)*9])):
            x=cell%3*450;y=cell//3*375;sheet.paste(im,(x,y+25));draw.text((x+3,y+3),f"{job['name']} i{r['i']:03} t{r['t']:.4f}s",font=font,fill='black')
        sheet.save(folder/f'page-{page+1}.jpg',quality=95)
    (folder/'frames.json').write_text(json.dumps({'name':job['name'],'source':job['source'].relative_to(ROOT).as_posix(),'nativeFps':info['streams'][0]['r_frame_rate'],'crop':[200,70,650,420],'records':records,'pixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(job['name'],len(images),'native authoring frames',flush=True)
