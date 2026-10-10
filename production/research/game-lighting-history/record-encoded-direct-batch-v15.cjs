const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const prod = 'projects/game-lighting-history-03/production';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write = (p, data) => {
  const dest = path.join(root,p), temp = dest + '.writing-' + process.pid;
  fs.writeFileSync(temp, JSON.stringify(data,null,2)+'\n'); fs.renameSync(temp,dest);
};
const requestPath = process.argv[2];
if (!requestPath) throw Error('Pass a saved direct-observation JSON, after viewing its exact boards.');
const request = read(requestPath), executionPath = prod + '/encoded-pixel-review-execution-v15.json';
const execution = read(executionPath);
if(execution.status !== 'complete' || execution.exitCode !== 0) throw Error('Extraction incomplete.');
if(sha(execution.source) !== execution.sourceSha256) throw Error('Encoded source changed.');
if(request.sourceSha256 !== execution.sourceSha256) throw Error('Observation is for another encoded source.');
const logPath = prod + '/encoded-pixel-direct-progress-v15.json';
const log = fs.existsSync(path.join(root,logPath)) ? read(logPath) : {
  source: execution.source, sourceSha256: execution.sourceSha256,
  extractionSha256: sha(executionPath), records: [], allFinalPixelsReviewed:false,
  fullAnimatedPlaybackReviewed:false, qaApproved:false, collected:false, uploaded:false
};
if(log.extractionSha256 !== sha(executionPath) || log.sourceSha256 !== execution.sourceSha256) throw Error('Preserve earlier review of different inputs.');
for(const observation of request.records) {
  const index = observation.boardIndex;
  if(!Number.isInteger(index) || index < 1 || index > execution.boards.length) throw Error('Invalid board index.');
  if(log.records.some(r => r.boardIndex === index)) throw Error('Board already recorded; preserve earlier observation.');
  const board = execution.boards[index-1];
  if(sha(board.path) !== board.sha256 || observation.boardSha256 !== board.sha256) throw Error('Board hash mismatch.');
  if(!observation.observations?.length) throw Error('Actual observations required.');
  const images = board.imageIndices.map(i => execution.images[i-1]);
  for(const im of images) if(sha(im.path) !== im.sha256) throw Error('Frame changed.');
  log.records.push({...observation, board:board.path, imageIndices:board.imageIndices,
    frames:images.map(i=>i.frame), cueIds:[...new Set(images.flatMap(i=>i.visibleCueIds))],
    directlyRead:true, reviewedAt:new Date().toISOString()});
}
log.records.sort((a,b)=>a.boardIndex-b.boardIndex);
log.boardsDirectlyRead = log.records.length;
log.totalBoards = execution.boards.length;
log.imagesDirectlyRead = log.records.reduce((n,r)=>n+r.imageIndices.length,0);
log.allBoardsDirectlyRead = log.records.length === execution.boards.length;
log.unresolved = log.records.flatMap(r => (r.unresolved||[]).map(issue=>({boardIndex:r.boardIndex,issue})));
log.updatedAt = new Date().toISOString();
write(logPath,log);
console.log(JSON.stringify({boards:log.boardsDirectlyRead,total:log.totalBoards,images:log.imagesDirectlyRead,
  unresolved:log.unresolved.length,allFinalPixelsReviewed:log.allFinalPixelsReviewed}));
