const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const old='production/research/game-lighting-history/local/episode04-physical-framing-v59';
const folder='production/research/game-lighting-history/local/episode04-physical-framing-label-repair-v64';
const src='motion-canvas/src/projects/game-lighting-history-04/spatial/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const write=(p,j)=>{const f=path.join(root,p);if(fs.existsSync(f))throw Error('Preserve '+p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof j==='string'?j:JSON.stringify(j,null,2)+'\n');};
const plan=read(old+'/plan.json');
const extractedPath='production/research/game-lighting-history/local/episode04-physical-framing-qa-v62/execution.json',extracted=read(extractedPath);
if(extracted.status!=='encoded-samples-ready'||extracted.boards.length!==50||extracted.commands.some(c=>c.exitCode!==0))throw Error('Actual completed extraction required');
for(const b of extracted.boards)if(sha(b.path)!==b.sha256)throw Error('Reviewed board changed');
const reviewPath=base+'physical-framing-encoded-direct-review-v63.json';
write(reviewPath,{schemaVersion:1,reviewedAt:new Date().toISOString(),scope:'Five source scenes only; not final episode approval',extraction:ref(extractedPath),
 boards:extracted.boards.map(b=>({...b,directlyViewed:true})),cleanFramesDirectlyRead:77,captionedFramesDirectlyRead:117,
 all50BoardsDirectlyRead:true,all28CueFirstMiddleLastAndAdjacentSamplesDirectlyRead:true,
 fixedBottomCaptionPlacementPassed:true,captionWrappingPassed:true,diagramCaptionOverlapDetected:false,
 findings:[{id:'part2-overview',status:'repair-required',frames:[2693,2766,2767,2856,3039,3150],issue:'The thin-overlapping-surface nameplate is partially, then fully occluded by the taller orange and teal planes.'},
 {id:'part2-conclusion',status:'repair-required',frames:[3527,3646,3647,3719,3949,4330],issue:'The same nameplate is occluded as the planes fade in.'},
 {id:'part1-overview',status:'sampled-source-pixels-passed'},{id:'part1-conclusion',status:'sampled-source-pixels-passed'},{id:'part3-overview',status:'sampled-source-pixels-passed'}],
 permittedRepair:['part2-overview','part2-conclusion'],retainEncodedScenes:['part1-overview','part1-conclusion','part3-overview'],
 repairAction:'Leave the two occluding planes and their narrated motion intact; place their semantic nameplate above their silhouette and later in draw order.',
 allFinalPixelsReviewed:false,allMovingPixelsReviewed:false,finalMixedAsrApproved:false,qaApproved:false,uploaded:false,humanWholeListening:'pending',newGitImages:0});
