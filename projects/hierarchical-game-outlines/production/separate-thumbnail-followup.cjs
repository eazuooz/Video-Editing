// Record the user's non-blocking thumbnail instruction without changing media or Studio.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p, x) => fs.writeFileSync(path.join(root, p), JSON.stringify(x, null, 2) + '\n');
const now = new Date().toISOString();
const slug = 'hierarchical-game-outlines';
const base = `projects/${slug}`;
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath), receipt = read(`${base}/publishing/youtube-upload.json`);
const manifest = read(`${base}/project.json`), checkpoint = read(`${base}/production/latest-checkpoint.json`);
const item = queue.items.find(x => x.slug === slug);
if (receipt.videoId !== 'lEwpxP_qsDY' || !receipt.uploadedPrivate || !item.checkpoints.qa || !item.checkpoints.collected) {
  throw Error('Expected the existing reviewed, collected and privately saved video.');
}
const authority = '이건 왜 멈춘거야? 썸네일 빼고 나머지 진행하고 썸네일 나중에 해도 되잖아';
const followup = {
  slug, videoId: receipt.videoId, type: 'custom-thumbnail', status: 'pending-platform-daily-limit',
  blockingProduction: false, authority, recordedAt: now,
  preparedFile: `${base}/publishing/thumbnail.png`,
  sha256: '6a3093d88ae62e7e05457f52280bb2c99d024f1742111aa42360a823fb83af68',
  limitObservedAt: '2026-10-03T14:50:04.773Z', retryNotBefore: '2026-10-04T14:50:04.773Z',
  evidence: `${base}/publishing/proof/thumbnail-daily-limit.png`,
  nextAction: 'Retry the prepared thumbnail through normal Studio UI after retryNotBefore; save and reopen to verify. Preserve the existing private video and do not reupload.'
};
const nextAction = 'Finish selected production commit and normal push now; then continue game-reward-planning preflight and subsequent production. Thumbnail is an independent non-blocking follow-up; fullSettingsVerified remains false until actual thumbnail save/reopen.';
receipt.productionContinuation = {authorizedAt: now, userEvidence: authority, thumbnailBlocksProduction: false};
receipt.publishingFollowups = [followup];
receipt.nextAction = nextAction;
receipt.fullSettingsVerified = false;
receipt.completed = false;
receipt.gitDelivery = {...receipt.gitDelivery, status: 'pending-production-commit-thumbnail-followup', complete: false, pushVerified: false};
manifest.status = 'rendered-QA-collected-private-saved-thumbnail-followup';
manifest.publishing.publishingFollowups = [followup];
manifest.publishing.thumbnailBlocksProduction = false;
item.status = 'uploaded-private-thumbnail-pending';
item.stage = 'production-git-delivery';
item.blockers = [];
item.publishing.followups = [followup];
item.gitDelivery = {...item.gitDelivery, status: 'pending-production-commit-thumbnail-followup', complete: false, pushVerified: false};
item.nextAction = nextAction;
item.updatedAt = now;
item.execution.activeTasks = [];
item.execution.phase = 'production-git-delivery';
item.execution.status = 'thumbnail-followup-does-not-block';
item.execution.updatedAt = now;
queue.publishingFollowups = [...(queue.publishingFollowups || []).filter(x => !(x.slug === slug && x.type === 'custom-thumbnail')), followup];
queue.continuationPolicy = {updatedAt: now, userEvidence: authority, thumbnailBlocksNextProduction: false, requireActualFullSettingsEvidence: true};
queue.automation.checkpointPromptUpdatedAt = now;
queue.automation.checkpointPromptVerified = 'Native automation24 update confirmed ACTIVE/hourly; thumbnail follow-up is non-blocking. Commit/push current production and proceed to next preflight while preserving fullSettingsVerified=false.';
queue.progress.productionRendered = queue.items.filter(x => x.checkpoints.render).length;
queue.progress.productionCollected = queue.items.filter(x => x.checkpoints.collected).length;
queue.progress.privateSaved = queue.items.filter(x => x.checkpoints.privateUploadSaved || x.checkpoints.uploaded).length;
queue.progress.publishingFollowups = queue.publishingFollowups.filter(x => x.status.startsWith('pending')).length;
queue.updatedAt = now;
checkpoint.previousCheckpoint = checkpoint.checkpointPath;
checkpoint.observedAt = now;
checkpoint.checkpointPath = `${base}/production/checkpoint-${now.replace(/[-:.]/g, '')}.json`;
checkpoint.status = 'production-git-delivery-thumbnail-nonblocking';
checkpoint.publishingFollowups = [followup];
checkpoint.finalVideo.productionDeliveredWithThumbnailFollowup = false;
checkpoint.activeTasks = [];
checkpoint.pending = checkpoint.pending.filter(x => !/Prepared custom thumbnail|Selected per-video/.test(x));
checkpoint.pending.unshift('Custom thumbnail is a non-blocking follow-up; retry normal UI not before2026-10-04T14:50:04.773Z.', 'Selected production commit/push now; next preflight can proceed independently of thumbnail.');
checkpoint.nextAction = nextAction;
checkpoint.gitDelivery = {...checkpoint.gitDelivery, status: 'pending-production-commit-thumbnail-followup', complete: false, pushVerified: false};
item.execution.runtimeCheckpoint = checkpoint.checkpointPath;
item.execution.latestCheckpoint = `${base}/production/latest-checkpoint.json`;
write(`${base}/publishing/youtube-upload.json`, receipt);
write(`${base}/project.json`, manifest);
write(checkpoint.checkpointPath, checkpoint);
write(`${base}/production/latest-checkpoint.json`, checkpoint);
write(queuePath, queue);
console.log(JSON.stringify({slug, checkpoint: checkpoint.checkpointPath, thumbnailBlocksProduction: false, fullSettingsVerified: false}));
