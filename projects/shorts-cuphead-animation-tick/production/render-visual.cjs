// Finite Cuphead-only renderer. No server/job starts when this file is imported.
const fs = require('node:fs'), path = require('node:path'), cp = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const slug = 'shorts-cuphead-animation-tick', revision = 'animation-tick-v1';
const media = 'C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-cuphead-animation-tick';
const outputRoot = path.join(media, 'local/motion-canvas-output');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));

function guard() {
  // Reuse the exact Python daily/date/revision/source/game checks, not a looser JS copy.
  const code = "import sys;sys.path.insert(0,sys.argv[1]);from audio_revision import guard,assert_no_game_apps;guard();assert_no_game_apps()";
  cp.execFileSync(path.join(root, 'qwen3-tts/.venv/Scripts/python.exe'), ['-B', '-X', 'utf8', '-c', code, __dirname],
    {cwd:root, stdio:'pipe', windowsHide:true, env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
}

async function main() {
  guard();
  const [name, firstArg='0', countArg] = process.argv.slice(2);
  if (!/^[a-z0-9][a-z0-9-]{1,120}$/.test(name||'')) throw Error('Use a safe unique render name.');
  const timing = read(path.join(__dirname, 'visual-timing.json'));
  const localTiming = read(path.join(__dirname, 'local/visual-timing.json'));
  if (JSON.stringify(timing)!==JSON.stringify(localTiming) || timing.revision!==revision || timing.previewOnly!==false || timing.fps!==60)
    throw Error('Use the same actual final-PCM timing for this project and mixer.');
  const firstFrame=Number(firstArg), frames=countArg===undefined?timing.frames-firstFrame:Number(countArg);
  if (!Number.isInteger(firstFrame)||!Number.isInteger(frames)||firstFrame<0||frames<1||firstFrame+frames>timing.frames)
    throw Error('Requested frame range exceeds this exact current version.');
  const output=path.join(outputRoot,name+'.mp4'), receipt=path.join(__dirname,'local',name+'-render.json');
  if (fs.existsSync(output)||fs.existsSync(receipt)) throw Error('Preserve prior render/receipt; select a new version name.');
  const response=await fetch('http://127.0.0.1:9275/__yamyam_production_scope');
  if(!response.ok) throw Error('The isolated Cuphead Vite server is not available.');
  const scope=await response.json();
  if(scope.slug!==slug||scope.revision!==revision||scope.output!==outputRoot.replaceAll('\\','/'))
    throw Error('Port 9275 belongs to another production server; preserve it and stop.');
  guard();
  const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer'));
  const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
  try {
    const page=await browser.newPage();
    await page.goto('http://127.0.0.1:9275/render-worker.html');
    await page.waitForFunction(()=>typeof renderVideo==='function');
    const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f)).catch(()=>{}),15000);
    try {
      await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-cuphead-animation-tick/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});
    } finally {clearInterval(pulse);}
    const result=await page.evaluate(()=>window.renderJob);
    const record={...result,slug,revision,output,firstFrame,frames,fullCurrentTimeline:firstFrame===0&&frames===timing.frames};
    fs.writeFileSync(receipt,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
    if(!result.done||result.result!==0||result.errors.length||!fs.existsSync(output)) throw Error(JSON.stringify(record));
    console.log(JSON.stringify({output,receipt,firstFrame,frames}));
  } finally {await browser.close();}
}

if(require.main===module) main().catch(error=>{console.error(error);process.exitCode=1;});
