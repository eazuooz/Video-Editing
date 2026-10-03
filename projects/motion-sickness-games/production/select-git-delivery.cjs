const fs = require('node:fs');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const {isMedia} = require('../../../scripts/media-policy.cjs');
const git = args => cp.execFileSync('git',args,{encoding:'utf8',windowsHide:true,maxBuffer:32e6});
if (git(['diff','--cached','--name-only']).trim()) throw Error('Existing staged work: preserve it and review before selecting this video');
const receipt = JSON.parse(fs.readFileSync('projects/motion-sickness-games/publishing/youtube-upload.json','utf8'));
if (receipt.status !== 'uploaded-private-settings-verified' || receipt.videoId !== 'vFhhQXgdeMs') throw Error('Finish actual private delivery first');
const roots = [
  'projects/motion-sickness-games/',
  'motion-canvas/src/projects/motion-sickness-games/',
  'manim/projects/motion-sickness-games/',
  'shared/output/narration/motion-sickness-games/',
  'production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/'
];
const existingChanges = [
  'motion-canvas/projects.json','projects/rebuild-index.json',
  'motion-canvas/tsconfig.motion-sickness-games.json','motion-canvas/vite.motion-sickness-games.config.ts',
  'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json',
  'production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/content-review.json',
  'production/batches/sakurai-planning-game-design/queue.json',
  'production/batches/sakurai-planning-game-design/README.md'
];
const candidates = git(['ls-files','--others','--exclude-standard','-z']).split('\0').filter(p=>roots.some(r=>p.startsWith(r)));
const imageSelected = p => /(?:contact-|caption-cues-\d+\.jpg$|final-composition-\d+\.jpg$)/.test(p)
  || p.includes('/publishing/proof/') || /\/publishing\/thumbnail(?:-source-frame)?\.png$/.test(p)
  || p.includes('/final-composition-native/') || /\/(?:watch-[^/]+|pws-official-watch)\.png$/.test(p);
const selected = candidates.filter(p => !isMedia(p) && !p.endsWith('.info.json') && (
  /\.(?:json|md|txt|srt|ass|py|cjs|mjs|ps1|ts|tsx|svg|html|css|log)$/.test(p)
  || (/\.(?:png|jpg|jpeg|webp)$/i.test(p) && imageSelected(p))
));
const files = [...new Set([...existingChanges,...selected])].filter(p=>fs.existsSync(p));
if (files.some(p=>isMedia(p) || p.endsWith('.info.json') || p.includes('blank-project-coding') || p.startsWith('scripts/'))) throw Error('Invalid mixed/media selection');
const reportPath = 'projects/motion-sickness-games/production/final-v1/git-selection.json';
const report = {
  at:new Date().toISOString(),selection:'approved-motion-production-and-private-delivery-only',
  mediaCommitted:false,otherUserChangesIncluded:false,rawDownloadInfoExcluded:true,
  nativeQaImages:'All preserved locally; compact contact pages and twenty composition frames selected for Git. Native cue/cut files and their hashes remain in QA/rebuild records.',
  fileCount:files.length+1,totalBytes:files.reduce((s,p)=>s+fs.statSync(p).size,0),
  selected:files.map(path=>({path,bytes:fs.statSync(path).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex')})),
  omittedLocalFiles:candidates.length-selected.length,
  checks:['node scripts/build-rebuild-manifests.cjs motion-sickness-games','node scripts/media-policy.cjs','node scripts/build-rebuild-manifests.cjs --check'],
  checkResults:'all-exit0-before-staging'
};
fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
files.push(reportPath);
for(let i=0;i<files.length;i+=50) git(['add','--',...files.slice(i,i+50)]);
console.log(JSON.stringify({selectedFiles:files.length,totalMiB:report.totalBytes/1048576,omittedLocalFiles:report.omittedLocalFiles,otherUserChangesIncluded:false,mediaCommitted:false}));
