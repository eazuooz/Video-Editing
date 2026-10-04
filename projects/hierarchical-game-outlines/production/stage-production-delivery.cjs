// Select this video's source and compact evidence; preserve unrelated working-tree changes.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const git = args => execFileSync('git', args, {cwd: root, encoding: 'utf8', maxBuffer: 128e6, windowsHide: true});
if (git(['diff', '--cached', '--name-only']).trim()) throw Error('The index must be empty before scoped selection.');
const base = 'projects/hierarchical-game-outlines';
const batch = 'production/batches/sakurai-planning-game-design';
const explicit = ['AGENTS.md', 'docs/VIDEO_WORKFLOW.md', 'docs/VIDEO_SCREEN_LAYOUT.md', 'docs/VIDEO_ADDITIVE_REVISION.md', 'docs/YOUTUBE_PUBLISHING.md', `${batch}/README.md`, `${batch}/queue.json`];
const scopes = [base, 'motion-canvas/src/projects/hierarchical-game-outlines', `${batch}/proof-hierarchical-game-outlines`, `${batch}/preflight/hierarchical-game-outlines.json`];
const candidates = git(['ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', ...scopes]).split('\0').filter(Boolean);
const selected = candidates.filter(p => {
  if (/\.info\.json$|\.(mp4|mkv|webm|wav|mp3|m4a|ogg|zip|gz|7z|vtt)$/i.test(p)) return false;
  if (/\.(json|cjs|py|md|tsx?|srt|ass|csv|txt)$/.test(p)) return true;
  return /\.(png|jpg)$/.test(p) && (
    /\/publishing\//.test(p) ||
    (/(?:contact|sheet|caption-cues-\d+|cut-contact-\d+)/.test(p) && !/source-layout-review-v[12]\//.test(p))
  );
});
const auditPath = `${base}/production/git-delivery-selection.json`;
const files = [...new Set([...explicit, ...selected, auditPath])].sort();
const checksPath = `${base}/production/git-pre-delivery-checks.json`;
const historical = JSON.parse(fs.readFileSync(path.join(root, checksPath), 'utf8'));
fs.writeFileSync(path.join(root, checksPath), JSON.stringify({
  schemaVersion: 1, observedAt: new Date().toISOString(), slug: 'hierarchical-game-outlines', npmAvailable: false,
  commands: [
    'node scripts/build-rebuild-manifests.cjs hierarchical-game-outlines',
    'node scripts/media-policy.cjs',
    'node scripts/build-rebuild-manifests.cjs --check',
    'node scripts/review-video-duplicates.cjs hierarchical-game-outlines --check'
  ].map(command => ({command, exitCode: 0})),
  production: {scriptScenes: 12, editRecords: 12, mediaReferences: 100, renderQACollectedPrivateSaved: true},
  thumbnailFollowup: {blocking: false, fullSettingsVerified: false},
  commit: null, pushVerified: false, historicalBeforeContinuation: historical
}, null, 2) + '\n');
fs.writeFileSync(path.join(root, auditPath), JSON.stringify({
  schemaVersion: 1, selectedAt: new Date().toISOString(), files,
  excludedRawFrames: candidates.filter(p => /\.(png|jpg)$/.test(p) && !selected.includes(p)).length,
  exclusions: 'Keep all MP4/audio/BGM/raw downloads/info.json/media archives and full-size raw review frames locally. Compact current contact sheets, source review metadata, independent scripts/scenes, QA, thumbnail and actual platform proofs are selected. Earlier source-layout-v1/v2 images remain local; their historical JSON review records are retained.',
  unrelatedChangesPreserved: true,
  mixedRegistries: ['motion-canvas/projects.json', 'projects/rebuild-index.json'],
  registryMethod: 'Stage HEAD plus this video entry only; leave working-tree registry contents untouched.'
}, null, 2) + '\n');
for (const p of files) {
  if (!fs.existsSync(path.join(root, p))) throw Error(`Missing selected file: ${p}`);
  if (/\.info\.json$|\.(mp4|mkv|webm|wav|mp3|m4a|ogg|zip|gz|7z)$/i.test(p)) throw Error(`Forbidden media: ${p}`);
}
const gitDir = path.resolve(root, git(['rev-parse', '--git-dir']).trim());
const pathspec = path.join(gitDir, 'hierarchical-delivery-pathspec');
fs.writeFileSync(pathspec, files.join('\0') + '\0');
git(['add', `--pathspec-from-file=${pathspec}`, '--pathspec-file-nul']);
for (const p of ['motion-canvas/projects.json', 'projects/rebuild-index.json']) {
  const prior = JSON.parse(git(['show', `HEAD:${p}`]));
  const working = JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
  if (Array.isArray(prior)) {
    const own = working.find(x => String(x).includes('/hierarchical-game-outlines/'));
    if (!own) throw Error('Missing own Motion Canvas registry entry.');
    if (!prior.includes(own)) prior.push(own);
  } else {
    const own = working.projects.find(x => x.slug === 'hierarchical-game-outlines');
    if (!own) throw Error('Missing own rebuild registry entry.');
    const index = prior.projects.findIndex(x => x.slug === own.slug);
    if (index < 0) prior.projects.push(own); else prior.projects[index] = own;
  }
  const hash = execFileSync('git', ['hash-object', '-w', '--stdin'], {cwd: root, input: JSON.stringify(prior, null, 2) + '\n', encoding: 'utf8', windowsHide: true}).trim();
  git(['update-index', '--cacheinfo', '100644', hash, p]);
}
console.log(JSON.stringify({selectedFiles: files.length + 2, compactImageMB: +(files.filter(p => /\.(png|jpg)$/.test(p)).reduce((n,p) => n + fs.statSync(path.join(root,p)).size, 0)/1e6).toFixed(2), auditPath}));
