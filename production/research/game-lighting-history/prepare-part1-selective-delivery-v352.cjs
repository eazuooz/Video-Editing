// Exact reviewed04-1 metadata/code closure. No index mutation or media selection.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const R='production/research/game-lighting-history/',P='projects/game-lighting-history-04/production/',Q='projects/game-lighting-history-04-1/',MC='motion-canvas/src/projects/game-lighting-history-04/';
const allowed=[R,P,Q,MC,'production/preflight/game-lighting-history-04-1.json'];
const images=[Q+'publishing/thumbnail-v1.png',Q+'publishing/proof/private-hd-v350.png'];
const selected=new Set(),expanded=new Set(),unchanged=[],stagedPreserved=[],rejected=[];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function git(args){const r=cp.spawnSync('git',args,{encoding:'utf8',windowsHide:true,maxBuffer:32e6});if(r.status)throw Error(r.stderr);return r.stdout}
const head=git(['rev-parse','HEAD']).trim();
const tracked=new Set(git(['ls-tree','-r','--name-only',head]).trim().split('\n'));
const staged=new Set(git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean));
function add(p,depth=0){
 p=p.replaceAll('\\','/');
 if(!allowed.some(a=>p.startsWith(a))||p===R+'checkpoint.json'||p===R+'series-plan.json'||p.includes('/local/')||p.includes('/publishing/proof/')||/\.info\.json$/.test(p)||!/(?:\.(?:json|py|cjs|tsx?|md|txt)|\/\.gitignore)$/.test(p)||!fs.existsSync(p)||!fs.statSync(p).isFile())return;
 const b=fs.readFileSync(p),text=b.toString('utf8').replace(/^\uFEFF/,'');
 let unchangedAtHead=false;
 if(tracked.has(p)){const before=git(['rev-parse',head+':'+p]).trim(),current=git(['hash-object','--path='+p,p]).trim();unchangedAtHead=before===current;}
 if(unchangedAtHead){if(!unchanged.includes(p))unchanged.push(p);if(staged.has(p)&&!stagedPreserved.includes(p))stagedPreserved.push(p);}
 else{if(staged.has(p))throw Error('Changed selected path is externally staged: '+p);selected.add(p);}
 if(expanded.has(p)||depth>4)return;expanded.add(p);
 if(expanded.size>700)throw Error('Closure too broad; inspect before selecting');
 if(p.endsWith('.json')){
  const j=JSON.parse(text);function walk(v){if(typeof v==='string'&&v.length<500&&v.includes('/')&&fs.existsSync(v))add(v,depth+1);else if(v&&typeof v==='object')for(const x of Object.values(v))walk(x)}walk(j);
 }
 if(/\.(py|cjs|tsx?)$/.test(p)){
  for(const m of text.matchAll(/['"](part1-[^'"\n]+\.json)['"]/g))add(P+m[1],depth+1);
  for(const m of text.matchAll(/['"]([^'"\n]+\.(?:py|cjs|ts|tsx))['"]/g)){
   if(m[1].includes('/'))add(m[1],depth+1);else add(path.posix.join(path.posix.dirname(p),m[1]),depth+1);
  }
  for(const m of text.matchAll(/(?:from\s+|import\s*\(|require\s*\()['"](\.[^'"\n]+)['"]/g)){
   const f=path.posix.normalize(path.posix.join(path.posix.dirname(p),m[1]));for(const e of ['', '.ts','.tsx','.cjs','.py'])if(fs.existsSync(f+e)){add(f+e,depth+1);break}
  }
 }
}
for(const f of ['.gitignore','README.md','project.json','rebuild.json','script/narration.ko.json','script/narration.en.json','sources/selected-sources.json','production/timeline.json','production/delivery-output.json','production/collection-index-resume-v349.json','production/resource-before-collection-v348.json','publishing/youtube-upload.json','publishing/upload-description.ko.txt','publishing/upload-description.en.txt','publishing/description.ko.txt','publishing/description.en.txt','publishing/pinned-comment.ko.txt'])add(Q+f);
for(const f of ['part1-final-input-plan-v309.json','part1-caption-layout-v309.json','part1-final-mix-settings-v310.json','part1-final-current-mixed-asr-direct-review-v312.json','part1-semantic-caption-review-v312.json','part1-final-visual-build-v344.json','part1-texture-native-input-direct-review-v344.json','part1-reviewed-pair-build-v345.json','part1-current-final-pixel-review-direct-v347.json','part1-current-final-moving-review-direct-v347.json','part1-final-qa-v347.json','part1-semantic-caption-delivery-map-v348.json','part1-delivery-input-overrides-v348.json'])add(P+f);
for(const f of ['candidate-04-1.json','part1-current-duplicate-direct-review-v351.json','part1-private-observations-v350.json','part1-final-texture-direct-observations-v347.json','record-part1-duplicate-review-v351.py','inspect-part1-duplicate-delta-v350.py','record-part1-private-observations-v350.py','prepare-part1-delivery-project-v348.py','resume-part1-output-index-v349.cjs','seal-part1-current-technical-qa-v347.py','seal-part1-vt-current-mix-review-v312.py','prepare-part1-captions-v309.py','prepare-part1-vt-correction-v309.py','build-part1-vt-correction-media-v310.py','build-part1-texture-preview-v343.py','build-part1-texture-stack-preview-v343d.py','extract-part1-texture-stack-cues-v343e.py','prepare-part1-texture-order-review-v343c.py','build-part1-texture-repaired-visual-v344.py','build-part1-reviewed-pair-v345.py','compare-extract-part1-texture-final-pixels-v346.py','prepare-part1-final-moving-viewer-v346.py','prepare-part1-selective-delivery-v352.cjs','deliver-part1-selective-v353.cjs'])add(R+f);
add('production/preflight/game-lighting-history-04-1.json');
// Raw AX/DOM remain byte-exact locally. Commit a small exact-quote JSON envelope.
add(R+'part1-publishing-ui-evidence-v353.json',5);
for(const p of images){if(!fs.existsSync(p))throw Error('Missing reviewed image');selected.add(p);}
const paths=[...selected].sort();
const ignored=cp.spawnSync('git',['check-ignore','--stdin'],{input:paths.join('\n')+'\n',encoding:'utf8',windowsHide:true});
if(ignored.status>1||ignored.stdout.trim())throw Error('No force-add: '+ignored.stdout+ignored.stderr);
const receipt=JSON.parse(fs.readFileSync(Q+'publishing/youtube-upload.json'));
if(receipt.actualVideoId!=='YOsG939kaBw'||!receipt.privateSaved||!receipt.fullSettingsVerified||!receipt.checksPassed)throw Error('Actual full private settings required');
const record={schemaVersion:1,preparedAt:new Date().toISOString(),actualHeadInspected:head,actualVideoId:receipt.actualVideoId,scope:'Reviewed04-1 current private delivery, exact metadata/code closure; historically identical tracked dependencies reused at actual HEAD. Foreign staged deletions untouched.',paths,essentialImages:images,unchangedAtActualHead:unchanged.sort(),externalStagedIdenticalDependenciesPreserved:stagedPreserved.sort(),sharedPatchFromActualHead:'shared/git-essential-images.json: actual HEAD plus only the two listed reviewed image entries',mediaAdded:0,otherImagesAdded:0,foreignIndexMutation:false,stats:{files:paths.length,bytes:paths.reduce((a,p)=>a+fs.statSync(p).size,0),expanded:expanded.size,unchangedDependencies:unchanged.length,byPrefix:Object.fromEntries(allowed.map(a=>[a,paths.filter(p=>p.startsWith(a)).length]))}};
fs.writeFileSync(R+'part1-selective-paths-v352.json',JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify(record.stats,null,2));console.log(JSON.stringify({images,externallyStagedIdenticalDependenciesPreserved:stagedPreserved.length},null,2));
