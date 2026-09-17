# 표현 방식 검토 — 2D / 2.5D

추천은 Motion Canvas 기반2.5D: 기존 흰 발표형 스타일을 유지하면서 바닥·두께로 깊이를 표현한다.
2D도 동작과 피드백 설명에 적합하다. 이번 샘플은 같은 동작을 좌우에 나란히 배치한12초 무음 비교다.
3D 엔진으로 렌더한 것은 아니며, 직접 만든2D 다각형으로 입체감을 표현한다. 실제 입력/충돌 물리 시뮬레이션이 아니다.
본편의8씬/1:1:1 비율/대본/음성 파일은 교체하지 않는다. 사용자 검토 후 적용 범위를 결정한다.

- 샘플: motion-canvas/src/projects/let-them-play/lookdev/project.ts
- 미리보기: http://localhost:9100/let-them-play-lookdev.html
- 렌더: motion-canvas 폴더에서 node scripts/render-let-them-play-lookdev.cjs
- 결과: shared/output/motion-canvas/let-them-play-2d-vs-25d-SILENT-*.mp4

Manim은 수학 애니메이션을 중심으로 하는 도구여서 수식·그래프·물리량 설명에 우선 활용한다. [공식 소개](https://www.manim.community/)
Motion Canvas는 코드 애니메이션과 편집기 음성 동기화를 제공한다. 이번 채널 파이프라인과 이어 쓰는 것이 유리하다는 판단이다. [공식 소개](https://motioncanvas.io/)
실제 시야 가림·카메라·3차원 공간의 경로/충돌이 설명 주제가 되면 별도3D 샘플 제작을 검토한다. 이번 작업에는 엔진 설치를 포함하지 않는다.
