// CPU-only layout stills use actual sparse native Unity preview frames, never a fake full capture.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const revision=process.argv[2]||'v1';
const finalInputs=true;
const root=path.resolve(__dirname,'../../..'),out=path.join(__dirname,'local/preflight-'+revision);
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8'));
if(control.selectedShortVideo!=='shorts-interior-mapping-window'||control.shortsDirectSelection?.selectedRevision!=='interior-mapping-v1')throw Error('Selection changed');
const timing=JSON.parse(fs.readFileSync(path.join(__dirname,'visual-timing.json'),'utf8'));
if(timing.revision!=='interior-mapping-v1')throw Error('Current aligned v2 timeline missing');
const ass='projects/shorts-interior-mapping-window/production/local/audio-r2/captions.ko.ass';
if(!fs.existsSync(path.join(root,ass)))throw Error('Current v2 actual ASS missing');
fs.mkdirSync(out,{recursive:true});
const ff='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe';
const times=process.argv[3]?process.argv[3].split(',').map(Number):[...new Set(timing.sections.flatMap(s=>[Math.min(s.end-1/60,s.start+.65),...(s.events??[]).map(e=>Math.min(s.end-1/60,e.start+.12))]).map(t=>Math.round(t*60)/60))];
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9252/render-worker.html'+(finalInputs?'':'?preflight=1'));await page.waitForFunction(()=>typeof renderVideo==='function');const rows=[];
for(const time of times){await page.goto('http://127.0.0.1:9252/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');const frame=Math.round(time*60),name='shorts-interior-mapping-window-preflight-'+revision+'-'+frame,video=path.join(root,'shared/output/motion-canvas',name+'.mp4'),png=path.join(out,'frame-'+frame+'.png');
 if(!fs.existsSync(video)){await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-interior-mapping-window/project.ts',name,firstFrame:frame,frames:1,fps:60,width:1080,height:1920,exactFrameRange:true});const job=await page.evaluate(()=>window.renderJob);if(!job.done||job.result!==0||job.errors.length)throw Error(JSON.stringify(job));}
 if(!fs.existsSync(png)){const result=cp.spawnSync(ff,['-v','error','-n','-i',video,'-vf',`setpts=PTS+${frame/60}/TB,ass=${ass},setpts=PTS-STARTPTS`,'-frames:v','1',png],{cwd:root,encoding:'utf8',windowsHide:true});if(result.status!==0)throw Error(result.stderr);}
 rows.push({time:frame/60,frame,png:path.relative(root,png).replaceAll('\\','/'),kind:finalInputs?'Current frame-indexed native input; may be preview-only partial spatial patch; single-frame composition QA':'preflight-only sparse native Unity states for layout; final uses continuous full capture'});console.log('Preflight '+time);
}
fs.writeFileSync(path.join(out,'index.json'),JSON.stringify({status:'layout-preflight-only',rows},null,2)+'\n');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
