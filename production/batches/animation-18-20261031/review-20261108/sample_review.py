from pathlib import Path
import json,subprocess,hashlib,io,re
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;L=P/'local';L.mkdir(exist_ok=True)
inventory=json.loads((P/'inventory.json').read_text('utf-8'))
times={
'A01':[48,102,187,271,349,447], 'A02':[58,107,167,223,290,334],
'A03':[62,112,159,211,289,341], 'A04':[49,82,109,143,169,196],
'A05':[55,88,118,149,173,204], 'A06':[58,108,137,168,224,264],
'A07':[60,100,139,183,217,252], 'A08':[67,106,143,191,237,279],
'A09':[65,110,158,196,264,322], 'A10':[64,121,150,216,258,356],
'A11':[69,108,141,169,277,331], 'A12':[70,78,93,153,200,261],
'A13':[82,103,147,176,240,289], 'A14':[103,127,175,214,274,337],
'A15':[74,81,133,159,199,228], 'A16':[96,133,153,186,206,239],
'A17':[78,111,166,191,240,270], 'A18':[109,131,199,252,328,375]}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
records=[]
for ep in inventory:
 vid=R/ep['video']['path'];actual=hashlib.file_digest(vid.open('rb'),'sha256').hexdigest();assert actual==ep['video']['sha256'],ep['id']
 sheet=Image.new('RGB',(1920,800),'#101010');d=ImageDraw.Draw(sheet);d.text((15,10),ep['id']+' | '+ep['title'],font=font,fill='white')
 for n,t in enumerate(times[ep['id']]):
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(vid),'-frames:v','1','-vf','scale=640:360','-threads','2','-f','image2pipe','-vcodec','png','-'])
  x=(n%3)*640;y=40+(n//3)*380;sheet.paste(Image.open(io.BytesIO(b)),(x,y));d.text((x+8,y+360),f'{t//60:02d}:{t%60:02d}',font=font,fill='#ffee99')
 out=L/(ep['id']+'-encoded-samples.jpg');sheet.save(out,quality=94)
 records.append({'id':ep['id'],'sha256Verified':actual,'sampleSeconds':times[ep['id']],'contactSheet':str(out.relative_to(R)).replace('\\','/'),'scope':'Targeted encoded stills; does not certify whole-video viewing or human listening.'})
 print(ep['id'],'sampled',flush=True)
(P/'visual-samples.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8')
