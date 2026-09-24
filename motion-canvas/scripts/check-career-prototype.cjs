const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const out=path.resolve(__dirname,'../../projects/game-dev-career/production');
(async()=>{const browser=await puppeteer.launch({headless:true});try{
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080});await page.goto('http://127.0.0.1:9191/career-prototype.html');await page.waitForFunction(()=>window.chestTest);
 await page.keyboard.press('Space');let a=await page.evaluate(()=>chestTest.state);if(!a.opened||a.items.length!==1||a.keys!==0)throw Error('Interactive reward failed');
 await page.keyboard.press('Space');let b=await page.evaluate(()=>chestTest.state);if(b.items.length!==1)throw Error('Duplicate reward');
 await page.keyboard.press('KeyR');await page.keyboard.press('KeyK');await page.keyboard.press('Space');let c=await page.evaluate(()=>chestTest.state);if(c.opened||c.items.length)throw Error('Missing-key test failed');
 await page.keyboard.press('KeyR');await page.keyboard.press('KeyF');await page.keyboard.press('Space');let d=await page.evaluate(()=>chestTest.state);if(d.opened||d.keys!==1||d.items.length!==4)throw Error('Full-bag test failed');
 await page.screenshot({path:path.join(out,'prototype-browser-check.png')});fs.writeFileSync(path.join(out,'prototype-browser-tests.json'),JSON.stringify({reward:a,repeat:b,noKey:c,full:d,passed:true},null,2));console.log('Interactive browser tests passed.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
