// Usage: node projects/player-customization/production/fix-delivery-whitespace-v1.cjs
// Preserve original bytes locally; fix only whitespace reported by the isolated staged check.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization';
const temp=fs.readdirSync(path.join(root,'.git')).filter(n=>n.startsWith('player-customization-delivery-')).map(n=>({dir:n,time:fs.statSync(path.join(root,'.git',n)).mtimeMs})).sort((a,b)=>b.time-a.time)[0];
if(!temp)throw Error('Isolated stage missing');
const env={...process.env,GIT_INDEX_FILE:path.join(root,'.git',temp.dir,'index')};
const checked=cp.spawnSync('git',['diff','--cached','--check'],{cwd:root,env,encoding:'utf8',windowsHide:true,maxBuffer:64e6});
if(checked.status!==2)throw Error('Expected the recorded whitespace-only check failure');
const findings=[...checked.stdout.matchAll(/^([^:\r\n]+):\d+: (trailing whitespace|new blank line at EOF)\./gm)].map(m=>({file:m[1],issue:m[2]}));
const files=[...new Set(findings.map(f=>f.file))];
if(!files.length||files.some(f=>!f.startsWith(base+'/publishing/')&&!f.startsWith('motion-canvas/src/projects/player-customization/')))throw Error('Unexpected whitespace path');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),records=[];
const backup='shared/output/player-customization/research/git-whitespace-originals-v1';
for(const file of files){
 const before=fs.readFileSync(path.join(root,file));
 const relative=path.join(backup,file),destination=path.join(root,relative);fs.mkdirSync(path.dirname(destination),{recursive:true});
 if(fs.existsSync(destination)&&!fs.readFileSync(destination).equals(before))throw Error('Original local backup already differs '+file);
 fs.writeFileSync(destination,before);
 let after=before.toString('utf8').replace(/\r\n/g,'\n');
 if(file.endsWith('.ax.txt'))after=after.split('\n').map(l=>l.replace(/[\t ]+$/,'')).join('\n');
 else if(findings.some(f=>f.file===file&&f.issue!=='new blank line at EOF'))throw Error('Only TS EOF normalization authorized '+file);
 after=after.replace(/\n+$/,'')+'\n';
 fs.writeFileSync(path.join(root,file),after);
 records.push({file,issues:findings.filter(f=>f.file===file).map(f=>f.issue),originalSha256:sha(before),finalSha256:sha(Buffer.from(after)),localOriginalBackup:relative.replaceAll('\\','/')});
}
const proof={schemaVersion:1,slug:'player-customization',recordedAt:new Date().toISOString(),reason:'Isolated staged whitespace check rejected generated TS EOF blank lines and trailing whitespace in CUA AX formatting. Only those reported paths were normalized; original bytes remain local. No narration, media, timing, plan or rendered pixels were changed.',failedStageIndex:env.GIT_INDEX_FILE,changedFiles:records,mediaChanged:false,sourcePlanChanged:false,foreignFilesChanged:false,newQaImages:0};
fs.writeFileSync(path.join(root,base+'/production/git-whitespace-normalization-v1.json'),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({whitespaceFiles:records.length,originalsPreservedLocally:true,mediaChanged:false}));
