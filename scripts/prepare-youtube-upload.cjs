#!/usr/bin/env node
// Local preparation only. Actual Studio upload and verification are separate.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const slug = process.argv[2];
if (!slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error('Usage: node scripts/prepare-youtube-upload.cjs <slug>');
const dir = path.join(root, 'projects', slug, 'publishing');
const receiptIndex = process.argv.indexOf('--receipt');
const receipt = receiptIndex >= 0 ? process.argv[receiptIndex + 1] : 'youtube-upload.json';
if (!receipt || !/^youtube-upload(?:-[a-z0-9]+)*\.json$/.test(receipt)) throw new Error('Receipt must be a youtube-upload[-revision].json filename in this project publishing directory');
const file = path.join(dir, receipt);
const descriptionPrefix = receipt === 'youtube-upload.json' ? 'upload-description' : receipt.replace('.json', '').replace('youtube-upload', 'upload-description');
const upload = JSON.parse(fs.readFileSync(file, 'utf8'));
const videoPath = path.join(root, upload.video.path);
const videoFd = fs.openSync(videoPath, 'r');
const videoDigest = crypto.createHash('sha256');
let videoBytes = 0;
try {
  const chunk = Buffer.allocUnsafe(8 * 1024 * 1024);
  let bytesRead;
  while ((bytesRead = fs.readSync(videoFd, chunk, 0, chunk.length, null)) > 0) {
    videoDigest.update(chunk.subarray(0, bytesRead));
    videoBytes += bytesRead;
  }
} finally {
  fs.closeSync(videoFd);
}
const videoHash = videoDigest.digest('hex');
if (videoHash !== upload.video.sha256 || videoBytes !== upload.video.bytes) throw new Error('Video differs from approved delivery; prepare a new revision record first');
const defaults = JSON.parse(fs.readFileSync(path.join(root, 'shared/publishing/youtube-defaults.json'), 'utf8'));
if (defaults.uploadVideo?.burnedKoreanCaptionsRequired) {
  const expected = defaults.uploadVideo.path.replaceAll('<slug>', slug);
  if (upload.video.path !== expected) throw new Error('Upload the reviewed bottom-center Korean-captioned MP4; the clean master is local preservation only');
  upload.burnedCaptionVerification ||= {required: true, position: [960, 970], playerCaptionsOff: true, status: 'pending-real-uploaded-frame-review'};
}
if (defaults.uploadAuthorization.initialUploadPrivacy === 'private') {
  if (upload.metadata.privacyStatus !== 'private' || upload.scheduled === true || upload.schedule?.active === true) {
    throw new Error('Current authorization permits private uploads only; public publication and scheduling belong to the user');
  }
}
const channelDefault = fs.readFileSync(path.join(root, defaults.description.channelDefaultSnapshot), 'utf8');
const footerKo = channelDefault.split('📚 수업 노트')[0].trim();
const footerEn = `🎮 Build games with real programming skills.

YamYamCoding is a Korean game-programming channel covering DirectX, Unity, Unreal Engine and computer graphics.

━━━━━━━━━━━━━━━━━━

🚀 Premium 1:1 programming coaching

Learn to design and implement real projects with guided feedback.
DirectX11 / DirectX12 · Unity / Unreal Engine · Computer Graphics & PBR · Shaders / Rendering · Game engines · Graphics papers and implementation

Programming coaching
${defaults.coaching.url}

━━━━━━━━━━━━━━━━━━

💬 YamYamCoding community

Questions, code reviews, feedback and course materials.

Discord
https://discord.gg/wZuqe7fqkR

YouTube channel membership
${defaults.membershipUrl}

━━━━━━━━━━━━━━━━━━`;
upload.descriptionBody ||= {ko: upload.metadata.description.trim(), en: upload.englishMetadata.description.trim()};
// Credits belong after every channel footer. Never remove attribution or append links after it.
const sourceHeading = /^(?:#{1,6}\s*)?(?:출처(?:[·\s]*(?:자료|영상|이미지|음악|제작 도구|및|참고자료))*|영상 출처|자료 출처|게임 화면 기록|Gameplay recordings|Credits|Sources(?:\s*(?:&|and|,)\s*(?:credits|assets|production tools))*)\s*[:：]?$/i;
const nextSectionHeading = /^(?:#{1,6}\s+\S.*|(?:챕터|Chapters|타임라인|Timeline|해시태그|Hashtags|채널 소개|About the channel|코칭|Coaching|Community|커뮤니티|Membership|멤버십|멤버쉽)\s*[:：]?)$/i;
const normalizeText = value => String(value ?? '').replace(/\r\n?/g, '\n').trim();
function splitSourceCredits(value, footer) {
  const text = normalizeText(value).split(normalizeText(footer)).join('').trim();
  const body = [], credits = [];
  let section = null;
  for (const line of text.split('\n')) {
    if (sourceHeading.test(line.trim())) {
      section = [];
      credits.push(section);
    } else if (section && nextSectionHeading.test(line.trim())) {
      section = null;
      body.push(line);
    } else {
      (section || body).push(line);
    }
  }
  return {body: body.join('\n').trim(), credits: credits.map(lines => lines.join('\n').trim()).filter(Boolean)};
}
const preparedCredits = {};
for (const [language, footer] of [['ko', footerKo], ['en', footerEn]]) {
  const extracted = splitSourceCredits(upload.descriptionBody[language], footer);
  // sourceCredits is the reviewed source/rights text supplied for this video, not a guessed inventory.
  const supplied = normalizeText(upload.sourceCredits?.[language]);
  const suppliedLines = supplied.split('\n');
  if (sourceHeading.test(suppliedLines[0]?.trim())) suppliedLines.shift();
  preparedCredits[language] = [...new Set([suppliedLines.join('\n').trim(), ...extracted.credits].filter(Boolean))].join('\n\n');
  if (!preparedCredits[language] || !/https?:\/\/\S+/.test(preparedCredits[language])) {
    throw new Error(`Missing verified ${language.toUpperCase()} source credits with original URLs; supply sourceCredits.${language} from the current production source/rights records`);
  }
  upload.descriptionBody[language] = extracted.body;
}
if (!upload.descriptionBody.ko || !upload.descriptionBody.en) throw new Error('Missing video description body; do not overwrite live metadata with an empty read');
upload.sourceCredits = preparedCredits;
upload.metadata.description = [upload.descriptionBody.ko, footerKo, '출처·자료 및 제작 도구\n' + preparedCredits.ko].join('\n\n');
upload.englishMetadata.description = [upload.descriptionBody.en, footerEn, 'Sources, assets and production tools\n' + preparedCredits.en].join('\n\n');
upload.descriptionSourceCredits = {policy: 'description-sources-last-v1', position: 'absolute-bottom', languages: ['ko', 'en'], sha256: Object.fromEntries(Object.entries(preparedCredits).map(([language, text]) => [language, crypto.createHash('sha256').update(text).digest('hex')])), actualUseAndRightsEvidence: 'existing production source/rights records; not inferred from a URL or this text assembler'};
for (const metadata of [upload.metadata, upload.englishMetadata]) {
  if (metadata.title.length > 100 || metadata.description.length > 5000) throw new Error('YouTube metadata character limit exceeded');
  for (const required of [defaults.coaching.url, defaults.membershipUrl]) {
    if (!metadata.description.includes(required)) throw new Error('Missing required channel link');
  }
}
for (const subtitle of upload.subtitles) {
  const data = fs.readFileSync(path.join(root, subtitle.path));
  const hash = crypto.createHash('sha256').update(data).digest('hex');
  if (hash !== subtitle.sha256) throw new Error(`Subtitle differs from approved delivery: ${subtitle.path}`);
  subtitle.method = 'manual-file-upload-with-timing';
}
upload.defaults = 'shared/publishing/youtube-defaults.json';
upload.coachingCard ||= {url: defaults.coaching.url, title: defaults.coaching.titleKo, teaser: defaults.coaching.teaserKo, startSeconds: 0, status: 'pending', requestedAvailability: defaults.coaching.requestedAvailability, platformConstraint: defaults.coaching.platformConstraint};
upload.endScreen ||= {startSeconds: upload.video.seconds - 10, endSeconds: upload.video.seconds, elements: defaults.endScreen.elements, status: 'pending'};
// The 2026-10-02 default is an ending link and a pinned coaching comment.
// These are preparation records, never evidence that Studio saved them.
if (defaults.coaching.endingRequired) {
  upload.coachingEndingLink ||= {url: defaults.coaching.url, title: defaults.coaching.titleKo, type: 'external-link-end-screen', startSeconds: upload.video.seconds - 10, endSeconds: upload.video.seconds, status: 'pending-platform-save', preserveMemberIdentity: true};
}
if (defaults.pinnedComment?.required) {
  const commentFile = path.join(dir, 'pinned-comment.ko.txt');
  if (!fs.existsSync(commentFile)) fs.writeFileSync(commentFile, '직접 만들어본 코드와 막힌 지점을 바탕으로 공부 방향을 잡고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해보세요.\n\n▶ 프로그래밍 코칭·과외\n' + defaults.coaching.url + '\n');
  if (!fs.readFileSync(commentFile, 'utf8').includes(defaults.coaching.url)) throw new Error('Pinned coaching comment must contain the canonical tutoring URL');
  upload.pinnedComment ||= {path: path.relative(root, commentFile).replaceAll('\\', '/'), url: defaults.coaching.url, status: 'pending-video-publication', reason: 'Private YouTube videos do not support comments. Keep private; post and pin only after comments become available.', commentId: null, pinnedVerified: false};
}
fs.writeFileSync(file, JSON.stringify(upload, null, 2) + '\n');
fs.writeFileSync(path.join(dir, descriptionPrefix + '.ko.txt'), upload.metadata.description + '\n');
fs.writeFileSync(path.join(dir, descriptionPrefix + '.en.txt'), upload.englishMetadata.description + '\n');
console.log(JSON.stringify({slug, receipt, status: upload.status, title: upload.metadata.title, titleEn: upload.englishMetadata.title, descriptionCharacters: {ko: upload.metadata.description.length, en: upload.englishMetadata.description.length}, subtitleFilesVerified: upload.subtitles.map(x => x.path), externalUploadPerformed: false}, null, 2));
