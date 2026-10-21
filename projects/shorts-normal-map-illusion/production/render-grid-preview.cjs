// Five CPU layout stills. No narration, full render, or replacement of v1 media.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const revision=process.argv[2]||'v2';
const root=path.resolve(__dirname,'../../..'),local=path.join(__dirname,'local'),out=path.join(local,'grid-rgb-source-preview-'+revision);
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8'));
if(control.selectedShortVideo!=='shorts-normal-map-illusion'||control.shortsDirectSelection?.selectedRevision!=='normal-map-v2-grid-rgb-deadcells')throw Error('Selection changed');
fs.mkdirSync(out,{recursive:true});
const ff='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe';
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9251/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  for(const [id,time] of [['grid-off',2],['grid-on',7],['signed',12],['encoding',17],['neutral',22],['game-start',25],['game-lift',28],['game-run',31]].filter(([id])=>!process.argv[3]||process.argv[3].split(',').includes(id))){
   const name='shorts-normal-map-illusion-grid-rgb-source-preview-'+revision+'-'+id,video=path.join(root,'shared/output/motion-canvas',name+'.mp4'),png=path.join(out,id+'.png');
   if(!fs.existsSync(video)){await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-normal-map-illusion/grid-preview-project.ts',name,firstFrame:time*60,frames:1,fps:60,width:1080,height:1920,exactFrameRange:true});const job=await page.evaluate(()=>window.renderJob);if(!job.done||job.result!==0||job.errors.length)throw Error(JSON.stringify(job));}
   if(!fs.existsSync(png)){const r=cp.spawnSync(ff,['-v','error','-n','-i',video,'-frames:v','1',png],{cwd:root,windowsHide:true,encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);}console.log(id);
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
