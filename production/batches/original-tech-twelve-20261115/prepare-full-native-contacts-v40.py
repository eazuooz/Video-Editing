from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[5];D=ROOT/'shared/output/original-tech-twelve-20261115';R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z')
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['temporal','remaining-seven'],required=True);a=p.parse_args();base=D/('shorts-inside-temporal-antialiasing/native-completion-v6'if a.case=='temporal'else'remaining-seven/native-reviewed-pose-v35');proof=base/'accepted-full.json';d=json.loads(proof.read_text(encoding='utf8'));assert d['actualUnityCapture']and d['framesPerCamera']==720 and d['allPixelsRoundTripVerified'];rows=[];items=[]
 for c in d['clips']:
  for f in([0,180,420,719]if a.case=='temporal'else[0,120,240,420,719]):
   ref=next(x for x in c['referenceFrames']if Path(x['path']).name==f'reference-{f:05}.png');path=Path(ref['path']);assert pin(path)==ref;items.append((str(c.get('topic')or'')+' '+c['mode']+' '+c['camera']+' '+str(f),Image.open(path).convert('RGB').resize((375,375),Image.Resampling.LANCZOS)));rows.append(dict(topic=c.get('topic'),mode=c['mode'],camera=c['camera'],frame=f,source=ref))
 contacts=[]
 for start in range(0,len(items),12):
  im=Image.new('RGB',(1500,1215),'#11221a');draw=ImageDraw.Draw(im)
  for i,(label,pic)in enumerate(items[start:start+12]):x=i%4*375;y=i//4*405;im.paste(pic,(x,y+30));draw.text((x+4,y+5),label,fill='white')
  out=R/f'{a.case}-full-v40-contact-{start//12}.jpg';assert not out.exists();im.save(out,quality=94);contacts.append(pin(out))
 out=R/(a.case+'-full-visual-inputs-v40.json');assert not out.exists();out.write_text(json.dumps(dict(fullProof=pin(proof),frames=rows,contacts=contacts,visualReviewStillRequired=True),indent=2)+'\n','utf8');print(json.dumps(dict(inputs=pin(out),frames=len(rows),contacts=contacts)))
if __name__=='__main__':main()
