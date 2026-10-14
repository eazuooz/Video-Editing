const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),source=read(base+'/voice-repair-asr-plan-v1.json'),out=base+'/voice-repair-diagnostic-plan-v2.json';
if(fs.existsSync(path.join(root,out)))throw Error('Existing plan preserved');
const reviewed=read(base+'/voice-repair-direct-progress-v1.json');if(!reviewed.all12DirectlyCompared||reviewed.reviewedWindows!==12)throw Error('Direct12window review required');
const narration=read('projects/game-lighting-history-04/script/narration.ko.json').scenes,ko=id=>narration.find(s=>s.id===id).lines;
const jobs=[
 {label:'opening-22rg4',mode:'context',sourceFromSeconds:100.68,sourceToSeconds:114.0425,expectedKo:[ko('22r')[0]],purpose:'Distinct unchunked complete opening paragraph to diagnose missing sentence1 and same at start sentence2.'},
 {label:'joined-18t-tail-22r-opening',mode:'context',sourceFromSeconds:87.8825,sourceToSeconds:114.0425,expectedKo:[ko('18t')[6],ko('22r')[0]],purpose:'Complete final18t paragraph through preserved280ms pause into complete22r opening; distinct context for both unresolved regions. Provisional paragraph boundary caveat retained.'}
];
const plan={...source,createdAt:new Date().toISOString(),scope:'Two diagnostic contexts newly selected for observed opening omission and failed tail criterion; not a repeat of completed12window batch.',previousPlan:{path:base+'/voice-repair-asr-plan-v1.json',sha256:sha(base+'/voice-repair-asr-plan-v1.json')},directReview:{path:base+'/voice-repair-direct-progress-v1.json',sha256:sha(base+'/voice-repair-direct-progress-v1.json')},jobs,allDirectlyReviewed:false,currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false,localOnly:true};
fs.writeFileSync(path.join(root,out),JSON.stringify(plan,null,2)+'\n');
const oldWorker='production/research/game-lighting-history/review-episode04-repair-window-v1.py',newWorker='production/research/game-lighting-history/review-episode04-repair-diagnostic-v2.py';
let code=fs.readFileSync(path.join(root,oldWorker),'utf8').replace("voice-repair-asr-plan-v1.json","voice-repair-diagnostic-plan-v2.json").replace("local/voice-repair-asr-v1","local/voice-repair-diagnostic-v2");
if(fs.existsSync(path.join(root,newWorker)))throw Error('Existing worker preserved');fs.writeFileSync(path.join(root,newWorker),code);
console.log(JSON.stringify({contexts:jobs.length,expectedTextPrompt:false,executionStarted:false}));
