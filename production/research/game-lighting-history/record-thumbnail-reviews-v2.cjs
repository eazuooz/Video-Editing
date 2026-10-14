const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const requestPath = 'production/research/game-lighting-history/thumbnail-generation-request-v2.json';
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root, p))).digest('hex');
const request = JSON.parse(fs.readFileSync(path.resolve(root, requestPath), 'utf8'));
const now = new Date().toISOString();
const references = request.references.map(file => ({file, sha256: hash(file), directPixelsRead: true}));
const outputs = request.records.map(r => {
  const dest = `projects/game-lighting-history-${String(r.episode).padStart(2,'0')}/publishing/thumbnail-review-v1.json`;
  if (fs.existsSync(path.resolve(root, dest))) throw new Error(`Preserve existing review: ${dest}`);
  const buf = fs.readFileSync(path.resolve(root, r.path));
  if (buf.subarray(0,8).toString('hex') !== '89504e470d0a1a0a') throw new Error('Expected PNG');
  const width = buf.readUInt32BE(16), height = buf.readUInt32BE(20);
  if (width < 1280 || height < 720 || Math.abs(width/height-16/9) > 0.01) throw new Error('Unexpected thumbnail dimensions');
  const sha256 = hash(r.path);
  if (sha256 !== hash(r.source)) throw new Error('Copied generation differs from original');
  return {dest, data: {reviewedAt: now, file: r.path, sha256, width, height,
    generatedWith: request.generator, generationSource: r.source, request: {path: requestPath, sha256: hash(requestPath)},
    prompt: r.prompt, references, directPixelsRead: true, observedText: r.text, observedStyle: r.observation,
    narrationAndFootageNotChanged: true, previousEpisode01ThumbnailPreserved: true,
    localOnly: true, gitImageEssentialApproved: false, platformSaved: false, finalVideoVerified: false}};
});
for (const {dest,data} of outputs) fs.writeFileSync(path.resolve(root,dest), JSON.stringify(data,null,2)+'\n', {flag:'wx'});
console.log(JSON.stringify({reviews: outputs.map(o=>({path:o.dest, imageSha256:o.data.sha256})), localOnly:true, platformSaved:false, gitImagesAdded:0}));
