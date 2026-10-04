// Read-only inventory. Only the ten completed batch projects are removal candidates.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const git = args => execFileSync('git', args, {cwd: root, encoding: 'utf8', maxBuffer: 128e6, windowsHide: true}).trimEnd();
const completed = ['counting-animation-frames','deconstruct-analyze-rebuild','meaningful-quests',
  'praise-player','responsive-game-feedback','game-writing','picking-sides','motion-sickness-games',
  'hierarchical-game-outlines','game-reward-planning'];
const raster = /\.(png|jpe?g|webp|gif|bmp|tiff?)$/i;
const derived = /(?:^|\/)(?:caption-cues-\d+|contact-\d+|frame-\d+|(?:first|last)-\d+|\d{3,5})\.(?:png|jpe?g)$/i;
const head = git(['rev-parse', 'HEAD']);
const tracked = git(['ls-tree','-r','--name-only','-z',head]).split('\0').filter(f => raster.test(f));
const visible = git(['ls-files','--others','--exclude-standard','-z']).split('\0').filter(f => raster.test(f));
const candidates = tracked.filter(f => completed.some(s => f.startsWith('projects/'+s+'/production/')) && derived.test(f));
function size(file) {try {return fs.statSync(path.join(root, file)).size;} catch {return 0;}}
const records = candidates.map(file => {
  const absolute = path.resolve(root, file);
  if (!absolute.startsWith(root+path.sep) || !fs.existsSync(absolute)) throw Error('Missing local candidate: '+file);
  const row = git(['ls-tree',head,'--',file]).match(/^(\d+) blob ([a-f0-9]+)\t/);
  if (!row) throw Error('Candidate must have an actual HEAD blob: '+file);
  return {path:file, mode:row[1], gitBlob:row[2], bytes:size(file),
    localSha256:crypto.createHash('sha256').update(fs.readFileSync(absolute)).digest('hex'),
    reason:'Reproducible frame or contact sheet in a completed batch production/QA directory; keep the actual local file and its QA records.'};
});
const result = {schemaVersion:1, recordedAt:new Date().toISOString(), headAtAudit:head,
  authority:'영상하나 제작끝나면 푸쉬좀 해줘 엄청쌓였어... jpg나 이미지파일은 필요한것만 나두고 추가 안하기로 했었어 확인해줘',
  trackedRasterBefore:{count:tracked.length,bytes:tracked.reduce((n,f)=>n+size(f),0)},
  visibleUntrackedRasterAfterDefaultIgnore:{count:visible.length,bytes:visible.reduce((n,f)=>n+size(f),0)},
  removalScope:'Only ten completed batch projects production directories and explicit derived frame/contact-sheet names. No original assets, thumbnails, Studio/rights proof or unrelated projects.',
  action:'Remove these paths from the next scoped Git tree only; preserve every local file. History is not rewritten.',
  candidateCount:records.length, candidateBytes:records.reduce((n,r)=>n+r.bytes,0),
  remainingTrackedRaster:tracked.length-records.length,
  localFilesDeleted:false, historyRewritten:false, candidates:records};
const output = 'production/batches/sakurai-planning-game-design/image-git-cleanup-20261005.json';
fs.writeFileSync(path.join(root,output),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,head,candidateCount:result.candidateCount,candidateBytes:result.candidateBytes,
  trackedRasterBefore:result.trackedRasterBefore,remainingTrackedRaster:result.remainingTrackedRaster,
  visibleUntrackedRasterAfterDefaultIgnore:result.visibleUntrackedRasterAfterDefaultIgnore,localFilesDeleted:false}));
