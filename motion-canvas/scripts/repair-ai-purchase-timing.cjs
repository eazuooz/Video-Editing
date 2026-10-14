// Correct only the normal-purchase interval; preserve completed source movies.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='ai-game-development-human-craft',out=path.join(root,'shared/output',slug),project=path.join(root,'motion-canvas/src/projects',slug);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{windowsHide:true,encoding:'utf8',maxBuffer:64e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
async function main(){
 const control=read(path.join(root,'shared/publishing/video-production-control.json'));if(control.selectedVideo!==slug)throw Error('Wrong selection');
 for(let i=1;i<=28;i++)if(!fs.existsSync(path.join(out,'composite',String(i).padStart(2,'0'),'render.json')))throw Error('Wait for the current render to finish');
 const kit=path.join(project,'scene-kit.tsx'),source=fs.readFileSync(kit,'utf8'),old="s.paragraphs[phase===2?6:phase===1?5:2].start",replacement="s.paragraphs[phase===2?6:phase===1?5:3].start";
 const dir=path.join(out,'composite/17/timing-v2');fs.mkdirSync(dir,{recursive:true});
 const stampFile=path.join(dir,'source-change.json');let change;
 if(fs.existsSync(stampFile)){change=read(stampFile);if(sha(kit)!==change.newKitSha256)throw Error('Changed repair input');}
 else{if(source.split(old).length!==2)throw Error('Inspect changed timing code');const before=sha(kit);fs.writeFileSync(path.join(dir,'scene-kit.before.tsx'),source);fs.writeFileSync(kit,source.replace(old,replacement));change={oldKitSha256:before,newKitSha256:sha(kit),onlyAffectedScene:'17',oldExpression:old,newExpression:replacement,reason:'Keep100G visible while paragraph3 introduces price; show purchase at that paragraph+4.4s.'};fs.writeFileSync(stampFile,JSON.stringify(change,null,2));}
 const s=read(path.join(project,'scene-data.json')).scenes.find(s=>s.id==='17'),frames=Math.round(s.duration*60);
 const first=Math.floor(s.paragraphs[2].start*60)-1,last=Math.ceil((s.paragraphs[3].start+12)*60)+1,count=last-first;
 const name='ai-craft-scene17-timing-patch-v2',patch=path.join(root,'shared/output/motion-canvas',name+'.mp4'),patchReceipt=path.join(dir,'patch.json');
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required'],protocolTimeout:180000});
 try{if(!fs.existsSync(patchReceipt)){
  if(fs.existsSync(patch))throw Error('Inspect partial patch before retry');const page=await browser.newPage();await page.goto('http://127.0.0.1:9199/render-worker.html?skipActual=1',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
  await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack||e));},{route:`/src/projects/${slug}/scenes/17/project.ts`,name,firstFrame:first,frames:count,fps:60,width:1920,height:1080,exactFrameRange:true});
  let logged=0;while(true){await new Promise(r=>setTimeout(r,1500));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors.length)throw Error(JSON.stringify(state));if(Date.now()-logged>20000){console.log(`${state.frame}/${last}`);logged=Date.now();}if(state.done){if(state.result!==0)throw Error('Patch exporter failed');break;}}
  const v=JSON.parse(run('ffprobe',['-v','error','-show_streams','-of','json',patch])).streams[0];if(+v.nb_frames!==count)throw Error('Patch length');fs.writeFileSync(patchReceipt,JSON.stringify({first,last,frames:count,sha256:sha(patch),change},null,2));
 }}finally{await browser.close();}
 const original=path.join(root,'shared/output/motion-canvas/ai-craft-scene-17-v1.mp4'),reportFile=path.join(out,'composite/17/render.json'),report=read(reportFile),fixed=path.join(dir,'scene17-v2.mp4');
 if(report.encoded.sha256!==sha(original))throw Error('Original hash differs');
 const filter=`[0:v]split=2[a][b];[a]trim=end_frame=${first},setpts=PTS-STARTPTS[a0];[1:v]setpts=PTS-STARTPTS[p];[b]trim=start_frame=${last},setpts=PTS-STARTPTS[b0];[a0][p][b0]concat=n=3:v=1:a=0,format=yuv420p[v]`;
 run('ffmpeg',['-v','error','-n','-i',original,'-i',patch,'-filter_complex',filter,'-map','[v]','-frames:v',String(frames),'-an','-c:v','h264_nvenc','-preset','p5','-cq','17','-pix_fmt','yuv420p','-r','60','-video_track_timescale','15360','-movflags','+faststart',fixed]);
 const v=JSON.parse(run('ffprobe',['-v','error','-show_streams','-of','json',fixed])).streams[0];if(+v.nb_frames!==frames)throw Error('Fixed scene length');run('ffmpeg',['-v','error','-i',fixed,'-f','null','-']);
 fs.copyFileSync(reportFile,path.join(dir,'render.before.json'));fs.renameSync(original,path.join(dir,'scene17-before-v1.mp4'));fs.renameSync(fixed,original);
 report.fingerprint.sceneKitHash=change.newKitSha256;report.encoded.sha256=sha(original);report.targetedTimingRepair={...change,range:[first,last],retainedRanges:[[0,first],[last,frames]],originalSha256:sha(path.join(dir,'scene17-before-v1.mp4')),patch:read(patchReceipt)};fs.writeFileSync(reportFile,JSON.stringify(report,null,2)+'\n');
 fs.writeFileSync(path.join(out,'scene-kit-compatibility.json'),JSON.stringify({...change,unaffectedScenes:Array.from({length:28},(_,i)=>String(i+1).padStart(2,'0')).filter(s=>s!=='17'),proof:'Exact one-expression replacement inside if(s.id===17). All other renderer paths, data, inputs and timing are byte-identical.'},null,2));
 fs.writeFileSync(path.join(out,'visual-revisions.pending.json'),'{}\n');console.log('Scene17 timing repaired; final encoded visual review pending.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
