import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "03-02",
    "scene": "03",
    "purpose": "return",
    "title": "재미있어서 고르는 다음 한 판",
    "labels": [
      "한 판의 재미",
      "자발적인 다음 선택",
      "뒤따라 쌓인 시간"
    ],
    "frames": 300,
    "startFrame": 1805,
    "endFrame": 2105,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 4826,
    "globalEndFrame": 5126,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "03-04",
    "scene": "03",
    "purpose": "damage",
    "title": "누적 피해 퍼센트 · 점수와 다르다",
    "labels": [
      "공격을 받는다",
      "피해가 쌓인다",
      "더 멀리 날아가기 쉬워진다"
    ],
    "frames": 360,
    "startFrame": 2105,
    "endFrame": 2465,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 5666,
    "globalEndFrame": 6026,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "03-06",
    "scene": "03",
    "purpose": "result",
    "title": "재미 → 다음 선택 → 플레이 시간",
    "labels": [
      "재미가 이유",
      "계속은 선택",
      "시간은 결과"
    ],
    "frames": 240,
    "startFrame": 2465,
    "endFrame": 2705,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 6566,
    "globalEndFrame": 6806,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
