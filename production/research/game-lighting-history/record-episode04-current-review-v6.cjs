const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const output=b+'/episode04-current-duplicate-rereview-v6.json';
if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing review');
const snapPath=b+'/local/episode04-current-inputs-v6.json',snap=read(snapPath);
const additionallyRead={
 'projects/game-math-interpolation-paths-v2/project.json':'f3d1784ce34e760172c6f9ca7663406d6ec0a8094b484b2d81a8d3173444a5b7',
 'projects/game-math-interpolation-paths-v2/publishing/youtube-upload.json':'bf56ffdf9c34c59827368692fea5491634929505e421efa9ba2b728c69a120c1'};
const expected=new Map(snap.files.map(f=>[f.path,additionallyRead[f.path]||f.sha256]));
const current=[];
for(const entry of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 const base='projects/'+entry.name,mp=base+'/project.json';
 if(!entry.isDirectory()||entry.name==='game-lighting-history-04'||!fs.existsSync(path.join(root,mp)))continue;
 const m=read(mp),files=new Set([mp,base+'/script/narration.ko.json',m.paths?.script,base+'/script/narration.en.json',m.paths?.scriptEn,m.paths?.scriptEnglish,base+'/planning/outline.md',base+'/sources/SOURCES.md',base+'/README.md',base+'/publishing/youtube-upload.json',m.publishing?.receipt].filter(Boolean));
 for(const p of files)if(fs.existsSync(path.join(root,p))){const h=sha(p);if(expected.get(p)!==h)throw Error('Unread new input: '+p);current.push({path:p,sha256:h});}
}
if(current.length!==expected.size)throw Error('Inventory changed');
const changed=[...snap.changes.map(c=>({...c,sha256:sha(c.path)})),...Object.entries(additionallyRead).map(([p,h])=>({path:p,sha256:h,previousSha256:snap.files.find(f=>f.path===p).sha256}))];
const comparisons=[
 {slug:'game-math-lines-bounds-teaching-additions-v2',scenes:20,paragraphsPerLanguage:59,fullKoEnDirectlyRead:true,question:'Prerequisites and bridges for segments, circles, equal-distance planes and transformed bounds.'},
 {slug:'game-math-lines-circles-v2',scenes:18,paragraphsPerLanguage:78,fullKoEnDirectlyRead:true,question:'How two endpoints define a connection and positions on it, and how to find an equal-distance position.'},
 {slug:'game-math-bounds-transform-v2',scenes:24,paragraphsPerLanguage:111,fullKoEnDirectlyRead:true,question:'How to enclose a target with a sphere/AABB and update its bounds after an affine transform.'}];
const reason='Current440 input files matched to retained full inventory and direct incremental reads. All6 new KOEN scripts read in full: 59+78+111=248 paragraphs per language, with numeric examples, Portal2 beams/grapple endpoints, circle/sphere membership, AABB overlap and c′=Ac+t/e′=|A|e. New manifests read using full object comparison against the already-read baseline, including every changed field. These geometry questions differ from episode04 shadow-page residency, temporal/attribute reconstruction, path-probability weighting, transparency, frame generation, post-processing and resource dependencies. Entire updated rotation-conversion and interpolation manifests/receipts also read; same original scripts, new private IDs n-k7zwaSum0 and _SzbJR4R6OI do not introduce history-pipeline coverage. Episode03 delivered14-chapter105-paragraph current KOEN and receipt are retained matching full-read evidence; episode04 continues from those ray/BVH/Lumen/Nanite responsibilities rather than repeating them. Prior PBR/RenderDoc/transparency overlap is explicitly acknowledged and used as prerequisite context. Standalone RenderFormer/NeRF excluded. Own87 KOEN and11 prerequisite insertions retained. Current CUA rendering-filter26 rows and known overlapping full scripts/descriptions compared; title counts alone do not establish distinctness. Evidence '+output;
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),candidate:b+'/candidate-04.json',snapshot:{path:snapPath,sha256:sha(snapPath)},inputFiles:current,changedInputs:changed.map(c=>({...c,fullContentDirectlyRead:true,method:c.path.endsWith('/project.json')&&comparisons.some(x=>c.path.includes('/'+x.slug+'/'))?'complete recursive structural comparison with previously read baseline; all differing keys directly read':'full current body directly read or retained matching episode03 delivery read'})),newScriptComparisons:comparisons,retainedFullInventory:'production/preflight/game-lighting-history-03.json',ownKo:{path:'projects/game-lighting-history-04/script/narration.ko.json',sha256:sha('projects/game-lighting-history-04/script/narration.ko.json'),paragraphs:87},ownEn:{path:'projects/game-lighting-history-04/script/narration.en.json',sha256:sha('projects/game-lighting-history-04/script/narration.en.json'),paragraphs:87},studio:{observedAt:new Date().toISOString(),method:'CUA browser4/tab4 actual26 rendering-filter rows, visible title/ID/date/privacy; prior full overlapping descriptions retained.',query:'렌',rowCount:26,knownRelatedIds:['_Zz5JF5WGj4','5zY45cmbSlQ','eiT2GlSeSeU','qfkL1VjnYo8','tHu9Gp580J0','Wry5ltdrDQI','ETDgyFRyT_8'],episode03DeliveredId:'lIDe30dqC28',latestForeignReceiptsRead:['n-k7zwaSum0','_SzbJR4R6OI'],foreignPlatformSettingsPersonallyReverified:false,settingsChanged:false},comparison:reason,decision:'distinct',foreignFilesModified:false,newAudioOrRaster:false,finalEpisode04Approved:false};
write(output,record);
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file',b+'/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',output],{cwd:root,stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{cwd:root,stdio:'inherit'});
