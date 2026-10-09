const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.relative(root,__dirname).replaceAll('\\','/'),mc='motion-canvas/src/projects/similar-game-design/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const text=(p,v)=>{const f=path.join(root,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,v);};
const write=(p,j)=>text(p,JSON.stringify(j,null,2)+'\n');
const planPath=base+'/measured-allocation-v2/plan.json',p=read(planPath),out=base+'/measured-spatial-preparation-v1.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve measured preparation');
if(!p.sourceAllocationApproved||!p.allSelectedNativePixelsReviewed)throw Error('Selected-native gate');
const engineSource=mc+'spatial-explanation-v1.tsx';let engine=fs.readFileSync(path.join(root,engineSource),'utf8');
engine=engine.replace('export type Timing={durationSeconds:number;paragraphStarts:number[];measured:boolean};','export type Timing={durationSeconds:number;paragraphStarts:number[];measured:boolean;timeOffsetSeconds?:number;visibleStartSeconds?:number;animationStarts?:number[];};');
engine=engine.replace('const t=createSignal(0),u=(i:number,d=2.5)=>smooth((t()-(timing.paragraphStarts[i]??timing.paragraphStarts[timing.paragraphStarts.length-1]))/d);','const begin=timing.timeOffsetSeconds??0,end=begin+timing.durationSeconds;\n const t=createSignal(begin),u=(i:number,d=2.5)=>{const a=timing.animationStarts?.[i]??timing.paragraphStarts[i]??timing.paragraphStarts[timing.paragraphStarts.length-1];return smooth((t()-a)/Math.max(.3,Math.min(d,end-a-.1)));};');
engine=engine.replace('const orbit=()=>Math.min(t(),7)/7;','const orbit=()=>Math.max(0,Math.min(t()-(timing.visibleStartSeconds??0),7))/7;');
engine=engine.replace('yield* t(timing.durationSeconds,timing.durationSeconds,linear);','yield* t(end,timing.durationSeconds,linear);');
// Late white paragraphs must not inherit a completed action clock from hidden
// gameplay. Explicit schedules below move the corresponding spatial relation.
engine=engine.replace("()=>210+60*Math.sin(Math.PI*u(2)),P.blue,'?'","()=>145+65*u(0)+60*Math.sin(Math.PI*u(2)),P.blue,'?'");
engine=engine.replace("note('도착하려는 방향과 피하려는 방향이 달라질 수 있습니다');","note('도착하려는 방향과 피하려는 방향이 달라질 수 있습니다');\n  token(()=>-370+870*u(3,5),()=>140-260*u(3,5),()=>70+90*Math.sin(Math.PI*u(3,5)),P.green,'?');");
engine=engine.replace("note('설명용 공간 비교 · 실제 용암 피해나 제작 의도를 나타내지 않습니다');","note('설명용 공간 비교 · 실제 용암 피해나 제작 의도를 나타내지 않습니다');\n  token(()=>-440+880*u(3,5),245,()=>65+110*Math.sin(Math.PI*u(3,5)),P.green,'?');");
engine=engine.replace("token(()=>-610+610*u(1)+610*u(2),190,()=>65+100*Math.sin(Math.PI*u(2)),P.blue,'?');note", "token(()=>-610+610*u(1)+610*u(2)-220*u(3,5),()=>190-150*u(3,5),()=>65+100*Math.sin(Math.PI*u(2))+110*Math.sin(Math.PI*u(3,5)),P.blue,'?');\n  arrow(()=>[[610,50,190],[390,-150,190]],P.green,()=>u(3,5),[13,8]);note");
engine=engine.replace("flag(450,-145);arrow", "token(()=>-450+900*u(3,6),205,()=>70+110*Math.sin(Math.PI*u(3,6)),P.green,'?');\n  flag(450,-145);arrow");
text(mc+'spatial-explanation-measured-v1.tsx',engine);
const fullRows=[],whiteRows=[],sceneModules=[],whiteModules=[],mapping=[];let whiteCursor=0;
for(let si=0;si<p.scenes.length;si++){
 const s=p.scenes[si],ps=s.paragraphs.map(x=>x.sourceInSample/24000),white=s.parts.filter(x=>x.role==='explanation');
 const schedule=(a,z)=>{const v=ps.slice(),entry=a/60+.08,p3=ps[2]??entry,p4=ps[3]??entry;switch(s.id){
  case '02-familiar-action':v[0]=entry;v[1]=entry+1.4;break;
  case '03-patterns-not-ranking':v[0]=entry;v[1]=p4+.08;break;
  case '04-mining-route':v[1]=entry;v[2]=entry+2.6;break;
  case '05-route-under-pressure':v[0]=entry+1.1;v[2]=entry;v[3]=p4+.08;break;
  case '08-world-and-route':v[2]=entry;v[3]=p4+.08;break;
  case '09-combination-in-motion':v[0]=entry;v[1]=entry+.5;v[3]=entry+1.1;break;
  case '10-playing-together':v[0]=entry;v[1]=entry+.6;break;
  case '12-check-your-reason':if(a===0){v[1]=.4;v[2]=3.2;}else{v[3]=entry;}break;
  case '15-corridor-to-open':case '16-effects-and-position':case '19-visible-destination':case '21-read-before-ranking':v[0]=entry;v[1]=entry+.55;break;
  case '24-destination-and-danger':v[0]=entry;v[1]=entry+.6;break;
 }return v;};
 const fullTiming={id:s.id,durationSeconds:s.frames/60,frames:s.frames,paragraphStarts:ps,measured:true,animationStarts:white.length?schedule(white[0].localStartFrame,white[0].localEndFrameExclusive):ps,visibleStartSeconds:white[0]?.localStartFrame/60||0,voiceSha256:s.voiceSha256,allPcmPreserved:true};fullRows.push(fullTiming);
 const module=mc+'measured-scenes-v1/'+s.id+'.tsx';text(module,`import {makeScene2D} from '@motion-canvas/2d';\nimport {similarExplanation} from '../spatial-explanation-measured-v1';\nimport timing from '../measured-timing-v1.json';\nexport default makeScene2D(function*(view){yield* similarExplanation(view,'${s.id}',timing.full[${si}]);});\n`);sceneModules.push(module);
 for(let wi=0;wi<white.length;wi++){
  const part=white[wi],row={...fullTiming,id:s.id,part:wi+1,durationSeconds:part.frames/60,frames:part.frames,timeOffsetSeconds:part.localStartFrame/60,visibleStartSeconds:part.localStartFrame/60,animationStarts:schedule(part.localStartFrame,part.localEndFrameExclusive),whiteProjectStartFrame:whiteCursor,whiteProjectEndFrameExclusive:whiteCursor+part.frames,finalStartFrame:part.startFrame,finalEndFrameExclusive:part.endFrameExclusive};
  const idx=whiteRows.length;whiteRows.push(row);whiteCursor+=part.frames;
  const f=mc+'measured-white-scenes-v1/'+s.id+'-p'+(wi+1)+'.tsx';text(f,`import {makeScene2D} from '@motion-canvas/2d';\nimport {similarExplanation} from '../spatial-explanation-measured-v1';\nimport timing from '../measured-timing-v1.json';\nexport default makeScene2D(function*(view){yield* similarExplanation(view,'${s.id}',timing.white[${idx}]);});\n`);whiteModules.push(f);mapping.push({scene:s.id,part:wi+1,window:[part.localStartFrame,part.localEndFrameExclusive],animationStarts:row.animationStarts,paragraphs:s.paragraphs.filter(x=>x.localStartFrame<part.localEndFrameExclusive&&x.localEndFrame>part.localStartFrame).map(x=>({paragraph:x.paragraph,ko:x.ko,en:x.en})),finalPixelsReviewed:false});
 }
}
if(whiteCursor!==14551||whiteRows.length!==19)throw Error('White total changed');
write(mc+'measured-timing-v1.json',{schemaVersion:1,plan:{path:planPath,sha256:sha(planPath)},full:fullRows,white:whiteRows,whiteFrames:whiteCursor,measuredPcmAndFrameTiming:true,finalPixelsReviewed:false});
const project=(modules)=>"import {makeProject} from '@motion-canvas/core';\n"+modules.map((f,i)=>`import s${i} from './${path.posix.relative(mc,f).replace(/\.tsx$/,'')}?scene';`).join('\n')+`\nexport default makeProject({scenes:[${modules.map((f,i)=>'s'+i).join(',')}]});\n`;
text(mc+'measured-project-v1.ts',project(sceneModules));text(mc+'measured-white-project-v1.ts',project(whiteModules));
// Keep the entire previously inspected authoring entry. Reuse the live Vite
// entry for the new measured white assembly without starting another server.
const live=mc+'authoring-project-v1.ts',archive=mc+'lookdev-project-v1.ts';if(fs.existsSync(path.join(root,archive)))throw Error('Lookdev archive exists');fs.copyFileSync(path.join(root,live),path.join(root,archive));text(live,"export {default} from './measured-white-project-v1';\n");
write(out,{schemaVersion:1,preparedAt:new Date().toISOString(),plan:{path:planPath,sha256:sha(planPath)},engineSource:{path:engineSource,sha256:sha(engineSource)},measuredEngine:{path:mc+'spatial-explanation-measured-v1.tsx',sha256:sha(mc+'spatial-explanation-measured-v1.tsx')},lookdevProjectPreserved:{path:archive,sha256:sha(archive)},independentMeasuredScenes:24,whiteParts:19,whiteFrames:14551,mapping,rendered:false,allAnimatedMeasuredPixelsReviewed:false,allCaptionPixelsReviewed:false,finalTimingApproved:false,finalMixedAsrApproved:false,render:false,qa:false,uploaded:false});
console.log(JSON.stringify({independentScenes:24,whiteParts:19,whiteFrames:14551,lookdevArchived:archive,serverReused:true,finalApproval:false}));
