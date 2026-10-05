// Whole changed orientation manifest was directly reread before this guarded refresh.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),base=path.relative(root,__dirname).replaceAll('\\','/');
const rp='production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const save=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const old=read(rp),changed=old.inputFiles.filter(x=>hash(x.path)!==x.sha256);
const expected='projects/game-math-orientation-matrices/project.json';
if(changed.length!==1||changed[0].path!==expected)throw Error('Unexpected input: read it before refresh '+JSON.stringify(changed));
const added=fs.readdirSync(path.join(root,'projects')).filter(s=>s!=='making-game-sequels'&&fs.existsSync(path.join(root,'projects',s,'project.json'))&&!old.existingProjects.some(x=>x.slug===s));
if(added.length)throw Error('New project requires whole content review: '+added);
const manifest=read(expected),conclusion='The entire updated orientation manifest now records a locally rendered902.4166667-second/54145-frame lecture with53425 body frames,21370 actual/32055 explanation, pending human listening/public rights and fixed caption output paths. Its question and all covered8.1–8.2.5 sections still concern right-handed column-vector axes, matrix columns, local/world transforms and inverse checks. The full previously read24KOEN scripts are unchanged. Render completion adds no sequel retained-activity/new-decision or production-reuse teaching. Its explicitly scoped40:60/noBGM permission remains separate from this batch60:40/Nimbus. No foreign files were changed or selected.';
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),previousDigest:old.inputsDigest,changedInputs:changed.map(x=>({...x,currentSha256:hash(x.path),fullContentDirectlyRead:true})),conclusion,actualStudioEvidenceRetained:old.studioEvidence,otherUsersFilesModified:false};
save(base+'/final-input-current-change-review-v1.json',record);
const content=read(base+'/content-review.json');content.updatedAt=record.reviewedAt;content.changedInputsDirectlyReviewed.push({review:base+'/final-input-current-change-review-v1.json',files:[expected],conclusion});save(base+'/content-review.json',content);
for(const args of [['scripts/review-video-duplicates.cjs','making-game-sequels','--decision','distinct','--reason',old.contentReview+' Current full orientation render manifest reread: '+base+'/final-input-current-change-review-v1.json','--studio-evidence',old.studioEvidence],['scripts/review-video-duplicates.cjs','making-game-sequels','--check']]){
const r=cp.spawnSync(process.execPath,args,{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);console.log(r.stdout.trim());}
const current=read(rp);record.currentDigest=current.inputsDigest;record.existingProjects=current.existingProjects.length;record.currentDistinctPassed=true;save(base+'/final-input-current-change-review-v1.json',record);
