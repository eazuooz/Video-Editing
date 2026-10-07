const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'../../..');process.chdir(ROOT);
const sources={ 'motion-sickness-games':'final-v1','hierarchical-game-outlines':'final-v1','game-reward-planning':'measured-edit-v3','avoid-game-comparisons':'final-v1','making-game-sequels':'final-v2','familiar-game-rules':'final-v1'};
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const [slug,version] of Object.entries(sources)){
 const source=`projects/${slug}/production/${version}/plan.json`,plan=read(source),rows=[];let cursor=0;
 const dest=`motion-canvas/src/projects/${slug}/depth-reel-plan-v1.json`;
 if(fs.existsSync(dest)){if(read(dest).sourcePlanSha256!==sha(source))throw Error('Existing plan source changed');console.log(slug,'existing prepared plan preserved');continue;}
 const ko=read(`projects/${slug}/script/narration.ko.json`),en=read(`projects/${slug}/script/narration.en.json`);
 if(slug==='familiar-game-rules')for(const [lang,target] of [['ko',ko],['en',en]])target.scenes.push(...read(`projects/${slug}/script/observation-guides.${lang}.json`).scenes);
 const add=(id,sceneId,frames,start,starts,originalFile=null)=>{
  const row={id,sceneId,frames,startFrame:start,reelStartFrame:cursor,paragraphStarts:starts,originalFile,ko:ko.scenes.find(s=>s.id===sceneId)?.lines,en:en.scenes.find(s=>s.id===sceneId)?.lines};
  if(!row.ko||!row.en)throw Error('Bilingual source missing');rows.push(row);cursor+=frames;
 };
 if(plan.whiteSegments){for(const s of plan.whiteSegments){add(s.id,s.id,s.frames,s.finalStartFrame,[0]);}}
 else for(const s of plan.scenes){
  if(s.classification==='explanation')add(s.id,s.id,s.frames,s.startFrame,s.paragraphs.map(p=>Math.round(p.start*60)),`projects/${slug}/production/${version}/explanation-${s.id}.mp4`);
  else for(const w of s.segments||[])if(w.classification==='explanation'){
   const local=w.startFrame-s.startFrame;const starts=(s.speechEvidence||[]).map(p=>Math.round(p.speechStart*60)-local).filter(f=>f>=0&&f<w.frames);
   add(w.id,s.id,w.frames,w.startFrame,[0,...starts.filter(f=>f>0)],w.video||null);
  }
 }
 if(cursor!==plan.explanationFrames)throw Error(slug+' white totals differ');
 fs.writeFileSync(dest,JSON.stringify({slug,fps:60,totalFrames:cursor,finalFrames:plan.totalFrames||plan.finalFrames,sourcePlan:source,sourcePlanSha256:sha(source),rows},null,2)+'\n');
 console.log(slug,rows.length,cursor);
}
