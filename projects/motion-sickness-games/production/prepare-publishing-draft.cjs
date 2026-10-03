// Write reviewable bilingual metadata. Chapters require the final measured timeline.
const fs = require('node:fs'), crypto = require('node:crypto');
const base = 'projects/motion-sickness-games/';
const defaults = JSON.parse(fs.readFileSync('shared/publishing/youtube-defaults.json', 'utf8'));
const manifest = JSON.parse(fs.readFileSync(base + 'project.json', 'utf8'));
const footerSource = fs.readFileSync(defaults.description.channelDefaultSnapshot, 'utf8');
const footerKo = footerSource.split('📚 수업 노트')[0].trim().replace(/\n━━━━━━━━━━━━━━━━━━\s*$/, '').trim();
for (const value of [defaults.coaching.url, defaults.membershipUrl, 'https://discord.gg/wZuqe7fqkR']) {
  if (!footerKo.includes(value)) throw new Error('Required channel footer link missing');
}
const openingKo = [
  '게임 멀미를 고려한 카메라 설계에서 시점 이동, 도구 조준, 추가 흔들림을 어떻게 나눌 수 있을까요?',
  '파워워시 시뮬레이터의 에임 모드 개발 시연과 탈로스 프린서플2의 실제 플레이 장면을 보며, 화면에서 무엇이 움직이고 플레이어가 어떤 선택을 할 수 있는지 살펴봅니다.',
  '필요한 방향 전환과 부가 연출을 구분하고, 설정의 의미·현재 방향·목표를 알아보기 쉽게 설계하는 방법을 설명합니다. 개발 당시 자료와 설명용 제안을 구분하며 개인에게 같은 결과를 약속하지 않습니다.',
].join('\n\n');
const openingEn = [
  'How can game camera design separate looking around, aiming a tool and added camera effects?',
  'We examine the PowerWash Simulator Aim Mode development demonstration and actual gameplay from The Talos Principle 2. Watch what moves on screen, how the task continues and which choices a player could control.',
  'The diagrams distinguish necessary changes in viewing direction from added presentation, and explain how to make settings, targets and current orientation understandable. Development-era footage and proposed interfaces are labelled separately. Individual responses can differ.',
].join('\n\n');
const footerEn = `🎮 Game development means building the ability to create, beyond following along.\n\nYamYamCoding is a game-programming channel covering DirectX, Unity, Unreal and computer graphics.\n\n━━━━━━━━━━━━━━━━━━\n\n🚀 Premium 1:1 programming coaching\n\nLearn to design and implement practical development tasks.\n• DirectX11 / DirectX12\n• Unity / Unreal Engine\n• Computer Graphics & PBR\n• Shaders / Rendering\n• Game engine development\n• Graphics research and implementation\n\n👉 Programming coaching\n${defaults.coaching.url}\n\n━━━━━━━━━━━━━━━━━━\n\n💬 YamYamCoding community\nQuestions, code reviews, feedback and learning resources.\n\nDiscord\nhttps://discord.gg/wZuqe7fqkR\n\nYouTube membership\n${defaults.membershipUrl}`;
const descriptions = {ko: `${openingKo}\n\n${footerKo}\n\n#게임개발 #게임디자인 #카메라설계`, en: `${openingEn}\n\n${footerEn}\n\n#GameDevelopment #GameDesign #CameraDesign`};
for (const language of ['ko', 'en']) {
  fs.writeFileSync(base + `publishing/youtube.${language}.md`, `# YouTube 게시 정보 — ${language === 'ko' ? '한국어' : 'English'}\n\n## 제목\n\n${manifest.titles[language]}\n\n## 썸네일 문구\n\n게임하면 왜 멀미날까?\n\n## 설명\n\n${descriptions[language]}\n\n## 챕터 상태\n\n최종 실측 타임라인 이후 설명의 새 영상 문단 아래에 챕터를 삽입합니다. 임시 00:00 목록은 게시하지 않습니다.\n`);
}
const comment = `게임 카메라·조준·입력 시스템을 직접 구현하며 배우고 싶다면 프로그래밍 과외를 확인해 주세요.\n${defaults.coaching.url}`;
fs.writeFileSync(base + 'publishing/pinned-comment.ko.txt', comment + '\n');
fs.writeFileSync(base + 'publishing/metadata-draft.json', JSON.stringify({
  preparedAt: new Date().toISOString(), status: 'local-draft-awaiting-final-timeline-and-platform-review',
  titles: manifest.titles, descriptions, chapters: [], finalChaptersReady: false,
  channelFooterSnapshot: defaults.description.channelDefaultSnapshot,
  channelFooterSha256: crypto.createHash('sha256').update(footerSource).digest('hex'),
  sourceCreditsInPublicDescription: false, internalSources: base + 'sources/SOURCES.md',
  coachingComment: {text: comment, status: 'pending-video-publication', posted: false, pinned: false,
    reason: 'Keep new upload private; private-video comments are unavailable.'},
  thumbnail: base + 'publishing/thumbnail.png', privacy: 'private', scheduledPublishAt: null,
  uploadFile: 'output/motion-sickness-games/motion-sickness-games.captioned.mp4',
  uploaded: false, videoId: null, burnedCaptionAndPlatformSettingsVerified: false,
}, null, 2) + '\n');
console.log('Bilingual metadata and exact coaching comment prepared locally; chapters/platform upload pending.');
