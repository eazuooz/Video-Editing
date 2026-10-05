// Records the four full bilingual scripts directly read before this refresh.
const fs = require('node:fs'), cp = require('node:child_process'), crypto = require('node:crypto'), path = require('node:path');
const root = path.resolve(__dirname, '../../../..');
const base = path.relative(root, __dirname).replaceAll('\\', '/');
const report = 'production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const save = (p, d) => fs.writeFileSync(path.join(root, p), JSON.stringify(d, null, 2) + '\n');
const reviewed = {
  'projects/game-math-euler-axis-angle/script/narration.ko.json': '8a5b1eaff35dfe3cea75f1fc763187ef0d43db7705af42166d3bfb008637f501',
  'projects/game-math-euler-axis-angle/script/narration.en.json': '6e4531e4d1fdc8c23d36cf24a35524c1f9e7346b171675ee25ac55ac0f723d3c',
  'projects/game-math-rotation-interpolation/script/narration.ko.json': 'b9dfdfda25dda53e3a332cf29d320aa903734283eb8c080b4502cb30cc5e72eb',
  'projects/game-math-rotation-interpolation/script/narration.en.json': '4516fd7c912432ffc0b261c2f0874f423486709c34420e16e68b1135df8187a3'
};
const old = read(report);
const changed = old.inputFiles.filter(r => !fs.existsSync(path.join(root, r.path)) || hash(r.path) !== r.sha256);
if (changed.some(r => !reviewed[r.path])) throw Error('Another changed input needs direct reading first');
for (const [p, h] of Object.entries(reviewed)) if (hash(p) !== h) throw Error('Reviewed script changed again: ' + p);
const projects = fs.readdirSync(path.join(root, 'projects')).filter(s => s !== 'making-game-sequels' && fs.existsSync(path.join(root, 'projects', s, 'project.json')));
if (projects.some(s => !old.existingProjects.some(r => r.slug === s))) throw Error('New project needs full review');
const conclusion = 'All current26-scene KO and EN Euler scripts and all current26-scene KO and EN interpolation scripts were directly read in full. Euler now includes explicit body-arrow/arm-line observation, separate-excerpt continuity limits and translation-versus-orientation guidance; its subject remains axis/order, intrinsic/extrinsic rotations, gimbal lock, wrapPi, axis-angle/rotation-vector composition and angular velocity. Interpolation includes the relative delta=end*inverse(start), delta^t applied to start, SLERP/NLERP timing/sign rules, representation conversions, Float32 storage/compression caveats and round-trip verification. These mathematical questions do not teach sequel retained core versus changed player decisions or production reuse. Shared observation/check terminology does not make the full substantive lessons duplicates. Previous actual Studio KO/EN and full related-content evidence remains preserved. No foreign script, setting, staging or worker was modified; their40:60/noBGM permission is not applied to this60:40/Nimbus batch.';
const record = {schemaVersion: 1, reviewedAt: new Date().toISOString(), previousDigest: old.inputsDigest,
  changedInputs: Object.entries(reviewed).map(([p, h]) => { const d = read(p); return {path: p, sha256: h, fullContentDirectlyRead: true, scenes: d.scenes.length, paragraphs: d.scenes.reduce((n,s) => n + s.lines.length, 0)}; }),
  conclusion, actualStudioEvidenceRetained: old.studioEvidence, foreignFilesModified: false, foreignFilesCommitted: false};
const recordPath = base + '/current-math-script-rereview-v2.json';
save(recordPath, record);
const content = read(base + '/content-review.json');
content.updatedAt = record.reviewedAt;
content.changedInputsDirectlyReviewed.push({review: recordPath, files: Object.keys(reviewed), conclusion});
save(base + '/content-review.json', content);
for (const args of [ ['scripts/review-video-duplicates.cjs', 'making-game-sequels', '--decision', 'distinct', '--reason', old.contentReview + ' Current full four changed math scripts directly read: ' + recordPath, '--studio-evidence', old.studioEvidence], ['scripts/review-video-duplicates.cjs', 'making-game-sequels', '--check'] ]) {
  const r = cp.spawnSync(process.execPath, args, {cwd: root, encoding: 'utf8', windowsHide: true});
  if (r.status !== 0) throw Error(r.stdout + r.stderr);
}
const current = read(report);
record.currentDigest = current.inputsDigest; record.existingProjects = current.existingProjects.length; record.currentDistinctPassed = true;
save(recordPath, record);
console.log(JSON.stringify({distinct: true, existingProjects: record.existingProjects, fullScripts: record.changedInputs.map(r => ({path: r.path, paragraphs: r.paragraphs}))}));
