// Explicit progress files; no media, research frames or other-user changes.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design',proof=batch+'/proof-avoid-game-comparisons',project='projects/avoid-game-comparisons',mc='motion-canvas/src/projects/avoid-game-comparisons';
const files=[
  mc+'/production-plan.json',mc+'/project.ts',
  ...['cue-diagrams.tsx','mixed-additive-scene.tsx','scene06.tsx','scene10.tsx','scene12.tsx','scene15.tsx'].map(p=>mc+'/scenes/'+p),
  batch+'/README.md',batch+'/queue.json',proof+'/latest-checkpoint.json',proof+'/expanded-voice-evidence-git-verification.json',
  proof+'/source-research/source-action-bank-v5.json',proof+'/source-research/direct-native-accessibility-actions-review.json',
  project+'/README.md',project+'/planning/chapter-plan.json',project+'/planning/outline.md',project+'/project.json',project+'/rebuild.json',
  project+'/script/narration.ko.json',project+'/script/narration.en.json',project+'/sources/action-map.json',project+'/sources/game-candidates.json',
  ...[
    'action-map-v4-preserved.json','inspect-native-accessibility-actions.py','inspect-native-cue-edges.py',
    'measured-paragraphs-expanded15.json','measured-paragraphs-new15.json','narration-expanded15-index.json',
    'narration-script-en-14-preserved.json','narration-script-ko-14-preserved.json',
    'native-accessibility-actions-execution.json','native-cue-boundary-direct-review.json','native-cue-commentary-text-review.json',
    'native-cue-context-asr-execution.json','native-cue-context-asr-session.json','native-cue-context-readback-request.json',
    'native-cue-edges-execution.json','native-cue-edges-initial-checkpoint-failure.json','native-cue-edges-initial-checkpoint-failure-42224.json','native-cue-edges-session.json',
    'native-cue-narration-direct-review.json','native-cue-narration-request.json','native-cue-narration-tts-execution.json','native-cue-narration-tts-session.json',
    'native-cue-proposal.json','native-cue-proposal-v2.json','native-cue-proposal-v3.json',
    'native-cue-whole-asr-execution.json','native-cue-whole-asr-session.json',
    'plan-native-cue-alignment.py','record-native-cue-boundary-review.py','record-native-cue-text-plan.py','record-native-cue-voice-review.py',
    'record-native-accessibility-action-review.py','normalize-current15-cue-checkpoint.py',
    'render-native-cue-narration.py','review-native-cue-narration.py','script-source-review-v3-preserved.json','script-source-review.json','latest-checkpoint.json',
    'native-cue-whole-asr-local/15.json','native-cue-context-asr-local/15-first-paragraph.json',
    'native-cue-context-asr-local/15-desk-pepper-context.json','native-cue-context-asr-local/15-target-mine-context.json',
  ].map(p=>project+'/production/'+p),
  batch+'/prepare-native-cue-progress-delivery.cjs',batch+'/deliver-native-cue-progress.cjs',batch+'/native-cue-progress-delivery-paths.json',
  proof+'/native-cue-progress-pre-delivery-checks.json',
];
if(new Set(files).size!==files.length)throw Error('Duplicate explicit path');
const missing=files.filter(p=>!fs.existsSync(path.join(root,p))&&!p.endsWith('native-cue-progress-delivery-paths.json')&&!p.endsWith('native-cue-progress-pre-delivery-checks.json'));
if(missing.length)throw Error('Missing reviewed file: '+missing.join(', '));
fs.writeFileSync(path.join(root,batch+'/native-cue-progress-delivery-paths.json'),JSON.stringify(files,null,2)+'\n');
console.log(JSON.stringify({explicitPaths:files.length,newImages:0,completedVideo:false}));
