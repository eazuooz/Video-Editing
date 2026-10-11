const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const slug = 'game-lighting-history-04-3';
const base = 'projects/game-lighting-history-04';
const read = p => JSON.parse(fs.readFileSync(path.resolve(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root, p))).digest('hex');
const planPath = `${base}/production/part3-final-input-plan-v145.json`;
const plan = read(planPath);
const defaults = read('shared/publishing/youtube-defaults.json');
const sections = [
 ['part3-overview', '예쁜 화면과 실제 계산은 같을까?', 'Appearance versus actual computation'],
 ['original-22-1', 'DLSS의 기능을 구별하는 기준', 'Distinguishing the DLSS features'],
 ['18-pre-generated-frame-count', '실제 프레임과 생성 프레임', 'Rendered and generated frames'],
 ['appearance-prerequisite', 'DLSS 5: 네 게임의 표면 비교', 'DLSS 5: surfaces in four games'],
 ['hogwarts-stair-reference', '같은 옷·난간·풍경으로 비교하기', 'Tracking clothing, railings and scenery'],
 ['appearance-to-controls', '노출과 톤 매핑의 입력·출력', 'Exposure and tone-mapping inputs and outputs'],
 ['histogram-open', '히스토그램과 로그 밝기', 'Histograms and logarithmic luminance'],
 ['tone-range', '톤 곡선·블룸·재질을 구별하기', 'Separating tone curves, bloom and materials'],
 ['grade-channel-controls', '색 보정과 룩업 텍스처', 'Color grading and lookup textures'],
 ['focus-scale-edit', '초점 거리·렌즈·깊이 레이어', 'Focus distance, lenses and depth layers'],
 ['focus-to-frame-inspection', '보이는 결과에서 프레임 자료로', 'From appearance to frame data'],
 ['capture-event-purpose', '캡처 이벤트와 입력 자료 읽기', 'Reading capture events and inputs'],
 ['capture-target-view', '렌더 타깃과 파이프라인 단계', 'Render targets and pipeline stages'],
 ['resource-viewer-context', '리소스 이름과 메모리 값의 한계', 'Resource names and memory-value limits'],
 ['resource-upload-control', '업로드 예산과 실제 측정', 'Upload budgets and actual measurement'],
 ['original-conclusion-1', '렌더링 기법을 검사하는 질문', 'Questions for inspecting rendering techniques'],
];
const chapters = sections.map(([id, titleKo, titleEn], i) => {
 const cut = plan.cuts.find(c => c.id === id || c.id.endsWith(':' + id));
 if (!cut) throw new Error('Missing measured chapter cut ' + id);
 return {id, actualStartFrame: cut.fromFrame, actualStartSeconds: cut.fromFrame / 60,
  descriptionStartSeconds: i === 0 ? 0 : Math.floor(cut.fromFrame / 60), titleKo, titleEn};
});
if (chapters.some((c, i) => i && c.descriptionStartSeconds - chapters[i - 1].descriptionStartSeconds < 10)) throw new Error('Chapter interval too short');
const time = s => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;
const discord = 'https://discord.gg/wZuqe7fqkR';
const footer = fs.readFileSync(path.resolve(root, 'shared/publishing/youtube-channel-description.ko.txt'), 'utf8')
 .split('📚 수업 노트')[0].trim().replace(/━━━━━━━━━━━━━━━━━━\s*$/, '').trim();
