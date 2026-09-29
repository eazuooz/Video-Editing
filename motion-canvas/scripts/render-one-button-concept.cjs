const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const revision=process.argv[2]||'v1';
if(!/^v\d+$/.test(revision))throw Error('Use a revision such as v1.');
const name=`one-button-concept-${revision}`,root=path.resolve(__dirname,'../..');
const dir=path.join(root,`projects/one-button-game-design/preview/${revision}`);
const source=path.join(root,`shared/output/motion-canvas/${name}.mp4`),output=path.join(dir,`${name}.mp4`);
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
(async()=>{
 if(fs.existsSync(output)||fs.existsSync(source))throw Error('Existing render preserved; use a new revision.');
 fs.mkdirSync(dir,{recursive:true});
 const browser=await puppeteer.launch({headless:true,protocolTimeout:240000});
 try{
  const page=await browser.newPage();
  page.on('pageerror',e=>console.error('PAGE',e.message));
  await page.goto('http://127.0.0.1:9210/render-worker.html');
  await page.waitForFunction(()=>typeof renderVideo==='function');
  await page.evaluate(name=>renderVideo({route:'/src/projects/one-button-game-design/preview/project.ts',name,frames:1440,fps:60,width:1920,height:1080,exactFrameRange:true}),name);
  const status=await page.evaluate(()=>renderJob);
  if(!status.done||status.result!==0||status.errors.length)throw Error(JSON.stringify(status));
 }finally{await browser.close();}
 const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',source]));
 const video=probe.streams.find(s=>s.codec_type==='video');
 if(+video.nb_frames!==1440||video.width!==1920||video.height!==1080||probe.streams.some(s=>s.codec_type==='audio'))throw Error('Unexpected preview specification');
 run('ffmpeg',['-v','error','-i',source,'-f','null','-']);
 fs.copyFileSync(source,output);
 for(let i=0;i<4;i++)run('ffmpeg',['-v','error','-n','-ss',String(i*6+3.5),'-i',source,'-frames:v','1',path.join(dir,`scene-${i+1}.png`)]);
 fs.writeFileSync(path.join(dir,'qa.json'),JSON.stringify({kind:'silent-original-2.5d-concept',scenes:4,frames:1440,seconds:24,width:1920,height:1080,fps:60,narration:false,bgm:false,externalFootage:false,membershipOutro:false,publishReady:false,fullDecodePassed:true,visualReview:'pending'},null,2));
 console.log(output);
})().catch(e=>{console.error(e);process.exitCode=1;});
