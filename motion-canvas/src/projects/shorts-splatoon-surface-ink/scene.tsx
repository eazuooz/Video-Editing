import {makeScene2D, Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK as C} from '../../styles/research-dark';
import {requireProductionInput} from './production-input';
import {cueProgress, focusAt, sectionAt, smooth, visualAt, type CueId, type Point} from './model';

const FONT = 'Malgun Gothic';
const point = (x: number, y: number): Point => [x - 540, y - 960];
const cats = {puzzled, realize, relief};

/** Enlarged two-view explanation from the SAME captured Unity frame. */
export default makeScene2D(function* (view) {
  const {timing, config} = requireProductionInput();
  view.fill(C.background);
  const time = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(time() * 60 + .0001));
  const section = () => sectionAt(timing, frame()).id;
  const visual = () => visualAt(timing, config, frame());
  const isGame = () => visual().kind === 'gameplay';
  const inCue = (id: CueId) => frame() >= timing.events[id].startFrame && frame() < timing.events[id].endFrame;
  const after = (id: CueId) => frame() >= timing.events[id].startFrame;
  const progress = (id: CueId) => smooth(cueProgress(timing, frame(), id));
  const orbit = () => section() === 'orbit';
  const definition = () => inCue('p2-3') ? {en:'Texture',ko:'텍스처',plain:'색을 저장하는 그림',cue:'p2-3' as CueId}
    : inCue('p4-2') ? {en:'UV coordinates',ko:'UV 좌표',plain:'그림 속 가로·세로 주소',cue:'p4-2' as CueId} : undefined;
  const defAlpha = () => {const d=definition();return d ? 1-smooth((cueProgress(timing,frame(),d.cue)-.6)/.4) : 0;};

  view.add(<Img src={() => visual().path} size={[1000,562.5]} position={point(540,820)} opacity={() => isGame()?1:0}/>);
  // Crop only blank margins of our own capture; native gameplay remains16:9.
  // Each crop is an equal-axis scale. All target anchors use the same transform.
  const explain = new Node({opacity:()=>isGame()?0:1}); view.add(explain);
  const surfaceCenter:Point=[320,930], surfaceSource:Point=[570,1120], surfaceScale=.8;
  const sheetCenter:Point=[830,870], sheetSource:Point=[544,546], sheetScale=1;
  const transform=(p:Point,center:Point,source:Point,scale:number):Point=>[center[0]+(p[0]-source[0])*scale,center[1]+(p[1]-source[1])*scale];
  const original=(p:Point):Point=>[(p[0]-216)/.6,(p[1]-284)/.6];
  const wall=transform(original(config.compositing.anchors.impact),surfaceCenter,surfaceSource,surfaceScale);
  const sheet=transform(original(config.compositing.anchors.sheet),sheetCenter,sheetSource,sheetScale);
  const surfacePanel=new Rect({size:[560,520],position:point(...surfaceCenter),clip:true,opacity:()=>orbit()?0:1-defAlpha()*.75});
  surfacePanel.add(<Img src={()=>visual().path} size={[1080*surfaceScale,1920*surfaceScale]}
    position={[(540-surfaceSource[0])*surfaceScale,(960-surfaceSource[1])*surfaceScale]}/>);explain.add(surfacePanel);
  const sheetPanel=new Rect({size:[420,410],position:point(...sheetCenter),clip:true,opacity:()=>orbit()?0:1-defAlpha()*.75});
  sheetPanel.add(<Img src={()=>visual().path} size={[1080,1920]}
    position={[540-sheetSource[0],960-sheetSource[1]]}/>);explain.add(sheetPanel);
  const orbitPanel=new Rect({size:[980,710],position:point(540,925),clip:true,opacity:()=>orbit()?1:0});
  orbitPanel.add(<Img src={()=>visual().path} size={[1080*.83,1920*.83]} position={[(540-540)*.83,(960-1160)*.83]}/>);explain.add(orbitPanel);

  view.add(<Txt text={()=>after('p4-2')?'UV 좌표 · UV coordinates':after('p2-3')?'텍스처 · Texture':'표면에 남는 잉크'} position={point(55,475)} offset={[-1,0]} fill={C.teal} fontFamily={FONT} fontSize={29} fontWeight={700}/>);
  view.add(<Txt text={()=>isGame()?'실제 게임 · 스플래툰 3':'우리 Unity 시연'} position={point(1025,475)} offset={[1,0]} fill={C.muted} fontFamily={FONT} fontSize={27}/>);
  const heading=()=>({game:'어떻게 맞은 자리에 남을까?',sheet:'벽과 색칠 그림을 연결한다',collision:'1  잉크가 맞은 위치를 찾는다',uv:'2  그림 속 같은 주소를 찾는다',stamp:'3  그림에 색을 기록한다',patch:after('p6-2')?'옆 조각에도 이어서 찍는다':'경계에서 자국이 끊겼다',orbit:'카메라만 움직여도, 잉크는 제자리'}[section()]);
  explain.add(<Txt text={heading} position={point(540,550)} fill={C.title} fontFamily={FONT} fontSize={40} fontWeight={700}/>);
  const labels=new Node({opacity:()=>orbit()?0:1-defAlpha()});explain.add(labels);
  labels.add(<Txt text="게임 속 벽·바닥" position={point(320,620)} fill={C.ink} fontFamily={FONT} fontSize={35} fontWeight={700}/>);
  labels.add(<Txt text={()=>after('p2-3')?'색 기록 · 텍스처':'투명한 색칠 그림'} position={point(830,620)} fill={C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);

  // One explicit correspondence replaces the previous persistent3-step list.
  const mapping=()=>['collision','uv','stamp'].includes(section());
  const arrowForward=()=>section()!=='stamp';
  const mappingProgress=()=>section()==='collision'?smooth(cueProgress(timing,frame(),'p3-3')):section()==='uv'?1:progress('p5-2');
  labels.add(<Line points={()=>arrowForward()?[point(...wall),point(610,wall[1]),point(640,sheet[1]),point(...sheet)]:[point(...sheet),point(640,sheet[1]),point(610,wall[1]),point(...wall)]}
    stroke={()=>section()==='stamp'?C.green:C.teal} lineWidth={7} endArrow arrowSize={18}
    end={mappingProgress} opacity={()=>mapping()&&after('p3-3')?1:0}/>);
  labels.add(<Circle position={point(...wall)} size={45} stroke={C.red} lineWidth={6}
    opacity={()=>section()==='collision'&&after('p3-2')?1:0}/>);
  labels.add(<Circle position={point(...sheet)} size={30} stroke={C.teal} lineWidth={6}
    opacity={()=>section()==='uv'&&after('p4-3')?1:0}/>);
  labels.add(<Txt text={()=>section()==='collision'?'맞은 곳 → 그림의 주소':section()==='uv'?'같은 지점을 두 좌표로 표현':section()==='stamp'?'그림을 바꾸면 벽에도 반영':'표면마다 자기 그림이 있다'}
    position={point(55,1220)} offset={[-1,0]} fill={C.title} fontFamily={FONT} fontSize={34} fontWeight={700}
    opacity={()=>section()==='patch'?0:1}/>);

  // A worked midpoint with horizontal/vertical guides, read from captured UV.
  const uv=config.compositing.uvReadout;
  labels.add(<Line points={[point(637,sheet[1]),point(...sheet)]} stroke={C.title} lineWidth={6} endArrow arrowSize={15}
    end={()=>smooth(cueProgress(timing,frame(),'p4-3','p4-4'))} opacity={()=>section()==='uv'&&after('p4-3')?1:0}/>);
  labels.add(<Line points={[point(sheet[0],1065),point(...sheet)]} stroke={C.teal} lineWidth={6} endArrow arrowSize={15}
    end={()=>smooth(cueProgress(timing,frame(),'p4-3','p4-4'))} opacity={()=>section()==='uv'&&after('p4-3')?1:0}/>);
  for (const [label,value,y] of [['가로 절반 → U',uv.u!,1108],['세로 절반 → V',uv.v!,1156]] as const) {
    labels.add(<Txt text={`${label} ${value.toFixed(1)}`} position={point(820,y)} fill={C.ink} fontFamily={FONT} fontSize={32} fontWeight={700}
      opacity={()=>section()==='uv'&&after('p4-4')?1:0}/>);
  }

  // Same captured boundary evolves from clipped mark to connected mark.
  labels.add(<Line points={[point(827,665),point(827,1060)]} stroke={()=>after('p6-2')?C.green:C.red} lineWidth={6}
    opacity={()=>section()==='patch'?1:0}/>);
  labels.add(<Txt text={()=>after('p6-2')?'양쪽에 이어서 기록':'한쪽 조각에만 기록'} position={point(820,1130)} fill={()=>after('p6-2')?C.green:C.red} fontFamily={FONT} fontSize={32} fontWeight={700}
    opacity={()=>section()==='patch'?1:0}/>);
  explain.add(<Txt text="같은 색 기록, 다른 카메라 위치" position={point(540,620)} fill={C.green} fontFamily={FONT} fontSize={35} fontWeight={700} opacity={()=>orbit()?1:0}/>);
  explain.add(<Txt text={'색은 화면이 아닌\n표면에 저장된다'} position={point(60,1200)} offset={[-1,0]} fill={C.title} fontFamily={FONT} fontSize={35} fontWeight={700} lineHeight={48} opacity={()=>orbit()?1:0}/>);

  const card=new Node({opacity:defAlpha});explain.add(card);
  card.add(<Txt text={()=>definition()?.en??''} position={point(540,710)} fill={C.title} fontFamily={FONT} fontSize={44} fontWeight={700}/>);
  card.add(<Txt text={()=>definition()?.ko??''} position={point(540,770)} fill={C.ink} fontFamily={FONT} fontSize={42} fontWeight={700}/>);
  card.add(<Txt text={()=>definition()?.plain??''} position={point(540,835)} fill={C.ink} fontFamily={FONT} fontSize={35}/>);

  const target=()=>{const v=visual();if(v.kind!=='gameplay')return undefined;const cut=config.gameplayCuts[v.cut];return focusAt(cut.focus??[],v.sourceSeconds!-cut.sourceStartSeconds);};
  view.add(<Circle position={()=>{const t=target();return t?point(540+(t.x-960)*1000/1920,820+(t.y-540)*1000/1920):[0,0];}}
    size={()=>{const t=target();return t?[t.radiusX*2000/1920,t.radiusY*2000/1920]:[1,1];}} stroke={C.green} lineWidth={7} opacity={()=>target()?1:0}/>);
  const reaction=()=>{for(const [id,kind] of [['p1-2','puzzled'],['p4-4','realize'],['p7-3','relief']] as const){const cue=timing.events[id];const start=cue.startFrame/60;const end=Math.min(cue.endFrame/60,start+2.3);if(time()>=start&&time()<end)return{kind,start,end};}return undefined;};
  const catOpacity=()=>{const r=reaction();return r?smooth((time()-r.start)/.16)*smooth((r.end-time())/.18):0;};
  const cat=new Rect({size:[460,560],position:point(830,1510),clip:true,opacity:catOpacity});view.add(cat);
  cat.add(<Img src={()=>cats[reaction()?.kind??'realize']} size={650} position={()=>[55+14*(1-catOpacity()),0]}/>);
  yield view.toPromise();
  yield* time(timing.frames/60,timing.frames/60,linear);
});
