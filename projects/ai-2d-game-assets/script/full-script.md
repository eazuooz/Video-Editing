# 전체 대본 · AI 2D 게임 리소스

AI 그림, 어떻게 게임 리소스로 만들까? | 2D 픽셀아트·애니메이션 제작

> 현지 제작 검수용. 플랫폼 업로드 승인 아님.

## 01 · 그림에서 게임 리소스로

이 캐릭터 그림을 게임에 넣는다고 생각해 볼까요? 서 있는 모습은 마음에 들어도, 옆으로 돌면 가방 위치가 바뀌고 움직일 때마다 얼굴이 달라진다면 쓰기 어렵습니다. 오늘은 캐릭터를 같은 모습으로 유지하고, 픽셀 크기와 배경을 맞춘 다음, 애니메이션과 효과까지 정리하는 과정을 살펴보겠습니다.

화면: Actual authored asset in game-like composition → identify consistency problem → preview pipeline

## 02 · 생성·정리·검수

먼저 작업을 세 부분으로 나누면 도구를 고르기 쉬워집니다. 이미지 모델은 그림의 후보를 만들고, 후처리 도구는 크기와 색, 투명 배경을 정리합니다. 마지막으로 엔진에서 실제 크기로 놓고 확인합니다. 여덟 가지 공개 도구도 이 과정의 서로 다른 부분을 맡습니다. 모든 도구를 한꺼번에 설치할 필요는 없습니다.

화면: Same sprite carried through generation / processing / validation; each stage reveals its actual output

## 03 · Character Design (캐릭터 디자인)

출발점은 캐릭터의 디자인을 확정하는 것입니다. 머리 모양, 옷 색, 장신구, 가방 위치처럼 바뀌면 안 되는 특징부터 적어 둡니다. 여기서는 노란 머리핀, 청록색 재킷, 갈색 가방을 기준으로 삼겠습니다. 노벨에이아이 같은 이미지 도구로 후보를 만들더라도, 예쁜 그림을 계속 모으기보다 하나의 디자인을 먼저 선택하는 편이 좋습니다.

화면: Full-sized original character; attached callouts on clip, jacket and bag

## 04 · Turnaround Sheet (방향별 설정화)

다음은 같은 캐릭터의 정면, 측면, 후면을 한눈에 보는 설정화입니다. 챗지피티 이미지 생성 등에 기준 그림을 넣고, 옷과 비율을 유지한 채 방향만 바꿔 달라고 요청할 수 있습니다. 하지만 시트가 만들어졌다고 검수가 끝나는 것은 아닙니다. 머리핀이 어느 쪽에 있는지, 가방 끈이 등에 어떻게 이어지는지, 신발과 소매가 같은지 나란히 비교해야 합니다.

화면: Generated four-view sheet, inspect accessories and strap; no claim of perfect consistency

## 05 · Dataset (학습 데이터)

같은 디자인을 여러 자세로 계속 만들어야 한다면, 이 설정화를 학습 데이터의 기준으로 사용합니다. 정면만 많이 모으면 측면이나 등 뒤를 만들 때 필요한 정보가 부족합니다. 노벨에이아이에서 만든 여러 자세와 챗지피티의 방향별 시트를 함께 모으되, 틀린 머리핀이나 다른 옷이 섞인 그림은 먼저 수정하거나 제외합니다. 처음에는 검수한 스무 장에서 쉰 장 정도로 실험할 수 있지만, 장수보다 서로 다른 자세와 정확한 디자인이 중요합니다.

화면: View/pose coverage diagram; identify training inputs versus learned adapter

## 06 · LoRA (저랭크 적응)

이때 사용하는 로라는 작은 이미지 폴더의 이름이 아닙니다. 이미 학습된 기본 모델을 통째로 다시 학습하는 대신, 모델에 더할 변화량을 작은 행렬로 학습하는 어댑터입니다. 쉽게 말하면 기본 모델의 그림 능력에, 특정 캐릭터나 표현 방식을 익힌 추가 설정을 붙이는 것입니다. 이미지와 설명문은 학습 재료이고, 학습이 끝난 로라 파일은 그 재료로 얻은 결과입니다.

화면: Input images → training → learned low-rank adapter; plain weight-change explanation

