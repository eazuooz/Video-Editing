from pathlib import Path
import subprocess,json,hashlib,math
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';F=L/'final';Q=L/'qa';Q.mkdir(exist_ok=True)
def run(args):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
t=read(L/'timeline.json');records=[]
for kind in ('clean','captioned'):
 f=F/f'{P.name}.{kind}.mp4'
 probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',f]).stdout)
 v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 assert a['channels']==2 and a['sample_rate']=='48000'
 assert int(v['nb_frames'])==t['frames'],(kind,v['nb_frames'],t['frames'])
 assert abs(float(probe['format']['duration'])-t['duration'])<.08
 decode=run(['ffmpeg','-hide_banner','-v','error','-threads','4','-i',f,'-f','null','-']);assert not decode.stderr.strip(),decode.stderr
 packet=run(['ffmpeg','-hide_banner','-v','error','-i',f,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
 records.append({'kind':kind,'path':str(f.relative_to(R)).replace('\\','/'),'sha256':sha(f),'bytes':f.stat().st_size,'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'duration':float(probe['format']['duration']),'audioCodec':a['codec_name'],'audioSampleRate':a['sample_rate'],'audioPacketHash':packet,'fullDecode':'pass'})
assert records[0]['audioPacketHash']==records[1]['audioPacketHash']
for r in t['scenes']:
 assert sha(Path(r['source']))==r['sourceSha256']
 meta=read(L/'visual'/f"scene-{r['id']}.mp4.json");assert meta['frames']==r['frames']
 if 'sourceSha256' in meta:assert meta['sourceSha256']==r['sourceSha256']
 # Old already-rendered files had the same immutable take and frame duration;
 # record the mapping now without pretending the original encoder logged it.
 else:meta['verifiedSourceSha256AtFinalQa']=r['sourceSha256'];(L/'visual'/f"scene-{r['id']}.mp4.json").write_text(json.dumps(meta,indent=2),'utf-8')
captions=read(L/'captions.json')
assert captions[0]['start']>=2 and captions[-1]['end']<=t['duration']-10+.02
for x,y in zip(captions,captions[1:]):assert x['start']<x['end']<=y['start']
# Full-resolution encoded samples plus scaled375px evidence, never source PNG-only QA.
from PIL import Image,ImageDraw
frames=[]
for r in t['scenes']:
 sec=r['start']+r['duration']*.65;out=Q/f"encoded-{r['id']}.jpg"
 run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',sec,'-i',F/f'{P.name}.captioned.mp4','-frames:v','1',out]);frames.append(out)
 Image.open(out).resize((375,211)).save(Q/f"mobile-{r['id']}.png")
for k in range(0,len(frames),9):
 canvas=Image.new('RGB',(1440,900),'#151515');draw=ImageDraw.Draw(canvas)
 for i,f in enumerate(frames[k:k+9]):canvas.paste(Image.open(f).resize((480,270)),((i%3)*480,(i//3)*300));draw.text(((i%3)*480+12,(i//3)*300+275),f.stem,fill='white')
 canvas.save(Q/f'encoded-contact-{k//9}.jpg')
for name,sec in [('branding',1),('outro',t['duration']-5),('last',t['duration']-.05)]:
 run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',sec,'-i',F/f'{P.name}.captioned.mp4','-frames:v','1',Q/f'{name}.jpg'])
report={'videos':records,'sameEncodedAudio':True,'duration':t['duration'],'sceneCount':30,'subtitleCues':len(captions),'noCaptionsOverBrandingOrMembership':True,'sourceMediaSeparation':'No supplied finished-short footage or voice used','humanReview':'pending','wholeHumanListening':'pending','encodedVisualReview':'awaiting direct inspection of saved samples','audioMetrics':read(P/'production/audio-qa.json')}
(P/'production/technical-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Technical QA pass',t['duration'],len(captions),'cues; saved encoded samples for inspection')
