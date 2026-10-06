const fs=require('node:fs'),path=require('node:path');
const base=__dirname,root=path.resolve(base,'../../../..');
const file=path.join(base,'additional-official-sources-v2.cjs');
if(fs.existsSync(file))throw Error('Prepared producer exists; inspect it rather than replacing it');
let s=fs.readFileSync(path.join(base,'additional-official-sources-v1.cjs'),'utf8');
const changes=[
 ["resource-observation-v5.json","resource-observation-v7.json"],
 ["additional-source-execution-v1.json","additional-source-execution-v2.json"],
 ["['FVkDc6u_4GQ','tEe5NYp9018']","['q8iWixSvfsI','XbW4873OPZo']"],
 ["-additional-","-additional-v2-"],
 ["research/additional-native-v1/","research/additional-native-v2/"],
 ["item.additionalSourceExecution=","item.additionalSourceExpansionExecution="]
];
for(const [from,to]of changes){if(!s.includes(from))throw Error('Source-template mismatch: '+from);s=s.replaceAll(from,to);}
const guard="const closedTts=read(base+'/narration-execution-v1.json');if(closedTts.exitCode!==0||closedTts.status!=='synthesis-finished-awaiting-current-ASR')throw Error('Current GPU synthesis must be closed before new source worker');\n";
s=s.replace("if(fs.existsSync(path.join(root,stateFile)))",guard+"if(fs.existsSync(path.join(root,stateFile)))");
fs.writeFileSync(file,s,{flag:'wx'});
const preflight={schemaVersion:1,preparedAt:new Date().toISOString(),purpose:'Expand measured actual-action capacity without shortening current explanation/PCM',producer:path.relative(root,file).replaceAll('\\','/'),executionStarted:false,sourceAudio:false,loop:false,editorSlowdown:false,finalRatioApproved:false,cutApproval:false,sources:[
 {id:'q8iWixSvfsI',game:'Gunbrella',url:'https://www.youtube.com/watch?v=q8iWixSvfsI',officialChannel:'DevolverDigital',evidence:'production/batches/sakurai-planning-game-design/proof-familiar-game-rules/official-gunbrella-reveal-watch.ax.txt',directBrowserPixelObservations:['20s outdoor movement among stalls/NPC','25s visible umbrella held toward left-side firing target','35s character above factory gate; surrounding movement/action needs native review'],exactIntervalsApproved:false},
 {id:'XbW4873OPZo',game:'Anger Foot',url:'https://www.youtube.com/watch?v=XbW4873OPZo',officialChannel:'DevolverDigital',evidence:'production/batches/sakurai-planning-game-design/proof-familiar-game-rules/official-anger-kicking-watch.ax.txt',directBrowserPixelObservations:['10s exterior shoe closeup: cinematic excluded','20s sneaker promotion card excluded','30s first-person kick at nearby target in burning corridor','40s first-person kicking in tiled bathroom'],exactIntervalsApproved:false}
],permission:'devolver-yamyamcoding-permission.ax.txt; previously directly read personalized commercial permission includes both games',recentUse:'Exact IDs searched in current project records; no prior delivered use found. Same-game different trailers may contain duplicate native shots; cross-source pixel review still required.',restrictedPedroCandidates:'JyahBxUAYbs/zaPBAKg3VT4 remain excluded from acquisition after actual age restriction; no bypass'};
fs.writeFileSync(path.join(base,'source-expansion-preflight-v2.json'),JSON.stringify(preflight,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:true,producer:preflight.producer,sourceCount:2,cutApproval:false,executionStarted:false}));
