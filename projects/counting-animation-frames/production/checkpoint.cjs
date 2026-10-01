const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const file = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const queue = JSON.parse(fs.readFileSync(file, 'utf8'));
const item = queue.items.find(item => item.slug === 'counting-animation-frames');
if(item.videoId || item.checkpoints.render || item.checkpoints.narration) throw Error('Existing production checkpoint: resume current queue; never reset completed or running stages.');
item.status = 'in-production';
item.stage = 'script-complete-narration-starting';
item.startedAt ||= new Date().toISOString();
item.updatedAt = new Date().toISOString();
item.checkpoints.script = true;
item.checkpoints.originalScript = true;
item.paths = {
  project: 'projects/counting-animation-frames/project.json',
  script: 'projects/counting-animation-frames/script/narration.ko.json',
  sources: 'projects/counting-animation-frames/sources/game-candidates.json',
};
item.localProgress = {originalBilingualScript: true, narration: 'not yet synthesized', finalRender: false, upload: false};
item.activeExecution ||= {};
item.nextAction = 'Single approved-voice synthesis; verify fresh official gameplay sources and implement Frame Timing Lab. Render/QA/collect/private upload/Git delivery are still pending.';
queue.currentSlug = item.slug;
queue.updatedAt = item.updatedAt;
const previous = queue.items.find(item => item.slug === 'meaningful-quests');
previous.publishing.receipt = 'projects/meaningful-quests/publishing/youtube-upload.json';
previous.localProgress.upload = true;
fs.writeFileSync(file, JSON.stringify(queue, null, 2) + '\n');
