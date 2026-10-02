const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const v2Root = path.join(root, 'output', 'youtube-library-refresh', 'v2');
const [id, source, selectedPromptPath] = process.argv.slice(2);
if (!/^[\w-]{11}$/.test(id || '') || !source || !fs.existsSync(source)) throw new Error('Expected video ID and existing generated PNG path');
const manifest = JSON.parse(fs.readFileSync(path.join(v2Root, 'prompts.json'), 'utf8'));
const item = manifest.items.find(x => x.id === id);
if (!item) throw new Error('ID is not in the authorized refresh manifest');
const rawPath = path.join(v2Root, 'raw', `${id}.png`);
const thumbnailPath = path.join(v2Root, 'thumbnails', `${id}.jpg`);
fs.copyFileSync(source, rawPath);
const ffmpeg = process.env.YOUTUBE_REFRESH_FFMPEG || 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';
const converted = spawnSync(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-y', '-i', rawPath, '-vf', 'scale=1280:720:flags=lanczos', '-frames:v', '1', '-q:v', '2', thumbnailPath], {encoding:'utf8', windowsHide:true});
if (converted.status !== 0) throw new Error(converted.stderr || 'Thumbnail conversion failed');
const bytes = fs.readFileSync(thumbnailPath);
if (bytes.length > 2 * 1024 * 1024) throw new Error('Thumbnail exceeds 2 MiB');
const exactPromptPath = path.join(v2Root, 'raw', `${id}.prompt.txt`);
if (selectedPromptPath) fs.copyFileSync(path.resolve(selectedPromptPath), exactPromptPath);
if (!fs.existsSync(exactPromptPath)) fs.writeFileSync(exactPromptPath, item.prompt + '\n');
const exactPrompt = fs.existsSync(exactPromptPath) ? fs.readFileSync(exactPromptPath, 'utf8').trimEnd() : item.prompt;
const receipt = {id, savedAt:new Date().toISOString(), mode:'built-in image_gen', source, rawPath, thumbnailPath,
  width:1280, height:720, bytes:bytes.length, sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
  promptSha256:crypto.createHash('sha256').update(exactPrompt).digest('hex'), status:'generated-awaiting-visual-check'};
fs.writeFileSync(path.join(v2Root, 'raw', `${id}.json`), `${JSON.stringify(receipt, null, 2)}\n`);
console.log(JSON.stringify(receipt));
