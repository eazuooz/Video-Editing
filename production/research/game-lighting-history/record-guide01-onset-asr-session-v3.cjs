const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-03/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const state=read(base+'/native-guide01-onset-asr-execution-v3.json');
if(state.exitCode!==null||state.cpuThreads!==2||state.gpuJobs!==0)throw Error('Observe live worker');
const record={schemaVersion:1,observedAt:new Date().toISOString(),sessionId:97250,actualPid:state.actualPid,createTime:state.createTime,commandLine:state.commandLine,cwd:state.cwd,structuredExecutionLog:base+'/native-guide01-onset-asr-execution-v3.json',log:base+'/local/native-guide01-onset-asr-v3.log',stage:state.stage,totalWindows:3,cpuThreads:2,gpuJobs:0,exitCode:null,initialImportFailure:null};
fs.writeFileSync(path.join(root,base+'/native-guide01-onset-asr-session-v3.json'),JSON.stringify(record,null,2)+'\n');
const cp=read('production/research/game-lighting-history/checkpoint.json');cp.episode03GuideOnsetAsrV3SessionId=97250;cp.ownedActiveWork=record;cp.next='Read all3 single-opener ASR windows and word endings; preserve original84/other19. Rebuild measured ratio and source cuts after direct approval.';fs.writeFileSync(path.join(root,'production/research/game-lighting-history/checkpoint.json'),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify(record));
