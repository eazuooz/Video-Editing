# 사용자 제공 자료와 제작 범위

2026-11-08 사용자 요청: 첨부 쇼츠 두 편에 소개된 도구와 아래 픽셀아트 가이드를 전부 확인하여 AI로 2D 게임 리소스를 만드는 영상 제작. 새 한 편의 전체 로컬 검수본까지 승인. YouTube·Drive·예약·다른 편은 미승인.

## 제공된 글의 학습 내용

- 중심 주장: 이미지 한 장 생성이 아니라 캐릭터 일관성 → 픽셀 규격 → 배경 제작 → 리터칭 → 게임 리소스 파이프라인.
- 캐릭터 디자인: NovelAI 원안, ChatGPT 정면·측면·후면·사분면 시트, 검수한 레퍼런스 확보.
- 학습: 픽셀 스타일 LoRA와 캐릭터 LoRA를 구분. LoRA는 작은 데이터셋 자체가 아니라 사전학습 가중치 변화의 저랭크 어댑터.
- 생성: ComfyUI에서 Illustrious XL 체크포인트와 두 LoRA를 결합. 스타일과 인물 특징을 각각 비교하며 강도 조절.
- 규격: 사례의 768×1344 생성 이미지를 96×168로 8배 축소, 필요하면 색 수 제한. 8배는 해당 학습 데이터 규격이며 모든 모델의 법칙이 아님. 축소만으로 결함이 전부 해결되지 않음.
- 학습 데이터: NovelAI 여러 포즈, ChatGPT 방향별 시트, 틀린 디자인을 수정한 이미지. 20~50장은 사용자가 제공한 가이드의 실험 제안이며 원문 수치/보장값이 아님.
- 배경: 캐릭터 포함 장면을 만든 뒤 좌우 Outpainting, 캐릭터 제거, 커진 픽셀 격자 측정·축소, 의자·탁자·벽 경계 리터칭. 사례의 약3배는 측정 기반 조정이며 고정 규칙이 아님.
- 원문 글에는 독립 워크플로우 JSON 첨부가 확인되지 않았다는 제공문 설명. 권장 노드는 재구성임을 구별. 실제 모델 페이지의 이미지 메타데이터 제공 여부는 별도 확인.
- 도구: ComfyUI, ILXL, PixelArt SakuLike ILXL, NovelAI, ChatGPT 이미지 생성, kohya_ss 또는 OneTrainer, Aseprite, Pixel Snapper.
- 검수8항목: 방향별 디자인, 픽셀 크기, 머리/옷 색, 캐릭터/배경 사물 크기, 선명한 외곽선, 투명/잔여 픽셀, 엔진 Point/Nearest, 모델·데이터·출력 사용조건.
- 실패 대응: 데이터 보강, 격자/축소, Palette Quantization, 같은 장면의 확장, 수동 리터칭. 애니메이션은 프레임 사이 정체성과 동작을 추가로 해결해야 하며 정지 이미지의 일관성과 별도 과제.
- 적용: 정지 캐릭터·대화 게임·비주얼 노벨·텍스트 RPG 삽화. 애니메이션 시트/리깅/제한된 동작은 대안이지 완전 자동 해결 보장이 아님.
- 결론: 스타일·캐릭터 분리 학습, AI 출력을 규격화, 사람이 실루엣·의상·경계 검수.
- 제공문 자체에는 실제 이미지 대신 '이미지' 자리표시자만 있음. 이전 작성자가 원문 첨부 이미지를 불러오지 못했다는 단서가 있음. 우리 실측/실행과 타인의 보고를 구분.

## 제공된 캐릭터 시트 프롬프트

Create a consistent character turnaround sheet based on the attached reference image. Include front, side, back, and three-quarter views. Preserve the exact hairstyle, clothing design, accessories, color palette, and body proportions. Use a neutral standing pose, consistent lighting, and a plain background. Do not redesign any character details.

## 첨부 쇼츠의 전체 역할

1편: 도입 → 2dimg2motion(기준 이미지·주요 포즈·중간 프레임·투명 시트) → sprite-gen(이미지/영상 정리·배경 제거·루프·시트) → pixelfx(코드 효과·색 변경·시트) → PixelOE(윤곽 보강·축소·색 제한) → 후처리 필요.

2편: Agent Sprite Forge(기준 이미지·행동별 영상·키잉·정렬·시트·맵) → Codixel(레퍼런스·픽셀·뼈대·코드 움직임) → Pixelbolt(편집 가능한 JSON·픽셀/애니메이션·출력) → Sprite Sheet Diffusion(인물 참조·포즈 조건·로컬 생성 모델) → 프레임별 검수·후처리.

첨부 MP4는 전부 research-reference-only. 타 제작자의 완성 쇼츠·음성·자막을 새 영상 소재로 전용하지 않는다. 원본 파일·해시는 production/local/research/inputs.json.
