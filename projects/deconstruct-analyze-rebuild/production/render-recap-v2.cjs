const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const {spawnSync}=require('node:child_process');
const work=path.join(__dirname,'final-v2'),p=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
(async()=>{
 if(!p.additionalExplanationFrames)return;
 if(!process.argv.includes('--normalize-only')){
 const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');await page.evaluate(frames=>renderVideo({route:'/src/projects/deconstruct-analyze-rebuild/expanded-v2/recap-project.ts',name:'deconstruct-analyze-rebuild-expanded-recap',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),p.additionalExplanationFrames);const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'recap-render-result.json'),JSON.stringify(result,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));}finally{await browser.close();}
 fs.copyFileSync(path.resolve(__dirname,'../../../shared/output/motion-canvas/deconstruct-analyze-rebuild-expanded-recap.mp4'),path.join(work,'recap.mp4'));
 }
 const normalized=path.join(work,'recap-normalized.mp4');const result=spawnSync('ffmpeg',['-v','error','-y','-i',path.join(work,'recap.mp4'),'-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',normalized],{encoding:'utf8',windowsHide:true});if(result.status!==0)throw Error(result.stderr);fs.copyFileSync(normalized,path.join(work,'recap.mp4'));
})().catch(e=>{console.error(e);process.exitCode=1;});
