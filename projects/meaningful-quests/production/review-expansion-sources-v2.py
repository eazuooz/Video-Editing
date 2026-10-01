"""Read-only source contact sheets before writing additive game commentary."""
from pathlib import Path
import subprocess, json, io, math, sys
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent/'expanded-source-review-v2'
DEST.mkdir(parents=True, exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
probe_file=DEST/'source-probes.json'
report=json.loads(probe_file.read_text(encoding='utf8')) if probe_file.exists() else []
for raw in sys.argv[1:]:
    file=ROOT/raw
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(file)]))
    seconds=float(meta['format']['duration']); frames=[]
    times=list(range(0, math.ceil(seconds), 4))
    for t in times:
        if t >= seconds-.08: continue
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=384:216','-f','image2pipe','-vcodec','mjpeg','-'])
        frames.append((t,Image.open(io.BytesIO(data)).convert('RGB')))
    sheets=[]
    for page in range(math.ceil(len(frames)/16)):
        chunk=frames[page*16:(page+1)*16]
        sheet=Image.new('RGB',(1536,math.ceil(len(chunk)/4)*244),'white');draw=ImageDraw.Draw(sheet)
        for i,(t,img) in enumerate(chunk):
            x=(i%4)*384;y=(i//4)*244;sheet.paste(img,(x,y));draw.text((x+5,y+216),f'{file.stem}  {t:6.1f}s',fill='black',font=font)
        target=DEST/f'{file.stem}-sheet-{page+1:02d}.jpg';sheet.save(target,quality=91);sheets.append(str(target.relative_to(ROOT)).replace('\\','/'))
    record={'file':raw,'seconds':seconds,'probe':meta,'samples':len(frames),'samplePeriodSeconds':4,'sheets':sheets,'status':'awaiting-direct-action-review'}
    report=[previous for previous in report if previous['file']!=raw]
    report.append(record);print(json.dumps({'file':raw,'seconds':seconds,'sheets':sheets},ensure_ascii=False),flush=True)
(DEST/'source-probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
