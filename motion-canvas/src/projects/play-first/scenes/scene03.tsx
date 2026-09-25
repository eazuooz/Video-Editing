import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/broll/scene03.mp4';
import {playScene} from './play-scene';

export default makeScene2D(function* (view) {
  yield* playScene(view, {
    index: 2,
    chapter: "03 · 이야기",
    title: "이야기는 짧게, 한복판에서",
    clip,
    exampleLabel: "슈퍼 마리오 오디세이 — 싸움 한복판에서 시작하는 오프닝 (조작 전 영상)",
    panels: [
      {line: 0, beat: 1, heading: "사건 한복판에서 시작"},
      {line: 3, beat: 3, heading: "손에 잡히면 궁금해진다"},
      {line: 4, beat: 4, heading: "이야기는 그대로, 조작은 앞으로"},
    ],
  });
});
