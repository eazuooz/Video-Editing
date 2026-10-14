const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p),'utf8')).digest('hex');
const old=new Map(read('production/research/game-lighting-history/episode04-current-duplicate-rereview-v8.json').inputFiles.map(x=>[x.path,x.sha256])),currentFiles=[],projects=[];
for(const e of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 if(!e.isDirectory()||e.name==='game-lighting-history-04')continue;
 const base='projects/'+e.name,mp=base+'/project.json';if(!fs.existsSync(path.join(root,mp)))continue;
 const m=read(mp);projects.push(e.name);
 const files=[...new Set([mp,base+'/script/narration.ko.json',m.paths?.script,base+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,base+'/planning/outline.md',base+'/sources/SOURCES.md',base+'/README.md',base+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean))];
 for(const p of files)if(fs.existsSync(path.join(root,p)))currentFiles.push({path:p,sha256:sha(p)});
}
const current=new Map(currentFiles.map(x=>[x.path,x.sha256]));
const delta=currentFiles.filter(x=>old.get(x.path)!==x.sha256).map(x=>({...x,previous:old.get(x.path)||null}));const deleted=[...old.keys()].filter(p=>!current.has(p));
const out={observedAt:new Date().toISOString(),currentFiles,projects,delta,deleted};fs.writeFileSync(path.join(root,'production/research/game-lighting-history/local/episode04-input-delta-v9.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({projects:projects.length,inputs:currentFiles.length,delta,deleted},null,2));
