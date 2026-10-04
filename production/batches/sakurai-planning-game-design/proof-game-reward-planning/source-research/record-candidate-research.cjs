// Preserve observed source/permission evidence without approving unreviewed cuts.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../../../../');
const base = path.relative(root, __dirname).replaceAll('\\', '/');
const request = JSON.parse(fs.readFileSync(path.join(__dirname, 'request.json'), 'utf8'));
const researchPath = path.resolve(__dirname, '../source-research.json');
const research = JSON.parse(fs.readFileSync(researchPath, 'utf8'));
research.updatedAt = new Date().toISOString();
research.candidates = research.candidates.filter(x => x.game !== 'Cult of the Lamb');
research.candidates.push({
  game: 'Cult of the Lamb',
  status: 'official-candidates-acquiring-before-direct-action-review',
  selected: false,
  selectedForSourceInspection: true,
  conceptFit: 'Potential distinction between power, access and customization, plus asset/production costs. No trailer title establishes a reward or unlock requirement; independent claims follow visible actions only.',
  primaryPages: [request.permission.publisherResourcePage, request.permission.publisherLinkedPolicy],
  usageConditions: 'The official publisher creator page directly links the game-video monetization policy. The publisher-generated page explicitly grants posting and monetization for the entered public channel and lists Cult of the Lamb. Presenter voices, source music, animated sequences and unrelated third-party crossover IP are excluded. Final public-rights review is still pending.',
  permission: request.permission,
  recentUse: 'Repository game-candidates/SOURCES search found no earlier Cult of the Lamb selection; prefer this fresh title over recent PWS/Talos/UCH/Gang Beasts/Museum examples.',
  sources: request.sources,
  acquisition: base + '/acquisition.json',
  directActionReview: 'pending',
  approvedIntervals: []
});
research.nextAction = 'Finish the sequential official downloads and full CPU decodes, inspect native action frames and boundaries, then approve meaningful action intervals before independent KO/EN narration or new scenes. Preserve the whole-video opening overview in planning; add relevant sources if the usable action bank is too short for body60:40.';
fs.writeFileSync(researchPath, JSON.stringify(research, null, 2) + '\n');
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const q = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const item = q.items.find(x => x.slug === request.slug);
item.execution = {...item.execution, sessionId: 94260, acquisitionSessionId: 94260, acquisitionStartedAt: '2026-10-04T07:13:25.457Z', acquisitionPid: 10276, sourceResearch: path.relative(root, researchPath).replaceAll('\\', '/'), overviewRequired: true, noTts: true, noNewScript: true};
item.nextAction = research.nextAction;
q.updatedAt = research.updatedAt;
fs.writeFileSync(queuePath, JSON.stringify(q, null, 2) + '\n');
console.log(JSON.stringify({slug: request.slug, sourceInspectionCandidates: request.sources.map(x => x.videoId), permissionEvidence: true, actionIntervalsApproved: false, narrationCreated: false, sessionId: 94260}));
