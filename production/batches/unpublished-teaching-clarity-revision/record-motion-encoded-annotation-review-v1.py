from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(R/'retained-annotation-render-execution-v1.json')
assert s['pid']==50112 and s['createTime']==1791659402.856759 and s['actualExitCode']==0
assert s['frames']==1812 and s['samples']==150
rows=[]
for w in s['windows']:
 assert w['sourceDecodeExitCode']==w['encodeExitCode']==w['wholeDecodeExitCode']==w['extractionExitCode']==0
 assert w['allPts1500Verified'] and w['allNativeSampleRgbMatched'] and w['allPreparedSampleRgbMatched']
 for row in w['samples']+w['boards']+[w['video'],w['allFrameGuides']]:assert sha(ROOT/row['path'])==row['sha256']
 rows.append(dict(scene=w['scene'],frames=w['frames'],samples=w['samples'],boards=w['boards'],video=w['video'],
  allListedEncodedSamplesDirectlyRead=True,allListedBoardsDirectlyRead=True,allPts1500Verified=True))
notes={
 '01':'Compact aim dot moves separately from the marked background post. Red mark is hidden at89/90; blue post ends after210 when the view shifts. All shown critical samples are consistent with these boundaries.',
 '03':'Actual compact aim dot stays inside red ring; separate blue post remains on the visible post while the tool moves. HUD, source credit and lower narration area remain readable.',
 '05':'Near red post and distant blue fence describe relative layout, not measured world coordinates or the same exact fence point. Both hide during first rapid pan1..14 and after90. Repaired15..90 positions match visible post/fence.',
 '07':'Red leader points to the real red laser. Blue leader targets the visible blue doorway boundary; hidden when uncertain and reappears on actual boundary. Independent trailer excerpt, no continuous solved-puzzle proof.',
 '09':'Red ring follows the compact aim dot as aim changes late in the excerpt. The label changes to water only once spraying begins338; source HUD and slide remain readable.',
 '11':'No red mark while off-centre aim cannot be determined0..179. Water leader appears180 onward and blue crossbar guide hides when the view no longer supports it. No skyline guide.'}
target=R/'retained-encoded-sample-direct-review-v1.json';assert not target.exists()
save(target,dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),
 execution='retained-annotation-render-execution-v1.json',executionSha256=sha(R/'retained-annotation-render-execution-v1.json'),
 actualSession=45777,actualOuterExitCode=0,actualExitToolChunk='7850cd',workerPidAbsentObserved=True,
 frames=1812,sampleCount=150,boardCount=27,allListedEncodedSamplesDirectlyRead=True,all27BoardsDirectlyRead=True,
 encodedSelectedSampleReviewPassed=True,rows=rows,observations=notes,
 everyIntermediateFrameDirectlyRead=False,wholeContinuousPlaybackReviewPassed=False,
 allFinalCaptionedPixelsApproved=False,currentMixedAudioApproved=False,humanListeningApproved=False,
 sourceAndPcmMutations=0,sourceAudioUsed=False,researchManipulations=0,newGitImages=0))
raw=ROOT/'shared/assets/presenting-game-scores/raw'
links=[]
for w in s['windows']:
 p=ROOT/w['video']['path'];dest=raw/f"motion-retained-annotations-v1-scene{w['scene']}.mp4"
 assert not dest.exists();os.link(p,dest);assert os.stat(p).st_ino==os.stat(dest).st_ino
 links.append(dict(scene=w['scene'],file=dest.name,frames=w['frames']))
html='''<!doctype html><meta charset="utf-8"><title>Retained annotation playback review</title>
<style>body{background:#111;color:white;font:16px sans-serif;margin:12px}video{width:min(1280px,100%)}button{padding:8px;margin:4px}pre{white-space:pre-wrap}</style>
<h1>조준과 배경 표시 · 여섯 정상속도 발췌</h1><p>무음 중간 영상입니다. 최종 혼합음성·고정자막 승인은 별도입니다.</p>
<video id="v" controls muted preload="auto"></video><div id="buttons"></div><button id="all">여섯 장면 1배속 재생</button><pre id="status"></pre><pre id="events"></pre>
<script>const clips=CLIPS,v=document.getElementById('v'),out=document.getElementById('status'),log=document.getElementById('events');let index=0,automatic=false,records=[];
function update(){out.textContent=JSON.stringify({scene:clips[index].scene,currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate},null,2);log.textContent=JSON.stringify(records,null,2)}
function open(i,play){index=i;v.src=clips[i].file;v.muted=true;v.playbackRate=1;if(play)v.play();update()}
clips.forEach((c,i)=>{let b=document.createElement('button');b.textContent='장면 '+c.scene;b.onclick=()=>{automatic=false;open(i,false)};document.getElementById('buttons').appendChild(b)});
document.getElementById('all').onclick=()=>{records=[];automatic=true;open(0,true)};
v.addEventListener('play',()=>{records.push({event:'start',scene:clips[index].scene,currentTime:v.currentTime,muted:v.muted,rate:v.playbackRate});update()});
v.addEventListener('ended',()=>{records.push({event:'end',scene:clips[index].scene,currentTime:v.currentTime,muted:v.muted,rate:v.playbackRate});if(automatic&&index+1<clips.length)open(index+1,true);else automatic=false;update()});
['timeupdate','pause','loadedmetadata'].forEach(e=>v.addEventListener(e,update));open(0,false);</script>'''.replace('CLIPS',json.dumps(links))
helper=raw/'motion-retained-annotations-review-v1.html';assert not helper.exists();helper.write_text(html,'utf-8')
print(json.dumps(dict(samples=150,boards=27,helper=str(helper.relative_to(ROOT)),sourceCopies=0,newGitImages=0)))
