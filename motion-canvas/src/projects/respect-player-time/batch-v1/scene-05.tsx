import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "05-02",
    "scene": "05",
    "purpose": "choice",
    "title": "남는 시간에도 선택지는 많다",
    "labels": [
      "대전의 즐거움",
      "청소의 즐거움",
      "내가 원하는 집중"
    ],
    "frames": 360,
    "startFrame": 3185,
    "endFrame": 3545,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-05.jpg",
    "globalStartFrame": 10036,
    "globalEndFrame": 10396,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "05-04",
    "scene": "05",
    "purpose": "wash",
    "title": "내 행동이 표면을 바꾼다",
    "labels": [
      "물줄기를 움직인다",
      "지나간 때가 사라진다",
      "깨끗한 면이 드러난다"
    ],
    "frames": 300,
    "startFrame": 3545,
    "endFrame": 3845,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-05.jpg",
    "globalStartFrame": 10936,
    "globalEndFrame": 11236,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "05-06",
    "scene": "05",
    "purpose": "cost",
    "title": "시작 전의 시간은 비용",
    "labels": [
      "돈과 함께 쓰는 시간",
      "돌아오지 않는 오늘",
      "그 시간의 가치"
    ],
    "frames": 272,
    "startFrame": 3845,
    "endFrame": 4117,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-05.jpg",
    "globalStartFrame": 11716,
    "globalEndFrame": 11988,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
