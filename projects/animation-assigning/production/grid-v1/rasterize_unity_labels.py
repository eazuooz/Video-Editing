"""Deterministic transparent typography for the isolated Animation Unity stage."""
from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
FONT=Path('C:/Windows/Fonts/malgun.ttf')
def key(text,size,width,height):return hashlib.sha256(f'{text}\n{size}\n{width}\n{height}'.encode('utf-8')).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('request');ap.add_argument('output');a=ap.parse_args()
 req=json.loads(Path(a.request).read_text('utf-8-sig'));out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 scale=2;created=0;skipped=0;fonts={}
 for layout in req['layouts']:
  size,width,height=(layout[k] for k in ('size','width','height'))
  fonts.setdefault(size,ImageFont.truetype(str(FONT),size*scale));font=fonts[size]
  for text in req['texts']:
   if not text:continue
   name=key(text,size,width,height)+'.png';target=out/name
   if target.exists():continue
   im=Image.new('RGBA',(width*scale,height*scale),(255,255,255,0));d=ImageDraw.Draw(im)
   lines=[]
   for paragraph in text.split('\n'):
    line=''
    for ch in paragraph:
     if line and d.textlength(line+ch,font=font)>width*scale-4:
      lines.append(line.rstrip());line=ch.lstrip()
     else:line+=ch
    lines.append(line)
   content='\n'.join(lines);bbox=d.multiline_textbbox((0,0),content,font=font,spacing=2*scale,align='center')
   if len(lines)>2 or bbox[3]-bbox[1]>height*scale-2:
    skipped+=1;continue # Invalid hypothetical layout; actual use will fail clearly.
   x=(width*scale-(bbox[2]-bbox[0]))/2-bbox[0];y=(height*scale-(bbox[3]-bbox[1]))/2-bbox[1]
   d.multiline_text((x,y),content,font=font,fill=(255,255,255,255),spacing=2*scale,align='center')
   im.resize((width,height),Image.Resampling.LANCZOS).save(target);created+=1
 proof={'fontFile':str(FONT),'fontSha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),'fontFamily':'Malgun Gothic','fontStyle':'regular','whiteTextTintedAtRuntime':True,'alignment':'center/center','antialiasScale':scale,'requestSha256':hashlib.sha256(Path(a.request).read_bytes()).hexdigest(),'created':created,'hypotheticalNonfittingLayoutsSkipped':skipped}
 (out/('request-'+proof['requestSha256']+'.json')).write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
if __name__=='__main__':main()
