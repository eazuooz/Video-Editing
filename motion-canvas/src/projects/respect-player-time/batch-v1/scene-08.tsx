import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "08-01",
    "scene": "08",
    "purpose": "timeline-before",
    "title": "설명용 시간표 · 직접 조작과 대기",
    "labels": [
      "40 ÷ 60 = 2/3",
      "조작 40초",
      "대기 20초"
    ],
    "frames": 1008,
    "startFrame": 5797,
    "endFrame": 6805,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 17216,
    "globalEndFrame": 18224,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": {
      "control": 40,
      "wait": 20,
      "total": 60,
      "share": "2/3"
    },
    "stageCueTimes": [
      8.2,
      10.9,
      14.8
    ]
  },
  {
    "id": "08-02",
    "scene": "08",
    "purpose": "timeline-after",
    "title": "같은 놀이에서 불필요한 대기만 줄이기",
    "labels": [
      "40 ÷ 50 = 80%",
      "조작 40초 유지",
      "대기 20초 → 10초"
    ],
    "frames": 954,
    "startFrame": 6805,
    "endFrame": 7759,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 18224,
    "globalEndFrame": 19178,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": {
      "control": 40,
      "wait": 10,
      "total": 50,
      "share": "80%"
    },
    "stageCueTimes": [
      0,
      3.5,
      9.1
    ]
  },
  {
    "id": "08-04",
    "scene": "08",
    "purpose": "menu-control",
    "title": "메뉴의 의미 있는 선택도 조작이다",
    "labels": [
      "할 수 있는 선택",
      "입력에 대한 반응",
      "직접 개입하는 시간"
    ],
    "frames": 360,
    "startFrame": 7759,
    "endFrame": 8119,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 19616,
    "globalEndFrame": 19976,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "08-06",
    "scene": "08",
    "purpose": "waiting",
    "title": "재미를 돕는 시간과 쓸모없는 대기",
    "labels": [
      "의미 있는 연출",
      "불필요한 전환 줄이기",
      "기다리는 중의 선택"
    ],
    "frames": 435,
    "startFrame": 8119,
    "endFrame": 8554,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-08.jpg",
    "globalStartFrame": 20516,
    "globalEndFrame": 20951,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
