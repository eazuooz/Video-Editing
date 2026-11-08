"""Verify the delivered frame/audio contract and sample only the changed areas."""
from pathlib import Path
import json,sys,subprocess,hashlib,math,importlib.util
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'

def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args):return subprocess.run([str(x) for x in args],capture_output=True,encoding='utf-8',errors='replace',check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]).stdout)
def aac_hash(p):return run(['ffmpeg','-nostdin','-v','error','-i',p,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()

def main(id):
 ep=next(e for e in read(H/'planning/relations-plan.json')['episodes'] if e['id']==id)
 O=R/'projects'/ep['slug']/'production/local/relations-v4';a=read(O/'assembly.json');V=O/'rendered';Q=O/'qa';Q.mkdir(exist_ok=True)
 results={};files=[]
 for kind in ['clean.mp4','captioned.mp4']:
  f=V/(ep['slug']+'.'+kind);info=probe(f);v=next(s for s in info['streams'] if s['codec_type']=='video');au=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',a['totalFrames']),(id,kind,v)
  assert int(au['sample_rate'])==48000 and au['channels']==2
  decode=run(['ffmpeg','-nostdin','-v','error','-threads','4','-i',f,'-map','0:v:0','-map','0:a:0','-f','null','-']);assert not decode.stderr.strip(),(id,kind,decode.stderr)
  rows=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts,dts,duration','-of','csv=p=0',f]).stdout.strip().splitlines()
  assert len(rows)==a['totalFrames']
  for i,row in enumerate(rows):assert list(map(int,row.split(',')[:3]))==[i*1000,i*1000,1000],(id,kind,i,row)
  hash=sha(f);files.append({'kind':kind,'path':f.relative_to(R).as_posix(),'sha256':hash,'bytes':f.stat().st_size})
  results[kind]={'sha256':hash,'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'fullDecode':'pass','uniformFrameTimestamps':True,'aacHash':aac_hash(f)}
 assert results['clean.mp4']['aacHash']==results['captioned.mp4']['aacHash']
 for lang in ['ko','en']:
  f=V/(ep['slug']+'.'+lang+'.srt');files.append({'kind':lang+'.srt','path':f.relative_to(R).as_posix(),'sha256':sha(f),'bytes':f.stat().st_size})
 # Only measure the final audio once; the two MP4s carry identical AAC packets.
 cap=V/(ep['slug']+'.captioned.mp4')
 meter=run(['ffmpeg','-nostdin','-hide_banner','-i',cap,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
 loud=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1]);assert float(loud['input_tp'])<=-.9,(id,'Unexpected audio peak',loud)
 tm=next(e for e in read(L/'timing.json')['episodes'] if e['id']==id)
 at=a['insertion']['pictureFrame']/60
 points=[('map-start',at+.35),('map-early',at+(tm['sentences'][0]['start']+tm['sentences'][0]['end'])/2),('map-middle',at+tm['duration']*.55),('map-final',at+tm['duration']-.3),('before-map',max(0,at-.3)),('after-map',at+tm['duration']+.3)]
 edit=read(O/'opening-edl.json');studies=[p for p in edit['pictureEdl'] if 'passIndex' in p]
 for i,p in enumerate(studies):points.append((f"native-{i+1}-{p['passIndex']}of3",(p['outputStartFrame']+min(p['frames']/2,45))/60))
 if studies:points.append(('return-to-body',studies[-1]['outputEndFrame']/60+.3))
 for r in a.get('bodyRepairs',[]):
  # Assembly records the final mapped picture start/end for changed body ranges.
  x=r.get('finalStartFrame');y=r.get('finalEndFrame')
  if x is not None and y is not None:
   for t in [.15,.5,.85]:points.append((r.get('kind','repair')+str(t),(x+(y-x)*t)/60))
 samples=[]
 for label,t in points:
  p=Q/(label+'.png');run(['ffmpeg','-nostdin','-v','error','-y','-threads','2','-ss',t,'-i',cap,'-frames:v','1',p]);samples.append({'label':label,'time':t,'path':str(p)})
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 sheets=[]
 for width,stem in [(768,'encoded-sheet'),(375,'mobile-sheet')]:
  for offset in range(0,len(samples),6):
   group=samples[offset:offset+6];height=round(width*1080/1920);sheet=Image.new('RGB',(width*2,(height+32)*math.ceil(len(group)/2)),(35,35,35));d=ImageDraw.Draw(sheet)
   for i,s in enumerate(group):
    x=i%2*width;y=i//2*(height+32);im=Image.open(s['path']).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);sheet.paste(im,(x,y));d.text((x+8,y+height+5),f"{id} {s['label']} {s['time']:.2f}s",font=font,fill='white')
   name=stem+('' if offset==0 else '-'+str(offset//6+1))+'.jpg';sheet.save(Q/name,quality=94);sheets.append(str(Q/name))
 report={'id':id,'revision':'relations-v4','status':'technical-checks-passed-visual-review-pending','files':files,'videoChecks':results,'loudnessMeasuredOnly':loud,'unchangedBodyAudio':a['audioProof'],'sampledFrames':samples,'sampleSheets':sheets,'humanViewed':False,'humanListened':False,'platformChanged':False}
 save(O/'qa.json',report);print(id,'technical verification passed; encoded visual review still required',flush=True)
if __name__=='__main__':main(sys.argv[1])
