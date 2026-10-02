const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
const W=__dirname,R=path.resolve(W,'../../../..'),B=path.join(W,'../original-restored-v2');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const rel=f=>path.relative(R,path.join(W,f)).replaceAll('\\','/');
const p=read(path.join(W,'plan.json')),q=read(path.join(W,'qa.json')),d=read(path.join(W,'direct-visual-review.json')),m=read(path.join(W,'final.manifest.json'));
if(d.status!=='passed'||d.captionedSha256!==q.videoBurnedCaptions.sha256||q.cueCount!==448||q.ratioErrorFrames>1)throw Error('Current final QA must pass before collection.');
const bq=read(path.join(B,'qa.json')),bm=read(path.join(B,'final.manifest.json'));
const baselineHashes={};for(const key of ['videoClean','videoBurnedCaptions']){
 const sha=crypto.createHash('sha256').update(fs.readFileSync(path.join(R,bm.paths[key]))).digest('hex');
 if(sha!==bq[key].sha256)throw Error('Original baseline changed '+key);baselineHashes[key]=sha;
}
write(path.join(W,'baseline-preservation.json'),{baseline:'original-restored-v2',unchangedOriginalVideoHashes:baselineHashes,previousReceipt:'projects/blank-project-coding/publishing/youtube-upload-original-restored-v2.json',previousVideoId:'bbpKRhlxeCs',newUpload:'pending'});
m.status='deduplicated-v3-rendered-reviewed';
m.production={currentStage:'rendered-reviewed-ready-for-private-upload',ttsGenerated:true,rendered:true,collected:false,uploaded:false};
m.editing.timingStatus='51-independent-editor-scenes-and-final68846frames-verified';
m.editing.exampleInterleaving.reviewStatus='retained-reviewed-cuts-and-all-current-caption-compositions-reviewed';
m.audio.mixStatus='49-retained-scene-sample-identities-and-AAC-mix-alignment-verified';
m.audio.finalMeasurement={integratedLufs:+q.mixMeasurement.input_i,truePeakDbtp:+q.mixMeasurement.input_tp,source:rel('qa.json')};
m.approvals.render='full-decode-caption-and-transition-QA-passed; full-human-listening-pending';
m.approvals.broll='retained-v2-reviewed-source-cuts; three-recomposed-cut-transitions-directly-reviewed';
m.finalRender.seconds=p.seconds;
m.finalRender.openItems=m.finalRender.openItems.filter(x=>!x.includes('truncated'));
m.duplicateReview={kind:'explicit-user-requested-removal-of-three-duplicate-sections',report:rel('publishing/revision-preflight.json'),status:'previous-private-upload-and-original-local-files-preserved',mustRefreshBeforeProduction:false};
write(path.join(W,'final.manifest.json'),m);
const active=path.join(R,'projects/blank-project-coding/project.json'),snapshot=path.join(W,'baseline-project.json');
if(!fs.existsSync(snapshot))fs.copyFileSync(active,snapshot);
write(active,m);
const r=spawnSync(process.execPath,['scripts/collect-video-output.cjs','blank-project-coding'],{cwd:R,windowsHide:true,encoding:'utf8',maxBuffer:5e6});
fs.writeFileSync(path.join(W,'collect-output.log'),r.stdout+'\n'+r.stderr);if(r.status!==0)throw Error(r.stderr||r.stdout);
m.production.collected=true;write(path.join(W,'final.manifest.json'),m);write(active,m);
const receipt=path.join(R,m.publishing.receipt);
if(!fs.existsSync(receipt)){
 const r=spawnSync(process.execPath,[path.join(W,'prepare-publishing.cjs')],{cwd:R,windowsHide:true,encoding:'utf8',maxBuffer:5e6});
 fs.writeFileSync(path.join(W,'prepare-publishing.log'),r.stdout+'\n'+r.stderr);if(r.status!==0)throw Error(r.stderr||r.stdout);
}
write(path.join(W,'checkpoint.json'),{stage:'local-delivery-ready-for-private-upload',completed:['duplicate-review','three-group-removal','sample-exact-retained-voice-audit','49-scene-mix-alignment','full-decode','all-cue-and-transition-review','exact60:40','51-editor-scene-timing','collected-four-current-output-files'],remaining:['private-upload','git-delivery'],pendingHumanOrPlatform:['full-human-listening','Nimbus-original-bytes-verification','external-media-backup','pinned-comment-unavailable-while-private']});
console.log('Reviewed 19m07s revision collected, baseline hashes verified, private-upload package prepared.');
