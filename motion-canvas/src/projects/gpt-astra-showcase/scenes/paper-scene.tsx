import {Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import manifest from '../../../../../projects/gpt-astra-showcase/project.json';

export function* paperScene(view:View2D,index:number,title:string,subtitle:string,duration:number) {
  view.fill(P.background);
  const exampleSeconds=manifest.editing.exampleSeconds;
  const placeholder=new Node({});view.add(placeholder);
  placeholder.add(<>
    <Txt x={-864} y={-477} offset={[-1,0]} text={`${index+1} · 실제 예시 구간`} fill={P.muted} fontFamily={P.font} fontSize={25}/>
    <Rect width={1664} height={936} y={-10} fill={P.panel} stroke={P.line} lineWidth={1}>
      <Txt text={`허용된 예시 영상 ${exampleSeconds}초를 연결하세요`} fill={P.ink} fontFamily={P.font} fontSize={45}/>
      <Txt y={90} text={'준비 화면입니다. 이 상태로 게시하지 않습니다.'} fill={P.muted} fontFamily={P.font} fontSize={29}/>
    </Rect>
  </>);
  yield* waitFor(Math.min(duration,exampleSeconds));placeholder.remove();
  view.add(<>
    <Txt text={`${index+1} · What Did Creators Build with GPT Astra? | 8 Showcases`} x={-864} y={-477} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
    <Txt text={title} x={-864} y={-405} offset={[-1,0]} fontFamily={P.font} fontSize={52} fontWeight={600} fill={P.ink}/>
    <Txt text={subtitle} x={-864} y={-325} offset={[-1,0]} fontFamily={P.font} fontSize={30} fill={P.muted}/>
    <Txt text={'이곳에 한 가지 핵심 도식·비교를 제작합니다.'} fontFamily={P.font} fontSize={38} fill={P.ink}/>
    <Rect y={425} width={1728} height={86} fill={P.panel} stroke={P.ink} lineWidth={1.5}>
      <Txt text={'시청자가 기억할 결론 한 문장'} fontFamily={P.font} fontSize={30} fill={P.ink}/>
    </Rect>
  </>);
  yield* waitFor(Math.max(0,duration-exampleSeconds));
}
