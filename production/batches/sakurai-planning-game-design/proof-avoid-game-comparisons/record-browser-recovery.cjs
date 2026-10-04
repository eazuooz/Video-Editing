// Record actual read-only browser recovery; this does not approve production.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../../..');
const base = 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons';
const read = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const write = (rel, value) => fs.writeFileSync(path.join(root, rel), JSON.stringify(value, null, 2) + '\n');
const sha = rel => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, rel))).digest('hex');
const now = new Date().toISOString();
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath);
const item = queue.items.find(x => x.slug === 'avoid-game-comparisons');
if (queue.currentSlug !== item.slug || item.checkpoints.script || item.checkpoints.narration) throw Error('Checkpoint changed; inspect before recording.');
const review = read(base + '/content-review.json');
review.reviewedAt = now;
review.originalConcept = {
  ...review.originalConcept,
  fullContentRead: true,
  status: 'Full automatically generated Japanese transcript directly read through the normal browser export; full human audiovisual review is not claimed.',
  transcript: base + '/research-local/gYuvggptkDM.ja.browser-transcript.txt',
  sha256: sha(base + '/research-local/gYuvggptkDM.ja.browser-transcript.txt'),
  observedVideoId: 'gYuvggptkDM',
  observedDurationSeconds: 185,
  transcriptCoverage: '00:03–03:03; closing nonverbal marker retained',
  sourcePurpose: 'Concept research only; no source video/audio or full copied/translated narration for production.',
  researchFindings: [
    'An unbuilt idea must be communicated to listeners who do not share the planner’s mental image.',
    'A familiar work name may obscure the new idea’s own appeal and may invoke different examples for different generations or experiences.',
    'The listener may form an analogy; the presenter should explain the actual distinctive experience and avoid relying on a title as the whole explanation.',
    'The source permits comparison shorthand in suitable shared contexts; it does not forbid all comparison or analysis.'
  ],
  limitations: 'Auto-caption transcription errors are preserved. Do not reconstruct an unclear specific Mario example or treat this as exact human-approved wording.'
};
for (const rel of [
  'projects/hierarchical-game-outlines/script/narration.ko.json',
  'projects/hierarchical-game-outlines/script/narration.en.json',
  'projects/game-dev-career/script/narration.ko.json',
  'projects/game-dev-career/script/narration.en.json'
]) {
  const script = read(rel);
  if (!review.relatedFullScriptsRead.some(x => x.path === rel)) review.relatedFullScriptsRead.push({path: rel, sha256: sha(rel), scenes: script.scenes.length, fullRead: true});
}
review.relatedFindings = [
  review.relatedFindings[0],
  {slug:'hierarchical-game-outlines',videoId:'lEwpxP_qsDY',fullKoEnRead:true,claims:['Organize goals, features and detail by containment and reading questions.','Fold, move and cross-reference branches; review their meaning afterward.'],comparison:'Document organization overlaps in context, but does not teach title shorthand, listener assumptions or communicating a new game’s distinctive experience.'},
  {slug:'game-dev-career',videoId:'7ZjcujPX_uc',fullKoEnRead:true,claims:['Explain design, programming and art roles.','Connect collaborative iteration and job fundamentals.'],comparison:'Explaining work to colleagues is a minor shared point, not the central question about analogy in a new-game pitch.'},
  {videoId:'YNJcFsRQoY8',actualCurrentTitle:'인디게임 데브캠프 지원사업 논란 | 왜 기획서 평가가 문제가 됐을까?',fullAutoTranscriptRead:true,transcript:base+'/research-local/YNJcFsRQoY8.browser-transcript.txt',sha256:sha(base+'/research-local/YNJcFsRQoY8.browser-transcript.txt'),coverage:'00:01–16:38 of 16:47',claims:['Historical discussion of support-program eligibility, evaluation procedure, existing development and unequal starting conditions.','The presenter gives criticism and opinions about verification and correcting the process.'],comparison:'A historical funding/evaluation critique, not an explanation of replacing familiar-title shorthand with visible player actions; its allegations are not newly verified facts for the proposed video.'}
];
const search = (query, filename, count, ids) => ({query,resultCount:count,actualVideoIds:ids,ax:base+'/'+filename+'.ax.txt',screenshot:base+'/'+filename+'.png',axSha256:sha(base+'/'+filename+'.ax.txt'),screenshotSha256:sha(base+'/'+filename+'.png')});
review.studioCurrentReview = {
  status:'partial-current-Studio-review; final duplicate decision still pending',
  observedAt:now,
  browser:'2',tab:'27',channelId:'UCOgtkPoyC0VXhCs7Xk3jvjQ',
  searches:[
    search('비교','studio-comparison-search',13,['TaVQIUwmWB8','bT7ndnuAuNE','5eF3u9xP35U','bJ8-HV_7F4w','23ojqqCJsiA','_xl6XACLpOo','syKT7UNaO70','Z2pkFu6Hb8o','00yN4MdU3Do','VANQySezO6o','ZRKdxkhOfe0','Y8hjb1fhFzI','DXHZDDLWfCY']),
    search('기획','studio-planning-search',4,['D81WnOMytG4','lEwpxP_qsDY','IHKv1p_aSJ4','YNJcFsRQoY8'])
  ],
  staleAxWarning:'Two reused checkbox labels lagged after filter changes. Result titles, thumbnail/title links, actual IDs and descriptions were read; stale checkbox names were not treated as video identity.',
  currentKoreanTitlesObserved:true,
  englishLocalizedTitleRecheck:'pending; binding existing Studio tab18 timed out in Emulation.setFocusEmulationEnabled. Do not alter completed settings.',
  decisionBasis:'Neither a title search, zero exact matches nor a different source ID establishes distinct content.'
};
review.verdict = 'pending-content-and-studio-review';
write(base+'/content-review.json',review);
const acquisition = read(base+'/source-concept-acquisition.json');
if (!acquisition.historicalDownloadAttempt) acquisition.historicalDownloadAttempt = JSON.parse(JSON.stringify(acquisition));
acquisition.status = 'source-concept-acquired-through-normal-browser';
acquisition.updatedAt = now;
acquisition.browserRecovery = {observedAt:now,tab:'33',sourceVideoId:'gYuvggptkDM',operation:'Normal watch-page navigation and documented content.exportYouTubeTranscript',transcript:review.originalConcept.transcript,sha256:review.originalConcept.sha256,fullTranscriptDirectlyRead:true,fullHumanAudiovisualListening:false,downloadRetryNeeded:false,noCookieOrIdentityBypass:true};
write(base+'/source-concept-acquisition.json',acquisition);
item.historicalExecution ||= [];
if (!item.historicalExecution.some(x=>x.sessionId===60174)) item.historicalExecution.push(item.execution);
item.execution = {observedAt:now,phase:'preflight-current-Studio-English-title-and-content-review',pid:null,sessionId:null,status:'normal-browser-source-recovered; duplicate decision pending',activeTasks:[],gpuSynthesisJobs:0,renderJobs:0,uploads:0,newNarrationCreated:false,newSceneCreated:false,doNotWaitClosedSessions:[60174]};
item.nextAction = 'Finish current Studio English localized-title/content comparison for likely overlaps and refresh distinct --check before production. Full original Japanese research transcript and six related KO/EN scripts plus existing YNJcFsRQoY8 content are already directly read; preserve hashes. Do not repeat the failed closed download. Then secure fresh concept-matched actual game actions before writing narration and the new whole-video overview. Thumbnail followups remain nonblocking and cannot be attempted before their recorded retry time.';
item.updatedAt = now;
queue.updatedAt = now;
queue.lastProgressAt = now;
write(queuePath,queue);
const checkpoint = read(base+'/latest-checkpoint.json');
checkpoint.updatedAt = now;
checkpoint.execution = item.execution;
checkpoint.sourceConceptFullRead = true;
checkpoint.fullHumanSourceAudiovisualReview = false;
checkpoint.currentStudioReview = review.studioCurrentReview.status;
checkpoint.duplicateDecision = 'pending';
checkpoint.nextAction = item.nextAction;
checkpoint.currentUi = {browser:'2',studioTab:'27',researchTab:'33',hierarchicalFollowupTab:'18',rewardWatchTab:'34',rebindTimeout:'18 Emulation.setFocusEmulationEnabled; inspect fresh state later'};
write(base+'/latest-checkpoint.json',checkpoint);
console.log(JSON.stringify({status:review.status,originalFullTranscriptRead:true,relatedFullScripts:review.relatedFullScriptsRead.length,studioSearches:2,duplicateDecision:'pending',newScriptCreated:false,updatedAt:now}));
