import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene01.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 0,
    chapter: "01 · 첫 3분",
    title: "스타트를 눌렀는데, 아직도 영상",
    clip,
    exampleLabel: "실제 예시 · 슈퍼 마리오 오디세이 — 짧은 오프닝 뒤 첫 조작",
    panels: [
      {line: 0, beat: 0, heading: "스타트 후 3분째, 아직도 영상"},
      {line: 2, beat: 1, heading: "처음 3분: 보기와 하기의 비율"},
      {line: 3, beat: 2, heading: "재미는 해 보고 판단한다"},
      {line: 5, beat: 3, heading: "오늘의 질문"},
    ],
  });
});
