// Configure this user-requested lecture sample; never change other projects.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/game-math-polar-sample/';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(root,f),JSON.stringify(v,null,2)+'\n');
const m=read(base+'project.json');
m.status='sample-production';m.publishReady=false;
m.editing.exampleSeconds=0;
Object.assign(m.editing,{targetGameplayShare:.4,targetExplanationShare:.6,gameplayShareRange:[.4,.4],ratioPolicy:'User-requested lecture sample: actual existing-game footage 40% / original explanation 60%; excludes 2-second intro and 10-second outro; at most one frame of rounding.',ratioPolicyVersion:'lecture-sample-40-60-20261004',ratioApprovedAt:'2026-10-04',ratioApprovalEvidence:'이번에는 강의영상이어서 실제사례 40, 설명 60으로 바꿔서 진행해줘',timingStatus:'target-only-awaiting-measured-speech',explanationStyle:'Manim Community white mathematical animation, including a genuine 3D cylindrical-coordinate scene'});
m.editing.exampleExpansion.planningFormula='additionalActualSeconds = max(0, (2/3) * retainedExplanationSeconds - retainedActualSeconds)';
m.editing.ratioException={scope:'this lecture sample and requested continuation of this lecture; not a change to completed videos or ordinary channel videos',userRequested:true};
m.editing.openingOverview={required:true,scene:'01',reviewedBeforeTts:true,question:'Why describe position using distance and angle?',outcome:'Locate a point and convert polar to Cartesian coordinates',orderedSteps:['observe gameplay','locate a point using r and theta','convert to x and y'],classification:'explanation',languages:['ko','en']};
m.video.durationSeconds=180;
m.tts.sceneGapSeconds=.45;
m.audio.backgroundMusic=read('projects/hierarchical-game-outlines/project.json').audio.backgroundMusic;
m.audio.mixStatus='approved-existing-voice-and-Nimbus-awaiting-render';
m.audio.sourceAudioPolicy='Retain original recordings locally. Source music and any third-party speech are excluded from the lecture mix because they are not independently cleared; approved Nimbus continues underneath narration.';
m.membershipOutro={...m.membershipOutro,kind:'original-screenshot',screenshot:'shared/assets/membership/member-list-20260929.png',cornerLogo:'shared/assets/branding/yamyamcoding-cats-original.png',title:'멤버쉽가입 감사드립니다.',truncatedHandlesReview:'pending',appliedToFinal:false};
m.approvals={production:'User explicitly requested one approximately three-minute polar-coordinate sample. Reuse approved voice and Nimbus; no new voice/music selection.',humanListening:'pending',publicUpload:'not requested for this sample'};
m.engines=['manim-community','motion-canvas-scene-wrappers','ffmpeg-final-composition'];
m.rendererDecision={selected:'Manim Community',version:'0.20.1',renderer:'Cairo',comparison:'planning/manim-comparison.md',reason:'Documented 2D/3D API and reproducible offline rendering; fits current repository. GL remains a useful option for interactive teaching and authoring.'};
m.paths.narration='shared/output/game-math-polar-sample/narration-final.wav';
m.paths.captionsKo=base+'script/final.ko.srt';m.paths.captionsEn=base+'script/final.en.srt';
m.paths.renderReport=base+'production/qa.json';m.paths.footageCuts=base+'sources/gameplay-cuts.json';
m.paths.editorAudioMix='motion-canvas/src/projects/game-math-polar-sample/assets/final-mix.wav';
write(base+'project.json',m);
const cuts={reviewedAt:new Date().toISOString(),reviewedBeforeNarration:true,source:{id:'SlqDHvpYgZo',game:'Enter the Gungeon',channel:'Rybolt',url:'https://www.youtube.com/watch?v=SlqDHvpYgZo',file:'shared/output/game-math-polar-sample/sources/SlqDHvpYgZo.mp4',permission:'Uploader description explicitly allows use in commentaries or other videos. This is uploader permission, not a universal fair-use ruling.',gameIpPolicyReview:'pending-final-publication-review',priorUse:'No matching ID/title in current project source history',sourceAudioUsed:false},cuts:[
 {scene:'02',in:205,duration:22,action:'Player turns and fires while fighting room enemies',focus:'Direction of outgoing bullets relative to the firing position',claim:'Direction plus displacement distance can describe a bullet position',connection:'Same relative position later represented by r and theta',inspection:'Full source contact sheet every 20s; selected interval review every 2s; initial loading at192–203s excluded'},
 {scene:'04',in:570,duration:23.2,viewport:[1600,900,0,40],viewportReason:'Full-screen aspect-preserving combat crop, keeping the projectile spread visible above fixed bottom-center captions; bottom boss-health HUD outside the crop.',action:'Gatling Gull boss fires red projectiles spreading away from the weapon; player dodges',focus:'Several directions and increasing distance from the firing position',claim:'Different angles form a spread; increasing radial distance forms outward movement',connection:'Angle and distance are controlled separately in the diagram; no claim about proprietary implementation',inspection:'550–598s review every 2s; opening boss title excluded'},
 {scene:'06',in:512,duration:22,action:'Player moves and shoots during an active room encounter',focus:'Moving firing position and relative projectile offsets',claim:'World position equals center plus relative Cartesian offset',connection:'Add center coordinates to r cos(theta), r sin(theta)',inspection:'Selected interval review every 2s'}
]};write(base+'sources/gameplay-cuts.json',cuts);
write(base+'sources/game-candidates.json',{reviewedAt:new Date().toISOString(),candidates:[{game:'Enter the Gungeon',selected:true,source:'SlqDHvpYgZo',reason:'Fresh title and recording; direction, spreading shots and moving firing point directly illustrate the chapter.',rights:'Uploader explicit reuse permission; game IP review pending'},{game:'Brotato',selected:false,source:'eDL84EC5mkQ',rights:'YouTube CC Attribution metadata and free-to-use description verified',reason:'Candidate reviewed for relative weapon direction; Gungeon provides a clearer single example chain in a three-minute sample. No footage from this source is counted.'},{game:'Vampire Survivors',selected:false,reason:'Already used in visible-rewards. Prefer the fresh Gungeon source; no automatic reuse.'},{game:'Nova Drift',selected:false,reason:'Considered for radial patterns but a directly relevant reusable source was not established for this sample.'}]});
console.log('Lecture-only 40:60 exception and reviewed footage plan recorded.');
