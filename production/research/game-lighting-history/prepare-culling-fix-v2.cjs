const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),dst='motion-canvas/src/projects/game-lighting-history-03/spatial';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,s)=>fs.writeFileSync(path.join(root,p),s),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const qaPath='production/research/game-lighting-history/local/culling-pipeline-proof-v1/qa/extraction.json',qa=read(qaPath);
if(qa.video.sha256!=='5854340582bcf04b6fd31e8440daba948d05b9e2332c077d28c1e4c5fdb80dd7')throw Error('Baseline changed');
const planPath='projects/game-lighting-history-03/production/culling-fix-proof-plan-v2.json';
if(fs.existsSync(path.join(root,planPath)))throw Error('Existing correction preserved');
qa.boards.forEach(b=>b.directlyViewed=true);
qa.directReview={reviewedAt:new Date().toISOString(),all36PoseFramesDirectlyRead:true,observations:{culling:'Frustum candidates differ from visibility; Early-Z example is conditional; HiZ max reduction and reverse-depth note are consistent. Paragraph2/6 orange candidate protrudes below the wall while fading entirely: incorrect full-occlusion illustration. Paragraph5 wall placement also needs a grounded foreground occluder.',pipeline:'Mesh-group removal,16→4 shading evaluations over the same16 output pixels,2x2 sharing,virtual64 pages versus selected resident pages,and feedback→arrival are distinct. Illustrative quantities are not measured game performance.'},issues:[{chapter:'16aa',paragraphs:[2,5,6],severity:'blocking-model-approval',finding:'Candidate/wall spatial ordering and full projected coverage must be corrected. Preserve this actual failed proof.'}],modelMotionProofReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false};
write(qaPath,JSON.stringify(qa,null,2)+'\n');
write('projects/game-lighting-history-03/production/culling-pipeline-animated-proof-review-v1.json',JSON.stringify({reviewedAt:qa.directReview.reviewedAt,evidence:qaPath,video:qa.video,boards:qa.boards,directReview:qa.directReview,pipelineScopedMotionReviewed:true,cullingScopedMotionReviewed:false,modelMotionProofReviewed:false,fullEpisodeApproved:false},null,2)+'\n');
let model=fs.readFileSync(path.join(root,dst,'culling-model-v1.tsx'),'utf8');
model=model.replace('export function cullingModel()', 'export function cullingModelV2()')
 .replace("m1.add(new Node({opacity:()=>1-progress(),children:[s.box(0,110,15,105,95,90,P.orange)]}));", "// Reveal the hidden candidate through an explicitly transparent wall, then make the wall opaque.\n m1.add(s.box(0,-100,14,105,95,90,P.orange));")
 .replace("m1.add(s.box(0,-30,15,460,25,215,P.surfaceFront));", "m1.add(new Node({opacity:()=>.22+.78*progress(),children:[s.box(0,160,14,480,25,300,P.surfaceFront)]}));")
 .replace("m1.add(s.path(()=>[[0,-235,50],[0,-48,50]],P.teal,progress));", "m1.add(s.path(()=>[[0,290,70],[0,175,70]],P.teal,progress));")
 .replace("'시야 검사 통과 → 가림 검사 필요':'확실히 가려진 경계 → 물체 제출 생략'", "'벽을 투명하게 표시 · 뒤 물체 위치':'불투명 벽 · 전체 경계 가림 → 제출 생략'")
 .replace("m4.add(floor());m4.add(s.box(0,120,15,105,95,100,P.teal));", "m4.add(floor());m4.add(s.box(0,-100,14,105,95,100,P.teal));")
 .replace("s.box(()=>-progress()*360,-30,15,380,25,215,P.surfaceFront)", "s.box(()=>-progress()*540,160,14,480,25,300,P.surfaceFront)")
 .replace("s.box(0,-30,15,380,25,215,P.red)", "s.box(0,160,14,480,25,300,P.red)")
 .replace("m5.add(new Node({opacity:()=>1-progress()*.85,children:[b.box(0,90,16,95,95,70,P.orange)]}));", "m5.add(b.box(0,-65,16,95,95,70,P.orange));")
 .replace("m5.add(b.box(0,-50,16,280,25,170,P.surfaceFront));", "m5.add(new Node({opacity:()=>.22+.78*progress(),children:[b.box(0,100,16,300,25,200,P.surfaceFront)]}));")
 .replace("0,365,24,P.muted", "0,350,24,P.muted")
 .replace("0,360,24,P.muted", "0,350,24,P.muted");
