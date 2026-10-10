// Explicit reviewed polar revision only. The external Git index is never written.
// Usage: node .../deliver-reviewed-polar-v3.cjs --prepare | --stage-only | --deliver
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const slug = 'game-math-polar-3d';
const base = `projects/${slug}`;
const rev = `${base}/revision-teaching-clarity-v1`;
const batch = 'production/batches/unpublished-teaching-clarity-revision';
const gitBin = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const envBase = {...process.env, PATH: path.dirname(gitBin) + path.delimiter + process.env.PATH};
const readText = f => fs.readFileSync(path.join(root, f), 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
const read = f => JSON.parse(readText(f));
const save = (f, value) => fs.writeFileSync(path.join(root, f), JSON.stringify(value, null, 2) + '\n');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function run(command, args, env = envBase, input) {
  const r = cp.spawnSync(command, args, {cwd: root, env, input, encoding: 'utf8', windowsHide: true, maxBuffer: 256e6});
  if (r.status !== 0) throw Error(command + ' ' + args.join(' ') + '\n' + r.stdout + '\n' + r.stderr);
  return r.stdout.trimEnd();
}
const git = (args, env = envBase, input) => run(gitBin, args, env, input);
function walk(dir) {
  if (!fs.existsSync(path.join(root, dir))) return [];
  return fs.readdirSync(path.join(root, dir), {withFileTypes: true}).sort((a,b) => a.name.localeCompare(b.name)).flatMap(e => {
    if (e.isSymbolicLink() || /^(?:node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks|__pycache__)$/.test(e.name)) return [];
    const f = dir + '/' + e.name;
    return e.isDirectory() ? walk(f) : [f];
  });
}
const selection = read(`${rev}/publishing/git-source-selection-v3.json`);
const planPath = `${rev}/publishing/git-stage-paths-v3.json`;
const proofPath = `${rev}/publishing/private-delivery-git-verification-v3.json`;
const excludedProofs = new Set([proofPath, `${rev}/publishing/schedule-evidence-git-verification-v3.json`, `${rev}/publishing/final-handoff-git-verification-v3.json`]);
const imageReviewPath = `${rev}/publishing/private-settings-direct-review-v3.json`;
const images = fs.existsSync(path.join(root, imageReviewPath)) ? read(imageReviewPath).minimalReviewedImages || [] : [];
const shared = [...Object.keys(selection.sharedFilesRequireOwnedOnlyMergeFromActualHead), ...images.length ? ['.gitignore', 'shared/git-essential-images.json'] : []];
const textFile = f => /\.(?:json|md|py|cjs|tsx?|meta|srt|ass|csv|html)$/.test(f) || /\/upload-description\.(?:ko|en)\.txt$/.test(f);
const forbidden = f => /(?:^|\/)(?:raw|assets|frames|boards|__pycache__|delivery-history|node_modules|\.git)\//.test(f) || /\.ax\.txt$|\.info\.json$/.test(f);
const baselinePaths = selection.selectedSourcePaths.filter(f => !f.startsWith(rev + '/') && !f.startsWith(batch + '/'));
const files = [...new Set([...walk(rev), ...walk(batch)].filter(f => textFile(f) && !forbidden(f) && !excludedProofs.has(f)).concat(baselinePaths, `${rev}/publishing/git-source-selection-v3.json`, planPath, images.map(e => e.path)))].sort();
const allowedRoots = [rev, batch];
for (const f of files) {
  if (!allowedRoots.some(d => f.startsWith(d + '/')) && !baselinePaths.includes(f)) throw Error('Foreign selected path ' + f);
  if (/\.(?:png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f) && !images.some(e => e.path === f)) throw Error('Unreviewed raster ' + f);
  if (/\.(?:mp4|wav|m4a|aac|mp3|webm|mkv|zip|7z|gz)$/i.test(f)) throw Error('Media selected ' + f);
}
for (const e of images) {
  if (!e.path.startsWith(rev + '/publishing/') || !e.reviewedAt || !e.reason || e.sha256 !== sha(fs.readFileSync(path.join(root, e.path)))) throw Error('Essential image changed or unreviewed ' + e.path);
}
if (process.argv.includes('--prepare')) {
  save(planPath, {schemaVersion: 3, slug, actualVideoId: '2kNMDlrwdU8', actualHeadAtPreparation: git(['rev-parse','HEAD']),
    preparedAt: new Date().toISOString(), selectedPaths: files, sharedPaths: shared,
    reviewedEssentialImages: images, staged: false, committed: false,
    externalIndexPolicy: 'Preserve every external byte and entry; do not reset/sync concurrent staged content.',
    sharedPolicy: 'Merge only the two owned rules/sections per file and the exact approved image records into actual HEAD.'});
  console.log(JSON.stringify({prepared: true, explicitPaths: files.length, sharedOwnedOnly: shared.length, reviewedImages: images.length}));
  process.exit(0);
}
if (!process.argv.includes('--stage-only') && !process.argv.includes('--deliver')) throw Error('Choose --prepare, --stage-only or --deliver');
const receipt = read(`${rev}/publishing/youtube-upload-v3.json`);
const pixels = read(`${rev}/final-pixel-direct-review-v2.json`);
const collection = read(`${rev}/collection-private-preflight-v3.json`);
const flow = read(`${rev}/final-flow-playback-direct-review-v3.json`);
if (receipt.actualVideoId !== '2kNMDlrwdU8' || !receipt.uploaded || !receipt.savedPrivate || !receipt.fullSettingsVerified || !receipt.checksVerified || !receipt.ccOffPixelsVerified) throw Error('Complete actual private settings and processing required');
if (!pixels.allListedSamplesDirectlyRead || !pixels.allFinalCueCutPixelsApproved || pixels.unresolved.length || pixels.sourceSha256 !== receipt.video.sha256) throw Error('Current moving pixel approval required');
if (!collection.sourceAndOutputAllFourHashesEqual || collection.actualCollectExitCode !== 0 || !flow) throw Error('Current collection/continuous flow record required');
if (!fs.existsSync(path.join(root, imageReviewPath))) throw Error('Publishing direct review required');
const plan = read(planPath);
if (JSON.stringify(plan.selectedPaths) !== JSON.stringify(files) || JSON.stringify(plan.sharedPaths) !== JSON.stringify(shared)) throw Error('Selection changed; prepare current explicit paths before staging');
const parent = git(['rev-parse','HEAD']);
const externalIndex = path.resolve(root, git(['rev-parse','--git-path','index']));
const beforeBytes = fs.readFileSync(externalIndex);
const beforeEntries = git(['ls-files','--stage','-z']);
const stagedForeign = git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean);
const dir = fs.mkdtempSync(path.join(root, '.git', 'polar-teaching-v3-'));
const env = {...envBase, GIT_INDEX_FILE: path.join(dir, 'index')};
function externalUnchanged() {
  if (sha(fs.readFileSync(externalIndex)) !== sha(beforeBytes) || git(['ls-files','--stage','-z']) !== beforeEntries) throw Error('Concurrent external index changed; preserve it and inspect before continuing');
}
function section(text, prefix) {
  const lines = text.split('\n');
  const start = lines.findIndex(l => l.startsWith(prefix));
  if (start < 0) throw Error('Owned section absent ' + prefix);
  let end = start + 1;
  while (end < lines.length && !lines[end].startsWith('## ') && !lines[end].startsWith('2026-10-02 사용자 지시:')) end++;
  return lines.slice(start, end).join('\n').trimEnd();
}
function mergeOwnedText(f, head) {
  const current = readText(f);
  const prefixes = selection.sharedFilesRequireOwnedOnlyMergeFromActualHead[f];
  let merged = head.replace(/\r\n/g, '\n');
  for (const prefix of prefixes) {
    const paragraph = !prefix.startsWith('## ');
    const addition = paragraph ? current.split('\n').find(l => l.startsWith(prefix)) : section(current, prefix);
    if (!addition) throw Error('Owned addition missing ' + f + ': ' + prefix);
    const existing = paragraph ? merged.split('\n').find(l => l.startsWith(prefix)) : merged.split('\n').some(l => l.startsWith(prefix)) ? section(merged, prefix) : null;
    if (existing) merged = merged.replace(existing, addition);
    else {
      const afterHeading = merged.indexOf('\n');
      merged = merged.slice(0, afterHeading + 1) + '\n' + addition + '\n' + merged.slice(afterHeading + 1);
    }
  }
  return merged.trimEnd() + '\n';
}
function mergeShared(f, head) {
  if (selection.sharedFilesRequireOwnedOnlyMergeFromActualHead[f]) return mergeOwnedText(f, head);
  if (f === '.gitignore') {
    let result = head.trimEnd();
    for (const e of images) if (!result.split(/\r?\n/).includes('!' + e.path)) result += '\n!' + e.path;
    return result + '\n';
  }
  const registry = JSON.parse(head);
  for (const e of images) {
    if (!registry.allowedPurposes.includes(e.purpose)) throw Error('Unknown essential purpose ' + e.purpose);
    const existing = registry.entries.find(x => x.path === e.path);
    if (existing && existing.sha256 !== e.sha256) throw Error('Conflicting essential raster approval');
    if (!existing) registry.entries.push(e);
  }
  return JSON.stringify(registry, null, 2) + '\n';
}
git(['read-tree', parent], env);
// Refresh this manifest only. Do not overwrite the shared rebuild index or other projects.
const slugs = fs.readdirSync(path.join(root, 'projects')).filter(s => fs.existsSync(path.join(root, 'projects', s, 'project.json'))).sort();
const rebuildFiles = [...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'], env).split('\0').filter(Boolean), ...slugs.flatMap(s => walk(`projects/${s}`)), ...slugs.flatMap(s => walk(`motion-canvas/src/projects/${s}`))])].filter(f => fs.existsSync(path.join(root, f))).sort();
save(`${base}/rebuild.json`, require(path.join(root, 'scripts/build-rebuild-manifests.cjs')).build(slug, rebuildFiles));
for (let i = 0; i < files.length; i += 15) git(['add','--',...files.slice(i, i + 15)], env);
const expectedShared = {};
for (const f of shared) {
  const blob = git(['hash-object','-w','--stdin'], env, mergeShared(f, git(['show', parent + ':' + f])));
  git(['update-index','--add','--cacheinfo','100644',blob,f], env);
  expectedShared[f] = blob;
}
const allowed = new Set([...files, ...shared]);
const changes = git(['diff','--cached','--name-status','-z',parent], env).split('\0').filter(Boolean);
const rows = [];
for (let i = 0; i < changes.length; i += 2) rows.push({status: changes[i], path: changes[i + 1]});
if (rows.some(r => !allowed.has(r.path) || !['A','M'].includes(r.status))) throw Error('Unexpected deletion/rename or foreign path');
const stagedMap = new Map(git(['ls-files','--stage','-z'], env).split('\0').filter(Boolean).map(l => {const [m,f] = l.split('\t'); return [f,m.split(' ')[1]];}));
const blobs = git(['hash-object','--stdin-paths'], env, files.join('\n') + '\n').split(/\r?\n/);
if (blobs.length !== files.length) throw Error('Explicit blob count differs');
files.forEach((f,i) => {if (stagedMap.get(f) !== blobs[i]) throw Error('Source staged blob differs ' + f);});
shared.forEach(f => {if (stagedMap.get(f) !== expectedShared[f]) throw Error('Owned merge staged blob differs ' + f);});
const checks = {
  whitespace: git(['diff','--cached','--check',parent], env),
  media: run(process.execPath, ['scripts/media-policy.cjs'], env),
  currentPolarRebuild: run(process.execPath, ['scripts/build-rebuild-manifests.cjs',slug,'--check'], env),
};
externalUnchanged();
if (git(['rev-parse','HEAD']) !== parent) throw Error('HEAD advanced; no commit created');
const proof = {schemaVersion: 3, slug, actualVideoId: receipt.actualVideoId, parent, temporaryIndex: env.GIT_INDEX_FILE,
  selectedPaths: files, changedPaths: rows, ownedSharedBlobs: expectedShared, checks,
  allFinalStagedBlobsVerified: true, externalStagedOverlapPaths: stagedForeign.filter(f => files.includes(f)),
  externalIndexSha256Before: sha(beforeBytes), externalIndexUnchanged: true,
  reviewedEssentialImages: images, mediaAdded: 0, recordedAt: new Date().toISOString(), pushed: false};
fs.writeFileSync(path.join(dir, 'external-index-before.bin'), beforeBytes);
fs.writeFileSync(path.join(dir, 'stage-verification.json'), JSON.stringify(proof, null, 2) + '\n');
if (process.argv.includes('--stage-only')) {
  console.log(JSON.stringify({stageOnly: true, changedPaths: rows.length, index: env.GIT_INDEX_FILE, checks}));
  process.exit(0);
}
const tree = git(['write-tree'], env);
const commit = git(['commit-tree',tree,'-p',parent], env, 'Deliver polar lesson with clear gameplay annotations and unpublished teaching rules\n');
externalUnchanged();
git(['update-ref','HEAD',commit,parent]);
Object.assign(proof, {commit, localCommit: commit});
save(proofPath, proof);
try {git(['push','origin',commit + ':refs/heads/main']);}
catch (error) {proof.pushFailure = {at: new Date().toISOString(), message: error.message}; save(proofPath, proof); throw error;}
const local = git(['rev-parse','HEAD']);
const remote = git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if (local !== commit || remote !== commit) throw Error('Actual local/remote differs; preserve commit and inspect concurrent delivery');
const finalMap = new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l => {const [m,f] = l.split('\t');return [f,m.split(' ')[2]];}));
for (const f of [...files, ...shared]) if (finalMap.get(f) !== stagedMap.get(f)) throw Error('Actual final remote blob differs ' + f);
externalUnchanged();
Object.assign(proof, {pushed: true, remoteCommit: remote, exactLocalRemoteMatch: true, allRemoteBlobsVerified: true,
  verifiedBlobCount: files.length + shared.length, externalIndexSha256After: sha(fs.readFileSync(externalIndex)), verifiedAt: new Date().toISOString()});
save(proofPath, proof);
console.log(JSON.stringify({commit, remote, changedPaths: rows.length, verifiedBlobs: proof.verifiedBlobCount,
  essentialImages: images.length, mediaAdded: 0, externalIndexUnchanged: true, pushed: true}));
