"""Local CPU normal-speed geometry check, independent of final caption approval."""
from pathlib import Path
import cv2,json,hashlib,subprocess,numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-motion';O.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2);records=[];offset=0
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','800x450','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'observed-motion.mp4')]
process=subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
for s in json.loads((B/'polygons-observed-track-seeds.json').read_text(encoding='utf8')):
 p=B/'polygons-tracks'/f'{s["id"]}.json';r=json.loads(p.read_text(encoding='utf8'));keys=r['keyframes'];assert len(keys)>=45,(s['id'],len(keys))
 assert hashlib.sha256((ROOT/r['sourceFile']).read_bytes()).hexdigest()==r['sourceSha256']
 c=cv2.VideoCapture(str(ROOT/r['sourceFile']));c.set(cv2.CAP_PROP_POS_FRAMES,keys[0]['nativeFrame']);assert r['nativeFps']==60
 for k in keys:
  ok,frame=c.read();assert ok;frame=cv2.resize(frame,(800,450))
  for col,bgr in [('red',(80,83,239)),('blue',(245,165,66)),('yellow',(79,213,255))]:
   if col in k:cv2.polylines(frame,[np.rint(k[col]).astype(np.int32)],r.get('closed',False) or col in ['blue','yellow'],bgr,3,cv2.LINE_AA)
  cv2.rectangle(frame,(5,67),(370,93),(15,15,15),-1);cv2.putText(frame,f'{s["id"]} source {k["t"]:.3f}s / observed draft',(10,86),cv2.FONT_HERSHEY_SIMPLEX,.49,(255,255,255),1,cv2.LINE_AA)
  process.stdin.write(frame.tobytes())
 c.release();n=len(keys);records.append({'id':s['id'],'trackSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'startFrame':offset,'frames':n,'sourceFile':r['sourceFile'],'sourceSha256':r['sourceSha256'],'sourceFirstFrame':keys[0]['nativeFrame'],'sourceLastFrame':keys[-1]['nativeFrame'],'sourceSpeed':1});offset+=n
process.stdin.close();assert process.wait()==0
r={'frames':offset,'seconds':offset/60,'records':records,'videoSha256':hashlib.sha256((O/'observed-motion.mp4').read_bytes()).hexdigest(),'finalNarrationCaptionApproval':False}
(O/'manifest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'review.html').write_text('''<!doctype html><meta charset="utf-8"><title>Polygon observed geometry motion</title><style>body{background:#111;color:white;font:17px sans-serif}video{width:min(100%,1280px)}pre{white-space:pre-wrap}</style><h1>Observed geometry · final narration/captions pending</h1><button id="play">Play native 1x whole geometry check</button><br><video id="v" src="observed-motion.mp4" controls preload="auto"></video><pre id="s">Ready</pre><script>let v=document.getElementById('v'),s=document.getElementById('s');document.getElementById('play').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.play()};function report(){s.textContent=JSON.stringify({ended:v.ended,paused:v.paused,current:v.currentTime,duration:v.duration,rate:v.playbackRate,width:v.videoWidth,height:v.videoHeight,played:Array.from({length:v.played.length},(_,i)=>[v.played.start(i),v.played.end(i)]),finalNarrationCaptionApproval:false})}v.addEventListener('timeupdate',report);v.addEventListener('ended',report)</script>''',encoding='utf8')
print(len(records),offset/60,'seconds normal-speed geometry draft, final QA pending')
