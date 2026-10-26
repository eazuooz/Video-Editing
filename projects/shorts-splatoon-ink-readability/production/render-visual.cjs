// Finite InkReadability-only renderer. No server/job starts when this file is imported.
const fs = require('node:fs'), path = require('node:path'), cp = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const slug = 'shorts-splatoon-ink-readability', revision = 'ink-readability-v1';
const media = 'C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-splatoon-ink-readability';
const outputRoot = path.join(media, 'local/motion-canvas-output');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));

function guard() {
  // Reuse the exact Python finite-batch/revision/source/game checks, not a looser JS copy.
  const code = "import sys;sys.path.insert(0,sys.argv[1]);from audio_revision import guard,assert_no_game_apps,LEASE;guard();assert_no_game_apps();assert not LEASE.exists(),'Foreign GPU/costly lease preserved; defer render'";
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
  const pcm = path.join(__dirname,'local/audio-v2/voice/narration.wav');
  const pcmHash = crypto.createHash('sha256').update(fs.readFileSync(pcm)).digest('hex');
  const config = read(path.join(__dirname,'visual-config.json'));
  const configHash=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'visual-config.json'))).digest('hex');
  if(timing.timingInputs?.voiceSha256!==pcmHash||config.inputs?.voice?.sha256!==pcmHash||
      config.inputsReady!==true||config.game?.framesPrepared!==true||config.unity?.framesPrepared!==true)
    throw Error('Current PCM, real Unity readback and reviewed source/anchor inputs are required before render.');
  const assetPrefix='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/';
  const acceptance=read(path.join(__dirname,'local/unity-capture-acceptance-v2.json'));
  if(acceptance.revision!==revision||acceptance.nativePlaybackReviewed!==true||acceptance.unityAnchorsReviewed!==true||
      JSON.stringify(acceptance.inputs)!==JSON.stringify(config.inputs)) throw Error('Capture acceptance/current inputs differ.');
  for(const key of ['timing','voice','readback','captureJob','captureSuccess']) {
    const asset=config.inputs[key];
    if(!asset?.url?.startsWith(assetPrefix)||asset.url.includes('..')||/[?#]/.test(asset.url)||!/^[a-f0-9]{64}$/.test(asset.sha256||''))
      throw Error('Expected exact own-project asset and SHA256: '+key);
    const file=path.join(__dirname,asset.url.slice(assetPrefix.length));
    if(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')!==asset.sha256)
      throw Error('Changed current capture input: '+key);
  }
  const firstFrame=Number(firstArg), frames=countArg===undefined?timing.frames-firstFrame:Number(countArg);
  if (!Number.isInteger(firstFrame)||!Number.isInteger(frames)||firstFrame<0||frames<1||firstFrame+frames>timing.frames)
    throw Error('Requested frame range exceeds this exact current version.');
  const output=path.join(outputRoot,name+'.mp4'), receipt=path.join(__dirname,'local',name+'-render.json');
  if (fs.existsSync(output)||fs.existsSync(receipt)) throw Error('Preserve prior render/receipt; select a new version name.');
  const response=await fetch('http://127.0.0.1:9278/__yamyam_production_scope');
  if(!response.ok) throw Error('The isolated InkReadability Vite server is not available.');
  const scope=await response.json();
  if(scope.slug!==slug||scope.revision!==revision||scope.output!==outputRoot.replaceAll('\\','/'))
    throw Error('Port 9278 belongs to another production server; preserve it and stop.');
  guard();
  const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer'));
  const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
  try {
    const page=await browser.newPage();
    await page.goto('http://127.0.0.1:9278/render-worker.html');
    await page.waitForFunction(()=>typeof renderVideo==='function');
    const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f)).catch(()=>{}),15000);
    try {
      await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-splatoon-ink-readability/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});
    } finally {clearInterval(pulse);}
    const result=await page.evaluate(()=>window.renderJob);
    if(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'visual-config.json'))).digest('hex')!==configHash)
      throw Error('Config changed during rendering; preserve output without promoting it.');
    const record={...result,slug,revision,output,firstFrame,frames,fullCurrentTimeline:firstFrame===0&&frames===timing.frames,
      inputHashes:config.inputs,configSha256:configHash,
      outputSha256:fs.existsSync(output)?crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'):null};
    fs.writeFileSync(receipt,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
    if(!result.done||result.result!==0||result.errors.length||!fs.existsSync(output)) throw Error(JSON.stringify(record));
    console.log(JSON.stringify({output,receipt,firstFrame,frames}));
  } finally {await browser.close();}
}

if(require.main===module) main().catch(error=>{console.error(error);process.exitCode=1;});
