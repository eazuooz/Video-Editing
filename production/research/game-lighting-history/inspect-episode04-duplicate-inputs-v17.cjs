const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p),'utf8')).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const prior=read('production/preflight/game-lighting-history-04.json'),old=new Map(prior.inputFiles.map(f=>[f.path,f.sha256])),current=[];
for(const e of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 const b='projects/'+e.name,mp=b+'/project.json';if(!e.isDirectory()||e.name==='game-lighting-history-04'||!fs.existsSync(path.join(root,mp)))continue;
 const m=read(mp),files=new Set([mp,b+'/script/narration.ko.json',m.paths?.script,b+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,b+'/planning/outline.md',b+'/sources/SOURCES.md',b+'/README.md',b+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean));
 for(const p of files)if(fs.existsSync(path.join(root,p)))current.push({path:p,sha256:sha(p)});
}
const out='production/research/game-lighting-history/local/episode04-duplicate-input-change-snapshot-v17.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve existing snapshot');
const changes=current.filter(f=>old.get(f.path)!==f.sha256).map(f=>({...f,previousSha256:old.get(f.path)||null})),removed=[...old.keys()].filter(p=>!current.some(f=>f.path===p));
fs.writeFileSync(path.join(root,out),JSON.stringify({observedAt:new Date().toISOString(),baselineReviewedAt:prior.reviewedAt,currentInputs:current,changes,removed},null,2)+'\n');
console.log(JSON.stringify({files:current.length,changes,removed},null,2));
