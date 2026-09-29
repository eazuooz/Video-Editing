// Rebuild index, not an automatic downloader. Existing project metadata remains authoritative.
// Usage: node scripts/build-rebuild-manifests.cjs [slug] [--check]
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {isMedia, git, root} = require('./media-policy.cjs');
const read = f => fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
const json = f => JSON.parse(read(f));
const exists = f => fs.existsSync(path.join(root,f));
const hash = text => crypto.createHash('sha256').update(text).digest('hex');
const canonical = {
  'choice-driven-classics':['projects/choice-driven-classics/script/storyboard.json'],
  'small-window-game-design':['projects/small-window-game-design/production/intro-v3/timeline.json'],
  'let-them-play':['motion-canvas/src/projects/let-them-play/timeline.generated.json','projects/let-them-play/sources/archive64-cuts.json'],
  'visible-rewards':['projects/visible-rewards/sources/gameplay-cuts.v2.json'],
  'game-dev-career':['motion-canvas/src/projects/game-dev-career/timing.generated.json','projects/game-dev-career/production/media-sources-v3.json'],
  'play-first':['motion-canvas/src/projects/play-first/storyboard.generated.json','motion-canvas/src/projects/play-first/assets/broll/media-report.json','projects/play-first/sources/odyssey-cuts.json'],
  'gpt-astra-showcase':['projects/gpt-astra-showcase/planning/edit-plan.json','projects/gpt-astra-showcase/planning/cuts.generated.json'],
  'renderformer-explained':['motion-canvas/src/projects/renderformer-explained/full/narrated/timing.generated.json','projects/renderformer-explained/planning/page-plan.json'],
  'ai-era-cs-fundamentals':['projects/ai-era-cs-fundamentals/sources/selected-footage.json'],
};
// Parse only literal configuration, never execute a project's renderer.
function literalSettings(file) {
  if(!exists(file)) return null;
  const ts=require(path.join(root,'motion-canvas/node_modules/typescript'));
  const source=ts.createSourceFile(file,read(file),ts.ScriptTarget.Latest,true);
  function value(n) {
    if(ts.isAsExpression(n)||ts.isParenthesizedExpression(n))return value(n.expression);
    if(ts.isStringLiteral(n)||ts.isNumericLiteral(n))return ts.isNumericLiteral(n)?+n.text:n.text;
    if(n.kind===ts.SyntaxKind.TrueKeyword)return true;
    if(n.kind===ts.SyntaxKind.FalseKeyword)return false;
    if(n.kind===ts.SyntaxKind.NullKeyword)return null;
    if(ts.isPrefixUnaryExpression(n)&&n.operator===ts.SyntaxKind.MinusToken)return -value(n.operand);
    if(ts.isArrayLiteralExpression(n))return n.elements.map(value);
    if(ts.isObjectLiteralExpression(n))return Object.fromEntries(n.properties.map(p=>{if(!ts.isPropertyAssignment(p))throw Error('not literal');return [p.name.text,value(p.initializer)];}));
    throw Error('not literal');
  }
  const data={};
  for(const statement of source.statements)if(ts.isVariableStatement(statement))for(const d of statement.declarationList.declarations) {
    if(d.initializer)try{data[d.name.text]=value(d.initializer);}catch{/* Dynamic expressions remain in editable source. */}
  }
  return {file,sha256:hash(read(file)),data};
}
function walkValues(value, visit, key='$') {
  if (typeof value==='string') visit(value,key);
  else if(value && typeof value==='object') for(const [k,v] of Object.entries(value)) walkValues(v,visit,key+'.'+k);
}
function walk(dir) {
  if(!exists(dir)) return [];
  return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{
    if(e.isSymbolicLink() || /^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name)) return [];
    const f=dir+'/'+e.name;
    return e.isDirectory()?walk(f):[f];
  });
}
function build(slug, files) {
  const base=`projects/${slug}`, project=json(`${base}/project.json`);
  const selectedPaths=[...new Set([...(canonical[slug]||[]),...['timeline','footageManifest','footageCuts','activeFootage','exampleClips'].map(k=>project.paths?.[k]).filter(f=>typeof f==='string'&&f.endsWith('.json'))])];
  const related=f=>f.startsWith(base+'/')||f.startsWith(`motion-canvas/src/projects/${slug}/`)||f.startsWith(`manim/projects/${slug}/`)||f.startsWith(`shared/output/narration/${slug}/`);
  const own=files.filter(related).filter(f=>!f.includes('/revisions/')&&!f.includes('/archive/')&&!f.endsWith('/rebuild.json'));
  const docs=[...new Set([...own.filter(f=>/\.json$/.test(f)&&/(plan|timeline|storyboard|timing|cuts|sources|footage|media-report|mix.*report|delivery-output)/i.test(f)),...selectedPaths,...Object.values(project.paths||{}).filter(f=>typeof f==='string'&&f.endsWith('.json'))])].filter(exists).sort();
  const documents=docs.map(file=>({file,sha256:hash(read(file)),purpose:selectedPaths.includes(file)?'selected-timeline-or-source-record':'supporting-record-not-necessarily-current',data:json(file)}));
  const scriptPath=project.paths?.script;
  const script=scriptPath&&exists(scriptPath)?json(scriptPath):null;
  const assets=new Map();
  function add(value,origin) {
    const f=value.replaceAll('\\','/');
    if(!isMedia(f) || /^https?:/i.test(f)) return;
    if(!assets.has(f)) assets.set(f,{path:f,references:[],storage:'external-or-regenerate; never Git'});
    const a=assets.get(f);if(!a.references.includes(origin)) a.references.push(origin);
  }
  walkValues(project,(v,k)=>add(v,'project.json'+k));
  for(const d of documents) walkValues(d.data,(v,k)=>add(v,d.file+k));
  // Include relative imports from the editable renderer/mixer, resolved against the code file.
  const code=[...new Set([...own.filter(f=>/\.(tsx?|cjs|py|ps1)$/.test(f)),...(slug==='jump-physics'?files.filter(f=>/^motion-canvas\/src\/(broll\.ts|narration\.ts|narrated\.ts|scenes\/narrated\/|scenes\/jumpPhysics\/)/.test(f)):[])])];
  for(const file of code) {
    const source=read(file);
    for(const m of source.matchAll(/['"`]([^'"`\r\n]+\.(?:mp4|webm|mov|wav|m4a|mp3|ogg|flac))['"`]/gi)) {
      if(m[1].includes('${')) continue;
      const v=m[1].startsWith('.')?path.posix.normalize(path.posix.join(path.posix.dirname(file),m[1])):m[1];add(v,file);
    }
  }
  const selected=documents.filter(d=>d.purpose.startsWith('selected'));
  const rows=selected.flatMap(d=>(Array.isArray(d.data)?d.data:(d.data.scenes||d.data.clips||d.data.pages||[])).map((data,index)=>({record:d.file,index,data})));
  const literalFiles=[`motion-canvas/src/projects/${slug}/timing.ts`,...(slug==='frame-rate-modern-rendering'?['motion-canvas/src/projects/frame-rate-modern-rendering/scenes/broll.tsx']:[]),...(slug==='jump-physics'?['motion-canvas/src/narration.ts','motion-canvas/src/broll.ts']:[])];
  const literalRecords=literalFiles.map(literalSettings).filter(Boolean);
  const timing=literalRecords.find(d=>d.data.SCENE_STARTS)?.data;
  const explicitScenes=selected.find(d=>d.data.scenes?.some(r=>Number.isFinite(r.start)||Number.isFinite(r.startFrame)))?.data.scenes;
  const sceneLayout=explicitScenes||(timing?timing.SCENE_STARTS.map((start,i)=>({id:String(i+1).padStart(2,'0'),startSeconds:start,durationSeconds:timing.SCENE_DURATIONS?.[i]??null,title:timing.SCENE_TITLES?.[i]??null})):literalRecords.find(d=>d.data.SEGMENTS)?.data.SEGMENTS||[]);
  const clipRecords=selected.flatMap(d=>{
    const items=d.data.clips||d.data.scenes||[];
    return items.flatMap((r,i)=>{
      const cuts=r.cuts||r.segments;
      if(cuts)return cuts.map((cut,j)=>({record:d.file,scene:r.scene||r.id||i,index:j,data:cut}));
      return r.source&&('sourceIn' in r)?[{record:d.file,scene:r.id||i,index:0,data:r}]:[];
    });
  });
  for(const d of literalRecords)for(const [i,r] of (d.data.EXAMPLES||d.data.BROLL||[]).entries()) {
    clipRecords.push({record:d.file,scene:r.segment||r.clip||i,index:i,data:r});
    if(r.clip) add(slug==='jump-physics'?`motion-canvas/src/assets/gameplay/${r.clip}.mp4`:`motion-canvas/src/projects/${slug}/assets/gameplay/${r.clip}.mp4`,d.file+' clip slot (check supported extension in renderer)');
  }
  // Preserve native time units and offsets. Never silently treat source offsets as output starts.
  const scripts=files.filter(f=>/\.(cjs|ps1|py)$/.test(f) && (related(f)||f.includes(slug)||(f.startsWith('scripts/')&&read(f).includes(slug)))).filter(exists);
  const sourceDocs=own.filter(f=>/\.(md|txt)$/.test(f)&&/(sources|publishing|README|production|audio)/i.test(f));
  const urls=[...new Set(sourceDocs.flatMap(f=>[...read(f).matchAll(/https?:\/\/[^\s<>"\])]+/g)].map(m=>m[0])))].sort();
  const srt={};for(const key of ['captionsKo','captionsEn','subtitlesKo','subtitlesEn','deliveryCaptionsKo','deliveryCaptionsEn']) {const f=project.paths?.[key];if(f&&exists(f))srt[key]={file:f,sha256:hash(read(f)),cueCount:(read(f).match(/ --> /g)||[]).length};}
  const inventoryFile='docs/media-removal-inventory.json';
  const formerlyTracked=exists(inventoryFile)?json(inventoryFile).currentFiles.filter(f=>related(f.path)||f.path.includes('/'+slug+'/')||f.path.includes('/'+slug+'-')):[];
  return {
    schemaVersion:1,slug,policy:'metadata-only-v1',
    notes:['Media binaries are not in Git, including archives. Keep originals in external storage.','The complete project settings below preserve approval/rights/outro warnings. This file does not grant publication approval.','Native timeline units and source-offset semantics are preserved; consult the named producer script before editing.','TTS regeneration is not byte-identical: revalidate duration, cuts, mix and BOTH SRTs.'],
    projectSettings:project,
    counts:{scriptScenes:Array.isArray(script?.scenes)?script.scenes.length:null,timelineScenes:Array.isArray(sceneLayout)?sceneLayout.length:Object.keys(sceneLayout).length,clipRecords:clipRecords.length,selectedEditRecords:rows.length,referencedMediaFiles:assets.size,formerlyTrackedMediaFiles:formerlyTracked.length},
    sceneScript:script?{file:scriptPath,data:script}:null,
    editRecords:rows,
    sceneLayout,clipRecords,literalSettings:literalRecords,
    structuredRecords:documents,
    editableSourceFiles:code,
    sourceAndRightsDocuments:sourceDocs,referenceUrls:urls,
    subtitles:srt,
    mediaAssets:[...assets.values()].sort((a,b)=>a.path.localeCompare(b.path)),formerlyTrackedMedia:formerlyTracked,
    rebuild:{
      automatic:false,
      prerequisites:['Node dependencies: npm ci --prefix motion-canvas','FFmpeg/ffprobe; Python/Manim where used; Qwen3 model/runtime for fresh TTS','Acquire original footage/music at the recorded paths with valid rights, or restore personal external backup','Private voice reference and original membership identity images must be transferred privately; never fabricate substitutes'],
      productionScripts:scripts,
      scriptRecords:scripts.map(file=>({file,sha256:hash(read(file)),usageHints:read(file).split('\n').filter(l=>/Usage:|usage:|process\.argv|^#.*(?:python|node|powershell)/.test(l)).slice(0,12)})),
      steps:[{order:1,action:'Read source/rights documents, project settings and selected edit records; restore inputs without changing filenames.'},{order:2,action:'Review the CLI/header of the project production scripts listed here. Run their prepare, narration, mix and render stages as documented, not every historical script.'},{order:3,action:'If generating new narration: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-project-narration.ps1 -Project '+slug},{order:4,action:'Validate timeline and current clean/captioned pair, KO/EN SRT, loudness, source rights and membership outro.'},{order:5,action:'node scripts/collect-video-output.cjs '+slug}],
      gaps:[...(!selected.length&&!literalRecords.length?['No selected structured timeline adapter; inspect renderer scripts for exact placement.']:[]),'External backup location is not configured. URLs can disappear; Git cannot recover absent media.','Project-specific render commands are retained in production scripts/README; not all legacy projects have a one-command rebuild.'],
    },
  };
}
function generate(slug,check=false) {
  if(slug&&!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw Error('Invalid project slug');
  const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>exists(`projects/${s}/project.json`)).sort();
  if(slug&&!slugs.includes(slug)) throw Error('Unknown project: '+slug);
  const files=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z']).split('\0').filter(Boolean),...slugs.flatMap(s=>walk(`projects/${s}`)),...slugs.flatMap(s=>walk(`motion-canvas/src/projects/${s}`))])].filter(f=>exists(f)).sort();
  for(const s of slug?[slug]:slugs) {
    const data=build(s,files), target=`projects/${s}/rebuild.json`, text=JSON.stringify(data,null,2)+'\n';
    if(check){if(!exists(target)||read(target)!==text)throw Error('Stale rebuild manifest: '+target);}
    else fs.writeFileSync(path.join(root,target),text);
    console.log(`${s}: ${data.counts.scriptScenes} script scenes; ${data.counts.selectedEditRecords} edit records; ${data.counts.referencedMediaFiles} media references`);
  }
  const index={schemaVersion:1,policy:'metadata-only-v1',projects:slugs.map(s=>({slug:s,manifest:`projects/${s}/rebuild.json`}))};
  if(!check)fs.writeFileSync(path.join(root,'projects/rebuild-index.json'),JSON.stringify(index,null,2)+'\n');
}
module.exports={generate,build};
if(require.main===module){try{generate(process.argv.slice(2).find(a=>!a.startsWith('--')),process.argv.includes('--check'));}catch(e){console.error(e);process.exitCode=1;}}
