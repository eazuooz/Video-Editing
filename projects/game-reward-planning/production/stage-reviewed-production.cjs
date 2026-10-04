const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const run = (args, input) => {
  const r = cp.spawnSync('git', args, {cwd: root, input, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024});
  if (r.status !== 0) throw Error(JSON.stringify({args, status: r.status, stderr: r.stderr}));
  return r.stdout.trim();
};
const file = 'projects/game-reward-planning/production/final-v1/git-selection.json';
const selection = JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const existing=run(['diff','--cached','--name-only']).split('\n').filter(Boolean);
if(existing.some(p=>!selection.files.includes(p)))throw Error('Existing unrelated staged changes must be preserved.');
const partial = ['motion-canvas/projects.json', 'projects/rebuild-index.json'];
selection.partialSharedFiles = {reason: 'Index only this project addition, preserving concurrent polar 2D/3D registry entries and unrelated working-tree content.', paths: partial};
selection.status = 'reviewed-selection-ready-for-staging';
fs.writeFileSync(path.join(root, file), JSON.stringify(selection, null, 2) + '\n');
require('../../../scripts/build-rebuild-manifests.cjs').generate('game-reward-planning');
const direct = selection.files.filter(p => !partial.includes(p));
if (!direct.includes(file)) direct.push(file);
run(['add', '--pathspec-from-file=-', '--pathspec-file-nul'], direct.join('\0') + '\0');
for (const rel of partial) {
  const previous = JSON.parse(run(['show', 'HEAD:' + rel]));
  if (rel === partial[0]) {
    const entry = './src/projects/game-reward-planning/project.ts';
    if (!previous.includes(entry)) previous.push(entry);
  } else {
    if (!previous.projects.some(x => x.slug === 'game-reward-planning')) {
      const entry = {slug: 'game-reward-planning', manifest: 'projects/game-reward-planning/rebuild.json'};
      const index = previous.projects.findIndex(x => x.slug > entry.slug);
      previous.projects.splice(index < 0 ? previous.projects.length : index, 0, entry);
    }
  }
  const blob = run(['hash-object', '-w', '--stdin'], JSON.stringify(previous, null, 2) + '\n');
  run(['update-index', '--cacheinfo', '100644,' + blob + ',' + rel]);
}
const staged = run(['diff', '--cached', '--name-only']).split('\n').filter(Boolean);
if (staged.some(p => !selection.files.includes(p))) throw Error('Unexpected staged path');
if (staged.some(p => /\.(mp4|wav|aac|m4a|mp3|zip|7z|gz|rar)$/i.test(p) || p.endsWith('.info.json') || p.includes('research-local'))) throw Error('Forbidden staged media/research');
console.log(JSON.stringify({stagedFiles: staged.length, partialSharedFiles: partial, preservedOtherUserChanges: true}));
