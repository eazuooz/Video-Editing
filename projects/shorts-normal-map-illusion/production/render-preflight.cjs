// CPU-only layout stills use actual sparse native Unity preview frames, never a fake full capture.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const revision=process.argv[2]||'v1';
const finalInputs=process.argv[4]==='final';
const root=path.resolve(__dirname,'../../..'),out=path.join(__dirname,'local/preflight-'+revision);
fs.mkdirSync(out,{recursive:true});
const ff='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe';
const times=process.argv[3]?process.argv[3].split(',').map(Number):[1,5,9,15,21,26,33,40,46,51];
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9251/render-worker.html'+(finalInputs?'':'?preflight=1'));await page.waitForFunction(()=>typeof renderVideo==='function');const rows=[];
for(const time of times){const frame=Math.round(time*60),name='shorts-normal-map-illusion-preflight-'+revision+'-'+frame,video=path.join(root,'shared/output/motion-canvas',name+'.mp4'),png=path.join(out,'frame-'+frame+'.png');
 if(!fs.existsSync(video)){await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-normal-map-illusion/project.ts',name,firstFrame:frame,frames:1,fps:60,width:1080,height:1920,exactFrameRange:true});const job=await page.evaluate(()=>window.renderJob);if(!job.done||job.result!==0||job.errors.length)throw Error(JSON.stringify(job));}
 if(!fs.existsSync(png)){const ass='projects/shorts-normal-map-illusion/production/local/captions.ko.ass';const result=cp.spawnSync(ff,['-v','error','-n','-i',video,'-vf',`setpts=PTS+${frame/60}/TB,ass=${ass},setpts=PTS-STARTPTS`,'-frames:v','1',png],{cwd:root,encoding:'utf8',windowsHide:true});if(result.status!==0)throw Error(result.stderr);}
 rows.push({time:frame/60,frame,png:path.relative(root,png).replaceAll('\\','/'),kind:finalInputs?'Current continuous full capture input, single-frame composition QA':'preflight-only sparse native Unity states for layout; final uses continuous full capture'});console.log('Preflight '+time);
}
fs.writeFileSync(path.join(out,'index.json'),JSON.stringify({status:'layout-preflight-only',rows},null,2)+'\n');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
