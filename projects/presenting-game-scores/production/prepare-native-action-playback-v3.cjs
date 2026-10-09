const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const proof=read(path.join(base,'native-actions-sample-direct-review-v3.json'));
const execution=read(path.join(base,'longplay-source-execution.json'));
if(!proof.allListedNativePtsSamplesDirectlyRead||proof.footageAdopted||execution.exitCode!==0)throw Error('Read reviewed source preflight');
const raw=path.join(root,'shared/assets/presenting-game-scores/raw');
const alias=path.join(raw,'balatro-c1WD4x9Dyg0-review-v2.mp4');
const html=path.join(raw,'balatro-native-action-playback-v3.html');
if(fs.existsSync(html))throw Error('Reuse existing helper');
if(!path.resolve(alias).startsWith(path.resolve(raw)+path.sep))throw Error('Alias outside preview root');
if(!fs.existsSync(alias))fs.linkSync(execution.sourcePath,alias);
if(fs.statSync(alias).ino!==fs.statSync(execution.sourcePath).ino||fs.statSync(alias).size!==819996936)throw Error('Original source hardlink mismatch');
const cuts=proof.intervals.map(i=>({id:i.id,start:i.draft[0],end:i.draft[1],claim:i.claim}));
const body=`<!doctype html><html lang="ko"><meta charset="utf-8"><title>발라트로 6:4 수정 — 실제 행동 관찰</title>
<style>body{margin:12px;background:#141414;color:#eee;font:15px sans-serif}h1{font-size:19px;margin:8px 0}nav{display:flex;gap:5px;flex-wrap:wrap}button{padding:6px 8px;border:0;background:#ecd487;cursor:pointer}#status{font:14px monospace;margin:6px 0}#info{margin:8px 0;min-height:20px}#shell{position:relative;margin:8px auto;overflow:hidden;background:#000;width:min(100%,1280px);aspect-ratio:16/9}#stage{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;overflow:hidden}video{position:absolute;width:1920px;height:1080px;left:0;top:0;object-fit:contain}.caption{position:absolute;left:960px;top:970px;transform:translate(-50%,-50%);color:#080b09;background:#fff;border:3px solid #161b18;padding:11px 22px;font:500 48px/62px 'Noto Sans KR','Malgun Gothic',sans-serif;text-align:center;white-space:pre;box-shadow:14px 14px 0 #073c32}.credit{position:absolute;right:32px;top:24px;background:#000b;padding:8px 12px;font:28px sans-serif;color:#fff}small{color:#bdbdbd}#note{margin-top:7px}</style>
<h1>발라트로 6:4 수정 — 실제 행동/자막 여백 관찰</h1><small>정상 1×, 음소거. 준비된 후보이며 채택/최종 자막 승인 아님. 기존 대사 표본만 표시. 정확 인아웃은 원본 PTS를 따름.</small>
<nav id="cuts"></nav><div id="info">구간 선택</div><div id="status">대기</div>
<div id="shell"><div id="stage"><video id="player" muted preload="metadata"></video><div id="caption" class="caption">카드의 반응 뒤에 숫자가 커지고\n강조되는 모습을 보세요.</div><div id="credit" class="credit">Footage: Squeaky Whale Gameplay Archive</div></div></div>
<nav><button id="toggle">재생/일시정지</button><button id="restart">현재 후보 처음부터</button><button id="captionToggle">자막 켜기/끄기</button><button id="reframe">원본/상단 48px 이동 표본</button></nav>
<div id="note">상단 48px 이동은 여백 검사 표본이며 하단 48px 검정은 임시 표시입니다. 실제 same-frame fill과 모든 cue 픽셀은 별도 검수합니다. 화면 크레딧도 준비 표본입니다.</div>
<script>const cuts=${JSON.stringify(cuts)};const v=document.querySelector('#player'),status=document.querySelector('#status'),shell=document.querySelector('#shell'),stage=document.querySelector('#stage');let current=null,history=[],offset=0;
function size(){stage.style.transform='scale('+(shell.clientWidth/1920)+')'}window.addEventListener('resize',size);size();
function choose(c){v.pause();current=c;document.querySelector('#info').textContent=c.id+' | '+c.claim+' | ['+c.start+','+c.end+')';const seek=()=>{v.currentTime=c.start;v.playbackRate=1;v.muted=true;v.play()};if(!v.currentSrc){v.src='balatro-c1WD4x9Dyg0-review-v2.mp4';v.addEventListener('loadedmetadata',seek,{once:true});v.load()}else seek();history.push({type:'selected',id:c.id,start:c.start,end:c.end,at:new Date().toISOString()})}
for(const c of cuts){const b=document.createElement('button');b.textContent=c.id;b.onclick=()=>choose(c);document.querySelector('#cuts').append(b)}
v.addEventListener('timeupdate',()=>{if(!current)return;status.textContent=current.id+' | source '+v.currentTime.toFixed(6)+'s | '+v.playbackRate+'× | '+(v.paused?'paused':'playing')+' | muted '+v.muted+' | offset '+offset;if(v.currentTime>=current.end&&!v.paused){v.pause();history.push({type:'end',id:current.id,sourceTime:v.currentTime,at:new Date().toISOString()})}});
document.querySelector('#toggle').onclick=()=>v.paused?v.play():v.pause();document.querySelector('#restart').onclick=()=>current&&choose(current);document.querySelector('#captionToggle').onclick=()=>{const c=document.querySelector('#caption');c.hidden=!c.hidden};document.querySelector('#reframe').onclick=()=>{offset=offset?0:-48;v.style.top=offset+'px';status.textContent+=(offset?' | preview up48':' | original')};
window.reviewObservation={get current(){return current},get history(){return history},get framingOffset(){return offset}};
</script></html>`;
fs.writeFileSync(html,body);
const prep={schemaVersion:1,preparedAt:new Date().toISOString(),sourcePath:execution.sourcePath,sourceSha256:execution.sourceSha256,alias,aliasIsHardlink:true,noSourceByteChange:true,helperPath:html,helperSha256:sha(html),url:'http://127.0.0.1:9250/balatro-native-action-playback-v3.html',candidateIntervals:cuts,playbackRate:1,muted:true,captionCenter:[960,970],captionStyle:'boxed-white-forest-v1',captionIsExistingTextSample:true,footageAdopted:false,finalFramingApproved:false,creditException:'pending',newImagesGitAdded:0,researchChanges:0};
fs.writeFileSync(path.join(base,'native-action-playback-helper-preparation-v3.json'),JSON.stringify(prep,null,2)+'\n');
console.log(JSON.stringify({html,url:prep.url,hardlink:true,adopted:false}));
