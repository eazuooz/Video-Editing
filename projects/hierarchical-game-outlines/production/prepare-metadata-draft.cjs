const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),dest=path.resolve(__dirname,'../publishing');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const file=path.join(dest,'metadata-draft.json');
if(fs.existsSync(file))throw Error('Preserve existing metadata; update measured chapters explicitly later.');
const defaults=read('shared/publishing/youtube-defaults.json'),coaching=defaults.coaching.url;
const ko=read('projects/hierarchical-game-outlines/script/narration.ko.json'),en=read('projects/hierarchical-game-outlines/script/narration.en.json');
const footerPath='shared/publishing/youtube-channel-description.ko.txt',footer=fs.readFileSync(path.join(root,footerPath),'utf8');
const membership=footer.match(/https:\/\/www\.youtube\.com\/channel\/[^\s]+\/join/)?.[0];
const discord=footer.match(/https:\/\/discord\.gg\/[^\s]+/)?.[0];
if(!coaching||!membership||!discord)throw Error('Canonical channel links required.');
const footerKo=footer.slice(0,footer.indexOf(membership)+membership.length).trim();
const introKo=[
 '게임 기획서의 목표, 기능, 세부 규칙을 어떻게 나누고 다시 찾기 쉽게 만들까요?',
 '투 포인트 뮤지엄의 실제 놀이기구 배치, 선로 조절, 입구와 장식 확인 장면을 보며 계층형 아웃라인의 읽는 순서를 설명합니다.',
 '비슷한 크기의 항목을 나란히 놓고, 필요한 가지를 접고 펼치며, 묶음을 옮긴 뒤 뜻을 다시 확인합니다. 포함 관계와 다른 항목을 참고하는 관계도 구분합니다.',
 '기획 메모와 도식은 관찰한 행동을 바탕으로 만든 우리의 설명용 구성입니다. 개발사의 실제 기획서를 재현하거나, 화면 조작이 문서 편집 기능과 같다고 주장하지 않습니다.',
].join('\n\n');
const footerEn=`🎮 Game development means building the ability to create, beyond following along.

YamYamCoding is a game-programming channel covering DirectX, Unity, Unreal and computer graphics.

━━━━━━━━━━━━━━━━━━

🚀 Premium 1:1 programming coaching

Learn to design and implement practical development tasks.
• DirectX11 / DirectX12
• Unity / Unreal Engine
• Computer Graphics & PBR
• Shaders / Rendering
• Game engine development
• Graphics research and implementation

👉 Programming coaching
${coaching}

━━━━━━━━━━━━━━━━━━

💬 YamYamCoding community
Questions, code reviews, feedback and learning resources.

Discord
${discord}

YouTube membership
${membership}`;
const introEn=[
 'How can a game design document organize goals, features and detailed rules so readers can find what they need?',
 'We examine actual ride placement, track adjustments, entrances and decoration in Two Point Museum, then connect those observations to the reading order of a hierarchical outline.',
 'Keep sibling items at comparable levels, fold and expand the relevant branch, and check meaning after moving a group. Distinguish containment from references to other items.',
 'The planning notes and diagrams are our explanatory proposals based on observed actions. They do not reproduce the developer’s internal design documents or equate camera and track controls with an outline editor.',
].join('\n\n');
const descriptions={ko:introKo+'\n\n'+footerKo+'\n\n#게임개발 #게임기획 #기획서',en:introEn+'\n\n'+footerEn+'\n\n#GameDevelopment #GameDesign #DesignDocuments'};
const comment=`게임 기획을 실제 구현으로 연결하는 연습이 필요하다면 프로그래밍 과외를 확인해 주세요.\n${coaching}`;
const draft={preparedAt:new Date().toISOString(),status:'local-draft-awaiting-final-timeline-and-platform-review',
 titles:{ko:ko.title,en:en.title},descriptions,chapters:[],finalChaptersReady:false,
 chapterPlacement:'Below new video introduction and above retained channel footer; write measured times after final timeline approval.',
 channelFooterSnapshot:footerPath,channelFooterSha256:crypto.createHash('sha256').update(footer).digest('hex'),
 sourceCreditsInPublicDescription:false,internalSources:'projects/hierarchical-game-outlines/sources/SOURCES.md',
 coachingComment:{text:comment,status:'pending-video-publication',posted:false,pinned:false,reason:'Keep private; private-video comments unavailable.'},
 thumbnail:'projects/hierarchical-game-outlines/publishing/thumbnail.png',privacy:'private',scheduledPublishAt:null,
 uploadFile:'output/hierarchical-game-outlines/hierarchical-game-outlines.captioned.mp4',uploaded:false,videoId:null,
 burnedCaptionAndPlatformSettingsVerified:false};
fs.writeFileSync(file,JSON.stringify(draft,null,2)+'\n');
for(const language of ['ko','en'])fs.writeFileSync(path.join(dest,`youtube.${language}.md`),`# ${draft.titles[language]}\n\n${descriptions[language]}\n`);
fs.writeFileSync(path.join(dest,'pinned-comment.ko.txt'),comment+'\n');
console.log('Local bilingual metadata/comment prepared. No final chapters or platform delivery claimed.');
