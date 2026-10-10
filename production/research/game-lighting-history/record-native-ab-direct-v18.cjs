const fs=require('node:fs'),crypto=require('node:crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prod='projects/game-lighting-history-03/production',p=prod+'/native-repair-ab-pixel-execution-v18.json',x=JSON.parse(fs.readFileSync(p));
if(x.status!=='complete'||x.exitCode!==0||x.boards.length!==19||x.images.length!==112)throw Error('Incomplete extraction');
const notes=[
'BF moving street/car reflection, fire/reflected eye and water replace the opening promotional portion. Fixed cues62/63 readable. These images illustrate hardware RT results, not measured acceleration or internal intersection implementation.',
'Eye and water then outdoor explosion; fixed cues62/63 readable and source identity retained. No numerical performance inference.',
'BF aircraft/water followed by Control split comparison; top lifted source labels distinguish original DLSS and DLSS2.0 Quality/RTX2060/1080p/High.',
'Control cue107/108: moving character and wall lettering; lifted original quality/hardware labels remain above captions, and source green comparison rectangles retained.',
'Control cue108/109: wall lettering transitions to rotating fan comparison. Top labels remain readable. Early versus DLSS2 distinction remains in narration.',
'Deliver helmet/glove comparison at cue113 before room/wall details. Original OFF/ON Quality, RTX2060,1080p/Epic and 2xZOOM remain visible above fixed captions.',
'Deliver room then helmet/glove; cue114 explains conditions. Source green rectangles identify the helmet edge and glove, top mode labels readable.',
'Deliver magnified glove/helmet and wall then room. Cues114/115 readable with source2xZOOM; no repeated source frames in plan.',
'Deliver room/table/wall detail; cues115/116 readable, retained source green rectangles begin selecting the table.',
'Deliver enlarged table/prop comparison; source2xZOOM and conditions readable with cue116. No claim that this is native-resolution footage.',
'Deliver cue117 limitation remains readable; transition to Wolf split comparison with original OFF/ON Quality/RTX2060/1080p/Uber and source2xZOOM.',
'Wolf indoor lights and outdoor bicycle/wall under cue127/128: boundary details and original conditions readable.',
'Wolf bicycle boundary then indoor thin lights under cue129. Fixed captions and lifted conditions readable.',
'UNRESOLVED: cue130 says branches behind the aim, but exact f34100/34187/34275 still show interior barrels. Chosen source39 begins too early; move only this473-frame cut to directly verified branch/aim footage. No approval of this semantic mismatch.',
'Wolf outside branches and changing aim under cue131, source green boxes and original mode labels readable. This does not resolve the preceding cue130 mismatch.',
'Wolf indoor light strings under general temporal-boundary cue131/132; mathematical internals are not inferred from appearance.',
'Wolf indoor magnified thin lights under cue132; source2xZOOM and OFF/ON labels remain clear.',
'Wolf outdoor bicycle then red corridor under general cue132 and vendor-condition cue133. Original source FPS text is labelled vendor supplied, not our measurement.',
'Wolf moving red corridor then dark passage under cue133; captions readable and source conditions remain above. No logo/black ending in these samples.'
];
const records=x.boards.map((b,i)=>{if(sha(b.path)!==b.sha256)throw Error('Changed board');const images=b.imageIndices.map(n=>x.images[n-1]);for(const q of images)if(sha(q.path)!==q.sha256)throw Error('Changed image');return{boardIndex:i+1,path:b.path,sha256:b.sha256,directlyRead:true,imageIndices:b.imageIndices,images,observation:notes[i],unresolved:i===13?['cue130-interior-instead-of-branches']:[]};});
const dest=prod+'/native-repair-ab-direct-review-v18.json';if(fs.existsSync(dest))throw Error('Preserve review');
fs.writeFileSync(dest,JSON.stringify({recordedAt:new Date().toISOString(),execution:{path:p,sha256:sha(p)},boardsDirectlyRead:19,imagesDirectlyRead:112,allChangedSampleBoardsRead:true,sourceLabelCaptionClearanceApproved:true,semanticApproval:false,unresolved:[{input:'06-dlss-thin-lines-repair-02',cue:130,frames:[34100,34187,34275],issue:'Interior footage remains while the narration requests branches behind aim.',next:'Directly verify42.5–50.383333 source; produce only this473-frame replacement and review exact caption pixels.'}],records,unchangedPcm:true,unchangedBodyRatio:true,captionAssSha256:x.originalCaptionAssSha256,fullAnimatedPlaybackReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0},null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json',c=JSON.parse(fs.readFileSync(cp));c.episode03NativeAbDirectReview={path:dest,sha256:sha(dest),boards:19,images:112,unresolvedCount:1,allFinalPixelsReviewed:false};c.updatedAt=new Date().toISOString();fs.writeFileSync(cp,JSON.stringify(c,null,2)+'\n');console.log(JSON.stringify({boards:19,images:112,unresolved:1,finalApproval:false}));
