const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),pp='projects/game-lighting-history-03/production/retained-clean-render-plan-v2.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const proof='projects/game-lighting-history-03/production/retained-clean-inclusive-range-correction-v3.json';
if(fs.existsSync(path.join(root,proof)))throw Error('Existing correction preserved');
const plan=read(pp),changes=[];
for(const c of plan.chapters){
 if(['overview','12a','13a'].includes(c.scene))continue;
 const i=plan.inputs.find(x=>x.path.endsWith('/'+c.name+'.meta')),m=read(i.path),before=sha(i.path);
 if(m.preview.fps!==60||m.rendering.fps!==60)throw Error('FPS changed');
 c.renderEndFrameInclusive=c.frames-1;m.shared.range=[0,c.renderEndFrameInclusive/60];
 fs.writeFileSync(path.join(root,i.path),JSON.stringify(m,null,2)+'\n');i.sha256=sha(i.path);
 changes.push({scene:c.scene,path:i.path,beforeSha256:before,afterSha256:i.sha256,plannedFrames:c.frames,rangeEndFrameInclusive:c.renderEndFrameInclusive});
}
const c=plan.chapters.find(x=>x.scene==='13a'),raw=c.output;c.rawOutput=raw;c.output=raw.replace(/\.mp4$/,'.normalized.mp4');
c.normalization={rawObservedFrames:5567,plannedFrames:5566,rawSha256:sha(raw),method:'Decode in presentation order; trim=end_frame=5566,setpts=N/(60*TB), libx264 veryfast CRF18 CPU2, timebase90000. Preserve raw exporter and source scenes. Exact PTS/decode verification remains required.',actualToolSessionId:64304,actualProcessIdObserved:null,actualToolSessionExitCode:null};
fs.writeFileSync(path.join(root,pp),JSON.stringify(plan,null,2)+'\n');
fs.writeFileSync(path.join(root,proof),JSON.stringify({observedAt:new Date().toISOString(),cause:'Installed Motion Canvas Renderer exports frame zero first, then each progress frame including range end. A 0..N range emits N+1 frames.',rendererCode:'motion-canvas/node_modules/@motion-canvas/core/lib/app/Renderer.js',rawFailure:c.normalization,changes,narrationChanged:false,modelMotionChanged:false,allPixelsApproved:false},null,2)+'\n');
console.log(JSON.stringify({futureRangesCorrected:changes.length,raw13aPreserved:true,normalizationVerificationPending:true}));
