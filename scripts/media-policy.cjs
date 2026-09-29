// Keep source/edit metadata in Git; video, sound and media archives are local-only.
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const media = /\.(mp4|m4v|mov|mkv|webm|avi|wmv|mpg|mpeg|m2ts|mts|ogv|flv|wav|wave|mp3|m4a|aac|flac|ogg|opus|aif|aiff|wma|caf|ac3|mka|mp2)(?:\.(?:part|tmp|zip|gz|7z|rar|\d{3})(?:\d*)?)*$/i;
const archive = /\.(?:zip|7z|rar|tar|gz|tgz|bz2|xz|zst)(?:\.(?:part)?\d+)?$/i;
function isMedia(file) {
  const f = file.replaceAll('\\', '/');
  return media.test(f) || archive.test(f) || (/^shared\/media-archives\//i.test(f) && /\.(?:part\d*|\d{3})$/i.test(f));
}
function git(args) {return execFileSync('git', args, {cwd:root, maxBuffer:128e6, windowsHide:true}).toString('utf8');}
function tracked() {return git(['ls-files','-z']).split('\0').filter(Boolean);}
function check() {
  const bad = tracked().filter(isMedia);
  if (bad.length) {console.error('Media must not be committed (use git rm --cached; retain local files):\n'+bad.join('\n')); return false;}
  console.log('OK: no tracked video/audio/media archives.'); return true;
}
module.exports = {isMedia, git, tracked, root, check};
if (require.main === module) process.exitCode = check() ? 0 : 1;
