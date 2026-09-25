import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene04.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 3,
    chapter: "04 · 게임만의 것",
    title: "보는 것이 아니라, 되어 보는 것",
    clip,
    exampleLabel: "슈퍼 마리오 오디세이 — 폭포의 나라에서 공룡에게 다가가 캡처하고 돌진",
    panels: [
      {line: 0, beat: 0, heading: "왜 플레이를 앞에 둘까?"},
      {line: 1, beat: 1, heading: "영상과 이야기는 공통, 입력에 대한 반응은 게임만"},
      {line: 4, beat: 2, heading: "손맛을 먼저, 할 일은 스스로 알게"},
    ],
  });
});
