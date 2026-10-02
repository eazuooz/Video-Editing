const fs=require('node:fs');const path=require('node:path');
const repo=path.resolve(__dirname,'..');
const root=path.join(repo,'output','youtube-library-refresh','v2');
const puppeteer=require(path.join(repo,'motion-canvas','node_modules','puppeteer'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'prompts.json'),'utf8'));
const items=manifest.items.filter(x=>fs.existsSync(path.join(root,'thumbnails',`${x.id}.jpg`)));
const contactRoot=path.join(root,'contacts');fs.mkdirSync(contactRoot,{recursive:true});
const e=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
(async()=>{
  const browser=await puppeteer.launch({headless:true});const page=await browser.newPage();
  await page.setViewport({width:1920,height:1250,deviceScaleFactor:1});
  for(let start=0;start<items.length;start+=12){
    const cards=items.slice(start,start+12).map(x=>`<article><img src="data:image/jpeg;base64,${fs.readFileSync(path.join(root,'thumbnails',`${x.id}.jpg`)).toString('base64')}"><p>${e(x.id)} · ${e(x.category)}</p></article>`).join('');
    await page.setContent(`<html><head><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;background:#18202f;padding:20px;font-family:'Malgun Gothic',sans-serif}.grid{display:grid;grid-template-columns:repeat(3,620px);gap:12px}article{margin:0;background:#fff;overflow:hidden;border-radius:8px}img{width:620px;height:349px;display:block}p{font-size:13px;margin:7px 10px;color:#242936}</style></head><body><div class="grid">${cards}</div></body></html>`,{waitUntil:'load'});
    await page.screenshot({path:path.join(contactRoot,`contact-${String(start/12+1).padStart(2,'0')}.png`),fullPage:true});
  }
  await browser.close();console.log(JSON.stringify({count:items.length,sheets:Math.ceil(items.length/12),contactRoot}));
})().catch(error=>{console.error(error);process.exitCode=1});
