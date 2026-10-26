// Finite Teardown-only renderer. No server/job starts when this file is imported.
const fs = require('node:fs'), path = require('node:path'), cp = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const slug = 'shorts-teardown-spray-palette', revision = 'spray-palette-v1';
const media = 'C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-teardown-spray-palette';
const outputRoot = path.join(media, 'local/motion-canvas-output');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const bounded = (promise, ms, label) => {
  let timer;
  return Promise.race([promise, new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error(label)),ms);})])
    .finally(()=>clearTimeout(timer));
};

function guard() {
  // Exact finite selection, frozen source/code hashes, actual timing, game/editor and lease checks.
  const code = "import sys;sys.path.insert(0,sys.argv[1]);from visual_revision import execution_guard,actual_inputs;execution_guard();actual_inputs()";
  cp.execFileSync(path.join(root, 'qwen3-tts/.venv/Scripts/python.exe'), ['-B', '-X', 'utf8', '-c', code, __dirname],
    {cwd:root, stdio:'pipe', windowsHide:true, env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
}

async function main() {
  guard();
  const [name, firstArg='0', countArg] = process.argv.slice(2);
  if (!/^[a-z0-9][a-z0-9-]{1,120}$/.test(name||'')) throw Error('Use a safe unique render name.');
  const timing = read(path.join(__dirname, 'visual-timing.json'));
  const localTiming = read(path.join(__dirname, 'local/visual-timing.json'));
  if (JSON.stringify(timing)!==JSON.stringify(localTiming) || timing.revision!==revision || timing.previewOnly!==false || timing.fps!==60)
    throw Error('Use the same actual final-PCM timing for this project and mixer.');
  const firstFrame=Number(firstArg), frames=countArg===undefined?timing.frames-firstFrame:Number(countArg);
  if (!Number.isInteger(firstFrame)||!Number.isInteger(frames)||firstFrame<0||frames<1||firstFrame+frames>timing.frames)
    throw Error('Requested frame range exceeds this exact current version.');
  const output=path.join(outputRoot,name+'.mp4'), receipt=path.join(media,'local',name+'-render.json');
  const diagnostics=path.join(media,'local',name+'-diagnostics.jsonl');
  if ([output,receipt,diagnostics].some(p=>fs.existsSync(p))) throw Error('Preserve prior render/receipt; select a new version name.');
  const response=await fetch('http://127.0.0.1:9277/__yamyam_production_scope',{signal:AbortSignal.timeout(10000)});
  if(!response.ok) throw Error('The isolated Teardown Vite server is not available.');
  const scope=await response.json();
  if(scope.slug!==slug||scope.revision!==revision||scope.output!==outputRoot.replaceAll('\\','/')||scope.productionWatch!=='disabled'||scope.encoderWebSocket!==true)
    throw Error('Port 9277 is wrong or not restarted with frozen production watching; preserve it and stop.');
  guard();
  const inputs=[__filename,path.join(__dirname,'visual-timing.json'),path.join(__dirname,'visual-config.json'),
    path.join(root,'motion-canvas/vite.teardown.config.ts'),path.join(root,'motion-canvas/render-worker.html'),
    ...['scene.tsx','model.ts','project.ts'].map(f=>path.join(root,'motion-canvas/src/projects',slug,f))];
  const inputHashes=Object.fromEntries(inputs.map(p=>[p,sha(p)]));
  fs.writeFileSync(diagnostics,'',{flag:'wx'});
  const log=(event,data={})=>fs.appendFileSync(diagnostics,JSON.stringify({at:new Date().toISOString(),event,...data})+'\n');
  const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer'));
  let browser,page,pulse,watchdog,result=null,failure=null,lastFrame=null,lastProgress=Date.now(),renderStarted=false;
  let fatalReject;
  const fatal=new Promise((_,reject)=>{fatalReject=reject;});
  // Keep the promise handled while browser setup precedes the render race.
  fatal.catch(()=>{});
  try {
    log('start',{slug,revision,name,firstFrame,frames,scope,inputHashes});
    browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
    browser.on('disconnected',()=>{log('browser-disconnected');if(renderStarted)fatalReject(Error('Owned browser disconnected during render.'));});
    browser.process()?.once('exit',(code,signal)=>log('browser-exit',{code,signal}));
    page=await browser.newPage();
    page.on('console',m=>{if(['error','warning','warn'].includes(m.type())||m.text().includes('[vite]'))log('console',{type:m.type(),text:m.text().slice(0,4000)});});
    page.on('pageerror',e=>log('pageerror',{message:String(e)}));
    page.on('error',e=>{log('page-crash',{message:String(e)});if(renderStarted)fatalReject(e);});
    page.on('requestfailed',req=>log('requestfailed',{url:req.url().slice(0,500),error:req.failure()?.errorText}));
    page.on('framenavigated',f=>{
      if(f!==page.mainFrame())return;
      log('main-frame-navigation',{url:f.url(),renderStarted});
      if(renderStarted)fatalReject(Error('Main page navigated/reloaded during render; inspect diagnostics.'));
    });
    const client=await page.createCDPSession();
    await client.send('Network.enable');
    client.on('Network.webSocketFrameReceived',event=>{
      try {
        const p=JSON.parse(event.response.payloadData);
        if(['full-reload','update','error','prune'].includes(p.type)) {
          log('vite-message',{message:p});
          if(renderStarted)fatalReject(Error('Vite changed a frozen render page: '+p.type));
        }
      } catch(e) { /* Non-JSON websocket frames are not production diagnostics. */ }
    });
    await page.goto('http://127.0.0.1:9277/render-worker.html',{waitUntil:'networkidle0',timeout:60000});
    await page.waitForFunction(()=>typeof renderVideo==='function',{timeout:60000});
    let reading=false;
    pulse=setInterval(async()=>{
      if(reading)return;
      reading=true;
      try {
        const status=await bounded(page.evaluate(()=>({frame:window.renderJob?.frame,done:window.renderJob?.done})),10000,'Progress read timed out.');
        if(Number.isFinite(status.frame)&&status.frame!==lastFrame){lastFrame=status.frame;lastProgress=Date.now();}
        log('progress',status);console.log('Frame '+status.frame);
      } catch(e) {log('progress-error',{message:String(e)});}
      finally{reading=false;}
    },15000);
    watchdog=setInterval(()=>{if(renderStarted&&Date.now()-lastProgress>180000)fatalReject(Error('No new frame for180seconds; partial output retained.'));},10000);
    renderStarted=true;lastProgress=Date.now();
    await bounded(Promise.race([fatal,page.evaluate(a=>window.renderVideo(a),{
      route:'/src/projects/shorts-teardown-spray-palette/project.ts',name,firstFrame,frames,
      fps:60,width:1080,height:1920,exactFrameRange:true})]),900000,'Render exceeded15minutes; use bounded chunks.');
    result=await bounded(page.evaluate(()=>window.renderJob),10000,'Final render state timed out.');
    if(!result?.done||result.result!==0||result.errors?.length||!fs.existsSync(output))throw Error('Renderer did not finish successfully.');
    if(Object.entries(inputHashes).some(([p,h])=>sha(p)!==h))throw Error('Inputs changed during render; do not promote the partial version.');
  } catch(error) {
    failure=error;
    log('failure',{message:String(error),stack:error.stack,lastFrame});
    if(page&&!page.isClosed()) {
      try {result=await bounded(page.evaluate(()=>window.renderJob),2000,'Failure-state read timed out.');}catch{}
      try {await bounded(page.evaluate(()=>window.cancelRender?.()),3000,'Cancel acknowledgement timed out.');}catch{}
    }
  } finally {
    renderStarted=false;clearInterval(pulse);clearInterval(watchdog);
    if(browser)try{await bounded(browser.close(),10000,'Owned browser close timed out.');}catch(e){log('close-error',{message:String(e)});}
    const record={...result,done:!failure&&result?.done===true,result:failure?null:result?.result,
      errors:[...(result?.errors||[]),...(failure?[String(failure)]:[])],
      slug,revision,output,firstFrame,frames,lastObservedFrame:lastFrame,
      outputSha256:fs.existsSync(output)?sha(output):null,timingSha256:inputHashes[path.join(__dirname,'visual-timing.json')],
      inputHashes,diagnostics,fullCurrentTimeline:!failure&&firstFrame===0&&frames===timing.frames,
      status:failure?'failed-preserved':'complete'};
    fs.writeFileSync(receipt,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  }
  if(failure)throw failure;
  console.log(JSON.stringify({output,receipt,diagnostics,firstFrame,frames}));
}

if(require.main===module) main().catch(error=>{console.error(error);process.exitCode=1;});
