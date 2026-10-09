const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p,v) => fs.writeFileSync(path.join(root,p), JSON.stringify(v,null,2)+'\n');
const statePath='projects/similar-game-design/production/unresolved-brotato-cut-extraction-v3.json';
const state=read(statePath);
if(state.exitCode!==0 || state.status!=='closed-unresolved-source-cut-extraction-awaiting-direct-review') throw new Error('Extraction is not closed successfully.');
const out='projects/similar-game-design/production/unresolved-brotato-cut-direct-review-v3.json';
if(fs.existsSync(path.join(root,out))) throw new Error('Preserve existing review.');
const now=new Date().toISOString();
const observations={
  'brotato-full-release': {
    actualCuts:[309,1223,2654,2953],
    cutObservations:{309:'Grey-ground robot shot cuts to brown-ground crowned avatar with blades.',1223:'Brown crowned-avatar shot cuts to grey-ground avatar with guns; this is a separate build/context.',2654:'Grey gunfire shot cuts to green-grey ground with a different avatar and large red enemy.',2953:'Green-grey crowded encounter cuts to brown-ground single avatar in a separate shot.'},
    sameShot:'All other detected triples directly retain their ground, avatar/build, enemy arrangement and camera continuity; red laser warnings, white hit flashes, yellow electricity or damage numbers cause detection. They are gameplay effects, not edits.'
  },
  'brotato-local-coop': {
    actualCuts:[2555,2902],
    cutObservations:{2555:'Brown-ground co-op shot cuts to grey-ground co-op shot with different combat setup.',2902:'Grey-ground shot cuts to brown-ground shot with different avatar/enemy arrangement.'},
    sameShot:'All other triples directly retain the same brown-ground co-op encounter. Laser warnings, hit flashes and changing damage numbers are effects inside a shot.'
  }
};
let boardCount=0, frameCount=0;
const sources=state.sources.map(source=>{
  const id=source.stem;
  const key=id || (source.boards[0].path.includes('brotato-local-coop')?'brotato-local-coop':'brotato-full-release');
  const note=observations[key]; if(!note) throw new Error('Unknown source '+key);
  const boards=source.boards.map(b=>{if(sha(b.path)!==b.sha256) throw new Error('Board changed '+b.path);boardCount++;return {...b,directlyRead:true,reviewedAt:now};});
  for(const f of source.frameEntries){if(sha(f.path)!==f.sha256) throw new Error('Frame changed '+f.path);frameCount++;}
  return {id:key,boards,frames:source.frameEntries,actualHardCuts:note.actualCuts.map(frame=>({sourceFrame:frame,sourceSeconds:frame/60,observation:note.cutObservations[frame]})),otherCandidates:note.sameShot,allBoardsDirectlyRead:true};
});
if(boardCount!==50 || frameCount!==293) throw new Error('Unexpected coverage '+boardCount+'/'+frameCount);
const proof={schemaVersion:1,reviewedAt:now,extraction:statePath,extractionSha256:sha(statePath),sources,allBoardsDirectlyRead:true,actualBoardCount:boardCount,actualFrameCount:frameCount,newHardCutCount:6,oldFiveSoloCutTriplesPreserved:true,detectorThreshold:0.08,detectorAloneUsedForApproval:false,wholeSourceDecodeRepeated:false,localOnly:true,imagesGitAdded:0,finalSourceAllocationApproved:false,allFinalPixelsReviewed:false,scope:'Direct native source cut/effect discrimination only. Selected interval endpoints, narration alignment, crop/caption and final encoded pixels remain pending.'};
write(out,proof);
state.sources.forEach(s=>{s.boards.forEach(b=>{b.directlyRead=true;b.reviewedAt=now;});s.allBoardsDirectlyRead=true;});
state.actualExitObserved=true;state.observedSessionId=2324;state.allBoardsDirectlyRead=true;state.directReview=out;state.directReviewSha256=sha(out);state.status='closed-source-cut-discrimination-direct-reviewed';write(statePath,state);
const cpPath='projects/similar-game-design/production/latest-checkpoint.json';const cp=read(cpPath);
cp.updatedAt=now;cp.stage='current24-native-source-cuts-direct-reviewed-awaiting-73paragraph-measured-allocation';cp.unresolvedBrotatoCutReview={path:out,boards:50,frames:293,newHardCuts:6,wholeSourceDecodeRepeated:false};write(cpPath,cp);
console.log('50 boards / 293 frames directly read and hashes verified; 6 new hard cuts separated from gameplay effects.');
