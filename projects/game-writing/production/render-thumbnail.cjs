// Native HTML/CSS composition with original channel logo and observed source frame.
const path=require('node:path'),fs=require('node:fs'),crypto=require('node:crypto'),{pathToFileURL}=require('node:url');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu']});try{
 const page=await browser.newPage();await page.setViewport({width:1280,height:720,deviceScaleFactor:1});
 await page.goto(pathToFileURL(path.resolve(__dirname,'../publishing/thumbnail.html')).href);await page.evaluate(()=>document.fonts.ready);
 const images=await page.evaluate(()=>[...document.images].map(i=>({src:i.getAttribute('src'),complete:i.complete,width:i.naturalWidth})));
 if(images.some(i=>!i.complete||!i.width))throw Error('Thumbnail image failed to load');
 const file=path.resolve(__dirname,'../publishing/thumbnail.png');await page.screenshot({path:file});
 fs.writeFileSync(path.resolve(__dirname,'../publishing/thumbnail-recipe.json'),JSON.stringify({generatedAt:new Date().toISOString(),path:'projects/game-writing/publishing/thumbnail.png',width:1280,height:720,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),method:'Native HTML/CSS composition',concept:'yellow strip, white, large black Korean, original channel cats and actual game image',sourceFrame:{sourceVideoId:'YEgrKLregCw',seconds:48,rightsRecord:'projects/game-writing/sources/SOURCES.md'},brand:'shared/assets/branding/yamyamcoding-cats-original.png',aiLarianIPGeneration:false,visualReview:'pending',uploaded:false},null,2)+'\n');
 console.log('New channel-style thumbnail rendered locally; Studio upload has not been performed.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
