// Rebuildable CPU-only proxies. Original FHD masters and prior versions stay intact.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'visual-config.json'),'utf8'));
const source=path.join(root,cfg.source),manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../sources/selected-footage.json'),'utf8'));
function run(bin,args){const r=spawnSync(bin,args,{encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-of','json',source]));
const video=probe.streams.find(s=>s.codec_type==='video');
if(video.width<1920||video.height<1080)throw Error('Native FHD source required; proxy is not source evidence.');
const log={source:cfg.source,recordedSourceSha256:manifest.sourceSha256,sourceDimensions:[video.width,video.height],reason:'Full-source aspect is preserved. Normal-width inserts use 1280 by 720 proxies; an enlarged crop explicitly requests full 1920 by 1080 frames. All originals are verified native FHD.',cuts:[]};
for(const [id,cut]of Object.entries(cfg.cuts)){
 const folder=path.join(__dirname,'local/game-frames',cut.frameDirectory??id),frames=Math.round(cut.maxDuration*60),w=cut.proxyWidth??1280,h=cut.proxyHeight??720;
 if(fs.existsSync(folder)){
  const count=fs.readdirSync(folder).filter(n=>/^\d{5}\.jpg$/.test(n)).length;
  if(count!==frames)throw Error('Preserve incomplete or unexpected folder and use a new frameDirectory: '+folder);
  log.cuts.push({id,folder,frames,proxyDimensions:[w,h],skippedExisting:true});continue;
 }
 fs.mkdirSync(folder,{recursive:true});
 const args=['-v','error','-n','-ss',String(cut.in),'-i',source,'-t',String(cut.maxDuration),'-an','-vf',`scale=${w}:${h}:force_original_aspect_ratio=decrease,pad=${w}:${h}:(ow-iw)/2:(oh-ih)/2,fps=60`,'-frames:v',String(frames),'-q:v','3','-start_number','0',path.join(folder,'%05d.jpg')];
 run('ffmpeg',args);log.cuts.push({id,folder,frames,proxyDimensions:[w,h],command:['ffmpeg',...args]});
}
fs.writeFileSync(path.join(__dirname,'local/media-preparation.json'),JSON.stringify(log,null,2)+'\n');
console.log(JSON.stringify(log));
