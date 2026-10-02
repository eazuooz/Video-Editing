const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const W=__dirname,R=path.resolve(W,'../../../..'),python=path.join(R,'qwen3-tts/.venv/Scripts/python.exe');
for(const f of ['verify-mix-alignment.py','verify-video.py','make-caption-strips.py','verify-retention.py']){
 const r=spawnSync(python,[path.join(W,f)],{cwd:R,encoding:'utf8',windowsHide:true,maxBuffer:8e6});
 fs.writeFileSync(path.join(W,f.replace('.py','.log')),r.stdout+'\n'+r.stderr);
 if(r.status!==0)throw Error(r.stderr||String(r.error));console.log(f,r.stdout.trim());
}
