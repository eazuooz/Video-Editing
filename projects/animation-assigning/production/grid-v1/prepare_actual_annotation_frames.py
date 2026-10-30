"""Bounded source-image evidence for editorial target tracking, not CV output."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as ap
H=Path(__file__).resolve().parent

def main():
 plan=ap.read(H/'measured-edit-plan.proposal.json')
 cuts=[c for c in plan['cuts'] if c['kind']=='independent-gameplay']
 out=H.parent/'local/grid-v1/preflight/actual-targets-v1';out.mkdir(parents=True,exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 manifest=[]
 for c in cuts:
  duration=c['frames']/60
  times=[0,(duration-1/60)*.25,(duration-1/60)*.5,(duration-1/60)*.75,duration-1/60]
  source=ap.repo_path(c['sourceFile']);assert ap.sha(source)==c['sourceSha256']
  sheet=Image.new('RGB',(1200,520),'#202626');d=ImageDraw.Draw(sheet)
  for i,t in enumerate(times):
   p=out/(c['id']+f'-{i}.png')
   if not p.exists():ap.run_ff(['-ss',float(c['sourceStart'])+t,'-i',source,'-frames:v',1,p],out/(c['id']+f'-{i}.log'))
   im=Image.open(p).convert('RGB');x,y=i%3*400,i//3*260
   sheet.paste(im.resize((400,225)),(x,y+30));d.text((x+5,y+3),c['id']+f' t={t:.3f}',font=font,fill='white')
   manifest.append({'cut':c['id'],'localTime':t,'sourceTime':float(c['sourceStart'])+t,'image':ap.artifact(p)})
  sheet.save(out/(c['id']+'.jpg'))
 ap.save(out/'frames.json',manifest);print('15 source tracking sheets ready')

if __name__=='__main__':main()
