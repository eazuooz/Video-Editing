// Two concurrent orientation scripts were read completely before this refresh.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),proof=path.relative(root,__dirname).replaceAll('\\','/');
const rp='production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const save=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const old=read(rp),changed=old.inputFiles.filter(x=>!fs.existsSync(path.join(root,x.path))||hash(x.path)!==x.sha256);
const expected=['projects/game-math-orientation-matrices/script/narration.ko.json','projects/game-math-orientation-matrices/script/narration.en.json'];
if(JSON.stringify(changed.map(x=>x.path).sort())!==JSON.stringify(expected.sort()))throw Error('Inspect new unexpected changes before refresh: '+JSON.stringify(changed));
const added=fs.readdirSync(path.join(root,'projects')).filter(s=>s!=='making-game-sequels'&&fs.existsSync(path.join(root,'projects',s,'project.json'))&&!old.existingProjects.some(x=>x.slug===s));
if(added.length)throw Error('Read newly added projects first: '+added);
const conclusion='The full24-scene KO/EN revision retains the direction/orientation question, three local/world axes, column-vector sign conventions, transpose inverse, rotation validity, reflection/scale, drift, storage, interpolation and two numerical exercises. Clarified Korean pronunciations of axes and equations do not introduce sequel production reuse or a retained-activity/new-player-decision lesson. Shared references to a body turning are different viewer questions and chapter claims. Its scoped40:60/noBGM exception remains separate.';
const d={schemaVersion:1,reviewedAt:new Date().toISOString(),previousInputDigest:old.inputsDigest,reason:'Current distinct check refused two changed concurrent orientation scripts before canonical60-paragraph adoption.',changedInputs:changed.map(x=>{const s=read(x.path);return {...x,currentSha256:hash(x.path),fullContentDirectlyRead:true,sceneCount:s.scenes.length,paragraphCount:s.scenes.reduce((n,x)=>n+x.lines.length,0),title:s.title};}),conclusion,otherUsersFilesModified:false,newImages:0,actualStudioEvidenceRetained:old.studioEvidence};
save(proof+'/guided-observation-current-input-change-review-v3.json',d);
const content=read(proof+'/content-review.json');content.updatedAt=d.reviewedAt;content.changedInputsDirectlyReviewed.push({review:proof+'/guided-observation-current-input-change-review-v3.json',files:d.changedInputs.map(x=>x.path),conclusion});save(proof+'/content-review.json',content);
let r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','making-game-sequels','--decision','distinct','--reason',old.contentReview+' Full changed24-scene KO/EN orientation scripts reread: '+proof+'/guided-observation-current-input-change-review-v3.json','--studio-evidence',old.studioEvidence],{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);
r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','making-game-sequels','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);
const current=read(rp);d.currentInputDigest=current.inputsDigest;d.currentProjectCount=current.existingProjects.length;d.currentDistinctCheckPassed=true;save(proof+'/guided-observation-current-input-change-review-v3.json',d);console.log(r.stdout.trim());
