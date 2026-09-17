// Download only sources with recorded reuse permission; originals stay in ignored cache.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),plan=require('../projects/visible-rewards/sources/gameplay-cuts.json');
for(const id of Object.keys(plan.sources)){
 const stem=`shared/output/visible-rewards/media-cache/${id}`;
 if(fs.existsSync(path.join(root,stem+'.mp4')))continue;
 const limit=id==='2_qxMaIZUds'?720:1080;
 const r=spawnSync(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-m','yt_dlp','--no-progress','--js-runtimes','node','-f',`bv*[height<=${limit}]+ba/b[height<=${limit}]`,'--merge-output-format','mp4','--write-info-json','-o',stem+'.%(ext)s','https://www.youtube.com/watch?v='+id],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:8e6});
 if(r.status!==0)throw Error(r.stderr);console.log('Downloaded '+id);
}
