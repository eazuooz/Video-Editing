import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "09-02",
    "scene": "09",
    "purpose": "comparison",
    "title": "같은 시간도 바라보는 쪽이 다르다",
    "labels": [
      "제작자의 분량",
      "플레이어의 삶",
      "그 시간을 쓸 이유"
    ],
    "frames": 398,
    "startFrame": 8554,
    "endFrame": 8952,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-09.jpg",
    "globalStartFrame": 21491,
    "globalEndFrame": 21889,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "09-04",
    "scene": "09",
    "purpose": "summary",
    "title": "그 시간을 쓰길 잘했다는 경험",
    "labels": [
      "재미를 먼저",
      "부담과 대기를 줄이기",
      "선택한 시간을 존중"
    ],
    "frames": 300,
    "startFrame": 8952,
    "endFrame": 9252,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-09.jpg",
    "globalStartFrame": 22451,
    "globalEndFrame": 22751,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
