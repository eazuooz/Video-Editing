const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-03/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const state=read(base+'/native-guide-repairs-asr-execution-v2.json');
if(state.exitCode!==null||state.cpuThreads!==2||state.gpuJobs!==0)throw Error('Observe live worker');
const record={schemaVersion:1,observedAt:new Date().toISOString(),sessionId:72800,actualPid:state.actualPid,createTime:state.createTime,commandLine:state.commandLine,cwd:state.cwd,structuredExecutionLog:base+'/native-guide-repairs-asr-execution-v2.json',log:base+'/local/native-guide-repairs-asr-resume-v2.log',stage:state.stage,totalWindows:17,cpuThreads:2,gpuJobs:0,exitCode:null,initialImportFailure:base+'/native-guide-repairs-asr-import-failure-v2.json'};
fs.writeFileSync(path.join(root,base+'/native-guide-repairs-asr-session-v2.json'),JSON.stringify(record,null,2)+'\n');
const cp=read('production/research/game-lighting-history/checkpoint.json');cp.episode03GuideRepairAsrSessionId=72800;cp.ownedActiveWork=record;cp.next='Read all17 selective repair ASR windows and word endings; preserve original84/other18. Rebuild measured ratio and source cuts after direct approval.';fs.writeFileSync(path.join(root,'production/research/game-lighting-history/checkpoint.json'),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify(record));
