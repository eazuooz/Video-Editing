// A local, silent, normal-speed inspection surface. No approval from source acquisition.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
process.chdir(root);
const base = 'production/research/game-lighting-history/local/episode04-native-v9';
const acquisition = JSON.parse(fs.readFileSync(base + '/nanite-foliage-stockholm-2025.acquisition.json', 'utf8'));
const execution = JSON.parse(fs.readFileSync(base + '/execution.json', 'utf8'));
if (execution.current || execution.status !== 'native-and-samples-ready' || acquisition.wholeDownloadedWindowDecodeExit !== 0 || !acquisition.wholeOriginalDecoded) throw Error('Closed complete native acquisition and whole decode required');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if (sha(acquisition.media) !== acquisition.sha256) throw Error('Observed native source changed');
const template = fs.readFileSync('production/research/game-lighting-history/local/episode04-process-windows-v4/native-motion-review-v4.html', 'utf8');
const entries = [{id: acquisition.slug, src: path.basename(acquisition.media), requestedOffset: 0, duration: +acquisition.probe.format.duration, sha256: acquisition.sha256}];
const html = template.replace('4편 실제 개발자 조절 · 클러스터 카메라 검수', '4편 나나이트 식생 · 공식 원본 검수')
  .replace('개발자 조절과 클러스터 카메라 · 원속도 검수', '나나이트 식생 · 원속도·무음 검수')
  .replace(/const entries=\[.*?\],v=document/s, 'const entries=' + JSON.stringify(entries) + ',v=document');
const output = base + '/foliage-native-review-v9.html';
if (fs.existsSync(output)) throw Error('Preserve existing prepared viewer');
fs.writeFileSync(output, html);
console.log(JSON.stringify({viewer: output, sha256: sha(output), sourceDuration: entries[0].duration, newMedia: 0, newImages: 0, finalUseApproved: false}));
