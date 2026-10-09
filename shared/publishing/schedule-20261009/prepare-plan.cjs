const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source = read(path.join(__dirname, 'studio-before-rows.json'));
const design = [
  ['picking-sides', 'xtUVcAHtQzg', 'youtube-upload-depth-v1.json'],
  ['motion-sickness-games', 'c18rkesgBSw', 'youtube-upload-depth-v1.json'],
  ['hierarchical-game-outlines', 'jBRt3xatdPk', 'youtube-upload-depth-v1.json'],
  ['game-reward-planning', 'Njz_o1YJh8Q', 'youtube-upload-depth-v1.json'],
  ['avoid-game-comparisons', 'cQE7_ygx_XM', 'youtube-upload-depth-v1.json'],
  ['making-game-sequels', '2-IyuwcP_vQ', 'youtube-upload-depth-v1.json'],
  ['familiar-game-rules', 'WpCmlV8KyOc', 'youtube-upload-depth-v1.json'],
  ['player-customization', 'lf765yYhPdM', 'youtube-upload-v1.json'],
  ['similar-game-design', '_p1IqDeg6YE', 'youtube-upload-v1.json'],
];
const lectures = [
  ['game-math-polar-3d', 'ZLOewk8JHXA'],
  ['game-math-orientation-matrices', '6-kP65hrZcI'],
  ['game-math-euler-axis-angle', 'iv9esV7vv_g'],
  ['game-math-quaternion-operations', '03OXtik2nes'],
  ['game-math-rotation-interpolation', 'mGBYkpSC9Mw'],
  ['game-math-lines-bounds', 'avLKKfQBV_U'],
  ['game-math-planes-barycentric', 'wsxSYEEj8aQ'],
  ['game-math-polygons-triangulation', 'L7SXFwn4i2k'],
  ['game-math-rendering-light', '-19ngvEqhao'],
  ['game-math-camera-frustum', 'CbX6KQ-_zsc'],
  ['game-math-camera-projection', 'c96qTnlHBVU'],
  ['game-math-projection-depth', 'PuXZUArWFko'],
  ['game-math-mesh-uv', 'xnIA0EAJtiA'],
  ['game-math-normal-transform-uv', 'nalAZHtEtw0'],
].map(a => [...a, 'youtube-upload.json']);
const assign = (records, category, offset) => records.map(([slug, videoId, receiptName], i) => {
  const row = source.page1Rows.find(r => r.videoId === videoId);
  if (!row || !['예약됨', '비공개'].includes(row.visibility)) throw Error('Unexpected actual Studio status: ' + videoId);
  const receipt = `projects/${slug}/publishing/${receiptName}`;
  const receiptPath = path.join(root, receipt);
  const content = fs.readFileSync(receiptPath, 'utf8');
  if (!content.includes(videoId)) throw Error('Delivery receipt ID mismatch: ' + videoId);
  const date = new Date(Date.UTC(2026, 9, 10 + offset + i * 2));
  const localDate = date.toISOString().slice(0, 10);
  const plannedPublishAt = localDate + 'T00:00:00Z';
  const oldDate = row.date.replace(/\.$/, '').split('.').map(s => Number(s.trim()));
  const actualOldDate = `${oldDate[0]}-${String(oldDate[1]).padStart(2, '0')}-${String(oldDate[2]).padStart(2, '0')}`;
  if (row.visibility === '예약됨' && actualOldDate !== localDate) throw Error('User date anchor mismatch; inspect before rearranging: ' + videoId);
  return { slug, videoId, title: row.title, category, categoryOrder: i + 1, date: localDate, time: '09:00', timezone: 'Asia/Seoul', plannedPublishAt, beforeVisibility: row.visibility, beforeDateShown: row.date, receipt, receiptSha256: sha(receiptPath), status: 'prepared-not-platform-scheduled', actualSavedAndReopened: false, humanListeningAndPublicRightsAreNotInferredFromScheduling: true };
});
const items = [...assign(design, 'game-design', 0), ...assign(lectures, 'game-lecture', 1)].sort((a, b) => a.date.localeCompare(b.date));
const futureDesignSlugs = ['presenting-game-scores', 'character-parameters', 'limited-color-world', 'computer-controlled-players', 'in-game-cutscenes', 'start-with-climax', 'kind-to-beginners', 'respect-player-time'];
const pending = futureDesignSlugs.map((slug, i) => ({ slug, category: 'game-design', date: new Date(Date.UTC(2026, 9, 28 + i * 2)).toISOString().slice(0, 10), time: '09:00', timezone: 'Asia/Seoul', videoId: null, status: 'target-slot-only-awaiting-reviewed-production-and-upload', scheduledOnPlatform: false }));
const now = new Date().toISOString();
const plan = { schemaVersion: 1, createdAt: now, userEvidence: '그리고 영상 업로드 예약 걸어줘 게임 디자인 하루 -> 게임 강의 하루 이렇게 순차적으로 업로드 되야해 내가 대충 예약 걸어뒀는데 만들어진 영상도 예약 기한 맞춰서 걸어줘 시간은 오전 9시로 통일해줘', anchor: { date: '2026-10-10', category: 'game-design', basis: 'Actual user-created Studio schedule; existing Oct10/11/12/13/15/17/19 dates preserved' }, timezone: 'Asia/Seoul', publicationTime: '09:00', cadence: 'one-video-per-day-alternating-game-design-and-game-lecture', onlyReviewedCompletedUploadsActuallyScheduled: true, existingPublishedVideosChanged: false, oldScoreBaselineExcluded: 'oDYJlcv2Dqk remains private during authorized Balatro60 revision; only completed revised ID may occupy its future slot', items, futureTargetSlots: pending, status: 'platform-execution-in-progress', imagesGitAdded: 0 };
fs.writeFileSync(path.join(__dirname, 'plan.json'), JSON.stringify(plan, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ items: items.length, existingSchedules: items.filter(i => i.beforeVisibility === '예약됨').length, newSchedules: items.filter(i => i.beforeVisibility === '비공개').length, first: items[0].date, last: items.at(-1).date, gameDesign: design.length, gameLectures: lectures.length, futureSlotsAreNotActualSchedules: pending.length }));
