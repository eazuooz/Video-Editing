import {makeScene2D} from '@motion-canvas/2d';
import {run as s01} from './scene-01';
import {run as s02} from './scene-02';
import {run as s03} from './scene-03';
import {run as s04} from './scene-04';
import {run as s05} from './scene-05';
import {run as s06} from './scene-06';
import {run as s07} from './scene-07';
import {run as s08} from './scene-08';
export default makeScene2D(function*(view){
yield* s01(view);
yield* s02(view);
yield* s03(view);
yield* s04(view);
yield* s05(view);
yield* s06(view);
yield* s07(view);
yield* s08(view);
});
