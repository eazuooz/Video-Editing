# M21 · 표면의 값과 조명

v6의 전체 편집(85컷)을 검토해 숫자 대입 예시는 대본·자막·수식 화면에서 함께 수정했다. 일반식의 상수와 좌표계의 경계조건은 의미를 붙여 설명한다. `narration.py`에는 바뀐 13개 문단의 한영 발화가, `teaching.py`에는 34개 수식 장면의 목표·기호·입력·결과가 들어 있다. `scene-catalog.json`은 전체 컷별 변경 또는 유지 근거를 기록한다.

`surface.cpp`와 `surface.hlsl`은 Direct3D 11 WARP로 실제 셰이더를 계산한다. 움직이는 구와 입력 눈금은 같은 프레임의 선형 파라미터를 사용한다. 두 구의 비교는 같은 삼각형 메시·광원·재질·관찰 조건을 두고, 꼭짓점의 밝기를 보간하는 경우와 픽셀에서 보간한 법선으로 조명을 계산하는 경우를 그린다. 조명식에는 관찰용 정사영과 별도로 고정된 시선 V를 사용한다. `guides.py`는 동일 삼각형의 표면점·법선·광원·R·V에서 스크린 좌표를 구한다. 기존 Unity 장면 표식은 `unity_guides.py`가 실제 캡처 프레임과 원래 카메라 투영에 맞춘다.

제작 순서는 음성 준비·합성과 `align.py`, `sequence.py`, WARP 렌더러 빌드(Visual Studio C++17, d3d11.lib, d3dcompiler.lib), `guides.py`, `assemble.py`, `audio_check.py`, `verification.py`, `record.py`다. GPU 음성·CPU 셰이더의 입력은 작업별 로컬 폴더에 둔다. 검수 근거는 두 최종 master 해시, 온전한 디코딩, 60fps 시각, 표면/벡터 픽셀, 브라우저 구간 재생, 변경된 음성 인식, 보존된 PCM 샘플 비교를 연결한다.
