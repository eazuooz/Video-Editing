// Render one frame from the middle of every diorama beat (plus each example window) for quick visual QA.
// Start the render server first. Usage: node scripts/render-play-first-stills.cjs [port] [t1,t2,...]
// With a comma-separated list of seconds, only those frames are rendered.
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const puppeteer = require('puppeteer');

const port = process.argv[2] || '9110';
const root = path.resolve(__dirname, '../..');
const board = JSON.parse(fs.readFileSync(path.join(root, 'motion-canvas/src/projects/play-first/storyboard.generated.json'), 'utf8'));
const qa = path.join(root, 'shared/output/play-first/qa/stills');
fs.mkdirSync(qa, {recursive: true});

// Sample times: middle of each gap between line starts outside the example window, and the example middle.
const times = [];
for (const s of board.scenes) {
  const marks = [0, ...s.lineStarts.slice(1), s.duration].filter(x => x < s.exampleStart || x >= s.exampleEnd);
  for (let i = 0; i < marks.length - 1; i++) {
    const a = marks[i], b = marks[i + 1];
    if (a < s.exampleStart && b > s.exampleStart) { if (s.exampleStart - a > 1.5) times.push(s.start + (a + s.exampleStart) / 2); continue; }
    if (b - a > 1.5) times.push(s.start + a + Math.min((b - a) * 0.7, 6));
  }
  times.push(s.start + s.exampleStart + 10);
}

if (process.argv[3]) times.splice(0, times.length, ...process.argv[3].split(',').map(Number));

async function main() {
  const host = `http://localhost:${port}`;
  const browser = await puppeteer.launch({headless: true, protocolTimeout: 180000});
  const page = await browser.newPage();
  await page.goto(`${host}/render-worker.html`, {waitUntil: 'domcontentloaded', timeout: 60000});
  await page.waitForFunction(() => typeof window.renderVideo === 'function');
  const stamp = Date.now();
  for (const [i, t] of times.entries()) {
    const name = `play-first-still-${stamp}-${String(i).padStart(2, '0')}`;
    await page.evaluate(config => {
      window.renderFailure = undefined;
      window.renderVideo(config).catch(error => window.renderFailure = String(error.stack ?? error));
    }, {route: '/src/projects/play-first/project.ts', name, frames: 2, fps: 60, width: 1920, height: 1080, firstFrame: Math.round(t * 60)});
    await page.waitForFunction(() => window.renderJob?.done || window.renderFailure, {timeout: 170000});
    const failure = await page.evaluate(() => window.renderFailure);
    if (failure) throw Error(failure);
    const video = path.join(root, 'shared/output/motion-canvas', `${name}.mp4`);
    const png = path.join(qa, `s${String(i).padStart(2, '0')}-${t.toFixed(1)}s.png`);
    spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', video, '-frames:v', '1', png]);
    fs.rmSync(video, {force: true});
    console.log(path.relative(root, png));
  }
  await browser.close();
}

main().catch(error => { console.error(error); process.exitCode = 1; });
