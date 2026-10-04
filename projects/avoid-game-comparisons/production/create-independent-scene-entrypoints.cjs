const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='avoid-game-comparisons';
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs',slug,'--check'],{cwd:root,stdio:'inherit'});
const project=path.join(root,'motion-canvas/src/projects',slug),scenes=path.join(project,'scenes');
const script=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'script/narration.ko.json'),'utf8'));
const white=new Set(['01','03','05','07','09','11']);
const save=(p,t)=>{if(fs.existsSync(p))throw Error('Preserve existing entrypoint: '+p);fs.writeFileSync(p,t);};
for(const scene of script.scenes){
  const kind=white.has(scene.id)?'explanation':'actual';
  save(path.join(scenes,`scene${scene.id}.tsx`),`import {${kind}Scene} from './${kind}-scene';\nexport default ${kind}Scene('${scene.id}');\n`);
}
for(const name of ['branding-intro','membership-outro']){
  const source=path.join(root,'motion-canvas/src/projects/game-reward-planning/scenes',name+'.tsx');
  save(path.join(scenes,name+'.tsx'),fs.readFileSync(source));
}
save(path.join(project,'project.ts'),`import {makeProject} from '@motion-canvas/core';
import intro from './scenes/branding-intro?scene';
${script.scenes.map(s=>`import scene${s.id} from './scenes/scene${s.id}?scene';`).join('\n')}
import outro from './scenes/membership-outro?scene';
// Final playback is guarded by measured scene/cut approval. The mix and
// burned narration captions will be attached only after current-audio QA.
export default makeProject({name:'avoid-game-comparisons',scenes:[intro,${script.scenes.map(s=>'scene'+s.id).join(',')},outro]});
`);
for(const scene of script.scenes.filter(s=>white.has(s.id))){
  save(path.join(scenes,`lookdev${scene.id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';
import {conceptDiagram} from './concept-diagrams';
import {addCaptionClearanceGuide} from './lookdev-caption-guide';
export default makeScene2D(function*(view){
  // Explicit silent lookdev only: these provisional20s are not production timing.
  const duration=20,ends=Array.from({length:${scene.lines.length}},(_,i)=>duration*(i+1)/${scene.lines.length});
  const diagram=conceptDiagram(view,'${scene.id}',duration,ends,true);
  addCaptionClearanceGuide(view);
  yield*diagram;
});
`);
}
save(path.join(project,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';
${script.scenes.filter(s=>white.has(s.id)).map(s=>`import scene${s.id} from './scenes/lookdev${s.id}?scene';`).join('\n')}
export default makeProject({name:'avoid-game-comparisons-silent-lookdev',scenes:[${script.scenes.filter(s=>white.has(s.id)).map(s=>'scene'+s.id).join(',')}]});
`);
save(path.join(root,'projects',slug,'production','independent-scene-design.json'),JSON.stringify({
  schemaVersion:1,createdAt:new Date().toISOString(),status:'independent-code-authored-not-final-render',
  scenes:script.scenes.map(s=>({id:s.id,title:s.title,paragraphs:s.lines.length,role:white.has(s.id)?'white2.5D-explanation':'full-screen-actual-existing-game',entrypoint:`motion-canvas/src/projects/${slug}/scenes/scene${s.id}.tsx`,pixelReview:false})),
  openingIndependentScene:'motion-canvas/src/projects/avoid-game-comparisons/scenes/scene01.tsx',
  logo:'shared/assets/branding/yamyamcoding-cats-original.png',members:'shared/assets/membership/member-list-20260929.png',
  introSeconds:2,outroSeconds:10,approvedEndingTitle:'멤버쉽가입 감사드립니다.',
  caption:{id:'boxed-white-forest-v1',centerPx:[960,970],motionCanvas:[0,430],finalPixelReview:false},
  finalTimingApproved:false,finalRatioApproved:false,audioAttached:false,finalVideoComplete:false,
  lookdev:'Independent6 white diagrams, explicitly silent/provisional20s each; not narrated delivery or ratio evidence.',
  nextAction:'Check each white diagram via normal CUA preview. Apply measured paragraph boundaries after whole current-PCM ASR, acquire sufficient unique action and build final native cuts; attach continuous Nimbus mix and reviewed fixed-caption render.'
},null,2)+'\n');
console.log('Created12 independent script entrypoints, six silent lookdev entrypoints, original2s cat/10s members; final timing and pixels pending.');
