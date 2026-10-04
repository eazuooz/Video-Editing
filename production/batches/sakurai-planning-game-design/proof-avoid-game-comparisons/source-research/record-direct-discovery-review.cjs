// Record directly read contact sheets; candidate windows are not final native cuts.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../../../..');
const base = 'production/batches/sakurai-planning-game-design';
const proof = `${base}/proof-avoid-game-comparisons`;
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
function write(p, value) {
  const file = path.join(root, p), temp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temp, JSON.stringify(value, null, 2) + '\n');
  fs.renameSync(temp, file);
}
const discovery = read(`${proof}/source-research/discovery.json`);
const acquisition = read(`${proof}/source-research/acquisition.json`);
if (discovery.sources.length !== 5 || discovery.sources.reduce((n, s) => n + s.frames, 0) !== 435)
  throw Error('Unexpected discovery inputs; this direct review must not approve changed sources.');
const observations = {
  z4utn4Sm6SY: {
    game: 'Pepper Grinder', decision: 'retain-for-native-action-review',
    candidates: [
      {seconds: [5, 16], observed: 'Avatar follows curved yellow burrowing terrain, leaves it in an arc and enters other terrain/water. Exact shot boundaries and inputs require native review.'},
      {seconds: [16, 30], observed: 'Burrowing near lava, launching vertically, red beetle encounter, projectile/cannon-cart sequence and moving blades. Separate actions; never imply one continuous route.'},
      {seconds: [38, 54], observed: 'Large moving-machine traversal, narrow saw passages, lava jumps, grapple lines, circular tunnel and airborne terrain traversal.'}
    ],
    excludedOrHeld: [
      {seconds: [0, 5], reason: 'Rating, logos and reveal; not actual-action time.'},
      {seconds: [30, 33], reason: 'Marketing text and black transition.'},
      {seconds: [33, 38], reason: 'Character encounter/story staging; no approved action chain.'},
      {seconds: [54, 72], reason: 'Title/release cards and long static blue-creature conversation.'}
    ]
  },
  '4c-3gbC5mc4': {
    game: 'Pepper Grinder', decision: 'retain-for-native-action-review-and-cross-source-deduplication',
    candidates: [
      {seconds: [5, 11], observed: 'Curved burrow exits, red beetle strike and yellow vertical columns. Several shots resemble the launch source and must be matched before selection.'},
      {seconds: [18, 20], observed: 'Avatar jumps along a rope bridge and drops beside a cliff.'},
      {seconds: [23, 35], observed: 'Burrowing beside brambles, projectile/cannon action, large machine and snowy vehicle/airborne traversal. Exact clip uniqueness remains pending.'},
      {seconds: [46, 55], observed: 'Vertical columns, hanging lava containers/projectiles and purple polygon traversal devices. Rules and continuity unapproved.'}
    ],
    excludedOrHeld: [
      {seconds: [0, 5], reason: 'Branding/reveal.'},
      {seconds: [11, 18], reason: 'Black transition and story/chest/standing characters.'},
      {seconds: [20, 23], reason: 'Standing/idle boat view.'},
      {seconds: [35, 46], reason: 'Maps, shop, sticker/gacha screens; unrelated to the proposed pitch question.'},
      {seconds: [55, 60], reason: 'Options/controls and game-speed changes. Do not use artificial slow-down to fill the quota.'},
      {seconds: [60, 69.833333], reason: 'Logo and release advertising.'}
    ]
  },
  xREgLxEzZE4: {
    game: 'The Plucky Squire', decision: 'exclude-from-current-actual-footage-bank',
    candidates: [],
    excludedOrHeld: [
      {seconds: [0, 87], reason: 'Physical hands manipulating paper pop-up craft and printed characters, with transitions/branding. Official marketing footage is not actual gameplay.'},
      {seconds: [87, 93], reason: 'Very short actual-game montage; held to avoid fragment padding and overlap with stronger gameplay sources.'},
      {seconds: [93, 98.366667], reason: 'Release/title card.'}
    ]
  },
  JdNZo7E_hXU: {
    game: 'The Plucky Squire', decision: 'retain-selected-portal-traversal-for-native-review',
    candidates: [
      {seconds: [3, 14], observed: 'Avatar moves on illustrated book pages, jumps across platforms, crosses a page/3D portal and strikes enemies. Several sub-shots, not one continuous cycle.'},
      {seconds: [17, 20], observed: 'Top-down book-page combat; native boundaries needed.'},
      {seconds: [22, 28], observed: 'Silhouette cave traversal and jumping/striking a goblin on a platform.'},
      {seconds: [53, 62], observed: 'Avatar leaves a glowing portal onto the 3D book surface, walks to another glowing marker and enters it. Source has just enabled Show Hidden Portals; disclose this and do not infer default visibility.'},
      {seconds: [73, 77], observed: '3D desk traversal over a ruler and collection of visible glowing objects; source accessibility changes precede this.'},
      {seconds: [80, 82], observed: 'Portal transition onto a paper strip, before dialogue.'},
      {seconds: [91, 104], observed: 'Several city, enemy, silhouette-stair and 3D sequences; short cuts require native continuity review.'}
    ],
    excludedOrHeld: [
      {seconds: [0, 3], reason: 'Title/rating.'},
      {seconds: [14, 17], reason: 'New-game/play-style menus.'},
      {seconds: [20, 22], reason: 'Play-style menu.'},
      {seconds: [28, 36], reason: 'Options and accessibility menu; context for modified demonstration settings, not actual-action quota.'},
      {seconds: [36, 53], reason: 'Assistance demonstration with repeated platforms and interspersed menus; held for this pitch topic. Do not describe it as default difficulty.'},
      {seconds: [62, 73], reason: 'Combat plus invincibility/one-hit-kill menus. Hold assisted combat rather than claim normal challenge.'},
      {seconds: [77, 80], reason: 'Dialogue/static page.'},
      {seconds: [82, 91], reason: 'Dialogue/hint scenes; no continuous approved action.'},
      {seconds: [104, 110.333333], reason: 'Release/title card.'}
    ]
  },
  WFIvd2HrMNY: {
    game: 'The Plucky Squire', decision: 'retain-for-native-world-change-and-portal-review',
    candidates: [
      {seconds: [12, 20], observed: 'Book-page walking/jumping and a stone block/staircase visual change. The sampled before/after does not establish the exact player input or full rule; inspect native frames first.'},
      {seconds: [30, 36], observed: 'City movement/combat and night/day word/world transition; full input/causal chain pending.'},
      {seconds: [36, 42], observed: 'Ball-matching board and boss arena; short separate interactions.'},
      {seconds: [42, 56], observed: 'Avatar exits the illustrated page, moves on the 3D desk, travels into a tall pictured surface/door portal and returns to a page. Check boundaries, menus/dialogue and duplicate source shots.'},
      {seconds: [58, 62], observed: 'Avatar moves from a pictured vertical surface along a suspended string among flags; exact transition pending native review.'}
    ],
    excludedOrHeld: [
      {seconds: [0, 12], reason: 'Room fly-through and title/developer reveal; not gameplay action.'},
      {seconds: [20, 30], reason: 'Map/cinematic/story setup and confrontation; held.'},
      {seconds: [56, 58], reason: 'Short arena/boss cut; not part of the preceding portal traversal.'},
      {seconds: [62, 71], reason: 'Fast transition, mode/accessibility menus and assisted hidden-portal showcase; held.'},
      {seconds: [71, 77], reason: 'Release/title advertising.'},
      {seconds: [77, 82.083333], reason: 'Standing celebration/dialogue; no useful continuous action for this topic.'}
    ]
  }
};
const now = new Date().toISOString();
const reviewPath = `${proof}/source-research/direct-discovery-review.json`;
const review = {
  schemaVersion: 1, slug: 'avoid-game-comparisons', reviewedAt: now,
  status: 'all-discovery-sheets-read-native-interval-approval-pending',
  method: 'Direct visual reading of every one-second PTS contact-sheet tile through view_image; displayed sheets were resized. This is discovery, not full audiovisual watching or frame-exact boundary approval.',
  sheetsDirectlyRead: 30, framesDirectlyRead: 435,
  acquisition: `${proof}/source-research/acquisition.json`, discovery: `${proof}/source-research/discovery.json`,
  discoverySha256: sha(`${proof}/source-research/discovery.json`),
  sourceAudioUsed: false, approvedIntervals: [], approvedActualSeconds: 0,
  bodyRatioApproved: false, humanWholeSourceAudiovisualReview: 'pending',
  crossSourceUniquenessApproved: false,
  sources: discovery.sources.map(s => ({videoId: s.videoId, framesDirectlyRead: s.frames,
    sourceSha256: acquisition.results.find(r => r.videoId === s.videoId)?.fileSha256 ?? null,
    sheets: s.sheets.map(p => ({path: p, sha256: sha(p)})), ...observations[s.videoId]})),
  constraints: ['Do not count physical craft advertising, title, menu, idle or unrelated shots in actual-game time.',
    'Book pages and virtual desk scenery in actual Plucky Squire footage are part of its game world; distinguish these from physical hands in the launch advertisement.',
    'Sampled before/after frames do not prove button inputs, default rules, successful outcomes or developer intent.',
    'Several official sources reuse the same shots; select unique native intervals rather than counting repetitions.',
    'Do not copy/translate source narration; source audio is excluded.',
    'Secure additional concept-matched official action if the unique approved bank cannot support60:40.'],
  nextAction: 'Inspect native action sequences and cut edges, deduplicate matching shots, obtain additional official gameplay as needed, then approve an action bank and independent overview/body plan before narration.'
};
write(reviewPath, review);
const researchPath = `${proof}/source-candidates-and-usage-review.json`;
const research = read(researchPath);
research.historicalCandidateResearch = research.historicalCandidateResearch || {
  reviewedAt: research.reviewedAt, status: research.status, actualFootageAcquired: research.actualFootageAcquired,
  approvedIntervals: research.approvedIntervals, nextAction: research.nextAction
};
Object.assign(research, {updatedAt: now, status: review.status, actualFootageAcquired: true,
  sourceAcquisition: review.acquisition, directDiscoveryReview: reviewPath, approvedIntervals: [], nextAction: review.nextAction});
