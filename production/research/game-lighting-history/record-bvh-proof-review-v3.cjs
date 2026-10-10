const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const rel='production/research/game-lighting-history/local/bvh-proof-v3/qa/extraction.json',r=read(rel);
for(const x of[r.video,r.renderedModel,...r.frames,...r.boards])if(sha(x.path)!==x.sha256)throw Error('Rendered input changed');
if(r.renderedModel.sha256!==sha('motion-canvas/src/projects/game-lighting-history-03/spatial/bvh-model-v1.tsx'))throw Error('Current model not rendered');
const record={reviewedAt:new Date().toISOString(),scope:'24-second model-motion proof for all8paragraphs of scene13a only; final full narration and body timeline not approved',
 style:'research-black-v1',extraction:{path:rel,sha256:sha(rel)},model:r.renderedModel,video:r.video,
 boards:r.boards.map(x=>({...x,directlyViewed:true})),directlyReadPoseFrames:r.frames,
 observations:[
  'All8paragraphs start/middle/end frames directly viewed. Projected top/side faces,12XYZ edges, triangle depth and moving ray point are present.',
  'Tree parent and both child branches/labels visible; visited versus skipped branches differ by purpose/color.',
  'Computed x[2,6],y[3,5],z[4,7] overlap[4,5]. Moving z reaches[8,9], no overlap; all interval lengths/labels follow actual computed values.',
  'Triangle goes from a computed hit to a miss while the conservative tight box still passes. Closest/any rails carry independent opaque examples and explicit tMax/alpha limitation.',
  'Looser conservative box remains outside the tight box and now above the equation/parameter warning. Cost blocks carry labels and an explicit non-benchmark caveat.',
  'Black background, white text, restrained yellow/teal/orange/RGB semantic emphasis; boxed captions stay at0,430. Final narration captions and word timing remain separate.'
 ],
 history:[{version:'v1',result:'rejected',reason:'Missing Node.add children, wrong moving z upper bound, overlapping interval labels and query description; preserved local snapshot'},
 {version:'v2',result:'rejected-for-final-use',reason:'All24poses directly read; paragraph7 loose-wire lower edges crossed ray equation/parameter warning; preserved local snapshot'}],
 numericalEvidence:{path:'projects/game-lighting-history-03/production/bvh-math-check-v1.json',sha256:sha('projects/game-lighting-history-03/production/bvh-math-check-v1.json'),cases:7},
 primarySources:['https://www.pbr-book.org/4ed/Shapes/Basic_Shape_Interface','https://pbr-book.org/4ed/Primitives_and_Intersection_Acceleration/Bounding_Volume_Hierarchies'],
 modelMotionProofReviewed:true,wholeDecodeExitCode:r.wholeDecode.exitCode,observedFrames:r.observedFrames,plannedProofFrames:r.plannedFrames,
 proofEndpointExtraFrames:r.endpointDifference,finalTrimAndPtsVerified:false,allEpisodePixelsReviewed:false,finalNarrationTimed:false,finalVideoApproved:false,newRasterGitAdded:0,localOnly:true};
const out='projects/game-lighting-history-03/production/bvh-animated-proof-review-v3.json';fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({record:out,reviewedProofPoses:24,finalVideoApproved:false}));
