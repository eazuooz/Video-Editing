import {Line, makeScene2D, Rect, Txt, Video} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';
import source from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/media/kirby-air-riders-first-race.mp4';

// Source review: local 121.5–128.9 s, first-race recording HjA-J3yKJ2I.
// Preserve all original pixels inside 1536×864. Fixed captions stay at (960,970).
// Marks are editorial emphasis of visible UI; no invented detector output.
export default makeScene2D(function* (view) {
  const film=createRef<Video>(), count=createRef<Rect>(), music=createRef<Rect>();
  const trace=createRef<Line>(), label=createRef<Txt>(), caption=createRef<Txt>();
  view.fill(D.background);
  view.add(<>
    <Video ref={film} src={source} width={1536} height={864} y={-108} time={121.5} loop={false}/>
    <Rect x={-462} y={-497} width={180} height={66} stroke={D.background} lineWidth={13} opacity={()=>count().opacity()}/>
    <Rect ref={count} x={-462} y={-497} width={180} height={66} stroke={D.title} lineWidth={7} opacity={0}/>
    <Rect x={472} y={-178} width={470} height={480} stroke={D.background} lineWidth={13} opacity={()=>music().opacity()}/>
    <Rect ref={music} x={472} y={-178} width={470} height={480} stroke={D.green} lineWidth={7} opacity={0}/>
    <Line points={[[-100,-360],[-380,-360],[-445,-455]]} stroke={D.background} lineWidth={13} endArrow arrowSize={23} end={()=>trace().end()} opacity={()=>trace().opacity()}/>
    <Line ref={trace} points={[[-100,-360],[-380,-360],[-445,-455]]} stroke={D.title} lineWidth={7} endArrow arrowSize={18} end={0}/>
    <Txt ref={label} x={90} y={-360} text={'완료한 과제 수'} fontFamily={D.font} fontSize={40} fontWeight={700} fill={D.title} stroke={D.background} lineWidth={8} strokeFirst opacity={0}/>
    <Txt x={-746} y={339} offset={[-1,0]} text={'Kirby Air Riders · Recording: LongplayArchive / SpectreBull'} fontFamily={D.font} fontSize={24} fill={D.muted}/>
    <Rect x={12} y={430} width={1680} height={146} fill={'#073c32'}/>
    <Rect y={430} width={1680} height={146} fill={'#ffffff'} stroke={'#161b18'} lineWidth={3}/>
    <Txt ref={caption} y={430} text={'한 판이 끝난 뒤, 달성한 과제를\n결과 화면에서 확인합니다.'} fontFamily={'Noto Sans KR, Malgun Gothic, sans-serif'} fontSize={48} lineHeight={62} fill={'#080b09'}/>
  </>);
  film().play();
  yield* waitFor(3);
  caption().text('완료한 과제가 47개에서 48개로 늘고,\n새 음악을 얻습니다.');
  yield* all(count().opacity(1,.2),label().opacity(1,.2),trace().end(1,.45));
  yield* waitFor(1.8);
  yield* all(count().opacity(0,.15),label().opacity(0,.15),trace().opacity(0,.15));
  yield* waitFor(.35);
  yield* music().opacity(1,.2);
  yield* waitFor(1.25);
  yield* music().opacity(0,.15);
  yield* waitFor(.05);
  film().pause();
});
