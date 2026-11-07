/* Inert on import. Exact11.05 PNG atlas under a current owned coordinator.
 * Public Renderer/Exporter, pinned bootstrap bridge, no editor/default plugin,
 * user browser profile, settings persistence, FFmpeg or unrelated source writes. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const ROOT=path.resolve(__dirname,'../../..'),MOTION=path.join(ROOT,'motion-canvas');
const MEDIA='C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05';
const PROTOCOL='architectural111-11-05-structure-atlas-v1',OWNER='architectural-111-11-05-structure-atlas';
const NAMES=['project-structure-atlas-v2.ts','solution-path-structure-atlas-v2.tsx','solution-path-structure.tsx'];
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const under=(p,r)=>{const rel=path.relative(path.resolve(r),path.resolve(p));return !!rel&&!rel.startsWith('..')&&!path.isAbsolute(rel);};
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const save=(p,v)=>{const t=`${p}.${process.pid}.tmp`;fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n',{flag:'wx'});fs.renameSync(t,p);};
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function validateJob(job,jobPath,checkFiles=true){
 const r=job.recipe,c=job.contract;
 if(job.schemaVersion!=='11.05-structure-atlas-execution-job-v1'||job.topicId!=='11.05'||
   !r||r.schemaVersion!=='11.05-structure-snapshot-job-v2'||r.topicId!=='11.05'||
   !/^[a-f0-9]{64}$/.test(job.fingerprint)||!c||c.width!==1080||c.height!==900||c.fps!==60||
   c.audio!==false||c.alpha!==true||!Number.isInteger(c.frames)||c.frames<1||c.frames>24960||
   c.frames!==r.assetFrames||r.packets.length!==c.frames||!equal(r.canvas,[1080,900])||r.exportFps!==60)
   throw Error('Exact finite11.05 current source-packet PNG atlas required');
 if(!under(job.attempt,path.join(MEDIA,'structure-attempts-v2'))||
   path.resolve(jobPath)!==path.join(path.resolve(job.attempt),'execution-job.json')||
   !under(job.sourceJob.path,path.join(MEDIA,'structure-jobs-v2'))||
   path.resolve(job.sourceJob.path)!==path.resolve(r.outputContract.jobPath))throw Error('Owned atlas paths required');
 if(!equal(job.stagedSources.map(x=>x.name),NAMES)||job.stagedSources.some(x=>
   path.resolve(x.path)!==path.join(MOTION,'src/projects/shorts-leveldesign-11-05',x.name))||
   path.resolve(job.font.path)!==path.resolve('C:/Windows/Fonts/NotoSansKR-VF.ttf'))throw Error('Exact owned sources/font only');
 if(job.variables.renderMode!=='source-pinned-structural-atlas-v2'||job.variables.jobFingerprint!==r.fingerprint||
   !equal(job.variables.sourcePackets,r.packets))throw Error('Exact finite source-packet variables required');
 const paths=new Set(job.inputPins.map(x=>path.resolve(x.path)));
 if([...job.stagedSources.map(x=>x.path),job.font.path,job.sourceJob.path,__filename].some(x=>!paths.has(path.resolve(x))))throw Error('Mandatory source/job/font/worker pins missing');
 if(job.actualSpeechTimingVerified!==false||job.nativePixelVisibilityClaim!==false||job.humanApproval!==false)throw Error('Atlas cannot approve speech/pixel visibility/humans');
 if(checkFiles){
  for(const x of job.inputPins)if(!/^[a-f0-9]{64}$/.test(x.sha256)||sha(x.path)!==x.sha256)throw Error(`Changed source ${x.path}`);
  if(sha(job.sourceJob.path)!==job.sourceJob.sha256||!equal(read(job.sourceJob.path),r))throw Error('Actual immutable source job differs');
  if(sha(job.tools.node.path)!==job.tools.node.sha256||path.resolve(job.tools.node.path).toLowerCase()!==path.resolve(process.execPath).toLowerCase())throw Error('Current Node executable changed');
 }
 return job;
}
function leaseMatches(job,rec,nodePid=process.pid){
 const x=job.lifecycle,p=x?.parent;
 return x&&x.protocol===PROTOCOL&&x.owner===OWNER&&typeof x.token==='string'&&x.token.length>0&&
  Number.isInteger(p?.pid)&&Number.isFinite(p.createTime)&&Array.isArray(p.argv)&&/^[a-f0-9]{64}$/.test(p.commandSHA256)&&
  rec.protocol===x.protocol&&rec.owner===x.owner&&rec.token===x.token&&rec.pid===p.pid&&rec.createTime===p.createTime&&
  rec.commandSHA256===p.commandSHA256&&equal(rec.argv,p.argv)&&rec.fingerprint===job.fingerprint&&
  path.resolve(rec.output)===path.resolve(job.attempt)&&rec.child?.pid===nodePid&&Number.isFinite(rec.child.createTime)&&
  Array.isArray(rec.child.argv)&&equal(rec.child.argv.slice(1),[__filename,job.jobPath,job.jobSHA256]);
}
async function verifyLease(job){
 if(path.resolve(job.lifecycle?.leasePath||'')!==path.join(ROOT,'shared/output/GPU_HANDOFF.json'))throw Error('Exact shared lease path required');
 for(let i=0;i<50;i++){
  const rec=read(job.lifecycle.leasePath);
  if(leaseMatches(job,rec)){try{process.kill(rec.pid,0);}catch{throw Error('Coordinator no longer live');}return;}
  // Only registration of this exact pre-recorded Node command may be pending.
  const command=rec.pendingCommand;
  if(rec.phase!=='launching'||rec.token!==job.lifecycle.token||!Array.isArray(command)||
    path.resolve(command[0]).toLowerCase()!==path.resolve(process.execPath).toLowerCase()||
    !equal(command.slice(1),process.argv.slice(1)))throw Error('Lease/actual child identity changed');
  await new Promise(resolve=>setTimeout(resolve,100));
 }
 throw Error('Exact child PID/create/argv registration missing; no renderer started');
}
function pngDimensions(data){
 const b=Buffer.isBuffer(data)?data:Buffer.from(data.split(',')[1],'base64');
 if(b.length<26||b.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||b.subarray(12,16).toString()!=='IHDR')throw Error('Actual PNG required');
 return {buffer:b,width:b.readUInt32BE(16),height:b.readUInt32BE(20),colorType:b[25]};
}
function sceneBridge(staged){
 const expected=path.resolve(staged,'solution-path-structure-atlas-v2.tsx');
 return {name:'owned-readonly-scene-import',load(id){
  if(!/[?&]scene\b/.test(id))return;
  if(path.resolve(id.split('?')[0])!==expected)throw Error('Unexpected scene import');
  // The installed scenes loader's public description/meta linkage, with a
  // virtual MetaFile(false); no createMeta, disk/meta/HMR settings writes.
  return `import {MetaFile} from '@motion-canvas/core';import description from './solution-path-structure-atlas-v2.tsx';description.name='owned-source-atlas';new MetaFile('owned-source-atlas',false).attach(description.meta);export default description;`;
 }};
}
function workerPage(job){
 const vars=JSON.stringify(job.variables).replaceAll('<','\\u003c');
 return `<!doctype html><html><head><meta charset="utf-8"><style>@font-face{font-family:'Noto Sans KR';src:url('/NotoSansKR-VF.ttf');font-style:normal;font-weight:100 900}body{margin:0;background:transparent}</style></head><body><script type="module">
import config from './project-structure-atlas-v2.ts';
import {Renderer,Vector2,MetaFile,MetaField,bootstrap} from '@motion-canvas/core';
const contract=${JSON.stringify(job.contract)};
class OwnedExporter{static id='yamyam/11-05-owned-atlas';static displayName='Finite11.05 source PNG atlas';static async create(){return new OwnedExporter()};static meta(){return new MetaField('options',{})};async handleFrame(canvas,frame,sceneFrame,sceneName,signal){if(signal.aborted)throw Error('Owned atlas aborted');await window.__ownedFrame(canvas.toDataURL('image/png'),frame,sceneFrame,sceneName)}async stop(result){window.__ownedResult=result}}
const project=bootstrap('11-05-owned-structure',${JSON.stringify(job.versions)},[{name:'owned-source-exporter',exporters:()=>[OwnedExporter]}],{...config,audio:undefined,variables:${vars}},new MetaFile('owned-project',false),new MetaFile('owned-settings',false));
project.meta.shared.size.set(new Vector2(1080,900));project.meta.shared.background.set(null);project.meta.shared.range.set([0,contract.frames/60]);project.meta.shared.audioOffset.set(0);project.meta.rendering.fps.set(60);project.meta.rendering.resolutionScale.set(1);project.meta.rendering.exporter.set({name:OwnedExporter.id,options:{}});
window.__ownedErrors=[];window.__ownedResult=null;project.logger.onLogged.subscribe(e=>{if(e.level==='error')window.__ownedErrors.push(String(e.message))});
await document.fonts.load('700 48px "Noto Sans KR"');await document.fonts.load('500 32px "Noto Sans KR"');await document.fonts.ready;window.__ownedReady=true;
window.__ownedRun=async()=>{const renderer=new Renderer(project);renderer.onFinished.subscribe(r=>window.__ownedResult=r);const settings={...project.meta.getFullRenderingSettings(),name:'owned11-05-atlas',range:[0,Math.max(0,(contract.frames-1.25)/60)],fps:60,size:new Vector2(1080,900),resolutionScale:1,colorSpace:'srgb',background:null,exporter:{name:OwnedExporter.id,options:{}}};await renderer.render(settings);if(window.__ownedResult!==0||window.__ownedErrors.length)throw Error(JSON.stringify({result:window.__ownedResult,errors:window.__ownedErrors}));return {settings:{...settings,size:{x:1080,y:900}},result:window.__ownedResult}};
</script></body></html>`;
}
async function main(jobPath,expectedSHA){
 if(!jobPath||!/^[a-f0-9]{64}$/.test(expectedSHA||'')||sha(jobPath)!==expectedSHA)throw Error('Exact immutable parent-pinned execution job required');
 const job=validateJob(read(jobPath),jobPath);job.jobPath=path.resolve(jobPath);job.jobSHA256=expectedSHA;
 await verifyLease(job);
 const attempt=path.resolve(job.attempt),staged=path.join(attempt,'staged');fs.mkdirSync(staged);
 for(const s of job.stagedSources)fs.copyFileSync(s.path,path.join(staged,s.name),fs.constants.COPYFILE_EXCL);
 fs.copyFileSync(job.font.path,path.join(staged,'NotoSansKR-VF.ttf'),fs.constants.COPYFILE_EXCL);
 fs.writeFileSync(path.join(staged,'worker.html'),workerPage(job),{flag:'wx'});
 // Runtime dependencies load only after an explicit verified owned invocation.
 const {createServer}=await import(pathToFileURL(path.join(MOTION,'node_modules/vite/dist/node/index.js')).href);
 const {webglPlugin}=require(path.join(MOTION,'node_modules/@motion-canvas/vite-plugin/lib/partials/webgl.js'));
 const puppeteer=require(path.join(MOTION,'node_modules/puppeteer'));
 let server,browser,actual,error,frames=[];
 try{
  server=await createServer({configFile:false,root:staged,cacheDir:path.join(attempt,'vite-cache'),plugins:[sceneBridge(staged),webglPlugin()],esbuild:{jsx:'automatic',jsxImportSource:'@motion-canvas/2d/lib'},resolve:{alias:['core','2d'].map(k=>({find:'@motion-canvas/'+k,replacement:path.join(MOTION,'node_modules/@motion-canvas/'+k)}))},optimizeDeps:{entries:[path.join(staged,'project-structure-atlas-v2.ts')],exclude:['preact','preact/*','@preact/signals']},server:{host:'127.0.0.1',port:0,strictPort:true,fs:{allow:[staged,path.join(MOTION,'node_modules')]}}});
  await server.listen();await verifyLease(job);
  const exe=puppeteer.executablePath(),profile=path.join(attempt,'chromium-profile');
  save(path.join(attempt,'browser-launch-gap.json'),{pending:true,nodePid:process.pid,exe,exeSHA256:sha(exe),userDataDir:profile,after:Date.now()/1000});
  browser=await puppeteer.launch({headless:true,userDataDir:profile,protocolTimeout:45*60*1000,args:['--disable-gpu','--use-gl=angle','--use-angle=swiftshader','--disable-background-networking','--no-first-run','--no-default-browser-check']});
  save(path.join(attempt,'owned-child-details.json'),{nodePid:process.pid,browserPid:browser.process()?.pid,browserArgv:browser.process()?.spawnargs,attempt});
  save(path.join(attempt,'browser-launch-gap.json'),{pending:false,nodePid:process.pid,browserPid:browser.process()?.pid,exe,exeSHA256:sha(exe),userDataDir:profile});
  const page=await browser.newPage();await page.setRequestInterception(true);
  page.on('request',request=>{const u=new URL(request.url());if(u.hostname==='127.0.0.1'||['data:','blob:'].includes(u.protocol))request.continue();else request.abort()});
  const diagnostics=[];page.on('pageerror',e=>diagnostics.push(String(e.message)));
  await page.exposeFunction('__ownedFrame',async(payload,frame,sceneFrame,sceneName)=>{
   if(frame!==frames.length||frame>=job.contract.frames)throw Error('Unexpected actual exported asset index');
   await verifyLease(job);const png=pngDimensions(payload);if(png.width!==1080||png.height!==900||png.colorType!==6)throw Error('Actual1080x900 RGBA PNG required');
   const file=path.join(attempt,`atlas-${String(frame).padStart(6,'0')}.png`);fs.writeFileSync(file,png.buffer,{flag:'wx'});const packet=job.recipe.packets[frame];
   frames.push({atlasIndex:frame,packetFingerprint:packet.fingerprint,mode:packet.mode,nativeFrame:packet.nativeFrame,image:{path:file,sha256:sha(file)},sceneFrame,sceneName});
  });
  await page.goto(`http://127.0.0.1:${server.httpServer.address().port}/worker.html`,{waitUntil:'domcontentloaded',timeout:90000});
  await page.waitForFunction(()=>window.__ownedReady,{timeout:60000});actual=await page.evaluate(()=>window.__ownedRun());
  if(frames.length!==job.contract.frames||diagnostics.length)throw Error('Incomplete actual atlas or SDK diagnostics');
 }catch(e){error=e;}finally{if(browser)await browser.close();if(server)await server.close();}
 if(error){save(path.join(attempt,'failed.json'),{complete:false,error:String(error.stack||error),frames,actual});throw error;}
 validateJob(job,jobPath);await verifyLease(job);if(sha(jobPath)!==expectedSHA)throw Error('Execution job changed');
 const stagedSources=job.stagedSources.map(s=>({name:s.name,path:path.join(staged,s.name),sha256:sha(path.join(staged,s.name))}));
 for(const s of stagedSources)if(s.sha256!==job.inputPins.find(p=>path.resolve(p.path)===path.resolve(job.stagedSources.find(x=>x.name===s.name).path))?.sha256)throw Error('Actually rendered staged source changed');
 const stagedFont={path:path.join(staged,'NotoSansKR-VF.ttf'),sha256:sha(path.join(staged,'NotoSansKR-VF.ttf'))};if(stagedFont.sha256!==job.font.sha256)throw Error('Actually rendered font changed');
 save(path.join(attempt,'render-manifest.json'),{schemaVersion:'11.05-structure-atlas-manifest-v2',topicId:'11.05',complete:true,job:job.sourceJob,jobFingerprint:job.recipe.fingerprint,picturePlanFingerprint:job.recipe.picturePlanFingerprint,canvas:[1080,900],assetFrames:frames.length,frames,aliases:job.recipe.aliases,producer:job.producer,inputPins:job.inputPins,stagedSources,stagedFont,executionJob:{path:jobPath,sha256:expectedSHA},actualSdk:actual,actualVisualReview:false,actual375Reviewed:false,actualSpeechTimingVerified:false,nativePixelVisibilityClaim:false,humanApproval:false});
}
module.exports={validateJob,leaseMatches,pngDimensions,workerPage,sceneBridge,under};
if(require.main===module)main(process.argv[2],process.argv[3]).catch(e=>{console.error(e.stack||e);process.exitCode=1});
