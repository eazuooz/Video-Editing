const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),dst='motion-canvas/src/projects/game-lighting-history-03/spatial';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,s)=>fs.writeFileSync(path.join(root,p),s),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const specs=[
 {scene:'overview',model:'navigationModel',modes:[0],titles:['표현·가속·재사용의 전체 순서']},
 {scene:'12a',model:'representationModel',modes:[0,1,2,3,4,5,6,7],titles:['화면 깊이·거리장·공간 격자','깊이 버퍼가 저장한 첫 표면','거리장 부호와 표면 거리','복셀에 저장하는 서로 다른 값','주변 가림과 빛의 전달','화면 질의와 세계 질의','얇은 구조와 표현 해상도','공간 표현에서 삼각형 탐색으로']},
 {scene:'13b',model:'dynamicRayModel',modes:[0,1,2,3,4,5],titles:['BLAS와 TLAS의 다른 역할','인스턴스 변환과 정점 변형','갱신 비용과 탐색 효율','래스터화와 선택된 레이 효과','Battlefield V의 DXR 반사','화면 밖 정보와 표본 노이즈']},
 {scene:'14a',model:'samplingModel',modes:[0,1,2,3,4,5],titles:['기여와 선택 확률','확률을 바꿀 때 생기는 편향','확률 보정과 분산','표본 수와 표준오차','시간 누적과 표면 대응','물체와 카메라의 별도 대응']},
 {scene:'14b',model:'temporalModel',modes:[0,1,2,3,4,5,6],titles:['DLSS 2의 현재·이전 입력','렌더링·재구성·표시','픽셀 수와 전체 비용','움직임 벡터의 규약','새로 드러난 표면','얇은 구조와 시간적 잔상','입력·결과·실패 조건']},
 {scene:'conclusion',model:'navigationModel',modes:[1,2,3],titles:['질의·저장·선택의 다른 정보','기하 공급과 조명 갱신','다음 편의 그림자·경로·최종 복원']}
];
const planPath='projects/game-lighting-history-03/production/foundation-proof-plan-v1.json';
if(fs.existsSync(path.join(root,planPath)))throw Error('Existing scoped plan preserved');
const scripts={};for(const lang of['ko','en'])scripts[lang]=read(`projects/game-lighting-history-03/script/narration.${lang}.json`);
const paragraphs=[];for(const spec of specs){const ko=scripts.ko.scenes.find(x=>x.id===spec.scene),en=scripts.en.scenes.find(x=>x.id===spec.scene);if(ko.lines.length!==spec.modes.length||en.lines.length!==ko.lines.length)throw Error('Full paragraph topology changed');for(let i=0;i<ko.lines.length;i++)paragraphs.push({scene:spec.scene,paragraph:i+1,model:spec.model,mode:spec.modes[i],title:spec.titles[i],ko:ko.lines[i],en:en.lines[i],plannedFrom:paragraphs.length*3});}
if(paragraphs.length!==31)throw Error('Expected31 full paragraphs');
write(`${dst}/foundation-proof-data-v1.json`,JSON.stringify(paragraphs,null,2)+'\n');
write(`${dst}/foundation-proof-runtime-v1.tsx`, `import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {representationModel,dynamicRayModel,samplingModel,temporalModel,navigationModel} from './foundation-models-v1';
import data from './foundation-proof-data-v1.json';
const factories={representationModel,dynamicRayModel,samplingModel,temporalModel,navigationModel};
export function foundationProof(i:number){return makeScene2D(function*(view){const d=data[i],m=factories[d.model as keyof typeof factories]();view.fill(P.background);view.add(heading(d.scene+' · 문단 '+d.paragraph,d.title,'자료·확률·시간·오류의 관계','게임 렌더링 역사 3편'));view.add(m.node);m.reset(m.poses[d.mode*2]);view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={d.title+'\\n입체·정보·움직임·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);yield*waitFor(.5);yield*m.transition(m.poses[d.mode*2+1],2);yield*waitFor(.5);});}
`);
const names=[];for(let i=0;i<paragraphs.length;i++){const n=`foundation-${String(i).padStart(2,'0')}-v1`;names.push(n);write(`${dst}/${n}.tsx`,`import {foundationProof} from './foundation-proof-runtime-v1';\nexport default foundationProof(${i});\n`);write(`${dst}/${n}.meta`,JSON.stringify({version:0,timeEvents:[],seed:2838358939},null,2)+'\n');}
write(`${dst}/foundation-project-v1.ts`,`import {makeProject} from '@motion-canvas/core';\n${names.map((n,i)=>`import p${i} from './${n}?scene';`).join('\n')}\nexport default makeProject({scenes:[${names.map((_,i)=>`p${i}`).join(',')}]});\n`);
write(`${dst}/foundation-project-v1.meta`,fs.readFileSync(path.join(root,dst,'work-project-v2.meta'),'utf8'));
const cfg='motion-canvas/vite.game-lighting-history.black-lookdev-v2.config.ts';let config=fs.readFileSync(path.join(root,cfg),'utf8');if(config.includes('foundation-project-v1.ts'))throw Error('Project already registered');config=config.replace("'./src/projects/game-lighting-history-03/spatial/work-project-v2.ts'","'./src/projects/game-lighting-history-03/spatial/work-project-v2.ts','./src/projects/game-lighting-history-03/spatial/foundation-project-v1.ts'");write(cfg,config);
const checks=[{name:'equal-discrete-mean',actual:(2+8)/2,expected:5},{name:'uncorrected-unequal-mean',actual:.25*2+.75*8,expected:6.5},{name:'probability-corrected-mean',actual:.25*(2/(2*.25))+.75*(8/(2*.75)),expected:5},{name:'quadruple-independent-samples-error-ratio',actual:Math.sqrt(1/4),expected:.5},{name:'half-width-half-height-pixels',actual:.5*.5,expected:.25}];if(checks.some(c=>Math.abs(c.actual-c.expected)>1e-10))throw Error('Math failure');
const primarySources=[
 {url:'https://dev.epicgames.com/documentation/en-us/unreal-engine/mesh-distance-fields-in-unreal-engine',directlyReadScope:'Signed closest-surface distance,positive exterior/negative interior,sphere tracing,offline generation,volume resolution and thin structures,global distance field clipmaps.',use:'12a representation distinction,not a game performance claim'},
 {url:'https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html',directlyReadScope:'BLAS/TLAS and instance matrix;updateable/static traversal tradeoff;PERFORM_UPDATE and input geometry/vertex constraints;BLAS update requires dependent TLAS update.',use:'13b rigid/geometry update and cost tradeoff,not a universal speed ranking'},
 {url:'https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/',directlyReadScope:'Official2020-03-23announcement,current low-resolution input,engine motion vectors and prior high-resolution temporal feedback.',use:'14b DLSS2 date and input roles;no invented network implementation'}
];
const plan={createdAt:new Date().toISOString(),scope:'Remaining31 complete bilingual paragraph explanations for episode03;93s scoped spatial/motion proof only. Original current PCM and all scripts unchanged. Not final narration timing,footage allocation or final episode.',style:'research-black-v1',scriptInputs:['ko','en'].map(l=>({path:`projects/game-lighting-history-03/script/narration.${l}.json`,sha256:sha(`projects/game-lighting-history-03/script/narration.${l}.json`)})),paragraphs,primarySources,mathChecks:checks,modelInputs:['foundation-models-v1.tsx','foundation-proof-runtime-v1.tsx','foundation-proof-data-v1.json'].map(n=>({path:`${dst}/${n}`,sha256:sha(`${dst}/${n}`)})),plannedFrames:5580,expectedDuration:93,actualPixelsReviewed:false,modelMotionProofReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false,localOnlyImages:true};
write(planPath,JSON.stringify(plan,null,2)+'\n');console.log(JSON.stringify({plan:planPath,paragraphs:31,mathChecks:checks.length,renderStarted:false,pcmChanged:false}));
