"""Prepare a local, normal-speed final-pair viewer using the existing range server."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
pair=read(R/'current17-final-pair-execution-v2.json')
session=read(R/'current17-final-pair-execution-v2.session.json')
assert pair['exitCode']==session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive']
row=next(v for v in pair['pair'] if '.captioned.' in v['path'])
source=ROOT/row['path'];assert sha(source)==row['sha256']
link=RAW/'motion-current17-final-captioned-v1.mp4'
page=RAW/'motion-current17-final-flow-v1.html'
receipt=R/'current17-flow-viewer-preparation-v1.json'
assert not link.exists() and not page.exists() and not receipt.exists()
os.link(source,link);assert os.path.samefile(source,link)
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>Motion current17 final flow review</title>
<style>body{margin:0;background:#111;color:#eee;font:16px sans-serif}main{max-width:1200px;margin:auto}video{display:block;width:100%;background:#000}button{padding:9px;margin:3px}#status{font-family:monospace;padding:8px}p{padding:0 8px}</style>
<main><video id="v" controls preload="metadata" src="motion-current17-final-captioned-v1.mp4"></video>
<div><button id="start">Start whole 1x muted</button><button id="pause">Pause</button><button id="resume">Resume 1x muted</button></div>
<div><label>Seek seconds <input id="seek" type="number" min="0" max="853.1" step="0.001" value="0"></label><button id="seekPaused">Seek paused</button><button id="seekPlay">Seek and play 1x muted</button></div>
<div id="status" role="status"></div><p>Final current17 captioned pair: 51186 frames / 853.1 seconds. Local visual flow review only; human listening and rights remain pending.</p></main>
<script>const v=document.getElementById('v'),s=document.getElementById('status');const update=()=>s.textContent=JSON.stringify({currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,rate:v.playbackRate,muted:v.muted,readyState:v.readyState,videoWidth:v.videoWidth,videoHeight:v.videoHeight});
document.getElementById('start').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.muted=true;v.play();};
document.getElementById('pause').onclick=()=>v.pause();document.getElementById('resume').onclick=()=>{v.playbackRate=1;v.muted=true;v.play();};
document.getElementById('seekPaused').onclick=()=>{v.pause();v.currentTime=Number(document.getElementById('seek').value);};
document.getElementById('seekPlay').onclick=()=>{v.currentTime=Number(document.getElementById('seek').value);v.playbackRate=1;v.muted=true;v.play();};
['loadedmetadata','timeupdate','play','pause','ended','seeked','ratechange','volumechange'].forEach(e=>v.addEventListener(e,update));update();</script></html>'''
page.write_text(html,'utf-8')
receipt.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),source=row['path'],sourceSha256=row['sha256'],viewer=page.relative_to(ROOT).as_posix(),viewerSha256=sha(page),sameInodeHardlink=link.relative_to(ROOT).as_posix(),sameFileVerified=True,serverPort=9250,newServers=0,newMediaCopies=0,normalPlaybackObserved=False,allFinalPixelApproval=False,newGitMedia=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(localOnly=True,sameInode=True,url='http://127.0.0.1:9250/'+page.name,playbackObserved=False)))