write(researchPath, research);
const q = read(`${base}/queue.json`), item = q.items.find(i => i.slug === 'avoid-game-comparisons');
if (item.checkpoints.script || item.checkpoints.narration || item.checkpoints.scenes)
  throw Error('Production has advanced: do not overwrite its execution checkpoint.');
const closed = [...new Set([...(item.execution.doNotWaitClosedSessions || []), 60174, 33630, 78586])];
if (item.execution.phase !== 'direct-source-discovery-reviewed-awaiting-native-cuts')
  item.historicalExecution.push({...item.execution, observationCorrection: 'Discovery session was78586; earlier33630 belonged to acquisition. Both completed.'});
item.execution = {observedAt: now, phase: 'direct-source-discovery-reviewed-awaiting-native-cuts',
  status: review.status, pid: null, sessionId: null, alive: false, activeTasks: [],
  gpuSynthesisJobs: 0, renderJobs: 0, uploads: 0, newNarrationCreated: false, newSceneCreated: false,
  doNotWaitClosedSessions: closed,
  completedWorkers: [{kind: 'official-acquisition-full-decode', pid: 55012, sessionId: 33630, status: 'closed',
    evidence: review.acquisition}, {kind: 'CPU-discovery', pid: discovery.pid, sessionId: 78586, status: 'closed',
    evidence: review.discovery, children: discovery.sources.map(s => ({videoId: s.videoId, pid: s.childPid, status: 'closed'}))}]
};
Object.assign(item, {stage: 'native-action-and-boundary-review', updatedAt: now, sourceDiscoveryReview: reviewPath, nextAction: review.nextAction});
q.updatedAt = now; q.lastProgressAt = now;
write(`${base}/queue.json`, q);
const checkpointPath = `${proof}/latest-checkpoint.json`, checkpoint = read(checkpointPath);
Object.assign(checkpoint, {updatedAt: now, stage: item.stage, execution: item.execution,
  sourceAcquisition: {state: review.acquisition, pid: 55012, sessionId: 33630, alive: false,
    status: acquisition.status, results: acquisition.results.length, actualCutApproval: false},
  sourceDiscovery: {state: review.discovery, pid: discovery.pid, sessionId: 78586, alive: false,
    sheetsDirectlyRead: 30, framesDirectlyRead: 435, nativeActionApproval: false, review: reviewPath},
  nextAction: review.nextAction});
write(checkpointPath, checkpoint);
console.log(JSON.stringify({status: review.status, sources: 5, frames: 435, sheets: 30,
  actualNativeCutApproval: false, gpuJobs: 0, closedSessions: closed}));
