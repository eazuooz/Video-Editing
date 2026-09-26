const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'projects/small-window-game-design/preview/narrated-v1');
const timing=JSON.parse(fs.readFileSync(path.join(dir,'timing.json'),'utf8'));
const source=path.join(root,'shared/output/motion-canvas/small-window-voice-preview-render-v3.mp4');
const output=path.join(dir,'small-window-voice-preview-v1.mp4');
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
(async()=>{
 if(fs.existsSync(source)||fs.existsSync(output))throw Error('Preserve prior render; use new revision.');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const progress=setInterval(()=>page.evaluate(()=>renderJob.frame).then(f=>console.log(`Frame ${f}/${timing.frames}`)).catch(()=>{}),30000);
 try {await page.evaluate(frames=>renderVideo({route:'/src/projects/small-window-game-design/voice-preview/project.ts',name:'small-window-voice-preview-render-v3',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),timing.frames);} finally {clearInterval(progress);}
 const result=await page.evaluate(()=>renderJob);if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 }finally{await browser.close();}
 run('ffmpeg',['-v','error','-n','-i',source,'-i',path.join(root,'motion-canvas/src/projects/small-window-game-design/voice-preview/assets/review-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',String(timing.seconds),'-movflags','+faststart',output]);
 run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
 for(const [name,second] of [['game',8],['diagram',timing.gameplaySeconds+3]])run('ffmpeg',['-v','error','-n','-ss',String(second),'-i',output,'-frames:v','1',path.join(dir,`${name}.png`)]);
 console.log(output);
})().catch(e=>{console.error(e);process.exitCode=1;});
