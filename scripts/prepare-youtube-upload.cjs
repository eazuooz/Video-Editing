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
const videoData = fs.readFileSync(path.join(root, upload.video.path));
const videoHash = crypto.createHash('sha256').update(videoData).digest('hex');
if (videoHash !== upload.video.sha256 || videoData.length !== upload.video.bytes) throw new Error('Video differs from approved delivery; prepare a new revision record first');
const defaults = JSON.parse(fs.readFileSync(path.join(root, 'shared/publishing/youtube-defaults.json'), 'utf8'));
if (defaults.uploadAuthorization.status === 'private-upload-authorized') {
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
if (defaults.description.includePublicSourceCredits === false) {
  // Remove only an explicit credits section; keep chapters, channel links and internal source records.
  upload.descriptionBody.ko = upload.descriptionBody.ko.replace(/\n+출처\n[\s\S]*?(?=\n+챕터\n|$)/g, '').trim();
  upload.descriptionBody.en = upload.descriptionBody.en.replace(/\n+Credits\n[\s\S]*?(?=\n+Chapters\n|$)/g, '').trim();
}
if (!upload.descriptionBody.ko || !upload.descriptionBody.en) throw new Error('Missing video description body; do not overwrite live metadata with an empty read');
upload.metadata.description = upload.descriptionBody.ko + '\n\n' + footerKo;
upload.englishMetadata.description = upload.descriptionBody.en + '\n\n' + footerEn;
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
fs.writeFileSync(file, JSON.stringify(upload, null, 2) + '\n');
fs.writeFileSync(path.join(dir, descriptionPrefix + '.ko.txt'), upload.metadata.description + '\n');
fs.writeFileSync(path.join(dir, descriptionPrefix + '.en.txt'), upload.englishMetadata.description + '\n');
console.log(JSON.stringify({slug, receipt, status: upload.status, title: upload.metadata.title, titleEn: upload.englishMetadata.title, descriptionCharacters: {ko: upload.metadata.description.length, en: upload.englishMetadata.description.length}, subtitleFilesVerified: upload.subtitles.map(x => x.path), externalUploadPerformed: false}, null, 2));
