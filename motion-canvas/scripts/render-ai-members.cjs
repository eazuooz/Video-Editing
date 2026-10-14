const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='ai-game-development-human-craft',dir=path.join(root,'shared/output',slug,'membership');fs.mkdirSync(dir,{recursive:true});
async function main(){
 const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8'));if(control.selectedVideo!==slug)throw Error('Selected video changed');
 const browser=await puppeteer.launch({headless:true});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9199/ai-production.html?scene=members');await page.waitForFunction(()=>window.sampleReview?.ready);
 for(const f of [0,300,599]){await page.evaluate(f=>sampleReview.player.requestSeek(f),f);await page.waitForFunction(f=>sampleReview.rendered===f,{},f);const png=await page.evaluate(()=>sampleReview.stage.finalBuffer.toDataURL());fs.writeFileSync(path.join(dir,`frame-${f}.png`),Buffer.from(png.split(',')[1],'base64'));}
 const errors=await page.evaluate(()=>reviewErrors);if(errors.length)throw Error(JSON.stringify(errors));
 if(!process.argv.includes('--render'))return;
 const movie=path.join(root,'shared/output/motion-canvas/ai-craft-membership-v1.mp4');if(fs.existsSync(movie))throw Error('Preserve existing member render');
 await page.goto('http://127.0.0.1:9199/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 await page.evaluate(()=>{renderVideo({route:'/src/projects/ai-game-development-human-craft/member-project.ts',name:'ai-craft-membership-v1',frames:600,fps:60,width:1920,height:1080,exactFrameRange:true}).catch(e=>window.renderFailure=String(e));});
 while(true){await new Promise(r=>setTimeout(r,1500));const s=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(s.failure||s.errors.length)throw Error(JSON.stringify(s));if(s.done){if(s.result!==0)throw Error('Failed');break;}}
 const probe=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',movie],{encoding:'utf8',windowsHide:true});if(probe.status)throw Error(probe.stderr);const p=JSON.parse(probe.stdout),v=p.streams.find(s=>s.codec_type==='video');if(+v.nb_frames!==600)throw Error('Length mismatch');
 fs.writeFileSync(path.join(dir,'render.json'),JSON.stringify({path:movie,frames:600,fps:60,seconds:10,sourceScreenshot:'shared/assets/membership/member-list-20260929.png',sha256:crypto.createHash('sha256').update(fs.readFileSync(movie)).digest('hex')},null,2)+'\n');console.log('Rendered original membership identities:600 frames.');
 }finally{await browser.close();}
}main().catch(e=>{console.error(e);process.exitCode=1;});
