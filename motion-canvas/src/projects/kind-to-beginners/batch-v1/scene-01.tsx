import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "01-02",
    "scene": "01",
    "purpose": "flow",
    "title": "다음 한 판을 스스로 고르게",
    "labels": [
      "직접 시도",
      "결과를 이해",
      "다음 선택"
    ],
    "frames": 301,
    "startFrame": 0,
    "endFrame": 301,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-01.jpg",
    "globalStartFrame": 720,
    "globalEndFrame": 1021,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "01-04",
    "scene": "01",
    "purpose": "flow",
    "title": "다음 한 판을 스스로 고르게",
    "labels": [
      "직접 시도",
      "결과를 이해",
      "다음 선택"
    ],
    "frames": 300,
    "startFrame": 301,
    "endFrame": 601,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-01.jpg",
    "globalStartFrame": 1560,
    "globalEndFrame": 1860,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
