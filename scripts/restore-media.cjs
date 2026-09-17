// Restore checked-in, lossless media archives without Git LFS or extra packages.
// Usage: node scripts/restore-media.cjs [--project <slug>] [--verify-only]
const fs = require('node:fs');
const path = require('node:path');
const {restore, verify} = require('./media-archive.cjs');
const root = path.resolve(__dirname, '..');

function manifests(dir) {
  return fs.readdirSync(dir, {withFileTypes: true}).sort((a,b) => a.name.localeCompare(b.name))
    .flatMap(entry => entry.isDirectory() ? manifests(path.join(dir, entry.name))
      : entry.isFile() && entry.name === 'manifest.json' ? [path.join(dir, entry.name)] : []);
}

async function main() {
  const args = process.argv.slice(2);
  let project = null, verifyOnly = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--verify-only') verifyOnly = true;
    else if (args[i] === '--project' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(args[i+1] || '')) project = args[++i];
    else throw new Error('Usage: node scripts/restore-media.cjs [--project <slug>] [--verify-only]');
  }
  const base = path.join(root, 'shared', 'media-archives', ...(project ? [project] : []));
  if (!fs.existsSync(base)) throw new Error(`Archive directory not found: ${base}`);
  const files = manifests(base);
  if (!files.length) throw new Error('No archive manifests found. Pull the complete repository first.');
  for (const file of files) {
    console.log(`${verifyOnly ? 'Verify' : 'Restore'}: ${path.relative(root, file)}`);
    if (verifyOnly) {
      const m = await verify(file);
      console.log(`  SHA-256 OK: ${m.source} (${m.bytes} bytes)`);
    } else {
      const result = await restore(file, {root});
      console.log(`  ${result.skipped ? 'Already identical' : 'Restored'}: ${path.relative(root, result.target)}`);
    }
  }
  console.log(`Done: ${files.length} archive(s). Existing different files were not overwritten.`);
}
main().catch(error => {console.error(error.message); process.exitCode = 1;});
