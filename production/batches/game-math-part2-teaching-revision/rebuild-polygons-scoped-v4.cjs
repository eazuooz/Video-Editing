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
const owned = new Set([
  'game-math-polygon-centers-v2','game-math-polygon-partition-v2','game-math-polygons-triangulation',
  'game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2',
  'game-math-interpolation-paths-v2','game-math-rotation-conversions-v2',
  'game-math-lines-circles-v2','game-math-bounds-transform-v2',
  'game-math-plane-distances-v2','game-math-triangle-addresses-v2',
  'game-math-rendering-light','game-math-camera-frustum','game-math-camera-projection',
  'game-math-projection-depth','game-math-mesh-uv','game-math-normal-transform-uv',
]);
const targets = process.argv.length > 2 ? process.argv.slice(2) :
  ['game-math-polygon-centers-v2','game-math-polygon-partition-v2'];
for (const slug of targets) {
  if (!owned.has(slug)) throw Error('Not an owned delivery: '+slug);
  fs.writeFileSync(path.join(root,'projects',slug,'rebuild.json'),
    JSON.stringify(build(slug,files),null,2)+'\n');
  console.log('Updated owned rebuild manifest: '+slug);
}
