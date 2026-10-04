// Sequential CPU native-frame discovery. Sampled frames are not final-cut approval.
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const root = path.resolve(__dirname, '../../../../../');
const base = path.relative(root, __dirname).replaceAll('\\', '/');
const request = JSON.parse(fs.readFileSync(path.join(__dirname, 'request.json'), 'utf8'));
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const stateFile = process.argv[2] ? 'inspection-' + process.argv[2] + '.json' : 'inspection.json';
const statePath = path.join(__dirname, stateFile);
const state = {pid:process.pid,startedAt:new Date().toISOString(),status:'initializing',gpuJobs:0,narrationCreated:false,finalCutApproval:false,children:[],results:[]};
const tasks = process.argv[2] ? process.argv[2].split(',').map(videoId=>({videoId,step:1,label:'native-discovery'})) : [{videoId:'JziX-60OyCc',step:1,label:'native-discovery'},{videoId:'rjeyYMuGZgU',step:1,label:'native-discovery'}];
function save(status) {
  state.status=status;state.updatedAt=new Date().toISOString();fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');
  const q=JSON.parse(fs.readFileSync(queuePath,'utf8'));const item=q.items.find(x=>x.slug===request.slug);
  item.stage='source-native-frame-discovery';item.execution={...item.execution,phase:'source-native-frame-discovery',status,pid:process.pid,state:base+'/'+stateFile,children:state.children,activeTasks:state.children.filter(x=>x.status==='running'),gpuJobs:0,noTts:true,noNewScript:true,updatedAt:state.updatedAt};
  item.nextAction='Directly inspect every source discovery sheet; reject animation, presenter/title screens and insufficient/unrelated actions. Inspect exact native boundaries before approving any final action interval. Acquire more appropriate official actions if this bank cannot support the independent explanations and60:40 body.';
  q.updatedAt=state.updatedAt;fs.writeFileSync(queuePath,JSON.stringify(q,null,2)+'\n');
}
(async()=>{
  for(const task of tasks) {
    const target=path.join(__dirname,'frames',task.videoId+'-'+task.label,'index.json');
    if(fs.existsSync(target)) {state.results.push({videoId:task.videoId,index:base+'/frames/'+task.videoId+'-'+task.label+'/index.json',reused:true});continue;}
    const log=base+'/logs/'+task.videoId+'-'+task.label+'.log';const fd=fs.openSync(path.join(root,log),'a');
    const child=spawn(request.python,[path.join(__dirname,'inspect-source-actions.py'),task.videoId,'--step',String(task.step),'--label',task.label],{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});
    const rec={kind:'native-frame-discovery',videoId:task.videoId,pid:child.pid,status:'running',startedAt:new Date().toISOString(),log};state.children.push(rec);save('native-frames-running');console.log(JSON.stringify(rec));
    try {await new Promise((resolve,reject)=>{child.once('error',reject);child.once('exit',code=>{rec.exitCode=code;rec.endedAt=new Date().toISOString();rec.status=code===0?'finished':'failed';code===0?resolve():reject(Error('Frame discovery failed '+task.videoId));});});}finally{fs.closeSync(fd);}
    state.results.push({videoId:task.videoId,index:base+'/frames/'+task.videoId+'-'+task.label+'/index.json'});save('native-frames-finished');
  }
  save('awaiting-direct-source-review');console.log(state.status);
})().catch(e=>{state.error=String(e.stack||e);save('failed');console.error(e);process.exitCode=1;});
