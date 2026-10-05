import {Node, Rect, Txt} from '@motion-canvas/2d';
import {PAPER} from '../../styles/research-paper';
/** Fixed bottom-center guide only; all final literal cues remain independently pending. */
export function captionLookdevGuide(view: Node) {
  view.add(<Rect x={14} y={444} width={1210} height={146} fill={'#073C32'}/>);
  view.add(<Rect y={430} width={1210} height={146} fill={'#FFFFFF'} stroke={'#161B18'} lineWidth={3}>
    <Txt text={`도구가 늘었을 때 달라지는 거리·위치의 판단
원래 설명은 보존하고 실제 행동을 함께 확인합니다.`}
      fontFamily={PAPER.font} fontSize={48} fill={'#080B09'} lineHeight={62} textAlign={'center'}/>
  </Rect>);
}
