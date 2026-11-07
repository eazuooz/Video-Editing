/* Inert-worker pure contracts only; no SDK/Vite/browser imports or processes. */
const assert=require('node:assert/strict'),path=require('node:path');
const w=require('./render-solution-path-structure-atlas-v1.cjs');
const ROOT=path.resolve(__dirname,'../../..'),M=path.join(ROOT,'motion-canvas/src/projects/shorts-leveldesign-11-05');
const MEDIA='C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05';
const SDK=path.join(__dirname,'render-solution-path-structure-atlas-v1.cjs');
let passed=0;function test(name,fn){fn();passed++;}
function fixture(){
 const attempt=path.join(MEDIA,'structure-attempts-v2/synthetic'),sourceJob=path.join(MEDIA,'structure-jobs-v2/synthetic/structure-job.json');
 const names=['project-structure-atlas-v2.ts','solution-path-structure-atlas-v2.tsx','solution-path-structure.tsx'];
 const recipe={schemaVersion:'11.05-structure-snapshot-job-v2',topicId:'11.05',fingerprint:'a'.repeat(64),picturePlanFingerprint:'b'.repeat(64),canvas:[1080,900],exportFps:60,assetFrames:2,packets:[{fingerprint:'c'.repeat(64)},{fingerprint:'d'.repeat(64)}],outputContract:{jobPath:sourceJob}};
 const font={path:'C:/Windows/Fonts/NotoSansKR-VF.ttf',sha256:'e'.repeat(64)};
 const sources=names.map(name=>({name,path:path.join(M,name)}));
 const job={schemaVersion:'11.05-structure-atlas-execution-job-v1',topicId:'11.05',attempt,sourceJob:{path:sourceJob,sha256:'f'.repeat(64)},recipe,fingerprint:'1'.repeat(64),contract:{width:1080,height:900,fps:60,frames:2,audio:false,alpha:true},stagedSources:sources,font,variables:{renderMode:'source-pinned-structural-atlas-v2',jobFingerprint:recipe.fingerprint,sourcePackets:recipe.packets},inputPins:[...sources.map(s=>({path:s.path,sha256:'2'.repeat(64)})),font,{path:sourceJob,sha256:'f'.repeat(64)},{path:SDK,sha256:'3'.repeat(64)}],versions:{core:'3.17.2',two:'3.17.2'},tools:{node:{path:process.execPath,sha256:'4'.repeat(64)}},actualSpeechTimingVerified:false,nativePixelVisibilityClaim:false,humanApproval:false};
 const jobPath=path.join(attempt,'execution-job.json');job.jobPath=path.resolve(jobPath);job.jobSHA256='5'.repeat(64);
 job.lifecycle={protocol:'architectural111-11-05-structure-atlas-v1',owner:'architectural-111-11-05-structure-atlas',token:'token',parent:{pid:123,createTime:10,argv:['synthetic-python'],commandSHA256:'6'.repeat(64)}};
 const rec={...job.lifecycle.parent,protocol:job.lifecycle.protocol,owner:job.lifecycle.owner,token:'token',fingerprint:job.fingerprint,output:attempt,child:{pid:999,createTime:11,argv:[process.execPath,SDK,job.jobPath,job.jobSHA256]}};
 return{job,jobPath,rec};
}
test('exact finite job',()=>{const x=fixture();assert.equal(w.validateJob(x.job,x.jobPath,false),x.job)});
for(const [name,mutate]of[
 ['wrongtopic',j=>j.topicId='06.02'],['oldprotocol',j=>j.schemaVersion='06-02-mc-render-job-v3'],
 ['count',j=>j.contract.frames=3],['rate',j=>j.contract.fps=30],['audio',j=>j.contract.audio=true],
 ['opaque',j=>j.contract.alpha=false],['escape',j=>j.attempt=path.join(MEDIA,'../foreign')],
 ['source',j=>j.stagedSources[0].path='foreign.ts'],['missingpin',j=>j.inputPins.pop()],
 ['variable',j=>j.variables.renderMode='unbound'],['speechpass',j=>j.actualSpeechTimingVerified=true],
 ['human',j=>j.humanApproval=true]])test(name,()=>{const x=fixture();mutate(x.job);assert.throws(()=>w.validateJob(x.job,x.jobPath,false))});
test('exact lease parent and actual child',()=>{const x=fixture();assert.equal(w.leaseMatches(x.job,x.rec,999),true)});
for(const key of['token','owner','createTime','commandSHA256'])test('changedlease-'+key,()=>{const x=fixture();x.rec[key]='changed';assert.equal(!!w.leaseMatches(x.job,x.rec,999),false)});
test('changed child tail',()=>{const x=fixture();x.rec.child.argv.push('--foreign');assert.equal(!!w.leaseMatches(x.job,x.rec,999),false)});
test('changed child PID',()=>{const x=fixture();assert.equal(!!w.leaseMatches(x.job,x.rec,888),false)});
test('virtual scene bridge writes no metadata',()=>{const loader=w.sceneBridge('/synthetic/staged');const source=loader.load('/synthetic/staged/solution-path-structure-atlas-v2.tsx?scene');assert.ok(source.includes("new MetaFile('owned-source-atlas',false)"));assert.ok(!source.includes('createMeta'));assert.throws(()=>loader.load('/foreign.tsx?scene'))});
test('worker page only public Renderer/exporter and virtual metadata',()=>{const x=fixture();const html=w.workerPage(x.job);assert.ok(html.includes('new Renderer(project)'));assert.ok(html.includes('handleFrame'));assert.ok(html.includes('new MetaFile'));assert.ok(!html.includes('editorBootstrap'));assert.ok(!html.includes('default-settings'));assert.ok(!html.includes('ffmpeg'));assert.ok(html.includes('source-pinned-structural-atlas-v2'))});
test('PNG header finite size',()=>{const b=Buffer.alloc(26);Buffer.from('89504e470d0a1a0a','hex').copy(b);b.write('IHDR',12);b.writeUInt32BE(1080,16);b.writeUInt32BE(900,20);b[25]=6;assert.equal(w.pngDimensions(b).colorType,6);assert.throws(()=>w.pngDimensions(Buffer.alloc(26)))});
console.log(JSON.stringify({passed,SDKImported:false,browserStarted:false,mediaProcessed:false}));
