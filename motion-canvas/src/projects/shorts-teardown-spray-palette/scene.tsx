import {makeScene2D, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import timingInput from '../../../../projects/shorts-teardown-spray-palette/production/visual-timing.json';
import configInput from '../../../../projects/shorts-teardown-spray-palette/production/visual-config.json';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK} from '../../styles/research-dark';
import {CELLS, FULL_PALETTE, ORIGINAL, ORIGINAL_MATERIAL, VARIANTS, BROWN_FALLBACK,
  clamp01, fallbackIndex, gridIndices, hex, slotsPerOriginal, smooth, targetForStep, unchangedIndex} from './model';

type Id = 'game' | 'index' | 'variants' | 'lookup' | 'capacity' | 'limits' | 'close';
type Event = {startFrame: number; endFrame?: number; durationFrames?: number};
type Section = {id: Id; visualId?: Id; start: number; end: number; startFrame: number; endFrame: number; forceDiagram?: boolean};
type Timing = {previewOnly?: boolean; fps: number; frames: number; sections: Section[]; events?: Record<string, Event>};
type Config = {footageReady: boolean; framesPrepared?: boolean; frameRoot?: string; cuts?: Partial<Record<Id, {frameDirectory?: string; maxDuration: number; firstFrame?: number; digits?: number}>>};
const timing = timingInput as Timing;
const config = configInput as Config;
const C = DARK;
const FONT = 'Malgun Gothic';
const labels: Record<Id, string> = {
  game: '스프레이가 바꾸는 것은 재질 번호', index: '작은 칸마다 재질 번호 하나',
  variants: '색칠된 재질을 미리 준비', lookup: '번호를 바꾸면, 색이 달라진다',
  capacity: '표의 칸도 무한하지 않다', limits: '같은 목표색 · 사용할 칸만 변경',
  close: '적은 메모리와 다양한 색 사이',
};

/**
 * No render/job registration here. Timing comes from the current PCM/caption proof.
 * Fixed header 0..440 and caption band1290..1470 are reserved for finalizer.
 * The picture stays a flat data-model explanation; no fabricated 3D game demo.
 * No candidate/research720p file is imported or referenced by this scene.
 */
