// Preserve complete current speech. Overflow is explicitly explanation time.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/',src='motion-canvas/src/projects/game-lighting-history-04/spatial/',folder='production/research/game-lighting-history/local/part1-spatial-bank-v206';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const write=(p,x)=>{p=path.join(root,p);if(fs.existsSync(p))throw Error('Preserve '+p);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof x==='string'?x:JSON.stringify(x,null,2)+'\n');};
const review=read(b+'part1-current-asr-direct-review-v201.json'),pcm=read(b+'part1-current-asr-pcm-corroboration-v202.json'),anchors=read(b+'part1-word-anchor-draft-v200.json');
if(!review.all74FullTextsDirectlyCompared||!review.all74WordTimestampsDirectlyRead||!pcm.all74ExactCurrentPcmCorroborated)throw Error('Current directly read full text/word times and exact PCM required');
const descriptions=[
 ['horizon-comparison-before','horizon-comparison-before','표시 조건과 같은 대상을 먼저',0],
 ['outer-comparison-before','outer-comparison-before','표시 빈도와 게임 상태를 구별',0],
 ['cyber-comparison-before','cyber-comparison-before','표면의 빛에서 복원 입력으로',0],
 ['fortnite-comparison-before','fortnite-comparison-before','실제 장면과 기기 예산을 연결',0],
 ['four-game-transfer-conclusion','four-game-transfer-conclusion','네 게임에 같은 자료 흐름 질문',0],
 ['shadow-wheel-change','shadow-address-update','주소 찾기와 내용 갱신',33.70],
 ['tsr-silhouette-history','history-silhouette','같은 위치가 같은 표면일까?',36.84],
 ['tsr-rotation-vectors','history-thin-blade','끝점과 새로 드러난 배경',30.48],
 ['cyber-light-reconstruction','different-reconstruction-inputs','표면 세부와 빛 자료의 차이',18.08],
 ['mobile-compiler-availability','missing-measurement','비어 있는 측정도 기록하기',12.36]
];
const scenes=[];let cursor=0;
for(const [id,role,title,start] of descriptions){
 const row=anchors.rows.find(x=>x.id===id);if(!row?.source||row.status!=='literal-word-anchor-draft')throw Error('Retained current take required '+id);
 if(ref(row.source.path).sha256!==row.source.sha256)throw Error('Changed PCM '+id);
 const firstFrame=Math.round(start*60),firstSample=firstFrame*400,lastSample=row.source.samples,frames=Math.ceil((lastSample-firstSample)/400);
 const selectedCues=row.cues.filter(c=>c.toFrame>firstFrame).map(c=>({...c,fromFrame:Math.max(0,c.fromFrame-firstFrame),toFrame:Math.min(frames,c.toFrame-firstFrame)}));
 if(!selectedCues.length||selectedCues.some(c=>c.toFrame<=c.fromFrame))throw Error('Empty excerpt captions');
 const stages=selectedCues.map((c,i)=>({fromFrame:c.fromFrame,toFrame:c.toFrame,progressFrom:i/selectedCues.length,progressTo:(i+1)/selectedCues.length,anchor:c.text.replaceAll('\n',' ')}));
 const wrapper=src+'part1-'+id+'-v206.tsx',clock={id,role,title,frames,sourceSha256:row.source.sha256,boundSourceSha256:row.source.sha256,sourceSampleRange:[firstSample,lastSample],wholeAndContextCompared:true,stages};
 write(wrapper,`import {part1ReviewedSourceScene} from './part1-reviewed-source-runtime-v200';\nexport default part1ReviewedSourceScene(${JSON.stringify(clock,null,2)});\n`);
 write(wrapper.replace(/\.tsx$/,'.meta'),{version:0,timeEvents:[],seed:206000+scenes.length});
 scenes.push({id,role,title,classification:'explanation',wrapper:ref(wrapper),source:ref(row.source.path),sourceSampleRange:[firstSample,lastSample],sourceSamples:lastSample-firstSample,frames,fromFrame:cursor,toFrame:cursor+frames,silentPaddingSamples:frames*400-(lastSample-firstSample),fullSpeechSeconds:row.source.samples/24000,explanationStartsInFullSpeechAtFrame:firstFrame,completeNativePrefixFrames:firstFrame,cues:selectedCues,stages,originalKo:row.ko,wordAnchorResult:row.result});cursor+=frames;
}
const name='episode04-part1-spatial-bank-v206',project=src+name+'.ts',audio=folder+'/audio/'+name+'.wav';
write(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>`import s${i} from './part1-${s.id}-v206?scene';`).join('\n')+`\nexport default makeProject({scenes:[${scenes.map((s,i)=>'s'+i).join(',')}],audio:'/@fs/${root.replaceAll('\\','/')+'/'+audio}'});\n`);
write(project.replace(/\.ts$/,'.meta'),{version:0,shared:{background:null,range:[0,(cursor-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:true}}}});
const template=fs.readFileSync(path.join(root,'motion-canvas/vite.game-lighting-history04.physical-framing-v59.config.ts'),'utf8');
write('motion-canvas/vite.game-lighting-history04.part1-spatial-bank-v206.config.ts',template.replaceAll('episode04-physical-framing-v59',name).replaceAll('physical-framing-v59','part1-spatial-bank-v206').replace('local/'+name,folder.slice(folder.indexOf('local/'))).replace('port:9270','port:9275'));
write('motion-canvas/tsconfig.game-lighting-history04-part1-spatial-bank-v206.json',{extends:'./tsconfig.json',include:['src/env.d.ts',src.replace('motion-canvas/','')+'part1-reviewed-source-runtime-v200.tsx',...scenes.map(x=>x.wrapper.path.replace('motion-canvas/','')),project.replace('motion-canvas/','')]});
write(folder+'/plan.json',{schemaVersion:1,preparedAt:new Date().toISOString(),review:ref(b+'part1-current-asr-direct-review-v201.json'),pcmCorroboration:ref(b+'part1-current-asr-pcm-corroboration-v202.json'),wordAnchorDraft:ref(b+'part1-word-anchor-draft-v200.json'),models:['part1-transfer-model-v171.tsx','part1-history-contract-v177.tsx','part1-observation-contract-v190.tsx','part1-reviewed-source-runtime-v200.tsx'].map(x=>ref(src+x)),jobs:[{name,project,frames:cursor,audio:{path:audio,samples:cursor*400},output:folder+'/renders/'+name+'.mp4',execution:folder+'/renders/'+name+'.execution.json'}],scenes,palette:'research-black-v1',classification:'explanation',captionStyle:'boxed-white-forest-v1',captionCenter:[960,970],captionsBurnedIntoSource:false,cpuThreads:2,gpuJobs:0,original111Regenerated:false,rendered:false,movingPixelsReviewed:false,finalMixedAsrApproved:false,uploaded:false});
console.log(JSON.stringify({independentScenes:10,frames:cursor,seconds:cursor/60,sourcePcmPreserved:true,overflowExplanationScenes:5,rendered:false}));
