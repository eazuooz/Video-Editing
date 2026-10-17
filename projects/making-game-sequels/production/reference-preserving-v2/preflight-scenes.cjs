const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..'),out=path.join(root,'projects/making-game-sequels/production/local/reference-preserving-v2/preflight');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});try{
const page=await browser.newPage();await page.goto('http://127.0.0.1:9231/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
const selected=process.argv[2]?process.argv[2].split(',').map(x=>Number(x)-1):Array.from({length:9},(_,i)=>i);
for(const i of selected){
 const name='game-sequels-design-'+(i+1);await page.evaluate(p=>renderVideo(p),{route:'/src/projects/making-game-sequels/revision-v2/project.ts',name,frames:1,firstFrame:i*720+540,fps:60,width:1920,height:1080,exactFrameRange:true});
 const r=await page.evaluate(()=>renderJob);if(!r.done||r.result!==0||r.errors.length)throw Error(JSON.stringify(r));
 cp.execFileSync('ffmpeg',['-v','error','-y','-i',path.join(root,'shared/output/motion-canvas',name+'.mp4'),'-frames:v','1',path.join(out,`scene-${String(i+1).padStart(2,'0')}.png`)]);
 console.log('scene '+(i+1));
}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
