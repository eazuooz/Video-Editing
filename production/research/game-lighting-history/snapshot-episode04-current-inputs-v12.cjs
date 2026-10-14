const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=process.cwd(),base='production/research/game-lighting-history',old=JSON.parse(fs.readFileSync(base+'/local/episode04-input-delta-v11.json','utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const currentFiles=[],projects=[];
for(const entry of fs.readdirSync('projects',{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 if(!entry.isDirectory()||entry.name==='game-lighting-history-04')continue;
 const b='projects/'+entry.name,mp=b+'/project.json';if(!fs.existsSync(mp))continue;
 const m=JSON.parse(fs.readFileSync(mp,'utf8'));
 const files=[...new Set([mp,b+'/script/narration.ko.json',m.paths?.script,b+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,b+'/planning/outline.md',b+'/sources/SOURCES.md',b+'/README.md',b+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean))];
 for(const p of files)if(fs.existsSync(p))currentFiles.push({path:p,sha256:hash(p)});
 projects.push(entry.name);
}
const previous=new Map(old.currentFiles.map(x=>[x.path,x.sha256])),current=new Map(currentFiles.map(x=>[x.path,x.sha256]));
const delta=currentFiles.filter(x=>previous.get(x.path)!==x.sha256).map(x=>({...x,previousSha256:previous.get(x.path)||null}));
const deleted=old.currentFiles.filter(x=>!current.has(x.path));
const out=base+'/local/episode04-input-delta-v12.json';
if(fs.existsSync(out))throw Error('Preserve existing v12 snapshot');
fs.writeFileSync(out,JSON.stringify({observedAt:new Date().toISOString(),projects,currentFiles,delta,deleted},null,2)+'\n');
console.log(JSON.stringify({projects:projects.length,files:currentFiles.length,delta,deleted},null,2));
