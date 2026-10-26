import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "08-02",
    "scene": "08",
    "purpose": "interest",
    "title": "처음 생긴 작은 관심을 지킨다",
    "labels": [
      "첫 시도",
      "알아낸 결과",
      "다음 시도"
    ],
    "frames": 330,
    "startFrame": 8002,
    "endFrame": 8332,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 19558,
    "globalEndFrame": 19888,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "08-04",
    "scene": "08",
    "purpose": "summary",
    "title": "친절함의 목표는 스스로 즐기는 것",
    "labels": [
      "목표 합의",
      "입력 지원",
      "선택 돌려주기"
    ],
    "frames": 270,
    "startFrame": 8332,
    "endFrame": 8602,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 20518,
    "globalEndFrame": 20788,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
