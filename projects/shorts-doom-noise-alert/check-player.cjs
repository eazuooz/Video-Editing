const path=require('path'),fs=require('fs');
const root=path.resolve(__dirname,'../..');
const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer-core'));
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'project.json'),'utf8'));
 const folder=path.join(data.mediaRoot,'final-reviewed-v2');
 const receipt=JSON.parse(fs.readFileSync(path.join(folder,'delivery.json'),'utf8'));
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--disable-gpu','--no-first-run','--autoplay-policy=no-user-gesture-required']});
 try{
  const page=await browser.newPage();await page.setViewport({width:375,height:810});
  await page.goto('http://127.0.0.1:'+process.argv[2]+'/index.html',{waitUntil:'domcontentloaded'});
  await page.click('button');await page.waitForFunction('document.querySelector("video").currentTime>.75');
  const target=await page.$$eval('button',items=>{let b=items[Math.floor(items.length/2)];b.click();return Number(b.dataset.s)});
  await page.waitForFunction(t=>document.querySelector('video').currentTime>t+.3,{},target);
  const result=await page.$eval('video',v=>({source:v.currentSrc,time:v.currentTime,width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null}));
  if(result.width!==1080||result.height!==1920||result.error)throw Error(JSON.stringify(result));
  const r={...result,masterSha256:receipt.files[1].sha256,seeked:target,viewportWidth:375,completeRealTimeWatch:false};
  fs.writeFileSync(path.join(folder,'player-check.json'),JSON.stringify(r,null,2));console.log(r);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