write(`${dst}/culling-model-v2.tsx`,model);
// Orthographic projected containment: every candidate corner must lie inside the foreground wall front face.
function containment(name,object,wall){
 const a=22*Math.PI/180,point=([x,y,z])=>[x*Math.cos(a)-y*Math.sin(a),(x*Math.sin(a)+y*Math.cos(a))*.48-z];
 const [ox,oy,oz,ow,od,oh]=object,[wx,wy,wz,ww,wd,wh]=wall;
 const face=[[-ww/2,wd/2,0],[ww/2,wd/2,0],[ww/2,wd/2,wh],[-ww/2,wd/2,wh]].map(([x,y,z])=>point([wx+x,wy+y,wz+z]));
 const corners=[];for(const x of[-ow/2,ow/2])for(const y of[-od/2,od/2])for(const z of[0,oh])corners.push(point([ox+x,oy+y,oz+z]));
 const inside=q=>{const c=face.map((v,i)=>{const n=face[(i+1)%4];return(n[0]-v[0])*(q[1]-v[1])-(n[1]-v[1])*(q[0]-v[0]);});return c.every(x=>x>=-1e-8)||c.every(x=>x<=1e-8);};
 if(!corners.every(inside))throw Error(name+' candidate not fully covered');
 return{name,object,wall,projectedCandidateCorners:corners,projectedWallFace:face,all8CornersCovered:true,wallIsInFront:true,convention:'yaw22 degrees, orthographic .48 y projection; visible front y+; full projected wall front face containment; independent diagram geometry'};
}
const checks=[containment('paragraph2',[0,-100,14,105,95,90],[0,160,14,480,25,300]),containment('paragraph5-closed',[0,-100,14,105,95,100],[0,160,14,480,25,300]),containment('paragraph6-right',[0,-65,16,95,95,70],[0,100,16,300,25,200])];
let runtime=fs.readFileSync(path.join(root,dst,'culling-pipeline-proof-runtime-v1.tsx'),'utf8').replace("import {cullingModel} from './culling-model-v1';","import {cullingModelV2} from './culling-model-v2';").replace('cullingModel()','cullingModelV2()');
write(`${dst}/culling-fix-proof-runtime-v2.tsx`,runtime);
const imports=[],scenes=[];for(const [id,i]of[1,4,5].entries()){const n=`culling-fix${id}-v2`;write(`${dst}/${n}.tsx`,`import {workProof} from './culling-fix-proof-runtime-v2';\nexport default workProof(0,${i});\n`);write(`${dst}/${n}.meta`,JSON.stringify({version:0,timeEvents:[],seed:2838358939},null,2)+'\n');imports.push(`import p${id} from './${n}?scene';`);scenes.push(`p${id}`);}
write(`${dst}/work-project-v2.ts`,`import {makeProject} from '@motion-canvas/core';\n${imports.join('\n')}\nexport default makeProject({scenes:[${scenes.join(',')}]});\n`);write(`${dst}/work-project-v2.meta`,fs.readFileSync(path.join(root,dst,'work-project-v1.meta'),'utf8'));
const cfg='motion-canvas/vite.game-lighting-history.black-lookdev-v2.config.ts';let config=fs.readFileSync(path.join(root,cfg),'utf8');config=config.replace("'./src/projects/game-lighting-history-03/spatial/work-project-v1.ts'", "'./src/projects/game-lighting-history-03/spatial/work-project-v1.ts','./src/projects/game-lighting-history-03/spatial/work-project-v2.ts'");write(cfg,config);
const plan={createdAt:new Date().toISOString(),scope:'Only3 defective culling paragraph proofs;9 seconds planned. Correct original spatial ordering, preserve all baseline proof/media, no PCM/timing change.',baseline:qaPath,baselineVideoSha256:qa.video.sha256,geometryChecks:checks,chapters:['16aa'],paragraphs:[2,5,6],modelInputs:['culling-model-v2.tsx','pipeline-model-v1.tsx','culling-fix-proof-runtime-v2.tsx'].map(n=>({path:`${dst}/${n}`,sha256:sha(`${dst}/${n}`)})),actualPixelsReviewed:false,narrationTimingApproved:false,fullEpisodeApproved:false,localOnlyImages:true};write(planPath,JSON.stringify(plan,null,2)+'\n');console.log(JSON.stringify({plan:planPath,geometryChecks:checks.map(x=>({name:x.name,covered:x.all8CornersCovered})),baselineDefectRecorded:true,renderStarted:false}));
