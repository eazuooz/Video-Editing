// Port of examples/jump-physics-showcase/profiles.py — same closed-form
// piecewise height(t)/x(t) curves, sampled continuously by the renderer.

export type Profile = {
  key: string;
  title: string;
  subtitle: string;
  height: (t: number) => number;
  total: number;
  x: (t: number) => number;
  caption: string;
  velocity?: (t: number) => number;
};

const DEFAULT_VX = 1.6;

function v0ForHeight(g: number, h: number) {
  return Math.sqrt(2 * g * h);
}

function tUp(v0: number, g: number) {
  return v0 / g;
}

function tDownForHeight(h: number, g: number) {
  return Math.sqrt((2 * h) / g);
}

export function basicConcept(g = 6.0, v0 = 5.0): Profile {
  const total = 2 * tUp(v0, g);
  const height = (t: number) => {
    const tt = t % total;
    return v0 * tt - 0.5 * g * tt ** 2;
  };
  const velocity = (t: number) => {
    const tt = t % total;
    return v0 - g * tt;
  };
  return {
    key: 'basic',
    title: '점프의 기본 원리',
    subtitle: '공중에 있는 동안 매 프레임 일정한 중력을 속도에 더한다',
    height,
    total,
    x: t => DEFAULT_VX * (t % total),
    velocity,
    caption: '위로 속도 5 → 매 프레임 -1 → 5,4,3,2,1,0,-1,-2 ... 로 자연스럽게 낙하 전환',
  };
}

export function mario(gUp = 4.0, gDown = 11.0, h = 3.0): Profile {
  const vUp = v0ForHeight(gUp, h);
  const tRise = tUp(vUp, gUp);
  const tFall = tDownForHeight(h, gDown);
  const total = tRise + tFall;
  const height = (t: number) => {
    const tt = t % total;
    if (tt <= tRise) return vUp * tt - 0.5 * gUp * tt ** 2;
    const td = tt - tRise;
    return h - 0.5 * gDown * td ** 2;
  };
  return {
    key: 'mario',
    title: '슈퍼 마리오브라더스',
    subtitle: '상승 중력은 약하게, 하강 중력은 강하게 — 체공감 + 경쾌한 착지',
    height,
    total,
    x: t => DEFAULT_VX * (t % total),
    caption: `상승 ${tRise.toFixed(2)}s / 하강 ${tFall.toFixed(2)}s — 버튼을 오래 누를수록 높이 조절도 쉬움`,
  };
}

export function metroid(g = 2.2, h = 3.0): Profile {
  const v0 = v0ForHeight(g, h);
  const total = 2 * tUp(v0, g);
  const height = (t: number) => {
    const tt = t % total;
    return v0 * tt - 0.5 * g * tt ** 2;
  };
  return {
    key: 'metroid',
    title: '메트로이드',
    subtitle: '상승·하강 모두 약한 중력 — 총알을 쏠 높이를 여유롭게 조절',
    height,
    total,
    x: t => DEFAULT_VX * (t % total),
    caption: `체공 시간 ${total.toFixed(2)}s — 마리오보다 훨씬 길게 둥실둥실`,
  };
}

export function ghostsNGoblins(g = 8.0, h = 1.2, vx = 1.6): Profile {
  const v0 = v0ForHeight(g, h);
  const total = 2 * tUp(v0, g);
  const height = (t: number) => {
    const tt = t % total;
    return v0 * tt - 0.5 * g * tt ** 2;
  };
  return {
    key: 'ghosts_n_goblins',
    title: '마계촌',
    subtitle: '낮은 점프 + 공중에서 좌우 조작 완전 불가',
    height,
    total,
    x: t => vx * (t % total),
    caption: '점프하는 순간 착지 지점이 이미 결정됨 — 신중한 점프, 히트&런 플레이 유도',
  };
}

function sf2Shape(s: number, h: number) {
  return 4 * h * s * (1 - s);
}

function sf2VanillaReparam(t: number, total: number) {
  return t / total;
}

function sf2TurboReparam(t: number, total: number, riseFrac = 0.68) {
  const riseT = total * riseFrac;
  const fallT = total * (1 - riseFrac);
  if (t <= riseT) return 0.5 * (t / riseT);
  const td = t - riseT;
  return 0.5 + 0.5 * (td / fallT);
}

