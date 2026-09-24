// Own-project rendering QA only. This does not approve narration or media rights.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),port=process.argv.find(x=>/^\d{4,5}$/.test(x))||'9191';
const base=path.join(root,'projects/game-dev-career/production/qa-storyboard-v1');
async function main(){
  fs.mkdirSync(base,{recursive:true});
  const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  try{
    const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.setViewport({width:1440,height:1000});
    await page.goto(`http://127.0.0.1:${port}/career-storyboard.html?reel`,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.careerBoard?.ready||document.querySelector('#status').textContent.startsWith('로딩 실패'),{timeout:60000});
    const state=await page.evaluate(()=>window.careerBoard?{ready:careerBoard.ready,frames:careerBoard.player.playback.duration,scenes:careerBoard.scenes}:null);
    if(!state?.ready||state.frames!==3240||state.scenes.length!==9)throw Error('Storyboard failed: '+JSON.stringify(state));
    await page.evaluate(()=>document.fonts.ready);
    const shots=[];
    for(const s of state.scenes){
      for(const f of [.18,.51,.84]){
        const frame=Math.round((s.start+6*f)*60);
        await page.evaluate(t=>careerBoard.jump(t),frame/60);
        await page.waitForFunction(frame=>careerBoard.rendered===frame,{timeout:30000},frame);
        const image=await page.evaluate(()=>careerBoard.stage.finalBuffer.toDataURL('image/png'));
        const name=`scene${s.id}-${Math.round(f*100)}`;
        fs.writeFileSync(path.join(base,name+'.png'),Buffer.from(image.split(',')[1],'base64'));
        shots.push({name,image});
      }
    }
    await page.setContent('<body style="margin:0;background:white;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+shots.map(s=>`<div>${s.name}<img width="480" src="${s.image}"></div>`).join('')+'</div>');
    await page.screenshot({path:path.join(base,'contact.png'),fullPage:true});
    if(errors.length)throw Error(errors.join('\n'));
    fs.writeFileSync(path.join(base,'report.json'),JSON.stringify({kind:'silent-storyboard-not-narrated-video',scenes:9,shots:27,frames:state.frames,errors},null,2));
    console.log('PASS: 9 independent scenes, 27 views; silent visual storyboard only.');
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
