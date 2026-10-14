const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p), 'utf8')).digest('hex');
const snapshotPath = 'production/research/game-lighting-history/local/episode04-duplicate-input-change-snapshot-v1.json';
const snapshot = read(snapshotPath);
const output = 'production/research/game-lighting-history/episode04-current-duplicate-rereview-v1.json';
if (fs.existsSync(path.join(root, output))) throw Error('Preserve existing review; inspect before preparing a new version');
if (snapshot.removed.length) throw Error('Removed input requires direct review');
for (const input of snapshot.currentInputs) if (sha(input.path) !== input.sha256) throw Error('Input changed after inspection: ' + input.path);
const priorPaths = ['production/research/game-lighting-history/current-duplicate-rereview-v9.json',
  'production/research/game-lighting-history/current-duplicate-rereview-v11.json'];
const evidence = priorPaths.flatMap(p => {
  const record = read(p);
  return [...(record.newFullRead || []), ...(record.incrementalFullReread || [])]
    .filter(f => f.fullBodyDirectlyRead).map(f => ({...f, retainedReviewPath: p}));
});
const retainedFullReads = snapshot.changes.map(change => {
  const proof = evidence.find(e => e.path === change.path && e.sha256 === change.sha256);
  if (!proof) throw Error('Current changed input lacks directly read matching evidence: ' + change.path);
  return {...change, retainedReviewPath: proof.retainedReviewPath, fullBodyReadAtMatchingHashRetained: true};
});
const reason = 'All current changed inputs are matched to retained full-body reviews: character-parameters37 KO/37 EN paragraphs, source decisions, outline, current manifest/README and actual nic5Sp6dylQ receipt; scores current manifest/README preserve names, units, quantities and action comparisons. These design questions differ from episode04 virtual-shadow pages/cache, temporal reconstruction, visibility attributes, path-sample weighting, Ray Reconstruction, MegaLights, transparency/hair, DLSS5 boundaries, post-processing and captured-resource dependencies. Current episode04 all87 original KO paragraphs and full14-chapter outline directly read; they preserve complete calculations and chronology. Prior full PBR, RenderDoc and transparency overlap is acknowledged; the new episode compares algorithm responsibilities and failures across a historical pipeline rather than repeating those standalone lessons. Standalone RenderFormer/NeRF are excluded. Review evidence: ' + output;
const record = {schemaVersion: 1, reviewedAt: new Date().toISOString(), candidate: 'production/research/game-lighting-history/candidate-04.json',
  snapshotPath, snapshotSha256: sha(snapshotPath), files: snapshot.currentInputs.length, changes: retainedFullReads,
  priorFullInventoryReview: 'production/research/game-lighting-history/current-series-duplicate-review.json',
  priorMatchingReviews: priorPaths.map(p => ({path: p, sha256: sha(p)})),
  currentOwnKo: {path: 'projects/game-lighting-history-04/script/narration.ko.json', sha256: sha('projects/game-lighting-history-04/script/narration.ko.json'), paragraphs: 87, fullBodyDirectlyRead: true},
  studio: {observedAt: new Date().toISOString(), method: 'CUA current browser4/tab4 actual26 rendering-filter title links, IDs, dates and privacy directly read; stale checkbox labels excluded. Retain earlier direct nic5Sp6dylQ full description/chapters/filename and scheduled-state inspection at the matching current receipt hash.',
    query: '렌', results: 26, actualHistorySeriesUploadObserved: false, currentMathScheduledIds: ['nalAZHtEtw0','xnIA0EAJtiA','PuXZUArWFko','c96qTnlHBVU','CbX6KQ-_zsc','-19ngvEqhao'],
    relatedPublishedIds: ['_Zz5JF5WGj4','5zY45cmbSlQ','eiT2GlSeSeU','qfkL1VjnYo8','tHu9Gp580J0','Wry5ltdrDQI','ETDgyFRyT_8'], settingsChanged: false},
  comparison: reason, decision: 'distinct', foreignFilesModified: false, generatedAudioOrScenes: false};
fs.writeFileSync(path.join(root, output), JSON.stringify(record, null, 2) + '\n');
const args = ['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath, [...args,'--decision','distinct','--reason',reason,'--studio-evidence',output], {cwd: root, stdio: 'inherit'});
cp.execFileSync(process.execPath, [...args,'--check'], {cwd: root, stdio: 'inherit'});
