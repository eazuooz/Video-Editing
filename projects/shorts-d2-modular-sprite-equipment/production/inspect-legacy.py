"""Bounded CPU inspection of publisher-distributed legacy gameplay captures."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'local/legacy-review'
OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'production/batches/distinctive-ten-shorts-20261025/local/d2r-official/comparison'
for scene in ['tristram','barracks']:
    source=BASE/f'{scene}_old_comparison_slider.mp4'
    folder=OUT/scene;folder.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-n','-threads','1','-i',str(source),'-vf','fps=2,scale=960:540','-q:v','2','-threads','1',str(folder/'%03d.jpg')],check=True)
    canvas=Image.new('RGB',(1920,870),'black');draw=ImageDraw.Draw(canvas)
    for n,p in enumerate(sorted(folder.glob('*.jpg'))):
        im=Image.open(p);im.thumbnail((480,270));x=n%4*480;y=n//4*290
        canvas.paste(im,(x,y));draw.text((x+8,y+270),f'{scene} original {n/2:.1f}s',fill='white')
    canvas.save(OUT/f'{scene}.jpg',quality=94)
print(json.dumps({'output':str(OUT),'reviewSamplingFps':2,'scope':'all 6 seconds sampled; actual visual review must be recorded separately'}))
