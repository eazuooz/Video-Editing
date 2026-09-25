import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene03.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 2,
    chapter: "03 · 이야기와 조작",
    title: "이야기가 꼭 필요하다면",
    clip,
    exampleLabel: "실제 예시 · 슈퍼 마리오 오디세이 — 싸움 한복판에서 시작하는 오프닝 (조작 전 영상)",
    panels: [
      {line: 0, beat: 0, heading: "도입부가 필요한 장르도 있다"},
      {line: 1, beat: 1, heading: "방법 1 · 사건 한복판부터"},
      {line: 3, beat: 2, heading: "플레이 순서는 바꿀 수 있다"},
      {line: 4, beat: 3, heading: "손에 잡히면 궁금해진다"},
      {line: 5, beat: 4, heading: "이야기는 그대로, 조작은 앞으로"},
    ],
  });
});
