// Isolated headless Chrome QA; play and seek the real served media through the script-review controls.
const path=require('path'),fs=require('fs');
const root=path.resolve(__dirname,'../../../..');
const browserDriver=require(path.join(root,'motion-canvas/node_modules/puppeteer-core'));
(async()=>{
 const browser=await browserDriver.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--disable-gpu','--no-first-run','--autoplay-policy=no-user-gesture-required']});
 try{
 const source='http://127.0.0.1:9359',rows=(await (await fetch(source+'/delivery/review-ten.json')).json()).projects.filter(r=>r.generated);
 const results=[];
 for(const r of rows){
 const tab=await browser.newPage();await tab.setViewport({width:375,height:810});
 const url=source+'/'+r.slug+'/local/final-reviewed-feedback-nov05-r2/index.html';
 await tab.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
 const pos=await tab.$eval('button:nth-of-type(1)',b=>Number(b.dataset.sec));
 await tab.click('button');await tab.waitForFunction('document.querySelector("video").currentTime > 0.65', {timeout:25000});
 const later=await tab.$$eval('button',buttons=>{const b=buttons[Math.floor(buttons.length/2)];b.click();return Number(b.dataset.sec)});
 await tab.waitForFunction(s=>document.querySelector('video').currentTime>s+.25,{timeout:25000},later);
 const status=await tab.$eval('video',v=>({src:v.currentSrc,time:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null,readyState:v.readyState}));
 if(status.error||status.width!==1080||status.height!==1920)throw Error(JSON.stringify(status));
 results.push({n:r.order,master:r.masterSha256,played:true,seekedTo:later,...status});await tab.close();
 }
 const out=path.join(JSON.parse(fs.readFileSync(path.join(__dirname,'../batch.json'),'utf8')).mediaRoot,'feedback-nov05','player-'+rows.length+'.json');fs.writeFileSync(out,JSON.stringify(results,null,2));console.log('Play + script seek passed:',rows.length);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
