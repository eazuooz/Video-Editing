"""Add production-caption geometry to the silent six-second visual prototype."""
from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[4]
H=Path(__file__).resolve().parent
M=H.parent/'local/grid-v1'
out=M/'preview';out.mkdir(parents=True,exist_ok=True)
source=M/'render/prototype-v2/pose-versus-motion/unity.mp4'
assert source.is_file()
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans KR,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for start,end,text in [('0:00:00.00','0:00:03.00','한 순간의 자세를 포즈라고 합니다.'),('0:00:03.00','0:00:06.00','그 자세가 시간에 따라 이어지면 애니메이션입니다.')]:
 width=1200 if start.endswith('03.00') else 900;x=(1920-width)//2
 for layer,xx,yy,tags in [(0,x+14,942,r'\bord0\shad0\1c&H323C07&'),(1,x,928,r'\bord3\shad0\1c&HFFFFFF&\3c&H181B16&')]:
  ass+=f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{{\\an7\\pos({xx},{yy})\\p1{tags}}}m 0 0 l {width} 0 {width} 84 0 84\n'
 ass+=f'Dialogue: 2,{start},{end},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0\\b500}}{text}\n'
(out/'preview.ass').write_text(ass,encoding='utf8')
movie=out/'animation-grid-prototype.captioned.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(source),'-vf','ass=preview.ass','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],cwd=out,check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),'-f','null','-'],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(movie),'-vf','fps=4,scale=640:360,tile=4x6','-frames:v','1',str(out/'motion-contact.jpg')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-ss','3.5','-i',str(movie),'-frames:v','1',str(out/'frame-fhd.png')],check=True)
Image.open(out/'frame-fhd.png').resize((375,211),Image.Resampling.LANCZOS).save(out/'frame-mobile375.png')
receipt={'prototypeOnly':True,'speechGenerated':False,'durationSeconds':6,'dimensions':[1920,1080],'fps':60,'source':str(source),'captioned':str(movie),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'decode':'passed all360frames','humanReview':False,'visualInspection':'pending moving contact and mobile checks','nativeScene':'Assets/VideoScenes/animation-assigning/grid-v1/RenderRevisions/prototype-v2/pose-versus-motion.unity'}
(H/'grid-preview-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'movie':str(movie),'sha256':receipt['sha256']}))
