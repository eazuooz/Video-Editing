const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),slug=path.basename(path.dirname(__dirname));
const timing=JSON.parse(fs.readFileSync(path.join(__dirname,'visual-timing.json'),'utf8'));
const project=JSON.parse(fs.readFileSync(path.join(__dirname,'../project.json'),'utf8'));
if(!project.authorization.fullProductionAuthorized)throw Error('Project not authorized');
const mode=process.argv[2]||'preview-silent-v1',firstFrame=Number(process.argv[3]||0),frames=Number(process.argv[4]||timing.frames);
if(!/^[a-z0-9-]+$/.test(mode)||!Number.isInteger(firstFrame)||!Number.isInteger(frames)||firstFrame<0||frames<1)throw Error('Invalid render range or version name');
const name=slug+'-'+mode,exporterRoot=process.env.YAMYAM_RENDER_OUTPUT_ROOT||path.join(root,'shared/output/motion-canvas');
const output=path.join(exporterRoot,name+'.mp4'),localOutput=path.join(__dirname,'local',name+'.mp4');
if(fs.existsSync(output)||fs.existsSync(localOutput))throw Error('Preserve completed render; choose a new version name '+name);
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:'+(process.env.YAMYAM_RENDER_PORT||'9265')+'/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f)).catch(()=>{}),15000);
try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/'+slug+'/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(__dirname,'local/motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');
if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
if(!fs.existsSync(output))throw Error('Exporter completed but output not at configured YAMYAM_RENDER_OUTPUT_ROOT: '+output);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),sha256=hash(output);
if(path.resolve(output)!==path.resolve(localOutput)){
 fs.copyFileSync(output,localOutput,fs.constants.COPYFILE_EXCL);
 if(hash(localOutput)!==sha256)throw Error('Copied render hash mismatch; preserve both files');
 fs.unlinkSync(output); // Only this invocation's newly-created temporary export, after verified preservation.
}
result.preservedPreview={path:localOutput,sha256};fs.writeFileSync(path.join(__dirname,'local/motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output:localOutput,sha256,firstFrame,frames}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
