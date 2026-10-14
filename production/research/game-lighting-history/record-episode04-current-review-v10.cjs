const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,j)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve existing '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');};
const previous=b+'/episode04-current-duplicate-rereview-v9.json',old=read(previous),s=read(b+'/local/episode04-input-delta-v10.json');
const expected={
 'projects/game-math-bounds-transform-v2/script/narration.ko.json':'9976639079b871bfe5f5b9f8073fa74e020d5351800b9d8f943eb66dfcc759ad',
 'projects/game-math-bounds-transform-v2/script/narration.en.json':'bf11e5472d75116924546a5cebf7b700e69387e616d476a801490c3ae6718cfb',
 'projects/game-math-lines-circles-v2/project.json':'769508d79375451dc3df3df76d7f36cbb5da40dd8a30cc417366e961b933c9a8',
 'projects/game-math-lines-opening-retake-v4/project.json':'299b9f498d23bce5738b0ab8330afc1c86c7a8b20f80f07510c247fc5fdbdd9c',
 'projects/game-math-lines-opening-retake-v4/script/narration.ko.json':'07e2d9d61debfd966384209d2b6cff36678e2c65c786d694210f42a6bd099235',
 'projects/game-math-lines-opening-retake-v4/script/narration.en.json':'6c0db977ff4742aca4d45ffb7f53b08666ad1fddf4350052d2efc52ca7f487f9'
};
if(s.projects.length!==72||s.currentFiles.length!==446||s.delta.length!==6||s.deleted.length)throw Error('Unread inventory change');
for(const d of s.delta)if(expected[d.path]!==d.sha256)throw Error('Unexpected full-read delta '+d.path);
for(const f of s.currentFiles)if(sha(f.path)!==f.sha256)throw Error('Changed after full read '+f.path);
const output=b+'/episode04-current-duplicate-rereview-v10.json';
const reason='Directly read every KO/EN paragraph in the changed bounds-transform scripts and the new lines-opening-retake-v4 scripts, plus both changed/new full manifests. These concern line representations, fraction versus distance, perpendicular bisectors, sphere distance, AABB candidates, affine abs(A)e and empty enclosure space. The Portal2 beam is used as a geometric connection observation, not a light transport or image reconstruction lesson. They remain distinct from episode04 virtual shadow storage, temporal image history, visibility, path sampling/survival, OIT, display transform, RenderDoc frame data and DLSS through5. The retake project explicitly forbids a standalone upload. The other440 fingerprints are unchanged and inherit previous actual full-script and Studio reviews, including the v9 directly observed interpolation IDs. No foreign final pixels/settings/rights are approved or changed.';
const before='production/preflight/game-lighting-history-04.json',archive='projects/game-lighting-history-04/production/duplicate-preflight-before-v10.json';
if(fs.existsSync(path.join(root,archive)))throw Error('Preserve historical preflight');
fs.copyFileSync(path.join(root,before),path.join(root,archive));
write(output,{schemaVersion:1,reviewedAt:new Date().toISOString(),previous:{path:previous,sha256:sha(previous)},inputFiles:s.currentFiles,changedOrNewInputs:s.delta.map(x=>({...x,wholeContentsDirectlyRead:true})),unchangedInputCount:440,changedScripts:2,newInputs:3,deletedInputs:0,studio:old.studio,studioRefresh:old.studioRefresh,comparison:reason,decision:'distinct',foreignFilesModified:false,finalEpisode04Approved:false,historicalPreflight:{path:archive,sha256:sha(archive)}});
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file',b+'/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',output],{cwd:root,stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{cwd:root,stdio:'inherit'});
console.log(JSON.stringify({review:output,wholeChangedScriptsRead:2,newRetakeScriptsRead:2,foreignModified:false}));
