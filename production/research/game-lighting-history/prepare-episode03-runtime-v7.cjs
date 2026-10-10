const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='motion-canvas/src/projects/game-lighting-history-03/spatial/',project='projects/game-lighting-history-03';
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const runtime=base+'narrated-runtime-v7.tsx';
if(fs.existsSync(path.join(root,runtime)))throw Error('Preserve existing runtime');
let s=fs.readFileSync(path.join(root,base+'narrated-runtime-v6.tsx'),'utf8');
for(const [from,to] of [
 ['narratedChapterV6','narratedChapterV7'],
 ["'./restir-model-v1'","'./restir-model-v2'"],
 ["'./lumen-model-v1'","'./lumen-model-v2'"],
 ["'./foundation-models-v4'","'./foundation-models-v5'"],
 ["'./culling-model-v2'","'./culling-model-v3'"]
]){if(!s.includes(from))throw Error('Expected runtime input missing '+from);s=s.split(from).join(to);}
fs.writeFileSync(path.join(root,runtime),s);
const modules=['foundation-models-v5.tsx','restir-model-v2.tsx','culling-model-v3.tsx','lumen-model-v2.tsx'];
const record={schemaVersion:1,preparedAt:new Date().toISOString(),runtime:{path:runtime,sha256:sha(runtime)},
 preservedRuntime:{path:base+'narrated-runtime-v6.tsx',sha256:sha(base+'narrated-runtime-v6.tsx')},
 adoptedImports:modules.map(x=>({path:base+x,sha256:sha(base+x)})),
 change:'Use already directly reviewed spatial corrections: yawed foundation faces, disjoint reservoir rows, separated culling labels and SurfaceCache layout. Preserve original narration clock, heading sequence and integer-frame bottom captions.',
 renderStarted:false,finalTimelineAdopted:false,finalInputTimingApproved:false,finalPixelReviewComplete:false,sourceAudioUsed:false,
 note:'Prepared runtime only. Final measured guide/native timeline and final animation/caption QA remain required.'};
const out=project+'/production/spatial-runtime-adoption-preparation-v7.json';fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({runtime,record:out,newTts:false,newMedia:false,finalTimelineAdopted:false}));
