"""Actual encoded frames, stream clocks and captioned/native-mobile proof."""
from pathlib import Path
import argparse,importlib.util,json,subprocess,time
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_qa_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
D=c.O/'qa';D.mkdir(parents=True,exist_ok=True)

def decode_clock(file,frames):
 name=file.stem;receipt=D/(name+'-decode.json');sig=c.sha(file)
 if receipt.exists():
  r=c.read(receipt)
  if r['sha256']==sig:return r
 probe=c.probe(file);v=next(s for s in probe['streams']if s['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'])==(1920,1080,'60/1','1/60000')
 log=D/(name+'-decode.log');data=D/(name+'-pts.csv')
 with data.open('wb')as out,log.open('wb')as err:
  r=subprocess.run(['ffprobe','-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','csv=p=0',str(file)],stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 assert r.returncode==0 and not log.read_text(encoding='utf8',errors='replace').strip(),log
 actual=[]
 for line in data.read_text().splitlines():
  first=line.split(',')[0]
  if first.lstrip('-').isdigit():actual.append(int(first))
 assert len(actual)==frames,(name,len(actual),frames)
 errors=[dict(frame=i,pts=t,expected=i*1000,delta=t-i*1000)for i,t in enumerate(actual)if t!=i*1000]
 result=dict(file=c.rel(file),sha256=sig,frames=len(actual),width=v['width'],height=v['height'],rate=v['r_frame_rate'],timeBase=v['time_base'],exactFrameClock=not errors,errors=errors[:30],errorCount=len(errors),completeSoftwareDecode=True,decoderThreads=2)
 c.save(receipt,result);return result

def frame(file,f,out):
 if out.exists():return
 out.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-threads','1','-ss',f'{f/60:.9f}','-i',str(file),'-frames:v','1','-update','1',str(out)],check=True,cwd=c.R,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)

def proof():
 t=c.read(H/'timeline.json');plan=c.read(H/'edit-plan.json');master=c.O/'orientation-matrix.captioned.mp4';sig=c.sha(master);folder=D/'visual-proof'/sig[:12];folder.mkdir(parents=True,exist_ok=True);rows=[]
 captions=c.read(c.O/'captions/captions.json')['cues']
 for p in plan['paragraphs']:
  cues=[x for x in captions if x.get('scene')==p['sceneId']and x.get('line')==p['line']]
  if cues:
   cue=max(cues,key=lambda x:len(x['ko']));f=round((cue['start']+cue['end'])*30)
  else:f=(p['startFrame']+p['endFrame'])//2
  out=folder/(p['id']+'.png');frame(master,f,out);im=Image.open(out);mobile=folder/(p['id']+'.mobile.png');im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
  rows.append(dict(id=p['id'],frame=f,file=c.rel(out),mobile=c.rel(mobile),sha256=c.sha(out),actualCaptionedMaster=True))
 for start in range(0,len(rows),8):
  im=Image.new('RGB',(1500,882),'#242424');d=ImageDraw.Draw(im)
  for j,r in enumerate(rows[start:start+8]):
   x=j%2*750;y=j//2*220;thumb=Image.open(c.R/r['file']);thumb.thumbnail((375,211));im.paste(thumb,(x+375,y+9));im.paste(Image.open(c.R/r['mobile']),(x,y+9));d.text((x,y),r['id'],fill='white')
  im.save(folder/f'contact-{start//8:02}.jpg')
 c.save(D/'visual-proof.json',dict(masterSha256=sig,rows=rows,contactDirectory=c.rel(folder),generatedFromEncodedMaster=True,actualHumanReview='pending',motionReview='pending'))
 print('Generated',len(rows),'actual captioned paragraph images and375px proofs')

def main():
 a=argparse.ArgumentParser();a.add_argument('--decode',action='store_true');a.add_argument('--proof',action='store_true');x=a.parse_args()
 if x.decode:
  t=c.read(H/'timeline.json');results=[]
  for kind in ['clean','captioned']:
   r=decode_clock(c.O/('orientation-matrix.'+kind+'.mp4'),t['totalFrames']);results.append(r);print(kind,r['frames'],r['errorCount'],'clock errors',flush=True)
  c.save(D/'decode-clock.json',dict(results=results,allExact=all(r['exactFrameClock']for r in results)));assert all(r['exactFrameClock']for r in results),'Inspect actual concat PTS before correcting, without changing decoded content'
 if x.proof:proof()
if __name__=='__main__':main()
