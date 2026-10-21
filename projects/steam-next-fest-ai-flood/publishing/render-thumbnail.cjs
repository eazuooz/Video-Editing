// Render publishing/thumbnail.html to a 1280x720 PNG with the project's puppeteer.
const path = require('node:path'); const fs = require('node:fs'); const crypto = require('node:crypto');
const R = path.resolve(__dirname, '../../..');
const puppeteer = require(path.join(R, 'motion-canvas/node_modules/puppeteer'));
(async () => {
  const browser = await puppeteer.launch({headless: true, args: ['--allow-file-access-from-files']});
  const page = await browser.newPage(); await page.setViewport({width: 1280, height: 720, deviceScaleFactor: 1});
  await page.goto('file:///' + path.join(__dirname, 'thumbnail.html').split(path.sep).join('/'), {waitUntil: 'networkidle0'});
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(__dirname, 'thumbnail.png'); await page.screenshot({path: out, type: 'png'}); await browser.close();
  const sha = crypto.createHash('sha256').update(fs.readFileSync(out)).digest('hex');
  fs.writeFileSync(path.join(__dirname, 'thumbnail-recipe.json'), JSON.stringify({createdAt: new Date().toISOString(), width: 1280, height: 720, sha256: sha, method: 'code-native channel layout (publishing/thumbnail.html): yellow strip, white ground, black/red headline, drawn star-field illustration, original cat logo; no video inset or slide screenshot', logo: 'shared/assets/branding/yamyamcoding-cats-original.png', visualReview: 'pending', uploaded: false}, null, 2) + '\n');
  console.log('thumbnail', sha);
})();
