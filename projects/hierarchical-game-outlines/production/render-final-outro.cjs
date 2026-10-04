// Local source-render worker, never a YouTube Studio UI controller.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const work=path.join(__dirname,'final-v1'),plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
if(!plan.finalSourceTimingApproved||!600)throw Error('Install exact reviewed compiled timing first');
if(fs.existsSync(path.join(work,'outro-render-result.json')))throw Error('Review existing render rather than duplicate it');
const root=path.resolve(__dirname,'../../..'),stateFile=path.join(work,'outro-render-execution.json'),queueFile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
if(fs.existsSync(stateFile))throw Error('Inspect existing render execution rather than duplicate it');
let browserPid=null,lastFrame=0;
function save(status,exitCode=null){const state={pid:process.pid,browserPid,status,frame:lastFrame,frames:600,updatedAt:new Date().toISOString(),exitCode,renderMode:'CPU Chromium disabled GPU; single original membership render',finalVideo:false,captionPixelReview:'pending'};fs.writeFileSync(stateFile,JSON.stringify(state,null,2)+'\n');const q=JSON.parse(fs.readFileSync(queueFile,'utf8')),item=q.items.find(i=>i.slug==='hierarchical-game-outlines');item.execution.outroRender=state;item.execution.activeTasks=status==='running'?[{kind:'local-MC-original-membership-render',pid:process.pid,browserPid,state:path.relative(root,stateFile).replaceAll('\\','/')}]:[];item.updatedAt=state.updatedAt;fs.writeFileSync(queueFile,JSON.stringify(q,null,2)+'\n');}
save('running');process.on('exit',code=>save(code===0?'finished':'failed',code));
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
 browserPid=browser.process()?.pid??null;save('running');
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9216/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>{lastFrame=frame;save('running');console.log(`Original membership outro ${frame}/${600}`);}).catch(()=>{}),20000);
  try{await page.evaluate(frames=>renderVideo({route:'/src/projects/hierarchical-game-outlines/membership-project.ts',name:'hierarchical-game-outlines-membership-outro',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),600);}finally{clearInterval(pulse);}
  const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'outro-render-result.json'),JSON.stringify({createdAt:new Date().toISOString(),pid:process.pid,renderMode:'headless-source-worker-disabled-gpu',frames:600,finalVideo:false,captionPixelReview:'pending',...result},null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
