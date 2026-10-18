// Render only our authored Motion Canvas scene using the repository export worker.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),local=path.join(__dirname,'local');
const mode=process.argv[2]||'full',frames=mode.startsWith('preview')?180:1800,firstFrame=mode.startsWith('preview')?450:0;
const name='shorts-forgiving-hitbox-'+mode;
const output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve existing completed render: '+output);
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9244/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Motion Canvas frame '+f+'/'+frames)).catch(()=>{}),15000);
try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-forgiving-hitbox/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
console.log(JSON.stringify({output,frames,result:result.result}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
