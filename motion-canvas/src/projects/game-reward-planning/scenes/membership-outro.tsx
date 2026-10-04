import {Img,Rect,Txt,makeScene2D} from '@motion-canvas/2d';
import {createRef,usePlayback} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import original from '../../../../../shared/assets/membership/member-list-20260929.png';
import cats from '../../../../../shared/assets/branding/yamyamcoding-cats-original.png';
export default makeScene2D(function*(view){view.fill(P.background);const title=createRef<Txt>();view.add(<>
 <Txt ref={title} text="멤버쉽가입 감사드립니다." x={-854} y={-385} offset={[-1,0]} fontFamily={P.font} fontSize={52} fontWeight={700} fill={P.ink}/>
 <Txt text="함께 배우고, 직접 만드는 시간을 응원합니다." x={-854} y={-303} offset={[-1,0]} fontFamily={P.font} fontSize={28} fill={P.muted}/>
 <Txt text="프로그래밍 코칭 · 과외" x={-850} y={-194} offset={[-1,0]} fontFamily={P.font} fontSize={32} fill={P.blue}/>
 <Txt text={"https://www.yamyamcoding.com/\n1430b1ff-a61e-8040-a542-d672d5d25328"} x={-850} y={-115} offset={[-1,0]} fontFamily={P.font} fontSize={23} fill={P.muted}/>
 <Img src={original} x={650} y={0} height={900}/><Img src={cats} x={886} y={484} width={88} height={88}/>
 </>);const playback=usePlayback(),start=playback.frame;while(playback.frame-start<600)yield;
});
