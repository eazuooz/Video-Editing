from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
aim=read(R/'aim-target-qa-execution-v3.json');goal=read(R/'two-target-qa-execution-v2.json')
assert aim['actualExitCode']==0 and goal['actualExitCode']==0
raw=ROOT/'shared/assets/presenting-game-scores/raw';helper=raw/'motion-target-repair-review-v3.html';receipt=R/'target-playback-preparation-v3.json'
assert not helper.exists() and not receipt.exists()
rows=[]
for id,state in [('02',aim),('06b',goal)]:
 r=next(x for x in state['completed'] if x['id']==id and x['variant']=='captioned');src=ROOT/r['source'];assert sha(src)==r['sourceSha256']
 linked=raw/f'motion-target-{id}-review-v3.mp4';assert not linked.exists();os.link(src,linked);assert os.path.samefile(src,linked)
 rows.append(dict(id=id,file=linked.name,source=r['source'],sourceSha256=r['sourceSha256'],frames=r['frames'],sameInode=True))
html='''<!doctype html><meta charset="utf-8"><title>Motion target repair review v3</title><style>body{background:#111;color:white;font:16px sans-serif;margin:10px}video{width:min(1280px,100%)}button,input{padding:8px;margin:4px}pre{white-space:pre-wrap}</style>
<h1>게임 멀미 · 두 수정 장면의 실제 움직임과 현재 자막</h1><p>1배속 음소거 픽셀 검수입니다. 사람 전체청취·발음 승인과 구별합니다.</p><div id="choices"></div><video id="v" controls muted preload="metadata"></video><div><button id="start">선택 장면 처음부터 1배속 재생</button><button id="pause">일시정지</button><label>장면 프레임 <input id="frame" type="number" value="0"></label><button id="seek">프레임 이동</button></div><pre id="status"></pre><pre id="events"></pre>
<script>const rows=ROWS,v=document.getElementById('v');let selected=rows[0],records=[];function update(){document.getElementById('status').textContent=JSON.stringify({scene:selected.id,currentTime:v.currentTime,duration:v.duration,frame:Math.round(v.currentTime*60),expectedFrames:selected.frames,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate},null,2);document.getElementById('events').textContent=JSON.stringify(records,null,2)}function choose(r){v.pause();selected=r;records=[];v.src=r.file;update()}rows.forEach(r=>{let b=document.createElement('button');b.textContent=r.id==='02'?'02 목표 회전과 추가 흔들림':'06b 방향을 읽는 단서';b.onclick=()=>choose(r);document.getElementById('choices').appendChild(b)});document.getElementById('start').onclick=()=>{records=[];v.currentTime=0;v.muted=true;v.playbackRate=1;v.play();update()};document.getElementById('pause').onclick=()=>v.pause();document.getElementById('seek').onclick=()=>{v.pause();v.currentTime=Number(document.getElementById('frame').value)/60;update()};['play','pause','ended','seeked','ratechange'].forEach(e=>v.addEventListener(e,()=>{records.push({event:e,currentTime:v.currentTime,muted:v.muted,rate:v.playbackRate,observedAt:new Date().toISOString()});update()}));['timeupdate','loadedmetadata'].forEach(e=>v.addEventListener(e,update));choose(selected);</script>'''.replace('ROWS',json.dumps(rows,ensure_ascii=False))
helper.write_text(html,'utf-8');receipt.write_text(json.dumps(dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),helper=helper.relative_to(ROOT).as_posix(),url='http://127.0.0.1:9250/motion-target-repair-review-v3.html',targets=rows,newServers=0,newMediaEncodes=0,actualNormalSpeedPlaybackApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Prepared target helper with exact hardlinked captioned outputs; no playback approval.')
