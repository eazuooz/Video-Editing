const fs = require('node:fs');
const crypto = require('node:crypto');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source = 'production/research/game-lighting-history/local/aligned-native-review-v117.html';
const out = 'production/research/game-lighting-history/local/followup-native-review-v123.html';
if (fs.existsSync(out)) throw Error('Preserve existing review player');
let html = fs.readFileSync(source, 'utf8');
const start = html.indexOf('<script>const rows='), end = html.indexOf(';const pick=', start);
const old = JSON.parse(html.slice(start + '<script>const rows='.length, end));
const guide = read('projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json');
const rows = [
  {id:'focus-ordinary-later', source:'post', ranges:[[2470,2486.2]], ko:'뒤의 다른 설정으로 돌아온 일반 화면의 실제 동작을 확인합니다. 동일 조건의 켜기/끄기로 연결하지 않습니다.'},
  {id:'focus-error-diagnostic', source:'post', ranges:[[2380.1,2397.633333333]], ko:'별도 시점의 진단 설정입니다. 17.52초 전체 음성을 보존하고 동일 조건의 반사 복원 비교를 주장하지 않습니다.'},
  {id:'grade-controls-reassigned', source:'post', ranges:[[1855,1872.5]], ko:guide.scenes.find(s=>s.id==='grade-channel-controls').ko},
  {id:'grade-reference-reassigned', source:'post', ranges:[[1872.5,1890.3]], ko:guide.scenes.find(s=>s.id==='grade-shared-reference').ko},
  {id:'grade-result-reassigned', source:'post', ranges:[[1890.3,1911]], ko:guide.scenes.find(s=>s.id==='grade-to-lookup').ko},
  {id:'capture-target-reassigned', source:'capture', ranges:[[48,67]], ko:guide.scenes.find(s=>s.id==='capture-target-view').ko},
  {id:'capture-position-reassigned', source:'capture', ranges:[[67,89.8]], ko:guide.scenes.find(s=>s.id==='capture-position-input').ko},
  {id:'capture-stage-reassigned', source:'capture', ranges:[[89.8,109.52]], ko:guide.scenes.find(s=>s.id==='capture-stage-selection').ko}
];
for (const row of rows) {
  const s = guide.sources[row.source];
  if (!s || sha(s.path) !== s.sha256) throw Error('Source changed ' + row.id);
  Object.assign(row, {path:s.path, sha256:s.sha256, sourceId:s.id});
}
html = html.slice(0,start)+'<script>const rows='+JSON.stringify([...rows,...old]).replaceAll('<','\\u003c')+html.slice(end);
fs.writeFileSync(out, html);
console.log(JSON.stringify({out, rows:rows.length+old.length, newImages:0, approved:false}));