## 07 · Style + Character (스타일과 캐릭터)

픽셀 스타일과 캐릭터의 정체성은 역할이 다릅니다. 스타일 로라는 어떤 느낌으로 그릴지를, 캐릭터 로라는 누구를 그릴지를 담당하도록 분리할 수 있습니다. 코야 에스에스나 원트레이너 같은 학습 도구를 사용할 때는, 나중에 생성에 쓸 기본 모델과 맞는 학습 구성을 선택해야 합니다. 같은 로라라는 이름이어도 서로 다른 모델 계열의 파일을 아무렇게나 섞어 쓸 수는 없습니다.

화면: Style and identity as two separate labeled adapter paths

## 08 · ComfyUI (노드 기반 생성)

이제 컴피유아이에서 생성 흐름을 연결해 보겠습니다. 체크포인트는 기본 이미지 모델입니다. 일러스트리어스 엑스엘 계열을 불러오고, 여기에 대응하는 픽셀 스타일 로라를 연결합니다. 캐릭터 로라가 준비되어 있다면 그다음 로라 노드로 이어 붙입니다. 모델과 클립 연결을 함께 이어야 이미지 모델과 문장을 해석하는 부분에 설정이 전달됩니다.

화면: Executable Comfy API workflow redrawn from actual graph, outputs beside MODEL/CLIP connections

## 09 · 같은 조건에서 강도 비교

프롬프트와 해상도, 시드를 고정하면 로라 강도를 바꿨을 때의 차이를 비교하기 좋습니다. 시드는 처음 사용하는 무작위 값의 출발점을 정합니다. 픽셀 스타일이 약하면 일반 일러스트에 가까워지고, 너무 강하면 작은 장식이나 얼굴이 뭉개질 수 있습니다. 스타일과 캐릭터 강도를 동시에 마구 바꾸기보다, 한쪽씩 바꾸며 지켜야 할 특징을 확인합니다. 같은 시드여도 자세와 장식까지 완전히 고정되는 것은 아니므로, 이 차이도 함께 봐야 합니다.

화면: Actual same-seed Comfy output with style strength 0 and 0.8; no fabricated trained character LoRA

## 10 · 생성에서 저장까지

연결은 기본 모델과 로라에서 끝나지 않습니다. 문장을 인코딩하고, 샘플러가 잠재 이미지의 노이즈를 단계적으로 정리한 뒤, 브이에이이 디코더가 보이는 이미지로 바꿉니다. 마지막에 크기 조절과 저장을 붙입니다. 이렇게 각 단계를 나누어 두면, 마음에 드는 캐릭터는 유지하면서 축소 방식이나 팔레트만 바꿔 비교하기 쉽습니다. 캐릭터 로라는 학습한 파일이 준비되었을 때 추가합니다.

화면: Saved graph stages with same output carried to processing

## 11 · Pixel Grid (픽셀 격자)

결과가 도트 그림처럼 보여도 바로 게임용 픽셀아트가 되는 것은 아닙니다. 확대하면 어떤 칸은 넓고 어떤 칸은 좁거나, 경계에 흐릿한 색이 끼어 있을 수 있습니다. 픽셀아트는 작은 논리 해상도에서 한 칸씩 읽혀야 합니다. 그래서 먼저 게임 안에서 사용할 원본 픽셀 크기를 정하고, 생성된 그림을 그 격자에 맞춰 정리합니다.

화면: Actual zoomed pixel clusters, source versus logical grid

## 12 · 768×1344 → 96×168

픽셀아트 사쿠라이크 일러스트리어스 로라는, 여덟 배로 커진 픽셀을 만드는 용도로 소개되어 있습니다. 이 규격에서는 가로 칠백육십팔, 세로 천삼백사십사 이미지를 가로 아흔여섯, 세로 백예순여덟로 줄이는 방법을 비교할 수 있습니다. 중요한 것은 숫자를 외우는 게 아닙니다. 생성 그림의 픽셀 표현과 게임에서 쓸 격자를 맞추는 것입니다. 다른 모델이나 다른 그림에 같은 축소 비율을 강제로 적용하지 않습니다.

화면: 768x1344 and96x168 exact-size example; nearest versus actual PixelOE

