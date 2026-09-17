// Fetch only reviewed v2 sources. Raw recordings stay in ignored local caches.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),plan=require('../projects/visible-rewards/sources/gameplay-cuts.v2.json');
const python=path.join(root,'qwen3-tts/.venv/Scripts/python.exe');
const cmd=fs.existsSync(python)?python:'yt-dlp',prefix=fs.existsSync(python)?['-X','utf8','-m','yt_dlp']:[];
for(const [id,s] of Object.entries(plan.sources)){
 const file=path.join(root,s.file);
 if(fs.existsSync(file)){console.log('Preserved '+id);continue;}
 fs.mkdirSync(path.dirname(file),{recursive:true});
 const args=['--no-overwrites','--no-progress','--write-info-json','--merge-output-format','mp4','-f','bv[ext=mp4][vcodec^=avc1][height<=1080][protocol=https]+ba[ext=m4a]/b[ext=mp4]', '-o',file];
 if(s.sourceOffsetSeconds!==undefined)args.push('--download-sections',`*${s.sourceOffsetSeconds}-${s.sourceOffsetSeconds+195}`);
 args.push('https://www.youtube.com/watch?v='+id);
 const result=spawnSync(cmd,[...prefix,...args],{cwd:root,stdio:'inherit',windowsHide:true});
 if(result.status!==0)throw Error('Download failed; retained partial for retry: '+id);
 const meta=JSON.parse(fs.readFileSync(file.replace(/\.mp4$/,'.info.json'),'utf8'));
 if(s.license.startsWith('Creative Commons')&&!/Creative Commons Attribution/.test(meta.license??''))throw Error('License changed. Re-review before editing: '+id);
 console.log('Fetched '+id+'; inspect source/rights again before publishing a new revision.');
}
