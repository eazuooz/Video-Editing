import {makeScene2D,Video} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {ACTUAL_MEDIA_READY,SCENE_DURATIONS} from '../timing';

export function actualScene(index:number){return makeScene2D(function*(view){
 if(!ACTUAL_MEDIA_READY)throw new Error('Game-writing actual media/timing has not been captured and verified. Do not render the prepared script as a completed video.');
 view.add(<Video src={`/@fs/D:/Github/Video-Editing/shared/assets/game-writing/playtest/scene${String(index+1).padStart(2,'0')}.mp4`} width={1920} height={1080} play={true}/>);
 yield* waitFor(SCENE_DURATIONS[index]);
});}
