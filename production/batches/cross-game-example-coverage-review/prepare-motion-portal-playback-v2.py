from pathlib import Path
import os,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
state=json.loads((R/'portal-annotation-pilot-execution-v2.json').read_text('utf-8-sig'))
p=ROOT/state['path']
assert hashlib.sha256(p.read_bytes()).hexdigest()==state['sha256']
raw=ROOT/'shared/assets/presenting-game-scores/raw'
target=raw/'motion-portal-annotation-pilot-v2.mp4'
assert not target.exists()
os.link(p,target)
assert os.stat(target).st_ino==os.stat(p).st_ino
html=raw/'motion-portal-annotation-pilot-v2.html'
assert not html.exists()
html.write_text('''<!doctype html><meta charset="utf-8"><title>Portal 2 표식 v2 정상속도 검수</title>
<style>body{margin:16px;background:#151515;color:white;font-family:sans-serif}video{width:min(100%,1280px)}button{font-size:20px;margin:8px}</style>
<h1>Portal 2 표식 v2 · 무음 3초 검수</h1><button id="play">처음부터 정상속도 재생</button>
<button id="pause">일시정지</button><output id="status"></output><br>
<video id="video" muted playsinline controls preload="auto" src="motion-portal-annotation-pilot-v2.mp4"></video>
<script>const v=document.getElementById('video'),s=document.getElementById('status');
document.getElementById('play').onclick=()=>{v.currentTime=0;v.muted=true;v.playbackRate=1;v.play()};
document.getElementById('pause').onclick=()=>v.pause();
function show(){s.textContent=JSON.stringify({time:v.currentTime,duration:v.duration,rate:v.playbackRate,paused:v.paused,ended:v.ended,muted:v.muted})};
['loadedmetadata','timeupdate','play','pause','ended'].forEach(e=>v.addEventListener(e,show));</script>''','utf-8')
print('Prepared same-inode local pilot playback through existing9250 server; server start0.')
