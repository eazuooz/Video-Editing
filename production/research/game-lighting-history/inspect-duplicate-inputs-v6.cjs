const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const previous=read('production/preflight/game-lighting-history-04.json');
const old=new Map(previous.inputFiles.map(f=>[f.path,f.sha256]));
const current=[];
for(const entry of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
  const base=`projects/${entry.name}`,mp=base+'/project.json';
  if(!entry.isDirectory()||entry.name==='game-lighting-history-04'||!fs.existsSync(path.join(root,mp)))continue;
  const m=read(mp);
  const files=new Set([mp,base+'/script/narration.ko.json',m.paths?.script,
    base+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,
    base+'/planning/outline.md',base+'/sources/SOURCES.md',base+'/README.md',
    base+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean));
  for(const p of files)if(fs.existsSync(path.join(root,p)))current.push({path:p,sha256:sha(p)});
}
const changes=current.filter(f=>old.get(f.path)!==f.sha256).map(f=>({...f,previousSha256:old.get(f.path)||null}));
const record={observedAt:new Date().toISOString(),baselineReviewedAt:previous.reviewedAt,currentInputs:current,
  changes,removed:[...old.keys()].filter(p=>!current.some(f=>f.path===p)),fullChangedContentsDirectlyRead:false};
const out=path.join(__dirname,'local/duplicate-input-change-snapshot-v6.json');
fs.writeFileSync(out,JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({baseline:previous.reviewedAt,currentFiles:current.length,
  changes:changes.map(f=>f.path),removed:record.removed},null,2));
