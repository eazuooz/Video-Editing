// Editable screen-space observation targets; these are not measured world coordinates.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),B='projects/game-lighting-history-04/production/',pp=B+'part1-final-input-plan-v240.json';
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const layers={
 'horizon-detail-motion:native':{label:'같은 무늬 경계 · 화면 좌표 관찰',labelX:650,labelY:96,boxes:[
  {from:0,to:5.68,x0:320,y0:145,x1:332,y1:145,width:310,height:280,color:'red'},
  {from:0,to:5.68,x0:1280,y0:145,x1:1284,y1:145,width:310,height:280,color:'0x73c7c2'}]},
 'outer-displayed-frames:native':{matteFrom:'bottom',label:'원본 표시 프레임 값 · 시뮬레이션 횟수 아님',labelX:470,labelY:680,boxes:[
  {from:0,to:5.7,x0:880,y0:150,x1:880,y1:150,width:410,height:450,color:'red'},
  {from:5.7,to:12,x0:1660,y0:0,x1:1660,y1:0,width:250,height:360,color:'red'},
  {from:12,to:14.2,x0:0,y0:0,x1:0,y1:0,width:255,height:365,color:'red'},
  {from:14.2,to:16.32,x0:1660,y0:0,x1:1660,y1:0,width:250,height:360,color:'red'}]},
 'cyber-light-reconstruction:native':{label:'표면 / 빛을 구별 · 원본 묶음 조건',labelX:520,labelY:100,boxes:[
  {from:0,to:7.2,x0:130,y0:310,x1:100,y1:420,width:480,height:250,color:'red'},
  {from:0,to:7.2,x0:1040,y0:310,x1:1030,y1:420,width:480,height:250,color:'0x73c7c2'}]},
 'fortnite-mobile-test:native':{label:'원본 진단 그래프 / 실제 표면 · 별도 자료',labelX:690,labelY:90,boxes:[
  {from:0,to:18.99,x0:105,y0:90,x1:105,y1:90,width:545,height:650,color:'red'}]}
};
const out=B+'part1-visual-layers-v244.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve layer plan');
fs.writeFileSync(path.join(root,out),JSON.stringify({preparedAt:new Date().toISOString(),inputPlan:ref(pp),layers,coordinateSystem:'1920x1080 final transformed source pixels; manually selected/interpolated screen targets pending moving verification',sourcesDirectlyRead:['horizon-super-resolution','outer-generated-display','cyber-light-reconstruction','fortnite-mobile-profiling'].map(id=>ref('production/research/game-lighting-history/local/part1-native-review-v166/samples/'+id+'/board-01.png')),actualWorldMeasurements:false,allMovingPixelsReviewed:false,allFinalPixelsReviewed:false,uploaded:false,newGitImages:0},null,2)+'\n');
console.log(JSON.stringify({layerGroups:4,finalApproved:false}));
