// Only the observed completed-pixel/status manifest delta; every changed body read.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const hash=text=>crypto.createHash('sha256').update(text).digest('hex');
const prior=JSON.parse(fs.readFileSync('production/preflight/game-lighting-history-04.json','utf8'));
const target='projects/game-math-polygon-partition-v2/project.json',expected='4490df725e90ef06195b2557327aeeac98c057414de719525f391ac776b83dfa';
const changed=prior.inputFiles.filter(f=>fs.existsSync(f.path)&&hash(fs.readFileSync(f.path,'utf8'))!==f.sha256);
if(changed.length!==1||changed[0].path!==target||hash(fs.readFileSync(target,'utf8'))!==expected||prior.inputFiles.some(f=>!fs.existsSync(f.path)))throw Error('Inspect new full delta before review');
const out='production/research/game-lighting-history/episode04-current-duplicate-rereview-v71.json';if(fs.existsSync(out))throw Error('Preserve earlier review');
const reason='Complete current polygon-partition manifest was directly read after v68. It now records current pixel/source review, reviewed-local-render and private-upload-pending; the same L-shaped concave partition, empty-space preservation, fan/ear/validity contracts and paired scripts remain. No rendering04 image reconstruction/exposure/focus/frame-resource overlap was added. Preserve its white40:60/noBGM contract, previous83-project body comparison, v68 full paired paragraphs and actual Studio lIDe30dqC28 private observation. Our111 original paragraphs/PCM and five framing takes remain unchanged. New guided37 are additions to display-stage and frame-inspection teaching, with current final QA/four-game/private gates false. Evidence: '+out;
fs.writeFileSync(out,JSON.stringify({reviewedAt:new Date().toISOString(),previous:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',changes:changed.map(f=>({path:f.path,previousSha256:f.sha256,sha256:expected,completeCurrentBodyDirectlyRead:true})),decision:'distinct',comparison:reason,actualStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',foreignFilesModified:false},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
