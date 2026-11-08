from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v4-video';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video');Q=O/'qa';Q.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace',check=True,creationflags=subprocess.CREATE_NO_WINDOW)
tm=read(L/'timeline.json');assembly=read(H/'assembly.json');cap=Path(assembly['files'][1]['path']);clean=Path(assembly['files'][0]['path'])
checks=[]
for f in [clean,cap]:
 probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',f]).stdout);v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',tm['frames']),probe;assert abs(float(probe['format']['duration'])-tm['duration'])<.06,probe
 checks.append({'file':str(f),'sha256':sha(f),'probe':probe})
# Decode the final encoded artifact once, including audio. No redundant full renders.
decode=run(['ffmpeg','-hide_banner','-v','error','-threads','2','-i',cap,'-f','null','-']);assert not decode.stderr.strip(),decode.stderr
audio_hashes=[]
for f in [clean,cap]:
 result=run(['ffmpeg','-v','error','-i',f,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']);audio_hashes.append(result.stdout.strip())
assert audio_hashes[0]==audio_hashes[1]
changed={s['id'] for s in assembly['sources'] if s['changed']};samples=[]
for row in tm['scenes']:
 fractions=[.22,.68] if row['id'] in changed else [.5]
 for fraction in fractions:
  sec=row['start']+row['duration']*fraction;name=f"{row['id']}-{round(fraction*100)}.jpg";dest=Q/name
  run(['ffmpeg','-hide_banner','-loglevel','error','-ss',f'{sec:.6f}','-i',cap,'-frames:v','1','-q:v','2','-update','1','-y',dest]);samples.append({'id':row['id'],'time':sec,'file':str(dest),'changed':row['id'] in changed})
  if row['id'] in ['01','R16','V33','V34','V35','W36'] and fraction==.68:
   with Image.open(dest) as im:im.resize((375,211),Image.Resampling.LANCZOS).save(Q/f"{row['id']}-mobile.png")
edited=[s for s in samples if s['changed']]
for page,start in enumerate(range(0,len(edited),12),1):
 part=edited[start:start+12];sheet=Image.new('RGB',(1920,4*302),(15,18,18));draw=ImageDraw.Draw(sheet)
 for i,s in enumerate(part):
  x=(i%4)*480;y=(i//4)*302
  with Image.open(s['file']) as im:sheet.paste(im.resize((480,270)),(x,y))
  draw.text((x+12,y+276),f"{s['id']} @ {s['time']:.2f}s",fill='white')
 sheet.save(Q/f'changed-contact-{page}.jpg',quality=92)
report={'revision':'room-v4-video','masterSha256':sha(cap),'duration':tm['duration'],'frames':tm['frames'],'width':1920,'height':1080,'fps':60,'sceneCount':len(tm['scenes']),'changedVisualScenes':len(changed),'unchangedVisualScenes':len(tm['scenes'])-len(changed),'existing51PcmSamplePreservation':read(H/'audio-qa.json')['oldSampleRangesIdentical'],'wholeFinalDecode':'pass','sameAacCleanCaptioned':True,'aacStreamHash':audio_hashes[0],'fourFilesPendingDelivery':True,'currentGameSnapshot':'source-snapshot.json','browserStills':'browser-evidence.json','checks':checks,'samples':samples,'sampleCount':len(samples),'humanWholeWatch':False,'wholeActualListening':False,'unresolved':['Sprite-Sheet-Diffusion official reproduction incomplete; unchanged disclosed result.']}
(H/'technical-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('Technical QA passed; samples',len(samples),flush=True)
