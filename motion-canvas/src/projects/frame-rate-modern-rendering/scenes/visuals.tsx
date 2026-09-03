import {Circle, Img, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, createSignal, linear} from '@motion-canvas/core';
import megamanSprite from '../../../assets/jump-physics/megaman.png';
import {SCENE_DURATIONS, SCENE_TITLES} from '../timing';
import {EXAMPLES, playExample} from './broll';

const FONT = 'Malgun Gothic';
const MONO = 'Consolas';

const C = {
  bg: '#070b14',
  panel: '#111827',
  panel2: '#182235',
  line: '#334155',
  text: '#dbe7f5',
  muted: '#8da0b8',
  white: '#f8fafc',
  blue: '#38bdf8',
  blue2: '#2563eb',
  cyan: '#22d3ee',
  green: '#34d399',
  yellow: '#fbbf24',
  orange: '#fb923c',
  red: '#f87171',
  purple: '#c084fc',
  purple2: '#7c3aed',
} as const;

type Progress = ReturnType<typeof createSignal<number>>;

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
const phase = (value: number, start: number, end: number) =>
  clamp01((value - start) / Math.max(0.0001, end - start));
const smooth = (value: number) => {
  const t = clamp01(value);
  return t * t * (3 - 2 * t);
};
const cycle = (value: number) => ((value % 1) + 1) % 1;

function avatar(props: {x: any; y: any; color?: string; scale?: number; opacity?: any}) {
  const color = props.color ?? C.blue;
  return (
    <Node x={props.x} y={props.y} scale={props.scale ?? 1} opacity={props.opacity ?? 1}>
      <Circle width={178} height={178} fill={`${color}28`} stroke={color} lineWidth={5} />
      <Circle width={126} height={24} y={98} fill={'#00000066'} />
      <Img src={megamanSprite} width={170} y={-2} />
    </Node>
  );
}

function chip(props: {
  text: string;
  x?: any;
  y?: any;
  width?: number;
  color?: string;
  opacity?: any;
  fontSize?: number;
}) {
  const color = props.color ?? C.blue;
  return (
    <Rect
      x={props.x ?? 0}
      y={props.y ?? 0}
      width={props.width ?? 190}
      height={96}
      radius={18}
      fill={`${color}22`}
      stroke={color}
      lineWidth={4}
      opacity={props.opacity ?? 1}
    >
      <Txt
        text={props.text}
        fontFamily={MONO}
        fontWeight={700}
        fontSize={props.fontSize ?? 34}
        fill={C.white}
      />
    </Rect>
  );
}

function metric(props: {title: string; value: string; x: number; color: string; note?: string}) {
  return (
    <Rect x={props.x} width={460} height={290} radius={30} fill={C.panel} stroke={props.color} lineWidth={5}>
      <Txt text={props.title} y={-86} fontFamily={MONO} fontSize={42} fontWeight={700} fill={props.color} />
      <Txt text={props.value} y={0} fontFamily={MONO} fontSize={66} fontWeight={800} fill={C.white} />
      {props.note ? <Txt text={props.note} y={88} fontFamily={FONT} fontSize={28} fill={C.muted} /> : null}
    </Rect>
  );
}

function addHeader(root: Node, index: number) {
  root.add(
    <>
      <Rect width={1920} height={1080} fill={C.bg} />
      <Rect y={-485} width={1920} height={110} fill={'#0c1322'}>
        <Txt
          text={`FRAME RATE  /  ${String(index + 1).padStart(2, '0')}`}
          x={-805}
          fontFamily={MONO}
          fontWeight={700}
          fontSize={25}
          fill={C.blue}
          offsetX={-1}
        />
        <Txt
          text={SCENE_TITLES[index]}
          x={790}
          fontFamily={FONT}
          fontWeight={700}
          fontSize={42}
          fill={C.white}
          offsetX={1}
        />
      </Rect>
      <Line points={[[-870, -430], [870, -430]]} stroke={C.line} lineWidth={2} />
    </>,
  );
}

