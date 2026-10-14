const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const out='production/research/game-lighting-history/local/episode04-duplicate-input-change-snapshot-v15.json';
if(fs.existsSync(out))throw Error('Preserve existing snapshot');
const old=new Map(read('production/research/game-lighting-history/episode04-current-duplicate-rereview-v14.json').inputFiles.map(x=>[x.path,x.sha256]));
const currentInputs=[],projects=[];
for(const e of fs.readdirSync('projects',{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 if(!e.isDirectory()||e.name==='game-lighting-history-04')continue;
 const base='projects/'+e.name,mp=base+'/project.json';if(!fs.existsSync(mp))continue;
 const m=read(mp);projects.push(e.name);
 const files=[...new Set([mp,base+'/script/narration.ko.json',m.paths?.script,base+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,base+'/planning/outline.md',base+'/sources/SOURCES.md',base+'/README.md',base+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean))];
 for(const p of files)if(fs.existsSync(p))currentInputs.push({path:p,sha256:sha(p)});
}
const current=new Map(currentInputs.map(x=>[x.path,x.sha256]));
const changes=currentInputs.filter(x=>old.get(x.path)!==x.sha256).map(x=>({...x,previous:old.get(x.path)||null}));
const removed=[...old.keys()].filter(p=>!current.has(p));
const result={observedAt:new Date().toISOString(),currentInputs,projects,changes,removed};
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({out,inputs:currentInputs.length,projects:projects.length,changes,removed},null,2));
