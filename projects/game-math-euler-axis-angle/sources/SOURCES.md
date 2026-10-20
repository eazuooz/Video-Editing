# 출처와 검토

## 현재 선택한 V6: 3차원 회전

- 학습 순서의 기준: 사용자 제공 [게임수학 3차원 회전](https://app.notion.com/p/3e10b1ffa61e81d289e1da0dd7584a13)의8.3–8.4. 유용한 설명·예제·중간 단계를 보존하고 독립적인 한국어 내레이션으로 풀었다.
- 현재 좌표 약속: 왼손 좌표계, +X오른쪽/+Y위/+Z앞, 물체축Y-X-Z, 행벡터, 물체→직립 R=Rz(b)Rx(p)Ry(h). 다른 문헌/라이브러리의 규약을 그대로 혼용하지 않는다.
- Unity 비행기·축·링은 자체 제작 설명용 구현이다. 실제 게임의 내부 자세/각도 측정값이 아니다. Manim 계산은 작성한 수식/예제의 시각화다.
- 실제 녹화는 아래3개 독립 소스의 짧은4구간이다. 모두 다운로드 파일의 실제1920×1080/60fps·SHA256를 검증했다. 게임 내부 렌더 해상도를 단정하지 않는다.
- 모든 출처/변형/원음 근거와 프레임 위치는 [현재 footage-plan](../production/revision-v6/footage-plan.json)에 연결한다. 편집자 추가 화면 출처줄은 사용하지 않고 원래 워터마크는 보존한다.

### 독립 게임 녹화

- **Mario Kart 8 Deluxe** — mrlateforschool, [MARIO KART 8 DELUXE (EDITED) NO COPYRIGHT GAMEPLAY for TikTok & YouTube | FREE TO USE | 4K 60FPS](https://www.youtube.com/watch?v=dbA2StfJhqw).
  - 사용 근거: Uploader-described free reuse; no named CC license. The original description permits free use on these platforms but does not separately name monetization. Do not relabel it CC0 or a blanket copyright guarantee.
- **The Legend of Zelda: Tears of the Kingdom** — Royalty Free Game Clips, [Tears of the Kingdom – Free to Use Gameplay (Using Ultrahand & Unlocking the Fuse Ability)](https://www.youtube.com/watch?v=YNQ20CKbY8U).
  - 사용 근거: Uploader-described free use including commercial/non-commercial projects; no named CC license. Explicit in the cached original uploader description.
- **Super Mario Odyssey** — Fox - No Copyright Gameplay, [Super Mario Odyssey Free To Use Gameplay No Copyright No Commentary #1](https://www.youtube.com/watch?v=_wH_-1saHnw).
  - 사용 근거: Creative Commons Attribution license (reuse allowed), per original YouTube metadata. Use the CC BY attribution terms; the description also permits reuse, but its optional-credit sentence does not replace the CC attribution requirement.
  - 라이선스: https://creativecommons.org/licenses/by/4.0/. 변경: 짧은 발췌, 비율 유지 축소, 설명 표식·자막·한국어 내레이션. 원저작자 및 원본 링크와 라이선스를 최종 설명란에 명시한다.
  - 추가 조건: Do not redistribute as a free-footage/no-copyright-gameplay channel.

녹화자의 재사용 허락과 Nintendo 게임IP 권리는 구분한다. 공개/업로드 단계에서는 기존 Nintendo 지침 근거도 함께 확인한다. 마리오 카트의 선택 범위는 무음이며 소리를 만들지 않는다. 젤다·마리오는 분리할 수 없는 원래 게임 혼합음 그대로 사용하고 표준 게임 음량/내레이션 덕킹을 적용한다. 별도로 추가하는 배경음악은 없다.

### 기술 검산에 사용한1차 자료

- [Fletcher Dunn/Ian Parberry official online book](https://gamemath.com/book/orient.html) — 8.3 physical convention;8.3.4 examples;8.4 wording;8.7.1 row matrices and BPH. Local user-provided article is the detailed source backbone.
- [Official online book](https://gamemath.com/book/multiplespaces.html) — 3.2.4 upright origin/object relation and parallel world axes; definition is author-specific, not a universal engine frame name.
- [SciPy official docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html) — Intrinsic/extrinsic distinction and radians/degrees unit parameter; library convention is not silently substituted for source convention.
- [SciPy official docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_euler.html) — Different proper/Tait–Bryan middle-angle ranges and gimbal third-angle-zero choice. Its closed first/third output range is not a replacement for the source half-open canonical choice.
- [Python official docs](https://docs.python.org/3/library/math.html) — floor vs trunc; IEEE-style remainder nearest-integer/ties-to-even definitions used by CPU checks.
- [Microsoft C/C++ runtime official docs](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/remainder-remainderf-remainderl?view=msvc-170) — C/C++ remainder API definition; no conflation with fmod.
- [Lynch/Park, Northwestern Modern Robotics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-2-angular-velocities/) — Angular velocity frame representation. Modern Robotics uses its own right-hand/column convention, so only invariant concepts are transferred.
- [Lynch/Park, Northwestern Modern Robotics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-3-exponential-coordinates-of-rotation-part-2-of-2/) — Exponential map is an operation from exponential coordinates to rotation matrices; constant-axis/velocity integration context.

### 제작 도구·자체 자산

- Unity6000.6.0f1: 직접 작성한 비행기·가동부·축·회전 링. 원본 프로젝트 URP17.6 설정은 보존하고 격리된 캡처 설정/실제 출력은 spatial-plan과 캡처 영수증에 기록한다. 다운로드한 외부 모델은 사용하지 않았다.
- Manim Community0.20.1/Cairo: 수식·코드·방향·범위·선형 보간 애니메이션.
- Qwen3-TTS12Hz1.7B-Base: 승인된 동일한 목소리 참조로 새 대본 음성 생성. 개인 음성참조 파일과 PCM은 Git 및 공개 출처에서 제외한다.
- FFmpeg: 프레임 단위 편집·자막 합성·인코딩·기술 검증. 원래 얌얌코딩 브랜딩2초와 회원 감사10초/회원 식별을 보존한다.

현재4개 출력과 전체 검수는 제작 중이며, 이 문서는 최종 인간 검수나 플랫폼 공개 승인을 의미하지 않는다. 이전 V5 결과·PCM·Drive·비공개 YouTube는 보존한다. 이전 사용 소스/정책은 이전 revision의 계획과 Git 이력에 남아 있다.
