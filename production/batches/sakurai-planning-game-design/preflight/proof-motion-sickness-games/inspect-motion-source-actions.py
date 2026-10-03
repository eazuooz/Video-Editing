"""Research contact sheets of acquired existing-game footage. Not final cuts."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
sources = [
    ('PF5L_2g9UVQ', sorted(set(list(range(48, 69, 3)) + list(range(99, 138, 3)) +
      list(range(149, 167, 2)) + list(range(169, 197, 3)) + list(range(301, 324, 3)) +
      list(range(345, 378, 5)) + list(range(408, 553, 12))))),
    ('6slinvkF0Rs', list(range(0, 74, 2))),
]
for source_id, times in sources:
    source = BASE / 'game-research' / f'{source_id}.mp4'
    out = BASE / 'game-research' / f'{source_id}-action-review'
    out.mkdir(parents=True, exist_ok=True)
    if source_id == '6slinvkF0Rs':
        decode = subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(source),'-f','null','-'],capture_output=True,text=True)
        (out/'full-decode.log').write_text(decode.stderr,'utf-8')
        if decode.returncode: raise RuntimeError(decode.stderr)
    for t in times:
        frame = out / f'{t:04}.jpg'
        if not frame.exists():
            subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=480:270','-q:v','2','-y',str(frame)],check=True)
    for page in range((len(times)+11)//12):
        sheet = Image.new('RGB',(1440,4*302),'white')
        draw = ImageDraw.Draw(sheet)
        for j,t in enumerate(times[page*12:(page+1)*12]):
            x,y = (j%3)*480,(j//3)*302
            sheet.paste(Image.open(out/f'{t:04}.jpg'),(x,y))
            draw.text((x+8,y+277),f'{source_id}  {t//60:02}:{t%60:02} ({t}s)',fill='black')
        sheet.save(out/f'contact-{page+1}.jpg',quality=93)
    (out/'review.json').write_text(json.dumps({'sourceId':source_id,'sampleSeconds':times,
      'fullDecode': {'exitCode':0,'errorBytes':len(decode.stderr)} if source_id=='6slinvkF0Rs' else {'evidence':'../pws-preview-review/review.json'},
      'manualActionReview':'pending','finalCutApproval':False},indent=2)+'\n','utf-8')
    print(source_id,len(times),'research samples ready',flush=True)
