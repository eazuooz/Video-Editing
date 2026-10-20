const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const puppeteer = require(path.join(root, 'motion-canvas/node_modules/puppeteer'));
const {spawnSync} = require('node:child_process');
const slug = 'vampire-survivors-d2-copyright';
const local = path.join(__dirname, 'local');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sample = process.argv.includes('--sample');
const jobs = sample ? [{id:'preflight',name:'vs-d2-preflight-v2',frames:480,route:`/src/projects/${slug}/preflight-project.ts`}]
  : JSON.parse(fs.readFileSync(path.join(local, 'diagrams.json'), 'utf8')).jobs;
const assertSelected = () => {
  const c = JSON.parse(fs.readFileSync(path.join(root, 'shared/publishing/video-production-control.json'), 'utf8').replace(/^\uFEFF/, ''));
  if (c.selectedVideo !== slug || !c.newProductionAuthorization.fullProductionAuthorized) throw Error('Selected production changed');
};
async function main() {
  assertSelected();
  const browser = await puppeteer.launch({headless:true,args:['--disable-gpu','--renderer-process-limit=2'],protocolTimeout:600000});
  try {
    const page = await browser.newPage();
    for (const job of jobs) {
      assertSelected();
      if (!/^vs-d2-[a-z0-9-]+$/.test(job.name) || !job.route.startsWith(`/src/projects/${slug}/`)) throw Error('Unowned render target');
      const output = path.join(root,'shared/output/motion-canvas',job.name+'.mp4');
      const receipt = path.join(local,job.name+'.render.json');
      const sceneRoute=job.route.replace(/-project\.ts$/,'.tsx');
      const signature = {job,visualsSha256:sha(path.join(root,`motion-canvas/src/projects/${slug}/visuals.tsx`)),sceneSha256:sha(path.join(root,'motion-canvas',sceneRoute.slice(1))),entrySha256:sha(path.join(root,'motion-canvas',job.route.slice(1)))};
      if (fs.existsSync(output) && fs.existsSync(receipt)) {
        const old=JSON.parse(fs.readFileSync(receipt,'utf8'));
        if (JSON.stringify(old.signature)===JSON.stringify(signature) && old.sha256===sha(output)) {console.log('Reused',job.name);continue;}
        throw Error('Changed output needs a new owned name: '+job.name);
      }
      if (fs.existsSync(output)) throw Error('Unreceipted output preserved: '+output);
      await page.goto('http://127.0.0.1:9257/render-worker.html');
      await page.waitForFunction(()=>typeof renderVideo==='function');
      const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(frame=>console.log(job.id,frame+'/'+job.frames)).catch(()=>{}),15000);
      try {await page.evaluate(p=>window.renderVideo(p),{route:job.route,name:job.name,frames:job.frames,firstFrame:0,fps:60,width:1920,height:1080,exactFrameRange:true});}
      finally {clearInterval(pulse);}
      const result=await page.evaluate(()=>window.renderJob);
      if (!result.done || result.result!==0 || result.errors.length) throw Error(JSON.stringify(result));
      const probe=spawnSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',output],{encoding:'utf8',windowsHide:true});
      if(probe.status!==0)throw Error(probe.stderr);
      const v=JSON.parse(probe.stdout).streams[0];
      if(v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||+v.nb_frames!==job.frames)throw Error('Render geometry/frame mismatch');
      fs.writeFileSync(receipt,JSON.stringify({status:'rendered-awaiting-pixel-review',signature,sha256:sha(output),output,frames:job.frames,result},null,2)+'\n');
      console.log('Rendered',job.name);
    }
  } finally {await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
