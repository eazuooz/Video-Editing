// CPU windows end normally and return resources between jobs. Never alter the research gate.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),statePath=path.join(__dirname,'remaining-voice-asr-execution-v2.json');
const researchStatus='C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json';
const worker='production/research/game-lighting-history/review-voice-window-v2.py';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const now=()=>new Date().toISOString();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function processes(){return [].concat(JSON.parse(execFileSync('powershell.exe',['-NoProfile','-Command',
  "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python(w)?|node)\\.exe$' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
  {encoding:'utf8',windowsHide:true,maxBuffer:1024*1024})));}
function research(){
  const s=read(researchStatus),p=processes();
  const owner=p.find(x=>x.ProcessId===s.owner_pid&&x.CommandLine?.includes('resume_with_preview.py'));
  const child=p.find(x=>x.ProcessId===s.child_pid&&x.ParentProcessId===s.owner_pid);
  const other=p.filter(x=>x.CommandLine?.replaceAll('\\','/').includes(worker));
  return {ready:s.status==='running'&&Boolean(owner&&child),status:s,owner,child,other};
}
function write(s){const temp=statePath+'.tmp-'+process.pid;fs.writeFileSync(temp,JSON.stringify(s,null,2)+'\n');fs.renameSync(temp,statePath);}
async function main(){
  if(fs.existsSync(statePath)&&!process.argv.includes('--resume'))throw Error('Existing job preserved; inspect real identity before explicit resume.');
  const jobs=[];
  const producer=read(path.join(__dirname,'remaining-tts-execution-v2.json'));
  if(producer.status!=='all-remaining-tts-produced-and-decoded')throw Error('Current producer not complete');
  for(const slug of ['game-lighting-history-03','game-lighting-history-04']){
    const done=producer.completed.find(x=>x.slug===slug),project=path.join(root,'projects',slug);
    const script=read(path.join(project,'script/narration.ko.json'));
    const review=read(path.join(project,'production/script-input-review-v1.json'));
    for(const lang of ['ko','en'])if(sha(path.join(project,`script/narration.${lang}.json`))!==review.finalInputHashes[lang])throw Error('Script changed');
    for(const ext of ['.wav','.timing.json'])if(sha(path.join(root,done.files[ext].path))!==done.files[ext].sha256)throw Error('Generated input changed');
    for(const scene of script.scenes)for(const mode of ['whole','context'])jobs.push({slug,scene:scene.id,mode,
      audioSha256:done.files['.wav'].sha256,result:`projects/${slug}/production/local/voice-asr-v2/${mode}-${scene.id}.json`});
  }
  const old=fs.existsSync(statePath)?read(statePath):null;
  if(old){
    const p=processes();if(p.some(x=>x.ProcessId===old.pid&&x.CommandLine?.includes(path.basename(__filename))))throw Error('Existing scheduler still alive');
  }
  const s={schemaVersion:2,startedAt:now(),pid:process.pid,command:process.argv,cwd:root,status:'checking-research-boundary',
    schedulingPolicy:'One CPU2/GPU0 voice window while a real research child is active; return Python resources between windows and wait for the research queue to resume. No STOP, pause, whitelist, source, GPU or foreign process mutation.',
    cpuThreads:2,gpuJobs:0,expectedWindows:jobs.length,completed:[],episodesReusedWithoutRecognition:['game-lighting-history-01','game-lighting-history-02'],
    currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false,previousRun:old?.startedAt};
  write(s);
  try{
    for(const job of jobs){
      const output=path.join(root,job.result);
      if(fs.existsSync(output)){
        const r=read(output);if(r.audioSha256!==job.audioSha256||r.scene!==job.scene||r.label!==job.mode+'-'+job.scene)throw Error('Existing result mismatch');
        s.completed.push({...job,sha256:sha(output),reused:true});write(s);continue;
      }
      const deadline=Date.now()+12*3600*1000;
      while(true){
        const snap=research();
        if(snap.other.length)throw Error('Another current voice worker already running');
        s.researchObservation={observedAt:now(),...snap.status,owner:snap.owner,child:snap.child};
        s.current=job;s.status=snap.ready?'launching-single-CPU-window':'waiting-for-live-research-child';write(s);
        if(snap.ready)break;
        if(Date.now()>deadline)throw Error('Research child did not resume within12hours; no queue changes attempted');
        await sleep(30000);
      }
      const logs=path.join(root,'projects',job.slug,'production/local/voice-asr-v2');fs.mkdirSync(logs,{recursive:true});
      const log=fs.openSync(path.join(logs,job.mode+'-'+job.scene+'.log'),'a');
      const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-u',worker,'--slug',job.slug,'--scene',job.scene,'--mode',job.mode],
        {cwd:root,windowsHide:true,env:{...process.env,CUDA_VISIBLE_DEVICES:'-1',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'},stdio:['ignore',log,log]});
      s.worker={proxyPid:child.pid,command:child.spawnargs,startedAt:now()};s.status='recognizing-single-CPU-window';write(s);
      const exit=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',(code,signal)=>resolve({code,signal}));});fs.closeSync(log);
      if(exit.code!==0)throw Error('Current voice window failed: '+JSON.stringify({job,...exit}));
      const result=read(output);if(result.audioSha256!==job.audioSha256)throw Error('Result audio hash drift');
      s.completed.push({...job,sha256:sha(output),reused:false,exitCode:exit.code});s.worker=null;
      s.status='returning-CPU-resources-to-research';s.lastWindowEndedAt=now();write(s);
      console.log('DONE '+job.slug+' '+job.mode+'-'+job.scene+' '+s.completed.length+'/'+jobs.length);
      // Original research gate requires20seconds of idle. No Python process is kept alive here.
      await sleep(30000);
    }
    s.status='all56-windows-complete-awaiting-direct-review';s.endedAt=now();s.exitCode=0;s.current=null;write(s);
  }catch(error){s.status='failed-preserving-completed-windows';s.error=String(error);s.endedAt=now();write(s);throw error;}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
