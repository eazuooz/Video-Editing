// Channel rule: every video ends with the ~10s membership thank-you (docs/MEMBERSHIP_OUTRO.md).
import {Img, makeScene2D, Txt} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import roster from '../../../shared/membership/members.json';
import memberImage from '../../../../../shared/assets/membership/member-list-20260929.png';

export default makeScene2D(function* (view) {
  // Reuse the user's latest image as one original asset: profiles, names and badges stay together.
  view.fill(P.background);
  const image=createRef<Img>();
  const title=createRef<Txt>();
  view.add(<>
    <Txt text="MEMBERSHIP" x={-864} y={-166} offset={[-1,0]} fontFamily={P.font} fontSize={26} fill={P.blue}/>
    <Txt ref={title} text={roster.title} x={-864} y={-80} offset={[-1,0]} fontFamily={P.font} fontSize={56} fontWeight={700} fill={P.ink} opacity={0}/>
    <Txt text={roster.subtitle} x={-864} y={20} offset={[-1,0]} fontFamily={P.font} fontSize={30} fill={P.muted}/>
    <Img ref={image} src={memberImage} x={646} y={0} height={900} opacity={0}/>
  </>);
  yield* all(title().opacity(1,.4),image().opacity(1,.4));
  yield* waitFor(9.1);
  yield* all(title().opacity(0,.5),image().opacity(0,.5));
});
