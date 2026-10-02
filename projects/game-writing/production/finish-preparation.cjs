// Record only directly reviewed preparation. Never approves narration/final video/upload.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-writing';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),samples=read(base+'/production/lookdev-proof/samples.json');
if(samples.source!=='shared/output/motion-canvas/game-writing-explanation-lookdev-v3.mp4')throw Error('Expected directly viewed v3 samples.');
if(!read(base+'/production/lookdev-render-result-v3.json').done)throw Error('Visual draft has not finished.');
write(base+'/production/lookdev-visual-review.json',{
 reviewedAt:now,kind:'Direct native visual preparation review, not final narrated/caption QA',
 source:samples.source,sourceSha256:sha(samples.source),width:1920,height:1080,seconds:48,
 code:[base+'/playtest/index.html','motion-canvas/src/projects/game-writing/scenes/narrative-concept.tsx'].map(p=>({path:p,sha256:sha(p)})),
 reviewedSamples:samples.samples.map(s=>({...s,sha256:sha(s.path),directlyViewed:true})),
 draftReviewPassed:true,
 corrections:['Use separate arrows joining all three choice branches, retain resource/history tokens after joining.','Place essential-information return path separately from the optional-background card.','Raise footer panels to reserve the default two-line caption box at bottom.'],
 findings:['All six early and six result frames are legible at native resolution without clipped titles, cards or footer labels.','The three choice paths converge concurrently; the results remain distinct.','Footer and shadow stay above the default caption reserve; actual caption text is not present in this draft.'],
 pending:['Measured narration and meaningful real-action cuts','Direct review of every final cue/cut and gameplay/UI overlap','Full final render decode, audio and current-hash ASR','Human comprehension/enjoyment review'],
 finalVideo:false,finalCaptionQaPassed:false
});
const thumb=read(base+'/publishing/thumbnail-recipe.json');
if(thumb.sha256!==sha(thumb.path))throw Error('Thumbnail changed since direct review.');
Object.assign(thumb,{visualReview:'passed-native-local-draft',reviewedAt:now,findings:['Yellow strip and white background match channel concept.','Three large headline lines, original cats, fact bubbles and observed game image are readable and do not overlap.'],uploaded:false});
write(base+'/publishing/thumbnail-recipe.json',thumb);
const source=read(base+'/sources/native-review.json');
source.preparationRecheck={reviewedAt:now,reviewedSheets:['detail-dialogue-1.jpg','detail-dialogue-2.jpg'],correction:'Caryl names Ifan at 47.8–50.5 seconds, not at 121–134. The latter interval is excluded from that claim.',scene01Candidate:{sourceVideoId:'YEgrKLregCw',in:46,out:47.8,visibleAction:'Multiple dialogue replies; short observation, then own fresh input.'},scene03Candidate:{sourceVideoId:'YEgrKLregCw',in:47.8,out:50.5,visibleAction:'Caryl addresses Ifan by name; no inference about hidden implementation.'},finalCutApproval:false};
write(base+'/sources/native-review.json',source);
const qPath='production/batches/sakurai-planning-game-design/queue.json',q=read(qPath),i=q.items.find(x=>x.slug==='game-writing');
i.preparation.visualDraft={sessionId:80711,state:'finished',exitCode:0,report:base+'/production/lookdev-render-result-v3.json',nativeVisualReview:base+'/production/lookdev-visual-review.json',nativeSamples:12,draftReviewPassed:true,finalVideo:false,finalCaptionQaPassed:false};
for(const s of [{sessionId:48831,kind:'second explanation visual draft'},{sessionId:80711,kind:'third corrected explanation visual draft'}])if(!i.preparation.finishedCpuSessions.some(x=>x.sessionId===s.sessionId))i.preparation.finishedCpuSessions.push({...s,exitCode:0,restart:false});
i.preparation.thumbnail={recipe:base+'/publishing/thumbnail-recipe.json',localNativeReviewPassed:true,uploaded:false};
i.preparation.nextVisualAction='After current-hash narration review, capture new actual UI paths, choose non-overlapping source action cuts and measure body 60:40. Final all-cue/cut native QA remains pending.';
i.updatedAt=now;q.updatedAt=now;
q.authorization.runtimeExpansion={userEvidence:'그럼 재생목록 내용보다 영상이 길어지는게 당연해',referenceRuntimeIsCeiling:false,guide:'docs/VIDEO_ADDITIVE_REVISION.md'};
write(qPath,q);
const lines=[
 '# 게임 시나리오 쓰는 법: 선택과 순서가 바뀌어도 말이 되게','',
 '2026-10-02 체크포인트: 독립 한영 12장/72대사, 새 DOS2 공식 자료 검토, 자체 이야기 게임 `항구의 봉인`, 6개 흰 2.5D 설명과 썸네일을 준비했다. **최종 내레이션·렌더·4파일 수집·YouTube 비공개 업로드는 아직 완료하지 않았다.** 0.1초 템플릿 WAV와 48초 설명 전용 lookdev는 완성 영상이 아니다.','',
 '제작 전 기존 활성 보강 대본까지 포함한 21개 프로젝트와 실제 Studio 검색/영상 ID를 직접 비교했다. [사전 중복 검토](../../production/batches/sakurai-planning-game-design/preflight/game-writing.json)는 distinct다. [장별 계획](planning/outline.md)에 주장·실제 동작·관찰 지점·설명 연결·출처 인아웃을 기록했다. 참고 대본의 복사/번역이나 원본 영상·음성 재사용은 하지 않았다.','',
 '## 현재 실행과 재개','',
 '- 단일 [resource-runner](production/resource-runner.cjs), 세션 `67834` / PID `46172`의 실제 현재 상태는 [resource-runner.json](production/resource-runner.json)과 [배치 대기열](../../production/batches/sakurai-planning-game-design/queue.json)을 읽는다. PID는 종료 후 재사용될 수 있으므로 실제 프로세스 명령까지 확인한다.',
 '- 다른 사용자 학습의 GPU 사용 중에는 기다린다. 해당 작업을 중단하지 않는다. 안정적으로 여유가 생기면 이 runner가 승인 Qwen3-TTS 1.7B로 한 번 합성하고 CPU ASR을 이어 실행한다. 살아 있는 runner/TTS와 중복 실행하지 않는다.',
 '- 기다리는 동안 `project.json`과 양언어 대본을 수정하면 입력 해시가 바뀌어 runner가 안전하게 실패한다. 수정이 필요하면 실제 종료 상태를 확인하고 명시적으로 새 실행을 시작한다.',
 '- 합성/ASR 종료는 음성 승인이나 영상 완료가 아니다. 현재 WAV 해시의 72대사를 모두 받아쓰기와 직접 대조하고 반복·누락·발음·임의 인사·끝소리를 검수한다. 실제 거부된 장면만 같은 승인 목소리로 복구한다.',
 '- Vite 세션 `26486` / PID `54652` / 포트 `9210`은 살아 있으면 재사용한다. 종료된 소스 샘플링·디코딩·UI 검증·lookdev 세션은 다시 기다리지 않는다.','',
 '## 준비된 증거와 남은 제작','',
 '[source-decode.json](production/source-decode.json)은 두 공식 자료 전체 디코딩의 실제 결과다. [출처 기록](sources/SOURCES.md), [새 게임 후보](sources/game-candidates.json), [native 검토](sources/native-review.json)는 화면에서 보이는 사실과 사용 조건/미완료 공개 권리 판단을 구분한다. 최종 선택 컷의 첫·중간·끝과 전환은 음성 실측 뒤 다시 검수한다.','',
 '[자체 상태 검증](production/playtest-state-proof.json)은 11개 시나리오, 도달 가능한 2,209개 사실/대화 상태와 표시 선택 1,424개의 유효성을 실행했다. [실제 UI 입력](production/playtest-ui-proof.json)은 새 게임의 다섯 경로/52개 입력과 화면 결과를 확인했다. 이는 사람의 재미·감정·이해 검토를 대신하지 않는다. 실제 녹화는 최종 타이밍을 정한 뒤 새 입력으로 촬영한다.','',
 '[lookdev v3 결과](production/lookdev-render-result-v3.json)와 [시각 검토](production/lookdev-visual-review.json)는 설명 6개/12개 1080p 샘플의 준비 검수다. 분기 합류와 결과 보존, 정보 전달, 물건 소유 토큰, 필수 사실 재확인을 표시한다. 최종 영상 자막 검수는 아직 남아 있다. `timing.ts`의 `ACTUAL_MEDIA_READY=false`와 계획 시간은 실제 음성·미디어가 검증되기 전 유지한다.','',
 '본편은 실제 동작 60% / 설명 40%로 실측한다. 인트로 2초와 원본 회원 엔딩 10초를 제외하고 최대 1프레임 반올림만 허용한다. 도식/숫자 테스트는 설명이며, 실제 게임도 무관한 대기·루프·저속으로 비중을 채우지 않는다. 각 설명 사이의 행동/새 해설을 충분히 담아 참고 영상보다 길어질 수 있다. 같은 승인 목소리와 연속 Nimbus를 유지한다.','',
 '음성 검수 뒤 컷별 실제 게임 녹화/공식 자료 → 실측 60:40 타이밍·믹스·KO/EN SRT·챕터·엔딩 동시 확정 → 최종 렌더 → 모든 큐/컷 시각 검수·전체 ASR·디코딩·음량/true peak·두 MP4 동일 오디오 → `node scripts/collect-video-output.cjs game-writing` → 모든 저장 규칙으로 새 비공개 업로드 → rebuild/media 검사·선택 커밋·일반 푸시를 진행한다. 공개와 예약은 사용자가 직접 한다.','',
 '`setup-editorial.cjs`, `setup-scenes.cjs`, `record-preparation.cjs`는 초기 생성용이다. 현재 준비물이나 향후 실측 타이밍을 덮어쓰므로 재개할 때 자동 재실행하지 않는다. `finish-preparation.cjs`도 준비 검수 증거용이므로 최종 제작 단계에서는 재실행하지 않는다. 관련 규칙은 [VIDEO_ADDITIVE_REVISION](../../docs/VIDEO_ADDITIVE_REVISION.md), [VIDEO_WORKFLOW](../../docs/VIDEO_WORKFLOW.md), [NARRATION_AUDIO_STANDARD](../../docs/NARRATION_AUDIO_STANDARD.md), [YOUTUBE_PUBLISHING](../../docs/YOUTUBE_PUBLISHING.md)를 따른다. 사람 청취·공개 권리·원래 Nimbus 파일·잘린 회원 핸들·외부 백업은 증거가 없으면 pending을 유지한다.',''
];
fs.writeFileSync(path.join(root,base+'/README.md'),lines.join('\n'));
const batchReadme=path.join(root,'production/batches/sakurai-planning-game-design/README.md'),marker='## 다음 신규 제작 game-writing 체크포인트';
if(!fs.readFileSync(batchReadme,'utf8').includes(marker))fs.appendFileSync(batchReadme,'\n'+marker+'\n\n2026-10-02: 보강 5편은 완료 증거대로 보존한다. game-writing은 활성 보강 대본을 포함한 21개 기존 프로젝트와 현재 Studio 검색을 다시 대조해 distinct를 통과한 뒤 신규 제작을 준비했다. 독립 한영 12장/72대사, 새 DOS2 공식 자료의 전체 디코딩과 native 화면 검토, 자체 항구 이야기 게임의 11개 상태 사례·2,209개 도달 상태·1,424개 선택·다섯 실제 UI 경로/52입력, 6개 흰 2.5D 설명의 12개 native 샘플과 새 썸네일 준비 검수를 마쳤다. 이는 최종 영상 완료가 아니다.\n\n단일 resource-runner 세션67834/PID46172가 다른 사용자 GPU 학습을 중단하지 않고 여유를 기다린다. 실제 현재 상태와 로그는 queue와 projects/game-writing/production/resource-runner.json을 우선한다. 안정적 여유가 생기면 승인 목소리 한 번 합성→CPU ASR까지 이어가며, 종료 후 전체72대사 직접 검수와 실측 촬영/60:40/최종 렌더·QA·수집·비공개 저장·Git 전달은 별도 증거로 완료해야 한다. 현재 manifest와 대본을 덮어쓰거나 살아 있는 작업을 중복 실행하지 않는다. 설명 사이에 새 실제 동작과 해설을 충분히 담아 참고 재생목록보다 길어지는 제작 방식은 docs/VIDEO_ADDITIVE_REVISION.md에 기록했다.\n');
console.log('Preparation evidence updated. Narration/final render/collection/private upload/Git delivery remain incomplete.');