## 13 · Palette Quantization (색상 수 제한)

격자를 맞춘 뒤에는 팔레트를 확인합니다. 팔레트는 이 리소스에 사용할 색의 묶음입니다. 비슷한 갈색이 수십 개 섞여 있으면 작은 화면에서 지저분해지고, 프레임마다 색을 따로 줄이면 옷이 깜빡일 수도 있습니다. 캐릭터 전체에 같은 팔레트를 적용하고, 눈이나 머리핀처럼 꼭 읽혀야 하는 부분이 남는지 비교합니다. 색을 줄이는 목적은 무조건 적게 만드는 것이 아니라 형태를 또렷하게 만드는 것입니다.

화면: Actual palette swatches counted from processed image, shared-palette concept

## 14 · Alpha + Retouch (투명도와 리터칭)

투명 배경도 눈으로 확인해야 합니다. 체크무늬가 그림에 그려져 있는 것과, 실제 알파 값으로 배경이 비어 있는 것은 다릅니다. 밝은 바탕과 어두운 바탕에 번갈아 올려 보면 흰 테두리나 남은 배경색이 잘 드러납니다. 아세프라이트 같은 편집기에서 외곽선과 잔여 픽셀을 정리하고, 확대 화면뿐 아니라 게임에서 보일 크기로도 읽히는지 확인합니다.

화면: Real alpha over light/dark/checker backgrounds; actual contour visible

## 15 · Outpainting (배경 확장)

이제 완성한 캐릭터 옆에 배경을 놓아 보겠습니다. 캐릭터와 배경을 완전히 따로 만들면 색감도 다르고, 의자와 사람의 크기도 어긋나기 쉽습니다. 한 가지 방법은 캐릭터가 들어 있는 장면을 기준으로 바깥 영역을 확장하는 아웃페인팅입니다. 기존 공간의 색과 사물 크기를 이어 가도록 확장하고, 배경 레이어에서는 캐릭터를 제거해 별도 스프라이트를 놓을 자리를 확보합니다.

화면: Outpainting process illustration over our workshop; not claimed as an executed outpaint

## 16 · 배경과 캐릭터의 기준 맞추기

확장한 배경은 픽셀 크기도 다시 봐야 합니다. 캐릭터의 외곽선은 한 칸인데 의자의 선만 세 칸처럼 커 보인다면, 같은 세계에 있다는 느낌이 약해집니다. 배경의 축소 비율은 실제 격자를 보고 정하고, 캐릭터 키와 의자 높이도 함께 맞춥니다. 마지막에는 벽과 바닥, 의자 다리처럼 깨진 경계를 손봅니다. 배경을 통째로 다시 뽑기보다 어긋난 부분을 구체적으로 고치는 단계입니다.

화면: Same real processed background and sprite; pixel scale and furniture scale shown separately

## 17 · 정지 이미지와 연속 동작

여기까지는 정지 리소스를 만드는 과정입니다. 대화 게임이나 비주얼 노벨에서는 이것만으로도 활용 범위가 넓습니다. 하지만 걷기나 공격에는 다른 검수가 필요합니다. 같은 얼굴을 유지하면서 발이 바닥에 닿고, 몸 크기가 튀지 않고, 동작의 시작과 끝이 이어져야 합니다. 이제 여덟 가지 도구가 이 남은 작업을 어떻게 나누어 맡는지 보겠습니다.

화면: Actual still asset versus native Pixelbolt animation; temporal criteria introduced

## 18 · 01 · 2dimg2motion

투디 이미지 투 모션은 기준 캐릭터에서 주요 자세를 다시 그리고, 그 사이 프레임을 채우는 작업 흐름입니다. 준비 자세, 크게 움직인 자세, 돌아오는 자세를 먼저 잡는 방식입니다. 기본 구성에는 열네 프레임 규칙이 있지만, 프레임 수 자체가 자연스러움을 보장하지는 않습니다. 무기와 손이 사라지지 않는지, 발 기준선과 몸 크기가 유지되는지 확인한 뒤 투명 이미지와 시트로 정리합니다.

화면: Key pose/in-between diagram with articulated original schematic figure, labeled workflow illustration

