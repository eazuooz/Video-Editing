"""Inspect the actual encoded world/UI and photo cut before the complete pair."""
from pathlib import Path
import json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as a
import video_pipeline as v
H=Path(__file__).resolve().parent

def main():
 a.require_authorized('bounded-actual-encoded-cut-proof')
 plan=a.read(H/'edit-plan.json');out=a.repo_path(plan['outputDir']);root=out/'qa/encoded-cut-preflight-v1'
 root.mkdir(parents=True,exist_ok=False);records={};ass=out/'captions.ko.ass'
 for cid,frames in {'c011':[0,157,266,376,869],'c012':[0,373,374,700,893]}.items():
  cut=next(x for x in plan['cuts'] if x['id']==cid);source=out/(cid+'.mp4');v.assert_video(source,cut['frames'])
  dest=root/cid;dest.mkdir();expr='+'.join(f'eq(n\\,{n})' for n in frames)
  vf='select='+expr+f",setpts=PTS+{cut['startFrame']}/60/TB,ass="+v.filter_path(ass)
  result=subprocess.run([a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(source),'-vf',vf,'-fps_mode','vfr','-frames:v',str(len(frames)),'-n',str(dest/'%03d.png')],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  (dest/'decode.log').write_bytes(result.stderr)
  if result.returncode:raise RuntimeError(result.stderr.decode('utf8','replace'))
  files=sorted(dest.glob('*.png'));assert len(files)==len(frames)
  rows=[{'localFrame':n,'globalFrame':cut['startFrame']+n,'file':a.artifact(f)} for n,f in zip(frames,files)]
  sheet=Image.new('RGB',(1125,math.ceil(len(rows)/3)*240),'#151515');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
  for i,row in enumerate(rows):
   pic=Image.open(a.repo_path(row['file']['path']));assert pic.size==(1920,1080);x,y=i%3*375,i//3*240
   sheet.paste(pic.resize((375,211),Image.Resampling.LANCZOS),(x,y+27));draw.text((x+4,y+4),f"{cid} f{row['localFrame']} | {row['globalFrame']/60:.3f}s",font=font,fill='white')
  mobile=dest/'mobile-375.jpg';sheet.save(mobile,quality=95)
  records[cid]={'encodedCut':a.artifact(source),'cut':cut,'frames':rows,'mobile':a.artifact(mobile)}
 a.save(root/'proof.json',{'status':'extracted-not-viewed','actualCaptionAss':a.artifact(ass),'method':'Exact decoded cut-frame n; unchanged global caption timeline; complete-pair review still pending','cuts':records})
 print('Ten real encoded-cut/caption states extracted; direct1080/375 review pending.')
if __name__=='__main__':main()
