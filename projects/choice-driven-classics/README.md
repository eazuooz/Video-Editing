# 내 선택으로 결말이 달라지는 세계 고전 소설

1920×1080, 60fps, **정확히 60초·6개 독립 씬**. 세계 고전을 선택형 PC 게임으로 출간하는 디지털 출판사 아이디어.

## 현재 상태

Childhood BGM 포함 화면 검토안. 사용자 제공 대본 사용. 새 톤 TTS 샘플과 선택 이후 화면 확인 대기. **전체 내레이션은 아직 연결되지 않은 검토본이다.**

- 검토 MP4: `shared/output/motion-canvas/choice-driven-classics-BGM-ONLY-REVIEW-20260913T092359Z.mp4`
- 1920×1080, 60fps, 3600프레임/60초. H.264 + AAC. 전체 디코딩 검사 통과.
- 목소리 샘플: `motion-canvas/src/projects/choice-driven-classics/assets/voice-approval-calm-v2.wav`

## 열기 / 빌드

저장소 루트에서:

```powershell
npm run start --prefix motion-canvas -- --host 127.0.0.1 --port 9100
npm run build --prefix motion-canvas
node motion-canvas/scripts/check-classics-visuals.cjs
```

- 편집기: http://localhost:9100/src/projects/choice-driven-classics/project
- 검토 페이지: http://localhost:9100/classics-review.html
- 대본: `script/narration.ko.json`
- 시간·편집 가능한 문구·숫자: `script/storyboard.json`
- 키워드 자막: `script/captions.keywords.ko.srt` (화면 문구, 발화 받아쓰기 자막이 아님)
- 독립 씬: `motion-canvas/src/projects/choice-driven-classics/scenes/scene01.tsx` ~ `scene06.tsx`

## 이 프로젝트에만 적용하는 예외

- 기존 연구 발표형 대신 크림색 책·펜화. 글로벌 기준/과거 프로젝트는 변경하지 않는다.
- 0/8/20/33/43/52/60초 경계 고정. 외부 게임영상 페어·19.5초 슬롯·밈은 적용하지 않는다.
- 원본 그림·본문은 수정/재생성하지 않는다. 균일 확대/위치 조절만 사용한다.
- UI에 `기획 화면 예시`, 가격에 `목표`. 제작비·예상 수익 등 요청하지 않은 자료 수치는 사용하지 않는다.
- 하단 자막 전용 공간. 신규 텍스트는 편집 가능. 기존 이미지 속 UI 문자는 래스터 원본이다.
- 일반 `build-project-narration.ps1` / `build_project_timing.py`를 실행해 고정 시간표를 덮어쓰지 않는다. 발화를 각 슬롯에 배치하고 말끝이 잘리지 않는지 실측한다.
- TTS 샘플 승인 후 전체 장면 합성. BGM 선택 후 다운로드·믹스. -16 LUFS 음성 / -28 LUFS 연속 BGM에서 시작한다.
- 선택 이후 원본 미확보: 새 본문을 꾸며내지 않는다. 현재 씬03의 심증4→5 개념도는 승인 대기 검토안.
- 원본 삽화는 영상 제작용 로컬 보관. 별도 승인 없이 공개 Git 저장소에 원본 자산을 배포하지 않는다.

## 게시 전

음성 샘플 승인 → 장면별 TTS·받아쓰기 → 60초 음성/SRT → BGM 선택·조건 기록 → 같은 믹스를 편집기 WAV/출력 AAC에 연결 → 3600프레임 렌더 → 전구간 시청·자막 겹침·음량 검수.

화면만 확인할 무음 초안 렌더: `node motion-canvas/scripts/render-classics-draft.cjs`. `--bgm` 옵션은 선택된 BGM을 연결한다. 내레이션 없는 검토용이며 최종본으로 사용하지 않는다. 렌더 중에는 소스를 수정하지 않는다(Vite 자동 새로고침으로 렌더 중단 가능).
