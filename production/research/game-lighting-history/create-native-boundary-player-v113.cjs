// Reuse already-inspected native sources; controls are for bounded review only.
const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const a=read('projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json');
const rows=[
 {id:'resident-end-boundary',source:'re',ranges:[[21,24]],ko:'원본 비교 표시가 끝나고 브랜드 카드로 바뀌는 정확한 경계를 확인합니다. 최종 예시 승인 아님.'},
 {id:'nba-end-boundary',source:'nba',ranges:[[39,52]],ko:'농구 장면의 실제 팔·유니폼 변화와 다음 안내 카드 시작을 분리합니다. 카드 시간은 실제 게임 비중에서 제외합니다.'},
 {id:'focus-preceding-native',source:'post',ranges:[[2230,2325]],ko:'아직 채택하지 않은 앞의 초점 시연에서 실제 입력 변경·카메라·가림·결과를 확인합니다. 길이나 파일 형식으로 실제 비중을 승인하지 않습니다.'}
 ];
for(const r of rows){const source=a.sources[r.source];if(!source)throw Error('Exact source key required '+r.source);r.path=source.path;r.sha256=source.sha256;if(sha(r.path)!==r.sha256)throw Error('Source changed '+r.id);}
const src='production/research/game-lighting-history/local/guided-source-motion-review-v102.html',out='production/research/game-lighting-history/local/native-boundary-review-v113.html';if(fs.existsSync(out))throw Error('Preserve prior player');
let page=fs.readFileSync(src,'utf8');const start=page.indexOf('<script>const rows='),end=page.indexOf(';const pick=',start);if(start<0||end<0)throw Error('Player structure changed');
page=page.slice(0,start)+'<script>const rows='+JSON.stringify(rows).replaceAll('<','\\u003c')+page.slice(end);page=page.replace('추가 시연 원본 · 움직임 검수','원본 경계와 추가 동작 · 검수');fs.writeFileSync(out,page);console.log(JSON.stringify({out,rows:rows.map(x=>x.id),newImages:0,approved:false}));
