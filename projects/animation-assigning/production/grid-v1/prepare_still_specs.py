"""Inspect source frames before choosing explanation crops and overlays."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as ap
H=Path(__file__).resolve().parent
L=H.parent/'local/grid-v1'

def main():
 plan=ap.read(H/'measured-edit-plan.proposal.json')
 rows=plan['stillCompositionQueue'];cuts={c['id']:c for c in plan['cuts']}
 out=L/'preflight/source-stills-v1';out.mkdir(parents=True,exist_ok=True)
 sheet=Image.new('RGB',(1200,280*((len(rows)+2)//3)), '#202626')
 draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
 evidence=[]
 for i,row in enumerate(rows):
  cut=cuts[row['id']];target=out/(row['id']+'.png')
  source=ap.repo_path(cut['sourceFile']);assert ap.sha(source)==cut['sourceSha256']
  if not target.exists():ap.run_ff(['-ss',row['sourceStillTimestamp'],'-i',source,'-frames:v',1,target],out/(row['id']+'.log'))
  im=Image.open(target).convert('RGB');assert min(im.size)>=1080
  x,y=(i%3)*400,(i//3)*280
  sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y+45))
  draw.text((x+6,y+7),row['id']+' '+row['source']+' '+str(row['sourceStillTimestamp']),font=font,fill='white')
  evidence.append({'cut':row['id'],'image':ap.artifact(target),'sourceFile':cut['sourceFile'],'sourceSha256':cut['sourceSha256'],'sourceTime':row['sourceStillTimestamp']})
 sheet.save(out/'contact.jpg');ap.save(out/'frames.json',evidence)
 print(out/'contact.jpg')

if __name__=='__main__':main()
