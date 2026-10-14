// Repair only seven actually failed source scenes; preserve the three passed renders.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),src='motion-canvas/src/projects/game-lighting-history-04/spatial/',folder='production/research/game-lighting-history/local/part1-label-repair-v225';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const write=(p,x)=>{p=path.join(root,p);if(fs.existsSync(p))throw Error('Preserve '+p);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof x==='string'?x:JSON.stringify(x,null,2)+'\n');};
const old=read('production/research/game-lighting-history/local/part1-spatial-bank-v206/plan.json');
const qa=read('projects/game-lighting-history-04/production/part1-spatial-source-direct-review-v223.json');
if(!qa.all53BoardsDirectlyViewed||qa.currentSourcePixelApproval)throw Error('Actual failed-pixel review required');
const replaceExact=(s,a,b)=>{if(!s.includes(a))throw Error('Source changed '+a);return s.replaceAll(a,b);};
let transfer=fs.readFileSync(path.join(root,src+'part1-transfer-model-v171.tsx'),'utf8');
transfer=replaceExact(transfer,'world.label(name,x,y,74,28,P.ink)','world.label(name,x,y,165,28,P.ink)');
let history=fs.readFileSync(path.join(root,src+'part1-history-contract-v177.tsx'),'utf8');
history=replaceExact(history,"x,-105,85,34,P.ink","x,-105,210,34,P.ink");
let observation=fs.readFileSync(path.join(root,src+'part1-observation-contract-v190.tsx'),'utf8');
observation=replaceExact(observation,'world.label(name,x,y,90,30,P.ink)','world.label(name,x,y,205,30,P.ink)');
// Avoid duplicate left names; retain the actual comparative-data label.
observation=replaceExact(observation,"slab(-540,0,'자료가 나온 대상',P.surfaceTop,390)","slab(-540,0,'',P.surfaceTop,390)");
observation=replaceExact(observation,"world.label('확인 필요',520,0,155,31,P.title)","world.label('확인 필요',520,0,270,31,P.title)");
write(src+'part1-transfer-model-v225.tsx',transfer);
write(src+'part1-history-contract-v225.tsx',history);
write(src+'part1-observation-contract-v225.tsx',observation);
let runtime=fs.readFileSync(path.join(root,src+'part1-reviewed-source-runtime-v200.tsx'),'utf8').replaceAll('part1-transfer-model-v171','part1-transfer-model-v225').replaceAll('part1-history-contract-v177','part1-history-contract-v225').replaceAll('part1-observation-contract-v190','part1-observation-contract-v225');
write(src+'part1-reviewed-source-runtime-v225.tsx',runtime);
const failed=new Set(qa.findings.map(x=>x.id)),scenes=[];let cursor=0;
for(const s of old.scenes.filter(x=>failed.has(x.id))){
 const wrapper=src+'part1-'+s.id+'-v225.tsx';
 const source=fs.readFileSync(path.join(root,s.wrapper.path),'utf8').replace('part1-reviewed-source-runtime-v200','part1-reviewed-source-runtime-v225');
 write(wrapper,source);write(wrapper.replace(/\.tsx$/,'.meta'),{version:0,timeEvents:[],seed:225000+scenes.length});
 scenes.push({...s,wrapper:ref(wrapper),priorEncodedRange:{source:qa.source.path,sha256:qa.source.sha256,fromFrame:s.fromFrame,toFrame:s.toFrame},fromFrame:cursor,toFrame:cursor+s.frames});cursor+=s.frames;
}
if(scenes.length!==7)throw Error('Only seven failed scenes');
const name='episode04-part1-label-repair-v225',project=src+name+'.ts',audio=folder+'/audio/'+name+'.wav';
write(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>`import s${i} from './part1-${s.id}-v225?scene';`).join('\n')+`\nexport default makeProject({scenes:[${scenes.map((s,i)=>'s'+i).join(',')}],audio:'/@fs/${root.replaceAll('\\','/')+'/'+audio}'});\n`);
write(project.replace(/\.ts$/,'.meta'),{version:0,shared:{background:null,range:[0,(cursor-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:true}}}});
let config=fs.readFileSync(path.join(root,'motion-canvas/vite.game-lighting-history04.part1-spatial-bank-v206.config.ts'),'utf8').replaceAll('part1-spatial-bank-v206','part1-label-repair-v225').replace('port:9275','port:9276');
write('motion-canvas/vite.game-lighting-history04.part1-label-repair-v225.config.ts',config);
write('motion-canvas/tsconfig.game-lighting-history04-part1-label-repair-v225.json',{extends:'./tsconfig.json',include:['src/env.d.ts',src.replace('motion-canvas/','')+'part1-reviewed-source-runtime-v225.tsx',...scenes.map(x=>x.wrapper.path.replace('motion-canvas/','')),project.replace('motion-canvas/','')]});
write(folder+'/plan.json',{schemaVersion:1,preparedAt:new Date().toISOString(),pixelFailureReview:ref('projects/game-lighting-history-04/production/part1-spatial-source-direct-review-v223.json'),priorPlan:ref('production/research/game-lighting-history/local/part1-spatial-bank-v206/plan.json'),jobs:[{name,project,frames:cursor,audio:{path:audio,samples:cursor*400},output:folder+'/renders/'+name+'.mp4',execution:folder+'/renders/'+name+'.execution.json'}],scenes,unchangedScenes:old.scenes.filter(x=>!failed.has(x.id)),changes:'Only label elevation and redundant covered label. Original geometry, progress clock, PCM, frame counts and three passed encoded scene ranges preserved.',models:['part1-transfer-model-v225.tsx','part1-history-contract-v225.tsx','part1-observation-contract-v225.tsx','part1-reviewed-source-runtime-v225.tsx'].map(x=>ref(src+x)),cpuThreads:2,gpuJobs:0,palette:'research-black-v1',classification:'explanation',captionsBurnedIntoSource:false,captionCenter:[960,970],rendered:false,movingPixelsReviewed:false,finalMixedAsrApproved:false,uploaded:false});
console.log(JSON.stringify({repairScenes:7,preservedEncodedScenes:3,frames:cursor,seconds:cursor/60,pcmAndClockUnchanged:true,rendered:false}));
