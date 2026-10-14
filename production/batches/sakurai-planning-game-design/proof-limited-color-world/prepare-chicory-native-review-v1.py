"""Prepare local normal-speed source review; does not adopt source or narrate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT=Path(__file__).resolve().parents[4]
PROOF=Path(__file__).resolve().parent
SERVE=ROOT/'shared/assets/presenting-game-scores/raw'
OUT=PROOF/'chicory-native-action-plan-v1.json'
assert not OUT.exists()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
state=json.loads((PROOF/'chicory-official-source-execution-v1.json').read_text(encoding='utf-8'))
review=json.loads((PROOF/'chicory-coarse-direct-review-v1.json').read_text(encoding='utf-8'))
assert review['actualOuterExitCode']==0 and review['totalBoards']==143
links=[]
for s in state['sources']:
    source=ROOT/s['localPath'];target=SERVE/(s['key']+'-limited-review-v1.mp4')
    assert sha(source)==s['sha256']
    if target.exists(): assert os.path.samefile(source,target)
    else: os.link(source,target)
    assert os.path.samefile(source,target) and source.stat().st_size==target.stat().st_size
    links.append({'source':s['key'],'original':s['localPath'],'servedLink':str(target.relative_to(ROOT)).replace('\\','/'),
        'sameInode':True,'bytes':source.stat().st_size,'sha256':s['sha256']})
rows=[
('outline-room',1,155,170,'Painted floor/portraits/pots retain black contour; exclude any competing dialogue.'),
('outline-town',1,193,203,'Outlined path, tree hatching and windows stay recognizable across fills.'),
('palette-contours',1,234,246,'Player cycles fills while geometric contours remain; not a simulated visual impairment.'),
('roof-pattern',1,293,303,'Roof ridges, wall hatching and windows remain visible under paint.'),
('erase-structure',1,314,333,'Erase colored fills while structural lines remain.'),
('flower-first',1,532,545,'Inspect shrinking flowers and movement; sign dialogue near539 must be excluded before adoption.'),
('flower-second',1,559,565,'Second route through flowers; inspect state and crossing without permanent-unlock claim.'),
('erase-flower',1,590,594,'Erase returns tall flowers; inspect exact state transition and route.'),
('mushroom-first',2,19,30,'Paint grows platform height; jump sequence. Exclude transition at30.'),
('mushroom-chain',2,33,39,'Multiple hues, height changes and hop toward gift; stop before acquisition.'),
('flower-stack',2,49,62,'Flower shrinking, climbing and paint/jump; exclude acquisition overlay at62.'),
('flower-repeat',2,78,87,'Distinct comparison only if warranted; avoid repeated route quota padding.'),
('flower-route',2,88,98,'New silhouette-changing barrier route before transition.'),
('mushroom-four',2,100,112,'Paint and jump across four platforms, height/contour rather than hue-match claim.'),
('dark-cave-first',2,144,149,'Local contours within limited illumination; surroundings remain dark.'),
('dark-cave-second',2,150,157,'Paint and movement within local light; no universal accessibility claim.'),
]
windows=[]
for key,n,start,end,focus in rows:
    windows.append({'key':key,'source':f'chicory-b-roll-{n}', 'sourceFile':f'chicory-b-roll-{n}-limited-review-v1.mp4',
        'startFrame':start*60,'endFrameExclusive':end*60,'startPts':start*15360,'endPtsExclusive':end*15360,
        'timeBase':'1/15360','frameRate':'60/1','startSeconds':start,'endSecondsExclusive':end,
        'potentialDurationSeconds':end-start,'candidateFocus':focus,'exactNativeActionBoundaryApproved':False,
        'finalCaptionUiApproved':False,'adopted':False})
data={'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'slug':'limited-color-world',
    'candidateWindows':windows,'candidateWindowCount':len(windows),'candidateSeconds':sum(w['potentialDurationSeconds'] for w in windows),
    'server':'existing loopback127.0.0.1:9250; PID27140/create2026-10-09T10:34:26.837781+09:00',
    'servedHardlinks':links,'serverRestarted':False,'sourceCopiedOrEncoded':False,
    'sourceAudioForFinal':'exclude-all','allIntermediateNativeFramesReviewed':False,
    'fullContinuousPlaybackReviewed':False,'sourceFootageAdopted':False,'publicRightsApproved':False,
    'newProjectScriptTtsMcOrFinalMedia':False,'gitImagesOrMediaAdded':0}
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>Chicory native action review v1</title>
<style>body{margin:16px;background:#181818;color:#fff;font:16px sans-serif}button,select{font:inherit;margin:5px;padding:7px}#frame{position:relative;width:min(1920px,100%);aspect-ratio:16/9;container-type:inline-size;background:#000}video{width:100%;height:100%;display:block}#caption{position:absolute;left:50%;top:89.8148148%;transform:translate(-50%,-50%);font:bold 2.1875cqw/1.25 Arial,sans-serif;text-align:center;white-space:pre;background:#fff;color:#000;border:0.1041667cqw solid #111;box-shadow:0.4166667cqw 0.4166667cqw #153f2f;padding:0.5208333cqw 0.8333333cqw}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>
<label for="window">검토 창</label><select id="window"></select><button id="prepare">준비</button><button id="play">정상속도 재생</button><button id="pause">일시정지</button><label><input type="checkbox" id="overlay" checked>고정 자막 공간 시험</label><span id="status">준비 전</span>
<div id="frame"><video id="video" muted playsinline preload="metadata"></video><div id="caption">색이 바뀌어도 윤곽과 높이로\n길의 상태를 읽을 수 있습니다.</div></div>
<p>후보 원본 정상속도·음소거 검토. 화면 표시와 자동정지 시각은 정확 native 인아웃 승인 또는 모든 사이프레임 검수의 증거가 아닙니다.</p>
<pre id="state"></pre><pre id="events"></pre>
<script>const windows=WINDOWS_JSON; const v=document.getElementById('video'),sel=document.getElementById('window'),s=document.getElementById('status'),e=document.getElementById('events'),state=document.getElementById('state'),cap=document.getElementById('caption');let current=null,events=[],mediaTime=null,active=false,callback=null;
windows.forEach(w=>{let o=document.createElement('option');o.value=w.key;o.textContent=w.key+' / '+w.source+' '+w.startSeconds+'–'+w.endSecondsExclusive;sel.append(o)});
function show(){state.textContent=JSON.stringify(current?{key:current.key,source:current.source,exactNativeStartPts:current.startPts,exactNativeEndPtsExclusive:current.endPtsExclusive,timebase:current.timeBase,start:current.startSeconds,end:current.endSecondsExclusive,muted:v.muted,rate:v.playbackRate,current:v.currentTime,lastMediaTime:mediaTime,paused:v.paused,captionOverlay:document.getElementById('overlay').checked}:{});e.textContent=JSON.stringify(events)}
function log(kind){events.push({kind,key:current.key,at:new Date().toISOString(),current:v.currentTime,mediaTime,muted:v.muted,rate:v.playbackRate,paused:v.paused});show()}
function frame(now,meta){mediaTime=meta.mediaTime;if(active&&v.currentTime>=current.endSecondsExclusive){active=false;v.pause();s.textContent='검토 창 재생 완료';log('end')}else if(active){callback=v.requestVideoFrameCallback(frame)}show()}
document.getElementById('prepare').onclick=async()=>{active=false;v.pause();if(callback!==null)v.cancelVideoFrameCallback(callback);current=windows.find(w=>w.key===sel.value);mediaTime=null;v.muted=true;v.playbackRate=1;if(!v.currentSrc.endsWith(current.sourceFile)){v.src=current.sourceFile;await new Promise(resolve=>v.addEventListener('loadedmetadata',resolve,{once:true}))}v.currentTime=current.startSeconds;await new Promise(resolve=>v.addEventListener('seeked',resolve,{once:true}));s.textContent='정상속도 준비';log('prepared');v.requestVideoFrameCallback((now,meta)=>{mediaTime=meta.mediaTime;show()})};
document.getElementById('play').onclick=async()=>{if(!current)return;v.muted=true;v.playbackRate=1;active=true;callback=v.requestVideoFrameCallback(frame);await v.play();s.textContent='정상속도 재생 중';log('start')};document.getElementById('pause').onclick=()=>{active=false;v.pause();s.textContent='일시정지';if(current)log('pause')};document.getElementById('overlay').onchange=()=>{cap.hidden=!document.getElementById('overlay').checked;show()};v.addEventListener('pause',show);show();</script></html>'''.replace('WINDOWS_JSON',json.dumps(windows,ensure_ascii=False))
hp=SERVE/'limited-chicory-native-action-playback-v1.html'
assert not hp.exists();hp.write_text(html,encoding='utf-8')
print(json.dumps({'candidateWindows':len(windows),'potentialSeconds':data['candidateSeconds'],'html':str(hp.relative_to(ROOT)).replace('\\','/'),'hardlinksSameInode':True,'adopted':False},ensure_ascii=False))
