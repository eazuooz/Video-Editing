const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const input=path.join(root,'projects/game-lighting-history-01/production/animation-storyboard-v3.json');
const story=JSON.parse(fs.readFileSync(input,'utf8'));
const selected=new Map();
for(const scene of story.scenes)for(const action of scene.paragraphs){
 if(!selected.has(action.model)&&Object.entries(action.to).some(([k,v])=>v!==action.from[k]))
  selected.set(action.model,{sceneId:scene.id,key:action.key,model:action.model,focus:action.focus});
}
if(selected.size!==12)throw Error('All12 projected models must have a motion proof.');
const folder=path.join(root,'motion-canvas/src/projects/game-lighting-history-01/black-lookdev-v2');
fs.mkdirSync(folder,{recursive:true});
const cases=[...selected.values()];
cases.forEach((c,i)=>fs.writeFileSync(path.join(folder,`proof${i}.tsx`),`import {blackProof} from './runtime';\nexport default blackProof('${c.sceneId}','${c.key}');\n`));
fs.writeFileSync(path.join(folder,'project.ts'),`import {makeProject} from '@motion-canvas/core';\n${cases.map((_,i)=>`import proof${i} from './proof${i}?scene';`).join('\n')}\nexport default makeProject({scenes:[${cases.map((_,i)=>'proof'+i).join(',')}]});\n`);
const record={schemaVersion:2,createdAt:new Date().toISOString(),styleId:'research-black-v1',
 storyboardSha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),
 purpose:'All12 model palette and spatial-motion proof;3s per case; not final measured narration or native quota.',
 cases,plannedFramesAt60:cases.length*180,pixelsReviewed:false,finalVideoProduced:false,
 localOnlyOutput:'projects/game-lighting-history-01/production/local/black-lookdev-v2'};
fs.writeFileSync(path.join(__dirname,'black-lookdev-plan-v2.json'),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({cases:cases.length,seconds:cases.length*3,frames:record.plannedFramesAt60,styleId:record.styleId}));
