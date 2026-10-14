const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const out=path.join(__dirname,'voice-diagnostic-plan-v1.json');if(fs.existsSync(out))throw Error('Existing immutable diagnostic plan preserved');
const slug='game-lighting-history-04',audio=read(`projects/${slug}/project.json`).productionState.generatedNarration;
const done=read('production/research/game-lighting-history/remaining-tts-execution-v2.json').completed.find(x=>x.slug===slug);
if(sha(audio.path)!==audio.sha256)throw Error('Current PCM changed');
const jobs=[];for(const[scene,ranges,reason]of[
 ['18v',[[18,40]],'Whole29.98s chunk collapse/backward20s repetition;existing tail context does not cover it'],
 ['18t',[[70,92],[90,110]],'Whole and tail context repeatp6 while enteringp7;short independent overlapping ranges distinguish recognition from speech'],
 ['22r',[[0,22],[-12,10]],'Whole omits first sentence;short start and leading boundary context verify onset versus neighboring content']
]){const r=read(`projects/${slug}/production/local/voice-asr-v2/whole-${scene}.json`);if(r.audioSha256!==audio.sha256)throw Error('Prior recognition input changed');for(const[lo,hi]of ranges){const from=r.sourceFromSeconds+lo,to=Math.min(r.sourceFromSeconds+hi,r.sourceToSeconds);jobs.push({label:`${scene}-${lo<0?'leading12':String(lo)}-${hi}`,scene,wholeRelativeSeconds:[lo,hi],sourceFromSeconds:from,sourceToSeconds:to,reason,boundaryCaveat:'Range endpoints are diagnostic windows,not approved spoken edit/caption boundaries;neighbor content and partial boundary words are preserved.'});}}
const plan={createdAt:new Date().toISOString(),scope:'Only5 short independent diagnostic windows after original56workers finish;current PCM/scripts/timing unchanged. Never infer actual repetition or omission from one recognizer output.',audio,timing:done.files['.timing.json'],scriptInputs:['ko','en'].map(l=>({path:`projects/${slug}/script/narration.${l}.json`,sha256:sha(`projects/${slug}/script/narration.${l}.json`)})),jobs,expectedTextUsedAsPrompt:false,cpuThreads:2,gpuJobs:0,started:false,currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false,localOnlyMedia:true};
fs.writeFileSync(out,JSON.stringify(plan,null,2)+'\n');console.log(JSON.stringify({plan:path.relative(root,out),windows:jobs.length,started:false,mediaProduced:0}));
