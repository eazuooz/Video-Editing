const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),base=path.relative(root,__dirname).replaceAll('\\','/');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'source-request-v1.json'),'utf8'));
const statePath=path.join(__dirname,'download-execution-v1.json');
if(fs.existsSync(statePath))throw Error('Existing source execution: read status/command line and resume only missing downloads explicitly.');
execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],{cwd:root,stdio:'inherit'});
const stamp=()=>new Date().toISOString();
const write=(p,d)=>{const t=p+'.'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(d,null,2)+'\n');fs.renameSync(t,p);};
const state={schemaVersion:1,slug:request.slug,pid:process.pid,commandLine:process.argv,startedAt:stamp(),status:'initializing',children:[],results:[],sessionId:null,cpuProductionJobs:0,gpuJobs:0,downloadJobs:0,fullDecode:false,directActionReview:false,sourceAudioForFinal:'exclude-all',resourceObservation:request.resourceObservation,newScriptCreated:false,newTtsStarted:false};
const media=path.join(root,request.localMediaDirectory);fs.mkdirSync(media,{recursive:true});fs.mkdirSync(path.join(__dirname,'logs'),{recursive:true});
const qPath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
function save(status){
 state.status=status;state.updatedAt=stamp();const sf=statePath+'.session.json';if(fs.existsSync(sf)){const s=JSON.parse(fs.readFileSync(sf));if(s.pid===process.pid)state.sessionId=s.sessionId;}
 write(statePath,state);const q=JSON.parse(fs.readFileSync(qPath));const i=q.items.find(x=>x.slug===request.slug);if(!i||i.videoId)throw Error('Candidate no longer unproduced');
 i.stage='official-source-'+status;i.updatedAt=state.updatedAt;
 i.execution={phase:'official-source-download-only',status,pid:process.pid,sessionId:state.sessionId,commandLine:process.argv,startedAt:state.startedAt,updatedAt:state.updatedAt,state:base+'/download-execution-v1.json',request:base+'/source-request-v1.json',children:state.children,downloadJobs:state.downloadJobs,cpuProductionJobs:0,gpuJobs:0,ttsJobs:0,renderJobs:0,uploadJobs:0,activeTasks:state.children.filter(x=>x.status==='running'),heavyDecodeDeferredForActualCpuLoad:true};
 i.nextAction='After sequential official downloads, inspect actual resources and run one limited CPU full-decode/direct action review. Preserve all foreign math synthesis/rendering. No narration before meaningful intervals are approved.';
 q.updatedAt=state.updatedAt;q.lastProgressAt=state.updatedAt;write(qPath,q);
}
async function hash(p){const h=crypto.createHash('sha256');for await(const c of fs.createReadStream(p))h.update(c);return h.digest('hex');}
async function run(s){
 const target=path.join(media,s.videoId+'.mp4'),info=path.join(media,s.videoId+'.info.json');
 if(!fs.existsSync(target)||!fs.existsSync(info)){
  const args=['-m','yt_dlp','--no-playlist','--write-info-json','--no-write-thumbnail','--http-chunk-size','1M','--retries','2','--fragment-retries','2','--socket-timeout','30','--js-runtimes','node:'+request.node,'--ffmpeg-location',request.ffmpegDirectory,'-f','bv*[height<=1080][vcodec^=avc]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*[height<=1080]+ba','--merge-output-format','mp4','-o',path.join(media,'%(id)s.%(ext)s'),s.url];
  const log=base+'/logs/'+s.videoId+'-download.log',fd=fs.openSync(path.join(root,log),'a');
  const child=spawn(request.python,args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});
  const c={kind:'download',videoId:s.videoId,pid:child.pid,commandLine:[request.python,...args],startedAt:stamp(),status:'running',log};state.children.push(c);state.downloadJobs=1;save('download-running');console.log(JSON.stringify(c));
  try{await new Promise((ok,bad)=>{child.once('error',bad);child.once('exit',code=>{c.exitCode=code;c.endedAt=stamp();c.status=code===0?'finished':'failed';code===0?ok():bad(Error('Download exited '+code));});});}finally{fs.closeSync(fd);state.downloadJobs=0;}
 }
 const m=JSON.parse(fs.readFileSync(info));if(m.id!==s.videoId||m.channel!=='DevolverDigital')throw Error('Actual official owner/id mismatch');
 state.results.push({videoId:m.id,title:m.title,channel:m.channel,channelId:m.channel_id,uploadDate:m.upload_date,sourceDuration:m.duration,url:m.webpage_url,localMediaPath:request.localMediaDirectory+'/'+s.videoId+'.mp4',fileBytes:fs.statSync(target).size,fileSha256:await hash(target),fullDecode:false,directActionReview:'pending',sourceAudioForFinal:'exclude-all',finalPublicRights:'pending'});save('source-downloaded');
}
(async()=>{save('initializing');for(const s of request.sources)await run(s);save('downloaded-awaiting-limited-cpu-decode-and-direct-review');console.log(state.status);})().catch(e=>{state.error=String(e.stack||e);try{save('failed');}catch(w){console.error(w);}console.error(e);process.exitCode=1;});
