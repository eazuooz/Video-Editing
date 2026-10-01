// Attach the actual shell session to the live runner's own checkpoint.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),[slug,id]=process.argv.slice(2);
if(!slug||!Number.isInteger(+id))throw Error('slug and actual session id required');
const qf=path.join(__dirname,'queue.json'),rf=path.join(root,'projects',slug,'production/revision-v2.json');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const write=(f,x)=>fs.writeFileSync(f,JSON.stringify(x,null,2)+'\n');
const q=read(qf),item=q.items.find(i=>i.slug===slug);if(!item?.execution?.pid)throw Error('No actual runner PID');
try{process.kill(item.execution.pid,0);}catch(e){throw Error('Runner no longer alive; inspect its final state before recording');}
item.execution.sessionId=+id;q.updatedAt=new Date().toISOString();q.preparationSlug=slug;
write(qf,q);const revision=read(rf);revision.execution.sessionId=+id;write(rf,revision);
console.log(JSON.stringify(item.execution));
