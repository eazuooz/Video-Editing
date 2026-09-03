import {Node, Rect, Txt, Video} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';

const FONT = 'Malgun Gothic';
const MONO = 'Consolas';
const FADE = 0.35;

export type ExampleTag = {
  text: string;
  x: number;
  color: string;
};

export type SceneExample = {
  clip: string;
  label: string;
  concept: string;
  source: string;
  duration: number;
  tags?: ExampleTag[];
};

export const EXAMPLES: readonly SceneExample[] = [
  {
    clip: 'scene01',
    label: 'SUPER MARIO BROS.',
    concept: '연속된 움직임을 정지 화면으로 분해',
    source: 'Gameplay Project · YouTube (CC BY)',
    duration: 6.5,
  },
  {
    clip: 'scene02',
    label: 'STREET FIGHTER 6',
    concept: '1초 동안 60번 그리는 빠른 전투 장면',
    source: 'Street Fighter 공식 채널 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene03',
    label: 'STREET FIGHTER II',
    concept: '프레임 단위로 설계된 공격·판정 타이밍',
    source: 'Sporefrog08 · YouTube · 교육 목적 짧은 인용',
    duration: 6.5,
  },
  {
    clip: 'scene04',
    label: 'FORZA HORIZON 5 · SAME SOURCE',
    concept: '같은 시간·같은 이동, 다른 표본 수',
    source: 'Xbox 공식 게임플레이 · YouTube',
    duration: 6.5,
    tags: [
      {text: '30 FPS', x: -480, color: '#fb923c'},
      {text: '60 FPS', x: 480, color: '#38bdf8'},
    ],
  },
  {
    clip: 'scene05',
    label: 'RATCHET & CLANK: RIFT APART',
    concept: '프레임 예산과 복잡한 렌더링 비용',
    source: 'PlayStation 공식 게임플레이 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene06',
    label: 'OVERWATCH 2 · FPS COUNTER',
    concept: '전투 복잡도에 따라 계속 변하는 FPS',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene07',
    label: 'CELESTE',
    concept: '프레임률과 분리해야 하는 게임의 시간',
    source: 'UltraPita · YouTube (CC BY)',
    duration: 6.5,
  },
  {
    clip: 'scene08',
    label: 'OVERWATCH · 60 / 144 / 360',
    concept: 'FPS와 모니터 주사율이 체감에 미치는 영향',
    source: 'NVIDIA GeForce 공식 비교 영상 · YouTube',
    duration: 6.5,
    tags: [
      {text: '60', x: -520, color: '#fb923c'},
      {text: '144', x: 0, color: '#a78bfa'},
      {text: '360', x: 520, color: '#38bdf8'},
    ],
  },
  {
    clip: 'scene09',
    label: 'SONIC THE HEDGEHOG · PAL / NTSC',
    concept: '50Hz PAL과 60Hz NTSC의 실제 속도 차이',
    source: 'redhotsonic · YouTube · 교육 목적 짧은 인용',
    duration: 6.5,
    tags: [
      {text: 'PAL · 50Hz', x: -480, color: '#fb923c'},
      {text: 'NTSC · 60Hz', x: 480, color: '#38bdf8'},
    ],
  },
  {
    clip: 'scene10',
    label: 'HORIZON FORBIDDEN WEST · PS5',
    concept: '그래픽 품질과 목표 프레임 레이트의 선택',
    source: 'PlayStation 공식 게임플레이 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene11',
    label: 'ALAN WAKE 2 · FULL RAY TRACING',
    concept: '조명·그림자·패스 트레이싱의 프레임 비용',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene12',
    label: 'BLACK MYTH: WUKONG · RTX 50',
    concept: '고성능 GPU와 AI 렌더링의 실제 사례',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene13',
    label: 'MINECRAFT WITH RTX',
    concept: '고해상도와 레이 트레이싱의 픽셀 계산량',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene14',
    label: 'HORIZON FORBIDDEN WEST · DLSS',
    concept: '낮은 내부 해상도에서 높은 출력 해상도로',
    source: 'NVIDIA GeForce 공식 DLSS 설명 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene15',
    label: 'CYBERPUNK 2077 · FRAME GENERATION',
    concept: '직접 렌더 프레임 사이에 생성 프레임 추가',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene16',
    label: 'STAR WARS OUTLAWS · DLSS 4',
    concept: '직접 렌더 프레임 사이의 여러 생성 프레임',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene17',
    label: 'BLACK MYTH: WUKONG · PERFORMANCE',
    concept: '렌더 FPS와 화면 표시 FPS를 따로 보기',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene18',
    label: 'COUNTER-STRIKE 2 · NVIDIA REFLEX',
    concept: 'FPS 수치와 입력 지연은 같은 지표가 아님',
    source: 'NVIDIA GeForce 공식 영상 · YouTube',
    duration: 6.5,
  },
  {
    clip: 'scene19',
    label: 'STREET FIGHTER II ↔ ALAN WAKE 2',
    concept: '프레임 결합형 로직에서 다단계 파이프라인으로',
    source: '교육 목적 짧은 인용 · NVIDIA 공식 영상',
    duration: 6.5,
    tags: [
      {text: 'OLD / FRAME-LINKED', x: -480, color: '#fb923c'},
      {text: 'MODERN / MULTI-STAGE', x: 480, color: '#c084fc'},
    ],
  },
  {
    clip: 'scene20',
    label: 'CONCEPT REVIEW MONTAGE',
    concept: '정의 → 시간 → 렌더링 → 표시 흐름 복습',
    source: '각 장면 출처는 프로젝트 SOURCES.md 참조',
    duration: 6.5,
  },
] as const;

