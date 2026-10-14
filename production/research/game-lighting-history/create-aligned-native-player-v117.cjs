const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const guide=read('projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json');
const dx=read('production/research/game-lighting-history/local/own-frame-submit-v73/execution.json');
const rows=[
 {id:'histogram-aligned-open',source:'post',ranges:[[1637.5,1657.5]],ko:'히스토그램 진단 표시가 켜지는 실제 전환과 음성 시점을 대조합니다.'},
 {id:'histogram-aligned-log',source:'post',ranges:[[1657.5,1677]],ko:'로그 분포와 설정값을 구분합니다.'},
 {id:'histogram-aligned-camera',source:'post',ranges:[[1677,1696]],ko:'카메라 변화에 따른 분포를 관찰합니다.'},
 {id:'histogram-aligned-result',source:'post',ranges:[[1696,1715]],ko:'설정, 진단, 최종 표시를 구분합니다.'},
 {id:'focus-scale-before-layers',source:'post',ranges:[[2263,2290]],ko:'2017 BokehDOF Scale 조작과 실제 화면을 대조합니다.'},
 {id:'focus-layers-enable',source:'post',ranges:[[2290,2317.7]],ko:'Depth of Field Layers 표시를 켜는 조작을 관찰합니다.'},
 {id:'focus-legend-expanded',source:'post',ranges:[[2317.7,2330],[2336.02,2349]],ko:'기존 예약 구간2330–2336.02를 보존하고 범례와 카메라를 읽습니다.'},
 {id:'focus-distance-expanded',source:'post',ranges:[[2349,2369]],ko:'거리 설정과 진단 색 변화를 관찰합니다.'},
 {id:'focus-return-expanded',source:'post',ranges:[[2380.1,2396.4]],ko:'예약2369–2380.1 뒤에 일반 화면 복귀를 확인합니다.'},
 {id:'focus-error-expanded',source:'post',ranges:[[2396.4,2415.2]],ko:'초점/블러 변화와 원본 위 주석의 실제 비중을 구별합니다.'},
 {id:'debugger-command-submit',source:'ownDx',ranges:[[42,64]],ko:'중단점, 호출 스택과 단계 이동. CPU 중단을 GPU 완료로 해석하지 않습니다.'}
];
const sources={...guide.sources,ownDx:{path:dx.source.media,sha256:dx.source.sha256}};
for(const row of rows){const s=sources[row.source];if(!s||sha(s.path)!==s.sha256)throw Error('Source changed '+row.id);Object.assign(row,{path:s.path,sha256:s.sha256,sourceId:s.id});}
const src='production/research/game-lighting-history/local/native-boundary-controls-v114.html';
const out='production/research/game-lighting-history/local/aligned-native-review-v117.html';
if(fs.existsSync(out))throw Error('Preserve previous review player');
let html=fs.readFileSync(src,'utf8');const start=html.indexOf('<script>const rows='),end=html.indexOf(';const pick=',start);
if(start<0||end<0)throw Error('Player structure changed');
html=html.slice(0,start)+'<script>const rows='+JSON.stringify(rows).replaceAll('<','\\u003c')+html.slice(end);
html=html.replace('원본 경계와 추가 동작 · 검수','설명 시점과 실제 조작 · 검수');
fs.writeFileSync(out,html);console.log(JSON.stringify({out,reviewRows:rows.length,newImages:0,sourceApproval:false}));
