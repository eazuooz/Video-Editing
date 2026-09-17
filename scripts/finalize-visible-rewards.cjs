// Update generated delivery state only after verified full picture/audio render.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),project=path.join(root,'projects/visible-rewards'),file=path.join(project,'project.json'),m=JSON.parse(fs.readFileSync(file,'utf8'));
const qa=JSON.parse(fs.readFileSync(path.join(root,'shared/output/visible-rewards/visual-qa-v1/render-report.json'),'utf8'));
const mix=JSON.parse(fs.readFileSync(path.join(root,'shared/output/visible-rewards/audio-final-v1/report.json'),'utf8'));
const plan=require('../projects/visible-rewards/sources/gameplay-cuts.json'),script=require('../projects/visible-rewards/script/narration.ko.json');
if(!qa.fullDecodePassed||!qa.aacMatchesEditor||qa.frames!==22546)throw Error('Final verification required');
for(const [f,h] of Object.entries(qa.protectedBefore))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex')!==h)throw Error('Protected inputs differ');
const ts=fs.readFileSync(path.join(root,'motion-canvas/src/projects/visible-rewards/timing.ts'),'utf8'),nums=n=>JSON.parse('['+ts.match(new RegExp(n+' = \\[([^\\]]+)'))[1].trim().replace(/,$/,'')+']'),starts=nums('SCENE_STARTS'),durations=nums('SCENE_DURATIONS');
m.status='rendered-review-awaiting-human-listening';m.publishReady=false;m.audio.mixStatus='final';m.editing.timingStatus='measured-narration-captions-picture-aligned';
m.paths.footageCuts='projects/visible-rewards/sources/gameplay-cuts.json';m.paths.renderReport='shared/output/visible-rewards/visual-qa-v1/render-report.json';m.paths.audioMeasurements='shared/output/visible-rewards/audio-final-v1/report.json';
fs.writeFileSync(file,JSON.stringify(m,null,2)+'\n');
const stamp=s=>`${String(Math.floor(s/60)).padStart(2,'0')}:${(s%60).toFixed(3).padStart(6,'0')}`;
const rows=[['scene','start','end','segment_type','visual','source','source_audio','bgm','status']];
for(let i=0;i<8;i++){
 const id=String(i+1).padStart(2,'0');rows.push([id,stamp(starts[i]),stamp(starts[i]+m.editing.exampleSeconds),'real-example',plan.clips[i].action,plan.clips[i].cuts.map(c=>`${c.id}@${c.in}+${c.duration}`).join(' / '),'game -23 LUFS; commentary -31 LUFS','Wanderlust continuous + overlap -3dB','rendered-human-review-pending']);
 rows.push([id,stamp(starts[i]+m.editing.exampleSeconds),stamp(starts[i]+durations[i]),'channel-explanation',script.scenes[i].title,'original Motion Canvas diagram','off','Wanderlust continuous','rendered-human-review-pending']);
}
fs.writeFileSync(path.join(project,'planning/edit-cues.csv'),rows.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n')+'\n');
const ledger=Object.entries(plan.sources).map(([id,s])=>{const media=path.join(root,`shared/output/visible-rewards/media-cache/${id}.mp4`);return {id,url:'https://www.youtube.com/watch?v='+id,...s,sha256:crypto.createHash('sha256').update(fs.readFileSync(media)).digest('hex'),bytes:fs.statSync(media).size};});
fs.writeFileSync(path.join(project,'sources/media-ledger.json'),JSON.stringify({verifiedAt:'2026-09-16',sources:ledger,final:{seconds:qa.seconds,frames:qa.frames,bytes:fs.statSync(qa.target).size},audio:mix.loudness},null,2)+'\n');
console.log('Final delivery recorded; human listening still pending.');
