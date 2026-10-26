import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "07-02",
    "scene": "07",
    "purpose": "instructions",
    "title": "모든 지시를 주면, 선택이 줄어든다",
    "labels": [
      "다음 버튼",
      "다음 길",
      "남이 정한 순서"
    ],
    "frames": 480,
    "startFrame": 6862,
    "endFrame": 7342,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-07.jpg",
    "globalStartFrame": 16393,
    "globalEndFrame": 16873,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "07-04",
    "scene": "07",
    "purpose": "route",
    "title": "스스로 가보고 싶은 길",
    "labels": [
      "지금 보이는 장소",
      "내가 고른 방향",
      "직접 확인한 결과"
    ],
    "frames": 360,
    "startFrame": 7342,
    "endFrame": 7702,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-07.jpg",
    "globalStartFrame": 17413,
    "globalEndFrame": 17773,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "07-06",
    "scene": "07",
    "purpose": "choice",
    "title": "필요한 정보 뒤에 선택을 돌려준다",
    "labels": [
      "조작·규칙 안내",
      "한 걸음 물러서기",
      "본인이 다음 행동"
    ],
    "frames": 300,
    "startFrame": 7702,
    "endFrame": 8002,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-07.jpg",
    "globalStartFrame": 18313,
    "globalEndFrame": 18613,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
