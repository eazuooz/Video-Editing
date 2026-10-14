> **현재 제작 인수인계:** [초심자 보강본 이어가기](production/beginner-revision-v1/HANDOFF.md). 재부팅으로 최종 믹스 ASR 3/13장에서 중단. 원본 업로드는 보존했고 수정본은 미업로드입니다. Git 외 미디어 전송이 별도로 필요합니다.

# 게임 렌더링 역사 · 1편

사용자가 선택한 첫 편의 Three.js 수정본을 [비공개 업로드](https://youtu.be/uT5FTLJx5_c)했다. 1080p60 실제 재생과 저장 설정을 확인했고, 광고 적합성 검사는 아직 진행 중이다. 현재 상태·실제 작업은 [체크포인트](production/checkpoint.json), 검사 근거는 [리뷰 원장](production/review-ledger.json)에서 관리한다. 자동 채팅·다음 편 자동 착수는 꺼져 있다.

둠의 구역 밝기 → 퀘이크 라이트맵 → 텍스처 필터링·밉맵 → 타일 기반 GPU → 둠3의 법선·섀도 볼륨 → 하프라이프2의 방향별 라이트맵·공간 표본 → 섀도 맵·CSM → 포워드·디퍼드 → SSAO 순서를 보존한다. 사용자 제공 설명에 전제·작은 계산·독립 게임/엔진 시연을 해당 설명 옆에 보강했다.

수정 설계는 [씬별 렌더러 선택](production/threejs-revision-v1/scene-plan.json)이다. 공간·광원·가림은 Three.js, 계산 전개는 Manim, 유지할 2D 도식은 기존 Motion Canvas를 사용한다. 실제 깊이·기하 법선·색 패스와 SSAO 구현을 설명용 화살표·CSM 배정·연산 순서 도식과 구별한다. 게임의 내부 버퍼나 성능 측정으로 표현하지 않는다. 7개 혼합 씬의 표식 구현은 Canvas2D이며 Motion Canvas 런타임 실행과 구별한다.

현재 수정 합성은 `production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json`이다. 1080p60, 131,010프레임, 2,183.5초(36분23.5초). 본편 실제 화면78,174프레임과 설명52,116프레임은 정확60:40이며, 원래 고양이2초와 회원10초는 별도다. 고정 총 길이·20분 자동 분할은 없다.

원래108문단과 추가36안내 PCM·믹스·KO380/EN388 자막 타이밍을 보존한다. 검정 배경·흰 본문·노란 제목과 고정 하단 자막을 사용한다. Three.js 설명의 보조 문장과 두 줄 자막이 겹친 첫 출력은 실패 근거로 보존했다. 현재 출력은 해당 설명 자산만 균등 축소하여 하단 여백을 확보한다. 자막은 이동하지 않는다.

50개 Three.js·8개 Manim 자산은 정지 상태와 정상 속도 재생으로 확인했다. 현재 합성의 변경 픽셀·접합부와 두 전체 디코드/PTS/AAC 검사는 리뷰 원장의 실제 상태를 따른다. 같은 오디오의 ASR·음량 검사와 변경하지 않은 H264 구간의 검수는 해시·패킷 일치로 재사용한다. 사람 전체 청취·발음은 별도 대기다.

기존 [비공개 기준본](https://youtu.be/ZUrPmDV-bSQ)은 보존한다. 수정본은 검수·`node scripts/collect-video-output.cjs game-lighting-history-01`의 clean/captioned/KO/EN 수집 후 단일 captioned 비공개 업로드를 완료했다. 새로운 실제 ID와 저장 설정은 `publishing/youtube-receipt-threejs-v1.json`에 기록하며 준비를 업로드로 간주하지 않는다. 기존 기준본의 기록은 `publishing/youtube-receipt.json`에 보존한다.

원본·음성·BGM·영상·QA 이미지는 로컬 전용이며 Git에 추가하지 않는다. 최종 사람 청취·공개 권리·원래 Nimbus 파일·잘린 회원 핸들·외부 미디어 백업은 실제 확인 전까지 pending이다. 다른 영상·기존 예약·연구 GPU·외부 스테이징은 보존하고 이 한 편 뒤 멈춘다.
