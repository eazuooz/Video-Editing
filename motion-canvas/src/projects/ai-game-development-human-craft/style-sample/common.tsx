import {Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {DARK} from '../../../styles/research-dark';
import {CaptionBox} from '../../game-dev-career/preview/caption-box';

export function scaffold(view: View2D, number: string, title: string, subtitle: string) {
  view.fill(DARK.background);
  view.add(<Txt text={`AI와 게임 개발   /   ${number}`} x={-850} y={-473} offsetX={-1}
    fontFamily={DARK.font} fontSize={25} fill={DARK.muted} />);
  view.add(<Txt text="설명용 모형" x={850} y={-473} offsetX={1} fontFamily={DARK.font} fontSize={25} fill={DARK.muted} />);
  view.add(<Txt text={title} y={-400} fontFamily={DARK.font} fontSize={56} fontWeight={700} fill={DARK.yellow} />);
  view.add(<Txt text={subtitle} y={-330} fontFamily={DARK.font} fontSize={31} fill={DARK.ink} />);
  view.add(<Line points={[[-850,-282],[850,-282]]} stroke="#343b3f" lineWidth={2} />);
  const diagram = new Node({}); view.add(diagram);
  const caption = new CaptionBox({y:430});view.add(caption);
  view.add(<Txt text="노랑: 현재 확인    ·    청록: 확인됨    ·    회색: 미확인    ·    빨강: 문제 발견"
    y={318} fontFamily={DARK.font} fontSize={25} fill={DARK.muted} />);
  return {diagram,caption};
}

export function annotation(parent: Node, text: string, x: number, y: number, color: string = DARK.muted) {
  const label=new Txt({text,x,y,fontSize:27,fontFamily:DARK.font,fill:color});parent.add(label);return label;
}
