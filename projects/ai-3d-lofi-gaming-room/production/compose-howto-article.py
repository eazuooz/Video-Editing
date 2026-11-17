"""Reconcile the existing article into an independent, reproducible methodology."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;P=H.parent
base=(H/'companion-source-v2.md').read_text('utf-8')
recipes=json.loads((P/'planning/reproduction-recipes.json').read_text('utf-8'))['recipes']
def request(key):
    r=next(x for x in recipes if x['id']==key)
    return '\n\n### 따라 만들기 요청 · '+r['tool']+' / '+r['id']+'\n\n입력: '+r['input']+'\n\n```txt\n'+r.get('request','\n'.join(r.get('settings',[])))+'\n```\n\n받을 결과: '+r['output']+'\n\n확인할 점: '+r['check']+'\n'
intro='''> 제작 상태: 새 웹게임과 AI 도구 활용 튜토리얼의 로컬 최종 검수 단계입니다. YouTube 게시와 공개 웹 배포는 아직 진행하지 않았습니다.

갈색 머리의 캐릭터가 창밖의 숲을 보며 쉬고, 아이맥 앞에 앉거나 빈백에 누워 책을 읽는 작은 로파이 방을 만들어 봅니다. 여기서 배우려는 것은 이미지 한 장을 잘 뽑는 요령을 넘어, **같은 디자인을 여러 도구의 입력과 출력으로 연결하는 방법**입니다. 그림은 디자인 기준, Tripo의 모델은 움직일 재료, Codex의 요청은 조작 규칙, Unity는 이 재료와 규칙을 실행하는 환경이 됩니다.

이 글은 작업 일지 순서가 아니라 직접 구현할 때 필요한 순서로 설명합니다. 아래 요청문은 같은 결과를 재현하기 위한 정리본입니다. 과거에 도구에 입력했던 문장을 그대로 복원했다는 뜻은 아닙니다. 실제 Tripo 작업은 자체 이미지를 입력한 Image to 3D였고 별도 텍스트 프롬프트는 비워 두었습니다.

{{frame:room}}

## 먼저 준비할 것과 완성 기준

Unity 6000.6 URP 프로젝트, 해당 버전의 Web Build Support, Tripo에서 내려받은 캐릭터 FBX·텍스처·동작 파일, 코드 작업을 할 Codex가 기본 준비물입니다. 이미지 생성은 방의 기준 그림과 캐릭터·소품 입력을 만드는 데 사용합니다. 유료 생성 전에는 현재 계정의 차감 표시를 확인합니다. 아래의 175크레딧은 이 작업의 실제 기록이며 모든 사람에게 적용되는 요금표가 아닙니다.

Unity Hub에서 URP 기반 3D 프로젝트를 준비하고, `Assets/Models`, `Assets/Textures`, `Assets/Animations`, `Assets/Scenes`처럼 입력과 씬을 나눕니다. FBX와 텍스처는 해당 폴더로 가져옵니다. 캐릭터 FBX의 Rig에서 Humanoid를 선택하고 뼈대 대응을 확인한 뒤 적용합니다. 움직이지 않는 헤드폰 같은 소품은 인체 뼈대에 맞출 필요가 없습니다. 비어 있는 씬의 바닥과 조명 아래서 캐릭터 크기와 재질부터 확인합니다.

모델을 너무 크게 또는 작게 가져왔다면 애니메이션 속도로 보상하지 않습니다. 우선 미터 단위의 공간과 캐릭터 키를 정한 뒤 가구 치수를 맞춥니다. 프로젝트마다 가져오기 배율과 뼈대 규격이 다를 수 있으므로, 파일을 가져왔다는 사실과 사용할 준비가 됐다는 사실을 구분합니다.

처음부터 이 방 전체를 한 번에 요청하기보다 최소 장면부터 확인합니다. 바닥에 캐릭터를 세우고, 걷게 하고, 의자 또는 빈백에 안전하게 진입하게 합니다. 이 세 동작이 맞은 다음 소리·날씨·메모를 붙이면, 문제가 생겼을 때 모델과 코드 중 어느 단계가 원인인지 구별하기 쉽습니다.

`<PROJECT_PATH>`는 작업할 Unity 프로젝트의 절대 경로, `<HERO_FBX>`는 실제 캐릭터 파일, `<ANIMATION_FOLDER>`는 사용 가능한 기존 모션 폴더로 바꿉니다. AI에게 파일 위치를 추측하게 하지 말고 존재하는 경로를 전달합니다. 완성 기준도 함께 줍니다. 버튼이 눌리는 것뿐 아니라 **걷기 → 방향 맞춤 → 앉기/눕기 → 생활 → 일어나기**가 이어지고, 새로고침 후 메모가 보존되어야 합니다.

## 그림에서 실행까지 이어지는 데이터

| 단계 | 넣는 것 | 받는 것 | 다음 단계 전에 확인 |
| --- | --- | --- | --- |
| 이미지 생성 | 디자인 조건·참고 그림 | 방 콘셉트, 단독 캐릭터·소품 PNG | 손발·소품 구조가 가려지지 않는지 |
| Tripo | 캐릭터/헤드폰 단독 이미지 | 게임용 메시·재질·뼈대·클립 | 실루엣·관절·파일 묶음 |
| Codex + Unity CLI/MCP | 실제 프로젝트 경로·파일·행동 조건 | 씬·컴포넌트·상태 전환 | 실행한 동작이 요청 조건과 같은지 |
| Unity Web | 검증한 씬·음원·HTML UI | HTTP로 실행할 웹 빌드 | 입력·소리·저장·동작 실제 확인 |

PNG는 모델의 앞모습을 정하지만 뒷면까지 보장하지 않습니다. FBX는 형태와 뼈대를 전달하지만 게임의 버튼과 저장을 만들지는 않습니다. 각 도구의 결과를 다음 도구가 쓸 수 있는 자료로 바꾸는 것이 파이프라인의 핵심입니다.

'''
start=base.index('## 도구 10가지를 역할로 고르기')
body=base[start:]
body=body.replace('## 방 전체보다 캐릭터와 소품을 나누어 만들기','## 일관된 입력 이미지와 분리된 자산 만들기')
body=body.replace('{{frame:model}}',request('room-image')+'\n'+request('hero-image')+'\n{{frame:reference}}\n'+request('headphone-image')+'\n{{frame:prop}}\n'+request('tripo')+'\n{{frame:model}}')
body=body.replace('## 메시와 텍스처를 서로 다른 문제로 보기','## 생성 결과를 게임용 데이터로 정리하기')
body=body.replace('**텍스처(texture)**','{{frame:retopo}}\n\n**텍스처(texture)**')
body=body.replace('## 모션을 이어 붙일 때 필요한 중간 단계','''## AI가 실제 프로젝트를 다루게 하기

Codex에는 먼저 작업할 프로젝트와 보존할 파일을 지정합니다. Unity 공식 CLI/MCP는 AI가 씬을 열고 오브젝트를 만들거나 실행 상태와 빌드 결과를 확인하는 통로입니다. 이 컴퓨터에서는 Unity Hub에 포함된 공식 CLI를 다음과 같이 호출했습니다. 설치 위치와 기능이 같은지 먼저 확인하고, 명령 이름이 PATH에 등록되지 않았다면 실행 파일의 절대 경로를 사용합니다.

```powershell
& "C:/Program Files/Unity Hub/resources/unity.exe" mcp --project-path "<PROJECT_PATH>" --no-banner
```

이 명령은 MCP 도구 서버를 여는 예시이며, 그 자체가 방을 생성하는 명령은 아닙니다. 해당 프로젝트의 Unity Editor와 연결한 뒤 AI가 지원되는 도구를 호출합니다. 도구 호출 성공과 게임 동작 성공은 다릅니다. 변경 뒤에는 Play 상태에서 대상이 보이는지, 버튼을 누른 뒤 어떤 상태로 갔는지까지 확인하도록 요청합니다.

{{frame:mcp}}
'''+request('unity-scope')+request('sofa-image')+request('table-image')+request('layout')+request('materials')+'''
## 모션을 이어 붙일 때 필요한 중간 단계''')
body=body.replace('처음 수정에서는 의자 등받이가 캐릭터를 가렸습니다. 등받이의 높이를 약 78cm에서 37cm로 줄이고 폭도 좁혔으며, 모니터는 13cm 낮췄습니다. 앉기 접촉점과 발이 놓이는 기준은 유지했습니다. 가구의 크기가 맞아야 움직임도 읽힙니다.','가구는 겉모양보다 접촉 기준을 먼저 정합니다. 이 방의 낮은 등받이는 약 37cm이고 모니터도 낮게 배치했습니다. 의자 좌면, 골반, 발바닥이 놓일 바닥, 키보드에 닿을 손의 기준점을 따로 둡니다. 캐릭터를 기준으로 가구 크기를 맞춘 뒤 같은 기준점으로 접근·회전·착석을 연결해야 합니다.')
body=body.replace('{{frame:sit}}','')
body=body.replace('## 차분하게 앉는 동작은 속도만의 문제가 아니다',request('actions')+'''
### 상태 자료와 처리 순서

행동 상태에는 현재 단계, 목적 행동, 진입 기준점, 접촉 가중치가 필요합니다. 다음은 같은 구조를 구현할 때 사용할 수 있는 의사코드입니다. 실제 API 이름과 프로젝트 코드는 다를 수 있습니다.

```txt
requestAction(next):
  pending = next
  if phase is Seated or Reclined:
    phase = Exit        // 책/손 정리와 기존 일어나기 클립
  else if phase is Idle:
    phase = Walk

update():
  Walk  -> 목적지 앞에 도착하면 Align
  Align -> 방향이 맞으면 Enter
  Enter -> 기존 앉기/눕기 클립이 끝나면 Loop
  Loop  -> 생활 동작과 작은 접촉 보정
  Exit  -> 안전한 바닥 자세가 되면 pending으로 Walk
```

움직임 도중 또 버튼을 눌러도 몸을 즉시 다른 자리로 옮기지 않습니다. 다음 요청을 보관하고 Exit를 마친 뒤 전환합니다. 걷기 속도는 기존 클립의 Root Motion과 실제 이동 거리를 함께 보면서 맞춥니다. 다리 주기만 빠르게 돌리면 발이 바닥에서 미끄러집니다.

## 차분하게 앉는 동작은 속도만의 문제가 아니다''')
body=body.replace('독서에는 **역운동학(Inverse Kinematics, IK)** 보정을 사용했습니다.','{{frame:reading}}\n\n독서에는 **역운동학(Inverse Kinematics, IK)** 보정을 사용했습니다.')
anchor='## 머리카락, 잎, 빛을 같은 공간에 놓기'
body=body.replace(anchor,'''### 책과 손을 함께 배치하는 이유

책의 위치만 움직이면 손이 표지 안으로 들어가거나 팔이 페이지를 가로지를 수 있습니다. 책을 먼저 고정 각도로 놓기보다 가슴과 얼굴을 기준으로 책의 자세를 만들고, 그 자세에서 손목과 팔꿈치의 목표를 함께 계산합니다.

책의 가로축은 양어깨 방향을 바닥 평면에 투영한 방향입니다. 누운 몸의 기울기를 그대로 가로축에 쓰면 한쪽 손이 지나치게 위로 올라갈 수 있기 때문입니다. 페이지의 법선은 책 중심에서 얼굴로 향하는 방향을 가로축에 수직이 되게 정리합니다. 손목은 이 책 좌표계의 왼쪽과 오른쪽 표지 바깥에 둡니다. 팔꿈치는 몸 밖으로 유도해 팔뚝이 책을 관통하지 않도록 합니다.

현재 장면에서는 가슴의 기본 위치에 몸 보정량을 더한 뒤 약 0.30m 위로 책 중심을 잡고, 손목은 책 로컬 좌표의 좌우 약 0.20m에 둡니다. 캐릭터와 책 크기가 바뀌면 이 값도 다시 측정해야 합니다. 숫자만 복사하면 다른 체형에 같은 접촉이 나오지 않습니다.

손의 회전도 맞춰야 합니다. Unity Humanoid의 IK 목표 회전과 손목 뼈의 회전 기준은 그대로 같지 않을 수 있습니다. 현재 클립에서 측정한 손바닥 기준 프레임을 역으로 제거한 뒤 목표 프레임을 적용합니다.

```txt
goalRotation = targetPalmFrame * inverse(measuredPalmFrame) * currentIKGoalRotation
```

세 회전은 같은 월드 기준으로 계산하고 곱하는 순서를 유지합니다. 손바닥의 앞뒤와 손가락 방향이 뒤집히면 손이 닿더라도 잡는 모습이 어색합니다. 완성 여부는 정면·옆면·반대쪽에서 손목, 페이지, 팔꿈치의 간격을 보면서 판단합니다. 기존 전신 클립은 유지하고 책을 잡는 데 필요한 부분만 보정하는 이유입니다.
'''+request('book-contact')+'\n'+anchor)
body=body.replace('{{frame:window}}',request('hair')+request('plants-window'))
body=body.replace('### 비 버튼의 상태와 실제 빗줄기를 함께 확인하기','### 창문 영역 안에 비를 만들기')
body=body.replace('비가 켜져도 보이지 않던 원인은 배경과 창문 효과의 앞뒤 순서였습니다.','비는 배경·유리·창틀의 앞뒤 순서를 정한 뒤 만듭니다.')
body=body.replace('{{frame:rain}}','{{frame:rain}}\n'+request('rain')+request('fire'))
body=body.replace('{{frame:coding}}','')
body=body.replace('{{frame:cat}}','''새 삼색 무늬는 몸통과 머리에 같은 노이즈를 반복하지 않고, 등·옆구리에 위치가 있는 큰 무늬를 배치합니다. 배와 얼굴은 밝게 남기고 황갈색과 짙은 무늬를 넓게 나눕니다. 표면은 금속성을 0으로 하고 Smoothness를 낮춰 반짝이는 플라스틱처럼 보이지 않게 합니다. 꼬리는 조각을 이어 붙이기보다 연속된 가늘어지는 메시로 구성하고 끝부분의 색만 점차 어둡게 합니다. 이 단순화는 가까이서도 무늬와 윤곽을 읽기 위한 선택입니다.

{{frame:cat}}
'''+request('cat'))
body=body.replace('## 웹에서는 입력과 저장도 실제로 확인하기',request('radio')+'\n## 웹에서는 입력과 저장도 실제로 확인하기')
body=body.replace('{{frame:web}}',request('notes-timer')+'''
### 저장할 자료와 타이머 계산

```js
// 구조를 설명하는 예시. 기존 프로젝트 키와 충돌하지 않게 이름을 정한다.
const memo = { text: "", updatedAt: 0 };
const timer = { running: false, remainingMs: 15 * 60 * 1000, endAt: null };
// 시작: endAt = Date.now() + remainingMs
// 표시: Math.max(0, endAt - Date.now())
// 일시정지: 남은 시간을 저장하고 endAt을 비운다.
```

메모 입력은 짧게 지연해 저장하되 창을 닫는 순간의 값도 보존합니다. 자동 저장 표시와 실제 저장은 따로 검증합니다. 한글·줄바꿈을 입력하고 새로고침한 뒤 같은 내용인지 비교합니다. 타이머는 실행 중, 일시정지 중, 새로고침 후 세 경우를 각각 확인합니다. 동일 출처(origin)는 프로토콜·호스트·포트의 조합이므로 개발 서버 포트가 바뀌면 저장 공간도 달라집니다.

{{frame:web}}
'''+request('web-build'))
body=body.replace('## 직접 바꿔 볼 세 가지','''## 실패를 빠르게 분리하는 검증 순서

| 보이는 문제 | 먼저 분리할 원인 | 직접 확인 |
| --- | --- | --- |
| 손과 책이 겹침 | 책 좌표와 IK 손목 기준 | 앞·옆·반대 시점, 전환 중간 |
| 걷는데 미끄러짐 | 보폭·실제 이동량·클립 속도 | 발 접촉점을 바닥 기준으로 관찰 |
| 털이 얼룩처럼 반복됨 | UV/무늬 좌표·거칠기 | 같은 조명에서 머리와 몸통 비교 |
| 비 버튼만 켜짐 | 입력 중복·활성 상태·레이어 | 한 클릭에 한 번 변화, 실제 창문 확인 |
| 웹에서 소리가 없음 | 자동재생 제한·로딩·음량 | 사용자 시작 버튼 후 재생 |
| 메모가 사라짐 | 출처 변경·저장 오류·이벤트 충돌 | 같은 주소 새로고침, 저장 내용 비교 |

최소 장면에서 시작해 한 동작씩 추가하고, 같은 카메라와 같은 입력으로 다시 확인합니다. AI에는 “자연스럽게”라는 평가와 함께 **어느 대상이 어디를 관통하는지, 어떤 상태에서 무엇이 남아야 하는지**를 전달하면 수정 범위가 구체적이 됩니다.

## 직접 바꿔 볼 세 가지''')
body=body.replace('- [Tripo Image to 3D]', '- [Tripo Retopo](https://www.tripo3d.ai/product-doc/module-post-processing/retopo), [Tripo Image to 3D]')
body+='\n- 영상 내레이션: [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), 12Hz 1.7B Base와 사용자 음성 레퍼런스를 로컬에서 사용했습니다. 게임 모델 생성 도구와는 별도입니다.\n'
out=intro+body
# Reconcile obsolete beanbag/procedural-animal paragraphs rather than appending
# contradictory revision notes to the reader's methodology.
out=out.replace('빈백에 누워 책을 읽는','소파에 기대어 책을 읽는').replace('의자 또는 빈백','의자 또는 소파').replace('실제 캐릭터·헤드폰 제작','실제 캐릭터·헤드폰·삼색고양이 제작').replace('이번 가구는 코드로 제작','코드 제작 가구와 라이선스 확인 소파 조합')
out=re.sub(r'### 가운데 빈백에서 누워 읽기\n.*?(?=\{\{frame:reading\}\})','''### 등과 다리를 받쳐 주는 소파 독서

독서 자리는 기존 라이브러리의 RG Poly Vintage Retro Stylized Pack 소파를 사용했습니다. CC0 에셋을 가져와 폭 약 2.35m로 맞추고 등 쿠션과 발받침을 배치합니다. 모든 오브젝트를 AI로 다시 생성할 필요는 없습니다. 적합한 기존 자료가 있으면 형태·라이선스를 확인한 뒤 조합합니다.

몸은 PHILIPP 팩의 `Tourist_sit_03` 휴식 클립으로 기대고 다리를 편 자세를 유지합니다. 손을 머리 뒤에 둔 원래 팔은 그대로 독서에 쓰기 어려우므로, `Tourist_sit_02_Map`의 팔만 Avatar Mask로 섞습니다. Avatar Mask는 추가 애니메이션이 영향을 줄 인체 부위를 고르는 기능입니다. 왼팔·오른팔·손가락만 선택하고, 몸통과 다리는 기본 휴식 동작을 유지합니다.

접근 → 방향 맞춤 → KayKit 착석 → 휴식 자세 → 책 펼치기로 이어집니다. 다른 행동을 누르면 책을 먼저 내리고 기존 기립 클립 뒤에 걷기를 연결합니다. 발받침을 통과하지 않도록 열린 옆쪽 통로로 접근합니다. 골반·쿠션·발바닥을 같은 가구 좌표에서 확인한 후 책과 손을 맞춥니다.

''',out,flags=re.S)
out=out.replace('누운 동작을 두 손 전체의 고정 자세로 바꾸지 않고 원래 몸의 흐름을 유지합니다.','기본 휴식 동작과 독서 팔의 흐름을 유지하면서 필요한 접촉만 보정합니다.')
out=out.replace('책의 가로축은 양어깨 방향을 바닥 평면에 투영한 방향입니다. 누운 몸의 기울기를 그대로 가로축에 쓰면 한쪽 손이 지나치게 위로 올라갈 수 있기 때문입니다.','책의 가로축은 소파의 좌우 방향을 기준으로 안정시키고, 몸 위치 보정량을 책에도 함께 적용합니다. 몸의 기울기를 그대로 책 가로축에 쓰면 한쪽 손이 지나치게 위로 올라갈 수 있기 때문입니다.')
out=out.replace('약 0.30m 위로 책 중심을 잡고','소파 앞쪽 약 0.34m, 위쪽 약 0.07m에 책 중심을 잡고')
out=re.sub(r'오른쪽 작은 카펫에는 직접 만든 삼색고양이를 놓았습니다\..*?(?=\{\{frame:cat\}\})','''오른쪽 카펫에는 실제 잠든 삼색고양이 사진을 기준으로 Tripo에서 생성한 모델을 배치했습니다. 입력은 Am9489의 [Calico Cat Asleep](https://commons.wikimedia.org/wiki/File:Calico_Cat_Asleep.jpg), CC0 1.0 사진입니다. 이미지 생성으로 침구와 배경을 정리한 **파생 이미지**를 사용했으므로, 원사진 그대로를 업로드했다고 소개하지 않습니다. 자연스럽게 몸을 말고 앞발을 접은 자세, 얼굴과 꼬리, 흰색·주황·검정 털의 큰 무늬를 유지하도록 요청합니다.

Tripo H3.1 생성에는 55크레딧, Smart Mesh P1.0 삼각형 목표 20K 정리에는 35크레딧이 들었습니다. 총 90크레딧은 앞의 캐릭터·헤드폰 175크레딧과 별도입니다. 약 194만 삼각형 원본에서 실제 19,398삼각형 게임용 결과를 얻고 4K 텍스처를 포함한 FBX로 내보냈습니다. 정리한 모델과 원본 텍스처의 짝이 맞는지 확인하고 Unity에서 얼굴·발·꼬리를 돌려 봅니다.

현재 고양이 재질에는 Base Color와 Normal을 연결하고 금속성을 0, Smoothness를 0.08로 두었습니다. 내보낸 Roughness·Metallic 파일은 보관하되 현재 고양이 재질에 모두 연결했다고 주장하지 않습니다. 작은 수면 호흡은 바닥 접촉을 유지한 미세한 스케일 변화입니다. 별도의 고양이 리깅이나 걷기 모션을 생성한 것은 아닙니다.

''',out,flags=re.S)
out=out.replace('웹 버튼에서는 또 다른 문제가 드러났습니다.','웹 입력은 한 번만 상태를 바꾸는지 확인합니다.').replace('입력을 받는 컴포넌트와 실제 비를 바꾸는 컴포넌트의 메서드 이름이 같아서 한 번 클릭할 때 두 번 토글됐습니다. 실제 변경 메서드를 `SwitchWindowRain`으로 나눠 한 번만 바뀌게 했습니다. 버튼의 켜짐 표시와 보이는 비를 함께 확인해야 찾을 수 있는 문제였습니다.','입력 처리와 실제 비 변경 메서드가 같은 이름이면 한 클릭에 두 번 토글될 수 있습니다. 실제 변경 메서드를 별도 이름으로 나누고 버튼 표시와 보이는 비를 함께 확인합니다.')
out=out.replace('현재 빈백 동작은 KayKit으로 연결했습니다.','현재 소파는 PHILIPP의 휴식 몸과 독서 팔을 Avatar Mask로 조합하고 착석·기립은 KayKit으로 연결했습니다.').replace('초기 의자 독서에 사용한 기존 모션의 출처이며,','휴식·독서 기존 모션의 출처이며,')
out+='\n- 소파: [Vintage Retro Stylized Pack / RG Poly](https://rg-poly.itch.io/vintage-retro-stylized-pack), CC0 1.0. 기존 사용자 라이브러리의 Sofa FBX와 재질을 가져왔습니다.\n- 고양이 사진: [Calico Cat Asleep / Am9489](https://commons.wikimedia.org/wiki/File:Calico_Cat_Asleep.jpg), CC0 1.0. 이미지 생성으로 배경과 구도를 정리한 뒤 Tripo 모델 입력으로 사용했습니다.\n'
out=re.sub(r'독서 자리는 기존 라이브러리의 RG Poly.*?조합합니다\.', '독서용 소파와 테이블은 각각의 단독 입력 이미지를 만들어 Tripo H3.1로 생성했습니다. 밝은 목재 프레임과 크림색 라탄/코드 짜임을 맞추고, 소파는 Triangle 목표 20K에서 실제 22,066삼각형, 테이블은 목표 10K에서 9,375삼각형으로 정리했습니다. 두 가구의 생성·정리는 각각 90크레딧, 합계 180크레딧이며 캐릭터·헤드폰 175와 고양이 90은 별도입니다. 기존 붉은 가죽 소파는 이전 검수본에 남기고 현재 장면은 새 가구를 사용합니다.', out, flags=re.S)
out=out.replace('발받침을 배치합니다.','낮은 우드 테이블을 배치합니다.').replace('발받침을 통과하지 않도록','테이블을 통과하지 않도록').replace('골반·쿠션·발바닥을 같은 가구 좌표에서 확인한 후','골반·등받이·테이블 상판·발바닥을 같은 가구 좌표에서 확인한 후')
out=out.replace('현재 고양이 재질에는 Base Color와 Normal을 연결하고 금속성을 0, Smoothness를 0.08로 두었습니다.', '현재 고양이 재질에는 Base Color와 Normal을 연결하고 금속성을 0, Smoothness를 0.08로 두었습니다.')
out=out.replace('작은 수면 호흡은 바닥 접촉을 유지한 미세한 스케일 변화입니다. 별도의 고양이 리깅이나 걷기 모션을 생성한 것은 아닙니다.', '수면 동작은 원래 메시의 몸통과 꼬리에 다른 가중치를 둔 국소 변형입니다. 몸통은 약 4.8초 주기로 최대 약 5mm, 꼬리는 약 7.5초 주기로 작은 움직임을 더합니다. 얼굴과 앞발은 안정적으로 남기고 꼬리 끝은 턱 바깥으로 움직입니다. 실제 표본에서 얼굴의 변위는 부동소수점 오차 범위였고, 몸통·꼬리의 최대 변위는 약 1.4cm였습니다. UV와 텍스처를 유지한 모델별 영역 마스크이며 일반적인 고양이 리깅이나 걷기 모션을 생성한 것은 아닙니다.')
out=re.sub(r'\n- 소파: \[Vintage Retro Stylized Pack.*?가져왔습니다\.\n', '\n- 현재 소파·테이블: 자체 이미지 입력과 Tripo H3.1 생성·정리 결과. 원본 FBX와 출력별 재질을 함께 보관하며, 과거 라이브러리 가죽 소파와 구분합니다.\n', out)

assert set(re.findall(r'\{\{frame:(.*?)\}\}',out))=={'room','reference','prop','model','retopo','texture','mcp','states','reading','rain','cat','web'}
assert out.count('### 따라 만들기 요청')==19
(H/'companion-article.md').write_text(out,'utf-8')
print('Prepared independent how-to article',len(out),'characters / 19 requests / 12 final frames')
