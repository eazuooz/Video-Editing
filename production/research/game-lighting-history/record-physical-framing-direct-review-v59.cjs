const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)}),write=(p,j)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');};
const statePath=base+'physical-framing-asr-execution-v56.json',state=read(statePath),prior=read(base+'physical-framing-asr-direct-progress-v58.json');
if(state.completed.length!==10||state.exitCode!==0||!state.endedAt)throw Error('Actual ten-window completion required');
const findings={
 'whole-part2-overview':'The complete three-sentence scope, first-path connection and all arguments are present. ASR 얼리얼의 versus 언리얼의 remains a technical pronunciation ambiguity. Closing 보조 versus expected 보죠 is independently recognized as 보죠 in the complete joined context; do not infer a clipped ending from the whole ASR spelling.',
 'context-part2-overview':'Complete new overview and complete preserved Cyberpunk2023/1.62 technology-preview paragraph are present. Ending 보죠 is present at18.42–18.94s. 얼리얼의 spelling persists; keep human technical pronunciation pending. 당시에/당시의 is a preserved-neighbour ASR particle ambiguity. A0.22s cross-sentence timestamp overlap has no duplicated text and does not establish an audio repetition.',
};
const windows=state.completed.map(d=>{
 if(sha(d.result)!==d.sha256)throw Error('Completed ASR bytes changed');const r=read(d.result);
 const old=prior.windows.find(w=>w.label===d.label);
 if(!old&&!findings[d.label])throw Error('Missing direct finding');
 return {...d,expectedCompleteTexts:r.job.sources.map(s=>s.ko),actualCompleteText:r.text,
 directFullTextCompared:true,finding:old?.finding??findings[d.label],sourceHashes:r.job.sources.map(s=>ref(s.path)),
 humanListeningApproved:false,pronunciationApproved:false};
});
const selectedPath=base+'physical-framing-selected-execution-v55.json',selected=read(selectedPath);
for(const r of selected.results)if(!r.technicalTailGatePassed||sha(r.path)!==r.sha256)throw Error('Selected PCM changed');
write(base+'physical-framing-direct-text-review-v59.json',{
 schemaVersion:1,reviewedAt:new Date().toISOString(),execution:ref(statePath),selectedTakes:ref(selectedPath),
 windows,directlyReadWholeWindows:5,directlyReadIndependentContexts:5,allTenCompleteTextsCompared:true,
 noDetectedSentenceOmission:true,noDetectedRepeatedSentence:true,noDetectedInventedGreeting:true,
 currentHashBoundTechnicalTailPassed:true,sourceSceneReviewRenderingAllowed:true,
 narrationApproved:false,pronunciationApproved:false,humanWholeListeningApproved:false,finalMixedAsrApproved:false,
 pending:['Human listening and technical pronunciation: 언리얼의; 맡는/맞는; DLSS 오까지의 context spelling.','Actual narrated moving scene pixels, final interleaving, current final mix ASR and whole-video QA.'],
 endingHeuristicUsedAsApproval:false,old111ParagraphsRegenerated:false,
});
console.log('Directly recorded all5 whole+5 complete contexts. Review-render scope allowed; human pronunciation/narration/final-mix approval remain false.');
