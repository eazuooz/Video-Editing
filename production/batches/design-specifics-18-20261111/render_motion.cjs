const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {createRequire} = require('node:module');

const root = path.resolve(__dirname, '../../..');
const motionRequire = createRequire(path.join(root, 'motion-canvas/package.json'));
const puppeteer = motionRequire('puppeteer');
const renders = {
  DS01: {name: 'ds01-effect-comparison-review', frames: 480},
  DS02: {name: 'ds02-button-response-preview', frames: 1080},
  'DS02-controls': {name: 'ds02-control-studies-review', frames: 960, entry: 'controls'},
};

async function main() {
  const [episode, port = '9297'] = process.argv.slice(2);
  const render = renders[episode];
  if (!render) throw Error(`Unknown design-specifics diagram ${episode}`);
  const control = require(path.join(root, 'shared/publishing/video-production-control.json'));
  const [episodeId] = episode.split('-');
  if (!control.designSpecifics18Selected20261111.episodes.includes(episodeId)) {
    throw Error(`Episode outside selected playlist: ${episode}`);
  }
  const output = path.join(root, 'shared/output/motion-canvas', `${render.name}.mp4`);
  const browser = await puppeteer.launch({headless: true, protocolTimeout: 120000});
  try {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${port}/render-worker.html`, {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => typeof window.renderVideo === 'function');
    await page.evaluate(config => {
      window.renderVideo(config).catch(error => { window.renderFailure = String(error.stack ?? error); });
    }, {...render, route: `/src/projects/design-specifics/${episodeId}/${render.entry ?? 'sample'}.ts`, fps: 60, width: 1920,
      height: 1080, exactFrameRange: true});
    await page.waitForFunction(() => window.renderJob?.done || window.renderJob?.errors.length || window.renderFailure,
      {timeout: 900000, polling: 2000});
    const state = await page.evaluate(() => ({...window.renderJob, failure: window.renderFailure}));
    if (!state.done || state.result !== 0 || state.errors.length || state.failure) throw Error(JSON.stringify(state));
  } finally {
    await browser.close();
  }
  const probe = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries',
    'stream=width,height,avg_frame_rate,nb_frames', '-of', 'json', output], {encoding: 'utf8'});
  if (probe.status !== 0) throw Error(probe.stderr);
  const [video] = JSON.parse(probe.stdout).streams;
  if (video.width !== 1920 || video.height !== 1080 || video.avg_frame_rate !== '60/1'
      || Number(video.nb_frames) !== render.frames) throw Error(`Unexpected render: ${JSON.stringify(video)}`);
  console.log(output);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
