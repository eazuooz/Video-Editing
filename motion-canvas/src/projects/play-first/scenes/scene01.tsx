import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene01.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 0,
    chapter: "01 · 첫 조작",
    title: "스타트를 누르면, 바로 마리오",
    clip,
    exampleLabel: "슈퍼 마리오 오디세이 — 짧은 오프닝 뒤 착지·첫 조작 안내, 달리고 뛰기",
    panels: [
      {line: 0, beat: 0, heading: "스타트 후 몇 분째, 아직도 영상"},
      {line: 1, beat: 1, heading: "처음 몇 분: 보기와 하기의 비율"},
      {line: 4, beat: 3, heading: "오늘 살펴볼 오디세이의 순서"},
    ],
  });
});
