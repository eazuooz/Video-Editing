const fs=require('node:fs'),path=require('node:path');
const base=__dirname,root=path.resolve(base,'../../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const file=path.join(base,'additional-official-sources-v4.cjs');
if(fs.existsSync(file))throw Error('Inspect existing producer instead of repeating');
const closed=read(path.relative(root,path.join(base,'additional-source-execution-v3.json')));
if(closed.exitCode!==0||!closed.actualExitObserved||!closed.all15BoardsDirectlyRead)throw Error('Previous single worker must be closed and reviewed');
const ax='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/official-pedro-code-yellow-watch.ax.txt';
const text=fs.readFileSync(path.join(root,ax),'utf8');
if(!text.includes('My Friend Pedro - Code Yellow Update')||!text.includes('DevolverDigital')||!text.includes('TjgJMgkRoCg'))throw Error('Actual official UI evidence required');
let s=fs.readFileSync(path.join(base,'additional-official-sources-v3.cjs'),'utf8');
for(const [a,b] of [['resource-observation-v10.json','resource-observation-v11.json'],['additional-source-execution-v3.json','additional-source-execution-v4.json'],["['zxzPcsI8l2o']","['TjgJMgkRoCg']"],['-additional-v3-','-additional-v4-'],['research/additional-native-v3/','research/additional-native-v4/'],['item.additionalSourceThirdExpansionExecution=','item.additionalSourceFourthExpansionExecution=']]){
 if(!s.includes(a))throw Error('Template mismatch '+a);s=s.replaceAll(a,b);
}
fs.writeFileSync(file,s,{flag:'wx'});
let b=fs.readFileSync(path.join(base,'make-additional-native-boards-v3.py'),'utf8').replaceAll('additional-source-execution-v3','additional-source-execution-v4').replaceAll('additional-native-v3','additional-native-v4').replaceAll('additional-native-boards-v3','additional-native-boards-v4');
fs.writeFileSync(path.join(base,'make-additional-native-boards-v4.py'),b,{flag:'wx'});
const p={schemaVersion:1,preparedAt:new Date().toISOString(),producer:path.relative(root,file).replaceAll('\\','/'),executionStarted:false,cutApproval:false,bodyRatioApproval:false,sourceAudio:false,
 sources:[{videoId:'TjgJMgkRoCg',game:'My Friend Pedro',title:'My Friend Pedro - Code Yellow Update',url:'https://www.youtube.com/watch?v=TjgJMgkRoCg',officialEvidence:ax,
 observations:['Actual20s hook/shaft passage, may match prior Full Throttle','Actual40s factory target and movement, full native continuity pending','Actual60s upward weapon view and changed clothing/head mode; distinguish promotional camera/modifier from ordinary play'],
 recentUse:'Scoped exact-ID rg in current project/batch JSON/MD returned no matches. Same-game native overlap still pending.',permission:'Existing directly read personalized Devolver/YamYamCoding permission; no new agreement accepted',selectedForAcquisition:true,cutSelected:false}],
 rejectedCandidate:{videoId:'qfIsOanxy3o',title:'Behind the Schemes | Gunbrella with Doinksoft',evidence:'production/batches/sakurai-planning-game-design/proof-familiar-game-rules/official-gunbrella-behind-watch.ax.txt',observation:'4:00 developer interview and4:30 hardware closeup directly observed. Other sections include Demon Throttle and music; no unobserved full-video rejection claim.',selectedForAcquisition:false,reason:'Prefer concept-matched native game actions; these observed interview/hardware shots cannot fill actual-game quota'},
 restrictedPedroSources:'Previously age-restricted JyahBxUAYbs/zaPBAKg3VT4 remain excluded; no bypass/retry',imagesGitPolicy:'local-only',foreignWorkPreserved:true};
fs.writeFileSync(path.join(base,'source-expansion-preflight-v4.json'),JSON.stringify(p,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:true,sources:1,executionStarted:false,cutApproval:false}));
