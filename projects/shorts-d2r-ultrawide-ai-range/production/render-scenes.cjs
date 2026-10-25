// Explicit finite CPU Motion Canvas job. Parent coordinates all large renders.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer'));
const map={ultrawide:'shorts-d2r-ultrawide-ai-range',grass:'shorts-d2r-loot-grass-clearance',sprites:'shorts-d2-modular-sprite-equipment'};
const topic=process.argv[2],mode=process.argv[3]||'preview',firstFrame=Number(process.argv[4]||0),count=Number(process.argv[5]||1),port=Number(process.argv[6]||9265);
if(!map[topic]||!['preview','full'].includes(mode))throw Error('Pass an owned topic and preview/full.');
const slug=map[topic],p=path.join(root,'projects',slug),read=x=>JSON.parse(fs.readFileSync(x,'utf8'));
const auth=read(path.join(root,'shared/publishing/video-production-control.json')).scopedBatchAuthorizations?.['explicit-ten-distinctive-shorts-20261025'];
if(!auth?.fullProductionAuthorized||!auth.slugs?.includes(slug))throw Error('Current explicit ten-Short scope must include this project.');
const timing=read(path.join(p,'production/visual-timing.json')),config=read(path.join(p,'production/scene-config.json')),plan=read(path.join(p,'planning/production-plan.json'));
const frames=mode==='full'?timing.frames:count;
if(mode==='full'&&(!plan.scriptFinalized||!plan.independentFootageViewed||!config.footageReady||timing.previewOnly!==false||timing.status!=='actual-pcm-caption-aligned'))throw Error('No full render before actual footage, narration and PCM timing are checked.');
if(mode==='preview'&&frames>180)throw Error('Preview capped at three seconds; coordinate full jobs separately.');
const name=slug+'-'+mode+'-'+firstFrame+'-'+Date.now(),local=path.join(p,'production/local');fs.mkdirSync(local,{recursive:true});
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:'+port+'/render-worker.html');await page.waitForFunction(()=>typeof window.renderVideo==='function');
 await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/diablo-tricks-shorts-20261025/'+topic+'/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});
 const result=await page.evaluate(()=>window.renderJob);const record={...result,slug,mode,firstFrame,frames,output:'shared/output/motion-canvas/'+name+'.mp4',gpuRendering:false};
 fs.writeFileSync(path.join(local,name+'.json'),JSON.stringify(record,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));console.log(JSON.stringify(record));
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
