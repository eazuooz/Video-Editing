// Update generated delivery state only after verified full picture/audio render.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),project=path.join(root,'projects/visible-rewards'),file=path.join(project,'project.json'),m=JSON.parse(fs.readFileSync(file,'utf8'));
const version=process.argv.includes('--v3')?3:process.argv.includes('--v2')?2:1;
const audioVersion=Math.min(version,2);
const qa=JSON.parse(fs.readFileSync(path.join(root,`shared/output/visible-rewards/visual-qa-v${version}/render-report.json`),'utf8'));
const mix=JSON.parse(fs.readFileSync(path.join(root,`shared/output/visible-rewards/audio-final-v${audioVersion}/report.json`),'utf8'));
const planName=version===1?'gameplay-cuts.json':'gameplay-cuts.v2.json';
const plan=require(path.join(project,'sources',planName)),script=require('../projects/visible-rewards/script/narration.ko.json');
if(!qa.fullDecodePassed||!qa.aacMatchesEditor||qa.frames!==22546)throw Error('Final verification required');
for(const [f,h] of Object.entries(qa.protectedBefore))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex')!==h)throw Error('Protected inputs differ');
const ts=fs.readFileSync(path.join(root,'motion-canvas/src/projects/visible-rewards/timing.ts'),'utf8'),nums=n=>JSON.parse('['+ts.match(new RegExp(n+' = \\[([^\\]]+)'))[1].trim().replace(/,$/,'')+']'),starts=nums('SCENE_STARTS'),durations=nums('SCENE_DURATIONS');
m.status='rendered-review-awaiting-human-listening';m.publishReady=false;m.audio.mixStatus='final';m.editing.timingStatus='measured-narration-captions-picture-aligned';
m.paths.footageCuts=`projects/visible-rewards/sources/${planName}`;m.paths.renderReport=`shared/output/visible-rewards/visual-qa-v${version}/render-report.json`;m.paths.audioMeasurements=`shared/output/visible-rewards/audio-final-v${audioVersion}/report.json`;
m.paths.videoClean=path.relative(root,qa.target).replaceAll('\\','/');
if(version===2){
 m.visualStyle='editorial-isometric-2.5d-white-v2';
 m.revision={version:2,date:'2026-09-17',changes:['8 animated 2.5D explanations','Facecam-free Stardew backpack purchase','Monster Hunter Wilds forging and hunting example'],narrationChanged:false,timingChanged:false,captionsChanged:false,optionalAdditionalNarration:'not-approved-not-generated'};
 m.previousDeliveries={v1:{video:'shared/output/motion-canvas/visible-rewards.mp4',audio:'motion-canvas/src/projects/visible-rewards/assets/final-mix.m4a'}};
 // Do not point at an old/nonexistent burned-in subtitle delivery.
 delete m.paths.videoBurnedCaptions;
}
if(version===3){
 m.visualStyle='editorial-isometric-2.5d-white-full-frame-v3';
 m.revision={version:3,date:'2026-09-17',changes:['Full-frame gameplay without reserved lower caption band','Removed bottom explanatory footers from all 8 scenes','Preserved v2 facecam-free Stardew and Monster Hunter Wilds examples'],narrationChanged:false,audioChanged:false,timingChanged:false,captionsChanged:false};
 m.previousDeliveries={...m.previousDeliveries,v2:{video:'shared/output/motion-canvas/visible-rewards-v2.mp4',audio:'motion-canvas/src/projects/visible-rewards/assets/final-mix-v2.m4a',videoAvailability:'preserved-locally-only'}};
 m.editing.exampleFullFrame=true;m.editing.explanatoryFooters=false;
 m.editing.captionPresentation='separate-ko-en-srt-no-burn-in';
 m.paths.mediaArchive='shared/media-archives/visible-rewards/final-video-v3/manifest.json';
 delete m.paths.videoBurnedCaptions;
 for(const lang of ['Ko','En']){
  const target=`shared/output/motion-canvas/visible-rewards-final.${lang.toLowerCase()}.srt`;
  const source=fs.readFileSync(path.join(root,m.paths['captions'+lang]));
  if(fs.existsSync(path.join(root,target))&&!fs.readFileSync(path.join(root,target)).equals(source))throw Error('Existing delivery SRT differs: '+target);
  fs.writeFileSync(path.join(root,target),source);
  m.paths['deliveryCaptions'+lang]=target;
 }
}
fs.writeFileSync(file,JSON.stringify(m,null,2)+'\n');
const stamp=s=>`${String(Math.floor(s/60)).padStart(2,'0')}:${(s%60).toFixed(3).padStart(6,'0')}`;
const rows=[['scene','start','end','segment_type','visual','source','source_audio','bgm','status']];
for(let i=0;i<starts.length;i++){
 const id=String(i+1).padStart(2,'0');rows.push([id,stamp(starts[i]),stamp(starts[i]+m.editing.exampleSeconds),'real-example',plan.clips[i].action??script.scenes[i].title,plan.clips[i].cuts.map(c=>`${c.id}@${c.in+(plan.sources[c.id].sourceOffsetSeconds??0)}+${c.duration}`).join(' / '),'game -23 LUFS; commentary -31 LUFS','Wanderlust continuous + overlap -3dB','rendered-human-review-pending']);
 rows.push([id,stamp(starts[i]+m.editing.exampleSeconds),stamp(starts[i]+durations[i]),'channel-explanation',script.scenes[i].title,version>=2?'original Motion Canvas animated 2.5D diorama':'original Motion Canvas diagram','off','Wanderlust continuous','rendered-human-review-pending']);
}
fs.writeFileSync(path.join(project,'planning/edit-cues.csv'),rows.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n')+'\n');
const ledger=Object.entries(plan.sources).map(([id,s])=>{const media=path.join(root,s.file??`shared/output/visible-rewards/media-cache/${id}.mp4`);return {id,url:'https://www.youtube.com/watch?v='+id,...s,sha256:crypto.createHash('sha256').update(fs.readFileSync(media)).digest('hex'),bytes:fs.statSync(media).size};});
fs.writeFileSync(path.join(project,`sources/media-ledger${version>=2?'.v'+version:''}.json`),JSON.stringify({verifiedAt:version>=2?'2026-09-17':'2026-09-16',sources:ledger,final:{file:m.paths.videoClean,seconds:qa.seconds,frames:qa.frames,bytes:fs.statSync(qa.target).size},audio:mix.loudness},null,2)+'\n');
if(version===3){
 const files=[m.paths.videoClean,m.paths.deliveryCaptionsKo,m.paths.deliveryCaptionsEn];
 fs.writeFileSync(path.join(project,'publishing/delivery-v3.json'),JSON.stringify({version,verifiedAt:'2026-09-17',seconds:qa.seconds,frames:qa.frames,fullDecodePassed:qa.fullDecodePassed,aacMatchesEditor:qa.aacMatchesEditor,burnedCaptions:false,files:files.map(file=>({file,bytes:fs.statSync(path.join(root,file)).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')})),protectedInputs:qa.protectedBefore,fullListeningApproval:'pending'},null,2)+'\n');
}
console.log('Final delivery recorded; human listening still pending.');
