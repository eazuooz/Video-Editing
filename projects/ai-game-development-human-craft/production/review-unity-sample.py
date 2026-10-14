"""Contact sheets of the current encoded sample, plus exact cut/action frames."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'shared/output/ai-game-development-human-craft/unity-sample'
VIDEO = ROOT / 'shared/output/motion-canvas/ai-human-craft-unity-sample-v1.mp4'
OUT.mkdir(parents=True, exist_ok=True)
frames = sorted(set(range(0, 1560, 30)) | {215,216,275,276,335,336,337,353,354,438,486,659,660,661,875,876,935,936,995,996,997,1013,1014,1319,1320,1559})
select = '+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(VIDEO),'-vf',f"select='{select}'",'-fps_mode','vfr',str(OUT/'encoded-%03d.png')],check=True)
files = sorted(OUT.glob('encoded-*.png'))
assert len(files) == len(frames), (len(files), len(frames))
for part in range(0,len(files),40):
    group=files[part:part+40]
    sheet=Image.new('RGB',(1920,((len(group)+3)//4)*290),'#172023')
    draw=ImageDraw.Draw(sheet)
    for j,file in enumerate(group):
        x=(j%4)*480;y=(j//4)*290
        im=Image.open(file).convert('RGB');im.thumbnail((480,270))
        sheet.paste(im,(x,y));draw.text((x+6,y+271),f"frame {frames[part+j]} / {frames[part+j]/60:.3f}s",fill='white')
    sheet.save(OUT/f'encoded-contact-{part//40+1}.jpg',quality=90)
(OUT/'encoded-review-frames.json').write_text(json.dumps({'video':str(VIDEO),'frames':frames,'method':'2fps full sample plus exact animation/transaction/cut boundaries'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(frames),'sheets':(len(frames)+39)//40}))
