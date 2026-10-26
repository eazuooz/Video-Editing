import {makeScene2D, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import timingInput from '../../../../projects/shorts-teardown-spray-palette/production/visual-timing.json';
import configInput from '../../../../projects/shorts-teardown-spray-palette/production/visual-config.json';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK} from '../../styles/research-dark';
import {CELLS, FULL_PALETTE, ORIGINAL, ORIGINAL_MATERIAL, VARIANTS, BROWN_FALLBACK,
  clamp01, gridIndices, hex, materialTextColor, slotsPerOriginal, smooth, targetForStep, unchangedIndex} from './model';

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
  // Each reveal uses the unchanged spoken clause, not an arbitrary scene clock.
  const beat = (name: string, from = 0, to = 1) => {
    const e = timing.events?.[name];
    if (!e) return 0;
    const progress = (frame() - e.startFrame) / Math.max(1, (e.endFrame ?? e.startFrame + 60) - e.startFrame);
    return smooth((progress - from) / Math.max(.001, to - from));
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
  stage.add(<Txt text="번호와 색은 설명용 예시" fontFamily={FONT} fontSize={27}
    position={[0, -335]} fill={C.muted}/>);

  const mechanism = new Node({opacity: () => ['capacity', 'limits'].includes(id()) ? 0 : 1});
  stage.add(mechanism);
  const swap = () => id() === 'variants' ? beat('p3-4', .1, .8)
    : id() === 'lookup' ? beat('p4-2', .25, .8) : id() === 'close' ? 1 : 0;
  const grid = () => gridIndices(1, swap());
  const numberOpacity = () => id() === 'index' ? beat('p2-2', 0, .2) : 1;
  const tableOpacity = () => id() === 'index' ? beat('p2-4', 0, .18) : 1;
  const paletteTop = () => id() === 'index' ? -80 : id() === 'variants' ? -80 - 140 * beat('p3-1', 0, .6) : -180;
  const paletteY = (row: number) => paletteTop() + row * (id() === 'variants' ? 72 : 155);
  const useYellow = () => id() === 'lookup' ? beat('p4-2', 0, .22)
    : id() === 'variants' ? beat('p3-3', 0, .3) : id() === 'close' ? 1 : 0;
  const arrowEnd = () => id() === 'index' ? beat('p2-4', .18, .6)
    : id() === 'variants' ? beat('p3-3', 0, .5) : id() === 'lookup' ? beat('p4-2', 0, .25) : 1;
  mechanism.add(<Txt text="복셀 단면" position={[-215, -270]} fontFamily={FONT} fontSize={36} fill={C.ink}/>);
  for (let i = 0; i < CELLS.length; i++) {
    const [x, y] = CELLS[i];
    const material = () => FULL_PALETTE.find(m => m.index === grid()[i])!;
    mechanism.add(<Rect position={[-380 + x * 110, -170 + y * 110]} size={[104, 104]} radius={2}
      fill={() => hex(material().rgb)} stroke={C.line} lineWidth={2}/>);
    mechanism.add(<Txt text={() => String(grid()[i])} position={[-380 + x * 110, -170 + y * 110]}
      fontFamily="Consolas" fontSize={48} fontWeight={700} fill={() => materialTextColor(material().rgb)} opacity={numberOpacity}/>);
  }
  // Follow the actual cell adjacent to the lookup, rather than a decorative arrow.
  mechanism.add(<Rect position={[-50,-170]} size={[108,108]} stroke={C.teal} lineWidth={5}
    opacity={() => id() === 'index' ? beat('p2-3',0,.2) : 1}/>);
  mechanism.add(<Txt text={() => id() === 'index' ? '1칸에 번호 하나 · 1바이트' : '칸의 모양은 그대로'}
    position={[-215, 155]} fontFamily={FONT} fontSize={31} fill={C.teal}
    opacity={() => id() === 'index' ? numberOpacity() : 1}/>);
  mechanism.add(<Line points={() => [[8,-170],[55,-170],[55,paletteY(useYellow()>.5?1:0)],[105,paletteY(useYellow()>.5?1:0)]]}
    stroke={C.teal} lineWidth={6} end={arrowEnd} endArrow arrowSize={18} opacity={tableOpacity}/>);
  mechanism.add(<Txt text="팔레트 = 재질표" position={[285, -270]} fontFamily={FONT} fontSize={34}
    fill={C.ink} opacity={tableOpacity}/>);
  for (let i = 0; i < FULL_PALETTE.length; i++) {
    const m = FULL_PALETTE[i];
    const visible = () => i === 0 ? tableOpacity() : id() === 'index' ? 0
      : id() === 'variants' ? beat('p3-2', (i-1)/4, Math.min(1,(i-1)/4+.18)) : i===1 ? 1 : 0;
    const selected = () => (useYellow()>.5 ? 1 : 0) === i;
    const row = new Node({opacity: visible});
    mechanism.add(row);
    row.add(<Rect position={() => [285, paletteY(i)]} size={() => [350,id()==='variants'?62:104]} radius={5}
      fill={hex(m.rgb)} stroke={() => selected() ? C.title : C.line} lineWidth={() => selected() ? 5 : 1}/>);
    row.add(<Txt text={`${m.index} · ${m.name}`} position={() => [285, paletteY(i)]} fontFamily={FONT}
      fontSize={() => id()==='variants'?35:44} fontWeight={700} fill={materialTextColor(m.rgb)}/>);
  }
  const besideCat = () => ['lookup','close'].includes(id());
  mechanism.add(<Txt text={() => id() === 'index' ? (beat('p2-4')>0 ? '표에서 색·표면·물리 성질을 찾음' : '재질 인덱스 = 재질을 찾는 번호')
    : id() === 'variants' ? (beat('p3-3')>0 ? '변환표에서 노란 재질 번호를 찾음' : '노랑 4단계를 미리 준비')
    : '번호를 바꾸면\n표에서 다른 재질을 찾음'}
    position={() => besideCat() ? [-230, 225] : [0, 225]} fontFamily={FONT}
    fontSize={32} fill={C.ink} opacity={() => id() === 'index' ? beat('p2-3',0,.15) : 1}/>);
  mechanism.add(<Txt text={() => useYellow()>.5 ? '3  →  9' : '재질 번호 3'} position={[-230, 300]}
    fontFamily={FONT} fontSize={43} fontWeight={700} fill={C.title}
    opacity={() => ['lookup','close'].includes(id()) ? 1 : 0}/>);

  const capacity = new Node({opacity: () => id() === 'capacity' ? 1 : 0});
  stage.add(capacity);
  capacity.add(<Txt text="재질표 전체: 최대 255칸" position={[0, -260]} fontFamily={FONT}
    fontSize={43} fill={C.ink} opacity={() => beat('p5-2',0,.15)}/>);
  capacity.add(<Txt text="원래 재질" position={[-408, -160]} fontFamily={FONT} fontSize={30} fill={C.ink}/>);
  capacity.add(<Rect position={[-408,-65]} size={[78,78]} fill={hex(ORIGINAL_MATERIAL.rgb)} stroke={C.line} lineWidth={3}/>);
  capacity.add(<Txt text="1" position={[-408,45]} fontFamily={FONT} fontSize={46} fill={C.ink}/>);
  for (let tint = 0; tint < 2; tint++) {
    const reveal = (i: number) => beat('p5-3', tint*.5+i*.1, tint*.5+i*.1+.1);
    const x = tint===0 ? -132 : 276;
    capacity.add(<Txt text={tint === 0 ? '노랑 4단계' : '검정 4단계'} position={[x,-160]}
      fontFamily={FONT} fontSize={32} fill={C.ink} opacity={() => reveal(0)}/>);
    for (let i=0;i<4;i++) capacity.add(<Rect position={[(tint===0?-264:144)+i*88,-65]} size={[78,78]}
      fill={tint===0 ? hex(VARIANTS[i].rgb) : ['#604637','#46372e','#2b2824','#141414'][i]}
      stroke={C.line} lineWidth={3} opacity={() => reveal(i)}/>);
    capacity.add(<Line points={[[x-171,0],[x-171,12],[x+171,12],[x+171,0]]} stroke={C.teal}
      lineWidth={3} opacity={() => reveal(3)}/>);
    capacity.add(<Txt text="4" position={[x,55]} fontFamily={FONT} fontSize={46} fill={C.ink} opacity={() => reveal(3)}/>);
    capacity.add(<Txt text="+" position={[tint===0?-336:72,-65]} fontFamily={FONT} fontSize={42}
      fill={C.muted} opacity={() => reveal(0)}/>);
  }
  capacity.add(<Txt text={`1 + 4 + 4 = ${slotsPerOriginal()}칸`} position={[0,165]} fontFamily={FONT}
    fontSize={62} fontWeight={700} fill={C.title} opacity={() => beat('p5-4',0,.2)}/>);
  capacity.add(<Txt text="벽돌 한 종류에도 표의 9칸을 사용" position={[0,245]} fontFamily={FONT}
    fontSize={35} fill={C.ink} opacity={() => beat('p5-4',.2,.4)}/>);
  capacity.add(<Txt text="노랑·검정을 섞은 변형은 별도" position={[0,305]}
    fontFamily={FONT} fontSize={26} fill={C.muted} opacity={() => beat('p5-4',.4,.55)}/>);

  const limits = new Node({opacity: () => id() === 'limits' ? 1 : 0});
  stage.add(limits);
  const selection = () => beat('p6-2',0,.12);
  const onlyOriginal = () => beat('p6-4',.55,.65)>.5;
  const chosen = () => onlyOriginal() ? ORIGINAL_MATERIAL : BROWN_FALLBACK;
  const merge = new Node({opacity:()=>1-selection()});limits.add(merge);
  merge.add(<Txt text="공간이 부족하면 비슷한 색을 합침" position={[0,-250]} fontFamily={FONT} fontSize={38} fill={C.ink}/>);
  merge.add(<Rect position={[-300,-75]} size={[155,155]} fill={hex(ORIGINAL_MATERIAL.rgb)} stroke={C.line} lineWidth={3}/>);
  merge.add(<Rect position={[-100,-75]} size={[155,155]} fill="#774938" stroke={C.line} lineWidth={3}/>);
  merge.add(<Txt text="비슷한 갈색 둘" position={[-200,60]} fontFamily={FONT} fontSize={34} fill={C.ink}/>);
  merge.add(<Line points={[[8,-75],[170,-75]]} end={()=>beat('p6-1',.25,.7)} stroke={C.teal} lineWidth={6} endArrow arrowSize={18}/>);
  merge.add(<Rect position={[290,-75]} size={[155,155]} fill={hex(ORIGINAL_MATERIAL.rgb)} stroke={C.title}
    lineWidth={4} opacity={()=>beat('p6-1',.6,.85)}/>);
  merge.add(<Txt text="하나로 합침" position={[290,60]} fontFamily={FONT} fontSize={34} fill={C.ink}
    opacity={()=>beat('p6-1',.6,.85)}/>);
  merge.add(<Txt text="2칸 → 1칸" position={[0,200]} fontFamily={FONT} fontSize={58} fill={C.title}
    opacity={()=>beat('p6-1',.6,.85)}/>);
  const match = new Node({opacity:selection});limits.add(match);
  match.add(<Txt text="남은 재질 중 가장 가까운 색" position={[0,-250]} fontFamily={FONT} fontSize={38} fill={C.ink}/>);
  match.add(<Rect position={[-260,-105]} size={[190,190]} fill={hex(targetForStep(4).rgb)} stroke={C.title} lineWidth={4}/>);
  match.add(<Txt text="원하는 노랑" position={[-260,30]} fontFamily={FONT} fontSize={34} fill={C.ink}/>);
  match.add(<Line points={[[-125,-105],[105,-105]]} stroke={C.teal} lineWidth={6} endArrow arrowSize={18}/>);
  match.add(<Rect position={[240,-105]} size={[190,190]} fill={()=>hex(chosen().rgb)} stroke={C.line} lineWidth={4}/>);
  match.add(<Txt text={()=>onlyOriginal()?'3 · 원래 벽돌':'7 · 기존 갈색'} position={[240,30]}
    fontFamily={FONT} fontSize={34} fill={C.ink}/>);
  match.add(<Txt text={()=>onlyOriginal()?'남은 후보가 원래 재질뿐이면':'사용할 수 있는 재질 (예시)'}
    position={[0,110]} fontFamily={FONT} fontSize={30} fill={C.muted}/>);
  for(const [i,m] of [ORIGINAL_MATERIAL,BROWN_FALLBACK].entries()){
    match.add(<Rect position={[-170+i*330,165]} size={[265,62]} fill={hex(m.rgb)}
      stroke={()=>chosen().index===m.index?C.teal:C.line} lineWidth={4} opacity={() => i===1 && onlyOriginal() ? .1 : 1}/>);
    match.add(<Txt text={`${m.index} · ${m.name}`} position={[-170+i*330,165]} fontFamily={FONT}
      fontSize={32} fill={materialTextColor(m.rgb)} opacity={()=>i===1&&onlyOriginal()?0:1}/>);
  }
  match.add(<Txt text={()=>onlyOriginal()?`${ORIGINAL} → ${unchangedIndex()} · 색이 그대로`:'2020 Castle: 노랑 대신 갈색도 선택'}
    position={[0,275]} fontFamily={FONT} fontSize={34} fill={C.title} opacity={()=>beat('p6-3',0,.15)}/>);

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
