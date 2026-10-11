// Regenerate only the owned manifests without writing the shared project index.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const {build} = require(path.join(root, 'scripts/build-rebuild-manifests.cjs'));
function walk(relative) {
  const absolute = path.join(root, relative);
  if (!fs.existsSync(absolute)) return [];
  return fs.readdirSync(absolute, {withFileTypes:true}).flatMap(entry =>
    entry.isDirectory() ? walk(relative+'/'+entry.name) : [relative+'/'+entry.name]);
}
const slugs = fs.readdirSync(path.join(root, 'projects')).filter(slug =>
  fs.existsSync(path.join(root, 'projects', slug, 'project.json'))).sort();
const tracked = execFileSync('git', ['ls-files','--cached','--others','--exclude-standard','-z'],
  {cwd:root, maxBuffer:128e6, windowsHide:true}).toString('utf8').split('\0').filter(Boolean);
const files = [...new Set([...tracked, ...slugs.flatMap(slug => walk('projects/'+slug)),
  ...slugs.flatMap(slug => walk('motion-canvas/src/projects/'+slug))])]
  .filter(file => fs.existsSync(path.join(root,file))).sort();
for (const slug of ['game-math-polygon-centers-v2','game-math-polygon-partition-v2']) {
  fs.writeFileSync(path.join(root,'projects',slug,'rebuild.json'),
    JSON.stringify(build(slug,files),null,2)+'\n');
  console.log('Updated owned rebuild manifest: '+slug);
}
