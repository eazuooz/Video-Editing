const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons';
const p=path.join(root,proof+'/content-review.json'),r=JSON.parse(fs.readFileSync(p,'utf8'));
for(const s of r.relatedFullScriptsRead){if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,s.path))).digest('hex')!==s.sha256)throw Error('Reviewed script changed: '+s.path);}
r.inputRefresh={observedAt:new Date().toISOString(),reason:'Both private thumbnail receipts now record actual saved/reopened completion. The concurrent polar2D receipt was directly reread after its upload ID/status changed: distance/angles/conversion/aiming chapters differ from new-game pitch communication. No concurrent file is edited or committed. The eight full compared scripts, source concepts and actual Studio evidence are unchanged.',changedMetadata:['hierarchical-game-outlines','game-reward-planning','game-math-polar-2d'].map(slug=>{const p='projects/'+slug+'/publishing/youtube-upload.json';return {path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')};})};
fs.writeFileSync(p,JSON.stringify(r,null,2)+'\n');
const old=JSON.parse(fs.readFileSync(path.join(root,base+'/preflight/avoid-game-comparisons.json'),'utf8'));
for(const args of [['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--decision','distinct','--reason',r.decisionReason,'--studio-evidence',old.studioEvidence],['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']]){
 const run=cp.spawnSync(process.execPath,args,{cwd:root,encoding:'utf8'});process.stdout.write(run.stdout||'');process.stderr.write(run.stderr||'');if(run.status!==0)process.exit(run.status||1);
}