## 19 · 02 · sprite-gen

스프라이트 젠은 이미지와 영상, 두 경로를 다룹니다. 자세별 이미지를 만들고 시트로 정리할 수도 있고, 이미지에서 만든 짧은 영상에서 필요한 프레임을 꺼낼 수도 있습니다. 배경 제거, 프레임 추출, 반복 구간 선택과 아틀라스 구성을 연결하는 도구입니다. 아틀라스는 여러 이미지를 한 장에 모으고 각각의 위치를 기록한 묶음입니다. 생성 서비스와 정리 도구의 역할을 나눠 보면 이해하기 쉽습니다.

화면: Video/row paths converge on actual exported atlas image and its real frame metadata

## 20 · 03 · pixelfx

픽셀 에프엑스는 캐릭터에 붙일 불꽃, 폭발, 검 궤적 같은 효과에 잘 맞습니다. 이미지 모델이 매번 새 그림을 만드는 대신, 코드가 시간에 따라 픽셀을 그립니다. 화면의 불꽃도 같은 동작을 유지하면서 팔레트만 바꿀 수 있습니다. 효과를 직접 실행하거나 투명 스프라이트 시트로 내보내면, 엔진에서는 그 프레임들을 순서대로 재생할 수 있습니다.

화면: Actual pixelfx fire/slash/frost exports at native timing; blue fire variant uses palette only

## 21 · 04 · PixelOE

픽셀 오이는 앞에서 본 픽셀 정리 단계에 들어갑니다. 작은 크기로 줄일 때 중요한 윤곽이 없어지지 않도록 경계를 보강하고, 축소와 색상 수 조절을 수행하는 이미지 처리 도구입니다. 픽셀 스내퍼도 흐트러진 픽셀 격자와 팔레트를 정리할 때 비교할 수 있습니다. 둘 다 새 걷기 동작을 만들어 주는 도구로 생각하면 안 됩니다. 실제 결과를 확대해 보고, 가는 선과 얼굴이 어느 쪽에서 잘 남는지 선택합니다.

화면: Actual PixelOE before/after on our sprite/background; Pixel Snapper described, not claimed executed

## 22 · 05 · Agent Sprite Forge

에이전트 스프라이트 포지는 하나의 기준 이미지에서 여러 행동을 준비하는 흐름을 묶습니다. 대기, 걷기, 달리기, 공격처럼 행동마다 영상을 만들고, 배경 제거와 정렬, 반복 구간, 재생 시간을 정리합니다. 맵과 타일을 위한 경로도 갖고 있습니다. 이때는 행동 하나가 예쁜지만 볼 게 아니라, 대기에서 달리기로 바꿀 때 키와 발 위치가 갑자기 달라지지 않는지 함께 검수해야 합니다.

화면: Action/registration/loop workflow illustration; no third-party generated demo assets assumed licensed

## 23 · 06 · Codixel

코디셀은 레퍼런스를 바탕으로 코드와 뼈대를 이용해 움직임을 구성하는 접근입니다. 예를 들어 긴 꼬리나 몸통을 여러 부분으로 나누고, 연결된 기준점을 따라 움직이도록 만들 수 있습니다. 같은 그림 조각을 제어하므로 원하는 부분의 움직임을 직접 고치기 좋습니다. 대신 몸이 돌아가며 새로 보여야 하는 뒷면은 없는 그림에서 저절로 생기지 않습니다. 그 부분은 추가 이미지나 다른 생성 과정이 필요합니다.

화면: Explicit skeletal principle illustration, linked tail control points; not fake Codixel execution

## 24 · 07 · Pixelbolt

픽셀볼트는 색과 모양, 프레임을 제이슨이라는 텍스트 설계도로 관리합니다. 지금 정령은 이미지 모델이 다시 그린 것이 아닙니다. 같은 설계도에서 팔레트만 바꿔 출력한 결과입니다. 눈 위치나 특정 프레임도 이렇게 좁은 범위로 고칠 수 있습니다. 작은 아이콘과 스프라이트, 반복 효과처럼 정확하게 수정하고 다시 출력해야 하는 작업에 어울립니다.

화면: Actual original/modified Pixelbolt recipe exports; palette-only diff shown next to synchronized animation

