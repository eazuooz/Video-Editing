"""Bounded stationary proof of inspected game targets, marks and actual captions."""
from pathlib import Path
import json,subprocess,math,argparse,re
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as a
import video_pipeline as v
HERE=Path(__file__).resolve().parent

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--version',default='v1');args=parser.parse_args()
 if not re.fullmatch(r'[A-Za-z0-9_-]+',args.version):raise ValueError('Unsafe proof version')
 a.require_authorized('bounded-source-annotation-caption-proof')
 plan=a.read(HERE/'edit-plan.draft.json')
 evidence=a.read(HERE/'evidence/annotation-sources-v1/evidence.json')
 destination=HERE/('evidence/annotation-caption-proof-'+args.version)
 destination.mkdir(exist_ok=False)
 selections=[('c019',10.01),('c019',14.014),('c020',16.5),('c020',18.5),('c028',23.990633),('c028',26.493133)]
 rows=[]
 for index,(cid,sourceTime) in enumerate(selections):
  cut=next(x for x in plan['cuts'] if x['id']==cid)
  rec=next(x for x in evidence['records'] if x['source']==cut['source'])
  sourceFrame=min(rec['frames'],key=lambda x:abs(x['seconds']-sourceTime))
  assert abs(sourceFrame['seconds']-sourceTime)<.018
  source=a.repo_path(sourceFrame['path'])
  image=Image.open(source).convert('RGB');assert image.size==(1920,1080)
  base=Image.new('RGB',(1920,1080),'black');x,y,w,h=cut['viewport'];base.paste(image.resize((w,h),Image.Resampling.LANCZOS),(x,y))
  localFrame=round((sourceFrame['seconds']-cut['sourceStart'])*60);globalFrame=cut['startFrame']+localFrame
  raw=destination/f'{index:02d}-raw.png';base.save(raw)
  marks=destination/f'{cid}-marks.ass';marks.write_text(v.annotations(cut,plan)[0],encoding='utf-8')
  target=destination/f'{index:02d}-{cid}.png'
  graph=f'setpts=PTS+{localFrame}/60/TB,ass='+v.filter_path(marks)+f',setpts=PTS+{cut["startFrame"]}/60/TB,ass='+v.filter_path(a.LOCAL/'edit/captions.ko.ass')
  done=subprocess.run([a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(raw),'-vf',graph,'-frames:v','1','-n',str(target)],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if done.returncode:raise RuntimeError(done.stderr.decode('utf8','replace'))
  rows.append({'cut':cid,'localFrame':localFrame,'globalFrame':globalFrame,'source':sourceFrame,'output':a.artifact(target)})
 sheet=Image.new('RGB',(1125,math.ceil(len(rows)/3)*235),'#171717');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
 for i,row in enumerate(rows):
  x,y=i%3*375,i//3*235;image=Image.open(a.repo_path(row['output']['path']));sheet.paste(image.resize((375,211),Image.Resampling.LANCZOS),(x,y+23));draw.text((x+4,y+2),f"{row['cut']} f{row['localFrame']} / {row['globalFrame']/60:.3f}s",font=font,fill='white')
 mobile=destination/'mobile.jpg';sheet.save(mobile,quality=95)
 a.save(destination/'proof.json',{'status':'generated-not-viewed','frames':rows,'mobile':a.artifact(mobile),'scope':'Six inspected source frames and corresponding measured editorial marks/captions only; final moving encoded review remains pending.'})
 print('Six source/mark/caption states ready for bounded direct viewing.')

if __name__=='__main__':main()
