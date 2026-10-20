# 영상 제작용 Unity 에셋 라이브러리

사용 프로젝트는 `unity/VideoEditing`이다. 에셋은 `Assets/ThirdParty/YamyamAssetLibrary` 아래에 제품별 `번호-상품명` 폴더로 배치한다. 번들의 Unity 사용 대상 83개와 기존 `LittleNightmare` 패키지 1개가 대상이며, Godot 전용 셰이더 2개는 포함하지 않는다.

제품 목록·공개 상품 주소·복원 원본·실제 설치 상태는 [에셋 목록](../shared/assets/unity-asset-library.json)에 기록한다. 준비 완료와 실제 Unity 검사 완료를 구분하며, 현재 상태는 목록의 `actualImport`를 확인한다.

## 사용

- Unity의 Project 창에서 해당 제품의 `Prefabs`, 모델, 재질과 애니메이션을 찾는다. 원본 제품 구조와 Unity 참조를 유지한다.
- FBX·텍스처 제공 제품은 제품 폴더의 `Generated` 아래에 생성한 URP 재질·프리팹을 사용한다. 애니메이션 전용 모델은 원본 FBX의 클립을 사용한다.
- 영상별 씬은 기존 `Assets/VideoScenes` 구조에 저장하고 공용 에셋을 참조한다. 라이브러리를 영상마다 복제하지 않는다.
- 제품에 포함된 자동 프로젝트 설정과 일부 선택형 Editor 도구는 기본 실행을 꺼 두었다. 모델·재질·프리팹을 사용하기 위해 이 도구들을 켤 필요는 없다.
- 일부 제품의 오래된 데모 씬과 선택형 효과에는 별도 제약이 있을 수 있다. 제품별 기록과 실제 검사 보고서를 확인한다.

프로젝트는 Unity `6000.6.0f1`, URP `17.6.0`을 기준으로 검사한다. `LittleNightmare`의 런타임 리소스 로더에는 Addressables `2.11.2`가 필요하다. 기존에 잠긴 다른 패키지 버전은 보존한다.

## 원본과 복원

다운로드 원본은 `D:\얌얌코딩 에셋`에 보존한다. 제품 파일·이미지·모델·압축파일은 로컬 전용이며 Git에 올리지 않는다. Git에는 가져오기 도구, 제품 목록, 필요한 패키지 설정과 이 안내만 남긴다.

복원 시 목록의 원본 경로와 로컬 `unity-import-candidates.json`을 사용한다. 준비 도구는 `scripts/import-unity-asset-library.py`, GUID·경로 복구 도구는 `scripts/finalize-unity-asset-library.py`다. 코드 호환성 처리는 [도구 안내](../scripts/unity-asset-library-code/README.md)를 따른다.

실제 Unity 검사와 생성 결과는 `unity/VideoEditing/Library/YamyamAssetLibrary` 아래에 남긴다. `headless-project`는 사용자 편집기와 분리된 숨김 검사 프로젝트다. 정상 종료 후 `record-unity-asset-import.py`로 최종 파일·GUID·생성 결과를 기록하고, `install-unity-asset-library.py`로 검증된 폴더와 대응 `.meta`를 설치한다. 기존 씬을 열거나 데스크톱을 조작하지 않는다.

최종 설치 보고서, 검증 보고서와 제품 목록은 기술 검사 범위를 기록한다. 제품별 대표 미리보기는 전체 애니메이션·모든 데모 씬의 시각 검수를 대신하지 않는다. 영상 제작 시 실제 사용 파일과 필요한 출처·크레딧은 해당 영상의 씬 계획에 연결한다.
