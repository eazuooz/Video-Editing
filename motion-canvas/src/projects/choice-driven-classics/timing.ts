// User-fixed timeline. Never overwrite with speech-length-derived timing.
import board from '../../../../projects/choice-driven-classics/script/storyboard.json';
export const NARRATION_FPS = board.fps;
export const TOTAL_DURATION = board.duration;
export const TOTAL_FRAMES = board.fps * board.duration;
export const SCENE_STARTS = board.scenes.map(s=>s.start);
export const SCENE_DURATIONS = board.scenes.map(s=>s.end-s.start);
export const SCENE_TITLES = ['관심을 여는 장면','제품 소개','선택의 결과','제작 방식','수익 구조','첫 데모'];
