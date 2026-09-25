const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),port=process.argv[2]||'9210';
const output=path.join(root,'shared/output/motion-canvas/membership-outro-review.mp4');
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
(async()=>{if(fs.existsSync(output))throw Error('Existing review preserved.');
const browser=await puppeteer.launch({headless:true,protocolTimeout:180000});try{
const page=await browser.newPage();await page.goto(`http://127.0.0.1:${port}/render-worker.html`);
await page.waitForFunction(()=>typeof renderVideo==='function');
await page.evaluate(async()=>{await renderVideo({route:'/src/shared/membership/preview/project.ts',name:'membership-outro-review',frames:600,fps:60,width:1920,height:1080});});
const state=await page.evaluate(()=>renderJob);if(!state.done||state.result!==0||state.errors.length)throw Error(JSON.stringify(state));
const info=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]));
if(+info.streams[0].nb_frames!==600||Math.abs(+info.format.duration-10)>.03)throw Error('Not a 10-second outro');
run('ffmpeg',['-v','error','-n','-ss','4','-i',output,'-frames:v','1',output.replace('.mp4','.png')]);
run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
fs.writeFileSync(output.replace('.mp4','.json'),JSON.stringify({frames:600,duration:10,reviewOnly:true,fullDecodePassed:true,hasNarration:false,pendingMemberHandle:'@HyungJoonJung-c…'},null,2));
console.log(output);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
