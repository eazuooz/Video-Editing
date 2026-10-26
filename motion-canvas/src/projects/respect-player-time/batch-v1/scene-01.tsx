import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "01-02",
    "scene": "01",
    "purpose": "thesis",
    "title": "시간이 쌓이는 순서를 보자",
    "labels": [
      "직접 행동",
      "재미를 확인",
      "다음 시도"
    ],
    "frames": 300,
    "startFrame": 0,
    "endFrame": 300,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-01.jpg",
    "globalStartFrame": 660,
    "globalEndFrame": 960,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "01-04",
    "scene": "01",
    "purpose": "thesis",
    "title": "시간이 쌓이는 순서를 보자",
    "labels": [
      "직접 행동",
      "재미를 확인",
      "다음 시도"
    ],
    "frames": 245,
    "startFrame": 300,
    "endFrame": 545,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-01.jpg",
    "globalStartFrame": 1500,
    "globalEndFrame": 1745,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
