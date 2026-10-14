const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const b='production/research/game-lighting-history/local/episode04-native-v9';
const acquisition=b+'/nanite-foliage-stockholm-2025.acquisition.json';
const a=read(acquisition),out='projects/game-lighting-history-04/production/native-source-observation-v9.json';
if(fs.existsSync(out))throw Error('Preserve completed review');
if(sha(a.media)!==a.sha256||a.boards.length!==10||a.wholeDownloadedWindowDecodeExit!==0)throw Error('Source mismatch');
const notes=[
 '0–150: presenters, agenda and static foliage/asset slides; excluded as actual action.',
 '180–330: constraints, asset thumbnails and instanced-branch slides; excluded as actual action.',
 '360–510: geometry atlas, stage and asset-size example slides; do not infer universal memory or speed improvement.',
 '540–690: wind/skinning explanation, stage and a forest wind demonstration at630; static voxel setting slide at690 is not an observed setting operation.',
 '720–870: static simplification examples, an exaggerated geometry-distance demonstration at780, stage, then forest at840/870. Preserve the exaggerated-visual-effect qualification.',
 '900–1050: normal forest at900, red/green geometry/debug views at930/960, then Houdini pipeline explanation and presenters. Geometry/debug colours do not prove GI or performance.',
 '1080–1230: procedural editor/node graph and asset presets. Editor action may be selected separately; static assembly and wind-authoring slides do not constitute gameplay.',
 '1260–1410: PCG/decay/gravity slides and stage; procedural pruning editor demonstration at1410.',
 '1440–1590: procedural tree/node/mesh/skinning editor views. Their scope is tree authoring, not a measured lighting benchmark.',
 '1620–1710: Unreal Editor selected tree followed by stage, future roadmap and closing text; roadmap/presenters excluded.'
];
const record={reviewedAt:new Date().toISOString(),priorObservation:'projects/game-lighting-history-04/production/native-source-observation-v8.json',source:{path:a.media,sha256:a.sha256,acquisition:{path:acquisition,sha256:sha(acquisition)},nativeFps:'50/1',nativeTimeBase:'1/12800',durationSeconds:1747.42,wholeDecodeExit:0},dates:{announcement:'2025-11-12',metadataUploadDateUtc:'2025-12-06',actualYouTubeDisplayKst:'2025-12-07',scope:'UE5.7 Experimental Nanite Foliage; official engine demonstration, not commercial-game adoption proof'},boards:a.boards.map((x,i)=>{if(sha(x.path)!==x.sha256)throw Error('Board changed');return{...x,directlyViewed:true,findings:notes[i]};}),allTenBoardsDirectlyRead:true,normalRateOfficialWebReview:{url:a.url,tab:36,browser:4,playbackRate:1,observedPoints:[{time:875,image:'presenter/stage; reject'},{time:901.383761,image:'normal forest camera view within conference inset'},{time:940.354066,image:'coloured triangle geometry debug, within inset'},{time:962,image:'red/green geometry representation debug, within inset'},{time:987.481769,image:'static Houdini pipeline slide; reject'}],requestedPlayRanges:[[900,940.354066],[940.354066,987.481769]],scope:'Normal-rate playback requested; screenshots directly inspected at recorded points. This is not uninterrupted full viewing or a frame-exact alignment of the browser stream with the local source.'},localPlayback:{approved:false,reason:'Browser rejected file navigation; no alternative hosting, browser-surface or indirect workaround attempted.'},candidateNativeIntervals:[[897,914],[946,966],[776,794]],exactNativeCropAndMovingReviewApproved:false,fullMotionReviewed:false,finalUseApproved:false,rightsApproved:false,recentUseCheckPassed:false,allFinalPixelsReviewed:false,actualRatioApproved:false,newGitImages:0};
fs.writeFileSync(out,JSON.stringify(record,null,2)+'\n');
const p='projects/game-lighting-history-04/sources/game-candidates.json',j=read(p),c=j.candidates.find(c=>c.id===a.id);
c.nativeAcquired=true;c.nativeEvidence={path:acquisition,sha256:sha(acquisition)};c.directObservation={path:out,sha256:sha(out)};c.nativeFps='50/1';c.metadataUploadDateUtc='2025-12-06';c.fullMotionReviewed=false;c.finalUseApproved=false;
fs.writeFileSync(p,JSON.stringify(j,null,2)+'\n');
console.log(JSON.stringify({record:out,boards:10,nativeFps:'50/1',final:false,newGitImages:0}));
