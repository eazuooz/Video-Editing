from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v2';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v2/video');F=O/'final';Q=O/'qa';Q.mkdir(exist_ok=True)
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
def sha(f):return hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
tm=json.loads((L/'timeline.json').read_text('utf8'));cues=json.loads((L/'captions.json').read_text('utf8'));rec=[]
for kind in ['clean','captioned']:
 f=F/f'ai-2d-game-assets.room-v2.{kind}.mp4';probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',f]).stdout)
 v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
 assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1');assert int(v['nb_frames'])==tm['frames'];assert abs(float(probe['format']['duration'])-tm['duration'])<.08;assert(a['sample_rate'],a['channels'])==('48000',2)
 dec=run(['ffmpeg','-v','error','-threads','3','-i',f,'-f','null','-']);assert not dec.stderr.strip(),dec.stderr
 ah=run(['ffmpeg','-v','error','-i',f,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
 rec.append({'kind':kind,'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'frames':int(v['nb_frames']),'fps':60,'width':1920,'height':1080,'audio':ah,'duration':float(probe['format']['duration']),'fullDecode':'passed'})
assert rec[0]['audio']==rec[1]['audio']
assert len(tm['scenes'])==46 and len([x for x in tm['scenes'] if x['originalPcmPreserved']])==30
for row in tm['scenes']:assert sha(Path(row['source']))==row['sourceSha256']
for a,b in zip(cues,cues[1:]):assert a['start']<a['end']<=b['start']
assert cues[0]['start']>=2 and cues[-1]['end']<=tm['duration']-10+.02
samples=[];cap=F/'ai-2d-game-assets.room-v2.captioned.mp4'
for row in tm['scenes']:
 for fraction in ([.22,.68] if row['id'].startswith('R') else [.65]):
  sec=row['start']+row['duration']*fraction;name=f"{row['id']}-{int(fraction*100)}";f=Q/(name+'.jpg')
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',sec,'-i',cap,'-frames:v','1',f]);Image.open(f).resize((375,211)).save(Q/(name+'-mobile.png'));samples.append({'scene':row['id'],'time':sec,'file':str(f),'mobile':str(Q/(name+'-mobile.png'))})
for k in range(0,len(samples),9):
 im=Image.new('RGB',(1440,900),'#151515');d=ImageDraw.Draw(im)
 for i,r in enumerate(samples[k:k+9]):im.paste(Image.open(r['file']).resize((480,270)),((i%3)*480,(i//3)*300));d.text(((i%3)*480+10,(i//3)*300+280),Path(r['file']).stem,fill='white')
 im.save(Q/f'contact-{k//9}.jpg')
for n,s in [('branding',1),('outro',tm['duration']-5)]:run(['ffmpeg','-v','error','-y','-ss',s,'-i',cap,'-frames:v','1',Q/(n+'.jpg')])
result={'videos':rec,'duration':tm['duration'],'sceneCount':46,'originalPcmScenesPreserved':30,'newPcmScenes':16,'subtitleCues':len(cues),'sameEncodedAudio':True,'fullDecode':'passed','samples':samples,'encodedVisualReview':'pending direct sample inspection','humanListening':False,'humanVideoReview':False,'previousMasterSha256':'023ca35a572c9b9d0902c3b3c9c88b06d24e6b5a751b521bd1707769fc768627','unresolved':['Sprite-Sheet-Diffusion inference not completed; actual setup failure disclosed']}
(H/'technical-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print('Technical QA passed',tm['duration'],len(cues))
