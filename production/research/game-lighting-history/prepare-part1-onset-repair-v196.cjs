// Prepare one unchanged paragraph repair. This script never starts a media job.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production',s='projects/game-lighting-history-04/script';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,j)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');};
const ep=b+'/part1-selected-current-tts-execution-v181.json',selected=read(ep),request=read(b+'/part1-selected-current-tts-request-v181.json');
if(!selected.generationComplete||selected.exitCode!==0||selected.results.length!==37)throw Error('Current37 technical selection required');
for(const r of selected.results)if(sha(r.path)!==r.sha256)throw Error('Changed take '+r.id);
const scriptPath=s+'/physical-part1-guided-actions.koen.v175.json',script=read(scriptPath),scene=script.scenes.find(r=>r.id==='runtime-texture-size');
if(!scene||!scene.ko.startsWith('이번 자산 창에서는'))throw Error('Preserve current literal onset');
for(const lang of ['ko','en'])write(s+`/physical-part1-onset-repair.${lang}.v196.json`,{title:'원래 자산 창 설명의 첫머리 제한 보완',scenes:[{id:scene.id,title:scene.id,lines:[scene[lang]],screenRole:scene.role}]});
const manifest=read(b+'/part1-guided-actions-tts-manifest-v169.json'),dir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-onset-repair-v196',stem='game-lighting-history-04-part1-onset-repair-v196';
manifest.paths={...manifest.paths,script:s+'/physical-part1-onset-repair.ko.v196.json',scriptEn:s+'/physical-part1-onset-repair.en.v196.json',narration:dir+'/'+stem+'.wav',captionsKo:dir+'/'+stem+'.srt',captionsEn:dir+'/'+stem+'.en.srt'};
manifest.tts={...manifest.tts,outputDir:dir,filenameStem:stem,maxRenderAttempts:3,maxNewTokens:1536};
const mpath=b+'/part1-onset-repair-tts-manifest-v196.json';write(mpath,manifest);
const protectedPaths=[...request.protectedInputs.map(r=>r.path),ep,b+'/part1-selected-current-tts-request-v181.json',scriptPath,s+'/physical-part1-onset-repair.ko.v196.json',s+'/physical-part1-onset-repair.en.v196.json',mpath,b+'/part1-current-asr-direct-progress-v195.json',...selected.results.map(r=>r.path),...['whole-runtime-texture-size','context-runtime-texture-size','context-ordinary-streaming-budget'].map(id=>b+'/local/part1-selected-actions-asr-v182/'+id+'.json')];
write(b+'/part1-onset-repair-tts-request-v196.json',{preparedAt:new Date().toISOString(),slug:'game-lighting-history-04',manifestOverride:mpath,previousExecution:{path:ep,sha256:sha(ep)},repairIds:[scene.id],reason:'Whole and complete-context recognition shorten the literal opening 이번 자산 창에서는. Preserve unresolved old result and synthesize only this unchanged complete paragraph after the single74-window CPU worker has actually exited. No pronunciation claim from ASR alone.',protectedInputs:[...new Set(protectedPaths)].map(path=>({path,sha256:sha(path)})),preservedTakes:selected.results.filter(r=>r.id!==scene.id),scenes:[{id:scene.id,path:dir+'/chunks/'+scene.id+'-scene.wav'}],requiredPreviousCpuExecution:b+'/part1-selected-actions-asr-execution-v182.json',cpuThreads:2,gpuJobs:1,batchSize:1,researchRestoreRequired:true,allAsrApproved:false,newJobStarted:false});
console.log(JSON.stringify({repairIds:[scene.id],preserved:36,original111AndFiveFramingPreserved:true,newJobStarted:false}));
