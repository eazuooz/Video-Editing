// This authors editable scene code and a guarded placeholder plan, never final media.
const fs = require('node:fs');
const base = 'motion-canvas/src/projects/motion-sickness-games/';
const script = JSON.parse(fs.readFileSync('projects/motion-sickness-games/script/narration.ko.json', 'utf8'));
const write = (file, text) => fs.writeFileSync(file, text);
if (fs.existsSync(base + 'production-plan.json')) throw new Error('Scene scaffold already authored; update it deliberately instead of replacing measured timing.');
const plan = {status: 'scene-code-authored-not-rendered', currentFinalTimingApproved: false,
  bodyRatioApproved: false, captionReviewComplete: false,
  scenes: script.scenes.map((s, i) => ({id: s.id, title: s.title, kind: i % 2 ? 'explanation' : 'actual-existing-game-action',
    seconds: 0, paragraphEnds: [], actualVideo: '', actualAudioStreams: -1, actualMediaVerified: false})),
};
write(base + 'production-plan.json', JSON.stringify(plan, null, 2) + '\n');
for (const [i, scene] of script.scenes.entries()) {
  write(base + `scenes/scene${scene.id}.tsx`, i % 2
    ? `import {explanationScene} from './explanation-scene';\nexport default explanationScene('${scene.id}', ${Math.floor(i / 2)});\n`
    : `import {actualScene} from './actual-scene';\nexport default actualScene('${scene.id}');\n`);
  if (i % 2) write(base + `lookdev-${scene.id}.tsx`, `import {makeScene2D} from '@motion-canvas/2d';\nimport {cameraConcept} from './scenes/camera-concepts';\nexport default makeScene2D(function*(view){yield* cameraConcept(view,${Math.floor(i / 2)},8);});\n`);
}
const ids = script.scenes.map(s => s.id);
write(base + 'lookdev-project.ts', `import {makeProject} from '@motion-canvas/core';\n` + ids.filter((_, i) => i % 2).map(id => `import s${id} from './lookdev-${id}?scene';`).join('\n') + `\nexport default makeProject({name:'motion-sickness-games-lookdev',scenes:[${ids.filter((_, i) => i % 2).map(id => 's' + id).join(',')}]});\n`);
write(base + 'project.ts', `import {makeProject} from '@motion-canvas/core';\nimport narration from './assets/narration.wav';\nimport intro from '../small-window-game-design/intro-cats-v2/scene?scene';\n` + ids.map(id => `import s${id} from './scenes/scene${id}?scene';`).join('\n') + `\nimport outro from './scenes/membership-outro?scene';\nexport default makeProject({name:'motion-sickness-games',audio:narration,scenes:[intro,${ids.map(id => 's' + id).join(',')},outro]});\n`);
// The original membership identities and logo remain pixels from supplied assets.
fs.copyFileSync('motion-canvas/src/projects/picking-sides/scenes/membership-outro.tsx', base + 'scenes/membership-outro.tsx');
write('projects/motion-sickness-games/production/scene-authoring.json', JSON.stringify({
  authoredAt: new Date().toISOString(), independentSceneCount: 12, explanationScenes: 6, actualScenes: 6,
  actualActionEncodingVerified: false, measuredTimingInstalled: false, narrationApproved: false,
  lookdevPacingOnly: '8 seconds per explanation; not final narration timing',
  finalPlaybackBlockedUntilCurrentMeasuredPlanApproved: true,
  captionAnchor: [960, 970], captionImplementationAndEveryCueReview: 'pending',
  originalMembershipScreenshotAndLogoReused: true, humanListening: 'pending',
}, null, 2) + '\n');
console.log('12 independent guarded scene entries and 6 editable white2.5D concept diagrams authored; no render or visual approval.');
