// Native, normal-speed review of specific edits and unassigned debugger actions.
const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const guide=read('projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json');
const dx=read('production/research/game-lighting-history/local/own-frame-submit-v73/execution.json');
const rows=[
 {id:'exposure-context-extended',source:'post',ranges:[[1567.6,1586]],ko:'기존 설명의 예약 구간1586–1602.88을 보존합니다. 카메라와 설정 조작이 보이는 범위를 확인합니다.'},
 {id:'exposure-bias-extended',source:'post',ranges:[[1602.88,1621]],ko:'제한과 바이어스의 실제 조작을 관찰합니다. 히스토그램으로 전환하는 시각은 별도로 확인합니다.'},
 {id:'histogram-mode-transition',source:'post',ranges:[[1621,1644.5]],ko:'일반 화면에서 초록·파랑 진단 표시로 바뀌는 실제 조작과 시각을 확인합니다.'},
 {id:'focus-scale-edit',source:'post',ranges:[[2263,2290]],ko:'2017년의 BokehDOF입니다. Scale 입력 변경과 같은 상자의 윤곽을 비교합니다. 문서 화면은 포함하지 않습니다.'},
 {id:'focus-visualize-entry',source:'post',ranges:[[2290,2325]],ko:'Show/Visualize에서 Depth of Field Layers를 선택하는 조작과 범례, 카메라 변경을 확인합니다.'},
 {id:'debugger-command-submit',source:'ownDx',ranges:[[42,64]],ko:'실제 중단점과 호출 스택을 검수합니다.66초 이후의 도식과 비어 있는 Launch 창은 실제 영상 비중에 쓰지 않습니다.'}
];
const sources={...guide.sources,ownDx:{path:dx.source.media,sha256:dx.source.sha256}};
for(const row of rows){const s=sources[row.source];if(!s||sha(s.path)!==s.sha256)throw Error('Source changed '+row.id);Object.assign(row,s);}
const src='production/research/game-lighting-history/local/native-boundary-controls-v114.html';
const out='production/research/game-lighting-history/local/control-allocation-review-v116.html';
if(fs.existsSync(out))throw Error('Preserve previous review player');
let html=fs.readFileSync(src,'utf8');const start=html.indexOf('<script>const rows='),end=html.indexOf(';const pick=',start);
if(start<0||end<0)throw Error('Player structure changed');
html=html.slice(0,start)+'<script>const rows='+JSON.stringify(rows).replaceAll('<','\\u003c')+html.slice(end);
html=html.replace('원본 경계와 추가 동작 · 검수','설정 조작과 추가 구간 · 검수');
fs.writeFileSync(out,html);console.log(JSON.stringify({out,reviewRows:rows.length,newImages:0,sourceApproval:false}));
