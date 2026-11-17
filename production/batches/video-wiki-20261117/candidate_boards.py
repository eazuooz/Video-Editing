"""QA contact sheets of unchanged actual video frames (not public media edits)."""
import json,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;E=P/'evidence'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
def boards(rows,prefix,portrait=False):
 for offset in range(0,len(rows),6):
  group=rows[offset:offset+6];w=630;h=400 if not portrait else 600
  sheet=Image.new('RGB',(w*3,h*2),'#222222');d=ImageDraw.Draw(sheet)
  for k,r in enumerate(group):
   im=Image.open(r['path']);im.thumbnail((w-16,h-45));x=(k%3)*w+(w-im.width)//2;y=(k//3)*h+40
   sheet.paste(im,(x,y));d.text(((k%3)*w+8,(k//3)*h+8),r['article']+' '+str(round(r['seconds'],2))+'s',font=font,fill='white')
  sheet.save(E/f'{prefix}-{offset//6+1}.jpg',quality=88)

if __name__=='__main__':
 rows=[]
 for n in range(4,19):
  ident=f'A{n:02}';d=json.loads((P/'drafts'/f'{ident}.json').read_text(encoding='utf8'));qa=Path(f'C:/Users/1/Videos/YamyamProduction/animation-gameplay-v8/{ident}/encoded-qa')
  if not (qa/'frames.json').exists():continue
  q=json.loads((qa/'frames.json').read_text(encoding='utf8'))
  choices=[d['sections'][1],d['sections'][max(2,len(d['sections'])//2)]]
  for sec in choices:
   target=sec['seconds']+8;sample=min(q['samples'],key=lambda s:abs(s['frame']/60-target));path=Path(sample['path']);dst=E/f'{ident}-{sample["frame"]}-selected.jpg';shutil.copyfile(path,dst)
   rows.append(dict(article=ident,path=str(dst),file=str(dst),seconds=sample['frame']/60,frame=sample['frame'],masterSha256=q['movieSha256'],sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),beforeHeading='## '+sec['title'],sourceFramePath=str(path)))
 (P/'animation-more-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');boards(rows,'animation-more')
 ds=json.loads((P/'design-capture-progress.json').read_text(encoding='utf8'));rs=[dict(r,article=i) for i,r in ds.items() if r.get('path')];boards(rs,'design-more')
 print(len(rows),'animation /',len(rs),'design candidates')
