const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production',d='motion-canvas/src/projects/game-lighting-history-04/spatial',name='postprocess-layout',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),dest=b+'/'+name+'-spatial-proof-plan-v1.json';
if(fs.existsSync(path.join(root,dest)))throw Error('Frozen scoped proof preserved');
const old=d+'/postprocess-model-v1.tsx',model=d+'/postprocess-model-v2.tsx',review=b+'/postprocess-inspection-spatial-proof-direct-review-v1.json';
const r=read(review);if(!r.allPlannedPosesDirectlyViewed||!r.modelLayoutCorrectionRequired)throw Error('Actual prior finding required');
let code=fs.readFileSync(path.join(root,old),'utf8');
const start=code.indexOf(' const a=layer(0)'),end=code.indexOf(' const b=layer(1)');if(start<0||end<start)throw Error('Original teaching model missing');
code=code.slice(0,start)+` const a=layer(0),s=depthSpace(()=>16,[0,135],1),values=[2,4,16];
 a.add(text('수치 예: y = x / (1 + x)',0,-275,32,P.teal));
 for(const [base,output] of [[-440,false],[440,true]] as [number,boolean][]){
  a.add(s.box(base,30,0,630,280,20,P.surfaceTop));
  a.add(text(output?'출력 축 0~1':'입력 HDR 축 0~16',base,-210,31,P.yellow));
  for(let i=0;i<3;i++){
   const x=base+(i-1)*170,y=values[i]/(1+values[i]);
   a.add(s.box(x,30,20,70,100,()=>220*(output?y*p():values[i]/16),output?P.teal:P.orange));
   a.add(text(()=>output?('y = '+(y*p()).toFixed(3)):('x = '+values[i]),x,255,28));
  }
 }
 note(a,'서로 다른 축 · 입력 고정/출력 계산 · UE의 ACES 곡선을 재현한 것이 아닌 독립 수치 예');

`+code.slice(end);
const scale='()=>50*((1-p())*input[i]+p()*out)';if(!code.includes(scale))throw Error('Exact exposure height missing');code=code.replace(scale,'()=>30*((1-p())*input[i]+p()*out)');
const labels="['가까움','초점면','멀어짐'][i]";if(!code.includes(labels))throw Error('Exact depth labels missing');code=code.replace(labels,"['멀어짐','초점면','가까움'][i]");
const anchor=" d.add(text('초점과 거리',-470,-235,34,P.yellow));";if(!code.includes(anchor))throw Error('Camera anchor missing');code=code.replace(anchor," d.add(ds.box(-470,330,20,95,70,45,P.muted));\n d.add(ds.box(-470,285,30,45,35,25,P.teal));\n d.add(ds.label('카메라',-470,370,90,26,P.ink));\n"+anchor);
fs.writeFileSync(path.join(root,model),code);
const original=read(b+'/postprocess-inspection-spatial-proof-plan-v1.json'),paragraphs=[],files=[];
for(const [ordinal,idx]of[0,1,3].entries()){
 const q=original.paragraphs.find(x=>x.scene==='22p'&&x.sceneParagraph===idx+1);if(!q)throw Error('Original bilingual paragraph missing');
 const file=d+'/'+name+'-proof'+ordinal+'-v1.tsx';
 fs.writeFileSync(path.join(root,file),`import {makeScene2D} from '@motion-canvas/2d';\nimport {waitFor} from '@motion-canvas/core';\nimport {DARK as P} from '../../../styles/research-dark';\nimport {heading} from '../../game-lighting-history-shared/depth-space';\nimport {postprocessModel} from './postprocess-model-v2';\nexport default makeScene2D(function*(view){view.fill(P.background);const m=postprocessModel();view.add(m.node);view.add(heading('22p.${idx+1}','후처리: 입력 단위와 카메라 기준 구별','문구·높이 수정 검수 · 최종 내레이션/실제 게임 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[${idx*2}]);yield*waitFor(.3);yield*m.transition(m.poses[${idx*2+1}],3.4);yield*waitFor(.3);});\n`);
 files.push(file);paragraphs.push({...q,paragraph:ordinal+1,timelineFrom:ordinal*4,sampleTimes:[ordinal*4+.15,ordinal*4+2,ordinal*4+3.85]});
}
const project=d+'/'+name+'-project-v1.ts';fs.writeFileSync(path.join(root,project),`import {makeProject} from '@motion-canvas/core';\n${files.map((p,i)=>`import p${i} from './${path.basename(p,'.tsx')}?scene';`).join('\n')}\nexport default makeProject({scenes:[p0,p1,p2]});\n`);
const meta=read(d+'/postprocess-inspection-project-v1.meta');meta.shared.range=[0,719/60];fs.writeFileSync(path.join(root,project.replace(/\.ts$/,'.meta')),JSON.stringify(meta,null,2)+'\n');
const cfgp='motion-canvas/vite.game-lighting-history.chapter-v4.config.ts',a='"./src/projects/game-lighting-history-04/spatial/postprocess-inspection-project-v1.ts"';let cfg=fs.readFileSync(path.join(root,cfgp),'utf8');if(!cfg.includes(a))throw Error('Owned config anchor missing');fs.writeFileSync(path.join(root,cfgp),cfg.replace(a,a+','+JSON.stringify('./'+project.replace(/^motion-canvas\//,''))));
const inputs=[...files,project,project.replace(/\.ts$/,'.meta'),model,'motion-canvas/src/projects/game-lighting-history-shared/depth-space.tsx','motion-canvas/src/styles/research-dark.ts','projects/game-lighting-history-04/script/narration.ko.json','projects/game-lighting-history-04/script/narration.en.json'].map(p=>({path:p,sha256:sha(p)}));
fs.writeFileSync(path.join(root,dest),JSON.stringify({createdAt:new Date().toISOString(),name,style:'research-black-v1',scope:'Only22p.1/2/4 corrected model proof; other24paragraphs preserve prior rendered poses; no final narration/pixel/native approval.',paragraphs,duration:12,plannedFrames:720,inputs,project,historicalFindings:{path:review,sha256:sha(review)},modelMotionProofReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false,localOnly:true},null,2)+'\n');console.log(JSON.stringify({paragraphs:3,poses:9,frames:720,preparedOnly:true}));
