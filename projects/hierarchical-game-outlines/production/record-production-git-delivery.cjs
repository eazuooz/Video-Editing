// Record a verified normal push and release the next production independently of thumbnail.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const git = args => execFileSync('git', args, {cwd: root, encoding: 'utf8', windowsHide: true}).trim();
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p,x) => fs.writeFileSync(path.join(root,p), JSON.stringify(x,null,2)+'\n');
const commit = git(['rev-parse','HEAD']);
const remote = git(['ls-remote','origin','refs/heads/main']).split(/\s+/)[0];
if (commit !== remote) throw Error('Remote main does not match the delivered commit.');
const now = new Date().toISOString(), base = 'projects/hierarchical-game-outlines';
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath), item = queue.items.find(x=>x.slug==='hierarchical-game-outlines');
const next = queue.items.find(x=>x.slug==='game-reward-planning');
const receipt = read(`${base}/publishing/youtube-upload.json`), checkpoint = read(`${base}/production/latest-checkpoint.json`);
if (item.gitDelivery?.complete) {
  console.log(JSON.stringify({alreadyDelivered: true, productionCommit: item.gitDelivery.productionCommit, currentSlug: queue.currentSlug, thumbnailBlocksProduction: false}));
  process.exit(0);
}
const delivery = {
  schemaVersion: 1, slug: item.slug, observedAt: now, status: 'production-delivered-thumbnail-followup',
  complete: true, productionCommit: commit, commit, branch: 'main', remote: 'origin/main',
  normalPush: {command:'git push origin main', exitCode:0, previous:'0eb40b345a80f7c1cb216cbc0e03f890c79bbf53', current:commit},
  remoteSha: remote, localSha: commit, remoteMatches: true, pushVerified: true,
  thumbnailPending: true, fullSettingsVerified: false,
  authority: '이건 왜 멈춘거야? 썸네일 빼고 나머지 진행하고 썸네일 나중에 해도 되잖아',
  checks: `${base}/production/git-pre-delivery-checks.json`,
  selection: `${base}/production/git-delivery-selection.json`,
  policy: 'Production/private-save/Git delivery is complete. Prepared thumbnail remains a normal-UI follow-up; do not claim all platform settings complete.'
};
write(`${base}/production/final-v1/git-delivery.json`,delivery);
item.gitDelivery = delivery;
item.checkpoints.gitDelivery = true;
item.checkpoints.productionDelivered = true;
item.checkpoints.publishingSettingsVerified = false;
item.stage = 'production-delivered-thumbnail-followup';
item.nextAction = 'Apply prepared thumbnail through normal UI after2026-10-04T14:50:04.773Z; next production proceeds separately.';
item.updatedAt = now;
receipt.gitDelivery = delivery;
receipt.productionDeliveredWithThumbnailFollowup = true;
receipt.nextAction = item.nextAction;
receipt.completed = false;
receipt.fullSettingsVerified = false;
checkpoint.observedAt = now;
checkpoint.previousCheckpoint = checkpoint.checkpointPath;
checkpoint.checkpointPath = `${base}/production/checkpoint-${now.replace(/[-:.]/g,'')}.json`;
checkpoint.status = 'production-delivered-thumbnail-nonblocking';
checkpoint.finalVideo.gitDelivered = true;
checkpoint.finalVideo.productionDeliveredWithThumbnailFollowup = true;
checkpoint.gitDelivery = delivery;
checkpoint.pending = checkpoint.pending.filter(x=>!/^Selected production commit/.test(x));
checkpoint.nextAction = 'Next game-reward-planning preflight proceeds now; thumbnail remains a separate non-blocking follow-up. Preserve all completed media.';
item.execution.runtimeCheckpoint = checkpoint.checkpointPath;
next.status = 'in-progress';
next.stage = 'preflight-content-and-studio-review';
next.updatedAt = now;
next.execution = {...next.execution, phase:'preflight', status:'reviewing', activeTasks:[], noTts:true, noNewScript:true, overviewRequiredForNewProduction:true};
next.nextAction = 'Review full source concept, all existing inventory, related full KO/EN scripts and current Studio matches; establish current distinct --check before any new narration/TTS/scenes. Overview required for subsequent new production.';
queue.currentSlug = next.slug;
queue.progress.rendered = queue.items.filter(x=>x.checkpoints.render).length;
queue.progress.collected = queue.items.filter(x=>x.checkpoints.collected).length;
// Older delivered entries use status/receipt rather than the newer checkpoint keys.
const privatelySaved = queue.items.filter(x=>x.status.startsWith('uploaded-private'));
queue.progress.uploaded = privatelySaved.length;
queue.progress.privateSaved = privatelySaved.length;
queue.progress.fullSettingsDelivered = 8;
queue.progress.productionDelivered = privatelySaved.length;
queue.progress.productionGitDelivered = privatelySaved.length;
queue.progress.inProgress = queue.items.filter(x=>x.status==='in-progress').length;
queue.progress.queued = queue.items.filter(x=>x.status==='queued').length;
queue.progress.remainingProduction = queue.progress.inProgress + queue.progress.queued;
queue.lastProgressAt = queue.updatedAt = now;
write(`${base}/publishing/youtube-upload.json`,receipt);
write(checkpoint.checkpointPath,checkpoint);
write(`${base}/production/latest-checkpoint.json`,checkpoint);
write(queuePath,queue);
console.log(JSON.stringify({productionCommit:commit,remoteMatches:true,currentSlug:queue.currentSlug,thumbnailBlocksProduction:false}));