## 25 · 08 · Sprite Sheet Diffusion

스프라이트 시트 디퓨전은 참조 캐릭터와 포즈 순서를 조건으로 사용하는 생성 모델 연구입니다. 뼈대를 원하는 순서로 제시하고, 그 자세에 맞는 캐릭터 프레임을 생성하는 방식입니다. 로컬 추론에는 코드만 아니라 모델 가중치와 환경도 필요합니다. 따라서 설치 버튼 하나로 끝나는 편집기와는 다릅니다. 결과에서도 옷과 얼굴의 일관성, 동작 사이의 연결을 프레임별로 확인해야 합니다.

화면: Reference + ordered poses → frames: research workflow illustration, no local weight execution claimed

## 26 · 내게 필요한 경로 선택

도구를 고를 때는 원하는 결과부터 정하면 됩니다. 정지 캐릭터와 배경이 필요하면 디자인과 픽셀 정리에 집중합니다. 여러 동작이 필요하면 주요 자세를 생성할지, 영상에서 프레임을 추출할지, 뼈대로 움직일지 결정합니다. 불꽃이나 작은 아이콘처럼 수정 범위가 명확한 자산은 코드 기반 방식도 효과적입니다. 모든 과정을 같은 생성 모델 하나에 맡길 이유는 없습니다.

화면: Asset-type routing with actual assets next to each route

## 27 · Unity Import (유니티 적용)

완성한 피엔지는 엔진에 넣어서 마지막으로 확인합니다. 유니티에서는 스프라이트로 임포트하고, 픽셀아트는 포인트 필터로 원래 칸을 또렷하게 보이게 할 수 있습니다. 한 장에 여러 프레임을 넣었다면 프레임 영역과 순서를 나눕니다. 픽셀 퍼 유닛은 게임 공간 한 단위에 들어가는 픽셀 수이고, 피벗은 배치와 회전의 기준점입니다. 같은 캐릭터의 동작들은 이 기준도 일치해야 합니다.

화면: Unity settings explained with actual nearest/bilinear sprite sampling and pivot guides; own compositor, not fake Unity UI

## 28 · 게임 안에서 확인할 것

검수는 파일이 열리는지에서 끝나지 않습니다. 밝고 어두운 배경에서 외곽선을 확인하고, 배경 사물 옆에서 캐릭터 크기를 봅니다. 애니메이션은 정상 속도로 반복한 뒤 프레임을 넘겨 보며 발 미끄러짐, 몸 크기 변화, 마지막에서 첫 프레임으로 튀는 지점을 찾습니다. 게임에 필요한 동작 길이와 맞는지도 봐야 합니다. 보기 좋은 생성 영상이 곧 반응 좋은 게임 동작인 것은 아닙니다.

화면: Real export native playback then frame steps; actual frame borders and baseline, no invented measured errors

## 29 · 무료 코드와 생성 비용

마지막으로 무료 공개 코드와 생성 서비스 비용은 구분해야 합니다. 도구가 엠아이티나 아파치 라이선스여도, 연결한 이미지나 영상 서비스까지 무료가 되는 것은 아닙니다. 기본 모델과 로라, 학습 이미지, 출력물의 이용 조건도 각각 확인합니다. 특히 다른 사람의 캐릭터를 그대로 학습한 경우까지 도구의 코드 라이선스가 해결해 주지는 않습니다. 프로젝트에는 사용한 모델 버전과 출처, 필요한 표시 조건을 함께 남겨 둡니다.

화면: Separate code/provider/model/data/output conditions beside actual asset versions

## 30 · 게임에 맞게 완성하기

결국 핵심은 세 가지입니다. 같은 캐릭터라고 알아볼 수 있도록 디자인을 유지하고, 픽셀 격자와 색, 투명도와 크기를 통일하고, 실제 게임 화면에서 움직임과 가독성을 확인하는 것입니다. 에이아이는 후보를 빠르게 만들고 반복 작업을 도와줄 수 있습니다. 그 후보를 우리 게임에 맞는 리소스로 완성하는 기준은, 생성 버튼 뒤의 이 과정에서 만들어집니다.

화면: Same final composed workshop + sprite/effects; three conclusions inherited from body
