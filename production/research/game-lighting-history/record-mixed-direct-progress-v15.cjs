const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const root = path.resolve(__dirname, '../../..');
const prod = path.join(root, 'projects/game-lighting-history-03/production');
const target = path.join(prod, 'review-mixed-asr-direct-progress-v15.json');
const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const state = read(path.join(prod, 'review-mixed-asr-execution-v15.json'));
const request = read(path.join(prod, 'review-mixed-asr-request-v15.json'));
const requestLabels = new Set(request.windows.map(w => w.label));
const previous = fs.existsSync(target) ? read(target) : {records: []};
if (previous.mixSha256 && previous.mixSha256 !== state.mixSha256) throw Error('Current mix changed');
for (const entry of input) {
  if (!requestLabels.has(entry.label) || (entry.pendingIndependentWindows || []).some(label => !requestLabels.has(label))) throw Error('Use exact current request identities');
  const actual = state.results.find(r => r.label === entry.label);
  if (!actual || hash(path.join(root, actual.path)) !== actual.sha256) throw Error('Missing/current result mismatch');
  if (!entry.directFullExpectedAndActualTextRead || !entry.allWordTimestampsRead || !entry.findings.length) throw Error('Direct review evidence required');
  if (previous.records.some(r => r.label === entry.label)) throw Error('Already recorded; preserve prior review');
  const result = read(path.join(root, actual.path));
  previous.records.push({...entry, reviewedAt: new Date().toISOString(), resultPath: actual.path,
    resultSha256: actual.sha256, windowSha256: result.windowSha256,
    expectedParagraphCount: result.window.expectedKo.length, wordCount: result.words.length,
    contentApproved: false, independentlyResolved: false, humanWholeListening: 'pending', humanPronunciation: 'pending'});
}
Object.assign(previous, {updatedAt: new Date().toISOString(), mixSha256: state.mixSha256,
  planSha256: state.planSha256, totalWindows: 54, directlyReadWindows: previous.records.length,
  all54WindowsDirectlyCompared: false, currentMixedContentApproved: false,
  humanWholeListening: 'pending', humanPronunciation: 'pending',
  policy: 'Progress only. Preserve raw recognition and resolve apparent errors with completed independent context and current PCM before final mix approval.'});
fs.writeFileSync(target, JSON.stringify(previous, null, 2) + '\n');
console.log(JSON.stringify({directlyRead: previous.records.length, total: 54, finalMixedApproved: false}));
