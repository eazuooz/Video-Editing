"""CPU1 source-cut boundary and completed Manim inspection. Local QA only."""
import pathlib,json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1/math-and-cuts'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
assert not O.exists();O.mkdir(parents=True)
rows=[]
for key,frames in [('04f-p3',711),('04f-p5',754),('09-p7',773)]:
 f=P/f'production/local/beginner-revision-v1/manim/videos/1080p60/{key}.mp4'
 for a in [0,frames//2,frames-1]:rows.append((key+'-'+str(a),f,a/60))
f=R/'production/research/game-lighting-history/local/bethesda-quake2-enhanced-2023.mp4'
for a in [43,43.5,43+59/60,47,47.5,47+59/60,56,57,57+59/60]:rows.append(('q2-'+str(a),f,a))
images=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
for key,f,a in rows:
 out=O/(key+'.png');subprocess.run([FF,'-v','error','-nostdin','-n','-threads','1','-ss',str(a),'-i',str(f),'-frames:v','1','-vf','scale=960:540','-threads','1',str(out)],check=True,creationflags=subprocess.CREATE_NO_WINDOW);images.append((key,out))
boards=[]
for off in range(0,len(images),6):
 b=Image.new('RGB',(1920,1710),'#111');d=ImageDraw.Draw(b)
 for j,(key,f) in enumerate(images[off:off+6]):x=j%2*960;y=j//2*570;b.paste(Image.open(f),(x,y+30));d.text((x+8,y+2),key,fill='white',font=font)
 out=O/f'board-{off//6:02}.jpg';b.save(out,quality=92);boards.append(out.relative_to(R).as_posix())
(O/'index.json').write_text(json.dumps(dict(boards=boards,images=len(images),approved=False),indent=2)+'\n')
print(json.dumps(dict(boards=boards,images=len(images))))
