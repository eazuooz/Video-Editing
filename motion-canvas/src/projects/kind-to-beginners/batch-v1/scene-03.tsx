import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "03-02",
    "scene": "03",
    "purpose": "goal",
    "title": "전력 승부는 서로 원할 때",
    "labels": [
      "승부 방식 합의",
      "할 수 있는 행동",
      "배울 수 있는 결과"
    ],
    "frames": 300,
    "startFrame": 2004,
    "endFrame": 2304,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 5462,
    "globalEndFrame": 5762,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "03-04",
    "scene": "03",
    "purpose": "goal",
    "title": "전력 승부는 서로 원할 때",
    "labels": [
      "승부 방식 합의",
      "할 수 있는 행동",
      "배울 수 있는 결과"
    ],
    "frames": 420,
    "startFrame": 2304,
    "endFrame": 2724,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 6242,
    "globalEndFrame": 6662,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1
  },
  {
    "id": "03-06",
    "scene": "03",
    "purpose": "feedback",
    "title": "내 조작과 결과를 연결하기",
    "labels": [
      "방어를 알려주기",
      "한 번 막아보기",
      "다음 행동 선택"
    ],
    "frames": 300,
    "startFrame": 2724,
    "endFrame": 3024,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-03.jpg",
    "globalStartFrame": 7202,
    "globalEndFrame": 7502,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
