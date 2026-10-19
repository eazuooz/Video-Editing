import {makeScene2D,Rect,Txt} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-zombie-quiet-director/production/intro-v2/timing.json';
import {makeMonsterFrequencyIntro} from './intro-animation';
export default makeScene2D(function*(view){
 const t=createSignal(0);view.fill('#000000');
 view.add(makeMonsterFrequencyIntro(t,timing.introSeconds));
 view.add(<Rect width={1080} height={490} position={[0,-715]} fill="#000000"/>);
 view.add(<Txt text="얌얌코딩" fontFamily="Malgun Gothic" fontSize={37} fontWeight={700} fill="#B8C3BC" position={[-340,-820]}/>);
 view.add(<Txt text="좀비가 조용해지면" fontFamily="Malgun Gothic" fontSize={74} fontWeight={700} fill="#FFFFFF" position={[-30,-700]}/>);
 view.add(<Txt text="안심해도 될까?" fontFamily="Malgun Gothic" fontSize={84} fontWeight={700} fill="#FFD25A" position={[-30,-590]}/>);
 view.add(<Txt text="전투 빈도의 조절" fontFamily="Malgun Gothic" fontSize={33} fill="#B8C3BC" position={[-30,-500]}/>);
 yield* t(timing.introSeconds,timing.introSeconds,linear);
});
