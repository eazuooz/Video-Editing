// Local native-motion review controls. Playback never approves source or QA.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const script='projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json';
const extra='projects/game-lighting-history-04/script/physical-part3-hogwarts-observation.koen.v81.json';
const classification='projects/game-lighting-history-04/production/focus-analysis-classification-v96.json';
const a=read(script),b=read(extra),c=read(classification),excluded=new Set(c.rows.map(x=>x.id));
const rows=a.scenes.filter(x=>x.ranges.length&&!excluded.has(x.id)).map(x=>({...x,path:a.sources[x.source].path,sha256:a.sources[x.source].sha256}));
for(const x of b.scenes){if(!x.sourcePath)throw Error('Exact supplementary source required');rows.push({...x,path:x.sourcePath,sha256:hash(x.sourcePath)});}
for(const x of rows)if(hash(x.path)!==x.sha256)throw Error('Changed native '+x.id);
const output='production/research/game-lighting-history/local/guided-source-motion-review-v102.html';
if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing review controls');
const data=JSON.stringify(rows).replaceAll('<','\\u003c');
const page=`<!doctype html><meta charset="utf-8"><title>추가 시연 원본 · 움직임 검수</title>
<style>body{background:#111;color:#eee;font:16px Malgun Gothic;margin:8px}button,select{font:16px Malgun Gothic;padding:6px;margin:2px}video{display:block;max-width:900px;width:100%;background:#000}h1{font-size:22px;margin:5px}p{margin:5px}#status{color:#e8cf83}#words{font-size:15px;max-width:1280px;line-height:1.65}#ranges{font-size:12px;color:#73c7c2;margin:5px}</style>
<h1>원본 후보의 정상 속도 검수</h1><p>제안 구간 재생 · 실제 비중/권리/최종 표식/음성 승인과 구별</p>
<label>후보 선택 <select id="scene"></select></label><button id="play">선택 구간 재생</button><button id="pause">일시정지</button><button id="next">다음 후보</button>
<p id="ranges"></p><p id="status" role="status">아직 재생하지 않음</p><video id="v" controls preload="metadata" muted></video><p id="words"></p>
<script>const rows=${data};const pick=document.querySelector('#scene'),v=document.querySelector('#v'),status=document.querySelector('#status');
for(const r of rows){const o=document.createElement('option');o.value=r.id;o.textContent=r.id;pick.append(o)}
let row=null,interval=0,playing=false;function choose(){v.pause();playing=false;row=rows.find(x=>x.id===pick.value);interval=0;v.src='/@fs/${root.replaceAll('\\','/')}/'+row.path;document.querySelector('#words').textContent=row.ko;document.querySelector('#ranges').textContent='native: '+row.ranges.map(x=>x.join('–')).join(', ')+' · rate1 · '+row.path;status.textContent='선택: '+row.id+' · 시작 전'}
async function play(){if(!row)return;interval=0;v.playbackRate=1;v.currentTime=row.ranges[0][0];playing=true;await v.play()}
pick.onchange=choose;document.querySelector('#play').onclick=play;document.querySelector('#pause').onclick=()=>{playing=false;v.pause()};document.querySelector('#next').onclick=()=>{pick.selectedIndex=Math.min(rows.length-1,pick.selectedIndex+1);choose()};
v.ontimeupdate=()=>{if(!row)return;if(playing&&v.currentTime>=row.ranges[interval][1]){interval++;if(interval>=row.ranges.length){playing=false;v.pause();interval=row.ranges.length-1;status.textContent='제안 구간 종료: '+row.id+' · 승인 아님';return}v.currentTime=row.ranges[interval][0]}status.textContent=row.id+' · native '+v.currentTime.toFixed(3)+'s · 구간 '+(interval+1)+'/'+row.ranges.length+' · rate '+v.playbackRate+' · '+(v.paused?'PAUSED':'PLAYING')};
v.onerror=()=>status.textContent='미디어 로드 오류 · 후보 승인 불가';choose();</script>`;
fs.writeFileSync(path.join(root,output),page);
console.log(JSON.stringify({output,scenes:rows.length,sourceHashVerified:true,rendered:false,approved:false,newImages:0}));
