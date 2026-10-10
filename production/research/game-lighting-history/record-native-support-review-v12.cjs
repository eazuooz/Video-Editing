const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',p='projects/game-lighting-history-03';
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const notes={
 'nanite-support':[
  '260–262 small camera change,263–268 nearly unchanged facade; changing counters alone are not action.',
  '269–277 facade hold; exclude.',
  '278 same facade,279–281 small camera shift,282–286 hold.',
  '287–294 hold;295 starts rapid camera movement.',
  '296–304 active temple/rock/sky camera; native counters visible.',
  '305–307 camera,308–310 hold,311–313 subtle movement.',
  '314–317 hold,318–322 active rock camera.',
  '323–331 active entrance-to-cave movement.',
  '332–340 cave and opening camera;338–339 near-hold.',
  '341–346 active floor/opening camera;347–349 near-hold.',
  '350–358 cave-to-door-to-facade camera;353–354 near-hold.',
  '359–367 facade-to-dark-ornament/bicycle camera;364–366 near-hold.',
  '368–372 ornament camera;373 one gray/broken diagnostic frame, exact mode unknown, exclude;374–376 lit camera.',
  '377–385 ornament/bicycle/floor camera;378–379 near-hold.',
  '386–394 active ornament/bicycle/detail/floor camera.',
  '395–403 active bicycle spokes/crank/wheels/tubes/floor; no geometry deformation demonstrated.',
  '404–405 bicycle movement,406–408 wheel hold,409 small shift,410–412 floor camera.',
  '413–418 bicycle/ornament camera;419–421 ornament hold.',
  '422–425 close ornament camera,426–427 hold,428 shift,429–431 near-hold.',
  '432–439 active ornament-to-dark-corridor-to-daylight camera.',
  '440–443 active statue rows/facade camera.',
  '528–536 active pillar/statue-row camera with foreground occlusion.',
  '537–545 active carved facade/pillar/arch camera.',
  '546–554 active close relief/pillar-to-statue camera.',
  '555–563 active facade/rows/columns camera.',
  '564–566 bicycle approach;567–572 nearly unchanged bicycle view, exclude.',
  '573 same bicycle near-hold, exclude.'
 ],
 'lighting-support':[
  '108–114 editor near-hold,115 PIE starts dark,116 moving sunlight/illumination visible.',
  '117–120 moving sunlight and cast shadows inside boxes,121 returns to editor,122–123 hold. Native Light Anim button visible; no update-latency measurement.',
  '157–158 lit boxes,159 becomes dark while postprocess menu changes,160–164 dark/menu,165 lit return. Exact selected GI item needs raw label verification.',
  '166–169 hold,170 camera reframes both boxes,171–174 near-hold.',
  '175–177 hold,178–181 volume selected and settings visible,182 lighting darkens with volume/details change; no exact checkbox claim.',
  '183–192 long unchanged dark box view; exclude.',
  '105–107 black shadow artifact in source;108 normal shadow view returns,109–112 hold,113 camera starts orbit. Do not present artifact as controlled benchmark.',
  '114–122 active reflective-sphere/cubes/shadow camera.',
  '123–132 mostly unchanged sphere view and postprocess selection; exclude prolonged hold.',
  '133 camera approaches cylinder,134–136 camera,137–139 holds,140 Source Angle field adjustment and softer-looking cylinder shadow.',
  '141–149 source directional-light parameter edits with similar camera; exact numerical effect not measured.',
  '150–153 cylinder hold;154 cut to point light and blue box.',
  '243 camera,244–251 near-hold on reflective sphere/postprocess properties.',
  '252–259 menu/view hold;260–261 reflective-sphere camera changes. No exact reflection method inferred from unreadable menu.',
  '262–263 active sphere approach.',
  '305–306 sphere hold,307–309 approach,310–311 near-hold,312–313 camera retreat.',
  '314–318 active camera around cubes/sphere,319–321 sphere hold,322 broad scene return.',
  '323–331 prolonged scene hold; exclude.',
  '332–333 scene hold;exclude.'
 ]
};
const records=[];
for(const group of Object.keys(notes)){
 const input=b+'/local/native-action-support-v12-'+group+'/execution.json',a=JSON.parse(fs.readFileSync(path.join(root,input),'utf8'));
 if(a.status!=='action-sequences-ready')throw Error('Completed extraction required');
 let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(board=>{if(sha(board.path)!==board.sha256)throw Error('Board changed');for(const s of board.samples)if(sha(s.path)!==s.sha256)throw Error('Sample changed');return {...board,directlyViewed:true,note:notes[group][i++]};})}));
 if(i!==notes[group].length)throw Error('Review count mismatch');
 const output=p+'/production/native-'+group+'-direct-review-v12.json';if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing review');
 const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},reviewed,boardCount:i,temporalSampleCount:a.completed.reduce((n,r)=>n+r.frames,0),allBoardsDirectlyViewed:true,allTemporalSamplesDirectlyViewed:true,method:'Every 1fps temporal sample and board directly read; exact encoded in/out, continuous motion and final caption pixels remain separate.',continuousFullMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,sourceAudioUsed:false,newGitRasterCount:0,localOnly:true};
 fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');records.push({path:output,sha256:sha(output),boards:i,frames:record.temporalSampleCount});
}
const cpath=path.join(root,b,'checkpoint.json'),c=JSON.parse(fs.readFileSync(cpath,'utf8'));c.updatedAt=new Date().toISOString();c.ownedActiveWork=[];c.ownedJobsRunning=[];c.episode03NativeSupportReview={records,boards:46,temporalSamples:382,allBoardsDirectlyViewed:true,continuousFullMotionReviewed:false,finalUseApproved:false};c.completedNativeSupportExtractions=Object.keys(notes).map(group=>{const f=b+'/local/native-action-support-v12-'+group+'/execution.json',a=JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));return{evidence:f,sha256:sha(f),pid:a.parentPid,command:a.command,status:a.status,completedAt:a.completedAt,exit0Observed:true,threads:2,gpuJobs:0,repeatRequired:false};});c.completedNativeSupportExtraction.directlyReviewed=true;c.next='Refine exact unique native selections and independent KO/EN observation guides using all169 temporal boards/1433 samples; preserve original84 PCM and all useful spatial math. Current duplicate review and one cooperative GPU handoff before new guideTTS. All4 final video delivery pending.';fs.writeFileSync(cpath,JSON.stringify(c,null,2)+'\n');console.log(JSON.stringify({records,boards:46,frames:382,newTtsStarted:false}));