for(const key of ['model','runtime','selected','review'])if(sha(plan[key].path)!==plan[key].sha256)throw Error('Historical binding changed: '+key);
let model=fs.readFileSync(path.join(root,plan.model.path),'utf8');
const needle="box(550,-40,230,55,P.green,'얇고 겹친 표면',layers);";
if(!model.includes(needle))throw Error('Expected reviewed occlusion source not found');
model=model.replace(needle,"box(550,-40,230,55,P.green,'',layers);");
const plane="node.add(new Node({opacity:layers,children:[space.box(560,-150,0,190,16,170,P.teal),space.box(560,90,0,190,16,170,P.orange)]}));";
if(!model.includes(plane))throw Error('Expected two planes not found');
model=model.replace(plane,plane+"\n  // Semantic nameplate stays above both silhouettes, after their draw order.\n  node.add(new Node({opacity:layers,children:[space.label('얇고 겹친 표면',550,-40,280,29,P.ink)]}));");
write(src+'physical-framing-model-v64.tsx',model);
write(src+'physical-framing-runtime-v64.tsx',fs.readFileSync(path.join(root,plan.runtime.path),'utf8').replaceAll('physical-framing-model-v57','physical-framing-model-v64'));
let cursor=0;const scenes=[];
for(const s of plan.scenes.filter(s=>s.id.startsWith('part2'))){
 if(sha(s.wrapper.path)!==s.wrapper.sha256||sha(s.source.path)!==s.source.sha256)throw Error('Original source changed');
 const wrapper=src+'physical-framing-'+s.id+'-v64.tsx';
 write(wrapper,fs.readFileSync(path.join(root,s.wrapper.path),'utf8').replaceAll('physical-framing-runtime-v59','physical-framing-runtime-v64'));
 write(wrapper.replace(/\.tsx$/,'.meta'),read(s.wrapper.path.replace(/\.tsx$/,'.meta')));
 scenes.push({...s,historicalFromFrame:s.fromFrame,historicalToFrame:s.toFrame,wrapper:ref(wrapper),fromFrame:cursor,toFrame:cursor+s.frames});cursor+=s.frames;
}
if(cursor!==2314||scenes.length!==2)throw Error('Scope drift');
const name='episode04-physical-framing-label-repair-v64',project=src+name+'.ts',audio=folder+'/audio/'+name+'.wav';
write(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>`import s${i} from './physical-framing-${s.id}-v64?scene';`).join('\n')+`\nexport default makeProject({scenes:[s0,s1],audio:'/@fs/${root.replaceAll('\\','/')+'/'+audio}'});\n`);
const meta=read(src+'episode04-physical-framing-v59.meta');meta.shared.range=[0,(cursor-1)/60];write(project.replace(/\.ts$/,'.meta'),meta);
write('motion-canvas/vite.game-lighting-history04.physical-framing-label-repair-v64.config.ts',fs.readFileSync(path.join(root,'motion-canvas/vite.game-lighting-history04.physical-framing-v59.config.ts'),'utf8').replaceAll('episode04-physical-framing-v59',name).replaceAll('physical-framing-v59','physical-framing-label-repair-v64').replace('port:9270','port:9271'));
write('motion-canvas/tsconfig.game-lighting-history04-physical-framing-label-repair-v64.json',{extends:'./tsconfig.json',include:['src/env.d.ts',src.replace('motion-canvas/','')+'physical-framing-runtime-v64.tsx',...scenes.map(s=>s.wrapper.path.replace('motion-canvas/','')),project.replace('motion-canvas/','')]});
write(folder+'/plan.json',{...plan,preparedAt:new Date().toISOString(),historicalPlan:ref(old+'/plan.json'),pixelRepairReview:ref(reviewPath),model:ref(src+'physical-framing-model-v64.tsx'),runtime:ref(src+'physical-framing-runtime-v64.tsx'),
 jobs:[{name,project,frames:cursor,audio:{path:audio,samples:cursor*400},output:folder+'/renders/'+name+'.mp4',execution:folder+'/renders/'+name+'.execution.json'}],scenes,
 changedSceneCount:2,retainedEncodedSceneCount:3,originalFivePcmChanged:false,original111Regenerated:false,rendered:false,animatedPixelsReviewed:false});
write('production/research/game-lighting-history/assemble-physical-framing-label-repair-audio-v64.py',fs.readFileSync(path.join(root,'production/research/game-lighting-history/assemble-physical-framing-render-audio-v59.py'),'utf8').replaceAll('episode04-physical-framing-v59',name));
const checkpointPath='production/research/game-lighting-history/checkpoint.json',cp=read(checkpointPath);
cp.episode04PhysicalFramingDirectPixelsV63={review:ref(reviewPath),all50BoardsDirectlyRead:true,repairRequired:scenes.map(s=>s.id),allFinalPixelsReviewed:false};
cp.ownedActiveWork={type:'physical-framing-label-repair-v64',status:'prepared-only',active:null,cpuThreads:2,gpuJobs:0,next:'Render only the two part2 nameplate repairs; retain the three passing encoded source scenes. Then add measured narrated game comparisons.'};cp.updatedAt=new Date().toISOString();
fs.writeFileSync(path.join(root,checkpointPath),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({reviewedBoards:50,changedScenes:2,retainedScenes:3,frames:cursor,seconds:cursor/60,imagesCreated:0,rendered:false}));