export function sf2ScrewPiledriver(total = 1.8, h = 3.0): [Profile, Profile] {
  const heightVanilla = (t: number) => {
    const tt = t % total;
    return sf2Shape(sf2VanillaReparam(tt, total), h);
  };
  const heightTurbo = (t: number) => {
    const tt = t % total;
    return sf2Shape(sf2TurboReparam(tt, total), h);
  };
  return [
    {
      key: 'sf2_vanilla',
      title: '스트리트 파이터 II',
      subtitle: '(오리지널) 스크류 파일드라이버 — 등속으로 경로를 그림',
      height: heightVanilla,
      total,
      x: () => 0,
      caption: '이동 경로(궤적)는 동일 — 속도만 균등하게 배분',
    },
    {
      key: 'sf2_turbo',
      title: '스트리트 파이터 II 터보 이후',
      subtitle: '같은 경로, 하강만 훨씬 빠르게 — 내리꽂는 타격감',
      height: heightTurbo,
      total,
      x: () => 0,
      caption: '궤적은 완전히 동일 — 속도 배분만 바꿔서 손맛이 달라짐',
    },
  ];
}

export function smashJumpSquat(squat = 0.12, g = 7.0, h = 2.6): Profile {
  const v0 = v0ForHeight(g, h);
  const flight = 2 * tUp(v0, g);
  const total = squat + flight;
  const height = (t: number) => {
    const tt = t % total;
    if (tt < squat) return 0.0;
    const td = tt - squat;
    return v0 * td - 0.5 * g * td ** 2;
  };
  return {
    key: 'smash_squat',
    title: '대난투 스매시브라더스',
    subtitle: '점프 직전 짧은 준비 동작(점프 스쿼트)',
    height,
    total,
    x: t => {
      const tt = t % total;
      return tt < squat ? 0 : DEFAULT_VX * (tt - squat);
    },
    caption: `준비 동작 ${(squat * 1000).toFixed(0)}ms — 0으로 만들면 위 스매시 입력과 점프가 오조작됨`,
  };
}

export function smashUltimateSpecial(v0Pop = 9.0, gPop = 26.0, tPop = 0.11, gNormal = 7.0): Profile {
  const v1 = v0Pop - gPop * tPop;
  const y1 = v0Pop * tPop - 0.5 * gPop * tPop ** 2;
  const tdLand = (v1 + Math.sqrt(v1 ** 2 + 2 * gNormal * y1)) / gNormal;
  const total = tPop + tdLand;
  const height = (t: number) => {
    const tt = t % total;
    if (tt <= tPop) return v0Pop * tt - 0.5 * gPop * tt ** 2;
    const td = tt - tPop;
    return y1 + v1 * td - 0.5 * gNormal * td ** 2;
  };
  return {
    key: 'smash_ultimate',
    title: '대난투 스매시브라더스 얼티밋',
    subtitle: "아주 강하게 '휙' 띄운 뒤 급감속, 이후 보통 중력으로 전환",
    height,
    total,
    x: t => DEFAULT_VX * (t % total),
    caption: '반응이 살짝 늦어도 조작이 자연스럽게 받아들여지도록 하는 숨은 설계',
  };
}

export type ChargeState = {charging: boolean; label: string};

export function jumpKing(
  charges: [number, number, number] = [2.6, 4.2, 6.0],
  g = 7.0,
  chargeTime = 0.55,
  landingPause = 0.35,
): {profile: Profile; chargeState: (t: number) => ChargeState} {
  const labels = ['약하게', '중간', '강하게'];
  const segments: Array<{start: number; ct: number; ft: number; v0: number; label: string}> = [];
  let cursor = 0;
  charges.forEach((v0, i) => {
    const flight = 2 * tUp(v0, g);
    segments.push({start: cursor, ct: chargeTime, ft: flight, v0, label: labels[i]});
    cursor += chargeTime + flight + landingPause;
  });
  const total = cursor;

  const height = (t: number) => {
    const tt = t % total;
    for (const {start, ct, ft, v0} of segments) {
      if (tt >= start && tt < start + ct + ft) {
        if (tt < start + ct) return 0;
        const td = tt - (start + ct);
        return v0 * td - 0.5 * g * td ** 2;
      }
    }
    return 0;
  };

  const chargeState = (t: number): ChargeState => {
    const tt = t % total;
    for (const {start, ct, ft, label} of segments) {
      if (tt >= start && tt < start + ct) return {charging: true, label};
      if (tt >= start + ct && tt < start + ct + ft) return {charging: false, label};
    }
    return {charging: false, label: ''};
  };

  const x = (t: number) => {
    const tt = t % total;
    for (const {start, ct, ft} of segments) {
      if (tt >= start && tt < start + ct + ft) {
        return tt < start + ct ? 0 : DEFAULT_VX * (tt - (start + ct));
      }
    }
    return 0;
  };

  const profile: Profile = {
    key: 'jump_king',
    title: '현대 게임 — 점프킹 (Jump King)',
    subtitle: '누르는 시간만큼 충전, 놓으면 그대로 발사 — 공중 조작 없음',
    height,
    total,
    x,
    caption: '한 번 발사되면 취소·조정 불가 — 파워를 예측하는 것 자체가 게임성',
  };
  return {profile, chargeState};
}

