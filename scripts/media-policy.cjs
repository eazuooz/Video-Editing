// Keep source/edit metadata in Git; video, sound and media archives are local-only.
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const media = /\.(mp4|m4v|mov|mkv|webm|avi|wmv|mpg|mpeg|m2ts|mts|ogv|flv|wav|wave|mp3|m4a|aac|flac|ogg|opus|aif|aiff|wma|caf|ac3|mka|mp2)(?:\.(?:part|tmp|zip|gz|7z|rar|\d{3})(?:\d*)?)*$/i;
const archive = /\.(?:zip|7z|rar|tar|gz|tgz|bz2|xz|zst)(?:\.(?:part)?\d+)?$/i;
function isMedia(file) {
  const f = file.replaceAll('\\', '/');
  return media.test(f) || archive.test(f) || (/^shared\/media-archives\//i.test(f) && /\.(?:part\d*|\d{3})$/i.test(f));
}
function git(args) {return execFileSync('git', args, {cwd:root, maxBuffer:128e6, windowsHide:true}).toString('utf8');}
function tracked() {return git(['ls-files','-z']).split('\0').filter(Boolean);}
const raster = /\.(png|jpe?g|webp|gif|bmp|tiff?)$/i;
function checkNewImages() {
  const additions = git(['diff','--cached','--diff-filter=A','--name-only','-z']).split('\0').filter(f => raster.test(f));
  if (!additions.length) return true;
  let registry;
  try { registry = JSON.parse(git(['show', ':shared/git-essential-images.json'])); }
  catch { console.error('New images require a staged shared/git-essential-images.json registry.'); return false; }
  const entries = new Map();
  for (const entry of registry.entries || []) {
    if (entries.has(entry.path)) { console.error('Duplicate essential image path: '+entry.path); return false; }
    entries.set(entry.path, entry);
  }
  const rejected = [];
  for (const file of additions) {
    const entry = entries.get(file);
    if (!entry || !registry.allowedPurposes?.includes(entry.purpose) ||
        typeof entry.reason !== 'string' || entry.reason.trim().length < 12 ||
        !entry.reviewedAt || !/^[a-f0-9]{64}$/i.test(entry.sha256 || '')) {
      rejected.push(file+' (exact path, purpose, reason, review time and SHA256 required)'); continue;
    }
    const blob = execFileSync('git', ['show', ':'+file], {cwd:root, maxBuffer:128e6, windowsHide:true});
    if (crypto.createHash('sha256').update(blob).digest('hex') !== entry.sha256.toLowerCase())
      rejected.push(file+' (staged image differs from reviewed SHA256)');
  }
  if (rejected.length) { console.error('Unapproved new raster images must remain local:\n'+rejected.join('\n')); return false; }
  return true;
}
function check() {
  const bad = tracked().filter(isMedia);
  if (bad.length) {console.error('Media must not be committed (use git rm --cached; retain local files):\n'+bad.join('\n')); return false;}
  if (!checkNewImages()) return false;
  console.log('OK: no tracked video/audio/media archives; new raster images require reviewed essential records.'); return true;
}
module.exports = {isMedia, git, tracked, root, checkNewImages, check};
if (require.main === module) process.exitCode = check() ? 0 : 1;
