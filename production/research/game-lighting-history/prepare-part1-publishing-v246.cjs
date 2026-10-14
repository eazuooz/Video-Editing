// Measured publishing preparation; upload completion requires later saved UI evidence.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/game-lighting-history-04';
const slug = 'game-lighting-history-04-1';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const planPath = `${base}/production/part1-final-input-plan-v240.json`;
const plan = read(planPath);
const defaults = read('shared/publishing/youtube-defaults.json');
const sections = [
 ['part1-overview', '부족한 픽셀과 메모리로 화면 만들기', 'Building images with limited pixels and memory'],
 ['first:original-18v-1', '가상 섀도 맵: 필요한 그림자만 갱신하기', 'Virtual shadow maps: updating required shadows'],
 ['shadow-wheel-surface:native', '움직이는 바퀴와 표면의 그림자', 'Moving wheels and surface shadows'],
 ['shadow-resource-cache:native', '그림자 리소스와 캐시 관찰', 'Observing shadow resources and caches'],
 ['texture-streaming-input:native', '가상 텍스처의 입력과 주소', 'Virtual-texture inputs and addresses'],
 ['runtime-texture-producer:native', '런타임 가상 텍스처: 생산자와 소비자', 'Runtime virtual textures: producers and consumers'],
 ['upscaling:original-18t-1', 'TSR: 현재 화면과 이전 기록', 'TSR: current images and history'],
 ['tsr-silhouette-history:native', '윤곽·회전·모션 벡터로 확인하기', 'Inspecting silhouettes, rotation and motion vectors'],
 ['horizon-comparison-before:model', '호라이즌: 같은 무늬 경계 관찰', 'Horizon: tracking matching pattern edges'],
 ['outer-comparison-before:model', '아우터 월드 2: 표시 프레임과 실제 계산', 'The Outer Worlds 2: displayed frames and computation'],
 ['cyber-comparison-before:model', '사이버펑크: 표면·빛·재구성 구별', 'Cyberpunk: separating surfaces, light and reconstruction'],
 ['mobile:original-18a-1', '가시성·기하·재질의 서로 다른 역할', 'Distinct roles of visibility, geometry and materials'],
 ['geometry-programmable-material:native', '프로그래머블 재질의 입력과 결과', 'Programmable-material inputs and results'],
 ['mobile-texture-group:native', '모바일 텍스처·기기·셰이더 정책', 'Mobile texture, device and shader policies'],
 ['fortnite-comparison-before:model', '포트나이트: 진단 그래프와 실제 표면', 'Fortnite: diagnostic graphs and visible surfaces'],
 ['rivalry-mobile-history:native', '모바일 엔진 시연을 읽는 방법', 'Reading mobile-engine demonstrations'],
 ['four-game-transfer-conclusion:model', '네 게임에서 공통으로 검사할 질문', 'Inspection questions across four games'],
 ['part1-conclusion', '그림자·복원·모바일 예산 정리', 'Shadow, reconstruction and mobile budgets'],
];
const chapters = sections.map(([id, titleKo, titleEn], i) => {
 const c = plan.cuts.find(c => c.id === id);
 if (!c) throw new Error('Missing measured chapter: ' + id);
 return {id, actualStartFrame: c.fromFrame, actualStartSeconds: c.fromFrame / 60,
  descriptionStartSeconds: i ? Math.floor(c.fromFrame / 60) : 0, titleKo, titleEn};
});
if (chapters.some((c, i) => i && c.descriptionStartSeconds - chapters[i-1].descriptionStartSeconds < 10)) throw new Error('Chapter spacing');
const time = s => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
const discord = 'https://discord.gg/wZuqe7fqkR';
const footer = fs.readFileSync(path.join(root, 'shared/publishing/youtube-channel-description.ko.txt'), 'utf8')
 .split('📚 수업 노트')[0].trim().replace(/━━━━━━━━━━━━━━━━━━\s*$/, '').trim();
