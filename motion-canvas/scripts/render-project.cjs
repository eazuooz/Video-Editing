// Render any manifest-backed Motion Canvas project through the editor's FFmpeg exporter.
// Usage: node scripts/render-project.cjs <project-slug> [port]

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const slug = process.argv[2];
const port = process.argv[3] || '9100';
if (!slug) {
  console.error('Usage: node scripts/render-project.cjs <project-slug> [port]');
  process.exit(1);
}

const repoRoot = path.resolve(__dirname, '../..');
const manifestPath = path.join(repoRoot, 'projects', slug, 'project.json');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
if (manifest.slug !== slug) throw new Error('Manifest slug mismatch');

const motionRoot = path.join(repoRoot, 'motion-canvas');
const projectFile = path.resolve(repoRoot, manifest.paths.motionCanvasProject);
const projectRoute = '/' + path.relative(motionRoot, projectFile).replaceAll('\\', '/').replace(/\.ts$/, '');
const url = `http://localhost:${port}${projectRoute}`;
const output = path.resolve(repoRoot, manifest.paths.videoClean);
const allowedOutput = path.join(repoRoot, 'shared', 'output', 'motion-canvas') + path.sep;
if (!output.startsWith(allowedOutput)) throw new Error(`Output is outside the render directory: ${output}`);

const stableChecksRequired = 6;
const pollMs = 5000;
const timeoutMs = 45 * 60 * 1000;

async function main() {
  console.log(`checking dev server at ${url} ...`);
  await fetch(`http://localhost:${port}/`);

  if (fs.existsSync(output)) {
    console.log(`Removing stale output: ${output}`);
    fs.unlinkSync(output);
  }

  const browser = await puppeteer.launch({
    headless: false,
    args: ['--window-size=1600,1000'],
  });
  const page = await browser.newPage();
  await page.setViewport({width: 1600, height: 1000});
  page.on('pageerror', error => console.log('[pageerror]', error.message));
  // Vite keeps its HMR websocket open, so `networkidle0` may never resolve.
  // The editor's Render button is the reliable readiness signal below.
  await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 120000});

  await page.waitForFunction(
    () => Array.from(document.querySelectorAll('button')).some(button =>
      (button.textContent || '').toUpperCase().includes('RENDER'),
    ),
    {timeout: 30000},
  );
  await page.evaluate(() => {
    const button = Array.from(document.querySelectorAll('button')).find(candidate =>
      (candidate.textContent || '').toUpperCase().includes('RENDER'),
    );
    button.click();
  });

  const startedAt = Date.now();
  let stable = 0;
  let lastSize = -1;
  while (true) {
    await new Promise(resolve => setTimeout(resolve, pollMs));
    const elapsed = Math.round((Date.now() - startedAt) / 1000);
    const size = fs.existsSync(output) ? fs.statSync(output).size : -1;
    stable = size > 0 && size === lastSize ? stable + 1 : 0;
    lastSize = size;
    console.log(`[${elapsed}s] size=${size} stable=${stable}/${stableChecksRequired}`);
    if (stable >= stableChecksRequired) break;
    if (Date.now() - startedAt > timeoutMs) throw new Error('Render timed out');
  }

  await browser.close();
  console.log(`DONE: ${output} (${lastSize} bytes)`);
}

main().catch(error => {
  console.error('FATAL', error);
  process.exit(1);
});
