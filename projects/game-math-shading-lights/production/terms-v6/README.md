# M21 · 빛과 셰이딩 용어·수식 수정본

기존 v5의 재질 구, 실제 게임 7컷, 해·법선·카메라 움직임과 장면 길이를 기준으로 편집했다. `notation.py`는 장면별 영문·국문 제목과 수학식·코드·예시를 정의한다. `layout.py`는 정식 수학 표기를 조판하고 강조할 구절을 원래 문단의 발화 시점과 연결한다. 공식과 코드가 같은 변수를 어떻게 표현하는지 한 화면에서 비교한다.

물리량의 이름과 단위는 [PBRT의 Radiometry](https://pbr-book.org/4ed/Radiometry,_Spectra,_and_Color/Radiometry), 삼각형의 정점 색 보간은 [Microsoft의 Triangle Interpolation](https://learn.microsoft.com/en-us/windows/win32/direct3d9/triangle-interpolation), 반사 함수의 입력 부호는 [HLSL reflect](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-reflect)에 근거한다. 면적·입체각에 대한 미분과 코드의 유한한 작은 구간 평균을 구분한다.

기존 한국어 음성과 게임 사운드 위에서 복사조도·복사휘도가 등장하는 여덟 문장만 승인된 Qwen 목소리로 녹음했다. `voice.py`가 문장과 경계를 찾고 `mix.py`가 문장 사이 호흡에서 기존 믹스와 잇는다. `speechcheck.py`가 녹음한 문장의 단어 시점을 검사한다. `build.py layers` → `build.py render` → `build.py join --audio <pair-audio.m4a>` 순서로 완성한다. `inspect_master.py`는 두 파일을 전체 디코딩하고 최종 인코딩에서 78개의 용어 제목과 수학식·코드 픽셀 및 브라우저 재생을 검사한다. `record.py`가 해당 버전의 결과를 M21 검수표에 기록한다.