for (const u of [defaults.coaching.url, defaults.membershipUrl, discord]) if (!footer.includes(u)) throw new Error('Missing canonical URL');
const ko = '게임 렌더링 역사 ④의 첫 번째 분할편. 계산할 픽셀과 사용할 메모리가 부족할 때, 게임은 그림자와 화면의 세부를 어떻게 유지할까요?\n\n가상 섀도 맵·가상 텍스처의 주소와 갱신, TSR의 이전 화면과 모션 벡터, 가시성·재질·모바일 자원 정책을 검정 2.5D 공간 도식과 실제 게임·엔진 시연으로 연결합니다. 호라이즌 포비든 웨스트의 무늬 경계, 아우터 월드 2의 표시 프레임, 사이버펑크 2077의 표면과 빛, 포트나이트의 모바일 진단 화면을 서로 다른 관찰 질문으로 비교합니다. 모바일 엔진 기술 시연도 실제 화면과 설정을 구별하며 살펴봅니다.\n\n원본 비교 영상의 카메라·설정·기능 묶음을 유지합니다. 화면에 표시된 프레임 수를 시뮬레이션 횟수로 해석하거나, 설정 이름만으로 내부 구현과 성능 향상을 단정하지 않습니다. 도식의 수치는 원리를 설명하기 위한 값입니다.\n\n';
const en = 'The first physical part of game-rendering history episode 4. How do games preserve shadows and image detail when pixel computation and memory are limited?\n\nSpatial diagrams connect virtual shadow maps, virtual-texture addressing and updates, TSR history and motion vectors, visibility, materials and mobile resource policies to actual game and engine demonstrations. Matching pattern edges in Horizon Forbidden West, displayed frames in The Outer Worlds 2, surfaces and light in Cyberpunk 2077, and Fortnite mobile diagnostic views each answer a different inspection question. Mobile-engine technology demonstrations distinguish visible surfaces from settings.\n\nOriginal camera, settings and bundled-feature conditions are retained. Displayed frame counts do not establish simulation counts; setting names alone do not prove unseen implementations or performance gains. Numerical values in diagrams illustrate principles.\n\n';
const enFooter = `🎮 YamyamCoding: DirectX, Unity, Unreal Engine and computer graphics.\n\nProgramming coaching\n${defaults.coaching.url}\n\nDiscord community\n${discord}\n\nChannel membership\n${defaults.membershipUrl}`;
const descriptionKo = ko + chapters.map(c=>`${time(c.descriptionStartSeconds)} ${c.titleKo}`).join('\n') + '\n\n' + footer;
const descriptionEn = en + chapters.map(c=>`${time(c.descriptionStartSeconds)} ${c.titleEn}`).join('\n') + '\n\n' + enFooter;
if ([descriptionKo, descriptionEn].some(t=>t.length>5000)) throw new Error('Description limit');
const comment = `그림자·화면 복원·모바일 자원 정책을 렌더링 코드와 실제 프레임 자료로 연결하는 연습을 함께 하고 싶으신가요?\n게임 프로그래밍 1:1 코칭·과외 안내: ${defaults.coaching.url}`;
const thumbnail = 'projects/game-lighting-history-04/production/local/part1-thumbnail-v172/illustrated-candidate.png';
const thumbnailSha = hash(thumbnail);
if (thumbnailSha !== '982db4d57cbedf4a18a8779c1dedaf180d6e9557969828089cf31d45a72789c3') throw new Error('Reviewed thumbnail changed');
const pub = `${base}/publishing`;
const record = {
 preparedAt:new Date().toISOString(), status:'prepared-only-awaiting-final-QA-and-collection', slug,
 logicalEpisode:4,physicalPart:1,
 titleKo:'부족한 픽셀과 메모리로 게임 화면을 만드는 법 | 그림자·TSR·모바일 렌더링',
 titleEn:'Building Game Images with Limited Pixels and Memory: Shadows, TSR and Mobile Rendering',
 descriptionKo,descriptionEn,chapters,
 inputs:[planPath,'shared/publishing/youtube-defaults.json'].map(p=>({path:p,sha256:hash(p)})),
 thumbnail:{path:thumbnail,sha256:thumbnailSha,directIllustratedReview:true,saved:false},
 uploadVariant:'captioned',uploadPath:`output/${slug}/${slug}.captioned.mp4`,cleanUploadAllowed:false,
 subtitles:['ko','en'].map(language=>({language,path:`output/${slug}/${slug}.${language}.srt`,method:'manual-file-upload-with-timing',published:false})),
 coaching:{url:defaults.coaching.url,cardStartSeconds:0,cardSaved:false,endingLinkSaved:false,pinnedCommentPrepared:true,commentStatus:'pending-comments-availability',commentId:null},
 endScreen:{startSeconds:(plan.finalFrames-600)/60,endSeconds:plan.finalFrames/60,durationSeconds:10,playlistId:null,ownSubscribeSaved:false,externalCoachingLinkSaved:false,verified:false},
 privacy:'private',scheduled:false,schedulingAuthorized:false,
 actualVideoId:null,privateSaved:false,uploaded:false,checksPassed:false,fullSettingsVerified:false,
 allFinalPixelsReviewed:false,qaApproved:false,collected:false,
 humanWholeListening:'pending',humanPronunciation:'pending',rightsApproved:false,
};
fs.writeFileSync(path.join(root,pub,'part1-prepared-upload-v246.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
for (const [name,text] of Object.entries({'part1-description.ko.v246.txt':descriptionKo,'part1-description.en.v246.txt':descriptionEn,'part1-pinned-comment.ko.v246.txt':comment})) fs.writeFileSync(path.join(root,pub,name),text+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:`${pub}/part1-prepared-upload-v246.json`,chapters:chapters.length,durationSeconds:plan.finalFrames/60,uploaded:false}));
