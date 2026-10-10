const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),dst='motion-canvas/src/projects/game-lighting-history-03/spatial';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,s)=>fs.writeFileSync(path.join(root,p),s),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const plan=read('projects/game-lighting-history-03/production/foundation-proof-plan-v1.json'),qa=read('production/research/game-lighting-history/local/foundation-proof-v1/qa/extraction.json');
if(fs.existsSync(path.join(root,dst,'foundation-models-v2.tsx')))throw Error('Existing correction preserved');
for(const i of plan.modelInputs)if(sha(i.path)!==i.sha256)throw Error('Baseline inputs changed');
const defects=[
 {scene:'overview',paragraph:1,reason:'Growing navigation boxes occlude their labels'},
 {scene:'12a',paragraph:4,reason:'Voxel upper layer overlaps central model heading'},
 {scene:'13b',paragraph:1,reason:'Three boxes labeled BLAS A/A/B obscure the shared BLAS instance relationship;TLAS and labels overlap geometry'},
 {scene:'14a',paragraph:4,reason:'N label touches standard-error equation;relative height needs explicit meaning'},
 {scene:'14b',paragraph:1,reason:'Previous-output box overlaps heading and source labels'},
 {scene:'14b',paragraph:2,reason:'Stage labels partially occluded by top faces'},
 {scene:'14b',paragraph:3,reason:'Extra geometry only on quarter-pixel grid distracts from equal image-domain comparison'},
 {scene:'14b',paragraph:7,reason:'Input/result/failure labels partially occluded by top faces'},
 ...[1,2,3].map(paragraph=>({scene:'conclusion',paragraph,reason:'Growing navigation boxes occlude labels'}))
];
const review={reviewedAt:new Date().toISOString(),scope:'All93 before/middle/after frames on16 boards directly read;baseline retained. Spatial model proof only,not narration timing or final episode.',video:qa.video,inputs:qa.modelInputs,wholeDecodeExit:qa.wholeDecode.exitCode,boards:qa.boards.map(b=>({...b,directlyViewed:true})),full93ProofFramesDirectlyRead:true,blockingDefects:defects,modelMotionProofReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false,finalCaptionPixelsApproved:false,actualFootageQuotaSeconds:0,localOnlyImages:true};
write('projects/game-lighting-history-03/production/foundation-animated-proof-review-v1.json',JSON.stringify(review,null,2)+'\n');
let code=fs.readFileSync(path.join(root,dst,'foundation-models-v1.tsx'),'utf8');
function replace(a,b){if(!code.includes(a))throw Error('Expected baseline missing:'+a.slice(0,60));code=code.replace(a,b);}
replace("const d=layer(3),sv=space(-130,.95);","const d=layer(3),sv=depthSpace(()=>22,[-130,155],.85);");
replace("text('복셀: 공간을 나눈 저장 칸',0,-195","text('복셀: 공간을 나눈 저장 칸',0,-235");
const old=code.slice(code.indexOf(' const a=layer(0),s=space(0,1);',code.indexOf('export function dynamicRayModel')),code.indexOf(' const b=layer(1)',code.indexOf('export function dynamicRayModel')));
replace(old,` const a=layer(0),s=depthSpace(()=>0,[0,80],1);
 // TLAS has three instances;two distinct references lead to ONE shared BLAS A.
 const instances=[{x:-440,label:'인스턴스 1 → A',to:-300},{x:0,label:'인스턴스 2 → A',to:-300},{x:440,label:'인스턴스 3 → B',to:300}];
 for(const i of instances)a.add(s.box(i.x,-140,80,200,150,55,P.orange));
 for(const x of[-300,300])a.add(s.box(x,180,0,250,190,65,P.teal));
 for(const i of instances)a.add(s.path(()=>[[i.x,-65,95],[i.to,80,50]],P.yellow,p));
 for(const i of instances)a.add(text(i.label,i.x,-170,28,P.orange));
 for(const[x,label]of[[-300,'共有 BLAS A'.replace('共有','공유')],[300,'BLAS B']]as[number,string][])a.add(text(label,x,105,32,P.teal));
 a.add(text('TLAS: 세 인스턴스와 각각의 변환',0,-250,34,P.orange));
 a.add(text('인스턴스 1·2 → 같은 기하 BLAS A',0,295,31,P.yellow));note(a,'BLAS는 기하 · TLAS는 인스턴스 · 서로 다른 가속 구조');

`);
replace("const d=layer(3),sd=space();bars(d,sd,[8,4],['N','4N']);", "const d=layer(3),sd=space();bars(d,sd,[6,3],['N: SE 1','4N: SE ½']);");
replace("text('SE ∝ 1/√N',0,-195", "text('SE ∝ 1/√N',0,-235");
replace("note(d,'상관 표본·시간 필터·전체 게임 성능에 그대로 적용하지 않기');", "note(d,'막대 높이: 상대 표준오차 · 상관 표본/시간 필터/전체 성능에는 별도 조건');");
replace("const a=layer(0),s=space();\n for(const[x,y,z,label,c]", "const a=layer(0),s=depthSpace(()=>0,[0,100],1);\n for(const[x,y,z,label,c]");
replace("[-100,-110,125,'이전 출력'", "[-100,-110,30,'이전 출력'");
replace("s.label(label,x,y,z+130,29,c)", "s.label(label,x,y,z+190,29,c)");
replace("[[-100,-110,200],[480,20,90]]", "[[-100,-110,115],[480,20,90]]");
replace("text('DLSS 2 · 2020 · 현재 입력과 시간 정보',0,-195", "text('DLSS 2 · 2020 · 현재 입력과 시간 정보',0,-250");
replace("const b=layer(1),sb=space();for(const[x,label,c]", "const b=layer(1),sb=depthSpace(()=>0,[0,100],1);for(const[x,label,c]");
replace("sb.label(label,x,0,145,33,c)", "sb.label(label,x,0,220,33,c)");
replace("c.add(new Node({opacity:p,children:[cb.box(0,0,18,130,130,90,P.orange)]}));", "c.add(cb.path(()=>[[-180,260,18],[180,260,18]],P.orange,p));");
replace("const g=layer(6),sg=space();for(const[x,label,c]", "const g=layer(6),sg=depthSpace(()=>0,[0,100],1);for(const[x,label,c]");
replace("sg.label(label,x,0,165,32,c)", "sg.label(label,x,0,235,32,c)");
replace("n.add(s.label(labels[j][i],x,0,180,30,c))", "n.add(s.label(labels[j][i],x,0,260,30,c))");
write(`${dst}/foundation-models-v2.tsx`,code);
const selected=defects.map(d=>plan.paragraphs.find(p=>p.scene===d.scene&&p.paragraph===d.paragraph));
if(selected.some(x=>!x)||selected.length!==11)throw Error('Correction selection mismatch');
const runtime=fs.readFileSync(path.join(root,dst,'foundation-proof-runtime-v1.tsx'),'utf8').replace('./foundation-models-v1','./foundation-models-v2').replace('./foundation-proof-data-v1.json','./foundation-fix-data-v2.json');
write(`${dst}/foundation-fix-runtime-v2.tsx`,runtime);
write(`${dst}/foundation-fix-data-v2.json`,JSON.stringify(selected,null,2)+'\n');
const names=[];selected.forEach((d,i)=>{const n=`foundation-fix-${String(i).padStart(2,'0')}-v2`;names.push(n);write(`${dst}/${n}.tsx`,`import {foundationProof} from './foundation-fix-runtime-v2';\nexport default foundationProof(${i});\n`);write(`${dst}/${n}.meta`,JSON.stringify({version:0,timeEvents:[],seed:2838358939},null,2)+'\n');});
write(`${dst}/foundation-fix-project-v2.ts`,`import {makeProject} from '@motion-canvas/core';\n${names.map((n,i)=>`import p${i} from './${n}?scene';`).join('\n')}\nexport default makeProject({scenes:[${names.map((_,i)=>`p${i}`).join(',')}]});\n`);
write(`${dst}/foundation-fix-project-v2.meta`,fs.readFileSync(path.join(root,dst,'foundation-project-v1.meta'),'utf8'));
const cfg='motion-canvas/vite.game-lighting-history.black-lookdev-v2.config.ts';let config=fs.readFileSync(path.join(root,cfg),'utf8');config=config.replace("'./src/projects/game-lighting-history-03/spatial/foundation-project-v1.ts'","'./src/projects/game-lighting-history-03/spatial/foundation-project-v1.ts','./src/projects/game-lighting-history-03/spatial/foundation-fix-project-v2.ts'");write(cfg,config);
write('projects/game-lighting-history-03/production/foundation-fix-plan-v2.json',JSON.stringify({createdAt:new Date().toISOString(),scope:'Only11 directly observed faulty paragraphs;33s spatial correction proof. All original31 bilingual paragraphs and approved current PCM unchanged.',baselineReview:'projects/game-lighting-history-03/production/foundation-animated-proof-review-v1.json',defects,paragraphs:selected,mathChecks:plan.mathChecks,modelInputs:['foundation-models-v2.tsx','foundation-fix-runtime-v2.tsx','foundation-fix-data-v2.json'].map(n=>({path:`${dst}/${n}`,sha256:sha(`${dst}/${n}`)})),plannedFrames:1980,expectedDuration:33,actualPixelsReviewed:false,modelMotionProofReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false,localOnlyImages:true},null,2)+'\n');
console.log(JSON.stringify({baselineFramesRead:93,boardsRead:16,correctedParagraphs:11,plannedSeconds:33,approved:false,PCMChanged:false}));
