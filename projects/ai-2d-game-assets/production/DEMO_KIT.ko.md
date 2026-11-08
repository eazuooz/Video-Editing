# 영상에 사용한 2D 리소스·워크플로

영상에서 직접 실행한 결과를 담은 자료입니다. 모델 가중치와 학습한 캐릭터 LoRA는 포함하지 않습니다. 영상의 키포즈·리깅·Outpainting 설명은 실제 실행 결과와 구분한 원리 도식입니다.

## ComfyUI 비교 재현

1. [ComfyUI 공식 안내](https://docs.comfy.org/)에 따라 환경을 준비합니다.
2. [Illustrious XL v0.1](https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0)과 [PixelArt SakuLike ILXL v0.1](https://civitai.com/models/1788100/pixelart-sakulikeilxl)의 정확한 이용 조건을 확인한 뒤 모델 파일을 준비합니다.
3. 체크포인트는 `models/checkpoints`, LoRA는 `models/loras`에 넣습니다. 워크플로의 파일 선택을 실제 파일명에 맞춥니다.
4. `comfy-style08-workflow.json`은 실행 서버의 노드 정의로 구성한 UI 연결 파일입니다. `comfy-*-api.json` 두 개는 이번 제작에서 실제 실행한 API 입력입니다.
5. 시드20261108,768×1344,24steps,CFG6,euler_ancestral,normal을 고정하고 LoRA의 MODEL/CLIP 강도0과0.8을 비교합니다. 고정 시드가 캐릭터의 자세·장식을 보장하지 않는 점도 결과에서 확인합니다.

## 픽셀 규격

- 캐릭터:96×168, 투명 PNG. 24색 상한의 무디더링 양자화 후 실제 불투명 영역은20색입니다.
- 배경:426×240. 원래 생성 이미지도 비교용으로 포함했습니다.
- 8배 축소는 이번 스타일 LoRA의 설명에 맞춘 사례입니다. 모든 모델과 이미지에 같은 값을 강제로 적용하지 않습니다.
- Pixelbolt 정령은24×24프레임입니다. JSON의 프레임별 재생 시간과 애니메이션 순서를 읽어야 합니다.
- pixelfx의 불꽃·검 궤적·얼음 효과는 PNG 시트와 JSON 메타데이터를 함께 제공합니다.

## 엔진에 넣을 때

Unity에서는 Sprite로 임포트하고 Point 필터를 비교합니다. 시트는 프레임 영역대로 나누고, 같은 캐릭터의 Pixels Per Unit과 Pivot을 맞춥니다. 화면 크기, 배경과의 비율, 투명도, 루프 연결을 실제 게임 화면에서 확인합니다.

## 권리와 출처

`licenses` 폴더에 Pixelbolt의 포함 예제와 pixelfx의 MIT/NOTICE를 보존했습니다. 새로운 캐릭터·작업실은 이번 제작용으로 생성했습니다. 코드 라이선스, 모델·LoRA, 학습 이미지, 외부 생성 서비스, 출력물의 조건은 각각 확인해야 합니다. 나머지 소개 도구를 실행한 것처럼 표시하지 않았습니다. 상세 실행 구분은 `ASSET_PROVENANCE.md`, 공식 링크·버전은 프로젝트의 `planning/sources.json`을 참고하세요.