export default makeScene2D(function* (view) {
  view.fill(C.background);
  const t = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(t() * timing.fps + .0001));
  const section = () => timing.sections.find(s => frame() >= s.startFrame && frame() < s.endFrame) ?? timing.sections[timing.sections.length - 1];
  const sourceId = () => section().id;
  const elapsed = () => t() - section().start;
  const phase = () => clamp01(elapsed() / Math.max(1 / timing.fps, section().end - section().start));
  const cue = (name: string, fallback: [number, number]) => {
    const e = timing.events?.[name];
    return e ? smooth((frame() - e.startFrame) / Math.max(1, (e.endFrame ?? e.startFrame + (e.durationFrames ?? 60)) - e.startFrame))
      : smooth((phase() - fallback[0]) / (fallback[1] - fallback[0]));
  };
  const cut = () => config.cuts?.[sourceId()];
  const footage = () => config.framesPrepared === true && config.footageReady && !section().forceDiagram
    && Boolean(cut()) && elapsed() >= 0 && elapsed() < (cut()?.maxDuration ?? 0);
  // Keep seven spoken sections intact. Only the picture changes after the
  // bounded official opening; never hold/loop the last source frame.
  const id = (): Id => sourceId() === 'game' && !footage()
    ? 'index' : section().visualId ?? sourceId();
  const stage = new Node({opacity: () => footage() ? 0 : 1});
  view.add(stage);
  view.add(<Txt text="팔레트 변환표 · 2020 공개 구현" fontFamily={FONT} fontSize={27}
    position={[-465, -482]} offset={[-1, 0]} fill={C.teal}/>);
  view.add(<Txt text={() => footage() ? '실제 게임 녹화' : '해설용 모형'} fontFamily={FONT} fontSize={25}
    position={[470, -445]} offset={[1, 0]} fill={C.muted}/>);
  stage.add(<Txt text={() => labels[id()]} fontFamily={FONT} fontSize={40} fontWeight={700}
    position={[0, -390]} fill={C.title}/>);
  stage.add(<Txt text="번호와 색은 설명용 예시 · 게임에서 측정한 값 아님" fontFamily={FONT} fontSize={25}
    position={[0, -335]} fill={C.muted}/>);

  const mechanism = new Node({opacity: () => ['capacity', 'limits'].includes(id()) ? 0 : 1});
  stage.add(mechanism);
  const step = () => id() === 'variants' ? Math.min(4, Math.floor(cue('variantsReveal', [.1, .75]) * 4 + .0001))
    : id() === 'lookup' || id() === 'close' ? 1 : id() === 'game' ? 4 : 0;
  const sweep = () => id() === 'game' ? phase() : id() === 'variants' ? cue('recolor', [.7, .95])
    : id() === 'lookup' ? cue('numberSwap', [.1, .64]) : id() === 'close' ? 1 : 0;
  const grid = () => gridIndices(step(), sweep());
  const showNumbers = () => id() !== 'game';
  mechanism.add(<Txt text="복셀 단면" position={[-375, -270]} fontFamily={FONT} fontSize={32} fill={C.ink}/>);
  for (let i = 0; i < CELLS.length; i++) {
    const [x, y] = CELLS[i];
    const material = () => FULL_PALETTE.find(m => m.index === grid()[i])!;
    mechanism.add(<Rect position={[-390 + x * 55, -205 + y * 55]} size={[52, 52]} radius={2}
      fill={() => hex(material().rgb)} stroke="#c8bbb0" lineWidth={1.5}/>);
    mechanism.add(<Txt text={() => String(grid()[i])} position={[-390 + x * 55, -205 + y * 55]}
      fontFamily="Consolas" fontSize={27} fontWeight={700} fill="#ffffff"
      stroke="#24201b" lineWidth={1} opacity={() => showNumbers() ? 1 : 0}/>);
  }
  mechanism.add(<Txt text={() => id() === 'index' ? '재질 인덱스 1바이트 / 복셀' : '같은 칸 · 같은 모양'}
    position={[-200, 155]} fontFamily={FONT} fontSize={29} fill={C.teal}/>);
  mechanism.add(<Line points={[[30, -80], [88, -80]]} stroke={C.teal} lineWidth={6} endArrow arrowSize={18}/>);
  mechanism.add(<Txt text="팔레트" position={[300, -270]} fontFamily={FONT} fontSize={32} fill={C.ink}/>);
  for (let i = 0; i < FULL_PALETTE.length; i++) {
    const m = FULL_PALETTE[i];
    const visible = () => i === 0 || ['lookup', 'close'].includes(id()) || (id() === 'variants' && i <= Math.max(1, step()));
    const row = new Node({opacity: () => visible() ? 1 : .12});
    mechanism.add(row);
    row.add(<Rect position={[300, -204 + i * 72]} size={[350, 58]} radius={5}
      fill={hex(m.rgb)} stroke={() => grid().includes(m.index) ? C.title : C.line}
      lineWidth={() => grid().includes(m.index) ? 5 : 1}/>);
    row.add(<Txt text={`${m.index} · ${m.name}`} position={[300, -204 + i * 72]} fontFamily={FONT}
      fontSize={29} fontWeight={700} fill="#ffffff" stroke="#24201b" lineWidth={1.2}/>);
  }
  const besideCat = () => ['lookup','close'].includes(id());
  mechanism.add(<Txt text={() => id() === 'index' ? '색 + 표면 성질 + 물리 재질'
    : id() === 'lookup' ? '변환표[3][노랑 1단계]\n→ 9' : id() === 'variants' ? '노랑을 4단계로 미리 준비' : '번호가 가리키는\n재질을 표시'}
    position={() => besideCat() ? [-230, 230] : [0, 235]} fontFamily={FONT}
    fontSize={() => besideCat() ? 29 : 31} fill={C.ink}/>);
  mechanism.add(<Txt text="재질 번호 3  →  9" position={[-230, 305]} fontFamily={FONT} fontSize={31}
    fill={C.title} opacity={() => ['lookup','close'].includes(id()) ? 1 : 0}/>);

  const capacity = new Node({opacity: () => id() === 'capacity' ? 1 : 0});
  stage.add(capacity);
  capacity.add(<Txt text="팔레트 하나: 최대 255개 재질" position={[0, -260]} fontFamily={FONT}
    fontSize={35} fill={C.ink}/>);
  capacity.add(<Txt text="원래 재질" position={[-320, -180]} fontFamily={FONT} fontSize={31} fill={C.ink}/>);
  capacity.add(<Rect position={[-320,-100]} size={[95,95]} fill={hex(ORIGINAL_MATERIAL.rgb)} stroke={C.line} lineWidth={3}/>);
  capacity.add(<Txt text="1" position={[-320,-100]} fontFamily={FONT} fontSize={36} fill={C.ink}/>);
  for (let tint = 0; tint < 2; tint++) {
    capacity.add(<Txt text={tint === 0 ? '노랑 4단계' : '검정 4단계'} position={[30,-180 + tint * 220]}
      fontFamily={FONT} fontSize={31} fill={C.ink}/>);
    for (let i=0;i<4;i++) capacity.add(<Rect position={[-90+i*112,-100+tint*220]} size={[95,95]}
      fill={tint===0 ? hex(VARIANTS[i].rgb) : ['#604637','#46372e','#2b2824','#141414'][i]}
      stroke={C.line} lineWidth={3} opacity={() => .15 + .85*cue('variantCount',[.25,.8])}/>);
  }
  capacity.add(<Txt text={`1 + 4 + 4 = ${slotsPerOriginal()}칸`} position={[0,230]} fontFamily={FONT}
    fontSize={51} fontWeight={700} fill={C.title}/>);
  capacity.add(<Txt text="노랑 위에 검정까지 섞으면 더 많은 변형이 필요" position={[0,305]}
    fontFamily={FONT} fontSize={25} fill={C.muted}/>);

  const limits = new Node({opacity: () => id() === 'limits' ? 1 : 0});
  stage.add(limits);
  const full = () => cue('slotsFull',[.1,.35]) < .5;
  const chosen = () => full() ? targetForStep(4) : BROWN_FALLBACK;
  limits.add(<Txt text="목표: 같은 노란 재질" position={[0,-260]} fontFamily={FONT} fontSize={33} fill={C.ink}/>);
  limits.add(<Rect position={[-310,-130]} size={[155,155]} fill={hex(targetForStep(4).rgb)} stroke={C.title} lineWidth={4}/>);
  limits.add(<Txt text="목표색" position={[-310,-20]} fontFamily={FONT} fontSize={30} fill={C.ink}/>);
  limits.add(<Line points={[[-195,-130],[-65,-130]]} stroke={C.teal} lineWidth={6} endArrow arrowSize={18}/>);
  limits.add(<Rect position={[100,-130]} size={[155,155]} fill={() => hex(chosen().rgb)} stroke={C.line} lineWidth={4}/>);
  limits.add(<Txt text={() => `${fallbackIndex(full())} · ${full()?'노랑':'기존 갈색'}`} position={[100,-20]}
    fontFamily={FONT} fontSize={30} fill={C.ink}/>);
  limits.add(<Txt text={() => full() ? '빈칸 있음 → 노란 재질 추가' : '빈칸 없음 → 기존 재질 중 선택'} position={[0,70]}
    fontFamily={FONT} fontSize={34} fill={() => full() ? C.green : C.red}/>);
  limits.add(<Txt text={() => full() ? '' : `다른 선택지가 없으면: ${ORIGINAL} → ${unchangedIndex()} (그대로)`}
    position={[0,150]} fontFamily={FONT} fontSize={29} fill={C.ink}/>);
  limits.add(<Txt text="2020 Castle 예시의 제한" position={[0,235]} fontFamily={FONT} fontSize={32} fill={C.title}/>);
  limits.add(<Txt text="현재 모든 표면이 안 칠해진다는 뜻은 아님" position={[0,300]} fontFamily={FONT}
    fontSize={25} fill={C.muted}/>);

  // Only the independently selected native-FHD official spray excerpt is used.
  if (config.footageReady && config.cuts && Object.keys(config.cuts).length) {
    const source = () => {
      const c = cut();
      if (!c || !footage()) return '';
      const n = (c.firstFrame ?? 0) + Math.min(Math.floor(elapsed()*timing.fps), Math.ceil(c.maxDuration*timing.fps)-1);
      return `${config.frameRoot}${c.frameDirectory ?? sourceId()}/${String(n).padStart(c.digits ?? 6,'0')}.jpg`;
    };
    view.add(<Img src={source} width={1080} height={608} position={[0,-45]} opacity={() => footage()?1:0}/>);
  }
  const reactionOn = () => (id()==='lookup' && phase()>.6) || (id()==='close' && phase()>.3);
  const catOpacity = () => reactionOn() ? smooth((phase()-(id()==='close'?.3:.6))/.12) : 0;
  // Same approved large bottom-right crop as Cuphead/SurfaceInk. The finalizer
  // draws captions above this area; mechanism labels stay in the left column.
  const cat = new Rect({size:[460,560],position:[290,430],clip:true,opacity:catOpacity});
  view.add(cat);
  cat.add(<Img src={() => id()==='close'?relief:realize} size={650}
    position={() => [55+14*(1-catOpacity()),0]}/>);
  if (timing.previewOnly) view.add(<Txt text="구성 초안 · 실제 음성 타이밍 미확정" position={[0,920]}
    fontFamily={FONT} fontSize={22} fill={C.muted}/>);
  yield* t(timing.frames / timing.fps, timing.frames / timing.fps, linear);
});
