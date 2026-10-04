// Read actual durations from our repository-owned Motion Canvas scenes.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const target=process.argv[2]||'measured-reel-v1/actual-scene-durations.json';
if(fs.existsSync(path.join(__dirname,target)))throw Error('Preserve duration evidence');
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9218/inspect-owned-scenes.html');await page.waitForFunction(()=>typeof inspectOwnedScenes==='function');const result=await page.evaluate(()=>inspectOwnedScenes());fs.mkdirSync(path.dirname(path.join(__dirname,target)),{recursive:true});fs.writeFileSync(path.join(__dirname,target),JSON.stringify({observedAt:new Date().toISOString(),...result},null,2)+'\n');console.log(JSON.stringify(result));if(result.errors.length)throw Error('Scene errors');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
