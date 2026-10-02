const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas,loadImage}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
const root=path.resolve(__dirname,'../../..'),dest=path.join(__dirname,'official-source-review');fs.mkdirSync(dest,{recursive:true});
function run(bin,args){const r=spawnSync(bin,args,{encoding:'utf8',windowsHide:true,maxBuffer:3e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
(async()=>{for(const id of process.argv.slice(2)){
 const file=path.join(root,'shared/output/picking-sides/media-cache',id+'.mp4');
 const meta=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]));
 const duration=+meta.format.duration,step=Number(process.env.SOURCE_REVIEW_STEP)||(duration>300?12:4),start=Number(process.env.SOURCE_REVIEW_START)||0,end=Math.min(duration-.1,Number(process.env.SOURCE_REVIEW_END)||duration-.1),frames=[];
 for(let t=start;t<end;t+=step){const p=path.join(dest,`${id}-${t}.png`);if(!fs.existsSync(p))run('ffmpeg',['-v','error','-y','-threads','2','-ss',String(t),'-i',file,'-frames:v','1','-vf','scale=480:270',p]);frames.push({seconds:t,file:p});}
 const pages=[];
 for(let page=0;page<Math.ceil(frames.length/12);page++){const c=createCanvas(1920,920),x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,1920,920);
 for(let n=0;n<12;n++){const item=frames[page*12+n];if(!item)break;const left=n%4*480,top=Math.floor(n/4)*306;x.drawImage(await loadImage(item.file),left,top+32);x.fillStyle='black';x.font='20px sans-serif';x.fillText(`${id} / ${item.seconds}s`,left+8,top+25);}
 const p=path.join(dest,`${id}-${start}-${end}-${step}-contact-${page+1}.png`);fs.writeFileSync(p,c.toBuffer('image/png'));pages.push(path.relative(root,p).replaceAll('\\','/'));}
 fs.writeFileSync(path.join(dest,`${id}-${start}-${end}-${step}.json`),JSON.stringify({id,duration,step,source:path.relative(root,file).replaceAll('\\','/'),pages,frameTimes:frames.map(x=>x.seconds),review:'pending-direct-review',finalCutSelection:'pending'},null,2)+'\n');console.log(JSON.stringify({id,duration,pages}));
}})().catch(e=>{console.error(e);process.exitCode=1;});
