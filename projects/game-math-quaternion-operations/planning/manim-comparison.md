# Manim 선택 — 2026-10-04

| 기준 | ManimGL (3b1b/manim) | Manim Community |
|---|---|---|
| 중심 작업 방식 | OpenGL 미리보기와 실시간 상호작용, 체크포인트를 이용한 장면 편집 | 문서화된 API와 배치 렌더; Cairo/OpenGL 렌더 선택 |
| 3D | 3D 객체·표면·카메라 지원 | ThreeDScene, 3D 축·표면·카메라·화면 고정 라벨 지원 |
| 강의 제작 | 실시간 조작을 보여 주는 수업과 빠른 장면 실험에 적합 | 녹화 강의의 대본·타이밍을 반복해서 렌더하기 편함 |
| 유지보수 | Grant Sanderson의 영상/개인 작업 흐름에 맞춰 발전 | 커뮤니티의 문서·테스트·릴리스 흐름 |
| 호환성 | 패키지 manimgl, import manimlib | 패키지 manim, import manim; GL 코드와 그대로 호환되지 않음 |

**이번 선택: Manim Community 0.20.1 / Cairo.** 현재 저장소의 Python 장면·영상 합성 흐름에 맞고 필요한 3D 몸체 축, 쿼터니언의 반각·곱셈·역회전과 서로 다른 거듭제곱 경로을 구현할 수 있다. 최신판 우열이나 무조건적인 속도 우위라는 뜻은 아니다. 0.20.1을 고정해 재렌더 조건을 보존한다. 설치한 환경에서 실제 import 버전을 확인했고 최종 3D 장면 렌더/검수 결과는 production/qa.json에 기록한다.

3Blue1Brown은 자신의 **ManimGL** 버전을 사용한다. 스타일을 참고하되 그의 대본·장면·목소리를 복제하지 않는다. 양쪽 모두 3D를 지원하므로 ‘3D이면 무조건 GL’이라는 선택 기준은 쓰지 않는다.

공식 확인 자료:
- https://github.com/3b1b/manim
- https://github.com/3b1b/videos#workflow
- https://3b1b.github.io/manim/development/contributing.html
- https://docs.manim.community/en/stable/faq/general.html
- https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html
- https://docs.manim.community/en/stable/installation.html

장면 호환성을 유지하려면 같은 패키지/버전/렌더러를 사용한다. 만약 실시간 마우스 조작 강의를 제작한다면 GL을 별도 프로젝트로 비교할 수 있다.
