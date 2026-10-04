// Source-rendering worker only; no Studio or browser UI automation.
const fs = require('node:fs'), path = require('node:path');
const puppeteer = require('../../../motion-canvas/node_modules/puppeteer');
const version=process.argv[2]||'v1';
if(!/^v\d+$/.test(version))throw Error('A numbered lookdev version is required.');
const work = path.join(__dirname, 'lookdev-'+version);
fs.mkdirSync(work, {recursive:true});
if (fs.existsSync(path.join(work, 'render-result.json'))) throw Error('Review existing render; do not duplicate it.');
(async () => {
 const browser = await puppeteer.launch({headless:true, args:['--disable-gpu'], protocolTimeout:600000});
 try {
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:9216/render-worker.html');
  await page.waitForFunction(() => typeof renderVideo === 'function');
  const pulse = setInterval(() => page.evaluate(() => renderJob?.frame)
   .then(frame => console.log('Silent lookdev frame '+frame+'/2880')).catch(()=>{}), 20000);
  try {
   await page.evaluate(version => renderVideo({route:'/src/projects/hierarchical-game-outlines/lookdev-project.ts',
    name:'hierarchical-game-outlines-lookdev-'+version, frames:2880, fps:60, width:1920, height:1080, exactFrameRange:true}), version);
  } finally {clearInterval(pulse);}
  const result = await page.evaluate(() => renderJob);
  fs.writeFileSync(path.join(work, 'render-result.json'), JSON.stringify({pid:process.pid,
   renderMode:'headless-source-renderer-disabled-gpu', silentLookdev:true, finalVideo:false, ...result}, null, 2)+'\n');
  if (!result.done || result.result !== 0 || result.errors.length) throw Error(JSON.stringify(result));
 } finally {await browser.close();}
})().catch(error => {console.error(error); process.exitCode=1;});
