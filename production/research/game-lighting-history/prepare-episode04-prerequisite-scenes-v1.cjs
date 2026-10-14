const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='motion-canvas/src/projects/game-lighting-history-04/spatial';
const plan=JSON.parse(fs.readFileSync(path.join(root,'projects/game-lighting-history-04/planning/causal-additive-preparation-v1.json'),'utf8'));
if(plan.nodes.length!==11)throw Error('Eleven reviewed prerequisites required');
const outputs=[];
function write(p,t){if(fs.existsSync(path.join(root,p)))throw Error('Preserve existing '+p);fs.writeFileSync(path.join(root,p),t);outputs.push(p);}
plan.nodes.forEach((n,i)=>write(`${base}/additive-prerequisite-proof${i}-v1.tsx`,`import {prerequisiteProof} from './additive-prerequisite-runtime-v1';\nexport default prerequisiteProof(${i});\n`));
write(`${base}/additive-prerequisite-project-v1.ts`,`import {makeProject} from '@motion-canvas/core';\n${plan.nodes.map((n,i)=>`import p${i} from './additive-prerequisite-proof${i}-v1?scene';`).join('\n')}\nexport default makeProject({scenes:[${plan.nodes.map((_,i)=>'p'+i).join(',')}]});\n`);
const record={preparedAt:new Date().toISOString(),independentScenes:11,style:'research-black-v1',models:plan.nodes.map((n,i)=>({id:n.id,originalScene:n.scene,placement:n.position,proof:outputs[i],question:n.question,calculation:n.calculation})),model:base+'/additive-prerequisite-model-v1.tsx',runtime:base+'/additive-prerequisite-runtime-v1.tsx',proofSecondsPerScene:8.8,narrationAttached:false,measuredTimingApproved:false,actualFootageTime:0,allAnimatedPixelsReviewed:false,allFinalPixelsReviewed:false,privateUploaded:false};
write('projects/game-lighting-history-04/production/additive-spatial-preparation-v1.json',JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({preparedSceneSources:11,outputs:outputs.length,proofOnly:true,allFinalPixels:false}));