function scene01(root: Node, p: Progress) {
  const move = () => smooth(phase(p(), 0.02, 0.38));
  root.add(
    <>
      <Txt text="MOVEMENT" y={-300} fontFamily={MONO} fontSize={34} fill={C.muted} />
      <Line points={[[-760, 120], [760, 120]]} stroke={C.line} lineWidth={5} />
      {avatar({x: () => -670 + move() * 1340, y: 20, color: C.blue})}
      <Txt
        text="PAUSE"
        y={220}
        fontFamily={MONO}
        fontSize={54}
        fontWeight={800}
        fill={C.yellow}
        opacity={() => phase(p(), 0.32, 0.42)}
      />
      {[0, 1, 2, 3].map((i) => (
        <Rect
          key={`frame-${i}`}
          x={-585 + i * 390}
          y={330}
          width={330}
          height={210}
          radius={24}
          fill={C.panel}
          stroke={i === 3 ? C.blue : C.line}
          lineWidth={4}
          opacity={() => phase(p(), 0.38 + i * 0.045, 0.5 + i * 0.045)}
        >
          {avatar({x: -95 + i * 62, y: 20, color: C.blue, scale: 0.38})}
          <Txt text={`FRAME ${i + 1}`} y={78} fontFamily={MONO} fontSize={23} fill={C.text} />
        </Rect>
      ))}
      <Txt
        text="FRAME = ONE IMAGE"
        y={-205}
        fontFamily={MONO}
        fontSize={72}
        fontWeight={800}
        fill={C.white}
        opacity={() => phase(p(), 0.46, 0.6)}
      />
      <Rect
        width={1660}
        height={610}
        radius={44}
        fill={'#070b14f2'}
        stroke={C.blue}
        lineWidth={4}
        opacity={() => 1 - phase(p(), 0.1, 0.2)}
      >
        <Txt
          text="게임의 프레임 레이트는 무엇일까?"
          y={-70}
          fontFamily={FONT}
          fontSize={82}
          fontWeight={900}
          fill={C.white}
        />
        <Txt
          text="30 · 60 · 120 FPS  →  DLSS & FRAME GENERATION"
          y={70}
          fontFamily={MONO}
          fontSize={39}
          fontWeight={700}
          fill={C.yellow}
        />
      </Rect>
    </>,
  );
}

function scene02(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="1 SECOND" y={-300} fontFamily={MONO} fontSize={72} fontWeight={800} fill={C.white} />
      <Rect y={-190} width={1520} height={12} radius={6} fill={C.line}>
        <Rect
          width={() => 1520 * phase(p(), 0.05, 0.72)}
          height={12}
          radius={6}
          fill={C.blue}
          offsetX={-1}
          x={-760}
        />
      </Rect>
      <Node y={40}>
        {Array.from({length: 60}, (_, i) => {
          const row = Math.floor(i / 15);
          const col = i % 15;
          return (
            <Rect
              key={`f-${i}`}
              x={-700 + col * 100}
              y={-105 + row * 76}
              width={72}
              height={52}
              radius={8}
              fill={C.blue}
              opacity={() => (i < phase(p(), 0.08, 0.72) * 60 ? 0.95 : 0.12)}
            />
          );
        })}
      </Node>
      <Txt
        text="60 FRAMES / SECOND"
        y={300}
        fontFamily={MONO}
        fontSize={54}
        fontWeight={700}
        fill={C.text}
        opacity={() => phase(p(), 0.5, 0.66)}
      />
      <Txt
        text="60 FPS"
        y={390}
        fontFamily={MONO}
        fontSize={92}
        fontWeight={900}
        fill={C.yellow}
        opacity={() => phase(p(), 0.62, 0.76)}
      />
    </>,
  );
}

function scene03(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="DISTANCE = SPEED × TIME" y={-295} fontFamily={MONO} fontSize={62} fontWeight={800} fill={C.white} />
      <Line points={[[-720, 80], [720, 80]]} stroke={C.line} lineWidth={6} />
      {[0, 1, 2, 3].map((i) => (
        <Node key={`position-${i}`} x={-600 + i * 400} y={20} opacity={() => phase(p(), 0.08 + i * 0.12, 0.2 + i * 0.12)}>
          {avatar({x: 0, y: 0, color: C.green, scale: 0.58})}
          <Circle y={60} width={18} height={18} fill={C.yellow} />
          <Txt text={`FRAME ${i}`} y={155} fontFamily={MONO} fontSize={28} fill={C.muted} />
          <Txt text={`X = ${i}`} y={205} fontFamily={MONO} fontSize={36} fontWeight={700} fill={C.green} />
        </Node>
      ))}
      <Rect y={350} width={1050} height={110} radius={24} fill={C.panel} opacity={() => phase(p(), 0.52, 0.68)}>
        <Txt text="FRAME  →  LOGIC  →  TIME" fontFamily={MONO} fontSize={46} fontWeight={700} fill={C.text} />
      </Rect>
    </>,
  );
}

