const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),file=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const q=JSON.parse(fs.readFileSync(file,'utf8')),item=q.items.find(x=>x.slug==='counting-animation-frames'),now=new Date().toISOString();
item.revision={revision:'final-v2',status:'preparing-footage',userRequest:'게임 애니메이션 프레임 세기 영상 너무 피피티만 많아 중간에 실제 게임영상 예시 잘 삽입해줘야할거같아 내용을 보니 격투게임이 적절할거같아',startedAt:now,checkpoint:'projects/counting-animation-frames/production/revision-v2.json',previousUpload:{videoId:'piZTx_239R8',revision:'final-v1',preserve:true},nextAction:'Use fresh fighting-game action in middle chapters, preserve approved narration/timing and numeric prototype evidence; actual final render/QA/collection before delivery.',execution:{status:'preparing',activeSession:null}};
q.currentSlug=item.slug;q.updatedAt=now;q.authorization.latestSteering=item.revision.userRequest;
fs.writeFileSync(file,JSON.stringify(q,null,2)+'\n');fs.writeFileSync(path.join(__dirname,'revision-v2.json'),JSON.stringify(item.revision,null,2)+'\n');
