import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene04.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 3,
    chapter: "04 · 게임만의 것",
    title: "게임만 줄 수 있는 것부터",
    clip,
    exampleLabel: "실제 예시 · 슈퍼 마리오 오디세이 — 폭포의 나라, 공룡 캡처",
    panels: [
      {line: 0, beat: 0, heading: "왜 플레이를 앞에 둘까?"},
      {line: 1, beat: 1, heading: "영상과 이야기는 공통, 입력에 대한 반응은 게임만"},
      {line: 3, beat: 2, heading: "첫 조작은 곧 게임의 약속"},
      {line: 4, beat: 3, heading: "다른 매체로는 대신할 수 없는 것부터"},
    ],
  });
});
