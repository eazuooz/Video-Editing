const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const report=JSON.parse(fs.readFileSync(path.join(root,'production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json'),'utf8'));
const old=new Map(report.inputFiles.map(f=>[f.path,f.sha256])),current=[];
for(const entry of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 if(!entry.isDirectory()||entry.name==='familiar-game-rules')continue;
 const base=`projects/${entry.name}`,mp=`${base}/project.json`;if(!fs.existsSync(path.join(root,mp)))continue;
 const m=JSON.parse(fs.readFileSync(path.join(root,mp),'utf8'));
 const files=[...new Set([mp,`${base}/script/narration.ko.json`,m.paths?.script,`${base}/script/narration.en.json`,m.paths?.scriptEn,`${base}/planning/outline.md`,`${base}/sources/SOURCES.md`,`${base}/README.md`,`${base}/publishing/youtube-upload.json`,m.publishing?.receipt].filter(Boolean))];
 for(const p of files)if(fs.existsSync(path.join(root,p)))current.push({path:p,sha256:hash(fs.readFileSync(path.join(root,p),'utf8'))});
}
const changed=current.filter(f=>old.get(f.path)!==f.sha256).map(f=>({...f,previousSha256:old.get(f.path)||null}));
const removed=report.inputFiles.filter(f=>!current.some(c=>c.path===f.path));
const result={observedAt:new Date().toISOString(),previousReviewedAt:report.reviewedAt,previousDigest:report.inputsDigest,previousReason:report.contentReview,previousStudioEvidence:report.studioEvidence,changed,removed,currentFileCount:current.length};
fs.writeFileSync(path.join(__dirname,'current-input-change-list-v1.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
