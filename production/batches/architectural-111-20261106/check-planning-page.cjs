const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer-core'));
const media='C:/Users/1/Videos/YamyamProduction/architectural-111-20261106';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--disable-gpu','--no-first-run']});
 try {
  const page=await browser.newPage();await page.setViewport({width:375,height:1000});
  await page.goto('file:///'+media+'/delivery/index.html',{waitUntil:'domcontentloaded'});
  const initial=await page.evaluate(()=>({count:document.querySelectorAll('article').length,visible:[...document.querySelectorAll('article')].filter(x=>!x.hidden).length,overflow:document.documentElement.scrollWidth>innerWidth,emptyPlayers:document.querySelectorAll('video:not([src])').length}));
  if(initial.count!==111||initial.visible!==111||initial.overflow||initial.emptyPlayers)throw Error(JSON.stringify(initial));
  await page.type('#q','수레');
  const search=await page.evaluate(()=>({visible:[...document.querySelectorAll('article')].filter(x=>!x.hidden).length,first:[...document.querySelectorAll('article')].find(x=>!x.hidden)?.querySelector('h2').textContent}));
  if(!search.visible||!search.first.includes('수레'))throw Error('Search failed');
  await page.$eval('#q',e=>{e.value='';e.dispatchEvent(new Event('input'))});
  await page.click('details summary');
  const expanded=await page.evaluate(()=>({open:document.querySelector('details').open,overflow:document.documentElement.scrollWidth>innerWidth,paragraphs:document.querySelector('details').querySelectorAll('p').length}));
  if(!expanded.open||expanded.overflow)throw Error(JSON.stringify(expanded));
  await page.screenshot({path:path.join(media,'delivery/planning-mobile.png')});
  await page.setViewport({width:1280,height:900});await page.screenshot({path:path.join(media,'delivery/planning-desktop.png')});
  const report={initial,search,expanded,viewportWidths:[375,1280],scope:'Authored planning page count/search/expansion/overflow; not video playback, audio, final-film or human review'};
  fs.writeFileSync(path.join(__dirname,'planning-page-qa.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
