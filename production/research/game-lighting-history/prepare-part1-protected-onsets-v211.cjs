const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/',s='projects/game-lighting-history-04/script/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const write=(p,x)=>{p=path.join(root,p);if(fs.existsSync(p))throw Error('Preserve '+p);fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');};
const ep=b+'part1-onset-replacement-asr-execution-v209.json',e=read(ep),selected=read(b+'part1-selected-current-tts-execution-v208.json');
if(e.exitCode!==0||e.completed.length!==5||!e.endedAt)throw Error('Five actual closed windows required');
const notes={
 'whole-runtime-texture-size':'All four sentences/end after the onset, but 이번 자산 창에서는 is recognized 가산창에서는0–0.66.',
 'context-runtime-texture-size':'Complete consumer paragraph and all four size clauses/end. Same unresolved onset 산창에서는24.80–25.48. Minor overlap28.68/28.54 preserved.',
 'context-ordinary-streaming-budget':'All four size and four ordinary-streaming sentences/end. Size onset again 가산창에서는. 화면의/화면에 and 앞의/앞에 remain human pronunciation pending.',
 'whole-geometry-car-material':'Both sentences/end present but 자동차 is recognized 갓동차0–0.40.',
 'context-geometry-car-material':'All nine programmable-material and two car sentences/end. Car onset recognized 동차42.46–42.84. 분기/붕기, 뒤의/뒤에 retained.'
};
const rows=e.completed.map(d=>{if(ref(d.result).sha256!==d.sha256)throw Error('Result changed');const r=read(d.result);return{label:d.label,result:ref(d.result),expected:r.job.sources.map(x=>({id:x.id,ko:x.ko,pcm:{path:x.path,sha256:x.sha256,sampleRange:x.sampleRange}})),actualFullText:r.text,actualAllWords:r.chunks,sourceRanges:r.sourceRanges,directFullExpectedAndActualTextCompared:true,allWordTimestampsDirectlyRead:true,notes:notes[d.label],onsetApproved:false,recognizerExpectedPrompt:false,actualPronunciationApproved:false,humanListening:'pending'};});
write(b+'part1-onset-direct-review-v210.json',{reviewedAt:new Date().toISOString(),execution:ref(ep),sessionId:19422,sessionObservedClosedExitCode:0,rows,allFiveFullTextsAndWordTimesRead:true,all74Approved:false,changedSourceOnsetsUnresolved:['runtime-texture-size','geometry-car-material'],currentMixAsrApproved:false,uploaded:false,next:'Generate two protected-lead-in takes, recognize full text without prompts, then remove only the separately reviewed lead-in at a silence boundary; retain final script verbatim.'});
const literal=s+'physical-part1-guided-actions.koen.v175.json',scripts=read(literal),ids=['runtime-texture-size','geometry-car-material'],lead='먼저 화면의 대상을 확인하겠습니다. ';
const scenes=ids.map(id=>scripts.scenes.find(x=>x.id===id));
for(const lang of ['ko','en'])write(s+`physical-part1-protected-onsets.${lang}.v211.json`,{title:'Temporary onset protection, excluded from final narration',scenes:scenes.map(x=>({id:x.id,title:x.id,lines:[lang==='ko'?lead+x.ko:'First identify the object on screen. '+x.en]}))});
const m=read(b+'part1-onset-repairs-tts-manifest-v199.json'),dir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-protected-onsets-v211',stem='game-lighting-history-04-part1-protected-onsets-v211';
m.paths={...m.paths,script:s+'physical-part1-protected-onsets.ko.v211.json',scriptEn:s+'physical-part1-protected-onsets.en.v211.json',narration:dir+'/'+stem+'.wav',captionsKo:dir+'/'+stem+'.srt',captionsEn:dir+'/'+stem+'.en.srt'};
m.tts={...m.tts,outputDir:dir,filenameStem:stem,maxNewTokens:1536,maxRenderAttempts:3};
const mp=b+'part1-protected-onsets-tts-manifest-v211.json';write(mp,m);
const paths=[...read(b+'part1-selected-current-tts-request-v208.json').protectedInputs.map(x=>x.path),literal,ep,b+'part1-onset-direct-review-v210.json',b+'part1-selected-current-tts-execution-v208.json',...selected.results.map(x=>x.path),mp,...['ko','en'].map(l=>s+`physical-part1-protected-onsets.${l}.v211.json`)];
write(b+'part1-protected-onsets-tts-request-v211.json',{preparedAt:new Date().toISOString(),slug:'game-lighting-history-04',manifestOverride:mp,repairIds:ids,scenes:ids.map(id=>({id,path:dir+'/chunks/'+id+'-scene.wav'})),protectedInputs:[...new Set(paths)].map(ref),preservedTakes:selected.results.filter(x=>!ids.includes(x.id)),finalLiteralScript:ref(literal),temporaryLeadIn:lead,temporaryLeadInMustBeRemoved:true,trimNotYetApproved:true,wholeAsrApproved:false,independentContextAsrApproved:false,researchRestoreRequired:true,uploaded:false});
const cp='production/research/game-lighting-history/checkpoint.json',c=read(cp);
c.updatedAt=new Date().toISOString();c.status='episode04-physical01-two-unresolved-onsets-protected-repair-v211';c.ownedActiveWork=null;
c.episode04Part1OnsetAsrV209={execution:ref(ep),actualIdentity:e.actualIdentity,endedAt:e.endedAt,exitCode:0,sessionId:19422,sessionClosed:true,allDirectReview:ref(b+'part1-onset-direct-review-v210.json'),approved:false};
c.next='Only two protected onset takes; all35 other takes and original111/five framing preserved. Direct full recognition and exact lead-in removal before final timeline.';
fs.writeFileSync(path.join(root,cp),JSON.stringify(c,null,2)+'\n');
console.log(JSON.stringify({fiveWindowsRead:true,onsetsApproved:false,protectedRepairTakes:2,preservedTakes:35}));
