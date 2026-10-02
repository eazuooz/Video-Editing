from pathlib import Path
import subprocess,json,io,concurrent.futures,sys
from PIL import Image,ImageDraw
W=Path(__file__).resolve().parent;R=W.parents[3];P=json.loads((W/'plan.json').read_text(encoding='utf-8'));O=W/'source-review'
jobs=[(c['id'],c['sourceIn'],c['sourceOut']) for c in P['cuts'] if c['key']=='tetris']+[('candidateA',350,380),('candidateB',600,630),('candidateC',700,745)]
final='--final' in sys.argv
if final:jobs=[(c['id'],0,c['seconds']) for c in P['cuts'] if c['key']=='tetris']
def get(j):
    name,a,b=j
    file=W/'cuts'/f'{name}.mp4' if final else R/'shared/assets/blank-project-coding/original-restored-v2/raw/tetris.mp4'
    raw=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(a),'-i',str(file),'-t',str(b-a),'-vf','fps=2,scale=320:180','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-'])
    return [(Image.frombytes('RGB',(320,180),raw[k:k+172800]),f'{name} src {a+i*.5:.2f}') for i,k in enumerate(range(0,len(raw),172800))]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:frames=[x for row in ex.map(get,jobs) for x in row]
for start in range(0,len(frames),48):
    page=Image.new('RGB',(1920,1600),'white');draw=ImageDraw.Draw(page)
    for i,(im,label) in enumerate(frames[start:start+48]):
        x=i%6*320;y=i//6*200;page.paste(im,(x,y));draw.text((x+4,y+181),label,fill='black')
    page.save(O/f'tetris-{"final" if final else "dense"}-{start//48+1:02d}-contact.jpg',quality=95)
print(len(frames),'frames', (len(frames)+47)//48,'pages')
