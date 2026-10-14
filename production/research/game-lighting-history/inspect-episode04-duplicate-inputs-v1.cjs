const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p), 'utf8')).digest('hex');
const previous = read('production/preflight/game-lighting-history-04.json');
const old = new Map(previous.inputFiles.map(f => [f.path, f.sha256]));
const current = [];
for (const entry of fs.readdirSync(path.join(root, 'projects'), {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name))) {
  const base = 'projects/' + entry.name, manifestPath = base + '/project.json';
  if (!entry.isDirectory() || entry.name === 'game-lighting-history-04' || !fs.existsSync(path.join(root, manifestPath))) continue;
  const manifest = read(manifestPath);
  const files = new Set([manifestPath, base + '/script/narration.ko.json', manifest.paths?.script,
    base + '/script/narration.en.json', manifest.paths?.scriptEn, manifest.paths?.scriptEnglish,
    base + '/planning/outline.md', base + '/sources/SOURCES.md', base + '/README.md',
    base + '/publishing/youtube-upload.json', manifest.publishing?.receipt].filter(Boolean));
  for (const p of files) if (fs.existsSync(path.join(root, p))) current.push({path: p, sha256: hash(p)});
}
const changes = current.filter(f => old.get(f.path) !== f.sha256).map(f => ({...f, previousSha256: old.get(f.path) || null}));
const removed = [...old.keys()].filter(p => !current.some(f => f.path === p));
const output = path.join(__dirname, 'local/episode04-duplicate-input-change-snapshot-v1.json');
if (fs.existsSync(output)) throw Error('Read the existing snapshot before preparing a new version');
fs.writeFileSync(output, JSON.stringify({observedAt: new Date().toISOString(), baselineReviewedAt: previous.reviewedAt, currentInputs: current, changes, removed}, null, 2) + '\n');
console.log(JSON.stringify({files: current.length, changes, removed}, null, 2));
