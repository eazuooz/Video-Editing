// Candidate narration for directly inspected official footage; no TTS launch.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const source='production/research/game-lighting-history/local/hogwarts-official-site-v79/hogwarts-official-site-castle2022.mp4';
const review='projects/game-lighting-history-04/production/hogwarts-official-source-direct-review-v80.json';
if(sha(source)!=='f7129a728b7833ca6205d63550f77c5cc6975bd0e77b93426103565c52563aed'||!read(review).allEightBoardsDirectlyRead)throw Error('Review changed source before drafting');
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],{stdio:'inherit'});
const rows=[
 ['hogwarts-stair-reference',[0,18],
  '네 게임의 표면을 비교했으니, 이번에는 관찰할 기준을 잡아 보죠. 이천이십이년 호그와트 시연입니다. 노란 옷의 인물이 밝은 창 아래 계단을 올라갑니다. 먼저 옷과 창, 그늘진 벽을 구별하세요.',
  'After comparing surfaces in four games, establish an observation reference in this2022 Hogwarts showcase. The character in yellow climbs stairs below bright windows. Identify the clothing, windows and shaded wall.',
  'Track robe and window as separate observed regions. Keep minimap/spells/health and source Work in Progress label clear; year label at top.'],
 ['hogwarts-arch-camera',[18,43],
  '문밖으로 나오면 같은 옷이 하늘과 돌기둥 사이에 놓입니다. 카메라는 탑을 올려다본 뒤 계단을 따라 움직이죠. 비교 대상은 같은 인물의 옷이지만 배경과 보는 방향이 함께 달라졌습니다. 다른 화면을 비교할 때 이런 조건도 같이 적어야 합니다.',
  'Outside, the same clothing is framed by sky and stone pillars. The camera looks up at the towers, then follows the stairs. The character remains the reference, while background and viewing direction change. Record those conditions when comparing images.',
  'Reacquire robe after arch occlusion and camera tilt; name changed viewpoint with a teal label, without invented physical units.'],
 ['hogwarts-terrace-reference',[43,65],
  '난간에 다가가니 가까운 돌과 멀리 있는 풍경이 한 화면에 들어옵니다. 먼저 가까운 난간을 빨간 표시로 잡고, 먼 풍경은 다른 색으로 구분하죠. 카메라가 아래를 볼 때 가려지는 영역도 달라집니다. 화면의 밝기 차이와 관찰 위치의 변화를 함께 봐야 하는 이유입니다.',
  'At the balustrade, nearby stone and distant landscape share one image. Red identifies the nearby rail; another color identifies the distant view. Looking down changes occlusion too. This is why brightness comparisons need the observation position as well.',
  'Red follows balustrade top; teal distant view region. Annotation is screen observation, not measured depth or the game\'s volume/GI implementation.'],
 ['hogwarts-brazier-view',[65,84],
  '불이 담긴 화로 옆에서 카메라가 인물 주위를 돌아갑니다. 불꽃, 옷, 돌바닥을 따로 따라가 보세요. 밝게 보이는 불꽃과 빛을 받는 표면은 서로 다른 관찰 대상입니다. 한쪽만 보고 화면 전체가 어떻게 만들어졌는지 판단하지 않습니다.',
  'The camera turns around the character near a burning brazier. Follow the flame, clothing and stone floor separately. A bright flame and a lit surface are different observation targets; one region alone does not describe the entire image.',
  'Track flame and robe separately; keep their silhouettes visible. No ray drawn as a captured light path.'],
 ['hogwarts-hall-camera',[120,146],
  '다시 홀 안입니다. 밝은 창을 등질 때 인물의 모습이 어둡게 보이고, 카메라를 돌리면 창과 조각 장식이 다른 위치에 놓입니다. 밝은 창, 인물의 옷, 계단을 같은 순서로 짚겠습니다. 무엇을 기준으로 비교하는지 정해야 색과 노출의 변화도 읽을 수 있습니다.',
  'Back in the hall, the character appears dark against a bright window. Turning the camera moves the window and carved decorations within the image. Identify the window, clothing and stairs in that order. A consistent reference makes color and exposure changes easier to read.',
  'Reset at the full-screen hall cut. Track the actual window and robe through camera pan; retain original game colors.'],
 ['hogwarts-courtyard-ui',[160,177],
  '마지막은 나무 아래 인물에게 다가가는 장면입니다. 대화 표시는 상호작용 대상이고, 빨간 표시는 우리가 관찰하는 옷입니다. 게임의 안내와 화면 비교용 표시를 구별하며 따라가세요.',
  'Finally, approach a character beneath the tree. The Talk prompt identifies an interaction target; our red mark identifies the clothing under observation. Keep the game\'s instructions distinct from our comparison marks.',
  'Track robe; avoid Nellie Oggspire/Talk prompt and spell/minimap UI. No inferred quest success.']
];
const scenes=rows.map((r,i)=>({id:r[0],role:'actual',source:'hogwarts-official-site-2022',sourcePath:source,sourceSha256:sha(source),sourceReview:review,ranges:[r[1]],sourceTimeIsNativeFileSeconds:true,insertAfter:i?rows[i-1][0]:'appearance-nba',ko:r[2],en:r[3],focus:r[4],normalSpeed:true,loop:false,slowdown:false,sourceAudio:false,exactCutAndMovingPixelsApproved:false}));
const out='projects/game-lighting-history-04/script/physical-part3-hogwarts-observation.koen.v81.json';
if(fs.existsSync(out))throw Error('Preserve existing preparation');
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-04',status:'draft-awaiting-bounded-normal-playback-and-measured-narration',sourceKind:'Official2022 game showcase; separate from2026 DLSS5 previews',purpose:'Insert surface/camera/UI prerequisites after four-game appearance comparison and before appearance-to-controls. Keep original111 and current37/five framing PCM and scripts unchanged.',scenes,candidateSeconds:127,ttsStarted:false,normalSpeedPlaybackReviewed:false,bodyRatioApproved:false,allFinalPixelsReviewed:false,rightsApprovedForPublicUse:false},null,2)+'\n');
console.log(JSON.stringify({prepared:out,scenes:scenes.length,sha256:sha(out),ttsStarted:false}));
