const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..', 'output', 'youtube-library-refresh');
const v2 = path.join(root, 'v2');
const read = name => JSON.parse(fs.readFileSync(path.join(v2, name), 'utf8'));
const status = read('review-status.json');
const progress = read('apply-progress.json');
const manifest = read('prompts.json');
// Keep a per-ID verification ledger so a stale browser-runtime cache cannot
// erase previously verified application receipts from the aggregate file.
const receiptRoot = path.join(v2, 'applied-receipts');
fs.mkdirSync(receiptRoot, {recursive:true});
const authorizedIds = new Set(manifest.items.map(x => x.id));
for (const receipt of progress.applied || []) {
  if (!receipt.verifiedAfterReload || !authorizedIds.has(receipt.id)) continue;
  const receiptPath = path.join(receiptRoot, `${receipt.id}.json`);
  if (!fs.existsSync(receiptPath)) fs.writeFileSync(receiptPath, JSON.stringify(receipt,null,2)+'\n', {flag:'wx'});
}
const mergedReceipts = new Map((progress.applied || []).map(x => [x.id,x]));
for (const name of fs.readdirSync(receiptRoot).filter(x => /^[\w-]{11}\.json$/.test(x))) {
  const receipt = JSON.parse(fs.readFileSync(path.join(receiptRoot,name),'utf8'));
  if (!receipt.verifiedAfterReload || !authorizedIds.has(receipt.id)) continue;
  const current = mergedReceipts.get(receipt.id);
  if (current && (current.title !== receipt.title || current.description !== receipt.description)) throw new Error(`Conflicting verified receipt ${receipt.id}`);
  if (!current) mergedReceipts.set(receipt.id,receipt);
}
progress.applied = [...mergedReceipts.values()];
progress.appliedCount = progress.applied.length;
if (progress.pending && mergedReceipts.has(progress.pending.id)) delete progress.pending;
const appliedIds = new Set((progress.applied || []).map(x => x.id));
if (progress.confirmationRequired?.status === 'awaiting-human-at-action-time') {
  const remainingConfirmationIds = progress.confirmationRequired.videoIds.filter(id => !appliedIds.has(id));
  if (!remainingConfirmationIds.length) progress.confirmationRequired.status = 'fulfilled-by-verified-saves';
}
const awaitingConfirmation = progress.confirmationRequired?.status === 'awaiting-human-at-action-time';
const generated = manifest.items.filter(x => fs.existsSync(path.join(v2, 'thumbnails', `${x.id}.jpg`)));
progress.checkpoint = {applied:appliedIds.size,generated:generated.length,total:manifest.count,remaining:manifest.count-appliedIds.size,heartbeatId:'382',stage:appliedIds.size===manifest.count?'all-verified':awaitingConfirmation?'awaiting-at-action-time-confirmation':'continue-next-distinct-generation-batch'};
progress.updatedAt = new Date().toISOString();
fs.writeFileSync(path.join(v2,'apply-progress.json'),JSON.stringify(progress,null,2)+'\n');
status.updatedAt = new Date().toISOString();
status.totalTargetVideos = manifest.count;
status.generatedVideos = generated.length;
status.pendingGeneration = manifest.count - generated.length;
status.publicChangesSaved = appliedIds.size;
status.remainingPublicChanges = manifest.count - appliedIds.size;
status.nextStep = appliedIds.size === manifest.count
  ? 'All scoped videos saved and verified; stop the thread heartbeat.'
  : awaitingConfirmation
    ? `Await human action-time confirmation for the prepared ${progress.confirmationRequired.videoIds.length} existing-video edits. No Save clicks until confirmation; preserve the existing prepared draft and do not repeat the question on unchanged heartbeats.`
    : 'Continue approved distinct-image generation, copy review, Studio saves, and reload verification.';
if (progress.confirmationRequired) status.confirmationRequired = progress.confirmationRequired;
status.userAuthorization = {
  date: '2026-10-01',
  message: '응 좋아 아주 진행해줘~계속 쭈욱 밤새도록 다 바꿀때까지',
  scope: '382 videos, excluding every member of C++ basics, basic data structures/algorithms, and game design playlists; thumbnails, titles, and description introductions only.',
  heartbeatId: '382',
};
if (status.preparedStudioDraft) status.preparedStudioDraft.saved = appliedIds.has(status.preparedStudioDraft.id);
status.pendingStudioDraft = progress.pending && !appliedIds.has(progress.pending.id) ? progress.pending : null;
fs.writeFileSync(path.join(v2, 'review-status.json'), JSON.stringify(status, null, 2) + '\n');
console.log(JSON.stringify({generated: generated.length, applied: appliedIds.size, total: manifest.count, pendingStudioDraft: status.pendingStudioDraft}));
