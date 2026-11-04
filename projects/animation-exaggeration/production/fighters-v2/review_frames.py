"""Real decoded pixels, contact sheets and full-resolution caption inspection frames."""
from pathlib import Path
import json,subprocess,sys,io
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def frame(file,t,width=640,filters=''):
 vf=(filters+',' if filters else '')+f'scale={width}:-1'
 raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-vf',vf,'-f','image2pipe','-vcodec','png','-threads','1','-'])
 return Image.open(io.BytesIO(raw)).convert('RGB')
def sheets(items,directory,prefix,cols=3,rows=4):
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
 for off in range(0,len(items),cols*rows):
  batch=items[off:off+cols*rows];w,h=batch[0][1].size
  image=Image.new('RGB',(w*cols,(h+26)*((len(batch)+cols-1)//cols)),'#161616');d=ImageDraw.Draw(image)
  for i,(label,pic) in enumerate(batch):
   x=(i%cols)*w;y=(i//cols)*(h+26);image.paste(pic,(x,y));d.text((x+6,y+h+3),label,font=font,fill='white')
  out=directory/f'{prefix}-{off//(cols*rows)+1:02}.jpg';image.save(out,quality=90);print(out)
def main():
 mode=sys.argv[1];p=load(H/'edit-plan.json');out=L/'qa'/mode;out.mkdir(parents=True,exist_ok=True);items=[]
 if mode=='preflight':
  samples=[('A02-F11',5),('A02-F12',1.96),('A02-F22',2),('A02-F23',2),('A02-F31',2.3),('A02-F32',2.7),('A02-E024',2),('A02-E013',5)]
  for cid,t in samples:
   c=next(c for c in p['cuts'] if c['id']==cid);g=c['startFrame']/60+t
   # This is a preflight cut composed with the actual global caption clock.
   ass_path=(L/'edit/captions.ko.ass').as_posix().replace(':','\\:')
   filters=f"setpts=PTS+{g}/TB,ass='{ass_path}'"
   pic=frame(L/f'edit/{cid}.mp4',t,960,filters);pic.save(out/f'{cid}.png');items.append((f'{cid} global {g:.2f}s',pic))
  sheets(items,out,'samples',2,2)
 elif mode=='final':
  video=L/'edit/animation-exaggeration-captioned.mp4';cues=load(L/'edit/captions.json')['cues']
  for c in p['cuts']:
   t=(c['startFrame']+c['frames']/2)/60;pic=frame(video,t);items.append((f'{c["id"]} {t:.2f}s',pic))
  sheets(items,out,'scenes',3,3);items=[]
  for c in cues:
   t=(c['start']+c['end'])/2;pic=frame(video,t,1920).crop((120,875,1800,1080));pic=pic.resize((840,102))
   items.append((f'cue{c["cue"]} {t:.2f}s',pic))
  sheets(items,out,'captions',2,10)
  for cid,t in [('A02-F11',5),('A02-F12',1.96),('A02-F23',2),('A02-F31',2.3),('A02-F32',2.7),('A02-E024',2)]:
   c=next(c for c in p['cuts'] if c['id']==cid);g=c['startFrame']/60+t;pic=frame(video,g,1920);pic.save(out/f'{cid}-fhd.png');pic.resize((375,211)).save(out/f'{cid}-mobile.png')
  (out/'extraction.json').write_text(json.dumps({'cutMidpoints':len(p['cuts']),'captionMidpoints':len(cues),'fullResolutionAndMobileFrames':6,'source':str(video),'note':'Actual final decoded pixels; sampled inspection is not full human viewing.'},indent=2),encoding='utf-8')
 else:raise ValueError(mode)
if __name__=='__main__':main()
