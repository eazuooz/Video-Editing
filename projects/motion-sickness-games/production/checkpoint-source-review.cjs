const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),at=new Date().toISOString();
const proof='production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
for(const [id,count] of [['PF5L_2g9UVQ',67],['6slinvkF0Rs',37]]){
 const p=proof+'game-research/'+id+'-action-review/review.json',r=read(p);
 Object.assign(r,{manualActionReview:'all-'+count+'-research-frames-directly-viewed',reviewedAt:at,finalCutApproval:false});write(p,r);
}
for(const id of ['PF5L_2g9UVQ','6slinvkF0Rs']){
 const p='projects/motion-sickness-games/production/source-action-review/'+id+'/index.json',r=read(p);
 r.manualReview='all-'+r.sampleSeconds.length+'-one-second-boundary-images-directly-viewed';r.reviewedAt=at;r.finalCutApproval=false;
 r.observations=id==='PF5L_2g9UVQ'?[
  'Aim cursor/washer moves independently while environmental lines remain stable; edge movement around157-158 turns the view. Do not call Aim Mode an unconditional camera freeze.',
  'Follower notification starts by124s, remains through131s. Exclude123.5-132s. Another notification is visible553-554; exclude552.5-555s.',
  '301-309 shows repositioning around the tower.546-552 shows upward spray and view changes; meaningful action, not stationary footage.'
 ]:[
  '31-35 bridge navigation,36-39.5 view rotates toward overhead geometry;40-42 is a separate wall-oriented attempt/shot,48-52 has camera roll and lasers.',
  'This2023 official trailer proves visible camera transitions only. It does not prove a current comfort setting, input binding or health outcome.',
  'Exclude rating, logos, cinematic establishing shots and title/outro. Do not narrate edited trailer shots as one continuous play.'
 ];write(p,r);
}
const qPath='production/batches/sakurai-planning-game-design/queue.json',q=read(qPath),i=q.items.find(x=>x.slug==='motion-sickness-games');
i.status='in-progress';i.stage='existing-game-source-review-before-script';i.updatedAt=at;
i.preflight={...i.preflight,status:'distinct',checkedBeforeCreation:true,projectCreation:'scripts/new-video-project.ps1 passed current distinct --check before creation'};
i.execution={...i.execution,phase:i.stage,noNewProject:false,noTts:true,projectCreated:true,sessionId:null,pid:null,workerPid:null,
 sourceResearch:{...i.execution.sourceResearch,sourcePreviewStatus:'finished-all31-research-preview-images-viewed',densePreviewSession:59505,densePreviewStatus:'finished-exit0-all104-frames-viewed',boundaryPreviewSession:82358,boundaryPreviewStatus:'finished-exit0-all89-frames-viewed',sourceIds:['PF5L_2g9UVQ','6slinvkF0Rs'],allSourceDecodesPassed:true,finalCutApproval:false}};
i.nextAction='Author source-action-matched independent KO/EN script after exact action/crop review. Use existing PowerWash/Talos footage only, preserve exclusions and medical boundaries, then one approved-voice resource-aware TTS/CPU-ASR. No final render/upload yet.';
q.progress.inProgress=1;q.progress.queued=15;q.currentSlug=i.slug;q.updatedAt=at;write(qPath,q);
console.log('Source-only checkpoint saved. No TTS, final render or upload completion implied.');
