// Explicit reviewed candidate records; media/raster/foreign paths are excluded.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design',proof=batch+'/proof-avoid-game-comparisons',project='projects/avoid-game-comparisons',prod=project+'/production',mc='motion-canvas/src/projects/avoid-game-comparisons';
const selected=[batch+'/README.md',batch+'/queue.json',proof+'/latest-checkpoint.json',proof+'/native-cue-evidence-git-verification.json',
 proof+'/source-research/source-action-bank-v6.json',proof+'/source-research/source-action-bank-v7.json',
 project+'/README.md',project+'/project.json',project+'/rebuild.json',project+'/sources/action-map.json',project+'/planning/chapter-plan.json',
 'motion-canvas/vite.avoid-game-comparisons.config.ts',mc+'/scenes/cue-diagrams.tsx',mc+'/cue-lookdev-project.ts',mc+'/cue-lookdev-review.html',
 ...['lookdev13','lookdev14','lookdev-cue062','lookdev-cue064','lookdev-cue102','lookdev-cue104','lookdev-cue122','lookdev-cue153'].map(p=>mc+'/scenes/'+p+'.tsx'),
 ...['all-actual-cue-trial-direct-review-v3.json','build-aligned-candidate-v5.py','build-candidate-captions-v2.py','build-measured-edit-v1.py','compile-native-review-v1.cjs',
 'extract-candidate-cue-review-v3.py','extract-flagged-native-context.py','extract-framing-corrections-v5.py','extract-targeted-lower-framing-v4.py',
 'flagged-native-context-direct-review.json','framing-corrections-direct-review-v5.json','inspect-rocket-reallocation.py','latest-checkpoint.json',
 'native-cue-proposal-v4.json','native-cue-proposal-v5.json','native-framing-pilot-direct-review.json','new-diagram-lookdev-review.json',
 'prepare-candidate-caption-layout-v2.cjs','record-all-actual-cue-review-v3.py','record-context-native-review.py','record-flagged-native-context-review.py',
 'record-framing-corrections-review-v5.py','record-native-framing-pilot-review.py','record-new-diagram-lookdev.py','record-targeted-framing-review-v4.py',
 'sync-measured-framing-checkpoint-v5.py','targeted-framing-direct-review-v4.json','word-action-alignment-review-v5.json'].map(p=>prod+'/'+p),
 prod+'/measured-edit-v1/plan.json',prod+'/measured-edit-v1/native-review-v1/compiled.json',prod+'/measured-edit-v1/native-review-v1/execution.json',prod+'/measured-edit-v1/native-review-v1/session.json',prod+'/measured-edit-v1/native-intro-candidate/extraction.json',
 ...[2,3,4,5].flatMap(v=>['plan.json','caption-layout-v1.json','caption-tracks-v1.json','captions.en.candidate.srt','captions.ko.candidate.ass','captions.ko.candidate.srt','native-review-v1/compiled.json','native-review-v1/execution.json'].map(p=>prod+'/measured-edit-v'+v+'/'+p)),
 prod+'/measured-edit-v2/framing-pilot-local/extraction.json',prod+'/measured-edit-v3/cue-review-local-v1/execution.json',prod+'/measured-edit-v3/flagged-native-context-local/execution.json',
 prod+'/measured-edit-v4/rocket-flight-context-local/execution.json',prod+'/measured-edit-v4/targeted-lower-framing-local/execution.json',prod+'/measured-edit-v5/framing-corrections-local/execution.json',
 batch+'/prepare-measured-framing-progress-delivery.cjs',batch+'/deliver-measured-framing-progress.cjs',batch+'/measured-framing-progress-delivery-paths.json',proof+'/measured-framing-progress-pre-delivery-checks.json'];
if(new Set(selected).size!==selected.length)throw Error('Duplicate explicit path');
const generated=new Set([batch+'/measured-framing-progress-delivery-paths.json',proof+'/measured-framing-progress-pre-delivery-checks.json']);
const missing=selected.filter(p=>!fs.existsSync(path.join(root,p))&&!generated.has(p));if(missing.length)throw Error('Missing reviewed path '+missing.join(', '));
if(selected.some(p=>/\.(?:png|jpe?g|webp|gif|bmp|tiff?|mp4|webm|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)))throw Error('Media/raster path');
fs.writeFileSync(path.join(root,batch+'/measured-framing-progress-delivery-paths.json'),JSON.stringify(selected,null,2)+'\n');
console.log(JSON.stringify({explicitPaths:selected.length,newImages:0,completedVideo:false}));
