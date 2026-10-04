const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),rel='production/batches/sakurai-planning-game-design/preflight/game-reward-planning.json';
const previous=JSON.parse(fs.readFileSync(path.join(root,rel),'utf8'));
const names=['game-math-polar-2d','game-math-polar-3d'];
const delta={reviewedAt:new Date().toISOString(),previousDigest:previous.inputsDigest,changedPriorInputPaths:[],newProjects:names,readFiles:[],contentFindings:[],studioEvidence:'production/batches/sakurai-planning-game-design/proof-game-reward-planning/studio-rewards-post-save-current.ax.txt',preserveCompletedVideo:true};
for(const name of names){
  for(const suffix of ['project.json','script/narration.ko.json','script/narration.en.json','planning/outline.md']){
    const p='projects/'+name+'/'+suffix,data=fs.readFileSync(path.join(root,p));
    delta.readFiles.push({path:p,sha256:crypto.createHash('sha256').update(data).digest('hex')});
  }
}
delta.contentFindings=[
  '2D polar: point/radius/angle, radians, equivalent coordinates, canonicalization, Cartesian conversion/atan2, relative aiming, angular time step, shortest rotation and vector addition. Full KO/EN18-scene scripts read. No reward catalogue/acquisition/production-scope argument.',
  '3D polar: cylinders/spheres, axis signs, heading/pitch conversions, aliases and poles, camera offset versus viewing direction, numeric error. Full KO/EN19-scene scripts read. No reward catalogue or reward production-scope argument.',
  'Shared visible game combat does not make these mathematical viewer questions equivalent to the current reward-function/condition/combination/work catalogue. Prior related10 full bilingual-script comparison and actual visible-rewards full-content review remain applicable.',
  'Current Studio 보상 search visibly contains new private D81WnOMytG4 plus existing public5W5f6T8Hho8 only. New ID is this delivered file, not an extra pre-existing duplicate. Existing reward video asks why players want one more goal and makes desired rewards/progress/use visible; current video plans catalogue functions, acquisition conditions, limits and production work.'
];
const deltaPath='production/batches/sakurai-planning-game-design/proof-game-reward-planning/inventory-refresh-20261004T1330.json';
fs.writeFileSync(path.join(root,deltaPath),JSON.stringify(delta,null,2)+'\n');
const reason=previous.contentReview+' Inventory refresh after two concurrent math drafts: full KO/EN2D18/3D19-scene scripts and outlines directly read; these concern coordinate representation/conversion/aiming/camera, not reward catalogue functions, conditions, limits and production work. Delta evidence: '+deltaPath+'.';
const studio=previous.studioEvidence+' Current post-save Studio 보상 search: '+delta.studioEvidence+' and matching PNG show only this new private D81WnOMytG4 plus existing public5W5f6T8Hho8. Existing full-content comparison preserved; no public settings altered.';
const r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','game-reward-planning','--decision','distinct','--reason',reason,'--studio-evidence',studio],{cwd:root,encoding:'utf8'});
process.stdout.write(r.stdout);process.stderr.write(r.stderr);process.exitCode=r.status;
