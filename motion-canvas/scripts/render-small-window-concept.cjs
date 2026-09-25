const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const revision=process.argv[2]||'v2';if(!/^v\d+$/.test(revision))throw Error('Use a revision such as v2.');
const name=`small-window-concept-${revision}`;
const root=path.resolve(__dirname,'../..'),dir=path.join(root,`projects/small-window-game-design/preview/${revision}`);fs.mkdirSync(dir,{recursive:true});
const source=path.join(root,`shared/output/motion-canvas/${name}.mp4`);
const output=path.join(dir,`${name}.mp4`);
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
(async()=>{
 if(fs.existsSync(output)||fs.existsSync(source))throw Error('Existing concept preserved; use a new revision.');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:240000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');
 await page.waitForFunction(()=>typeof renderVideo==='function');
 await page.evaluate(name=>renderVideo({route:'/src/projects/small-window-game-design/project.ts',name,frames:2160,fps:60,width:1920,height:1080,exactFrameRange:true}),name);
 const s=await page.evaluate(()=>renderJob);if(!s.done||s.result!==0||s.errors.length)throw Error(JSON.stringify(s));
 }finally{await browser.close();}
 const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',source]));
 if(+probe.streams[0].nb_frames!==2160)throw Error('Frame mismatch');
 run('ffmpeg',['-v','error','-i',source,'-f','null','-']);fs.copyFileSync(source,output);
 for(let i=0;i<6;i++)run('ffmpeg',['-v','error','-n','-ss',String(i*6+3),'-i',source,'-frames:v','1',path.join(dir,`scene-${i+1}.png`)]);
 fs.writeFileSync(path.join(dir,'qa.json'),JSON.stringify({kind:'silent-original-2.5d-concept',scenes:6,frames:2160,seconds:36,narration:false,bgm:false,externalFootage:false,membershipOutro:false,publishReady:false,fullDecodePassed:true},null,2));
 console.log(output);
})().catch(e=>{console.error(e);process.exitCode=1;});
