"""Jump-physics models for the "jump design" showcase.

Every game applies gravity to vertical velocity every frame; what differs
between games is *when* gravity is strong or weak, and whether the player
keeps any control once airborne. These functions build closed-form
piecewise height(t) (and sometimes x(t)) curves for each design, so a
Manim ``always_redraw`` can sample them at any point in continuous time.

All heights share the same scene scale (peak height around H = 3) unless
a game's design specifically calls for a lower/higher jump.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np


def _v0_for_height(g: float, h: float) -> float:
    return float(np.sqrt(2 * g * h))


def _t_up(v0: float, g: float) -> float:
    return v0 / g


def _t_down_for_height(h: float, g: float) -> float:
    return float(np.sqrt(2 * h / g))


@dataclass
class Profile:
    key: str
    title: str
    subtitle: str
    height: Callable[[float], float]
    total: float
    x: Callable[[float], float] = field(default=lambda t: 0.0)
    caption: str = ""
    show_trajectory: bool = False  # True -> plot x/y path instead of height/time
    velocity: Optional[Callable[[float], float]] = None  # for the HUD readout in the intro


# ---------------------------------------------------------------------------
# 0. Basic concept: one constant gravity, applied every frame
# ---------------------------------------------------------------------------

def basic_concept(g=6.0, v0=5.0):
    t_up = _t_up(v0, g)
    total = 2 * t_up

    def height(t):
        tt = t % total
        return v0 * tt - 0.5 * g * tt**2

    def velocity(t):
        tt = t % total
        return v0 - g * tt

    return Profile(
        key="basic",
        title="점프의 기본 원리",
        subtitle="공중에 있는 동안 매 프레임 일정한 중력을 속도에 더한다",
        height=height,
        total=total,
        velocity=velocity,
        caption="위로 속도 5 → 매 프레임 -1 → 5,4,3,2,1,0,-1,-2 ... 로 자연스럽게 낙하 전환",
    )


# ---------------------------------------------------------------------------
# 1. Super Mario Bros: weak rise gravity, strong fall gravity
# ---------------------------------------------------------------------------

def mario(g_up=4.0, g_down=11.0, h=3.0):
    v_up = _v0_for_height(g_up, h)
    t_up = _t_up(v_up, g_up)
    t_down = _t_down_for_height(h, g_down)
    total = t_up + t_down

    def height(t):
        tt = t % total
        if tt <= t_up:
            return v_up * tt - 0.5 * g_up * tt**2
        td = tt - t_up
        return h - 0.5 * g_down * td**2

    return Profile(
        key="mario",
        title="슈퍼 마리오브라더스",
        subtitle="상승 중력은 약하게, 하강 중력은 강하게 — 체공감 + 경쾌한 착지",
        height=height,
        total=total,
        caption=f"상승 {t_up:.2f}s / 하강 {t_down:.2f}s — 버튼을 오래 누를수록 높이 조절도 쉬움",
    )


# ---------------------------------------------------------------------------
# 2. Metroid: weak gravity both ways -> long floaty hang time
# ---------------------------------------------------------------------------

def metroid(g=2.2, h=3.0):
    v0 = _v0_for_height(g, h)
    t_up = _t_up(v0, g)
    total = 2 * t_up

    def height(t):
        tt = t % total
        return v0 * tt - 0.5 * g * tt**2

    return Profile(
        key="metroid",
        title="메트로이드",
        subtitle="상승·하강 모두 약한 중력 — 총알을 쏠 높이를 여유롭게 조절",
        height=height,
        total=total,
        caption=f"체공 시간 {total:.2f}s — 마리오보다 훨씬 길게 둥실둥실",
    )


# ---------------------------------------------------------------------------
# 3. Ghosts'n Goblins: low jump, trajectory locked at takeoff (no air control)
# ---------------------------------------------------------------------------

def ghosts_n_goblins(g=8.0, h=1.2, vx=1.6):
    v0 = _v0_for_height(g, h)
    t_up = _t_up(v0, g)
    total = 2 * t_up

    def height(t):
        tt = t % total
        return v0 * tt - 0.5 * g * tt**2

    def xpos(t):
        tt = t % total
        return vx * tt

    return Profile(
        key="ghosts_n_goblins",
        title="마계촌",
        subtitle="낮은 점프 + 공중에서 좌우 조작 완전 불가",
        height=height,
        total=total,
        x=xpos,
        caption="점프하는 순간 착지 지점이 이미 결정됨 — 신중한 점프, 히트&런 플레이 유도",
    )


# ---------------------------------------------------------------------------
# 4. Street Fighter II: same spatial path, different time-remapping
# ---------------------------------------------------------------------------

def sf2_shape(s, h=3.0):
    return 4 * h * s * (1 - s)


def sf2_vanilla_reparam(t, total):
    return t / total


def sf2_turbo_reparam(t, total, rise_frac=0.68):
    rise_t = total * rise_frac
    fall_t = total * (1 - rise_frac)
    if t <= rise_t:
        return 0.5 * (t / rise_t)
    td = t - rise_t
    return 0.5 + 0.5 * (td / fall_t)


def sf2_screw_piledriver(total=1.8, h=3.0):
    def height_vanilla(t):
        tt = t % total
        return sf2_shape(sf2_vanilla_reparam(tt, total), h)

    def height_turbo(t):
        tt = t % total
        return sf2_shape(sf2_turbo_reparam(tt, total), h)

    return (
        Profile(
            key="sf2_vanilla",
            title="스트리트 파이터 II",
            subtitle="(오리지널) 스크류 파일드라이버 — 등속으로 경로를 그림",
            height=height_vanilla,
            total=total,
            caption="이동 경로(궤적)는 동일 — 속도만 균등하게 배분",
        ),
        Profile(
            key="sf2_turbo",
            title="스트리트 파이터 II 터보 이후",
            subtitle="같은 경로, 하강만 훨씬 빠르게 — 내리꽂는 타격감",
            height=height_turbo,
            total=total,
            caption="궤적은 완전히 동일 — 속도 배분만 바꿔서 손맛이 달라짐",
        ),
    )


# ---------------------------------------------------------------------------
# 5. Smash Bros: jump squat delay + Ultimate's initial pop-then-normal gravity
# ---------------------------------------------------------------------------

def smash_jump_squat(squat=0.12, g=7.0, h=2.6):
    v0 = _v0_for_height(g, h)
    t_up = _t_up(v0, g)
    flight = 2 * t_up
    total = squat + flight

    def height(t):
        tt = t % total
        if tt < squat:
            return 0.0
        td = tt - squat
        return v0 * td - 0.5 * g * td**2

    return Profile(
        key="smash_squat",
        title="대난투 스매시브라더스",
        subtitle="점프 직전 짧은 준비 동작(점프 스쿼트)",
        height=height,
        total=total,
        caption=f"준비 동작 {squat*1000:.0f}ms — 0으로 만들면 위 스매시 입력과 점프가 오조작됨",
    )


def smash_ultimate_special(v0_pop=9.0, g_pop=26.0, t_pop=0.11, g_normal=7.0):
    v1 = v0_pop - g_pop * t_pop
    y1 = v0_pop * t_pop - 0.5 * g_pop * t_pop**2
    td_land = (v1 + np.sqrt(v1**2 + 2 * g_normal * y1)) / g_normal
    total = t_pop + td_land

    def height(t):
        tt = t % total
        if tt <= t_pop:
            return v0_pop * tt - 0.5 * g_pop * tt**2
        td = tt - t_pop
        return y1 + v1 * td - 0.5 * g_normal * td**2

    return Profile(
        key="smash_ultimate",
        title="대난투 스매시브라더스 얼티밋",
        subtitle="아주 강하게 '휙' 띄운 뒤 급감속, 이후 보통 중력으로 전환",
        height=height,
        total=total,
        caption="반응이 살짝 늦어도 조작이 자연스럽게 받아들여지도록 하는 숨은 설계",
    )


# ---------------------------------------------------------------------------
# 6. Modern: Jump King — charge-based, fully committed once launched
# ---------------------------------------------------------------------------

def jump_king(charges=(2.6, 4.2, 6.0), g=7.0, charge_time=0.55, landing_pause=0.35):
    segments = []
    labels = ["약하게", "중간", "강하게"]
    cursor = 0.0
    for v0, label in zip(charges, labels):
        t_up = _t_up(v0, g)
        flight = 2 * t_up
        segments.append((cursor, charge_time, flight, v0, label))
        cursor += charge_time + flight + landing_pause
    total = cursor

    def height(t):
        tt = t % total
        for start, ct, ft, v0, _ in segments:
            if start <= tt < start + ct + ft:
                if tt < start + ct:
                    return 0.0
                td = tt - (start + ct)
                return v0 * td - 0.5 * g * td**2
        return 0.0

    def charge_state(t):
        """Returns (is_charging, label) for the HUD text."""
        tt = t % total
        for start, ct, ft, v0, label in segments:
            if start <= tt < start + ct:
                return True, label
            if start + ct <= tt < start + ct + ft:
                return False, label
        return False, ""

    profile = Profile(
        key="jump_king",
        title="현대 게임 — 점프킹 (Jump King)",
        subtitle="누르는 시간만큼 충전, 놓으면 그대로 발사 — 공중 조작 없음",
        height=height,
        total=total,
        caption="한 번 발사되면 취소·조정 불가 — 파워를 예측하는 것 자체가 게임성",
    )
    return profile, charge_state


# ---------------------------------------------------------------------------
# 7. Modern: Celeste — variable jump height via hold duration + "jump cut"
# ---------------------------------------------------------------------------

def celeste_variable_jump(hold_time, v0=4.24, g_rise=3.0, g_cut=20.0, g_fall=8.0):
    t_natural_apex = v0 / g_rise
    if hold_time >= t_natural_apex:
        # held through the whole natural rise: no cut needed
        y_release = v0 * t_natural_apex - 0.5 * g_rise * t_natural_apex**2
        v_release = 0.0
        t_release = t_natural_apex
        peak = y_release
        t_cut_end = t_release
    else:
        t_release = hold_time
        y_release = v0 * t_release - 0.5 * g_rise * t_release**2
        v_release = v0 - g_rise * t_release
        t_cut = v_release / g_cut
        peak = y_release + v_release * t_cut - 0.5 * g_cut * t_cut**2
        t_cut_end = t_release + t_cut

    t_fall = _t_down_for_height(peak, g_fall)
    total = t_cut_end + t_fall

    def height(t):
        tt = t % total
        if tt <= t_release:
            return v0 * tt - 0.5 * g_rise * tt**2
        if tt <= t_cut_end:
            td = tt - t_release
            return y_release + v_release * td - 0.5 * g_cut * td**2
        td = tt - t_cut_end
        return peak - 0.5 * g_fall * td**2

    return height, total, peak


def celeste_pair():
    tall_h, tall_total, tall_peak = celeste_variable_jump(hold_time=1.5)
    short_h, short_total, short_peak = celeste_variable_jump(hold_time=0.32)
    return (
        Profile(
            key="celeste_full",
            title="현대 게임 — 셀레스트 (길게 눌렀을 때)",
            subtitle="버튼을 계속 누르고 있으면 최대 높이까지",
            height=tall_h,
            total=tall_total,
            caption=f"최고 높이 {tall_peak:.2f} — 정밀한 플랫포밍을 위한 느린 상승",
        ),
        Profile(
            key="celeste_cut",
            title="현대 게임 — 셀레스트 (짧게 눌렀을 때)",
            subtitle="일찍 떼면 강한 '컷' 중력이 걸려 점프가 짧아짐",
            height=short_h,
            total=short_total,
            caption=f"최고 높이 {short_peak:.2f} — 같은 캐릭터, 입력 길이로 높이를 직접 조절",
        ),
    )


# ---------------------------------------------------------------------------
# 8. Modern: Mega Man X — dash jump carries dash speed into the same arc
# ---------------------------------------------------------------------------

def megaman_x_dash_jump(g=7.0, h=2.6, vx_walk=1.3, vx_dash=4.2):
    v0 = _v0_for_height(g, h)
    t_up = _t_up(v0, g)
    total = 2 * t_up

    def height(t):
        tt = t % total
        return v0 * tt - 0.5 * g * tt**2

    def x_walk(t):
        return vx_walk * (t % total)

    def x_dash(t):
        return vx_dash * (t % total)

    return (
        Profile(
            key="megaman_walk",
            title="현대 게임 — 록맨 X (걷기 점프)",
            subtitle="걷다가 그냥 점프 — 이동 거리가 짧음",
            height=height,
            total=total,
            x=x_walk,
            caption=f"같은 체공 시간, 착지 거리 {vx_walk*total:.1f}",
        ),
        Profile(
            key="megaman_dash",
            title="현대 게임 — 록맨 X (대시 점프)",
            subtitle="대시 속도를 그대로 이어받아 점프 — 높이는 같고 거리만 훨씬 멀리",
            height=height,
            total=total,
            x=x_dash,
            caption=f"같은 체공 시간, 착지 거리 {vx_dash*total:.1f} — 이동 효율이 크게 늘어남",
        ),
    )
