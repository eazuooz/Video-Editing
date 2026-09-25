import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene05.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 4,
    chapter: "05 · 설계",
    title: "무엇을 먼저 보여 줄지 정하기",
    clip,
    exampleLabel: "실제 예시 · 슈퍼 마리오 오디세이 — 본편 길 위의 캡처, 첫 보스 뒤 타이틀",
    panels: [
      {line: 0, beat: 0, heading: "정답은 게임마다 다르다"},
      {line: 1, beat: 1, heading: "먼저 보여 줄 것을 의도해서 정하기"},
      {line: 4, beat: 2, heading: "내 게임의 첫 3분 점검"},
      {line: 5, beat: 3, heading: "기다리게 하지 말고, 먼저 놀게 해 주세요."},
    ],
  });
});
