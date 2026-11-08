# 실제 실행과 화면 자료

- 사용자 제공 두 쇼츠는 전체 음성·화면을 조사한 참고자료다. 완성 영상의 클립·음성·화면 자산은 편집에 사용하지 않는다.
- 캐릭터 설정화와 작업실은 이번 제작을 위해 이미지 생성 도구로 만든 새로운 자산이다. 생성 파일은 `assets/local/character-turnaround-v1.png`, `workshop-generated-v1.png`. 기존 게임 캐릭터를 사용하지 않았다.
- 캐릭터 핵심 디자인: 성인 지도 제작자, 적갈색 단발, 노란 삼각 머리핀, 청록 재킷, 황토색 스카프, 남색 바지, 갈색 가방. 방향별 설정화는 정면·측면·후면·3/4, 투명 배경을 요청했다. 결과의 스트랩·장신구 차이는 검수 대상으로 설명한다.
- 배경 프롬프트: 지도 제작자의 따뜻한 작업실, 청록/황토/나무 팔레트, 책상·의자·지도·창문, 사람 없음. 생성 배경과 캐릭터의 합성은 제작 설명용이며 실제 상용 게임 녹화가 아니다.
- ComfyUI `bdb0816a292d221efeb6ec4ae41bcdff3f91fc86`: Illustrious XL v0.1 + SakuLike ILXL v0.1. 시드20261108,768×1344,24steps,CFG6,euler_ancestral,normal. 강도0/0.8 실제 실행. `production/comfy-*-api.json`과 원본PNG의 실행 메타데이터를 보존했다. 새 캐릭터 LoRA 학습은 수행하지 않았다.
- PixelOE1.0.0 실제 실행: 캐릭터96×168, 배경426×240. 실제 결과의 팔레트가 설정된 색 수와 정확히 같다고 가정하지 않는다. 추가 MEDIANCUT24상한/무디더링과 원본 알파를 적용한 최종 캐릭터는 불투명 영역20색이다.
- pixelfx `a84159688af3ca37a4be05a0d422b94451b2e24e`: fire/torch,melee/sword-slash,ice/frost-nova 직접 실행·PNG시트/JSON출력. 원래 시간·프레임 선택을 보존했다. 파랑 불꽃은 palette 옵션만 변경했다. MIT/NOTICE는 `sources/licenses` 참고. 갤러리 전용 유료 폰트는 사용하지 않는다.
- 발 기준점 검수 장면은 pixelfx의 actor-enabled sword-slash 실제 MP4를 원래 30fps/24프레임으로 추출한 합성 프레임을 확대한다. PNG 투명 효과 시트에는 actor가 포함되지 않으므로, 실제 MP4에서 추출한 별도 composite atlas를 사용했다. 기준선은 편집 안내이며 움직임 오류를 측정했다고 주장하지 않는다.
- Pixelbolt `3e69f0581954f908b83f02973cbb26e20601c430`: MIT로 명시된 포함 예제 forest-spirit와 palette 변경본을 실제 CLI로 출력했다. 원래24×24프레임·duration·animation순서를 읽어 재생한다. 포함 예제 및 수정본의 MIT 저작권 고지를 보존한다.
- 나머지 도구는 공식 README를 근거로 원리 도식을 독립 제작했다. API 서비스·모델을 실제 실행한 결과처럼 표시하지 않는다. 외부 생성 예시GIF의 이용 권리를 추정하여 가져오지 않는다.
- Outpainting/캐릭터 제거 장면은 과정 설명용 도식이다. Unity 설정 설명은 자체 픽셀 샘플링·기준점 도식이며 실제 Unity UI 녹화라고 표시하지 않는다.
- 승인된 A01 로컬 clean마스터의 앞2초/마지막10초를 그대로 재사용했다. 회원의 신원·프로필·명단을 새로 만들지 않았다. 해당 강의는 추가 BGM 없는 현재 기본값을 적용한다.

원본·중간산출물의 크기와SHA256: `production/asset-inventory.json`. 모델/데이터/출력물 권리와 코드 라이선스는 서로 구분한다. 링크와 버전은 `planning/sources.json`에 기록했다.
