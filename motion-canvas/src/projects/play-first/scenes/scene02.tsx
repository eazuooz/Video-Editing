import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene02.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 1,
    chapter: "02 · 첫인사",
    title: "그래서, 무슨 게임인데?",
    clip,
    exampleLabel: "실제 예시 · 슈퍼 마리오 오디세이 — 모자 던지기와 캡처",
    panels: [
      {line: 0, beat: 0, heading: "가상의 상점 트레일러 A"},
      {line: 1, beat: 1, heading: "궁금증이 풀리는 시점: A와 B"},
      {line: 2, beat: 2, heading: "그래서, 뭘 하는 게임인데?"},
    ],
  });
});
