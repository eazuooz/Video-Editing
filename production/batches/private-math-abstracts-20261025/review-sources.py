from pathlib import Path
import json,subprocess,hashlib,io
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/VideoEditing');B=R/'production/batches/private-math-abstracts-20261025';cache={};font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for pp in sorted((B/'plans').glob('*.json')):
 p=json.loads(pp.read_text('utf8'));work=Path(p['work']);work.mkdir(parents=True,exist_ok=True);rows=[];sheet=Image.new('RGB',(1920,248*len(p['segments'])),'#111611');draw=ImageDraw.Draw(sheet)
 for n,s in enumerate(p['segments']):
  src=R/s['source']
  if s['source'] not in cache:
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert v['width']>=1920 and v['height']>=1080
   cache[s['source']]=dict(sha256=hashlib.file_digest(src.open('rb'),'sha256').hexdigest(),width=v['width'],height=v['height'],fps=v['r_frame_rate'],seconds=float(probe['format']['duration']))
  s['sourceProbe']=cache[s['source']];assert s['sourceOut']<=s['sourceProbe']['seconds']
  for i,dt in enumerate([.2,s['seconds']*.25,s['seconds']*.5,s['seconds']*.75,s['seconds']-.2]):
   t=s['sourceIn']+dt;raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=384:216','-f','image2pipe','-vcodec','png','pipe:1']);im=Image.open(io.BytesIO(raw)).convert('RGB');x=i*384;y=n*248;sheet.paste(im,(x,y+30));draw.text((x+4,y+4),f'{n}: {s["game"]} {t:.2f}s',fill='white',font=font)
  rows.append(dict(index=n,game=s['game'],sourceIn=s['sourceIn'],sourceOut=s['sourceOut']))
 file=work/'source-contact.png';sheet.save(file);p['sourceContact']=str(file);save(pp,p);print(p['id'],str(file),flush=True)
