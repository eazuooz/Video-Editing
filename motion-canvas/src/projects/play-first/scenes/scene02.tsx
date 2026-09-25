import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene02.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 1,
    chapter: "02 · 핵심 행동",
    title: "모자 하나로 알려 주는 게임",
    clip,
    exampleLabel: "슈퍼 마리오 오디세이 — 모자로 코인·상자, 멍멍이 캡처와 튕겨 보내기",
    panels: [
      {line: 0, beat: 0, heading: "조작 후 가장 먼저: 던지기 하나"},
      {line: 4, beat: 1, heading: "배울 것은 하나, 쓰임은 계속 늘어난다"},
    ],
  });
});
