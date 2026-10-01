const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'shared/assets/praise-player/expanded-v2');fs.mkdirSync(out,{recursive:true});
const candidates=JSON.parse(fs.readFileSync(path.join(__dirname,'publisher-movie-candidates-v2.json'),'utf8')).records;
const selected=[{appid:1817230,id:257229003,key:'hifi-deep-dive'},{appid:1817230,id:257228983,key:'hifi-arcade'},{appid:1817230,id:257229428,key:'hifi-remix'},{appid:2395210,id:256971669,key:'thps-launch'}];
const records=[];for(const s of selected){const app=candidates.find(a=>a.appid===s.appid),m=app.movies.find(m=>m.id===s.id),file=path.join(out,s.key+'.mp4');
 if(fs.existsSync(file))throw Error('Preserve existing download; inspect before retry: '+file);
 console.log('Downloading '+app.name+' / '+m.name);
 const result=spawnSync('ffmpeg',['-v','warning','-i',m.hls_h264,'-map','0:v:0','-map','0:a:0?','-c','copy','-movflags','+faststart',file],{encoding:'utf8'});
 if(result.status!==0)throw Error(result.stderr);
 records.push({...s,game:app.name,title:m.name,storeSource:app.url,publisher:app.publishers,file:path.relative(root,file).replaceAll('\\','/'),url:m.hls_h264,sourceAudio:'Must be muted in expanded video',status:'awaiting-direct-visual-action-review'});
 console.log('Saved '+s.key);
 fs.writeFileSync(path.join(__dirname,'downloaded-publisher-footage-v2.json'),JSON.stringify({checkedAt:new Date().toISOString(),records},null,2)+'\n');
}
