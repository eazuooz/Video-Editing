"""Reuse the existing range server and same-inode media for muted1x source review."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import json,os,hashlib
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
TARGET=RAW/'character-parameters-native-playback-v1.html'; STATE=P/'native-playback-preparation-v1.json'
assert not TARGET.exists() and not STATE.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
resource=json.loads((ROOT/'shared/output/character-parameters/preflight/resource-before-boundary-v1.json').read_text(encoding='utf-8-sig'))
server=next(p for p in resource['processes'] if p['ProcessId']==27140)
assert 'serve-native-review-v1.py' in server['CommandLine'] and server['CreationDate'].startswith('2026-10-09T10:34:26.837781')
srcs=json.loads((P/'native-action-execution-v2.json').read_text(encoding='utf-8-sig'))['sources']
plan=json.loads((P/'native-trim-plan-v3.json').read_text(encoding='utf-8-sig'))
links=[]
for s in srcs:
 src=ROOT/s['sourcePath'];target=RAW/f"character-parameters-{s['sourceKey']}.mp4"
 assert sha(src)==s['sourceSha256']
 if target.exists():assert os.path.samefile(src,target)
 else:os.link(src,target)
 assert os.path.samefile(src,target) and src.stat().st_size==target.stat().st_size
 links.append({'sourceKey':s['sourceKey'],'originalPath':s['sourcePath'],'hardlinkPath':str(target.relative_to(ROOT)).replace('\\','/'),'sameInode':True,'bytes':src.stat().st_size,'sha256':s['sourceSha256']})
windows=[{**w,'file':f"character-parameters-{w['sourceKey']}.mp4",'startSeconds':float(Fraction(w['startPts'])*Fraction(w['timeBase'])),'endSeconds':float(Fraction(w['endPtsExclusive'])*Fraction(w['timeBase']))} for w in plan['windows']]
html='''<!doctype html><meta charset="utf-8"><title>Character parameters native action review v1</title>
<style>body{margin:12px;background:#161616;color:#eee;font:15px sans-serif}header{display:flex;gap:8px;align-items:center;flex-wrap:wrap}button,select{font:15px sans-serif;padding:6px}canvas{display:block;width:min(960px,100%);height:auto;margin:8px 0}pre{white-space:pre-wrap;font:12px monospace;max-width:960px}video{display:none}</style>
<header><label>창<select id="window"></select></label><button id="prepare">준비</button><button id="play">정상속도 재생</button><button id="pause">일시정지</button><span id="status">선택 후 준비</span></header>
<canvas id="frame" width="1920" height="1080"></canvas><p id="metadata"></p><pre id="observations"></pre><video id="source" muted playsinline preload="metadata"></video>
<script>
const windows=__WINDOWS__,v=document.querySelector('#source'),c=document.querySelector('#frame'),ctx=c.getContext('2d'),sel=document.querySelector('#window');
let chosen=windows[0],active=false,ready=false,reviewEvents=[],lastMediaTime=null;
for(const w of windows){const o=document.createElement('option');o.value=w.key;o.textContent=w.key;sel.append(o)}
function status(text){document.querySelector('#status').textContent=text}
function details(){document.querySelector('#metadata').textContent=JSON.stringify({key:chosen.key,source:chosen.sourceKey,start:chosen.startSeconds,end:chosen.endSeconds,exactNativeStartPts:chosen.startPts,exactNativeEndPtsExclusive:chosen.endPtsExclusive,timebase:chosen.timeBase,muted:v.muted,rate:v.playbackRate,current:v.currentTime,paused:v.paused,lastMediaTime})}
function event(kind){reviewEvents.push({kind,key:chosen.key,at:new Date().toISOString(),current:v.currentTime,mediaTime:lastMediaTime,muted:v.muted,rate:v.playbackRate,paused:v.paused});document.querySelector('#observations').textContent=JSON.stringify(reviewEvents)}
function region(sx,sy,sw,sh,dx,dy,dw,dh,blur=0){ctx.save();ctx.filter=blur?`blur(${blur}px)`:'none';ctx.drawImage(v,sx,sy,sw,sh,dx,dy,dw,dh);ctx.restore()}
function draw(){if(v.readyState<2)return;ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,1920,1080);
 if(chosen.sourceKey==='gBbKFYZYvbc'){
  ctx.drawImage(v,0,0,1920,1080);region(0,602,1280,55,0,985,1920,95,12);region(16,657,299,63,24,985,449,95);region(335,657,296,63,1476,985,444,95);region(639,657,641,63,729,1035,462,45);
 }else if(chosen.sourceKey==='a8nwpiCqyTQ'){
  ctx.drawImage(v,0,0,1920,1080);region(406,870,1114,50,406,921,1114,144,12);region(406,921,1114,144,1490,135,424,55);
 }else{ctx.save();ctx.filter='blur(22px)';ctx.drawImage(v,0,0,1920,1080);ctx.restore();ctx.drawImage(v,0,0,1920,960)}
 const text='캐릭터마다 규칙이 다릅니다.';ctx.font='48px Malgun Gothic';const width=ctx.measureText(text).width+44,x=(1920-width)/2,y=928;
 ctx.fillStyle='#073c32';ctx.fillRect(x+14,y+14,width,84);ctx.fillStyle='#fff';ctx.fillRect(x,y,width,84);ctx.strokeStyle='#161b18';ctx.lineWidth=3;ctx.strokeRect(x+1.5,y+1.5,width-3,81);ctx.fillStyle='#080b09';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,960,970);details()}
function tick(now,meta){lastMediaTime=meta.mediaTime;draw();if(active&&v.currentTime>=chosen.endSeconds){active=false;v.pause();status('재생 완료');event('end')}v.requestVideoFrameCallback(tick)}
v.requestVideoFrameCallback(tick);
v.addEventListener('loadedmetadata',()=>{v.currentTime=chosen.startSeconds});
v.addEventListener('seeked',()=>{draw();ready=true;status('준비 완료');event('prepared')});
v.addEventListener('error',()=>{status('미디어 오류');event('error')});
document.querySelector('#prepare').onclick=()=>{v.pause();active=false;ready=false;chosen=windows.find(w=>w.key===sel.value);status('원본 준비 중');if(v.getAttribute('src')===chosen.file)v.currentTime=chosen.startSeconds;else{v.src=chosen.file;v.load()}details()};
document.querySelector('#play').onclick=async()=>{if(!ready)return;v.muted=true;v.playbackRate=1;active=true;await v.play();status('정상속도 재생 중');event('start')};
document.querySelector('#pause').onclick=()=>{active=false;v.pause();status('일시정지');event('manual-pause');details()};
</script>'''.replace('__WINDOWS__',json.dumps(windows,ensure_ascii=False))
TARGET.write_text(html,encoding='utf-8')
state={'schemaVersion':1,'slug':'character-parameters','preparedAt':datetime.now(timezone.utc).isoformat(),'status':'prepared-only','htmlPath':str(TARGET.relative_to(ROOT)).replace('\\','/'),'htmlSha256':sha(TARGET),'url':'http://127.0.0.1:9250/character-parameters-native-playback-v1.html','serverIdentity':server,'newServerStarts':0,'hardlinks':links,'windows':windows,'normalSpeedPlaybackObserved':False,'nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'sourceAudioUse':False,'newEncodes':0,'externalResearchChanges':0,'rasterGitAdditions':0}
STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'windows':len(windows),'sameInodeHardlinks':len(links),'newServerStarts':0}))
