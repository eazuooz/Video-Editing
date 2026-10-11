// Complete the collector's index-only tail after its shared-index write error.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),r=path.join(root,'projects/motion-sickness-games/production/revision-cross-game-four-v1');
const hash=async p=>{const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(p))h.update(b);return h.digest('hex');};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page=(title,content)=>`<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(title)}</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.7 'Malgun Gothic',sans-serif;color:#202020;background:white}a{color:#24569b}video{width:100%;background:#eee}section{margin:32px 0}small{color:#666}.notice{padding:16px;border-left:4px solid #bb8624;background:#fff8e9}</style><h1>${esc(title)}</h1>${content}</html>`;
(async()=>{
 const out=path.join(r,'current17-four-output-collection-verification-v1.json');if(fs.existsSync(out))throw Error('Already closed');
 const report=JSON.parse(fs.readFileSync(path.join(root,'projects/motion-sickness-games/production/delivery-output.json'),'utf8'));
 if(report.cueCounts.ko!==220||report.cueCounts.en!==220||report.videos.some(v=>v.duration!==853.1))throw Error('Stale delivery');
 for(const f of report.files)if(await hash(path.join(root,f.source))!==f.sha256||await hash(path.join(root,report.directory,f.name))!==f.sha256)throw Error('Delivery hash mismatch');
 const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
 const expected=JSON.stringify({schemaVersion:1,policy:'metadata-only-v1',projects:slugs.map(s=>({slug:s,manifest:`projects/${s}/rebuild.json`}))},null,2)+'\n';
 const indexPath=path.join(root,'projects/rebuild-index.json');const bytes=fs.readFileSync(indexPath);
 if(bytes.toString('utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n')!==expected)throw Error('Shared rebuild index differs; do not overwrite foreign state.');
 const check=spawnSync(process.execPath,['scripts/build-rebuild-manifests.cjs','motion-sickness-games','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(check.status!==0)throw Error(check.stderr);
 const outputRoot=path.join(root,'output');const dirs=fs.readdirSync(outputRoot,{withFileTypes:true}).filter(e=>e.isDirectory()&&!e.isSymbolicLink()&&fs.existsSync(path.join(outputRoot,e.name,'index.html')));
 fs.writeFileSync(path.join(outputRoot,'index.html'),page('영상 결과물 모음',`<p>프로젝트마다 자막 영상·무자막 영상·한글 SRT·영어 SRT를 모았습니다. 게시 전 확인 사항은 각 페이지에 표시됩니다.</p><ul>${dirs.map(e=>`<li><a href="${encodeURIComponent(e.name)}/index.html">${esc(e.name)}</a></li>`).join('')}</ul>`));
 const proof={verifiedAt:new Date().toISOString(),collector:{actualSession:46047,actualOuterExit:1,completion:'1e412b',failure:'UNKNOWN write projects/rebuild-index.json after four files, delivery report and own rebuild were saved'},recovery:{recollectedMedia:false,sharedRebuildIndexAlreadyCorrect:true,sharedRebuildIndexBytesPreserved:bytes.equals(fs.readFileSync(indexPath)),ownRebuildCheckExit:check.status,outputIndexTailSaved:true},files:report.files,fourOutputsCollected:true,humanListeningApproved:false,publicRightsApproved:false,newGitMedia:0};
 fs.writeFileSync(out,JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
 const cpPath=path.join(r,'latest-checkpoint.json');const cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));Object.assign(cp,{recordedAt:proof.verifiedAt,stage:'current17-four-outputs-verified-awaiting-single-private-upload',outputCollected:true,currentCollectionVerification:path.basename(out),next:'Single new reviewed captioned upload privately, then possible settings/CCoff/save-reopen/selectGit/current09slot. Baseline mBDd remains private and unchanged.'});fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
 console.log(JSON.stringify({files:4,shaMatched:true,ownRebuildCheck:0,sharedIndexUnchanged:true,collectorFailurePreserved:true}));
})().catch(e=>{console.error(e);process.exitCode=1;});
