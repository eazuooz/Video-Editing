"""Temporal sample sheets and exact boundary checks, with explicit review scope."""
from pathlib import Path
import sys,json,subprocess,math,io
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2]
sys.path.insert(0,str(B/'local/pacing-v3/python-deps'))
import render as rr
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
def frame(file,t,width=375):
 data=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(max(0,t)),'-i',str(file),'-frames:v','1','-vf',f'scale={width}:-1','-f','image2pipe','-vcodec','mjpeg','-threads','1','-'])
 return Image.open(io.BytesIO(data)).convert('RGB')
def main(ep,mode):
 row=next(x for x in rr.read(B/'real-clips-v2/review-manifest.json')['records'] if x['id']==ep)
 P=R/'projects'/row['slug'];p=rr.read(P/'production/pacing-v3/edit-plan.json');Q=P/'production/local/pacing-v3/qa';Q.mkdir(exist_ok=True)
 manifest=rr.read(R/p['outputDirectory']/'delivery-manifest.json') if mode=='final' else None
 cap=R/next(f['path'] for f in manifest['files'] if f['kind']=='captioned.mp4') if manifest else None
 rows=[];samples=[];offset=0
 for i,e in enumerate(manifest['events'] if manifest else p['events']):
  if mode=='plan':
   source=R/e['source'];start=e['sourceStartFrame']/60;n=(e['sourceEndFrame']-e['sourceStartFrame'])/60
   times=[start,start+n*.25,start+n*.5,start+max(0,n-1/60)]
  else:
   source=cap;start=(e['pictureAt']+offset)/60;n=e['frames']/60
   times=[max(0,start-1/60),start+min(.45,n*.25),start+n-.03,start+n+.35];offset+=e['frames']
  im=Image.new('RGB',(1500,252),'#101713');d=ImageDraw.Draw(im);d.text((8,4),f'{ep} {i+1:02} {e["key"]} | {e["reason"]}',font=font,fill='#f3dc9b')
  for j,t in enumerate(times):im.paste(frame(source,t),(375*j,38))
  rows.append(im);samples.append(dict(key=e['key'],path=str(source.relative_to(R)),times=times))
 for k in range(math.ceil(len(rows)/5)):
  group=rows[k*5:k*5+5];sheet=Image.new('RGB',(1500,len(group)*252),'#101713')
  for j,im in enumerate(group):sheet.paste(im,(0,j*252))
  sheet.save(Q/f'{mode}-{k:02}.jpg',quality=91)
 rr.save(Q/(mode+'-samples.json'),dict(episode=ep,mode=mode,samples=samples,fullPlayback=False,actualMobileWidth=375,modelVisualInspection='pending'))
 print(ep,mode,'sheets',math.ceil(len(rows)/5),flush=True)
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
