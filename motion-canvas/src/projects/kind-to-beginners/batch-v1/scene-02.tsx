import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "02-01",
    "scene": "02",
    "purpose": "arcade",
    "title": "화면 너머의 사람은 보이지 않는다",
    "labels": [
      "공격은 보인다",
      "기대는 숨겨져 있다",
      "의도를 먼저 읽기"
    ],
    "frames": 360,
    "startFrame": 601,
    "endFrame": 961,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 2079,
    "globalEndFrame": 2439,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "02-03",
    "scene": "02",
    "purpose": "intent",
    "title": "같은 경기, 서로 다른 목적",
    "labels": [
      "진지한 승부",
      "가벼운 첫 시도",
      "목표 확인"
    ],
    "frames": 360,
    "startFrame": 961,
    "endFrame": 1321,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 2979,
    "globalEndFrame": 3339,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "02-05",
    "scene": "02",
    "purpose": "intent",
    "title": "같은 경기, 서로 다른 목적",
    "labels": [
      "진지한 승부",
      "가벼운 첫 시도",
      "목표 확인"
    ],
    "frames": 300,
    "startFrame": 1321,
    "endFrame": 1621,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 3759,
    "globalEndFrame": 4059,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1
  },
  {
    "id": "02-07",
    "scene": "02",
    "purpose": "intent",
    "title": "같은 경기, 서로 다른 목적",
    "labels": [
      "진지한 승부",
      "가벼운 첫 시도",
      "목표 확인"
    ],
    "frames": 383,
    "startFrame": 1621,
    "endFrame": 2004,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-02.jpg",
    "globalStartFrame": 4659,
    "globalEndFrame": 5042,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 2
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