function scene04(root: Node, p: Progress) {
  const run = () => cycle(phase(p(), 0.08, 0.94) * 2.2);
  const x30 = () => -720 + Math.floor(run() * 30) / 29 * 1440;
  const x60 = () => -720 + Math.floor(run() * 60) / 59 * 1440;
  root.add(
    <>
      <Line points={[[0, -350], [0, 390]]} stroke={C.line} lineWidth={3} />
      <Txt text="30 FPS" x={-470} y={-310} fontFamily={MONO} fontSize={66} fontWeight={800} fill={C.orange} />
      <Txt text="60 FPS" x={470} y={-310} fontFamily={MONO} fontSize={66} fontWeight={800} fill={C.blue} />
      <Line points={[[-820, 20], [-80, 20]]} stroke={C.line} lineWidth={6} />
      <Line points={[[80, 20], [820, 20]]} stroke={C.line} lineWidth={6} />
      {Array.from({length: 15}, (_, i) => <Circle key={`l-${i}`} x={-800 + i * 51} y={20} width={10} height={10} fill={C.orange} opacity={0.55} />)}
      {Array.from({length: 30}, (_, i) => <Circle key={`r-${i}`} x={100 + i * 24} y={20} width={8} height={8} fill={C.blue} opacity={0.55} />)}
      {avatar({x: () => -770 + ((x30() + 720) / 1440) * 650, y: -80, color: C.orange, scale: 0.58})}
      {avatar({x: () => 120 + ((x60() + 720) / 1440) * 650, y: -80, color: C.blue, scale: 0.58})}
      <Txt text="SAME TIME" x={-470} y={245} fontFamily={MONO} fontSize={34} fill={C.text} />
      <Txt text="SAME DISTANCE" x={470} y={245} fontFamily={MONO} fontSize={34} fill={C.text} />
      <Txt text="MORE SAMPLES  ≠  FASTER GAME TIME" y={360} fontFamily={MONO} fontSize={44} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function scene05(root: Node, p: Progress) {
  const rows = [
    {fps: '30 FPS', ms: '33.33 ms', width: 1280, color: C.orange},
    {fps: '60 FPS', ms: '16.67 ms', width: 640, color: C.blue},
    {fps: '120 FPS', ms: '8.33 ms', width: 320, color: C.purple},
  ];
  root.add(
    <>
      <Txt text="FRAME BUDGET" y={-310} fontFamily={MONO} fontSize={76} fontWeight={900} fill={C.white} />
      {rows.map((row, i) => (
        <Node key={row.fps} y={-120 + i * 190} opacity={() => phase(p(), 0.06 + i * 0.1, 0.2 + i * 0.1)}>
          <Txt text={row.fps} x={-660} fontFamily={MONO} fontSize={46} fontWeight={700} fill={row.color} />
          <Rect x={70} width={1280} height={76} radius={18} fill={C.panel} offsetX={0}>
            <Rect width={row.width} height={76} radius={18} fill={`${row.color}bb`} offsetX={-1} x={-640} />
          </Rect>
          <Txt text={row.ms} x={760} fontFamily={MONO} fontSize={42} fontWeight={700} fill={C.white} />
        </Node>
      ))}
      <Txt text="HIGHER FPS  →  LESS TIME PER FRAME" y={390} fontFamily={MONO} fontSize={44} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function scene06(root: Node, p: Progress) {
  const values = [60, 60, 59, 60, 54, 45, 38, 52, 58, 60];
  const shown = () => Math.max(1, Math.ceil(phase(p(), 0.08, 0.82) * values.length));
  root.add(
    <>
      <Txt
        text={() => `${values[Math.min(values.length - 1, shown() - 1)]} FPS`}
        y={-305}
        fontFamily={MONO}
        fontSize={82}
        fontWeight={900}
        fill={() => values[Math.min(values.length - 1, shown() - 1)] < 50 ? C.red : C.green}
      />
      <Line points={[[-700, 260], [-700, -180]]} stroke={C.line} lineWidth={4} />
      <Line points={[[-700, 260], [720, 260]]} stroke={C.line} lineWidth={4} />
      <Line
        points={() => values.slice(0, shown()).map((v, i) => [-650 + i * 145, 230 - (v - 30) * 12] as [number, number])}
        stroke={C.blue}
        lineWidth={8}
        radius={12}
      />
      {values.map((v, i) => (
        <Circle
          key={`fps-${i}`}
          x={-650 + i * 145}
          y={230 - (v - 30) * 12}
          width={22}
          height={22}
          fill={v < 50 ? C.red : C.blue}
          opacity={() => (i < shown() ? 1 : 0)}
        />
      ))}
      <Txt text="AVERAGE FPS" x={-460} y={355} fontFamily={MONO} fontSize={30} fill={C.muted} />
      <Txt text="FRAME TIME" x={460} y={355} fontFamily={MONO} fontSize={30} fill={C.yellow} />
    </>,
  );
}

function scene07(root: Node, p: Progress) {
  const run = () => phase(p(), 0.25, 0.9);
  const q30 = () => Math.floor(run() * 30) / 30;
  const q60 = () => Math.floor(run() * 60) / 60;
  root.add(
    <>
      <Rect x={-470} y={-220} width={720} height={190} radius={26} fill={C.panel} stroke={C.red} lineWidth={4}>
        <Txt text="position += speed;" fontFamily={MONO} fontSize={42} fill={C.white} />
        <Txt text="FRAME DEPENDENT" y={65} fontFamily={MONO} fontSize={25} fill={C.red} />
      </Rect>
      <Rect x={470} y={-220} width={720} height={190} radius={26} fill={C.panel} stroke={C.green} lineWidth={4}>
        <Txt text="position += speed × deltaTime;" fontFamily={MONO} fontSize={36} fill={C.white} />
        <Txt text="TIME BASED" y={65} fontFamily={MONO} fontSize={25} fill={C.green} />
      </Rect>
      <Line points={[[-760, 120], [760, 120]]} stroke={C.line} lineWidth={6} />
      {avatar({x: () => -700 + q30() * 1400, y: 20, color: C.orange, scale: 0.5})}
      {avatar({x: () => -700 + q60() * 1400, y: 170, color: C.blue, scale: 0.5})}
      <Txt text="30 FPS" x={-820} y={20} fontFamily={MONO} fontSize={28} fill={C.orange} />
      <Txt text="60 FPS" x={-820} y={170} fontFamily={MONO} fontSize={28} fill={C.blue} />
      <Txt text="SAME 1 SECOND  →  SAME POSITION" y={370} fontFamily={MONO} fontSize={46} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function scene08(root: Node, p: Progress) {
  const rows = [
    {fps: 30, hz: 60, color: C.orange},
    {fps: 60, hz: 60, color: C.blue},
    {fps: 120, hz: 120, color: C.green},
    {fps: 240, hz: 240, color: C.purple},
  ];
  root.add(
    <>
      <Txt text="GAME OUTPUT" x={-520} y={-320} fontFamily={MONO} fontSize={38} fill={C.muted} />
      <Txt text="DISPLAY REFRESH" x={520} y={-320} fontFamily={MONO} fontSize={38} fill={C.muted} />
      {rows.map((row, i) => (
        <Node key={`${row.fps}`} y={-175 + i * 165} opacity={() => phase(p(), 0.05 + i * 0.1, 0.18 + i * 0.1)}>
          <Txt text={`${row.fps} FPS`} x={-610} fontFamily={MONO} fontSize={44} fontWeight={700} fill={row.color} />
          <Rect x={-50} width={620} height={78} radius={18} fill={C.panel}>
            {Array.from({length: Math.min(24, row.fps / 5)}, (_, n) => (
              <Rect key={`tick-${n}`} x={-275 + n * (550 / Math.max(1, Math.min(23, row.fps / 5 - 1)))} width={10} height={48} radius={5} fill={row.color} />
            ))}
          </Rect>
          <Rect x={560} width={310} height={105} radius={18} fill={'#08101e'} stroke={row.color} lineWidth={4}>
            <Txt text={`${row.hz} Hz`} fontFamily={MONO} fontSize={40} fontWeight={700} fill={C.white} />
          </Rect>
        </Node>
      ))}
      <Txt text="FPS ≠ Hz" y={405} fontFamily={MONO} fontSize={54} fontWeight={900} fill={C.yellow} />
    </>,
  );
}

function crtCard(props: {x: number; title: string; region: string; rate: string; color: string; speed: number; p: Progress}) {
  return (
    <Rect x={props.x} width={760} height={650} radius={34} fill={'#07110e'} stroke={props.color} lineWidth={6} clip>
      <Txt text={props.title} y={-245} fontFamily={MONO} fontSize={68} fontWeight={900} fill={props.color} />
      <Txt text={props.region} y={-180} fontFamily={MONO} fontSize={26} fill={C.muted} />
      <Txt text={props.rate} y={-118} fontFamily={MONO} fontSize={38} fill={C.white} />
      <Line points={[[-310, 160], [310, 160]]} stroke={C.line} lineWidth={5} />
      {avatar({x: () => -280 + cycle(phase(props.p(), 0.08, 0.94) * 2 * props.speed) * 560, y: 55, color: props.color, scale: 0.55})}
      {Array.from({length: 13}, (_, i) => <Line key={`scan-${i}`} points={[[-360, -70 + i * 40], [360, -70 + i * 40]]} stroke={'#ffffff12'} lineWidth={2} />)}
    </Rect>
  );
}

function scene09(root: Node, p: Progress) {
  root.add(
    <>
      {crtCard({x: -420, title: 'NTSC', region: 'JAPAN / NORTH AMERICA', rate: '≈ 60 fields/sec', color: C.blue, speed: 1, p})}
      {crtCard({x: 420, title: 'PAL', region: 'EUROPE / AUSTRALIA', rate: '50 fields/sec', color: C.orange, speed: 5 / 6, p})}
      <Rect y={370} width={700} height={100} radius={22} fill={C.panel}>
        <Txt text="50 / 60 = 5 / 6" fontFamily={MONO} fontSize={48} fontWeight={800} fill={C.yellow} />
      </Rect>
    </>,
  );
}

function scene10(root: Node, p: Progress) {
  root.add(
    <>
      <Rect x={-430} y={-40} width={720} height={620} radius={38} fill={C.panel} stroke={C.purple} lineWidth={6}>
        <Txt text="QUALITY / RESOLUTION" y={-225} fontFamily={MONO} fontSize={42} fontWeight={800} fill={C.purple} />
        <Txt text="HIGHER IMAGE QUALITY" y={-90} fontFamily={MONO} fontSize={34} fill={C.white} />
        <Txt text="RAY TRACING" y={0} fontFamily={MONO} fontSize={34} fill={C.white} />
        <Txt text="MORE RENDER COST" y={90} fontFamily={MONO} fontSize={34} fill={C.orange} />
      </Rect>
      <Rect x={430} y={-40} width={720} height={620} radius={38} fill={C.panel} stroke={C.green} lineWidth={6}>
        <Txt text="PERFORMANCE" y={-225} fontFamily={MONO} fontSize={48} fontWeight={800} fill={C.green} />
        <Txt text="HIGHER TARGET FPS" y={-90} fontFamily={MONO} fontSize={34} fill={C.white} />
        <Txt text="LOWER RENDER COST" y={0} fontFamily={MONO} fontSize={34} fill={C.white} />
        <Txt text="FASTER RESPONSE" y={90} fontFamily={MONO} fontSize={34} fill={C.green} />
      </Rect>
      <Node y={340} rotation={() => Math.sin(p() * Math.PI * 5) * 2}>
        <Line points={[[-440, 0], [440, 0]]} stroke={C.yellow} lineWidth={10} />
        <Line points={[[0, 0], [-80, 110], [80, 110], [0, 0]]} closed fill={C.yellow} />
        <Txt text="IMAGE QUALITY" x={-340} y={-50} fontFamily={MONO} fontSize={28} fill={C.purple} />
        <Txt text="FRAME RATE" x={340} y={-50} fontFamily={MONO} fontSize={28} fill={C.green} />
      </Node>
    </>,
  );
}

function scene11(root: Node, p: Progress) {
  const tasks = [
    {name: 'GEOMETRY', color: C.blue, width: 220},
    {name: 'LIGHTING', color: C.yellow, width: 250},
    {name: 'SHADOWS', color: C.purple, width: 210},
    {name: 'RAY TRACING', color: C.orange, width: 320},
    {name: 'POST FX', color: C.green, width: 210},
  ];
  let cursor = -660;
  root.add(
    <>
      <Txt text="16.67 ms @ 60 FPS" y={-310} fontFamily={MONO} fontSize={66} fontWeight={900} fill={C.white} />
      <Rect y={-190} width={1460} height={24} radius={12} fill={C.line}>
        <Rect width={() => 1460 * phase(p(), 0.05, 0.8)} height={24} radius={12} fill={C.blue} offsetX={-1} x={-730} />
      </Rect>
      <Node y={20}>
        {tasks.map((task, i) => {
          const x = cursor + task.width / 2;
          cursor += task.width + 24;
          return (
            <Rect key={task.name} x={x} width={task.width} height={230} radius={26} fill={`${task.color}22`} stroke={task.color} lineWidth={4} opacity={() => phase(p(), 0.08 + i * 0.08, 0.2 + i * 0.08)}>
              <Txt text={task.name} fontFamily={MONO} fontSize={task.name === 'RAY TRACING' ? 25 : 29} fontWeight={700} fill={C.white} />
            </Rect>
          );
        })}
      </Node>
      <Txt text="LIMITED MILLISECONDS" y={270} fontFamily={MONO} fontSize={46} fontWeight={800} fill={C.yellow} />
      <Txt text="QUALITY  ↔  FRAME RATE" y={365} fontFamily={MONO} fontSize={58} fontWeight={900} fill={C.text} />
    </>,
  );
}

function scene12(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="RTX 50 SERIES" y={-320} fontFamily={MONO} fontSize={78} fontWeight={900} fill={C.white} />
      <Node>
        {Array.from({length: 16}, (_, i) => {
          const angle = (Math.PI * 2 * i) / 16;
          const r = 330;
          return (
            <Line
              key={`circuit-${i}`}
              points={[[Math.cos(angle) * 170, Math.sin(angle) * 170], [Math.cos(angle) * r, Math.sin(angle) * r]]}
              stroke={i % 2 ? C.purple : C.blue}
              lineWidth={() => 4 + 5 * Math.sin(p() * Math.PI * 8 + i) ** 2}
              opacity={0.72}
            />
          );
        })}
        <Rect width={390} height={300} radius={42} fill={C.panel2} stroke={C.blue} lineWidth={8}>
          <Rect width={290} height={200} radius={26} fill={'#08111f'} stroke={C.purple} lineWidth={4} />
          <Txt text="GPU" y={-22} fontFamily={MONO} fontSize={74} fontWeight={900} fill={C.white} />
          <Txt text="AI + RT" y={62} fontFamily={MONO} fontSize={34} fontWeight={700} fill={C.blue} />
        </Rect>
      </Node>
      {['HIGH RESOLUTION', 'RAY TRACING', 'AI RENDERING'].map((text, i) => (
        <Rect key={text} x={-540 + i * 540} y={340} width={430} height={105} radius={22} fill={C.panel} stroke={[C.blue, C.orange, C.purple][i]} lineWidth={4} opacity={() => phase(p(), 0.15 + i * 0.12, 0.28 + i * 0.12)}>
          <Txt text={text} fontFamily={MONO} fontSize={30} fontWeight={700} fill={C.white} />
        </Rect>
      ))}
    </>,
  );
}

function scene13(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="3840 × 2160" y={-330} fontFamily={MONO} fontSize={72} fontWeight={900} fill={C.white} />
      <Txt text="8,294,400 PIXELS" y={-245} fontFamily={MONO} fontSize={42} fontWeight={700} fill={C.yellow} />
      <Rect y={60} width={1152} height={648} radius={20} fill={'#08111f'} stroke={C.line} lineWidth={4}>
        {Array.from({length: 32 * 18}, (_, i) => {
          const col = i % 32;
          const row = Math.floor(i / 32);
          const reveal = phase(p(), 0.08, 0.76);
          return (
            <Rect
              key={`pixel-${i}`}
              x={-548 + col * 35.3}
              y={-305 + row * 35.3}
              width={28}
              height={28}
              radius={4}
              fill={(col + row) % 5 === 0 ? C.purple : C.blue}
              opacity={() => (i / (32 * 18) < reveal ? 0.82 : 0.08)}
            />
          );
        })}
      </Rect>
      <Txt text="RAY  ·  SAMPLE  ·  SHADE" x={710} y={0} rotation={90} fontFamily={MONO} fontSize={28} fill={C.muted} />
      <Txt text="RENDER EVERY PIXEL DIRECTLY?" y={425} fontFamily={MONO} fontSize={46} fontWeight={800} fill={C.yellow} opacity={() => phase(p(), 0.6, 0.75)} />
    </>,
  );
}

function pixelGrid(props: {x: number; cols: number; rows: number; cell: number; color: string; p: Progress; start: number}) {
  return (
    <Node x={props.x}>
      <Rect width={props.cols * props.cell + 40} height={props.rows * props.cell + 40} radius={24} fill={'#08111f'} stroke={props.color} lineWidth={4}>
        {Array.from({length: props.cols * props.rows}, (_, i) => {
          const col = i % props.cols;
          const row = Math.floor(i / props.cols);
          return (
            <Rect
              key={`g-${i}`}
              x={(col - (props.cols - 1) / 2) * props.cell}
              y={(row - (props.rows - 1) / 2) * props.cell}
              width={props.cell - 4}
              height={props.cell - 4}
              fill={(col + row) % 4 === 0 ? props.color : `${props.color}55`}
              opacity={() => phase(props.p(), props.start + i / (props.cols * props.rows) * 0.18, props.start + 0.14 + i / (props.cols * props.rows) * 0.18)}
            />
          );
        })}
      </Rect>
    </Node>
  );
}

function scene14(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="DLSS SUPER RESOLUTION" y={-330} fontFamily={MONO} fontSize={66} fontWeight={900} fill={C.white} />
      {pixelGrid({x: -590, cols: 10, rows: 6, cell: 46, color: C.orange, p, start: 0.06})}
      <Txt text="LOWER INTERNAL" x={-590} y={270} fontFamily={MONO} fontSize={30} fill={C.orange} />
      <Rect width={330} height={180} radius={32} fill={C.panel2} stroke={C.purple} lineWidth={6}>
        <Txt text="DLSS" y={-25} fontFamily={MONO} fontSize={66} fontWeight={900} fill={C.white} />
        <Txt text="MOTION + HISTORY" y={48} fontFamily={MONO} fontSize={22} fill={C.purple} />
      </Rect>
      <Txt text="→" x={-295} fontFamily={MONO} fontSize={84} fill={C.muted} />
      <Txt text="→" x={295} fontFamily={MONO} fontSize={84} fill={C.muted} />
      {pixelGrid({x: 590, cols: 20, rows: 12, cell: 28, color: C.blue, p, start: 0.35})}
      <Txt text="HIGHER OUTPUT" x={590} y={270} fontFamily={MONO} fontSize={30} fill={C.blue} />
      <Txt text="PIXEL RECONSTRUCTION  ≠  FRAME GENERATION" y={405} fontFamily={MONO} fontSize={38} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function timelineFrames(props: {labels: string[]; colors: string[]; y: number; p: Progress; start?: number; width?: number}) {
  const width = props.width ?? 1420;
  return (
    <Node y={props.y}>
      <Line points={[[-width / 2, 0], [width / 2, 0]]} stroke={C.line} lineWidth={6} />
      {props.labels.map((label, i) => {
        const x = -width / 2 + i * (width / Math.max(1, props.labels.length - 1));
        return (
          <Rect
            key={`${props.y}-${i}`}
            x={x}
            width={120}
            height={120}
            radius={20}
            fill={`${props.colors[i]}33`}
            stroke={props.colors[i]}
            lineWidth={5}
            opacity={() => phase(props.p(), (props.start ?? 0.08) + i * 0.07, (props.start ?? 0.08) + 0.14 + i * 0.07)}
          >
            <Txt text={label} fontFamily={MONO} fontSize={48} fontWeight={900} fill={C.white} />
          </Rect>
        );
      })}
    </Node>
  );
}

function scene15(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="WITHOUT FRAME GENERATION" y={-315} fontFamily={MONO} fontSize={34} fill={C.muted} />
      {timelineFrames({labels: ['R', 'R', 'R'], colors: [C.blue, C.blue, C.blue], y: -175, p, start: 0.05, width: 1180})}
      <Txt text="WITH FRAME GENERATION" y={25} fontFamily={MONO} fontSize={34} fill={C.muted} />
      {timelineFrames({labels: ['R', 'G', 'R', 'G', 'R'], colors: [C.blue, C.purple, C.blue, C.purple, C.blue], y: 175, p, start: 0.34, width: 1420})}
      <Rect x={-330} y={365} width={520} height={78} radius={18} fill={C.panel}>
        <Txt text="R = RENDERED" fontFamily={MONO} fontSize={30} fill={C.blue} />
      </Rect>
      <Rect x={330} y={365} width={520} height={78} radius={18} fill={C.panel}>
        <Txt text="G = GENERATED" fontFamily={MONO} fontSize={30} fill={C.purple} />
      </Rect>
    </>,
  );
}

function scene16(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="RTX 50 SERIES" y={-335} fontFamily={MONO} fontSize={48} fontWeight={700} fill={C.blue} />
      <Txt text="DLSS 4  ·  MULTI FRAME GENERATION" y={-265} fontFamily={MONO} fontSize={62} fontWeight={900} fill={C.white} />
      {timelineFrames({
        labels: ['R', 'G', 'G', 'G', 'R', 'G', 'G', 'G', 'R'],
        colors: [C.blue, C.purple, C.purple, C.purple, C.blue, C.purple, C.purple, C.purple, C.blue],
        y: 0,
        p,
        start: 0.08,
        width: 1500,
      })}
      <Txt text="DLSS 4 LAUNCH: UP TO 3 GENERATED FRAMES / RENDERED FRAME" y={170} fontFamily={MONO} fontSize={30} fill={C.text} />
      <Rect y={315} width={1250} height={130} radius={26} fill={C.panel} stroke={C.yellow} lineWidth={3} opacity={() => phase(p(), 0.62, 0.76)}>
        <Txt text="DLSS 4.5  ·  DYNAMIC MFG  ·  UP TO 5 G / R" y={-20} fontFamily={MONO} fontSize={34} fontWeight={700} fill={C.yellow} />
        <Txt text="RESULTS VARY BY GAME · SETTINGS · GPU · CPU" y={32} fontFamily={MONO} fontSize={24} fill={C.muted} />
      </Rect>
    </>,
  );
}

function scene17(root: Node, p: Progress) {
  root.add(
    <>
      <Txt text="GAME ENGINE" x={-620} y={-300} fontFamily={MONO} fontSize={38} fill={C.muted} />
      <Txt text="DISPLAY" x={620} y={-300} fontFamily={MONO} fontSize={38} fill={C.muted} />
      <Line points={[[0, -350], [0, 360]]} stroke={C.line} lineWidth={3} />
      <Txt text="RENDERED FPS" x={-470} y={-205} fontFamily={MONO} fontSize={58} fontWeight={900} fill={C.blue} />
      <Node x={-470}>
        {timelineFrames({labels: ['R', 'R', 'R'], colors: [C.blue, C.blue, C.blue], y: 0, p, start: 0.06, width: 680})}
      </Node>
      <Txt text="DISPLAYED FPS" x={470} y={-205} fontFamily={MONO} fontSize={58} fontWeight={900} fill={C.purple} />
      <Node x={470}>
        {timelineFrames({labels: ['R', 'G', 'G', 'G', 'R'], colors: [C.blue, C.purple, C.purple, C.purple, C.blue], y: 0, p, start: 0.28, width: 720})}
      </Node>
      <Txt text="NOT EVERY DISPLAYED FRAME IS DIRECTLY RENDERED" y={300} fontFamily={MONO} fontSize={39} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function scene18(root: Node, p: Progress) {
  const stages = [
    {name: 'INPUT', color: C.yellow},
    {name: 'GAME', color: C.green},
    {name: 'RENDER', color: C.blue},
    {name: 'FRAME GEN', color: C.purple},
    {name: 'DISPLAY', color: C.orange},
  ];
  root.add(
    <>
      {metric({title: 'RENDER FPS', value: 'R / sec', x: -520, color: C.blue, note: 'directly rendered'})}
      {metric({title: 'DISPLAY FPS', value: 'R + G', x: 0, color: C.purple, note: 'presented frames'})}
      {metric({title: 'INPUT LATENCY', value: 'ms', x: 520, color: C.yellow, note: 'click to photon'})}
      <Node y={275}>
        {stages.map((stage, i) => (
          <Node key={stage.name} x={-680 + i * 340} opacity={() => phase(p(), 0.2 + i * 0.08, 0.34 + i * 0.08)}>
            <Rect width={250} height={105} radius={22} fill={`${stage.color}22`} stroke={stage.color} lineWidth={4}>
              <Txt text={stage.name} fontFamily={MONO} fontSize={28} fontWeight={700} fill={C.white} />
            </Rect>
            {i < stages.length - 1 ? <Txt text="→" x={170} fontFamily={MONO} fontSize={48} fill={C.muted} /> : null}
          </Node>
        ))}
      </Node>
      <Txt text="ONE FPS NUMBER IS NOT THE WHOLE PIPELINE" y={410} fontFamily={MONO} fontSize={38} fontWeight={800} fill={C.yellow} />
    </>,
  );
}

function pipelineColumn(props: {x: number; title: string; items: string[]; colors: string[]; p: Progress; start: number}) {
  return (
    <Node x={props.x}>
      <Txt text={props.title} y={-330} fontFamily={MONO} fontSize={50} fontWeight={900} fill={props.colors[0]} />
      {props.items.map((item, i) => (
        <Node key={item} y={-220 + i * (500 / Math.max(1, props.items.length - 1))} opacity={() => phase(props.p(), props.start + i * 0.07, props.start + 0.14 + i * 0.07)}>
          <Rect width={540} height={82} radius={18} fill={C.panel} stroke={props.colors[Math.min(i, props.colors.length - 1)]} lineWidth={3}>
            <Txt text={item} fontFamily={MONO} fontSize={26} fontWeight={700} fill={C.white} />
          </Rect>
          {i < props.items.length - 1 ? <Txt text="↓" y={68} fontFamily={MONO} fontSize={34} fill={C.muted} /> : null}
        </Node>
      ))}
    </Node>
  );
}

function scene19(root: Node, p: Progress) {
  root.add(
    <>
      {pipelineColumn({x: -430, title: 'OLD GAME', items: ['GAME LOGIC', 'FRAME', 'DISPLAY'], colors: [C.orange, C.orange, C.orange], p, start: 0.05})}
      {pipelineColumn({x: 430, title: 'MODERN GAME', items: ['INPUT', 'SIMULATION', 'RENDERING', 'UPSCALING', 'FRAME GENERATION', 'DISPLAY'], colors: [C.green, C.green, C.blue, C.cyan, C.purple, C.orange], p, start: 0.28})}
      <Line points={[[0, -350], [0, 390]]} stroke={C.line} lineWidth={3} />
      <Txt text="STAGES MAY RUN AT DIFFERENT RATES" y={420} fontFamily={MONO} fontSize={38} fontWeight={700} fill={C.yellow} />
    </>,
  );
}

function scene20(root: Node, p: Progress) {
  const cards = [
    {title: 'FRAME', value: 'ONE IMAGE', color: C.blue},
    {title: 'FPS', value: 'FRAMES / SECOND', color: C.green},
    {title: 'FRAME TIME', value: '33 · 16 · 8 ms', color: C.orange},
    {title: 'deltaTime', value: 'ELAPSED TIME', color: C.yellow},
    {title: 'FRAME GEN', value: 'R ≠ EVERY DISPLAYED FRAME', color: C.purple},
    {title: 'DEVELOPER', value: 'TARGET · PROFILE · TEST', color: C.cyan},
  ];
  root.add(
    <>
      <Txt text="FRAME RATE — FINAL CHECK" y={-330} fontFamily={MONO} fontSize={64} fontWeight={900} fill={C.white} />
      {cards.map((card, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        return (
          <Rect
            key={card.title}
            x={-430 + col * 860}
            y={-155 + row * 205}
            width={760}
            height={165}
            radius={26}
            fill={C.panel}
            stroke={card.color}
            lineWidth={4}
            opacity={() => phase(p(), 0.04 + i * 0.08, 0.17 + i * 0.08)}
          >
            <Txt text={card.title} x={-315} fontFamily={MONO} fontSize={30} fontWeight={800} fill={card.color} offsetX={-1} />
            <Txt text={card.value} x={315} fontFamily={MONO} fontSize={card.value.length > 22 ? 24 : 30} fontWeight={700} fill={C.white} offsetX={1} />
          </Rect>
        );
      })}
      <Txt text="CHOOSE A TARGET  →  MEASURE FRAME TIME  →  TEST GAME SPEED" y={430} fontFamily={MONO} fontSize={35} fontWeight={800} fill={C.yellow} opacity={() => phase(p(), 0.56, 0.72)} />
    </>,
  );
}

const BUILDERS = [
  scene01,
  scene02,
  scene03,
  scene04,
  scene05,
  scene06,
  scene07,
  scene08,
  scene09,
  scene10,
  scene11,
  scene12,
  scene13,
  scene14,
  scene15,
  scene16,
  scene17,
  scene18,
  scene19,
  scene20,
] as const;

/**
 * Build one editor-visible Motion Canvas scene.
 *
 * Every scene first shows a short real-game example and then hands the same
 * concept to this channel's own motion graphic. The two parts together keep
 * the exact narration-derived scene duration from timing.ts.
 */
export function createFrameRateScene(index: number) {
  const builder = BUILDERS[index];
  if (!builder || !EXAMPLES[index]) {
    throw new Error(`Unknown frame-rate scene index: ${index}`);
  }

  return makeScene2D(function* (view) {
    view.fill(C.bg);
    const root = createRef<Node>();
    const progress = createSignal(0);
    view.add(<Node ref={root} opacity={0} />);
    addHeader(root(), index);
    builder(root(), progress);

    const duration = SCENE_DURATIONS[index];
    yield* playExample(view, index);

    const visualDuration = Math.max(0.5, duration - EXAMPLES[index].duration);
    const active = Math.max(0.1, visualDuration - 0.4);
    yield* all(root().opacity(1, 0.4), progress(1, active, linear));
    yield* root().opacity(0, 0.4);
    root().remove();
  });
}
