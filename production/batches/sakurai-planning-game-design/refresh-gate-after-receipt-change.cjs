// Refresh only the directly reread, unrelated math lecture metadata. No Studio edits.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design';
const read=f=>fs.readFileSync(path.join(root,f),'utf8'),hash=f=>crypto.createHash('sha256').update(read(f)).digest('hex');
const reportPath=base+'/preflight/avoid-game-comparisons.json',reviewPath=base+'/proof-avoid-game-comparisons/content-review.json';
const report=JSON.parse(read(reportPath)),review=JSON.parse(read(reviewPath));
for(const s of review.relatedFullScriptsRead)if(hash(s.path)!==s.sha256)throw Error('Reviewed script changed: '+s.path);
const changed=report.inputFiles.filter(f=>!fs.existsSync(path.join(root,f.path))||hash(f.path)!==f.sha256);
const allowed=['projects/game-math-polar-2d/publishing/youtube-upload.json','projects/game-math-polar-3d/project.json','projects/game-math-polar-3d/publishing/youtube-upload.json'];
const reviewedHashes={
  'projects/game-math-polar-2d/publishing/youtube-upload.json':'4d2740e581254db0bd9c2c004cc3ea1f8030f92a74822a3019da8bdd6ef55dd3',
  'projects/game-math-polar-3d/project.json':'c7c52d53b820e6f533afde77d389482eb692d24a5766fdc209a8f49cb089286c',
  'projects/game-math-polar-3d/publishing/youtube-upload.json':'c959e51ef8d0ac8e604b44134b9918d1c9644323dd73e37a6a0e2563e554c22e'
};
if(changed.some(f=>!allowed.includes(f.path)||hash(f.path)!==reviewedHashes[f.path]))throw Error('Another/unread metadata change; directly review it before refreshing.');
const receipt=JSON.parse(read(allowed[0]));
const lecture3d=JSON.parse(read(allowed[1]));
const receipt3d=JSON.parse(read(allowed[2]));
if(receipt.videoId!=='PcxaKEvbzjg'||!receipt.metadata.title.includes('극좌표계'))throw Error('Unexpected math lecture identity.');
if(lecture3d.slug!=='game-math-polar-3d'||!lecture3d.titles.ko.includes('원통·구면좌표'))throw Error('Unexpected3D lecture identity.');
if(receipt3d.videoId!=='ZLOewk8JHXA'||!receipt3d.metadata.title.includes('원통·구면좌표'))throw Error('Unexpected3D upload identity.');
if(changed.length){
  review.historicalInputRefreshes=[...(review.historicalInputRefreshes||[]),review.inputRefresh].filter(Boolean);
  review.inputRefresh={observedAt:new Date().toISOString(),reason:'Directly reread both entire concurrent polar-coordinate upload receipts and the3D lecture manifest. Latest receipt changes add the two companion links and platform/Git observations, including the3D upload still processing; they do not introduce a new viewer question or substantive chapter. The2D distance/angle/conversion/aiming/vector chapters and3D cylindrical/spherical conversion/camera/boundary chapters remain unrelated to communicating an unbuilt game idea without relying on different familiar-title images. All eight compared full scripts and actual saved Studio evidence are unchanged. Preserve the concurrent project-specific40:60/no-BGM lecture exception; it does not change this batch60:40/Nimbus policy.',changedMetadata:changed.map(f=>({path:f.path,previousSha256:f.sha256,sha256:hash(f.path)})),currentReceiptVideoId:receipt.videoId,current3dReceiptVideoId:receipt3d.videoId,concurrentFilesModified:false};
  fs.writeFileSync(path.join(root,reviewPath),JSON.stringify(review,null,2)+'\n');
  const run=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--decision','distinct','--reason',review.decisionReason,'--studio-evidence',report.studioEvidence],{cwd:root,encoding:'utf8'});
  process.stdout.write(run.stdout||'');process.stderr.write(run.stderr||'');if(run.status!==0)process.exit(run.status||1);
}
const run=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],{cwd:root,encoding:'utf8'});
process.stdout.write(run.stdout||'');process.stderr.write(run.stderr||'');process.exitCode=run.status||0;
