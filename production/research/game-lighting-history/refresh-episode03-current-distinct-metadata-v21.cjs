// Narrow refresh after a directly read foreign manifest change. Never auto-approve script changes.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const prefix='production/research/game-lighting-history/',slug='game-lighting-history-03';
const json=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const reportPath='production/preflight/'+slug+'.json',prior=json(reportPath);
const changed=prior.inputFiles.filter(x=>!fs.existsSync(x.path)||sha(fs.readFileSync(x.path))!==x.sha256);
const expected='projects/game-math-interpolation-paths-v2/project.json';
if(changed.length!==1||changed[0].path!==expected)throw Error('Unexpected input changes: read current full contents before refreshing');
const bytes=fs.readFileSync(expected),m=JSON.parse(bytes);
if(m.lecture.viewerQuestion!=='시작과 끝 자세 사이를 어떤 경로와 속도로 움직일까?'||m.paths.script!=='projects/game-math-interpolation-paths-v2/script/narration.ko.json')throw Error('Topic or active script changed');
const auditPath=prefix+'episode03-current-distinct-rereview-v21.json',audit=json(auditPath),at=new Date().toISOString();
audit.incrementalMetadataRefresh={reviewedAt:at,path:expected,priorSha256:changed[0].sha256,sha256:sha(bytes),method:'Current complete manifest literally read without truncation after the check rejected its changed digest. Every active KO/EN script, outline and receipt remains byte-identical to the preceding full review.',comparison:'The viewer question remains the path and speed between two orientations, with Hamilton wxyz, SLERP/NLERP and declared Euler conventions. The current local-render/private-upload-pending status, noBGM and40:60 exception do not change the lighting-history episode03 question or its60:40/Nimbus/black contract.',foreignFileModified:false};
fs.writeFileSync(auditPath,JSON.stringify(audit,null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs',slug,'--candidate-file',prefix+'candidate-03.json','--decision','distinct','--reason',prior.contentReview+'; directly read single current manifest refresh: '+auditPath,'--studio-evidence',prior.studioEvidence];
for(const a of [args,['scripts/review-video-duplicates.cjs',slug,'--candidate-file',prefix+'candidate-03.json','--check']]){const r=cp.spawnSync(process.execPath,a,{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);console.log(r.stdout.trim());}
const ownPath='projects/'+slug+'/project.json',own=json(ownPath);own.currentDuplicateReview={record:auditPath,sha256:sha(fs.readFileSync(auditPath)),preflight:reportPath,inputsDigest:json(reportPath).inputsDigest,checkedAt:at};
fs.writeFileSync(ownPath,JSON.stringify(own,null,2)+'\n');
