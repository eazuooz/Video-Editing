// Initialize requested revisions without changing existing deliverables or Studio settings.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),rel=f=>path.relative(root,f).replaceAll('\\','/');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const file=path.join(__dirname,'queue.json');if(fs.existsSync(file))throw Error('Queue exists; resume rather than initialize again');
const ids=[['counting-animation-frames','piZTx_239R8','final-v3'],['deconstruct-analyze-rebuild','reng7uTFE7s','final-v2'],['meaningful-quests','n-NaCpzAMlE','final-v2'],['praise-player','nq7NhHi9FSE','final-v2'],['responsive-game-feedback','Lqbqugmpsl8','final-v2']];
const inventory=read(path.join(__dirname,'proof/studio-private-inventory.json'));
const items=ids.map(([slug,videoId,revision],index)=>{
 if(!inventory.rows.some(r=>r.links.some(l=>l.href===`/video/${videoId}/edit`)&&r.cells[3]==='비공개'))throw Error('Missing actual private evidence '+slug);
 const base=path.join(root,'projects',slug),m=read(path.join(base,'project.json')),p=read(path.join(base,'production/final-v1/plan.json'));
 const preserved=path.join(base,'production/private-expansion-baseline');fs.mkdirSync(preserved,{recursive:true});
 const snapshots=['project.json','script/narration.ko.json','script/narration.en.json','production/final-v1/plan.json','production/final-v1/captions.ko.srt','production/final-v1/captions.en.srt','publishing/youtube-upload.json'];
 const records=snapshots.filter(f=>fs.existsSync(path.join(base,f))).map(f=>{const dst=path.join(preserved,f);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(path.join(base,f),dst);return{original:rel(path.join(base,f)),copy:rel(dst),sha256:hash(dst)};});
 const media=slug==='counting-animation-frames'?{clean:'production/final-v1/archived-media/clean.mp4',captioned:'production/final-v1/archived-media/captioned.mp4',mix:'production/final-v1/archived-media/final-mix.wav'}:{clean:m.paths.videoClean,captioned:m.paths.videoBurnedCaptions,mix:m.paths.editorAudioMix};
 for(const [kind,location] of Object.entries(media)){
  const src=slug==='counting-animation-frames'?path.join(base,location):path.join(root,location),dst=path.join(preserved,kind+path.extname(src));
  if(!fs.existsSync(src))throw Error('Missing baseline '+src);
  fs.copyFileSync(src,dst);records.push({kind,original:rel(src),copy:rel(dst),sha256:hash(dst),git:false});
 }
 const commercialFrames=p.scenes.flatMap(s=>s.cuts).filter(c=>c.file.includes('/raw/')).reduce((n,c)=>n+c.frames,0);
 const explanationFrames=p.bodyFrames-commercialFrames;
 const newActualFrames=Math.round(explanationFrames*1.5),addedFrames=newActualFrames-commercialFrames;
 const baseline={uploadedRevision:'final-v1',videoId,files:records,bodyFrames:p.bodyFrames,commercialFrames,explanationFrames,classification:'Conservative initial classification: all diagram-dominated own tests retained as explanation. Confirm every baseline screen before final QA.',preserveAllBodyFrames:true,preserveAllOriginalNarration:true,createdAt:new Date().toISOString()};
 write(path.join(preserved,'preservation.json'),baseline);
 return {order:index+1,slug,revision,originalVideoId:videoId,originalPrivacy:'private',status:index===0?'in-progress':'queued',stage:index===0?'fresh-source-and-preserved-content-review':'awaiting-expansion',baseline:rel(path.join(preserved,'preservation.json')),target:{explanationFrames,actualFrames:newActualFrames,additionalActualFrames:addedFrames,fps:60,estimatedFinalSeconds:(explanationFrames+newActualFrames+720)/60,ratio:'60:40',maxRoundingFrames:1},execution:null,qa:null,output:null,newPrivateUpload:null,gitDelivery:null};
});
const q={schemaVersion:1,createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),status:'active',currentSlug:items[0].slug,authorization:{userRequest:'지금까지 비공개로 올려진 영상이 다그러네 피피티 내용을 줄이지는 말고 여기에 중간삽입으로 대본을 늘려서 진행해줘',preservePptContent:true,preservePptDuration:true,extendScript:true,privateUpload:true,noPublicSchedule:true,preserveOldUploads:true,perVideoCommitPush:true},scopeEvidence:'production/batches/private-review-expansion/proof/studio-private-inventory.json',excluded:[{videoId:'6ZzSh40WojQ',reason:'2025 private free-asset video unrelated to this generated review batch'},{videoId:'DeSXTV41GXs',reason:'Currently scheduled in Studio; not currently private. Preserve user-managed scheduling/publication; this revision scope covers the five current private generated videos.'}],items,nextAction:'Review source history and visible exact fighting-game actions; write additive KO/EN narration preserving uploaded v1 PPT and narration. Only then synthesize additions and render expanded revision.'};
write(file,q);
const batchFile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),batch=read(batchFile);batch.priorityRevisionBatch=rel(file);batch.priorityRevisionReason=q.authorization.userRequest;batch.updatedAt=new Date().toISOString();write(batchFile,batch);
console.log(JSON.stringify(items.map(i=>({slug:i.slug,target:i.target})),null,2));
