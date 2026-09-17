// Headless QA of our local application only.
const puppeteer=require('puppeteer'),fs=require('node:fs'),path=require('node:path');
const out=path.resolve(__dirname,'../../shared/output/let-them-play/visual-qa');
async function main(){
 fs.mkdirSync(out,{recursive:true});const browser=await puppeteer.launch({headless:true});const errors=[];
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-review.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.thirdReview?.ready,{timeout:60000});
  const timing=await page.evaluate(()=>({starts:thirdReview.starts,segment:thirdReview.segmentSeconds,duration:thirdReview.player.playback.duration}));
  if(timing.duration!==28080)throw Error('Wrong runtime frames: '+timing.duration);
  const images=[];
  for(let i=0;i<8;i++)for(let k=0;k<3;k++){
   const t=timing.starts[i]+timing.segment*(k+0.68),frame=Math.round(t*60);
   await page.evaluate(t=>thirdReview.jump(t),t);
   await page.waitForFunction(f=>thirdReview.rendered===f,{timeout:30000},frame);
   const data=await page.evaluate(()=>thirdReview.stage.finalBuffer.toDataURL('image/png'));
   const name='scene'+String(i+1).padStart(2,'0')+'-part'+(k+1);
   fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data.split(',')[1],'base64'));images.push({name,data});
   console.log(name);
  }
  // Contact sheet is a rendered QA report, not an alteration to production assets.
  await page.setViewport({width:1440,height:1000,deviceScaleFactor:1});
  await page.setContent('<body style="margin:0;background:#ddd"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+images.map(x=>'<div><b>'+x.name+'</b><img width="480" src="'+x.data+'"></div>').join('')+'</div></body>');
  await page.screenshot({path:path.join(out,'contact-sheet.png'),fullPage:true});
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({timing,errors,screens:images.map(x=>x.name),publishReady:false},null,2));
  if(errors.length)throw Error(errors.join('\n'));
 }finally{await browser.close()}
}
main().catch(e=>{console.error(e);process.exitCode=1});
