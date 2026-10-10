// A current-turn waiter only: no model, queue edits, process termination or GPU.
// Preserve the failed head42 evidence. Request one normal guarded handoff when
// the manifest's next training family runs; its own finite-validation gate stays.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const queue='C:/Users/eazuo/renderformer/tmp/placement_focus_20261008';
const target='train_wireframe_cnnA_42';
const manifest=JSON.parse(fs.readFileSync(path.join(queue,'manifest.json'),'utf8').replace(/^\uFEFF/,''));
const targetIndex=manifest.findIndex(j=>(j.id||j.name||j.job)===target);
if(targetIndex!==679)throw Error('Queue manifest changed; inspect before requesting another handoff');
const failed=JSON.parse(fs.readFileSync(path.join(queue,'done/train_wireframe_head_42.json'),'utf8'));
if(failed.validation.numerically_finite!==false)throw Error('Saved failure evidence changed');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 let last='';
 for(;;){
  const state=JSON.parse(fs.readFileSync(path.join(queue,'status.json'),'utf8').replace(/^\uFEFF/,''));
  const label=[state.status,state.job,state.completed].join(' / ');
  if(label!==last){console.log('Waiting without occupying GPU:',label);last=label;}
  if(state.status==='failed')throw Error('Original queue failed; preserve it and inspect, no TTS handoff requested');
  if(state.completed>targetIndex)throw Error('Target boundary passed; recheck the actual queue before any new request');
  if(state.status==='running'&&state.job===target&&!fs.existsSync(path.join(root,'shared/output/GPU_HANDOFF.json')))break;
  await wait(10000);
 }
 console.log('Requesting the unchanged cooperative handoff for',target);
 const exe=path.join(root,'qwen3-tts/.venv/Scripts/python.exe');
 const args=['-X','utf8','production/batches/game-math-part2-full-series/gpu-handoff.py','--project','game-math-quaternion-teaching-additions-v3','--queue-dir',queue,'--',exe,'-X','utf8','production/batches/game-math-part2-teaching-revision/render-narration-v3.py','--project','game-math-quaternion-teaching-additions-v3','--device','cuda:0','--batch-size','1'];
 const child=spawn(exe,args,{cwd:root,stdio:'inherit',windowsHide:true});
 child.on('error',e=>{console.error(e.message);process.exitCode=1;});
 child.on('exit',code=>{process.exitCode=code??1;});
})().catch(e=>{console.error(e.message);process.exitCode=1;});
