const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),mc=path.join(root,'motion-canvas/src/projects/game-writing');
const script=JSON.parse(fs.readFileSync(path.join(root,'projects/game-writing/script/narration.ko.json'),'utf8'));
for(const [i,scene]of script.scenes.entries()){
 const code=scene.classification==='actual'?`import {actualScene} from './actual-scene';\nexport default actualScene(${i});\n`:`import {makeScene2D} from '@motion-canvas/2d';\nimport {narrativeConcept} from './narrative-concept';\nimport {SCENE_DURATIONS} from '../timing';\nexport default makeScene2D(function*(view){yield* narrativeConcept(view,${(i-1)/2},SCENE_DURATIONS[${i}]);});\n`;
 fs.writeFileSync(path.join(mc,`scenes/scene${scene.id}.tsx`),code);
 if(scene.classification==='explanation')fs.writeFileSync(path.join(mc,`lookdev-${scene.id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {narrativeConcept} from './scenes/narrative-concept';\nexport default makeScene2D(function*(view){yield* narrativeConcept(view,${(i-1)/2},8);});\n`);
}
fs.copyFileSync(path.join(root,'motion-canvas/src/projects/responsive-game-feedback/scenes/membership-outro.tsx'),path.join(mc,'scenes/membership-outro.tsx'));
fs.writeFileSync(path.join(mc,'timing.ts'),`// Planning only. Replace together with validated narration/cuts/SRT before final render.\nexport const ACTUAL_MEDIA_READY=false;\nexport const SCENE_DURATIONS=[60,40,60,40,60,40,60,40,60,40,60,40];\n`);
const imports=script.scenes.map(s=>`import scene${s.id} from './scenes/scene${s.id}?scene';`).join('\n');
fs.writeFileSync(path.join(mc,'project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport narration from './assets/narration.wav';\nimport intro from '../small-window-game-design/intro-cats-v2/scene?scene';\n${imports}\nimport membershipOutro from './scenes/membership-outro?scene';\nexport default makeProject({name:'game-writing',audio:narration,scenes:[intro,${script.scenes.map(s=>'scene'+s.id).join(',')},membershipOutro]});\n`);
const explain=script.scenes.filter(s=>s.classification==='explanation');
fs.writeFileSync(path.join(mc,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${explain.map(s=>`import scene${s.id} from './lookdev-${s.id}?scene';`).join('\n')}\nexport default makeProject({name:'game-writing-explanation-lookdev',scenes:[${explain.map(s=>'scene'+s.id).join(',')}]});\n`);
console.log('12 independent script scenes + original intro/outro prepared. Actual-media final rendering remains gated.');
