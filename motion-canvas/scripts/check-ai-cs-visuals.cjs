// Local-app QA only. Saves representative frames without changing final outputs.
const puppeteer=require('puppeteer'),fs=require('fs'),path=require('path');
const out=path.resolve(__dirname,'../../shared/output/ai-cs-media-cache/visual-qa');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  const page=await browser.newPage();await page.setViewport({width:1480,height:1100});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/ai-cs-review.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.aiReview?.ready,{timeout:60000});
  const times=await page.evaluate(()=>aiReview.starts.flatMap((s,i)=>[{scene:i+1,kind:'example',t:s+3},{scene:i+1,kind:'example-middle',t:s+10},{scene:i+1,kind:'example-end',t:s+18.5},{scene:i+1,kind:'meme',t:s+aiReview.exampleSeconds+1},{scene:i+1,kind:'concept',t:s+aiReview.exampleSeconds+(aiReview.durations[i]-aiReview.exampleSeconds)*.84}]));
  for(const t of times){
   const frame=Math.round(t.t*30);
   await page.evaluate(n=>aiReview.jump(n),t.t);
   await page.waitForFunction(f=>aiReview.rendered===f,{timeout:30000},frame);
   const data=await page.evaluate(()=>aiReview.stage.finalBuffer.toDataURL('image/png').split(',')[1]);
   fs.writeFileSync(path.join(out,`${String(t.scene).padStart(2,'0')}-${t.kind}.png`),Buffer.from(data,'base64'));
   console.log(`QA ${t.scene} ${t.kind}`);
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({frames:times.length,errors},null,2));
  if(errors.length)throw Error(errors.join('\n'));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
