// All newly added26-scene KO/EN lecture paragraphs and six input files were directly read.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),base=path.relative(root,__dirname).replaceAll('\\','/');
const rp='production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const save=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const old=read(rp);if(old.inputFiles.some(x=>hash(x.path)!==x.sha256))throw Error('Changed input must be reread before refresh');
const added=fs.readdirSync(path.join(root,'projects')).filter(s=>s!=='making-game-sequels'&&fs.existsSync(path.join(root,'projects',s,'project.json'))&&!old.existingProjects.some(x=>x.slug===s));
if(JSON.stringify(added)!==JSON.stringify(['game-math-rotation-interpolation']))throw Error('Unexpected new project; read content first');
const prefix='projects/game-math-rotation-interpolation/';
const expected={
 'project.json':'49cd36c68f13b0f96038dbf7c6e14e8a0bfc7713ccf4c23c8459fdf99cd7c740',
 'script/narration.ko.json':'efc35777dc1ac3fb6d245a0bfdedc1b9437a7ff53a56dab1c6fdc9a7eff4e57d',
 'script/narration.en.json':'8379d263667b7fb9d5b1fee51012308b605e2f49a18e8c33b593dcf30996d117',
 'planning/outline.md':'bf4e80be2d47d6752b14d0aea5a935e095dcb5947fd8f77c859c862feedf48f3',
 'sources/SOURCES.md':'fc13b82d52e84cec08ee2d691b6ed9eab0c6474ae6babdc423fa62e8448d5741',
 'README.md':'a0bf86e435e8ef1ee9310037bf27255acbb0d328451cfe646a8c6a9b3f738a94'};
for(const [p,h] of Object.entries(expected))if(hash(prefix+p)!==h)throw Error('New lecture changed after direct read: '+p);
const conclusion='All26 KO scenes/128 paragraphs and26 EN scenes/128 paragraphs, full manifest/outline/source/README were directly read. The question is intermediate3D orientation and rotation-representation conversion: q/-q signs, physical180 ties, SLERP/NLERP paths and speed, fixed endpoints/linear time, Hamilton wxyz right-handed local-to-world rules, Euler singular branches, stable matrix/quaternion extraction, zero-axis handling and round-trip vector tests. It does not teach sequel core activities versus new player decisions, production reuse or our separate OMD observation/retained-versus-changed writing. Its40:60/noBGM lecture permission remains separate. No foreign file, staging or worker was modified.';
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),previousDigest:old.inputsDigest,newInputs:Object.entries(expected).map(([p,h])=>({path:prefix+p,sha256:h,fullContentDirectlyRead:true})),koScenes:26,enScenes:26,koParagraphs:128,enParagraphs:128,conclusion,actualStudioEvidenceRetained:old.studioEvidence,otherUsersFilesModified:false};
save(base+'/final-input-interpolation-change-review-v1.json',record);
const content=read(base+'/content-review.json');content.updatedAt=record.reviewedAt;content.changedInputsDirectlyReviewed.push({review:base+'/final-input-interpolation-change-review-v1.json',files:Object.keys(expected).map(p=>prefix+p),conclusion});save(base+'/content-review.json',content);
for(const args of [['scripts/review-video-duplicates.cjs','making-game-sequels','--decision','distinct','--reason',old.contentReview+' Current full26KOEN interpolation lecture directly read: '+base+'/final-input-interpolation-change-review-v1.json','--studio-evidence',old.studioEvidence],['scripts/review-video-duplicates.cjs','making-game-sequels','--check']]){
 const r=cp.spawnSync(process.execPath,args,{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);console.log(r.stdout.trim());}
const current=read(rp);record.currentDigest=current.inputsDigest;record.existingProjects=current.existingProjects.length;record.currentDistinctPassed=true;save(base+'/final-input-interpolation-change-review-v1.json',record);
