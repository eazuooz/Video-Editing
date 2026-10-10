"""Expose the completed pair on the existing owned range server; no encode/server start."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
pair=read(R/'final-pair-execution-v2.json')
session=read(R/'final-pair-execution-v2.session.json')
assert pair['exitCode']==0 and session['actualOuterExitCode']==0 and session['workerCurrentlyAlive']==False
source_row=next(x for x in pair['pair'] if '.captioned.' in x['path'])
source=ROOT/source_row['path']
assert source.is_file() and sha(source)==source_row['sha256']
raw=ROOT/'shared/assets/presenting-game-scores/raw'
linked=raw/'motion-reviewed-current-pair-v2.mp4'
helper=raw/'motion-final-flow-review-v2.html'
receipt=R/'final-flow-helper-preparation-v2.json'
assert not helper.exists() and not receipt.exists(), 'Reuse actual prepared helper; no overwrite.'
if linked.exists():assert os.path.samefile(source,linked)
else:os.link(source,linked)
assert os.path.samefile(source,linked) and source.stat().st_size==linked.stat().st_size
plan=read(R/'measured-additive-plan-v1.json')
scenes=[{'id':s['id'],'frame':s['startFrame'],'title':s['title']} for s in plan['scenes']]
body='''<!doctype html><meta charset="utf-8"><title>Motion final flow review</title>
<style>body{background:#111;color:white;font:16px sans-serif;margin:12px}video{width:min(1280px,100%)}button,input{padding:8px;margin:4px}pre{white-space:pre-wrap}</style>
<h1>게임 멀미와 카메라 설계 · 현재 최종 흐름 검수</h1>
<p>실제 1배속 재생과 선택 픽셀 관찰입니다. 사람 전체청취·발음·모든 사이프레임 승인은 별도입니다.</p>
<video id="v" controls muted preload="metadata" src="motion-reviewed-current-pair-v2.mp4"></video>
<div><button id="start">처음부터 1배속 전체 재생</button><button id="pause">일시정지</button><label>60fps 프레임 <input id="frame" type="number" min="0" max="40192" value="0"></label><button id="seek">프레임으로 이동</button></div>
<div id="scenes"></div><pre id="status"></pre><pre id="events"></pre>
<script>const scenes=SCENES,v=document.getElementById('v'),status=document.getElementById('status'),events=document.getElementById('events');let records=[];
function update(){status.textContent=JSON.stringify({currentTime:v.currentTime,duration:v.duration,frame:Math.round(v.currentTime*60),paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate},null,2);events.textContent=JSON.stringify(records,null,2)}
function jump(f){v.pause();v.currentTime=f/60;update()}
document.getElementById('start').onclick=()=>{records=[];v.currentTime=0;v.muted=true;v.playbackRate=1;v.play();update()};
document.getElementById('pause').onclick=()=>v.pause();document.getElementById('seek').onclick=()=>jump(Number(document.getElementById('frame').value));
scenes.forEach(s=>{let b=document.createElement('button');b.textContent=s.id+' '+s.title;b.onclick=()=>jump(s.frame);document.getElementById('scenes').appendChild(b)});
['play','pause','ended','seeked','ratechange'].forEach(e=>v.addEventListener(e,()=>{records.push({event:e,currentTime:v.currentTime,muted:v.muted,rate:v.playbackRate,observedAt:new Date().toISOString()});update()}));['timeupdate','loadedmetadata'].forEach(e=>v.addEventListener(e,update));</script>'''.replace('SCENES',json.dumps(scenes,ensure_ascii=False))
helper.write_text(body,'utf-8')
receipt.write_text(json.dumps({'schemaVersion':1,'preparedAt':datetime.now(timezone.utc).isoformat(),'source':str(source.relative_to(ROOT)).replace('\\','/'),'sourceSha256':sha(source),'linkedPath':str(linked.relative_to(ROOT)).replace('\\','/'),'sameInode':os.path.samefile(source,linked),'helper':str(helper.relative_to(ROOT)).replace('\\','/'),'url':'http://127.0.0.1:9250/motion-final-flow-review-v2.html','newMediaEncodes':0,'newServers':0,'wholeNormalSpeedPlaybackReachedEnd':False,'sampledContinuousFlowApproved':False,'humanListeningApproved':False},ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'prepared':True,'actualPlayback':False,'newServers':0}))
