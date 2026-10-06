// Hash guards refer to the actual full texts read on 2026-10-06, not inferred updates.
const fs = require('node:fs'), cp = require('node:child_process'), crypto = require('node:crypto'), path = require('node:path');
const root = path.resolve(__dirname, '../../../..');
const base = path.relative(root, __dirname).replaceAll('\\', '/');
const report = 'production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const save = (p,d) => fs.writeFileSync(path.join(root,p), JSON.stringify(d,null,2)+'\n');
const reviewed = {
 'projects/game-math-euler-axis-angle/project.json':'e984d71b6a8a94170aec6827240c9f49eb127f496cfb392e1b8693495f5ce092',
 'projects/game-math-quaternion-operations/script/narration.ko.json':'f3c3303f11d84e5021f4ec9cfa3e6b5377018832d1332725a979f32ac83026c2',
 'projects/game-math-quaternion-operations/script/narration.en.json':'bf640daa3592076557bafce9ec26ca612559f5efec7caa40b1fe51633dd48e8d',
 'projects/game-math-rotation-interpolation/script/narration.ko.json':'000a54537e5154d971e9ef205416e430449f6bf3a5bdfae2ce1c181001bc23ac',
 'projects/game-math-rotation-interpolation/script/narration.en.json':'72619ce0fb3c3f720badd93bf9f74cffc81772102acd03617d89a881bb1ae74a'
};
const old=read(report), changed=old.inputFiles.filter(r=>!fs.existsSync(path.join(root,r.path))||hash(r.path)!==r.sha256);
if(changed.some(r=>!reviewed[r.path])) throw Error('Unreviewed changed input');
for(const [p,h] of Object.entries(reviewed)) if(hash(p)!==h) throw Error('Reviewed input changed again: '+p);
const projects=fs.readdirSync(path.join(root,'projects')).filter(s=>s!=='making-game-sequels'&&fs.existsSync(path.join(root,'projects',s,'project.json')));
if(projects.some(s=>!old.existingProjects.some(r=>r.slug===s))) throw Error('New project needs direct full review');
const conclusion='The current full Euler manifest and all26 scenes/all paragraphs in each current KO and EN quaternion-operations and rotation-interpolation script were directly read. Quaternion operations teaches unit norm, half-angle, q/-q, conjugate versus inverse, squared-norm inverse, Hamilton product, world/body delta and two-sided vector rotation. Its expanded scene20 distinguishes landing pose from position, separate excerpts from one jump, and relative rotation from rewinding collisions. Interpolation teaches sign-aligned delta=end*inverse(start), delta^t*start, SLERP/NLERP speed/time/sign conditions, conversions and boundary/round-trip tests; the expanded driving/flight passages preserve separate-excerpt and camera limitations. These full questions and chapter claims remain distinct from sequel retained core actions, production reuse and new player decisions. Euler timing now records1131.4167s and the explicitly authorized40:60/noBGM exception; this batch keeps60:40/continuousNimbus. Current Studio title-prefix filter 속 contains no video, while the previous complete inventory/related KOEN content reviews remain the substantive duplicate basis. Existing completed public/scheduled states were observed and preserved. No foreign file was modified or committed.';
const studio=old.studioEvidence+'; '+base+'/studio-sequel-current-title-filter.ax.txt';
const recordPath=base+'/current-math-script-rereview-v3.json';
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),previousDigest:old.inputsDigest,changedInputs:Object.entries(reviewed).map(([p,h])=>{const d=read(p); return {path:p,sha256:h,fullContentDirectlyRead:true,...(d.scenes?{scenes:d.scenes.length,paragraphs:d.scenes.reduce((n,s)=>n+s.lines.length,0)}:{kind:'full-manifest'})};}),conclusion,actualStudioEvidence:studio,foreignFilesModified:false,foreignFilesCommitted:false};
save(recordPath,record);
const content=read(base+'/content-review.json');content.updatedAt=record.reviewedAt;content.changedInputsDirectlyReviewed.push({review:recordPath,files:Object.keys(reviewed),conclusion});save(base+'/content-review.json',content);
for(const args of [['scripts/review-video-duplicates.cjs','making-game-sequels','--decision','distinct','--reason',old.contentReview+' Current full five changed inputs reviewed: '+recordPath,'--studio-evidence',studio],['scripts/review-video-duplicates.cjs','making-game-sequels','--check']]){const r=cp.spawnSync(process.execPath,args,{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);}
const current=read(report);Object.assign(record,{currentDigest:current.inputsDigest,existingProjects:current.existingProjects.length,currentDistinctPassed:true});save(recordPath,record);console.log(JSON.stringify({distinct:true,existingProjects:record.existingProjects,reviewedInputs:record.changedInputs}));
