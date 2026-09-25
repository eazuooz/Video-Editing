const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..');
const out=path.join(root,'projects/renderformer-explained/production/layout-qa');
const overlays=require('../../projects/renderformer-explained/production/slide-overlays.json');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await puppeteer.launch({headless:true,protocolTimeout:240000});
 try{
  const page=await browser.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:9210/renderformer-layout.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.lectureReview?.ready,{timeout:120000});
  const runtime=await page.evaluate(()=>({frames:lectureReview.player.playback.duration,scenes:lectureReview.player.playback.scenes.current.length}));
  if(runtime.scenes!==88||runtime.frames!==26400)throw Error('Page coverage mismatch '+JSON.stringify(runtime));
  const sizes=await page.evaluate(data=>{
   const c=document.createElement('canvas').getContext('2d'),results=[];
   for(const [id,boxes] of Object.entries(data.pages))for(const [x,y,w,h,text,size] of boxes){
    c.font=`500 ${size}px 'Malgun Gothic'`;
    let lines=[];
    for(const paragraph of text.split('\n')){
     let line='';
     for(const char of paragraph){
      if(line&&c.measureText(line+char).width>w-14){lines.push(line);line='';}
      line+=char;
     }
     lines.push(line);
    }
    const needed=lines.length*size*1.5+14;
    results.push({id,x,y,w,h,fontSize:size,lines,needed,overflow:needed>h+1});
   }
   return results;
  },overlays);
  for(let i=0;i<88;i++){
   const frame=i*300+228;
   await page.evaluate(t=>lectureReview.jump(t),frame/60);
   await page.waitForFunction(f=>lectureReview.rendered===f,{timeout:30000},frame);
   const png=await page.evaluate(()=>lectureReview.stage.finalBuffer.toDataURL('image/png'));
   fs.writeFileSync(path.join(out,`page-${String(i+1).padStart(2,'0')}.png`),Buffer.from(png.split(',')[1],'base64'));
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({runtime,errors,sizes,overflowCount:sizes.filter(x=>x.overflow).length,humanVisualReview:false},null,2));
  console.log(JSON.stringify({runtime,errors,overflows:sizes.filter(x=>x.overflow)},null,2));
  if(errors.length||sizes.some(x=>x.overflow))process.exitCode=1;
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
