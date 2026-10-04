import {Rect,Txt,View2D} from '@motion-canvas/2d';
export function addCaptionClearanceGuide(view:View2D){
  // Two-line approved typography at the fixed anchor tests the maximum
  // narration footprint. This lookdev label is not an actual SRT cue.
  view.add(<>
    <Rect x={14} y={444} width={1570} height={146} fill={'#073c32'}/>
    <Rect y={430} width={1570} height={146} fill={'white'} stroke={'#161b18'} lineWidth={3}/>
    <Txt y={430} text={'무음 구성 검토 · 최종 음성과 자막은 미검수\n현재 화면은 최종 전달본이 아닙니다.'} fontFamily={'Noto Sans KR, Malgun Gothic, sans-serif'} fontSize={48} lineHeight={62} fontWeight={500} fill={'#080b09'}/>
  </>);
}
