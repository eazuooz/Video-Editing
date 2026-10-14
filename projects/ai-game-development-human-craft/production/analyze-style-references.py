"""Local research-only filmstrips; reference footage never enters production cuts."""
from pathlib import Path
import json, subprocess, hashlib, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'shared/sources/style-references/jeose-sang-developer'
OUT = ROOT / 'shared/output/style-references/jeose-sang-developer'
OUT.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 19)
records = []
for vid in ['eHn7TLjzVFU', 'IQVeIrF3KfE', 'xNp8De8CEoI']:
    path = SOURCE / f'{vid}.mp4'
    info = json.loads((SOURCE / f'{vid}.info.json').read_text(encoding='utf-8'))
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    duration = float(probe['format']['duration'])
    frames = OUT / vid
    frames.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(path),'-vf','fps=1/3,scale=240:-1',str(frames/'%03d.jpg')],check=True)
    paths = sorted(frames.glob('*.jpg'))
    cell_w, cell_h, cols = 244, 454, 6
    sheet = Image.new('RGB',(cols*cell_w, math.ceil(len(paths)/cols)*cell_h),'#20242a')
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate(paths):
        x,y = (i%cols)*cell_w,(i//cols)*cell_h
        im = Image.open(frame)
        sheet.paste(im,(x,y+25))
        draw.text((x+5,y+2),f'{i*3+1.5:04.1f}s',font=font,fill='white')
    sheet_path = OUT / f'{vid}-filmstrip.jpg'
    sheet.save(sheet_path,quality=92)
    records.append({'videoId':vid,'url':f'https://www.youtube.com/shorts/{vid}','title':info['title'],'uploader':info.get('uploader'),'description':info.get('description'),'durationSeconds':duration,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sourceRole':'research-reference-only','productionReuse':False,'filmstrip':str(sheet_path),'sampling':'fps=1/3; labels show nominal bin centers, not frame-exact event measurements'})
(OUT/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'id':r['videoId'],'seconds':r['durationSeconds'],'filmstrip':r['filmstrip']} for r in records],ensure_ascii=False))