function celesteVariableJump(holdTime: number, v0 = 4.24, gRise = 3.0, gCut = 20.0, gFall = 8.0) {
  const tNaturalApex = v0 / gRise;
  let tRelease: number;
  let yRelease: number;
  let vRelease: number;
  let peak: number;
  let tCutEnd: number;

  if (holdTime >= tNaturalApex) {
    yRelease = v0 * tNaturalApex - 0.5 * gRise * tNaturalApex ** 2;
    vRelease = 0;
    tRelease = tNaturalApex;
    peak = yRelease;
    tCutEnd = tRelease;
  } else {
    tRelease = holdTime;
    yRelease = v0 * tRelease - 0.5 * gRise * tRelease ** 2;
    vRelease = v0 - gRise * tRelease;
    const tCut = vRelease / gCut;
    peak = yRelease + vRelease * tCut - 0.5 * gCut * tCut ** 2;
    tCutEnd = tRelease + tCut;
  }

  const tFall = tDownForHeight(peak, gFall);
  const total = tCutEnd + tFall;

  const height = (t: number) => {
    const tt = t % total;
    if (tt <= tRelease) return v0 * tt - 0.5 * gRise * tt ** 2;
    if (tt <= tCutEnd) {
      const td = tt - tRelease;
      return yRelease + vRelease * td - 0.5 * gCut * td ** 2;
    }
    const td = tt - tCutEnd;
    return peak - 0.5 * gFall * td ** 2;
  };

  return {height, x: (t: number) => DEFAULT_VX * (t % total), total, peak};
}

export function celestePair(): [Profile, Profile] {
  const tall = celesteVariableJump(1.5);
  const short = celesteVariableJump(0.32);
  return [
    {
      key: 'celeste_full',
      title: '현대 게임 — 셀레스트 (길게 눌렀을 때)',
      subtitle: '버튼을 계속 누르고 있으면 최대 높이까지',
      height: tall.height,
      total: tall.total,
      x: tall.x,
      caption: `최고 높이 ${tall.peak.toFixed(2)} — 정밀한 플랫포밍을 위한 느린 상승`,
    },
    {
      key: 'celeste_cut',
      title: '현대 게임 — 셀레스트 (짧게 눌렀을 때)',
      subtitle: "일찍 떼면 강한 '컷' 중력이 걸려 점프가 짧아짐",
      height: short.height,
      total: short.total,
      x: short.x,
      caption: `최고 높이 ${short.peak.toFixed(2)} — 같은 캐릭터, 입력 길이로 높이를 직접 조절`,
    },
  ];
}

export function megamanXDashJump(g = 7.0, h = 2.6, vxWalk = 1.3, vxDash = 4.2): [Profile, Profile] {
  const v0 = v0ForHeight(g, h);
  const total = 2 * tUp(v0, g);
  const height = (t: number) => {
    const tt = t % total;
    return v0 * tt - 0.5 * g * tt ** 2;
  };
  return [
    {
      key: 'megaman_walk',
      title: '현대 게임 — 록맨 X (걷기 점프)',
      subtitle: '걷다가 그냥 점프 — 이동 거리가 짧음',
      height,
      total,
      x: t => vxWalk * (t % total),
      caption: `같은 체공 시간, 착지 거리 ${(vxWalk * total).toFixed(1)}`,
    },
    {
      key: 'megaman_dash',
      title: '현대 게임 — 록맨 X (대시 점프)',
      subtitle: '대시 속도를 그대로 이어받아 점프 — 높이는 같고 거리만 훨씬 멀리',
      height,
      total,
      x: t => vxDash * (t % total),
      caption: `같은 체공 시간, 착지 거리 ${(vxDash * total).toFixed(1)} — 이동 효율이 크게 늘어남`,
    },
  ];
}
