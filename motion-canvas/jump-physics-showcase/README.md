# Jump Physics Showcase

프레임마다 중력을 더하는 기본 원리부터, 게임마다 점프를 다르게 설계하는 이유까지
다루는 데모입니다. 캐릭터는 배경을 제거한 각 게임의 실제 레퍼런스 스프라이트를
사용합니다 (`sprites/`, 출처: `Resources/Jump Physics/`).

10개 게임을 각각 **개별 영상**으로 뽑았습니다. 모든 영상은 캐릭터가 화면
왼쪽에 고정된 채로 제자리에서 점프하고, 그 값(높이 또는 이동 거리)이
오른쪽 그래프에 실시간으로 그려지는 동일한 시각 언어를 씁니다(0.85배속).
데모 뒤에는 "왜 이렇게 만들었나" + "어떻게 동작하는가(C++ 핵심 로직)" 설명
카드가 붙습니다.

스트리트 파이터 II(#05)는 왼쪽에 고정된 캐릭터 두 개 + 높이/시간 그래프로
비교합니다. 록맨 X(#10)만 예외로, 두 점프의 높이 곡선이 완전히 동일(수평
속도만 다름)해서 높이/시간 그래프로는 차이가 전혀 안 보이기 때문에 —
캐릭터가 실제로 화면을 가로질러 점프하는 **공간 궤적(포물선)** 그대로
비교합니다.

## 영상 목록

| # | 파일 | 핵심 아이디어 |
|---|---|---|
| 01 | `01_basic_concept.mp4` | 매 프레임 일정한 중력을 속도에 더하는 것 뿐 |
| 02 | `02_mario.mp4` | 상승 중력 약하게 / 하강 중력 강하게 — 체공감 + 경쾌한 착지 |
| 03 | `03_metroid.mp4` | 상승·하강 모두 약하게 — 총알 조준을 위한 둥실둥실한 느낌 |
| 04 | `04_ghosts_n_goblins.mp4` | 낮은 점프 + 공중 좌우 조작 완전 불가 (궤적이 발판 순간 결정) |
| 05 | `05_street_fighter_zangief.mp4` | 궤적은 동일, 시간 배분만 바꿔 하강을 빠르게 — 손맛의 차이 |
| 06 | `06_smash_jump_squat.mp4` | 점프 스쿼트(준비 동작) — 스매시 공격과의 입력 구분 |
| 07 | `07_smash_ultimate.mp4` | 강한 초기 속도 + 순간적 고중력 → 일반 중력 전환 (입력 유예) |
| 08 | `08_jump_king.mp4` | 차지 시간에 비례한 파워, 발사 후 조작 불가 — 올인 설계 |
| 09 | `09_celeste.mp4` | 버튼 홀드 길이로 점프 높이 조절 + 조기 이탈 시 '점프 컷' |
| 10 | `10_megaman_x_dash.mp4` | 걷기 점프 vs 대시 점프 — 높이는 같고 이동 거리만 대폭 증가 |

각 항목의 정확한 "왜 / 어떻게" 문구는 [explanations.py](explanations.py)에
`profiles.py`의 물리 파라미터와 1:1로 매핑되어 있습니다.

## 파일

| 파일 | 설명 |
|---|---|
| `profiles.py` | 각 게임의 점프 물리(속도·중력·구간)를 정의하는 순수 함수 모음 |
| `explanations.py` | 각 점프별 "왜/어떻게" 텍스트 + C++ 의사코드 + Unity C# / Unreal C++ 실제 코드 |
| `scene.py` | Manim 씬 — `BaseJumpScene`(공용 렌더링) + 10개 개별 `SceneXX` 클래스 |
| `01_basic_concept.mp4` ~ `10_megaman_x_dash.mp4` | 게임별 개별 클립 (720p30) |
| `sprites/` | 배경 제거·크롭된 각 게임 캐릭터 스프라이트 |

## 다시 렌더링하기

```powershell
cd d:/Github/VideoEditing

# 개별 영상 하나만
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/jump-physics-showcase/scene.py" Scene02Mario

# 10개 전부
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/jump-physics-showcase/scene.py" Scene01Basic Scene02Mario Scene03Metroid Scene04GhostsNGoblins Scene05StreetFighter Scene06SmashSquat Scene07SmashUltimate Scene08JumpKing Scene09Celeste Scene10MegaManDash
```

`profiles.py`의 각 함수(`mario()`, `metroid()`, `jump_king()` 등) 인자를 바꾸면
해당 영상의 느낌이 바로 달라집니다. 설명 문구를 바꾸려면 `explanations.py`의
`EXPLANATIONS` 딕셔너리를 수정하세요.

## 구현 코드 (Unity C# / Unreal C++)

영상 안에는 엔진 공통의 C++ 스타일 의사코드만 나오고, 실제 엔진별 소스는 여기 아래에 있습니다.
Unity는 `MonoBehaviour`의 `Start()`/`Update()`, Unreal은 `AActor`의 `BeginPlay()`/`Tick()` 기준입니다.

### 점프의 기본 원리

**Unity (C#)**
```csharp
float velocity;
public float gravity = 1f;

void Start() {
    velocity = 5f;   // 처음 위로 주는 속도
}

void Update() {
    velocity -= gravity;   // 매 프레임 중력 적용
    transform.position += Vector3.up * velocity * Time.deltaTime;
}
```

**Unreal (C++)**
```cpp
float Velocity;
float Gravity = 1.0f;

void AJumper::BeginPlay() {
    Super::BeginPlay();
    Velocity = 5.0f;   // 처음 위로 주는 속도
}

void AJumper::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    Velocity -= Gravity;   // 매 프레임 중력 적용
    AddActorWorldOffset(FVector::UpVector * Velocity * DeltaTime);
}
```

### 슈퍼 마리오브라더스

**Unity (C#)**
```csharp
public float gUp = 4f, gDown = 11f;
float velocity;

void Update() {
    float gravity = velocity > 0f ? gUp : gDown;
    velocity -= gravity * Time.deltaTime;
    transform.position += Vector3.up * velocity * Time.deltaTime;
}
```

**Unreal (C++)**
```cpp
float GUp = 4.0f, GDown = 11.0f;
float Velocity;

void AMarioCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    float Gravity = Velocity > 0.0f ? GUp : GDown;
    Velocity -= Gravity * DeltaTime;
    AddActorWorldOffset(FVector::UpVector * Velocity * DeltaTime);
}
```

### 메트로이드

**Unity (C#)**
```csharp
public float gravity = 2.2f;   // 상승·하강 동일, 아주 약하게
float velocity;

void Update() {
    velocity -= gravity * Time.deltaTime;
    transform.position += Vector3.up * velocity * Time.deltaTime;
}
```

**Unreal (C++)**
```cpp
float Gravity = 2.2f;   // 상승·하강 동일, 아주 약하게
float Velocity;

void ASamusCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    Velocity -= Gravity * DeltaTime;
    AddActorWorldOffset(FVector::UpVector * Velocity * DeltaTime);
}
```

### 마계촌

**Unity (C#)**
```csharp
float vx, vy;

void Start() {
    vx = launchVX; vy = launchVY;   // 점프 시작 시 단 한 번만 결정
}

void Update() {
    vy -= gravity * Time.deltaTime;
    // 좌우 입력을 아예 읽지 않음 (Input.GetAxis 호출 없음)
    transform.position += new Vector3(vx, vy) * Time.deltaTime;
}
```

**Unreal (C++)**
```cpp
float Vx, Vy;

void AArthurCharacter::BeginPlay() {
    Super::BeginPlay();
    Vx = LaunchVX; Vy = LaunchVY;   // 점프 시작 시 단 한 번만 결정
}

void AArthurCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    Vy -= Gravity * DeltaTime;
    // 좌우 입력 액션을 아예 바인딩하지 않음
    AddActorWorldOffset(FVector(Vx, 0, Vy) * DeltaTime);
}
```

### 스트리트 파이터 II — 장기에프

**Unity (C#)**
```csharp
float Shape(float s) => 4f * H * s * (1f - s);

void Update() {
    float s = isTurbo ? TurboRemap(t) : t / T;
    transform.position = path.EvaluatePosition(Shape(s));
}

float TurboRemap(float t) =>
    t <= Tup ? 0.5f * (t / Tup) : 0.5f + 0.5f * (t - Tup) / Tdown;
```

**Unreal (C++)**
```cpp
float AZangiefCharacter::Shape(float S) const {
    return 4.0f * H * S * (1.0f - S);
}

void AZangiefCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    float S = bTurbo ? TurboRemap(ElapsedTime) : ElapsedTime / T;
    SetActorLocation(EvaluatePathPosition(Shape(S)));
}
```

### 대난투 스매시브라더스 — 점프 스쿼트

**Unity (C#)**
```csharp
enum State { Squat, Airborne }
State state;
float squatTimer;

void Update() {
    if (state == State.Squat) {
        squatTimer -= Time.deltaTime;
        if (squatTimer <= 0f) {
            state = State.Airborne;
            velocity = jumpV;   // 이제서야 실제로 발사
        }
    }
}
```

**Unreal (C++)**
```cpp
enum class EJumpState { Squat, Airborne };
EJumpState State;
float SquatTimer;

void ASmashCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    if (State == EJumpState::Squat) {
        SquatTimer -= DeltaTime;
        if (SquatTimer <= 0.0f) {
            State = EJumpState::Airborne;
            Velocity = JumpV;   // 이제서야 실제로 발사
        }
    }
}
```

### 대난투 스매시브라더스 얼티밋

**Unity (C#)**
```csharp
void Update() {
    if (t <= tPop) {
        gravity = gPop;                  // 매우 강한 중력
        velocity = vPop - gravity * t;   // 초기 속도도 매우 큼
    } else {
        gravity = gNormal;                // 이후엔 평범한 점프
    }
    velocity -= gravity * Time.deltaTime;
}
```

**Unreal (C++)**
```cpp
void AFighterCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    if (ElapsedTime <= TPop) {
        Gravity = GPop;
        Velocity = VPop - Gravity * ElapsedTime;
    } else {
        Gravity = GNormal;
    }
    Velocity -= Gravity * DeltaTime;
}
```

### 점프킹 (Jump King)

**Unity (C#)**
```csharp
void Update() {
    if (Input.GetButton("Jump")) {
        charge += Time.deltaTime;   // 누르는 시간 = 파워
    }
}

void OnJumpButtonReleased() {
    velocity = charge * powerScale;
    isLocked = true;   // 이후 좌우 입력 완전 무시
}
```

**Unreal (C++)**
```cpp
void AJumpKingCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    if (bJumpHeld) {
        Charge += DeltaTime;   // 누르는 시간 = 파워
    }
}

void AJumpKingCharacter::OnJumpReleased() {
    Velocity = Charge * PowerScale;
    bLocked = true;   // 이후 좌우 입력 완전 무시
}
```

### 셀레스트 (Celeste)

**Unity (C#)**
```csharp
void Update() {
    bool held = Input.GetButton("Jump");
    gravity = (rising && held) ? gRise : gCut;
    velocity -= gravity * Time.deltaTime;
}
// gCut(20) >> gRise(3) 이라 놓자마자 상승이 확 꺾인다
```

**Unreal (C++)**
```cpp
void AMadelineCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    const bool bHeld = bJumpInputHeld;
    Gravity = (bIsRising && bHeld) ? GRise : GCut;
    Velocity -= Gravity * DeltaTime;
}
// GCut(20) >> GRise(3) 이라 놓자마자 상승이 확 꺾인다
```

### 록맨 X — 대시 점프

**Unity (C#)**
```csharp
void Update() {
    yVelocity -= gravity * Time.deltaTime;   // 오직 y에만 중력
    transform.position += new Vector3(vx, yVelocity) * Time.deltaTime;
    // vx는 대시 여부에 따라 1.3 또는 4.2 — 체공 시간엔 영향 없음
}
```

**Unreal (C++)**
```cpp
void AMegaManCharacter::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    YVelocity -= Gravity * DeltaTime;   // 오직 Y에만 중력
    AddActorWorldOffset(FVector(Vx, 0, YVelocity) * DeltaTime);
    // Vx는 대시 여부에 따라 1.3 또는 4.2 — 체공 시간엔 영향 없음
}
```

## 참고

원본 아이디어는 사쿠라이 마사히로(『대난투 스매시브라더스』 디렉터)의
"점프 디자인" 해설 영상에서 다룬 내용을 바탕으로, 현대 게임(점프킹·셀레스트·록맨 X)
사례를 추가해 확장했습니다.
