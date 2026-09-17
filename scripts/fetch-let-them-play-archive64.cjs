// Download only approved source windows. Proxies and prior sources are preserved.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const windows=[['p1','tOvTBrO7bPo',135,160],['p1','tOvTBrO7bPo',254,278],['p1','tOvTBrO7bPo',281,365],['p1','tOvTBrO7bPo',475,515],['p1','tOvTBrO7bPo',1484,1516],['p1','tOvTBrO7bPo',1764,1788],['p1','tOvTBrO7bPo',1845,1870],['p2','kjSH8R2fk2c',205,246],['p2','kjSH8R2fk2c',2752,2780]];
windows.push(['p2','kjSH8R2fk2c',3503,3535]);
windows.push(['p1','tOvTBrO7bPo',708,733]);
for(const [part,id,start,end] of windows){
 const output=`shared/output/let-them-play/media-cache/archive64-${part}-${start}.mp4`;
 if(fs.existsSync(path.join(root,output))){console.log('Cached '+output);continue;}
 const r=spawnSync(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-m','yt_dlp','--no-progress','--js-runtimes','node','-f','299+140','--download-sections',`*${start}-${end}`,'--merge-output-format','mp4','-o',output,`https://www.youtube.com/watch?v=${id}`],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:32*1024*1024});
 if(r.status!==0)throw Error((r.stderr||r.stdout).slice(-3000));
 console.log('Downloaded '+part+' '+start+'-'+end);
}
