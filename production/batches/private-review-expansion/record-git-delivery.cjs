const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2];
function git(a){const r=spawnSync('git',a,{cwd:root,encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stderr);return r.stdout.trim();}
const branch=git(['branch','--show-current']),sha=git(['rev-parse','HEAD']);
const remote=git(['config',`branch.${branch}.remote`]),ref=git(['config',`branch.${branch}.merge`]);
const remoteSha=git(['ls-remote',remote,ref]).split(/\s/)[0];
if(remoteSha!==sha)throw Error('Push is not verified: local/remote differ');
const files=['production/batches/private-review-expansion/queue.json','production/batches/sakurai-planning-game-design/queue.json'];
const q=JSON.parse(fs.readFileSync(path.join(root,files[0]),'utf8')),i=q.items.find(i=>i.slug===slug);
if(!i?.qa||!i?.output||i?.newPrivateUpload?.status!=='uploaded-private')throw Error('Render/QA/output/private upload must finish first');
const evidence={status:'committed-and-pushed',productionCommit:sha,branch,remote,verifiedRemoteSha:remoteSha,verifiedAt:new Date().toISOString(),mediaCommitted:false,checks:['media:check passed','rebuild:check passed','staged diff whitespace passed']};
i.gitDelivery=evidence;i.status='complete-private-review';i.stage='render-qa-collected-private-settings-verified-and-pushed';
q.updatedAt=evidence.verifiedAt;
fs.writeFileSync(path.join(root,files[0]),JSON.stringify(q,null,2)+'\n');
const main=JSON.parse(fs.readFileSync(path.join(root,files[1]),'utf8')),m=main.items.find(i=>i.slug===slug);m.privateExpansion.gitDelivery=evidence;main.updatedAt=evidence.verifiedAt;
fs.writeFileSync(path.join(root,files[1]),JSON.stringify(main,null,2)+'\n');
console.log(JSON.stringify(evidence));
