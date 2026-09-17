# 2.5D 첫 화면 설계 비교 — 무음 검토본

8개 독립 씬 × 19.5초 = 156초. 1920×1080, 60 FPS.
본편468초 중 세번째⅓ 구간만 모은 검토 영상이다. 야숨 장면을 대체한 가짜 자료화면이 아니다.
본편의 야숨 사례 / 디자인 해설 / 설계 비교 1:1:1 구성과 시간은 변경하지 않았다.

## 표현 방식

Motion Canvas의 면·선·전후 배치로 깊이를 만든 2.5D 설명 애니메이션이다.
실제 3D 물리 시뮬레이터, 엔진 구현 튜토리얼, 야숨 복제 맵이 아니다.
흰 배경과 청색 강조를 사용하고, 장면별 한 가지 설계 변수만 A/B로 비교한다.
같은 도형 캐릭터와 공간을 유지해 시선·정보 순서의 차이가 읽히게 한다.
시선 추적 실험이나 검증된 우열처럼 제시하지 않는다.

## 재생 / 편집

- 비교 모음: http://localhost:9100/let-them-play-design-reel.html
- 비교 편집기: http://localhost:9100/src/projects/let-them-play/design-reel/project
- 본편 초안: http://localhost:9100/let-them-play-review.html
- 공통 애니메이션: motion-canvas/src/projects/let-them-play/scenes/design-comparison.tsx
- 독립 씬: motion-canvas/src/projects/let-them-play/design-reel/scene01.tsx ~ scene08.tsx

```powershell
npm run start --prefix motion-canvas -- --host 127.0.0.1 --port 9100
node motion-canvas/scripts/render-let-them-play-design-reel.cjs --qa-only
node motion-canvas/scripts/render-let-them-play-design-reel.cjs
```

렌더 전 전 씬의 전반/후반 정지 화면과 타임라인을 확인한다.
출력은 shared/output/motion-canvas/let-them-play-DESIGN-25D-SILENT-날짜.mp4.
렌더 도중에는 소스를 수정하지 않는다(HMR로 렌더 작업이 중단될 수 있음).
스크립트는 각 씬1170프레임, 전체9360프레임, 해상도, 음성 미포함과 전체 디코딩을 검사한다.

## 미포함 / 다음 제작 단계

실제 야숨 영상, 내레이션, BGM, 음성 동기 자막은 미포함이다.
스크립트·음성·음악 승인은 별도이며, 이 무음 검토본을 업로드용 최종본으로 표시하지 않는다.
음성 확정 후 전체 세 구간의 타이밍과 한·영 SRT를 함께 갱신한다.
