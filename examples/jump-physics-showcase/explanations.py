"""Why each jump was designed this way, and the core logic behind it.

Paired 1:1 with the profiles in profiles.py. Kept as plain data (not
docstrings) so scene.py can render it directly as on-screen text/code.
"""

EXPLANATIONS = {
    "basic": {
        "why": [
            "가장 단순한 물리 모델이지만, 이후 모든 점프 설계의 '재료'가 된다.",
            "이 프레임 단위 계산을 이해해야 무엇을, 왜 바꾸는지 알 수 있다.",
        ],
        "how": [
            "# 매 프레임 (예: 60fps라면 1/60초마다)",
            "velocity -= gravity        # 중력만큼 속도 감소",
            "position += velocity       # 속도만큼 위치 이동",
            "",
            "# v0=5, gravity=1 이라면:",
            "# 5 → 4 → 3 → 2 → 1 → 0 → -1 → -2 ...",
            "# 0을 지나는 순간, 자연스럽게 상승에서 하강으로 전환된다",
        ],
    },
    "mario": {
        "why": [
            "상승 중엔 약한 중력으로 '체공감'을 주고,",
            "정점을 지나면 강한 중력으로 빠르게 착지시켜 경쾌한 손맛을 만든다.",
            "버튼을 오래 누를수록 약한 중력이 유지돼 점프 높이도 자연히 조절된다.",
        ],
        "how": [
            "if velocity > 0:            # 상승 중",
            "    gravity = G_UP          # 약하게 (4.0)",
            "else:                       # 하강 중",
            "    gravity = G_DOWN        # 강하게 (11.0)",
            "velocity -= gravity",
            "position += velocity",
        ],
    },
    "metroid": {
        "why": [
            "총알을 쏘는 높이가 전투의 핵심이라, 공중에서 조준할 여유가 필요하다.",
            "상승·하강 중력을 둘 다 약하게 줘서 입력 타이밍 실수에 관대해진다.",
        ],
        "how": [
            "gravity = G_FLOATY          # 상승·하강 동일 (2.2)",
            "velocity -= gravity          # 마리오(4.0/11.0)보다 훨씬 약함",
            "position += velocity",
            "",
            "# 같은 최고 높이라도 체공 시간이 훨씬 길어짐",
            "# (약 3.3초 vs 마리오 약 2.0초)",
        ],
    },
    "ghosts_n_goblins": {
        "why": [
            "점프 버튼을 누르는 순간 착지 지점까지 전부 확정시켜서,",
            "'점프는 신중하게'라는 긴장감과 후퇴하며 던지는 히트&런 플레이를 유도한다.",
        ],
        "how": [
            "vx, vy = LAUNCH_VX, LAUNCH_VY   # 점프 시작 시 단 한 번만 결정",
            "",
            "def update():                    # 매 프레임",
            "    vy -= gravity",
            "    x += vx      # 좌우 입력이 들어와도 절대 반영하지 않음",
            "    y += vy",
        ],
    },
    "sf2": {
        "why": [
            "동일한 애니메이션/궤적 그래픽을 그대로 재사용하면서,",
            "속도 배분만 바꿔 '내리꽂는' 타격감을 강화한 사례 — 아트 재작업이 필요 없다.",
        ],
        "how": [
            "# 공간 경로(모양)는 완전히 고정:",
            "shape(s) = 4 * H * s * (1 - s)      # s: 진행도 0~1",
            "",
            "# 오리지널: 일정한 속도로 경로를 따라감",
            "s(t) = t / T",
            "",
            "# 터보: 상승 구간은 느리게, 하강 구간은 빠르게 재분배",
            "s(t) = 0.5 * (t / T_up)                     if t <= T_up",
            "     = 0.5 + 0.5 * (t - T_up) / T_down       if t >  T_up",
        ],
    },
    "smash_squat": {
        "why": [
            "점프와 '위 스매시 공격'이 같은 방향 입력을 공유하기 때문에,",
            "0프레임으로 만들면 두 입력이 구분되지 않아 오조작이 잦아진다.",
            "아주 짧은 준비 프레임을 둬서 입력을 판별할 여유를 만든다.",
        ],
        "how": [
            "state = SQUAT               # 착지 프레임부터 짧게 대기",
            "squat_timer -= 1",
            "if squat_timer <= 0:",
            "    state = AIRBORNE",
            "    velocity = JUMP_V       # 이제서야 실제로 발사",
        ],
    },
    "smash_ultimate": {
        "why": [
            "플레이어 입력이 살짝 늦어도 '즉시 반응했다'는 느낌을 주기 위해,",
            "처음엔 확 띄우고 곧바로 급감속시켜 이후 궤적을 일반적인 점프로 수렴시킨다.",
        ],
        "how": [
            "if t <= T_POP:               # 발동 직후 아주 짧은 구간",
            "    gravity = G_POP           # 매우 강한 중력 (26.0)",
            "    velocity = V_POP - gravity * t   # 초기 속도도 매우 큼 (9.0)",
            "else:                        # 이후에는 평범한 점프처럼",
            "    gravity = G_NORMAL        # 7.0",
        ],
    },
    "jump_king": {
        "why": [
            "차지가 끝나는 순간 결과가 전부 확정되고 공중 수정이 불가능해서,",
            "'파워를 정확히 예측하는 것' 자체가 게임의 핵심 긴장감이 된다.",
        ],
        "how": [
            "while button_held:",
            "    charge += dt              # 누르는 시간 = 파워",
            "",
            "on_release():",
            "    velocity = charge * POWER_SCALE",
            "    locked = True             # 이후 좌우 입력 완전 무시",
        ],
    },
    "celeste": {
        "why": [
            "버튼 하나로 '즉시 반응하는 정밀한 점프 높이 조절'을 구현한다.",
            "일찍 떼면 훨씬 짧게, 오래 잡고 있으면 최대 높이까지 —",
            "같은 초기 속도로 다양한 상황에 대응할 수 있게 만든다.",
        ],
        "how": [
            "velocity = V0                # 홀드 길이와 무관하게 초기 속도는 항상 동일",
            "while rising:",
            "    if button_held:",
            "        gravity = G_RISE      # 느슨하게 (3.0)",
            "    else:",
            "        gravity = G_CUT       # 놓는 순간 확 커짐 (20.0)",
            "    velocity -= gravity",
        ],
    },
    "megaman": {
        "why": [
            "대시로 얻은 수평 속도를 점프에 그대로 이어받게 해서,",
            "'대시 점프'가 순수한 이동 효율 보상이 되도록 설계했다.",
        ],
        "how": [
            "# 수평(x)과 수직(y)은 서로 완전히 독립적으로 계산된다",
            "y_velocity -= gravity        # 오직 y에만 중력이 작용",
            "x += vx                      # x는 일정한 속도로 계속 이동",
            "",
            "# 체공 시간 T는 y축(중력, 초기 수직 속도)에만 좌우된다",
            "# → vx가 아무리 커져도 T는 그대로!",
            "distance = vx * T            # 그래서 vx가 클수록 거리만 커진다",
            "# 걷기 vx=1.3 → 대시 vx=4.2  (같은 T에서 약 3.2배 더 멀리)",
        ],
    },
}
