"""CPU-only coordinate authoring frames. These are never pixel approval."""
from pathlib import Path
import argparse,subprocess,json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision'
parser=argparse.ArgumentParser();parser.add_argument('id');parser.add_argument('source');parser.add_argument('start',type=float);parser.add_argument('end',type=float);parser.add_argument('--step',type=float,default=.5);args=parser.parse_args()
source=ROOT/(('shared/output/game-math-part2-teaching-revision/sources/' if args.source=='_dw9jjRpanA' else 'shared/output/game-math-part2-full-series/sources/')+args.source+'.mp4')
D=O/'landmark-authoring'/args.id;D.mkdir(parents=True,exist_ok=True)
rate=1/args.step;count=round((args.end-args.start)/args.step)+1
stride=round(60*args.step);assert abs(stride/60-args.step)<1e-8
# fps downsampling chooses the last frame of the rounded output bin, not n=0.
# Explicit native-frame selection keeps every labelled reference time exact.
command=['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(args.start),'-i',str(source),'-t',str(args.end-args.start+args.step),'-vf',f'scale=800:450,select=not(mod(n\\,{stride}))','-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
decoder=subprocess.Popen(command,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
frames=[]
for i in range(count):
    raw=decoder.stdout.read(800*450*3);assert len(raw)==800*450*3
    frames.append(Image.frombytes('RGB',(800,450),raw))
decoder.stdout.read();assert decoder.wait()==0
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
pages=[]
for page in range(math.ceil(count/9)):
    sheet=Image.new('RGB',(1500,3*350),'white');draw=ImageDraw.Draw(sheet)
    for cell,im in enumerate(frames[page*9:(page+1)*9]):
        idx=page*9+cell;t=args.start+idx*args.step;x=cell%3*500;y=cell//3*350
        im.save(D/f'{t:.2f}.png');sheet.paste(im.crop((125,100,600,420)),(x+10,y+20))
        draw.text((x+10,y+2),f'{args.id} {t:.2f}s; crop125,100',font=font,fill='black')
        for val in range(150,601,50):
            px=x+10+val-125;draw.line((px,y+20,px,y+30),fill='#00ffff',width=2);draw.text((px-8,y+20),str(val),font=font,fill='white',stroke_width=1,stroke_fill='black')
        for val in range(150,401,50):
            py=y+20+val-100;draw.line((x+10,py,x+20,py),fill='#00ffff',width=2);draw.text((x+10,py),str(val),font=font,fill='white',stroke_width=1,stroke_fill='black')
    f=D/f'page-{page+1}.jpg';sheet.save(f,quality=94);pages.append(f.relative_to(ROOT).as_posix())
(D/'frames.json').write_text(json.dumps({'id':args.id,'source':args.source,'interval':[args.start,args.end],'step':args.step,'coordinatePixels':[800,450],'pages':pages,'manuallyReviewed':False},indent=2)+'\n',encoding='utf8')
print(json.dumps({'id':args.id,'authoringFrames':count,'pages':len(pages)}))
