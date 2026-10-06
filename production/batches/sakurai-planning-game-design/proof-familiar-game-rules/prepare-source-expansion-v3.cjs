const fs=require('node:fs'),path=require('node:path');
const base=__dirname,root=path.resolve(base,'../../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const file=path.join(base,'additional-official-sources-v3.cjs');
if(fs.existsSync(file))throw Error('Inspect existing producer rather than repeating preparation');
const closed=read('projects/familiar-game-rules/production/current-independent-asr-execution-v1.json');
if(closed.exitCode!==0||!closed.actualExitObserved||!closed.directReview)throw Error('Current independent ASR must be closed and directly reviewed');
const ax='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/official-gunbrella-facts-watch.ax.txt';
const text=fs.readFileSync(path.join(root,ax),'utf8');
if(!text.includes('What the Facts: Gunbrella')||!text.includes('DevolverDigital')||!text.includes('zxzPcsI8l2o'))throw Error('Actual official browser evidence required');
let s=fs.readFileSync(path.join(base,'additional-official-sources-v2.cjs'),'utf8');
for(const [a,b]of [['resource-observation-v7.json','resource-observation-v10.json'],['additional-source-execution-v2.json','additional-source-execution-v3.json'],["['q8iWixSvfsI','XbW4873OPZo']","['zxzPcsI8l2o']"],['-additional-v2-','-additional-v3-'],['research/additional-native-v2/','research/additional-native-v3/'],['item.additionalSourceExpansionExecution=','item.additionalSourceThirdExpansionExecution=']]){
 if(!s.includes(a))throw Error('Template mismatch '+a);s=s.replaceAll(a,b);
}
s=s.replace("if(fs.existsSync(path.join(root,stateFile)))", "const closedAsr=read('projects/familiar-game-rules/production/current-independent-asr-execution-v1.json');if(closedAsr.exitCode!==0||!closedAsr.actualExitObserved)throw Error('Single ASR must be closed');\nif(fs.existsSync(path.join(root,stateFile)))");
fs.writeFileSync(file,s,{flag:'wx'});
const p={schemaVersion:1,preparedAt:new Date().toISOString(),producer:path.relative(root,file).replaceAll('\\','/'),executionStarted:false,cutApproval:false,bodyRatioApproval:false,sourceAudio:false,
 sources:[{videoId:'zxzPcsI8l2o',game:'Gunbrella',title:'What the Facts: Gunbrella',url:'https://www.youtube.com/watch?v=zxzPcsI8l2o',officialEvidence:ax,
 observations:['5s large title overlay excluded','20s umbrella glide toward rooftop target; likely trailer overlap, needs cross-source review','40s industrial platforms/bridge with aimed projectiles','60s container-platform fire and airborne target; native continuity and exact edges pending'],
 recentUse:'Scoped rg exactID in project/batch records found only familiar-game-rules discovery AX; no previously delivered use. Same-game native overlap still pending.',permission:'Existing directly read personalized Devolver/YamYamCoding permission; no new agreement accepted',selectedForAcquisition:true,cutSelected:false}],
 restrictedPedroSources:'Previously age restricted JyahBxUAYbs/zaPBAKg3VT4 remain excluded; no bypass/retry',imagesGitPolicy:'local-only',foreignWorkPreserved:true};
fs.writeFileSync(path.join(base,'source-expansion-preflight-v3.json'),JSON.stringify(p,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:true,sources:1,executionStarted:false,cutApproval:false}));
