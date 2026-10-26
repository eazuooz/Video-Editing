/** Finite selected-episode Motion Canvas export. Own local Vite/browser only. */
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const ROOT=path.resolve(__dirname,'../../..');
const MC=path.join(ROOT,'motion-canvas');
const BATCH='design-finish-six-20261026';
const SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes',
  'start-with-climax','kind-to-beginners','respect-player-time'];

async function main(){
  const [slug,name,count,first='0']=process.argv.slice(2);
  const frames=Number(count),firstFrame=Number(first);
  if(!SLUGS.includes(slug)||!new RegExp('^'+slug+'-[a-z0-9-]+$').test(name||''))throw Error('Exact selected episode output required');
  if(!Number.isSafeInteger(frames)||frames<1||!Number.isSafeInteger(firstFrame)||firstFrame<0)throw Error('Exact frame range required');
  const control=JSON.parse(fs.readFileSync(path.join(ROOT,'shared/publishing/video-production-control.json'),'utf8'));
  const batch=control.finiteBatchAuthorizations?.[BATCH];
  if(!batch?.localProductionAuthorized||!batch.slugs.includes(slug)||batch.automaticOutsideBatch!==false)throw Error('Actual user six-episode authorization required');
  const physical=path.resolve('C:/Users/1/.codex/video-production',BATCH,slug,'batch-v1');
  const logical=path.join(ROOT,'projects',slug,'production/local/batch-v1');
  if(path.resolve(fs.realpathSync(logical))!==physical)throw Error('Exact C storage junction required');
  const rendered=path.join(physical,'rendered');fs.mkdirSync(rendered,{recursive:true});
  const output=path.join(rendered,name+'.mp4');
  if(fs.existsSync(output))throw Error('Preserve existing animation export; choose a new version name');
  const leaseRoot=path.resolve('C:/Users/1/.codex/video-production',BATCH);fs.mkdirSync(leaseRoot,{recursive:true});
  const lease=path.join(leaseRoot,'heavy-job.lock.json');
  const fd=fs.openSync(lease,'wx');
  fs.writeFileSync(fd,JSON.stringify({owner:'root',pid:process.pid,kind:'Motion Canvas',slug,name,startedAt:new Date().toISOString()}));fs.closeSync(fd);
  const receipt=path.join(rendered,name+'.render.json');
  const state={slug,name,frames,firstFrame,fps:60,width:1920,height:1080,
    output:path.relative(ROOT,path.join(logical,'rendered',name+'.mp4')).replaceAll('\\','/'),
    startedAt:new Date().toISOString(),status:'running',device:'CPU Chromium (--disable-gpu)',foreignJobsChanged:false};
  const save=()=>fs.writeFileSync(receipt,JSON.stringify(state,null,2)+'\n');save();
  let server,browser;
  try{
    process.env.DESIGN_EPISODE_SLUG=slug;
    const {createServer}=await import(pathToFileURL(path.join(MC,'node_modules/vite/dist/node/index.js')));
    server=await createServer({configFile:path.join(MC,'vite.design-finish-six.config.ts')});await server.listen();
    const puppeteer=require(path.join(MC,'node_modules/puppeteer'));
    browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--renderer-process-limit=2'],protocolTimeout:600000});
    const page=await browser.newPage();await page.goto('http://127.0.0.1:9268/render-worker.html');
    await page.waitForFunction(()=>typeof window.renderVideo==='function');
    const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(frame=>{
      state.frame=frame;save();console.log(slug,frame+'/'+(firstFrame+frames));
    }).catch(()=>{}),20000);
    try{await page.evaluate(job=>window.renderVideo(job),{
      route:`/src/projects/${slug}/batch-v1/project.ts`,name,frames,firstFrame,
      fps:60,width:1920,height:1080,exactFrameRange:true});}finally{clearInterval(pulse);}
    state.result=await page.evaluate(()=>window.renderJob);
    if(!state.result.done||state.result.result!==0||state.result.errors.length||!fs.existsSync(output))throw Error('Animation export incomplete: '+JSON.stringify(state.result));
    state.status='rendered-pixel-review-pending';state.completedAt=new Date().toISOString();save();
  }catch(e){state.status='failed';state.error=String(e);save();throw e;}
  finally{
    if(browser)await browser.close();if(server)await server.close();
    if(fs.existsSync(lease)&&JSON.parse(fs.readFileSync(lease,'utf8')).pid===process.pid)fs.unlinkSync(lease);
  }
}
main().catch(error=>{console.error(error);process.exitCode=1});
