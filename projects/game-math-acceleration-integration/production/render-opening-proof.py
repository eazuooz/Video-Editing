"""A short real FHD60 comparison of M25 speech, actual action, labels, and captions."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];R=P.parents[1];B=R/'production/batches/game-math-remaining-20261104'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audio=P/'production/local/audio-v1';audionew=P/'production/local/audio-v2'
assert sha(audio/'chunks/000-01-scene.wav')==sha(audionew/'chunks/000-01-scene.wav')
assert P.name in read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['projectSlugs']
t=read(P/'production/local/edit-v1/word-aligned-timeline.json');assert not any(x['scene']=='000' for x in t['flags'])
source=read(P/'planning/scene-bindings.json')['scenes'][0]['actualGamePart'];assert source['sourceIn']==58 and source['sourceOut']==65 and source['nativeFps']=='60/1'
old=t['scenes'][0]['actualGamePart'];assert source['sourceSha256']==old['sourceSha256'] and source['sourceIn']==old['sourceIn']
sys.argv=['compose','--queue',str(P/'production/unity-staging/local-preflight-v3/queue.json')]
sp=importlib.util.spec_from_file_location('picture',B/'compose-module.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
w=P/'production/local/opening-motion-proof-v2';w.mkdir(exist_ok=True,parents=True)
out=R/'output/game-math-remaining-20261104';dest=out/'M25-opening-action-7s.mp4'
cut=dict(source,frames=420,scene='000');sources=read(P/'planning/footage-audit.json')['sources'];src=next(x for x in sources if x['id']==source['sourceId']);footage=R/src['file'];assert m.sha(footage)==src['sha256']
annotation=m.annotation_ass(cut,src,w/'game.ass')
cs=[dict(x,id=i+1,end=min(x['end'],7.)) for i,x in enumerate(t['ko']) if 0<=x['start']<7 and x['scene']=='000']
layout=m.C.caption_ass(w/'caption.ass',cs,0,{});assert all(len(x['lines'])==1 for x in layout)
m.normalized_audio(footage,58,420,w/'game-original.wav',-23,w,'source')
m.normalized_audio(audio/'narration.wav',0,420,w/'speech.wav',-16,w,'narration')
mix='[1:a]asplit=2[voice][key];[2:a][key]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[game];[voice][game]amix=inputs=2:normalize=0,alimiter=limit=0.831764:level=false:latency=true[mix]'
vf=m.game_filters(cut,'game.ass')+',ass=caption.ass'
m.ff(['-ss','58','-t','7','-i',footage,'-i',w/'speech.wav','-i',w/'game-original.wav','-vf',vf,'-filter_threads','2','-filter_complex_threads','1','-filter_complex',mix,'-map','0:v:0','-map','[mix]','-t','7','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',dest],w/'opening-proof.log',w)
m.video_check(dest,420);f=[42,168,303,391];choose='+'.join('eq(n,'+str(i)+')' for i in f)
if not (w/'mobile.jpg').is_file():
 subprocess.run([str(m.FF),'-v','error','-nostdin','-n','-threads','2','-i',dest,'-vf',"select='"+choose+"'",'-fps_mode','vfr','-frames:v','4','-threads','1','-start_number','0',str(w/'frame-%d.png')],check=True,creationflags=m.CREATE)
 board=Image.new('RGB',(750,470),'black');dr=ImageDraw.Draw(board)
 for i,fr in enumerate(f):
  im=Image.open(w/f'frame-{i}.png');assert im.size==(1920,1080);im.thumbnail((375,211),Image.Resampling.LANCZOS);x=i%2*375;y=i//2*235;board.paste(im,(x,y));dr.text((x+4,y+213),f'{fr/60:.2f}s',fill='white')
 board.save(w/'mobile.jpg',quality=95)
m.save(w/'evidence.json',dict(file=str(dest),sha256=m.sha(dest),frames=420,rate=60,pixels=[1920,1080],rawNarrationTakeSha256=sha(audio/'chunks/000-01-scene.wav'),sourceId=src['id'],sourceSeconds=[58,65],slowdown=False,freeze=False,sourceAudioRetained=True,musicAdded=False,captions=cs,labels=annotation,labelAndCaptionSamples=str(w/'mobile.jpg'),notFullLecture=True,humanListening=False))
print(dest)
