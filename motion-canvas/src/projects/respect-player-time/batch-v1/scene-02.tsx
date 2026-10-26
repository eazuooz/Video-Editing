import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "02-01",
    "scene": "02",
    "purpose": "commitment",
    "title": "시작 전에 300시간을 약속한다면",
    "labels": [
      "가정한 분량: 300시간",
      "아직 재미는 모른다",
      "먼저 보이는 부담"
    ],
    "frames": 480,
    "startFrame": 545,
    "endFrame": 1025,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 1745,
    "globalEndFrame": 2225,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "02-03",
    "scene": "02",
    "purpose": "calendar",
    "title": "하루 1시간이면 300일",
    "labels": [
      "300시간 ÷ 하루 1시간",
      "매일 해도 300일",
      "설명용 가정"
    ],
    "frames": 480,
    "startFrame": 1025,
    "endFrame": 1505,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 2765,
    "globalEndFrame": 3245,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "02-05",
    "scene": "02",
    "purpose": "opportunity",
    "title": "기회비용 · 고르지 못한 다른 기회",
    "labels": [
      "다른 게임",
      "영화·휴식·친구",
      "같은 시간을 나눠 쓰기"
    ],
    "frames": 300,
    "startFrame": 1505,
    "endFrame": 1805,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 3785,
    "globalEndFrame": 4085,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
