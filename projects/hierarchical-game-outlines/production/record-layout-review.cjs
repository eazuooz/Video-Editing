// Record only direct silent-layout and thumbnail observations already performed.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/hierarchical-game-outlines/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const now=new Date().toISOString();
for(const version of ['v1','v2']){
 const folder=base+'lookdev-'+version+'/',inspection=read(folder+'inspection.json'),render=read(folder+'render-result.json');
 if(inspection.directVisualReview!=='pending')throw Error('Preserve recorded inspection; do not silently rewrite a previous review.');
 if(hash(inspection.source)!==inspection.sourceSha256||!render.done||render.result!==0||render.frames!==2880)throw Error('Rendered source/hash mismatch.');
 const decode=folder+'decode-errors.log';
 if(fs.statSync(path.join(root,decode)).size!==0)throw Error('Review decode errors first.');
 const accepted=version==='v2';
 Object.assign(inspection,{reviewedAt:now,directVisualReview:accepted?'passed-silent-layout-only':'rejected-transition-overlap',
  framesDirectlyReviewed:inspection.frames.length+inspection.transitionFrames.length,
  observed:{width:1920,height:1080,fps:'60/1',frames:2880,durationSeconds:48,audioStreams:0,fullDecodeExitCode:0,decodeErrorBytes:0},
  commands:{probe:'ffprobe -v error -show_streams -show_format -of json '+inspection.source,
   decode:'ffmpeg -v error -i '+inspection.source+' -f null -',
   typeScript:'node motion-canvas/node_modules/typescript/bin/tsc -p motion-canvas/tsconfig.hierarchical-game-outlines.json --noEmit'},
  typeScriptExitCode:0,silentLookdev:true,finalNarratedVideo:false,allFinalCaptionApproval:false,
  observations:accepted?[
   'All18 early/middle/late views preserve readable white2.5D cards, headers and lower summary space.',
   'Six transition states inspected: tree reveal, child movement, folded preservation, unfolding, branch movement and return arrow.',
   'Grey arrows behind cards no longer cross moving label text in corrected movement views.',
   'Fold label disappears before children unfold; preserved cards and arrows return without label overlap.',
   'Containment/cross-reference diagrams are explanatory proposals, not developer internal documents.',
   'This silent reel does not approve final measured narration, gameplay cuts or fixed caption cues.',
  ]:[
   'Transition views exposed grey arrows crossing height/curve labels during movement.',
   'Concurrent fold-label fade and scaled child cards overlapped during unfolding.',
   'Preserved rejected reel/images; corrected source and rendered a separate v2.',
  ],
  evidenceImages:[...inspection.frames,...inspection.transitionFrames].map(item=>({path:item.path,sha256:hash(item.path)})),
 });
 if(accepted)inspection.sceneCodeSha256=hash('motion-canvas/src/projects/hierarchical-game-outlines/scenes/outline-concepts.tsx');
 write(folder+'inspection.json',inspection);
}
const recipePath='projects/hierarchical-game-outlines/publishing/thumbnail-recipe.json',recipe=read(recipePath);
if(recipe.sha256!==hash('projects/hierarchical-game-outlines/publishing/thumbnail.png'))throw Error('Thumbnail changed.');
Object.assign(recipe,{visualReview:'passed-local-layout-only',directlyReviewedAt:now,
 observations:['Yellow strip, white base, large black Korean and original cats preserved.',
 'Observed native3173-second face-free Two Point Museum track/support frame used.',
 'Title, bubbles, goal/feature/rule tiles and frame fit without clipping or overlap.'],uploaded:false});
write(recipePath,recipe);
console.log('Recorded silent v2 layout/local thumbnail review; final-video approval remains false.');
