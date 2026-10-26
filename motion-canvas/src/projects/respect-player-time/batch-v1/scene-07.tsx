import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "07-03",
    "scene": "07",
    "purpose": "action-loop",
    "title": "선택 → 행동 → 확인",
    "labels": [
      "물건을 본다",
      "놓을 곳을 고른다",
      "방의 변화를 확인"
    ],
    "frames": 300,
    "startFrame": 5497,
    "endFrame": 5797,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-07.jpg",
    "globalStartFrame": 16119,
    "globalEndFrame": 16419,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
