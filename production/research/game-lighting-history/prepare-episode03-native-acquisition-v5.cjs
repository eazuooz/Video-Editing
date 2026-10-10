const fs=require('node:fs'),path=require('node:path');
let src=fs.readFileSync(path.join(__dirname,'acquire-episode03-native-v4.cjs'),'utf8');
src=src.replace("local/episode03-native-v4'","local/episode03-native-v5'").replace("let completed=[],current=null;","let completed=[],failures=[],current=null;").replace("completed,current,finalUseApproved:false","completed,failures,current,finalUseApproved:false");
src=src.replace("['-X','utf8','-m','yt_dlp','--no-playlist'","['-X','utf8','-m','yt_dlp','--no-progress','--http-chunk-size','1M','--no-playlist'");
src=src.replace("for(const s of sources){const file=","for(const s of sources){try{const file=");
src=src.replace("boards:record.boards.length}));}","boards:record.boards.length}));}catch(e){failures.push({source:s.slug,error:e.message,observedAt:new Date().toISOString(),noAuthenticationOrAccessBypass:true});console.log(JSON.stringify(failures.at(-1)));current=null;write({status:'source-failed-continuing-independent-sources'});}} ");
src=src.replace("status:'native-and-samples-ready',completedAt","status:failures.length?'partial-native-and-samples-ready':'native-and-samples-ready',completedAt");
if(!src.includes('try{const file=')||!src.includes("--http-chunk-size"))throw Error('Scoped copy failed');
fs.writeFileSync(path.join(__dirname,'acquire-episode03-native-v5.cjs'),src);console.log('prepared7 independent public sources with standard1MiB HTTP chunks; prior failures retained');
