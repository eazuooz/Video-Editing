const fs=require('fs');const root='motion-canvas/src/projects/similar-game-design/',b='projects/similar-game-design/production/';
const ids=['23-mining-and-pursuit','24-destination-and-danger','25-gap-during-pursuit'];
const timing=JSON.parse(fs.readFileSync(root+'authoring-timing-v1.json','utf8'));
for(const id of ids){if(timing.rows.some(x=>x.id===id))throw Error('Already prepared');timing.rows.push({id,durationSeconds:14,paragraphStarts:[0,7]});
fs.writeFileSync(root+'scenes/'+id+'.tsx',`import {makeScene2D} from '@motion-canvas/2d';\nimport {similarExplanation} from '../spatial-explanation-v1';\nimport timing from '../authoring-timing-v1.json';\nexport default makeScene2D(function*(view){const row=timing.rows.find(x=>x.id==='${id}');if(!row)throw Error('Guide timing missing');yield* similarExplanation(view,'${id}',{...row,measured:false});});\n`);}
fs.writeFileSync(root+'authoring-timing-v1.json',JSON.stringify(timing,null,2)+'\n');
let project=fs.readFileSync(root+'authoring-project-v1.ts','utf8');
project=project.replace('export default makeProject',ids.map((id,i)=>`import s${i+21} from './scenes/${id}?scene';`).join('\n')+'\nexport default makeProject').replace('s19,s20]','s19,s20,s21,s22,s23]');
fs.writeFileSync(root+'authoring-project-v1.ts',project);
fs.writeFileSync(b+'three-guide-spatial-lookdev-preparation-v3.json',JSON.stringify({preparedAt:new Date().toISOString(),ids,independentSceneWrappers:24,meaningfulGeometry:'Projected front/top/side faces, depth sorting and occluded ground paths, approach/avoid vectors, target circle with continuing nearby actors, rock gap and pursuer. This is illustration of relationships, not actual footage.',measuredNarrationTimingApplied:false,allNewAnimatedPixelsReviewed:false,allFinalParagraphPixelsReviewed:false,finalRenderApproved:false,previewFps:30,finalFps:60,imagesGitAdded:0},null,2)+'\n');
console.log(JSON.stringify({newWrappers:3,totalWrappers:24,timing:'unmeasured-lookdev-only',renders:0}));
