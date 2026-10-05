const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const base='projects/making-game-sequels/production/';
const request=read(base+'additive-narration-request.json');
const state=read(base+'additive-narration-tts-execution.json');
if(state.exitCode!==0||!state.generationComplete||state.cpuJobs!==0)throw Error('New narration measurement is incomplete');
if(fs.existsSync(path.join(root,base+'additive-whole-asr-execution.json')))throw Error('Resume/read existing ASR instead of repeating it');
for(const input of request.protectedInputs)if(sha(input.path)!==input.sha256)throw Error('Changed input '+input.path);
const contexts=state.results.map(r=>{
  if(sha(r.path)!==r.sha256)throw Error('Changed new PCM');
  return {id:r.id+'-whole',audioPath:r.path,audioSha256:r.sha256,fromSeconds:0,toSeconds:r.seconds,expectedKo:r.text,scope:'All four new independent paragraphs; expected text is comparison-only and never a recognizer prompt.'};
});
const value={schemaVersion:1,preparedAt:new Date().toISOString(),protectedInputs:[...request.protectedInputs,...state.results.map(r=>({path:r.path,sha256:r.sha256}))],contexts,expectedWasRecognizerPrompt:false,humanWholeListening:'pending',humanPronunciation:'pending'};
fs.writeFileSync(path.join(root,base+'additive-whole-readback-request.json'),JSON.stringify(value,null,2)+'\n');
console.log(JSON.stringify({contexts:contexts.length,seconds:state.results.reduce((s,r)=>s+r.seconds,0),protectedInputs:value.protectedInputs.length}));
