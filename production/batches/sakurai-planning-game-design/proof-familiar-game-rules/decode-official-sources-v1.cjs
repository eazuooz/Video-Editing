const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),base=path.relative(root,__dirname).replaceAll('\\','/');
const downloaded=JSON.parse(fs.readFileSync(path.join(__dirname,'download-execution-v1.json')));
const statePath=path.join(__dirname,'decode-execution-v1.json');
if(fs.existsSync(statePath))throw Error('Existing decode execution: inspect its actual state and command line; do not repeat completed source decoding.');
if(downloaded.status!=='downloaded-awaiting-limited-cpu-decode-and-direct-review'||downloaded.results.length!==4||downloaded.children.some(x=>x.exitCode!==0))throw Error('Four actual downloads are required.');
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const stamp=()=>new Date().toISOString(),rel=p=>path.relative(root,p).replaceAll('\\','/');
const write=(p,d)=>{const t=p+'.'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(d,null,2)+'\n');fs.renameSync(t,p);};
const resource=JSON.parse(fs.readFileSync(path.join(__dirname,'resource-observation-v2.json')));
if(Date.now()-Date.parse(resource.observedAt)>120000||resource.ownHeavyJobs!==0||resource.cpuLoadPercent>85)throw Error('Fresh resource observation supporting one CPU2 worker is required.');
const state={schemaVersion:1,slug:'familiar-game-rules',pid:process.pid,commandLine:process.argv,startedAt:stamp(),status:'initializing',sessionId:null,cpuThreads:2,gpuJobs:0,children:[],results:[],resourceObservation:resource,allSourceFullDecode:false,directActionReview:false,newScriptCreated:false,newTtsStarted:false};
const qPath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const discovery=path.join(root,'shared/output/familiar-game-rules/research/discovery-v1');fs.mkdirSync(discovery,{recursive:true});
function save(status){state.status=status;state.updatedAt=stamp();const sf=statePath+'.session.json';if(fs.existsSync(sf)){const s=JSON.parse(fs.readFileSync(sf));if(s.pid===process.pid)state.sessionId=s.sessionId;}write(statePath,state);
 const q=JSON.parse(fs.readFileSync(qPath)),item=q.items.find(x=>x.slug===state.slug);if(!item||item.videoId)throw Error('Candidate is no longer unproduced');
 item.stage='official-source-'+status;item.updatedAt=state.updatedAt;item.execution={phase:'official-source-full-decode-and-discovery',status,pid:process.pid,sessionId:state.sessionId,commandLine:process.argv,startedAt:state.startedAt,updatedAt:state.updatedAt,state:base+'/decode-execution-v1.json',children:state.children,activeTasks:state.children.filter(x=>x.status==='running'),cpuProductionJobs:state.children.some(x=>x.status==='running')?1:0,cpuThreads:2,gpuJobs:0,ttsJobs:0,renderJobs:0,uploadJobs:0,foreignWorkPreserved:true};
 item.nextAction='Directly inspect all source discovery boards, then complete native action sequences and exact source intervals. No narration or scene production before action approval.';
 q.updatedAt=state.updatedAt;q.lastProgressAt=state.updatedAt;write(qPath,q);
 for(const p of [path.join(root,'projects/familiar-game-rules/production/latest-checkpoint.json'),path.join(__dirname,'latest-checkpoint.json')])write(p,{schemaVersion:1,slug:state.slug,updatedAt:state.updatedAt,stage:item.stage,execution:item.execution,nextAction:item.nextAction,allSourceFullDecode:state.allSourceFullDecode,directActionReview:false,newScriptCreated:false,newTtsStarted:false,render:false,qa:false,collected:false,uploaded:false});
}
async function hash(p){const h=crypto.createHash('sha256');for await(const c of fs.createReadStream(p))h.update(c);return h.digest('hex');}
async function run(kind,id,args){const log=base+'/logs/'+id+'-'+kind+'.log',fd=fs.openSync(path.join(root,log),'wx');const child=spawn(ff,args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});const c={kind,videoId:id,pid:child.pid,commandLine:[ff,...args],log,startedAt:stamp(),status:'running'};state.children.push(c);save(kind+'-running');console.log(JSON.stringify(c));
 try{await new Promise((ok,bad)=>{child.once('error',bad);child.once('exit',code=>{c.exitCode=code;c.endedAt=stamp();c.status=code===0?'finished':'failed';code===0?ok():bad(Error(kind+' exited '+code));});});}finally{fs.closeSync(fd);}return c;
}
(async()=>{save('initializing');for(const source of downloaded.results){const file=path.join(root,source.localMediaPath);if(await hash(file)!==source.fileSha256)throw Error('Current source hash changed: '+source.videoId);
 const probe=JSON.parse(execFileSync(fp,['-v','error','-show_streams','-show_format','-of','json',file],{encoding:'utf8',windowsHide:true}));write(path.join(__dirname,source.videoId+'-probe.json'),probe);
 const v=probe.streams.find(x=>x.codec_type==='video');if(!v||v.width<1280||v.height<720)throw Error('Unexpected source dimensions');
 const decoded=await run('full-decode',source.videoId,['-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',file,'-map','0:v:0','-map','0:a:0?','-threads','2','-f','null','NUL']);
 state.results.push({...source,probe:base+'/'+source.videoId+'-probe.json',actualDurationSeconds:Number(probe.format.duration),width:v.width,height:v.height,frameRate:v.avg_frame_rate,videoTimebase:v.time_base,fullDecode:true,fullDecodeExitCode:decoded.exitCode,fullDecodeLog:decoded.log,directActionReview:'pending'});save('source-decoded');
 }
 state.allSourceFullDecode=true;save('all-sources-decoded');
 for(const source of state.results){const interval=source.videoId==='m2CN7zy2nA4'?30:5,out=path.join(discovery,source.videoId);fs.mkdirSync(out);await run('discovery',source.videoId,['-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',path.join(root,source.localMediaPath),'-an','-vf','fps=1/'+interval+':start_time=0,scale=960:540','-q:v','3','-threads','2',path.join(out,'%04d.jpg')]);source.discovery={directory:rel(out),intervalSeconds:interval,frameCount:fs.readdirSync(out).filter(x=>x.endsWith('.jpg')).length,imagesGitPolicy:'local-only',directlyRead:false};save('source-discovery-extracted');}
 save('decoded-discovery-awaiting-direct-review');console.log(state.status);
})().catch(e=>{state.error=String(e.stack||e);try{save('failed');}catch(w){console.error(w);}console.error(e);process.exitCode=1;});
