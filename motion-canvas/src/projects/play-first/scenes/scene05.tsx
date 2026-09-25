import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene05.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 4,
    chapter: "05 · 튜토리얼과 제목",
    title: "튜토리얼도, 제목도 놀이 뒤에",
    clip,
    exampleLabel: "슈퍼 마리오 오디세이 — 본편 길 위의 개구리 캡처, 첫 보스 뒤 타이틀",
    panels: [
      {line: 0, beat: 5, heading: "본편 길 위에서 배우는 튜토리얼"},
      {line: 3, beat: 4, heading: "오디세이의 처음 몇 분, 네 단계"},
      {line: 4, beat: 2, heading: "내 게임의 첫 3분 점검"},
      {line: 5, beat: 3, heading: "기다리게 하지 말고, 먼저 놀게 해 주세요."},
    ],
  });
});
