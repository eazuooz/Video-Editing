import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "05-01",
    "scene": "05",
    "purpose": "steering",
    "title": "Smart Steering · 핸들 어시스트",
    "labels": [
      "코스를 벗어나려 할 때",
      "방향 조절 지원",
      "뒤쪽 안테나로 확인"
    ],
    "frames": 522,
    "startFrame": 4217,
    "endFrame": 4739,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/sources/mk8-official-035.jpg",
    "globalStartFrame": 10539,
    "globalEndFrame": 11061,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "05-02",
    "scene": "05",
    "purpose": "acceleration",
    "title": "Auto-Accelerate · 가속 유지",
    "labels": [
      "가속 버튼 유지 부담 ↓",
      "코너·아이템을 볼 여유 ↑",
      "필요한 보조만 선택"
    ],
    "frames": 486,
    "startFrame": 4739,
    "endFrame": 5225,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/sources/mk8-official-034.jpg",
    "globalStartFrame": 11061,
    "globalEndFrame": 11547,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  },
  {
    "id": "05-04",
    "scene": "05",
    "purpose": "turbo",
    "title": "익숙해지면 더 정교하게",
    "labels": [
      "미니 터보",
      "슈퍼 미니 터보",
      "울트라: 보조를 끈 뒤"
    ],
    "frames": 480,
    "startFrame": 5225,
    "endFrame": 5705,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/kind-to-beginners/batch-v1/diagram-assets/scene-05.jpg",
    "globalStartFrame": 12327,
    "globalEndFrame": 12807,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
