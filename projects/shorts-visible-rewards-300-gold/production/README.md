# 첫 Shorts 제작 코드

원본 `visible-rewards`의 첫 네 문단만 유지한다. 실제 게임 화면은 clean master의 **0–13.5초만** 읽으며, 이후의720p 구매 장면은 렌더 입력에 들어가지 않는다. 부모 작업이 직접 확인한 가로 편집본의 흰 여백만 `crop=1920:888:0:95`로 제거한 뒤 실제 화면비를 유지해1080×500으로 배치한다. 실제 HUD의500G는 수정하지 않으며 `상황 예시`로 표시한다.13.5초 이후의 가방·금액·선·계산은 직접 그린 설명이고,1,700/2,000/300은 `설명용 가정 · 실제 HUD 값 아님`으로 표시한다.

부모 작업의 명시적 렌더 인계 전에는 아래 준비 명령만 실행한다. 준비는 JSON/SRT/ASS와 폰트 폭 검사만 수행하며 영상·음성 작업을 시작하지 않는다.

```powershell
& 'D:/Github/VideoEditing/manim/.venv/Scripts/python.exe' 'projects/shorts-visible-rewards-300-gold/production/render-short.py' --prepare
```

현재 소스 검수는 `sources/current-source-review.json`에 실제 master SHA256과 `first13_5SecondsDirectlyViewed`, `nativeFhdSourceVerified`, `noLowResolutionPurchaseCutIncluded`를 부모 작업이 기록한다. 렌더는 현재 통합 control의 선택이 이 프로젝트인지 확인하며, 승인 기록을 꾸며 만들지 않는다.

인계 후 유한 작업 순서:

```powershell
& 'D:/Github/VideoEditing/manim/.venv/Scripts/python.exe' 'projects/shorts-visible-rewards-300-gold/production/render-short.py' --render
& 'D:/Github/VideoEditing/manim/.venv/Scripts/python.exe' 'projects/shorts-visible-rewards-300-gold/production/build-audio.py' --build
& 'D:/Github/VideoEditing/manim/.venv/Scripts/python.exe' 'projects/shorts-visible-rewards-300-gold/production/render-short.py' --pair
```

음성은 승인된 원래 PCM0–30.10초를 사용한다. 말끝29.98초 후 낮은 잔향을 보존하고, 다음 문단이 들리기 전의 낮은 에너지 구간 마지막3ms만 디클릭한 뒤0.10초 무음을 붙인다. 새 TTS는 없다. 기존의 외국어 해설 가능성이 있는 믹스 대신 Wanderlust를−31LUFS부터 새로 조용히 믹스하며 음성은 일정한 이득을 유지하고 음악만 덕킹한다. 음악 CC BY4.0 크레딧은 게시 설명에서 생략할 수 없다.

최종 인코딩의 전체 디코딩·프레임/PTS·AAC 동일성·한영 자막·음성 수준·전체 대사 ASR1회·현재 모든 자막/컷/움직임·1080세로/375px 모바일 검수는 아직 남아 있다. 기술 검사로 사람 청취 승인을 대신하지 않는다.

검수 후:

```powershell
node scripts/collect-video-output.cjs shorts-visible-rewards-300-gold
```

완성 Drive 버전의 실제 사용자 승인 뒤 같은 captioned master만 게시한다. 기존 롱폼용 `prepare-youtube-upload.cjs`는960/970 자막과10초 엔드스크린을 자동 주입하므로 이 Shorts에 그대로 실행하지 않는다. 실제 ID·처리 상태·관련 동영상·자막·제목/설명·커버·일일 예약 저장/재열람은 부모 게시 단계에서 수행한다. 이 코드 작성 자체는 업로드·공개·예약·자동화를 실행하지 않는다.
