// Record scoped direct reading; do not turn metadata reading into full-script review.
const fs = require('node:fs'), crypto = require('node:crypto'), cp = require('node:child_process');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const snapshotPath = 'production/research/game-lighting-history/local/episode04-duplicate-input-change-snapshot-v16.json';
const snapshot = read(snapshotPath);
const out = 'production/research/game-lighting-history/episode04-current-duplicate-rereview-v16.json';
if (fs.existsSync(out) || snapshot.changes.length !== 33 || snapshot.removed.length) throw Error('Preserve existing review; inspect actual delta');
for (const x of snapshot.currentInputs) if (sha(x.path) !== x.sha256) throw Error('Input changed after reading: ' + x.path);
const reason = 'Retain preceding complete-inventory and actual-channel comparisons. Read the complete eight changed polygon-center/partition/retake/teaching-addition KOEN script files, including all20 addition scenes. They concern weighted area, centers, valid boundaries, convexity and triangulation, with observed game geometry distinguished from implementation claims. Read changed manifest content and editing contracts, including signed-plane distance and barycentric addresses. Read all18 changed current publishing receipts for actual IDs, titles, complete topic descriptions/chapter claims and visibility/schedule/deletion fields; repeated historical UI evidence and bilingual channel footers were not a new whole-body reread. Camera/frustum/projection, mesh/normal/UV and rendering-light lectures remain geometric/photometric prerequisites, not this episode04 temporal reconstruction, virtual allocation, bandwidth, sampling, developer controls and post-process progression. The current motion-sickness replacement mBDd9VzSTkA is now saved/settings verified and scheduled in its receipt; its camera-choice subject is distinct. Foreign40:60/noBGM and user-paused polygon queues stay untouched. CUA browser4/tab22 directly shows our existing episode03 lIDe30dqC28 title, Korean-captioned filename, completed SD/HD and private status; this is current own-upload evidence and does not validate foreign UI settings. New four-game coverage is a separate incomplete production gate. No title/ID-only duplicate inference; no new audio or final pixels approved by this record. Evidence: ' + out;
const record = {
  schemaVersion: 1, reviewedAt: new Date().toISOString(),
  previous: 'production/research/game-lighting-history/episode04-current-duplicate-rereview-v15.json',
  snapshot: {path: snapshotPath, sha256: sha(snapshotPath)}, inputFiles: snapshot.currentInputs,
  changes: snapshot.changes.map(x => ({...x, reviewScope: x.path.includes('/script/') ? 'complete changed script directly read' : x.path.includes('/publishing/') ? 'current ID, complete topic description/chapter claims and status/schedule fields directly read; retained UI history not newly reread' : 'current manifest subject and editing/delivery/publishing contracts directly read'})),
  comparison: reason, decision: 'distinct',
  currentStudio: {method:'CUA browser4/tab22', id:'lIDe30dqC28', title:'레이 트레이싱·루멘은 화면 밖의 빛을 어떻게 찾을까? | BVH·ReSTIR·나나이트', filename:'game-lighting-history-03.captioned.mp4', privacy:'비공개', sdAndHdComplete:true, saveButtonDisabled:true, actualForeignUiInspectedThisPass:false},
  foreignFilesModified: false, fourGameCoverageApproved: false, newTts: 0, newMedia: 0, newGitImages: 0
};
fs.writeFileSync(out, JSON.stringify(record, null, 2) + '\n');
const args = ['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
const checkpointPath = 'production/research/game-lighting-history/checkpoint.json', checkpoint = read(checkpointPath);
checkpoint.episode04DuplicateReviewV16 = {record:out,sha256:sha(out),currentInputCount:snapshot.currentInputs.length,changedInputCount:snapshot.changes.length,decision:'distinct',fourGameCoverageApproved:false};
checkpoint.updatedAt = new Date().toISOString();
fs.writeFileSync(checkpointPath,JSON.stringify(checkpoint,null,2)+'\n');
