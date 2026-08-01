// Where real gameplay footage goes in the narrated cut.
//
// Each entry reserves a window inside one narration segment. During that window
// the physics graph steps aside and the gameplay clip takes the stage; if the
// clip file is not there yet, a labelled placeholder of the exact same geometry
// shows instead, so adding footage later never shifts the layout.
//
// To fill a slot, drop a video at src/assets/gameplay/<clip>.mp4 -- it is picked
// up automatically (see scenes/jumpPhysics/broll.tsx), no code change needed.
//
// `offset` is measured from the START OF THE SCENE, which is also the start of
// the narration segment, so the absolute timecode in the audio is simply
// SEGMENTS[segment].start + offset. `npm run check:narration` verifies every
// window still fits inside its scene.

// Explicit .ts extension: this module is also loaded by
// scripts/check-narration-sync.ts under Node's type stripping, whose resolver
// does not infer extensions.
import {SEGMENTS} from './narration.ts';

export type BrollWindow = {
  /** Narration segment this clip plays inside. */
  segment: keyof typeof SEGMENTS;
  /** Basename of the file under src/assets/gameplay/ (without extension). */
  clip: string;
  /** Seconds from the start of the segment to when the clip appears. */
  offset: number;
  /** How long the clip stays on screen, including its fades. */
  duration: number;
  /** Shown on the placeholder, and as the on-screen source caption. */
  label: string;
  /** What footage to capture — shown on the placeholder only. */
  hint: string;
};

export const BROLL: BrollWindow[] = [
  {
    segment: 'intro',
    clip: 'intro-montage',
    offset: 9.0,
    duration: 13.0,
    label: '여러 게임의 점프 비교',
    hint: '서로 다른 게임 2~3개의 점프를 빠르게 이어붙인 몽타주',
  },
  {
    segment: 'axes',
    clip: 'axes-horizontal',
    offset: 6.0,
    duration: 8.0,
    label: '가로 이동 비교 플레이',
    hint: '같은 점프에서 가로 속도만 다른 두 플레이를 나란히',
  },
  {
    segment: 'mario',
    clip: 'mario',
    offset: 7.0,
    duration: 9.0,
    label: '슈퍼 마리오브라더스',
    hint: '느린 상승과 빠른 하강이 드러나는 점프. 버튼 길이에 따른 높이 차이도',
  },
  {
    segment: 'metroid',
    clip: 'metroid',
    offset: 6.0,
    duration: 8.0,
    label: '메트로이드',
    hint: '둥실둥실한 체공과 공중에서 높이를 조절해 쏘는 장면',
  },
  {
    segment: 'ghosts',
    clip: 'ghosts',
    offset: 7.0,
    duration: 9.0,
    label: '마계촌',
    hint: '점프 직후 착지 지점이 이미 정해진 장면. 실패/성공 한 번씩',
  },
  {
    segment: 'sf2',
    clip: 'sf2',
    offset: 7.0,
    duration: 9.0,
    label: '스트리트 파이터 II — 장기에프',
    hint: '스크류 파일드라이버의 상승/하강 속도 차. 슬로 모션 권장',
  },
  {
    segment: 'smashSquat',
    clip: 'smash-squat',
    offset: 8.0,
    duration: 9.0,
    label: '스매시브라더스 — 점프 스쿼트',
    hint: '점프 직전 준비 프레임을 프레임 스텝으로. 위 스매시 입력과 대비',
  },
  {
    segment: 'smashUltimate',
    clip: 'smash-ultimate',
    offset: 9.0,
    duration: 10.0,
    label: '스매시브라더스 얼티밋',
    hint: '초반에 확 뜨고 곧바로 감속하는 점프를 실제 플레이로',
  },
  {
    segment: 'jumpKing',
    clip: 'jump-king',
    offset: 8.0,
    duration: 10.0,
    label: '점프킹',
    hint: '차지 게이지가 차오르다 발사되는 순간, 공중에서 전혀 수정 못 하는 장면',
  },
  {
    // Scene runs two demos back to back (long-hold, then early-release) --
    // see scenes/narrated/celeste.tsx. This window is attached to the first
    // one, which typically gets ~19s of a ~28s segment; keep offset+duration
    // comfortably under that (celeste.tsx also clamps the split as a
    // safety net if the narration timing ever shifts).
    segment: 'celeste',
    clip: 'celeste',
    offset: 7.0,
    duration: 9.0,
    label: '셀레스트',
    hint: '오래 눌러 최대 높이까지 가는 점프와, 일찍 떼서 짧아지는 점프를 나란히',
  },
  {
    segment: 'megaman',
    clip: 'megaman-x',
    offset: 8.0,
    duration: 9.0,
    label: '록맨 X — 대시 점프',
    hint: '걷기 점프와 대시 점프의 이동 거리 차이가 드러나는 장면',
  },
  {
    segment: 'outro',
    clip: 'outro-prototype',
    offset: 8.0,
    duration: 10.0,
    label: '직접 만든 프로토타입',
    hint: '파라미터 슬라이더를 바꿔가며 점프 감각이 달라지는 화면',
  },
];

/** The window reserved inside a given segment, if any. */
export function brollFor(segment: keyof typeof SEGMENTS): BrollWindow | undefined {
  return BROLL.find(window => window.segment === segment);
}

/** Absolute start time of a window within the narration audio, in seconds. */
export function absoluteStart(window: BrollWindow): number {
  return SEGMENTS[window.segment].start + window.offset;
}

/** Absolute end time of a window within the narration audio, in seconds. */
export function absoluteEnd(window: BrollWindow): number {
  return absoluteStart(window) + window.duration;
}

/** Format seconds as `m:ss.mmm` for cue sheets and on-screen slates. */
export function timecode(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds - minutes * 60;
  return `${minutes}:${rest.toFixed(3).padStart(6, '0')}`;
}
