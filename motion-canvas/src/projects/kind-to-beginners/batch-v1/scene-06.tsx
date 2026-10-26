import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "06-02",
    "scene": "06",
    "purpose": "distance",
    "title": "Dynamic · 입력과 판단을 나누기",
    "labels": [
      "버튼 입력",
      "상대와의 거리",
      "상황에 맞는 공격"
    ],
    "frames": 318,
    "startFrame": 5705,
    "endFrame": 6023,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-06.jpg",
    "globalStartFrame": 13904,
    "globalEndFrame": 14222,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "06-04",
    "scene": "06",
    "purpose": "offline",
    "title": "오프라인의 일부 모드에서",
    "labels": [
      "Dynamic controls",
      "Fighting Ground",
      "첫 흐름을 경험하는 선택지"
    ],
    "frames": 360,
    "startFrame": 6023,
    "endFrame": 6383,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-06.jpg",
    "globalStartFrame": 14714,
    "globalEndFrame": 15074,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "06-06",
    "scene": "06",
    "purpose": "handoff",
    "title": "입력 부담을 덜고, 선택을 남긴다",
    "labels": [
      "대신할 입력",
      "직접 해볼 판단",
      "도움을 멈출 때"
    ],
    "frames": 479,
    "startFrame": 6383,
    "endFrame": 6862,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-06.jpg",
    "globalStartFrame": 15554,
    "globalEndFrame": 16033,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