for (const url of [defaults.coaching.url, defaults.membershipUrl, discord]) if (!footer.includes(url)) throw new Error('Missing canonical footer URL');
const koBody = '게임 렌더링 역사 ④의 마지막 분할편. 화면이 더 예뻐지면 실제 계산도 같은 방식으로 달라졌을까요?\n\nDLSS의 재구성·프레임 생성·DLSS 5의 화면 표현을 구별하고, 바이오하자드·스타필드·호그와트 레거시·농구 게임의 표면을 관찰합니다. 이어서 언리얼 엔진의 노출, 톤 매핑, 히스토그램, 색 보정과 초점 설정을 입력과 결과로 연결합니다. 마지막에는 RenderDoc의 이벤트·렌더 타깃·입력 자료와 리소스 예산을 읽으며, 실제 계산을 검사하는 순서를 정리합니다.\n\n검은 배경의 공간 도식과 실제 게임·엔진 시연을 함께 사용합니다. 도식의 수치는 설명용이며, 서로 다른 카메라·노출·버전의 화면으로 성능이나 내부 구현을 단정하지 않습니다.\n\n';
const enBody = 'The final physical part of game-rendering history episode 4. Does a more attractive image mean the underlying computation changed in the same way?\n\nWe separate reconstruction, frame generation and the appearance changes demonstrated by DLSS 5, observing surfaces in Resident Evil, Starfield, Hogwarts Legacy and basketball footage. Unreal Engine demonstrations connect exposure, tone mapping, histograms, color grading and focus controls to their inputs and results. Finally, RenderDoc events, render targets, inputs and resource budgets provide a practical inspection order.\n\nSpatial diagrams accompany actual game and engine demonstrations. Numerical values in diagrams are illustrative. Different camera, exposure or version conditions do not prove performance or unseen implementations.\n\n';
const enFooter = `🎮 YamyamCoding: DirectX, Unity, Unreal Engine and computer graphics.\n\nProgramming coaching\n${defaults.coaching.url}\n\nDiscord community\n${discord}\n\nChannel membership\n${defaults.membershipUrl}`;
const descriptionKo = koBody + chapters.map(c => `${time(c.descriptionStartSeconds)} ${c.titleKo}`).join('\n') + '\n\n' + footer;
const descriptionEn = enBody + chapters.map(c => `${time(c.descriptionStartSeconds)} ${c.titleEn}`).join('\n') + '\n\n' + enFooter;
if ([descriptionKo, descriptionEn].some(t => t.length > 5000)) throw new Error('Description exceeds platform limit');
const comment = `DLSS·노출·렌더 타깃을 설명으로만 이해하는 데서 끝내지 않고, 렌더링 코드와 프레임 자료를 직접 연결하는 연습을 함께 하고 싶으신가요?\n게임 프로그래밍 1:1 코칭·과외 안내: ${defaults.coaching.url}`;
const pub = `${base}/publishing`;
const thumbnail = `${pub}/local/part3-v150/thumbnail-v1.png`;
const record = {
 preparedAt: new Date().toISOString(), status: 'prepared-only-awaiting-final-QA-and-collection', slug,
 logicalEpisode: 4, physicalPart: 3,
 titleKo: 'DLSS 5는 무엇을 바꿀까? | 노출·초점부터 프레임 검사까지',
 titleEn: 'What Does DLSS 5 Change? Exposure, Focus and Frame Inspection',
 descriptionKo, descriptionEn, chapters,
 inputs: [planPath, 'shared/publishing/youtube-defaults.json'].map(p => ({path: p, sha256: hash(p)})),
 thumbnail: {path: thumbnail, sha256: hash(thumbnail), review: `${pub}/part3-thumbnail-review-v150.json`, saved: false},
 uploadVariant: 'captioned', uploadPath: `output/${slug}/${slug}.captioned.mp4`, cleanUploadAllowed: false,
 subtitles: ['ko', 'en'].map(language => ({language, path: `output/${slug}/${slug}.${language}.srt`, method: 'manual-file-upload-with-timing', published: false})),
 coaching: {url: defaults.coaching.url, cardStartSeconds: 0, cardSaved: false, endingLinkSaved: false, pinnedCommentPrepared: true, commentStatus: 'pending-comments-availability', commentId: null},
 endScreen: {startSeconds: (plan.finalFrames - 600) / 60, endSeconds: plan.finalFrames / 60, durationSeconds: 10, playlistId: null, ownSubscribeSaved: false, externalCoachingLinkSaved: false, memberIdentitiesPreserved: true, verified: false},
 scheduling: {category: 'game-lecture', time: '09:00', timezone: 'Asia/Seoul', requireFreshStudioAndCalendar: true, requireAscendingPhysicalOrder: true, targetDate: null, saved: false},
 actualVideoId: null, privateSaved: false, uploaded: false, checksPassed: false,
 fullSettingsVerified: false, allFinalPixelsReviewed: false, qaApproved: false, collected: false,
 humanWholeListening: 'pending', humanPronunciation: 'pending', rightsApproved: false,
};
fs.writeFileSync(path.resolve(root, pub, 'part3-prepared-upload-v150.json'), JSON.stringify(record, null, 2) + '\n', {flag: 'wx'});
for (const [name, text] of Object.entries({'part3-description.ko.v150.txt': descriptionKo, 'part3-description.en.v150.txt': descriptionEn, 'part3-pinned-comment.ko.v150.txt': comment})) fs.writeFileSync(path.resolve(root, pub, name), text + '\n', {flag: 'wx'});
console.log(JSON.stringify({prepared: `${pub}/part3-prepared-upload-v150.json`, chapters: chapters.length, durationSeconds: plan.finalFrames / 60, actualVideoId: null, uploaded: false}));
