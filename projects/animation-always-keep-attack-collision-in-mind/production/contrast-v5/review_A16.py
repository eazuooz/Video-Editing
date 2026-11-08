"""Encoded A16 interval samples. CPU only; no full watch/listen claim."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
H=ROOT/'production/batches/animation-18-20261031/contrast-v5';OUT=Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review/A16')
LOCAL=H/'local/explanation-assembly/A16';QA=H/'local/final-encode/A16/qa'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 d=read(OUT/'delivery.json');edl=read(LOCAL/'edl.json');p=Path(next(x['path']for x in d['files']if x['kind']=='captioned.mp4'));assert sha(p)==next(x['sha256']for x in d['files']if x['kind']=='captioned.mp4')
 QA.mkdir(parents=True,exist_ok=True)
 samples=[]
 for i,r in enumerate(edl['pictureEdl']):
  frame=(r['outputStartFrame']+r['outputEndFrame']-1)//2
  samples.append({'index':i+1,'frame':frame,'seconds':frame/60,'id':r['id'],'kind':r['kind'],'source':r['source'],'sourceFrame':r['sourceStartFrame']+frame-r['outputStartFrame']})
 filt='select='+ '+'.join('eq(n\\,'+str(x['frame'])+')'for x in samples)
 subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-threads','4','-i',str(p),'-filter_threads','1','-vf',filt,'-fps_mode','vfr','-q:v','3',str(QA/'interval-%03d.jpg')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',16)
 sheets=[]
 for start in range(0,len(samples),12):
  canvas=Image.new('RGB',(1500,741),'#101316');draw=ImageDraw.Draw(canvas)
  for k,s in enumerate(samples[start:start+12]):
   file=QA/f"interval-{s['index']:03}.jpg";im=Image.open(file);assert im.size==(1920,1080)
   small=im.resize((375,211));small.save(QA/f"interval-{s['index']:03}-375.png")
   x=(k%4)*375;y=(k//4)*247;canvas.paste(small,(x,y));draw.text((x+6,y+214),f"{s['index']:02d} {s['seconds']:.3f}s {s['id'][:21]}",font=font,fill='white')
   s['frameFile']=str(file);s['frameSha256']=sha(file);s['mobileFile']=str(QA/f"interval-{s['index']:03}-375.png")
  dest=QA/f'contact-{start//12+1:02}.jpg';canvas.save(dest,quality=92);sheets.append(str(dest))
 report={'id':'A16','captionedMasterSha256':sha(p),'frames':edl['frames'],'encodedIntervalSamples':samples,'contactSheets':sheets,
  'samplingScope':'One exact midpoint frame from every final picture EDL interval, actual burned captions included, with375px derivatives.',
  'modelVisualInspection':'pending','humanFullWatch':False,'humanFullListening':False,'nativeGameplayFrames':3856,
  'bodyFramesExcludingBrandingAndMember':edl['frames']-120-600,'nativeGameplayBodyShare':3856/(edl['frames']-120-600),
  'audio':'Exact prior full voice+Nimbus PCM retained. No unreviewed external source audio added.',
  'technicalDelivery':str(OUT/'delivery.json'),'sourcePublicationConditions':'production/batches/animation-18-20261031/contrast-v5/footage/final-audio-adoption.json'}
 save(HERE/'encoded-review.json',report);print('A16 samples',len(samples),str(QA),flush=True)
if __name__=='__main__':main()
