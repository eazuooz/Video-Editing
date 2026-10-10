const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),pp='projects/game-lighting-history-03/production/retained-clean-render-plan-v2.json';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const plan=read(pp),changes=[];
for(const c of plan.chapters){
 const p=plan.inputs.find(x=>x.path.endsWith('/'+c.name+'.meta'));const m=read(p.path);
 if(['overview','12a'].includes(c.scene)){c.previewFps=30;continue;}
 const old=sha(p.path);m.preview.fps=60;fs.writeFileSync(path.join(root,p.path),JSON.stringify(m,null,2)+'\n');
 c.previewFps=60;p.sha256=sha(p.path);changes.push({path:p.path,beforeSha256:old,afterSha256:p.sha256,reason:'Preview60fps preserves integer rendering range boundaries; all source/scene/rendering60fps settings retained.'});
}
const c=plan.chapters.find(x=>x.scene==='12a'),raw=c.output;c.rawOutput=raw;c.output=raw.replace(/\.mp4$/,'.trimmed.mp4');
c.normalization={rawObservedFrames:4650,plannedFrames:4649,rawSha256:sha(raw),normalizedSha256:sha(c.output),method:'FFmpeg stream-copy frames:v4649, no audio, video_track_timescale90000. Raw media and exporter evidence preserved; exact all packet PTS and decode checked separately.'};
fs.writeFileSync(path.join(root,pp),JSON.stringify(plan,null,2)+'\n');
fs.writeFileSync(path.join(root,'projects/game-lighting-history-03/production/retained-clean-settings-frame-boundary-v2.json'),JSON.stringify({observedAt:new Date().toISOString(),changes,firstRenderExtraFrame:c.normalization,reRendered:false,allPixelsApproved:false},null,2)+'\n');
console.log(JSON.stringify({futurePreview60:changes.length,rawPreserved:true,trimmedFrames:4649,pixelsApproved:false}));
