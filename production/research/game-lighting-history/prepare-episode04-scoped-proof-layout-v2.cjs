const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production',d='motion-canvas/src/projects/game-lighting-history-04/spatial',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const out=b+'/scoped-proof-layout-plan-v2.json';if(fs.existsSync(path.join(root,out)))throw Error('Existing v2 plan preserved');
const records=[];
for(const name of ['vsm','upscaling']){
 const review=b+'/'+name+'-spatial-proof-direct-review-v1.json',r=read(review);if(!r.allPlannedPosesDirectlyViewed||!r.modelLayoutCorrectionRequired)throw Error('Direct correction evidence required');
 let model=fs.readFileSync(path.join(root,d+'/'+name+'-model-v1.tsx'),'utf8');
 const changes=name==='vsm'?[
  ["[x,-240,240]","[x,-200,150]"],
  ["190+(-240-190)*.53,55+(240-55)*.53","190+(-200-190)*.53,55+(150-55)*.53"]
 ]:[
  ["Independent small-grid/2-rendered-4-displayed diagrams","Independent small-grid/one-complete-adjacent-frame-interval diagrams"],
  ["{x:-600,label:'렌더 R0',c:P.teal,g:false},{x:-200,label:'생성 G½',c:P.orange,g:true},{x:200,label:'렌더 R1',c:P.teal,g:false},{x:600,label:'생성 G1½',c:P.orange,g:true}","{x:-470,label:'렌더 R0',c:P.teal,g:false},{x:0,label:'생성 G½',c:P.orange,g:true},{x:470,label:'렌더 R1',c:P.teal,g:false}"],
  ["for(let i=0;i<3;i++)f.add(fs.path(()=>[[-455+i*400,0,55],[-345+i*400,0,55]],P.yellow,p));","for(let i=0;i<2;i++)f.add(fs.path(()=>[[-320+i*470,0,55],[-155+i*470,0,55]],P.yellow,p));"],
  ["표시 ${p()<.5?2:4}","표시 ${p()<.5?2:3}"],
  ["['표시 프레임','4개']","['표시 프레임','3개']"]
 ];
 for(const [a,z]of changes){if(!model.includes(a))throw Error('Exact patch input missing:'+a);model=model.replace(a,z);}
 const mp=d+'/'+name+'-model-v2.tsx';fs.writeFileSync(path.join(root,mp),model);
 const modes=name==='vsm'?[5]:[5,6],files=[];
 for(const mode of modes){const sp=d+'/'+name+'-layout-proof'+mode+'-v2.tsx';fs.writeFileSync(path.join(root,sp),`import {makeScene2D} from '@motion-canvas/2d';\nimport {waitFor} from '@motion-canvas/core';\nimport {DARK as P} from '../../../styles/research-dark';\nimport {heading} from '../../game-lighting-history-shared/depth-space';\nimport {${name}Model} from './${name}-model-v2';\nexport default makeScene2D(function*(view){view.fill(P.background);const m=${name}Model();view.add(m.node);view.add(heading('${name==='vsm'?'18v':'18t'}','${name==='vsm'?'SMRT: 표본과 제목의 공간 분리':mode===5?'인접 렌더 프레임 사이의 생성':'해상도·렌더·표시·지연의 별도 기록'}','수정 구간 모델 검수 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[${mode*2}]);yield*waitFor(.3);yield*m.transition(m.poses[${mode*2+1}],3.4);yield*waitFor(.3);});\n`);files.push(sp);}
 const project=d+'/'+name+'-layout-project-v2.ts';fs.writeFileSync(path.join(root,project),`import {makeProject} from '@motion-canvas/core';\n${modes.map((m,i)=>`import p${i} from './${name}-layout-proof${m}-v2?scene';`).join('\n')}\nexport default makeProject({scenes:[${modes.map((_,i)=>'p'+i).join(',')}]});\n`);
 const meta=read(d+'/'+name+'-project-v1.meta');meta.shared.range=[0,(modes.length*240-1)/60];fs.writeFileSync(path.join(root,project.replace(/\.ts$/,'.meta')),JSON.stringify(meta,null,2)+'\n');
 records.push({name,sourceReview:{path:review,sha256:sha(review)},preservedV1Model:{path:d+'/'+name+'-model-v1.tsx',sha256:sha(d+'/'+name+'-model-v1.tsx')},project,model:mp,modes,plannedFrames:modes.length*240,sampleFrames:modes.flatMap((_,i)=>[9+i*240,120+i*240,231+i*240]),inputs:[mp,...files,project].map(p=>({path:p,sha256:sha(p)})),renderStarted:false,pixelsReviewed:false});
}
const mobile=read(b+'/mobile-spatial-proof-plan-v1.json'),mobileMeta=mobile.project.replace(/\.ts$/,'.meta');if(fs.existsSync(path.join(root,mobileMeta)))throw Error('Existing mobile metadata preserved');const m=read(d+'/visibility-project-v1.meta');m.shared.range=[0,(mobile.plannedFrames-1)/60];fs.writeFileSync(path.join(root,mobileMeta),JSON.stringify(m,null,2)+'\n');
const config='motion-canvas/vite.game-lighting-history.chapter-v4.config.ts';let code=fs.readFileSync(path.join(root,config),'utf8');const anchor='"./src/projects/game-lighting-history-04/spatial/visibility-project-v1.ts"';if(!code.includes(anchor))throw Error('Exact config anchor missing');code=code.replace(anchor,anchor+','+['mobile-project-v1.ts','vsm-layout-project-v2.ts','upscaling-layout-project-v2.ts'].map(p=>JSON.stringify('./src/projects/game-lighting-history-04/spatial/'+p)).join(','));fs.writeFileSync(path.join(root,config),code);
fs.writeFileSync(path.join(root,out),JSON.stringify({preparedAt:new Date().toISOString(),scope:'Only direct-reviewed layout findings corrected in independent v2 models; v1 pixels/models/records preserved. No narration or episode approval.',primarySource:{url:'https://images.nvidia.com/aem-dam/Solutions/geforce/ada/ada-lovelace-architecture/nvidia-ada-gpu-science.pdf',claim:'A generated display frame lies between adjacent rendered frame inputs; this finite diagram shows2rendered+1generated, not a frame-rate benchmark.'},records,mobileMetadata:{path:mobileMeta,sha256:sha(mobileMeta)},config,renderStarted:false,allPixelsReviewed:false,finalVideoProduced:false,localOnly:true},null,2)+'\n');console.log(JSON.stringify(records.map(x=>({name:x.name,frames:x.plannedFrames}))));
