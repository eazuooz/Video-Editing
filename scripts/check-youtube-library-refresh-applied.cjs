const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..', 'output', 'youtube-library-refresh', 'v2');
const read = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const progress = read('apply-progress.json');
const manifest = read('prompts.json');
const authorizedIds = new Set(manifest.items.map(x => x.id));
const reviewedIds = new Set(read('review-status.json').visualReviewedIds);
const metadata = new Map(read('metadata.json').items.map(x => [x.id, x]));
const seen = new Set();
const failures = [];
const notes = [];
for (const item of progress.applied || []) {
  const fail = reason => failures.push({id: item.id, reason});
  if (seen.has(item.id)) fail('Duplicate applied ID');
  seen.add(item.id);
  if (!authorizedIds.has(item.id)) fail('ID outside authorized scope');
  if (!reviewedIds.has(item.id)) fail('Missing visual review');
  if (!item.verifiedAfterReload) fail('Missing reload-verification receipt');
  const copy = metadata.get(item.id);
  if (!copy || item.title !== copy.proposedTitle) fail('Saved title differs from editorial copy');
  if (!item.title || item.title.length > 100 || !item.description || item.description.length > 5000) fail('Metadata length or content invalid');
  const backupPath = path.join(root, 'studio-backups', `${item.id}.json`);
  if (!fs.existsSync(backupPath)) { fail('Missing original backup'); continue; }
  const backup = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
  const oldDescription = backup.description.trimEnd();
  if (copy) {
    const expected = oldDescription.startsWith(copy.descriptionIntro.trim()) ? oldDescription : `${copy.descriptionIntro.trim()}\n\n────────────\n\n${oldDescription}`;
    if (item.description.trimEnd() !== expected) fail('Full original description or intro mismatch');
  }
  for (const url of oldDescription.match(/https?:\/\/[^\s]+/g) || []) {
    if (!item.description.includes(url)) fail(`Original URL missing: ${url}`);
  }
  if (item.privacyBefore && item.privacyAfter && item.privacyBefore !== item.privacyAfter) fail('Visibility differs');
  if (item.privacyComparison === 'rendered-value-not-surrounding-button-markup') {
    const valueFromExcerpt = text => text?.match(/^- generic: 공개 상태\n\s+- generic: ([^\n]+)/)?.[1]?.trim();
    const beforeValue = valueFromExcerpt(backup.privacyExcerpt);
    const afterValue = valueFromExcerpt(item.privacyExcerptAfter);
    if (!['공개', '일부 공개', '비공개', '회원'].includes(beforeValue) || beforeValue !== item.privacyBefore || afterValue !== item.privacyAfter) fail('Rendered visibility differs from original or saved excerpt');
    if (item.privacyExcerptBefore !== backup.privacyExcerpt) fail('Original visibility excerpt not preserved');
  }
  if (!item.privacyBefore || !item.privacyAfter) notes.push({id:item.id, note:'Privacy excerpts not serialized in initial receipt; original before/after screenshots retained.'});
  if (!item.proof || !fs.existsSync(path.join(root, item.proof))) fail('Missing saved Studio screenshot');
  const thumbnailPath = path.join(root, 'thumbnails', `${item.id}.jpg`);
  const imageReceiptPath = path.join(root, 'raw', `${item.id}.json`);
  if (!fs.existsSync(thumbnailPath) || !fs.existsSync(imageReceiptPath)) { fail('Missing image or generation receipt'); continue; }
  const hash = crypto.createHash('sha256').update(fs.readFileSync(thumbnailPath)).digest('hex');
  if (hash !== JSON.parse(fs.readFileSync(imageReceiptPath, 'utf8')).sha256) fail('Applied thumbnail file changed since image receipt');
}
const report = {checkedAt:new Date().toISOString(), applied:seen.size, total:manifest.count, remaining:manifest.count-seen.size, failures, notes};
fs.writeFileSync(path.join(root, 'apply-validation.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
if (failures.length) process.exitCode = 1;