const CLIPS = import.meta.glob('../assets/gameplay/*.{mp4,webm,mov}', {
  eager: true,
  query: '?url',
  import: 'default',
}) as Record<string, string>;

function findClip(name: string): string {
  const match = Object.entries(CLIPS).find(([path]) => {
    const file = path.split('/').pop() ?? '';
    return file.replace(/\.[^.]+$/, '') === name;
  });
  if (!match) throw new Error(`Missing frame-rate example clip: ${name}`);
  return match[1];
}

export function* playExample(view: any, index: number) {
  const example = EXAMPLES[index];
  const stage = createRef<Node>();

  view.add(
    <Node ref={stage} opacity={0}>
      <Rect width={1920} height={1080} fill={'#05070d'} />
      <Video src={findClip(example.clip)} width={1920} height={1080} play />

      <Rect y={-475} width={1920} height={130} fill={'#05070ddd'}>
        <Rect x={-690} width={330} height={72} radius={18} fill={'#fbbf2422'} stroke={'#fbbf24'} lineWidth={3}>
          <Txt text="1  실제 게임 예시" fontFamily={FONT} fontSize={30} fontWeight={800} fill={'#f8fafc'} />
        </Rect>
        <Txt text="→" x={-455} fontFamily={MONO} fontSize={42} fill={'#8da0b8'} />
        <Rect x={-205} width={390} height={72} radius={18} fill={'#38bdf811'} stroke={'#475569'} lineWidth={3}>
          <Txt text="2  채널 모션그래픽" fontFamily={FONT} fontSize={30} fontWeight={700} fill={'#94a3b8'} />
        </Rect>
        <Txt
          text={`${String(index + 1).padStart(2, '0')} / 20`}
          x={820}
          fontFamily={MONO}
          fontSize={28}
          fontWeight={800}
          fill={'#38bdf8'}
        />
      </Rect>

      {example.tags?.map(tag => (
        <Rect key={tag.text} x={tag.x} y={-300} width={390} height={84} radius={18} fill={'#05070ddd'} stroke={tag.color} lineWidth={4}>
          <Txt text={tag.text} fontFamily={MONO} fontSize={34} fontWeight={900} fill={tag.color} />
        </Rect>
      ))}

      <Rect x={-490} y={420} width={860} height={210} radius={28} fill={'#05070de8'} stroke={'#334155'} lineWidth={3}>
        <Txt text={example.label} x={-385} y={-58} offsetX={-1} fontFamily={MONO} fontSize={31} fontWeight={900} fill={'#f8fafc'} />
        <Txt text={example.concept} x={-385} y={0} offsetX={-1} fontFamily={FONT} fontSize={31} fontWeight={700} fill={'#fbbf24'} />
        <Txt text={`출처  ${example.source}`} x={-385} y={58} offsetX={-1} fontFamily={FONT} fontSize={22} fill={'#94a3b8'} />
      </Rect>
    </Node>,
  );

  yield* stage().opacity(1, FADE);
  yield* waitFor(Math.max(0, example.duration - FADE * 2));
  yield* stage().opacity(0, FADE);
  stage().remove();
}
