// Rebuild review artifacts from the canonical per-project narration and this batch's plan.
// Reads the engine repository. Writes only the three new lesson project directories and this batch.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const batch = 'production/batches/yamyam-dx12-three-lessons';
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8').replace(/^\uFEFF/, '');
const json = relative => JSON.parse(read(relative));
const write = (relative, value) => {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), {recursive: true});
  fs.writeFileSync(target, typeof value === 'string' ? value : JSON.stringify(value, null, 2) + '\n', 'utf8');
};
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const clock = seconds => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
const plan = json(`${batch}/plan.json`);
const template = read('templates/video-project/project.json');
const official = [
  ['CommandAllocator Reset', 'https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandallocator-reset'],
  ['Texture upload', 'https://learn.microsoft.com/en-us/windows/win32/direct3d12/upload-and-readback-of-texture-data'],
  ['Graphics PSO', 'https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12'],
  ['SRV component mapping', 'https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_shader_component_mapping'],
];
const summary = [];
for (const lesson of plan.videos) {
  const base = `projects/${lesson.slug}`;
  const script = json(`${base}/script/narration.ko.json`);
  if (script.scenes.length !== lesson.scenes.length) throw Error(`${lesson.slug}: scene count mismatch`);
  const text = script.scenes.flatMap(scene => scene.lines).join(' ');
  let start = 2; // planned reuse of the original 2s cat intro; not a measured narration timestamp
  const scenes = script.scenes.map((scene, i) => {
    if (scene.id !== lesson.scenes[i].id || !scene.lines.length) throw Error(`${lesson.slug}: scene id mismatch`);
    const seconds = Math.max(35, Math.ceil((scene.lines.join(' ').length / 8.5) / 5) * 5);
    const result = {...lesson.scenes[i], title: scene.title, plannedStartSeconds: start, plannedDurationSeconds: seconds};
    start += seconds;
    return result;
  });
  const bodySeconds = start - 2;
  const weighted = scenes.reduce((n, scene) => n + scene.plannedDurationSeconds * scene.developmentWeight, 0);
  let totalDevelopment = 0;
  for (const scene of scenes) {
    scene.plannedDevelopmentSeconds = Math.round(scene.plannedDurationSeconds * scene.developmentWeight * (bodySeconds * 0.6 / weighted));
    totalDevelopment += scene.plannedDevelopmentSeconds;
  }
  scenes.at(-1).plannedDevelopmentSeconds += Math.round(bodySeconds * 0.6) - totalDevelopment;
  for (const scene of scenes) {
    scene.plannedExplanationSeconds = scene.plannedDurationSeconds - scene.plannedDevelopmentSeconds;
    if (scene.plannedExplanationSeconds <= 0) throw Error('No explanation allocation');
  }
  const evidence = new Map();
  for (const scene of scenes) {
    scene.codeReferences = scene.refs.map(([relative, first, last]) => {
      const file = path.join(plan.sourceRepository, relative);
      const bytes = fs.readFileSync(file);
      const lines = bytes.toString('utf8').replace(/\r\n/g, '\n').split('\n');
      if (first < 1 || last < first || last > lines.length) throw Error(`${relative}: invalid range ${first}-${last}, length ${lines.length}`);
      const excerpt = lines.slice(first - 1, last).join('\n');
      const key = `${relative}:${first}-${last}`;
      if (!evidence.has(key)) evidence.set(key, {path: file.replaceAll('\\', '/'), firstLine: first, lastLine: last, fileSha256: sha(bytes), excerptSha256: sha(excerpt), excerpt});
      return {file: relative, firstLine: first, lastLine: last, snapshotKey: key};
    });
    delete scene.refs;
  }
  const storyboard = {
    schemaVersion: 1, slug: lesson.slug, status: 'proposed-not-rendered', timingIsMeasured: false,
    timingMethod: 'Planning only: characters including spaces / 8.5 per second, rounded up to 5 seconds. Replace from approved narration and actual footage; never pad, loop, or slow media to match these estimates.',
    intro: {kind: 'original-cat-branding', plannedSeconds: 2, source: 'shared/assets/branding/yamyamcoding-cats-original.png'},
    body: {plannedSeconds: bodySeconds, plannedDevelopmentSeconds: Math.round(bodySeconds * 0.6), plannedExplanationSeconds: bodySeconds - Math.round(bodySeconds * 0.6), targetShare: [0.6, 0.4], actualDevelopmentSeconds: null, actualExplanationSeconds: null},
    scenes,
    outro: {kind: 'membership-thanks', plannedSeconds: 10, title: '멤버쉽가입 감사드립니다.', narration: false, subtitles: false, preserveOriginalProfileNameBadge: true, sourceVerification: 'pending-before-render'},
  };
  write(`${base}/planning/storyboard.json`, storyboard);
  write(`${base}/sources/code-evidence.json`, {sourceHead: plan.sourceHead, reviewType: 'source-read-only-not-runtime-verification', excerpts: Object.fromEntries(evidence)});

  const manifest = JSON.parse(template.replaceAll('{{SLUG}}', lesson.slug).replaceAll('{{TITLE_KO}}', script.title).replaceAll('{{TITLE_EN}}', lesson.titleEn));
  manifest.status = 'script-review';
  manifest.publishReady = false;
  manifest.approvals = {script: 'pending', voice: 'pending-sample', music: 'pending', finalListening: 'pending'};
  manifest.production = {
    sourceRepository: plan.sourceRepository, sourceHead: plan.sourceHead, relatedCommits: lesson.relatedCommits,
    notionPage: `https://www.notion.so/${lesson.pageId.replaceAll('-', '')}`, sceneCount: scenes.length,
    targetBodySeconds: [600, 840], plannedBodySeconds: bodySeconds, timingIsMeasured: false,
    sourceReview: 'complete-for-visible-page-text-and-listed-code', runtimeVerification: 'not-executed-in-this-session',
    motionCanvasStatus: 'storyboard-only; one independent scene per narration scene after approval',
    manimStatus: lesson.order === 3 ? 'optional transparency depth illustration; not implemented' : 'not required for the planned diagrams',
    scope: 'script and storyboard only; no narration, rendering, or platform action',
  };
  delete manifest.editing.exampleSeconds;
  manifest.editing = {
    ...manifest.editing, targetGameplayShare: 0.6, targetExplanationShare: 0.4, gameplayShareRange: [0.6, 0.62],
    exampleSource: 'new own-engine recordings, actual source navigation and generated-color smoke scenes',
    timingStatus: 'proposed-not-measured', narrationPlacement: 'continuous-across-example-and-explanation',
    explanationPresentation: 'all explanation scenes white research style 2.5D with depth, motion and comparisons',
    sharedStyle: 'motion-canvas/src/styles/research-paper.ts',
    creditPlacement: 'internal-source-records; no public description credits under current user defaults',
    plannedDevelopmentSeconds: storyboard.body.plannedDevelopmentSeconds, plannedExplanationSeconds: storyboard.body.plannedExplanationSeconds,
    actualGameplaySeconds: null, actualExplanationSeconds: null, actualGameplayShare: null,
  };
  manifest.membershipOutro = {enabled: true, durationSeconds: 10, rosterPath: 'motion-canvas/src/shared/membership/members.json', scenePath: 'motion-canvas/src/shared/membership/membership-outro.tsx', appliedToFinal: false, originalImageVerification: 'pending'};
  manifest.paths = {...manifest.paths, reviewScript: `${base}/script/review.ko.md`, narrationOnlyReview: `${base}/script/narration.ko.md`, storyboard: `${base}/planning/storyboard.json`, codeEvidence: `${base}/sources/code-evidence.json`};
  write(`${base}/project.json`, manifest);
  const page = `https://www.notion.so/${lesson.pageId.replaceAll('-', '')}`;
  let review = `# ${script.title}\n\n전체 한국어 대본 초안입니다. 예상 10~14분이며 실제 음성 길이는 아직 측정하지 않았습니다. 이 문서는 대사를 전부 읽으면서 실제 화면과 흰색 2.5D 설명의 연결을 검토하는 용도입니다.\n\n이 편에서 기억할 내용은 다음과 같습니다. **${lesson.takeaway}** [해당 노션 강의](${page})와 현재 소스의 구현을 대조했습니다. 대본·목소리·음악 승인은 각각 대기 상태입니다.\n\n장면 시간과 실제 개발 화면 60%·설명 40%는 계획값입니다. 촬영과 승인 음성 이후 다시 맞추며, 시간에 맞추려고 반복·저속 재생·정지 화면을 늘리지 않습니다. 각 장면은 실제 예시 뒤 원리 설명으로 이어지는 독립 Motion Canvas 씬을 계획합니다.\n\n`;
  let narrationOnly = `# ${script.title}\n\n낭독용 전체 대본입니다. 아래 문단은 장면별 내레이션이며 화면 지시는 별도 검토본에 있습니다.\n\n`;
  for (let i = 0; i < scenes.length; i++) {
    const scene = scenes[i];
    review += `## 장면 ${scene.id} ${scene.title}\n\n계획 구간 ${clock(scene.plannedStartSeconds)}~${clock(scene.plannedStartSeconds + scene.plannedDurationSeconds)}. 실제 개발 자료 ${scene.plannedDevelopmentSeconds}초, 자체 설명 ${scene.plannedExplanationSeconds}초. 확정 타임코드가 아닙니다.\n\n### 전체 내레이션\n\n`;
    const paragraphs = script.scenes[i].lines.map(line => line.trim()).join('\n\n');
    review += paragraphs + '\n\n### 실제 예시와 촬영 지시\n\n' + scene.footage + '\n\n### 흰색 2.5D 설명 연출\n\n' + scene.explanation + '\n\n';
    review += `화면 핵심 문구는 **${scene.label}**입니다.\n\n` + scene.cues.map(cue => `- ${cue}`).join('\n') + '\n\n';
    review += '### 소스코드 확인 위치\n\n' + scene.codeReferences.map(ref => `- [${ref.file} ${ref.firstLine}행](${plan.sourceRepository}/${ref.file}:${ref.firstLine}) — 확인 범위 ${ref.firstLine}~${ref.lastLine}행`).join('\n') + '\n\n';
    narrationOnly += `## 장면 ${scene.id} ${scene.title}\n\n${paragraphs}\n\n`;
  }
  review += `## 채널 인트로와 회원 감사 엔딩\n\n처음에는 원본 고양이 로고의 기존 인트로를 사용합니다. 마지막에는 원본 회원 프로필·표시 이름·배지가 함께 보이는 10초 감사 씬을 한 번 추가하고 제목은 정확히 멤버쉽가입 감사드립니다.로 유지합니다. 이 장면은 별도 내레이션이나 자막이 없습니다. 원본 명단·이미지 확인 및 엔딩 적용은 렌더 단계에서 진행합니다.\n\n## 검토 상태와 근거\n\n[소스 검토 기록](../sources/SOURCES.md), [장면 계획](../planning/storyboard.json), [낭독용 대본](narration.ko.md)을 함께 보관합니다. 현재 엔진을 새로 빌드하거나 실행한 결과, 실제 녹화, 음성, PPT 파일, Motion Canvas 렌더는 포함되지 않았습니다. 자동 테스트의 범위는 코드로 확인했으며 당시 통과 기록과 이번 실행 결과를 구분합니다.\n`;
  write(`${base}/script/review.ko.md`, review);
  write(`${base}/script/narration.ko.md`, narrationOnly);
  const table = '| 장면 | 제목 | 계획 초 | 개발 자료 초 | 2.5D 초 |\n|---|---|---:|---:|---:|\n' + scenes.map(scene => `| ${scene.id} | ${scene.title} | ${scene.plannedDurationSeconds} | ${scene.plannedDevelopmentSeconds} | ${scene.plannedExplanationSeconds} |`).join('\n');
  write(`${base}/planning/outline.md`, `# ${script.title} 제작 기획\n\n${lesson.takeaway}\n\n예상 10~14분. DX12를 처음 구현하는 게임 개발자가 대상이며 용어를 실제 코드·동작과 함께 설명합니다. 이전 편을 보지 않아도 시작의 문제와 목적을 이해하도록 구성했습니다.\n\n${table}\n\n본편 계획 ${bodySeconds}초이며 실측 전 추정입니다. 실제 자료 ${storyboard.body.plannedDevelopmentSeconds}초, 2.5D ${storyboard.body.plannedExplanationSeconds}초. 실제 코드 탐색·디버거·자체 테스트 도형·새 엔진 조작을 우선합니다. 기존 캡처는 날짜가 있는 참고자료이며 영상 분량을 채우는 용도로 길게 정지하지 않습니다.\n\nMotion Canvas는 내레이션 씬 10개를 각각 독립 구현합니다. ${lesson.order === 3 ? '반투명 판의 깊이·카메라 이동만 Manim ThreeDScene을 선택적으로 사용하며, 흰 2.5D 합성 도식은 Motion Canvas로 제작합니다.' : '시간 축·서랍·텍스처 판은 Motion Canvas의 원근 투영, 면 두께, 겹침, 그림자와 단계별 강조로 표현합니다.'}\n\n첫 TTS 전 대본과 발음표를 확인하고 샘플 승인 후 KO/EN SRT·타이밍을 생성합니다. 실제 자막 cue로 변환할 때 최대 두 줄과 UI 가림을 확인합니다.\n`);
  const header = 'scene,title,planned_start_seconds,planned_duration_seconds,planned_development_seconds,planned_explanation_seconds,timing_status';
  write(`${base}/planning/edit-cues.csv`, header + '\n' + scenes.map(scene => [scene.id,scene.title,scene.plannedStartSeconds,scene.plannedDurationSeconds,scene.plannedDevelopmentSeconds,scene.plannedExplanationSeconds,'proposed-not-measured'].map(value => '"' + String(value).replaceAll('"', '""') + '"').join(',')).join('\n') + '\n');
  const candidates = [
    {name: `YamYam Engine lesson ${lesson.order}: newly recorded source navigation and procedural-color smoke scenes`,decision:'selected-for-planning',conceptFit:lesson.diagrams,priorUse:'existing yamyam-dx12-rendering is a planning draft; do not recycle its clips. Record new chapter-specific actions.',rights:'source repository belongs to the user; use newly made simple shapes/colors. Embedded third-party sprites require separate rights confirmation.',fileStatus:'not-captured'},
    {name:'Existing engine scene-game-views.png and scene-view.png',decision:'reference-only',conceptFit:'dated engine layout evidence; not frame-sync or alpha correctness proof',priorUse:'used in the 2026-09-15 wiki; viewed during this review',rights:'screenshot has existing sprite content; asset rights pending for video inclusion',fileStatus:'existing local reference; no new capture'},
    {name:'Godot editor reference',decision:'not-selected-for-main-footage',conceptFit:'useful UI role comparison but does not prove YamYam DX12 behavior',priorUse:'AI-era CS draft contains Godot footage; source wiki also uses a Godot reference',rights:'no external footage acquired; verify exact image/clip license if adopted',fileStatus:'not-acquired'},
    {name:'Kirby, Celeste, Super Meat Boy, Hollow Knight, Portal existing channel footage',decision:'rejected',conceptFit:'cannot demonstrate these engine-internal Fence/descriptor/PSO implementations',priorUse:'recent SOURCES.md and game-candidates.json history reviewed on 2026-10-01',rights:'previous clip permission does not select or clear new segments',fileStatus:'not-reused'},
  ];
  write(`${base}/sources/game-candidates.json`, {reviewedAt:'2026-10-01',scope:'developer lesson footage; own fresh source segments chosen after checking recent game/source history',historyReviewed:['projects/yamyam-dx12-rendering','projects/ai-era-cs-fundamentals/README.md','projects/one-button-game-design/sources/SOURCES.md','projects/deconstruct-analyze-rebuild/sources/SOURCES.md','projects/deconstruct-analyze-rebuild/sources/game-candidates.json','production/batches/sakurai-planning-game-design/README.md'],candidates});
  let sources = `# ${script.title} 출처와 구현 확인\n\n검토일 2026-10-01. 현재 엔진 HEAD는 ${plan.sourceHead}입니다. 소스코드와 노션에서 읽을 수 있는 본문을 검토했으며 이번 세션에서 엔진 빌드·테스트·실행은 하지 않았습니다.\n\n## 노션과 커밋 연결\n\n- [해당 강의](${page})\n- 최신 문서 커밋 [845442b](https://github.com/eazuooz/YamYam_Engine/commit/845442b7d756e7a991c09799ab58a775803a006a)는 문서 묶음이며 엔진 기능 한 개를 추가한 커밋이 아닙니다.\n- 구현은 주로 [49e04e5](https://github.com/eazuooz/YamYam_Engine/commit/49e04e5e875f04cfb792ea8a71e10667be78ad41)와 [ce56f16](https://github.com/eazuooz/YamYam_Engine/commit/ce56f16dd7a40fd2b4bf03c680790e5b637c7530)에 연결됩니다.\n- 역사적 동기화 사례 일부는 이전 7ac7ef2에도 연결됩니다. 과거의 Reset 뒤 Wait 오류를 49e04e5에서 처음 고쳤다고 대본에 단정하지 않았습니다.\n\n`;
  if (lesson.order === 1) sources += '첫 페이지 fetch는 truncated=true, unknown_block_count=1입니다. 맨 위 external_object_instance 임베드를 도구가 해석하지 못했습니다. 반환 본문의 마지막 연결까지 검토하고 local Docs/DX12_FrameLoop_And_Fence.md와 실제 소스도 대조했습니다. 기존 임베드 영상 전체를 시청했다고 주장하지 않습니다.\n\n';
  sources += `## 직접 확인한 코드\n\n범위별 발췌와 파일 SHA-256은 code-evidence.json에 보관합니다. 전체 코드 경로와 행 번호는 대본의 각 장면에 연결했습니다. 다음 사실은 현재 소스 범위로 확인했습니다.\n\n`;
  const facts = lesson.order === 1 ? [
    'WaitForNextFrameResources는 현재 mFrameIndex의 슬롯을 조회하며 증가시키지 않습니다. Editor main에서 Reset보다 먼저 호출합니다.',
    'SignalFrameCompletion은 실제 사용한 슬롯의 FenceValue를 저장한 뒤 SwapChain 인덱스를 조회합니다.',
    'Game-only의 MoveToNextFrame도 다음 슬롯의 이전 사용만 기다리므로 CPU/GPU 작업 겹침이 가능합니다.',
    'Editor 최종 Signal은 main list, 추가 OS 창, main Present 뒤에 놓입니다. 로컬 ImGui backend는 engine queue를 사용하며 추가 창의 allocator 등은 별도로 관리합니다.',
    'SignalFrameCompletion/WaitForNextFrameResources 등에 일부 HRESULT·Wait 반환값 검사가 빠져 있습니다. 실패 안전성까지 완성됐다고 말하지 않습니다.'
  ] : lesson.order === 2 ? [
    'Texture loader는 2D 단일 배열의 mip0 RGBA8을 사용하며 UploadTexture는 별도 allocator/list와 동기식 WaitForGpu를 사용합니다.',
    'RTV/SRV는 동일 resource를 쓰거나 읽는 view입니다. CPU/GPU handle은 같은 descriptor 슬롯에 대한 서로 다른 참조이며 이미지 복사본이 아닙니다.',
    'root parameter 0은 b0, root parameter 1은 t0 table입니다. 현재 Texture::Bind stage/slot 인자는 사용하지 않습니다.',
    'Transform은 3개 row_major 행렬 192바이트이며 stride 256, 64KiB page당 256 Draw입니다. per-frame·per-draw 주소를 나눕니다.',
    '현재 RT 분리는 Scene/Game 단위입니다. 모든 game camera에 전용 RT가 생성되지는 않습니다.',
    'Game의 resize는 UI에서 요청한 다음 Bind에 적용하고 Scene은 렌더 직전 Bind에 적용합니다. 렌더러는 현재 viewport 크기로 camera projection을 갱신합니다.',
    'ReadPixel은 0 반환 stub입니다. MSAA RT와 전체 mip/array/cubemap 스트리밍이 완성됐다고 말하지 않습니다.'
  ] : [
    'Material은 mode만 저장하고 Bind 때 Shader::Bind(mMode)로 전달합니다. Shader는 raster/blend/depth 조합 PSO를 캐시합니다.',
    'Opaque/CutOut은 LessEqual 및 depth write, Transparent는 Always 및 no-write입니다. Transparent는 기존 정책을 보존해 불투명 뒤에서도 합성될 수 있습니다.',
    'CutOut에만 YA_ALPHA_TEST PS blob을 사용하며 clip(color.a-0.01f)는 음수만 버립니다. alpha0.01은 통과합니다. 일반 custom shader에도 해당 분기가 필요합니다.',
    '정렬은 현재 전달된 scene 목록 안에서 object position 거리 기준입니다. 전체 scene들 간 전역 정렬이나 교차 삼각형 픽셀 정렬이 아닙니다.',
    'RGB는 SRC_ALPHA/INV_SRC_ALPHA, alpha는 ONE/ZERO입니다. 원본 RT alpha는 누적 coverage가 아닙니다.',
    'GetDisplaySRV는 첫 RGBA8 attachment의 같은 resource에 새 descriptor를 만들고 alpha를 1로 mapping합니다. 원본 픽셀 수정/전체 복사는 하지 않습니다.',
    'Retire는 resource와 descriptor를 UINT64_MAX 미확정 상태로 보관하고 최종 frame Signal에서 Seal한 뒤 completed value로 Collect합니다. 중간 Upload Wait는 미확정 retirement를 Seal하지 않습니다.',
    'Smoke test는 303 Draw, 두 카메라, 모드/깊이/정렬/공유 shader 변경/ImGui 합성을 검사하지만 해당 ImGui 구간은 ViewportsEnable를 끕니다. 별도 OS 창의 수동 조작 검증이 남습니다.'
  ];
  sources += facts.map(fact => `- ${fact}`).join('\n') + '\n\n## 공식 기술 교차 확인\n\n' + official.map(([label,url]) => `- [${label}](${url})`).join('\n');
  sources += '\n\n공식 문서는 API 조건 교차 확인에만 사용했습니다. YamYam 구현의 모든 정책이 일반적 정답이라는 근거로 쓰지 않습니다. 수치 예시는 측정 결과가 아닌 설명용 계산입니다.\n\n## 실제 테스트 기록과 이번 검토의 구분\n\n노션 후속 강의는 2026-09-14 Debug/Release x64 및 WARP·하드웨어 통과, 2026-09-15 실행 캡처와 하드웨어 재검사 이력을 기록합니다. 이는 페이지의 당시 기록입니다. 이번 세션은 테스트 소스를 읽었으며 현재 환경의 성공을 재확인한 것이 아닙니다. 통과 콘솔을 새로 만들어 붙이지 않습니다.\n\n## 새 자료 후보와 권리\n\n매 편 신규 후보 검토 결과는 game-candidates.json에 있습니다. 최근 커비·Celeste·Super Meat Boy·Hollow Knight·Portal 자료를 관성적으로 재사용하지 않고, 직접 만든 색 도형과 새 엔진/코드 조작 구간을 선택했습니다. 외부 그림·영상은 아직 확보하거나 최종본에 넣지 않았습니다. 원본 screenshot의 스프라이트 권리는 별도 확인 전 게시 미승인입니다.\n\n기존 로컬 이미지 Docs/Wiki/DX12_Rendering_Continuation/images/scene-game-views.png와 scene-view.png는 날짜가 있는 실제 실행 참고자료입니다. lesson-texture-path.png는 자체 개념도이며 실제 UI가 아닙니다. 이번에는 이미지를 새로 캡처하거나 영상 파일을 생성하지 않았습니다.\n';
  write(`${base}/sources/SOURCES.md`, sources);
  write(`${base}/README.md`, `# ${script.title}\n\n[전체 내레이션과 2.5D 화면 연출](script/review.ko.md), [낭독용 전체 대본](script/narration.ko.md), [원본 대본 JSON](script/narration.ko.json)을 제공합니다.\n\n${lesson.takeaway}\n\n10개 독립 장면, 예상 10~14분. 실제 개발 화면 60%와 흰색 2.5D 설명 40%를 본편 전체에 계획했으며 실측은 대기입니다. 현재 결과는 대본과 스토리보드입니다.\n\n[노션 강의](${page}) · [코드 검토/출처](sources/SOURCES.md) · [장면 계획](planning/storyboard.json) · [세 편 안내](../../${batch}/README.md)\n`);
  summary.push({order:lesson.order,slug:lesson.slug,title:script.title,sceneCount:scenes.length,lineCount:script.scenes.reduce((n,s)=>n+s.lines.length,0),characters:text.length,plannedBodySeconds:bodySeconds,plannedDevelopmentSeconds:storyboard.body.plannedDevelopmentSeconds,plannedExplanationSeconds:storyboard.body.plannedExplanationSeconds,narrationSha256:sha(read(`${base}/script/narration.ko.json`)),scriptApproval:'pending',runtimeVerification:'not-executed-in-this-session',renderStatus:'not-started',publishReady:false});
}
write(`${batch}/review-summary.json`, {createdAt:'2026-10-01',sourceHead:plan.sourceHead,timingIsMeasured:false,videos:summary});
console.log(JSON.stringify(summary.map(({slug,sceneCount,lineCount,characters,plannedBodySeconds,plannedDevelopmentSeconds,plannedExplanationSeconds})=>({slug,sceneCount,lineCount,characters,plannedBodySeconds,plannedDevelopmentSeconds,plannedExplanationSeconds})),null,2));
