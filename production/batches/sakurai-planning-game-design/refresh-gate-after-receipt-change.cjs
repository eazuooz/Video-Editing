// Refresh only the directly reread, unrelated math lecture receipt. No Studio edits.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design';
const read=f=>fs.readFileSync(path.join(root,f),'utf8'),hash=f=>crypto.createHash('sha256').update(read(f)).digest('hex');
const reportPath=base+'/preflight/avoid-game-comparisons.json',reviewPath=base+'/proof-avoid-game-comparisons/content-review.json';
const report=JSON.parse(read(reportPath)),review=JSON.parse(read(reviewPath));
for(const s of review.relatedFullScriptsRead)if(hash(s.path)!==s.sha256)throw Error('Reviewed script changed: '+s.path);
const changed=report.inputFiles.filter(f=>!fs.existsSync(path.join(root,f.path))||hash(f.path)!==f.sha256);
const allowed='projects/game-math-polar-2d/publishing/youtube-upload.json';
if(changed.some(f=>f.path!==allowed))throw Error('Another input changed; directly review it before refreshing.');
const receipt=JSON.parse(read(allowed));
if(receipt.videoId!=='PcxaKEvbzjg'||!receipt.metadata.title.includes('극좌표계'))throw Error('Unexpected math lecture identity.');
if(changed.length){
  review.historicalInputRefreshes=[...(review.historicalInputRefreshes||[]),review.inputRefresh].filter(Boolean);
  review.inputRefresh={observedAt:new Date().toISOString(),reason:'Directly reread the entire concurrent polar-coordinate receipt after its private settings and Git delivery were updated. Its distance/angle/coordinate conversion/rotation/aiming/vector chapters remain unrelated to new-game pitch communication. All eight compared full scripts and the existing actual Studio evidence are unchanged. The concurrent project and its settings are preserved.',changedMetadata:changed.map(f=>({path:f.path,previousSha256:f.sha256,sha256:hash(f.path)})),currentReceiptVideoId:receipt.videoId,concurrentFilesModified:false};
  fs.writeFileSync(path.join(root,reviewPath),JSON.stringify(review,null,2)+'\n');
  const run=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--decision','distinct','--reason',review.decisionReason,'--studio-evidence',report.studioEvidence],{cwd:root,encoding:'utf8'});
  process.stdout.write(run.stdout||'');process.stderr.write(run.stderr||'');if(run.status!==0)process.exit(run.status||1);
}
const run=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],{cwd:root,encoding:'utf8'});
process.stdout.write(run.stdout||'');process.stderr.write(run.stderr||'');process.exitCode=run.status||0;
