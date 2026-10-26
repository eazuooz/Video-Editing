import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "04-02",
    "scene": "04",
    "purpose": "onboarding",
    "title": "온보딩 · 첫 재미까지 가는 길",
    "labels": [
      "버튼을 안다",
      "하나를 해본다",
      "결과를 느낀다"
    ],
    "frames": 420,
    "startFrame": 3024,
    "endFrame": 3444,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-04.jpg",
    "globalStartFrame": 8266,
    "globalEndFrame": 8686,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "04-04",
    "scene": "04",
    "purpose": "onboarding",
    "title": "온보딩 · 첫 재미까지 가는 길",
    "labels": [
      "버튼을 안다",
      "하나를 해본다",
      "결과를 느낀다"
    ],
    "frames": 360,
    "startFrame": 3444,
    "endFrame": 3804,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-04.jpg",
    "globalStartFrame": 9226,
    "globalEndFrame": 9586,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 1
  },
  {
    "id": "04-06",
    "scene": "04",
    "purpose": "burden",
    "title": "한꺼번에 요구하는 입력을 나눈다",
    "labels": [
      "방향 조절",
      "가속 유지",
      "아이템 선택"
    ],
    "frames": 413,
    "startFrame": 3804,
    "endFrame": 4217,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-04.jpg",
    "globalStartFrame": 10126,
    "globalEndFrame": 10539,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
