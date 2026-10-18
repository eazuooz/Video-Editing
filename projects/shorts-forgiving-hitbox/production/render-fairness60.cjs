// Finite export of this selected60s composition; preserve all completed versions.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),local=path.join(__dirname,'local/fairness-60s');
const mode=process.argv[2]||'full',firstFrame=Number(process.argv[3]||(mode.startsWith('preview')?1260:0)),frames=mode.startsWith('preview')?Number(process.argv[4]||180):3600;
const name='shorts-forgiving-hitbox-fairness60-'+mode,output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve existing completed render: '+output);
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9245/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Motion Canvas frame '+f+' / end '+(firstFrame+frames))).catch(()=>{}),15000);
try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-forgiving-hitbox-fairness60/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
console.log(JSON.stringify({output,firstFrame,frames,result:result.result}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
