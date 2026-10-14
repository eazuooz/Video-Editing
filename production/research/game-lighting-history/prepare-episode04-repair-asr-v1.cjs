// Prepare current generated PCM windows only after synthesis and verified research restoration.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production',read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const output=base+'/voice-repair-asr-plan-v1.json';if(fs.existsSync(path.join(root,output)))throw Error('Existing frozen ASR plan preserved');
const repair=read(base+'/voice-repair-plan-v1.json'),execution=read(base+'/voice-repair-execution-v1.json'),leasePath='shared/output/gpu-handoff/a86fde7e-5dd9-410f-8d37-9c569cedb1cb.json',lease=read(leasePath),m=read(repair.manifest);
if(execution.status!=='six-scoped-chunks-generated-awaiting-current-ASR'||execution.exitCode!==0||lease.state!=='research_resume_verified'||lease.ttsExitCode!==0)throw Error('Actual scoped TTS completion and research resume required');
for(const i of [...repair.inputHashes,...repair.originalChunks,repair.originalAudio])if(sha(i.path)!==i.sha256)throw Error('Preserved original input changed:'+i.path);
const research=read(path.join(lease.queueDir,'status.json')),procs=[].concat(JSON.parse(execFileSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(w)?\\.exe$' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true})));
const owner=procs.find(p=>p.ProcessId===research.owner_pid&&p.CommandLine?.includes('resume_with_preview.py')),child=procs.find(p=>p.ProcessId===research.child_pid&&p.ParentProcessId===research.owner_pid);
if(!owner||!['running','waiting_for_resources'].includes(research.status))throw Error('Restored research queue is not actually alive');
if(research.status==='running'&&!child)throw Error('Research running status has no matching actual child');
const audio=m.paths.narration,timing=m.tts.outputDir+'/'+m.tts.filenameStem+'.timing.json',ko=read(m.paths.script),en=read(m.paths.scriptEn),entries=read(timing).entries,jobs=[];
for(const g of repair.groupMap){
 const e=entries.filter(e=>e.scene_id===g.groupId),k=ko.scenes.find(s=>s.id===g.groupId),n=en.scenes.find(s=>s.id===g.groupId);if(e.length!==k.lines.length||n.lines.length!==k.lines.length)throw Error('Group paragraph mismatch');
 const from=e[0].start,to=e.at(-1).end,common={groupId:g.groupId,originalScene:g.originalScene,originalParagraphRange:[g.fromParagraph,g.toParagraph],expectedKo:k.lines,expectedEn:n.lines};
 jobs.push({...common,label:'whole-'+g.groupId,mode:'whole',sourceFromSeconds:from,sourceToSeconds:to});
 const contextFrom=Math.max(from,e[Math.max(0,e.length-2)].start-3);
 jobs.push({...common,label:'context-'+g.groupId,mode:'context',sourceFromSeconds:contextFrom,sourceToSeconds:to,expectedKo:k.lines.slice(-2),expectedEn:n.lines.slice(-2),boundaryCaveat:'Provisional paragraph timing with3s lead; extra neighboring content is preserved and is not target repetition.'});
}
const chunkInputs=repair.groupMap.map(g=>{const p=m.tts.outputDir+'/chunks/'+g.groupId+'-scene.wav';return{path:p,sha256:sha(p),groupId:g.groupId};});
const record={createdAt:new Date().toISOString(),scope:'Only six replacement continuous groups:whole plus independent complete trailing context,12windows. Full14chapter original PCM remains unchanged and unapproved; no expected text recognizer prompt.',audio:{path:audio,sha256:sha(audio)},timing:{path:timing,sha256:sha(timing)},inputHashes:repair.inputHashes,chunkInputs,originalInputHashes:[...repair.originalChunks,repair.originalAudio],lease:{path:leasePath,state:lease.state,ttsExitCode:lease.ttsExitCode,research,owner,child},jobs,expectedTextUsedAsPrompt:false,cpuThreads:2,gpuJobs:0,allDirectlyReviewed:false,currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false,localOnly:true};
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({plan:output,windows:jobs.length,researchJob:research.job,mainManifestChanged:false}));
