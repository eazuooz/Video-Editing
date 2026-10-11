// Prepare a reviewable exact path list, without touching either Git index.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const prefix='production/research/game-lighting-history/',base='projects/game-lighting-history-04-3/',parent='projects/game-lighting-history-04/';
const allowed=[prefix,parent,base,'motion-canvas/src/projects/game-lighting-history-04/'];
const selected=new Set(),ignored=[],outside=[];
const media=/\.(?:mp4|m4a|wav|aac|mp3|webm|mov|zip|7z|gz|png|jpe?g|webp|gif|bmp|tiff?)$/i;
const images=[base+'publishing/thumbnail-v1.png',base+'publishing/proof/private-hd-v164.jpg'];
function add(p,expand=true){
 p=p.replaceAll('\\','/');if(!allowed.some(a=>p.startsWith(a))||p.includes('/local/')||/\.info\.json$/.test(p)||media.test(p))return;
 if(!/\.(json|py|cjs|tsx?|md|txt)$/.test(p)&&!p.endsWith('/.gitignore'))return;
 if(!fs.existsSync(p)||!fs.statSync(p).isFile()||selected.has(p))return;
 selected.add(p);if(selected.size>900)throw Error('Dependency closure too broad; inspect');
 const text=fs.readFileSync(p,'utf8');
 if(expand&&p.endsWith('.json')){
  const j=JSON.parse(text.replace(/^\uFEFF/,'')); const walk=v=>{if(typeof v==='string'&&v.length<500&&v.includes('/')&&fs.existsSync(v))add(v,false);else if(v&&typeof v==='object')for(const x of Object.values(v))walk(x)};walk(j);
 }
 if(/\.(tsx?|py|cjs)$/.test(p)){
  for(const m of text.matchAll(/(?:from\s+|import\s*\(|require\s*\()['"](\.[^'"\n]+)['"]/g)){
   let f=path.posix.normalize(path.posix.join(path.posix.dirname(p),m[1]));for(const suffix of ['', '.ts','.tsx','.cjs','.py'])if(fs.existsSync(f+suffix)){add(f+suffix);break}
  }
  for(const m of text.matchAll(/['"]([^'"\n]+\.(?:py|cjs|ts|tsx))['"]/g))if(allowed.some(a=>m[1].startsWith(a)))add(m[1]);
 }
}
for(const p of ['.gitignore','README.md','project.json','rebuild.json','production/timeline.json','production/delivery-output.json','script/narration.ko.json','script/narration.en.json','sources/selected-sources.json','publishing/youtube-upload.json','publishing/description.ko.txt','publishing/description.en.txt','publishing/pinned-comment.ko.txt'])add(base+p);
for(const n of fs.readdirSync(parent+'production').filter(n=>n.startsWith('part3-')&&n.endsWith('.json')))add(parent+'production/'+n);
for(const n of fs.readdirSync(prefix).filter(n=>n.includes('part3-')&&/\.(py|cjs)$/.test(n)))add(prefix+n);
for(const n of ['review-media-common-v15.py','candidate-04-3.json','prepare-part3-selective-delivery-v165.cjs'])add(prefix+n);
const spatial='motion-canvas/src/projects/game-lighting-history-04/spatial/';
for(const n of fs.readdirSync(spatial).filter(n=>/^(?:clean-input-original-(?:22(?:p|r|rb)?-\d+|conclusion-\d+)-v5|clean-input-(?:18-pre-generated-frame-count|20-pre-display-transform|23-pre-capture-dataflow)-v5|guided-.*-v(?:132|137|140)|physical-framing-part3-overview-v59|postprocess-model-v4)\.tsx$/.test(n)))add(spatial+n);
add(prefix+'part3-current-duplicate-direct-review-v153.json',false);
add(prefix+'checkpoint.json',false);
for(const p of images){if(!fs.existsSync(p))throw Error('Missing essential image '+p);selected.add(p)}
const paths=[...selected].sort();
const check=cp.spawnSync('git',['check-ignore','--stdin'],{input:paths.join('\n')+'\n',encoding:'utf8',windowsHide:true});
if(check.status>1)throw Error(check.stderr);const forbidden=check.stdout.trim().split('\n').filter(Boolean);if(forbidden.length)throw Error('Ignored files must not be force-added:\n'+forbidden.join('\n'));
const receipt=JSON.parse(fs.readFileSync(base+'publishing/youtube-upload.json'));if(!receipt.privateSaved||!receipt.fullSettingsVerified||receipt.actualVideoId!=='ydW9Glmh0nM')throw Error('Actual delivery required');
const record={schemaVersion:1,preparedAt:new Date().toISOString(),scope:'Reviewed04-3 private delivery and its owned metadata/code dependencies only; completed/historical records preserve their original status.',actualVideoId:receipt.actualVideoId,paths,essentialImages:images,mediaAdded:0,foreignSharedPatchOnly:'shared/git-essential-images.json: actual HEAD plus these two exact reviewed image entries',foreignIndexMutation:false,stats:{files:paths.length,bytes:paths.reduce((a,p)=>a+fs.statSync(p).size,0),byPrefix:Object.fromEntries(allowed.map(a=>[a,paths.filter(p=>p.startsWith(a)).length]))}};
fs.writeFileSync(prefix+'part3-selective-paths-v165.json',JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify(record.stats,null,2));console.log('Essential images: '+images.join(', '));console.log('Other image/media additions:0. External index unchanged. Review exact paths before guarded delivery.');
