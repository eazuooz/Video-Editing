import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "04-02",
    "scene": "04",
    "purpose": "cost",
    "title": "시작 전의 시간은 비용",
    "labels": [
      "돈과 함께 쓰는 시간",
      "돌아오지 않는 오늘",
      "그 시간의 가치"
    ],
    "frames": 240,
    "startFrame": 2705,
    "endFrame": 2945,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-04.jpg",
    "globalStartFrame": 7566,
    "globalEndFrame": 7806,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "04-04",
    "scene": "04",
    "purpose": "alternatives",
    "title": "경쟁 상대는 여가 전체에 있다",
    "labels": [
      "게임 한 판",
      "영상·휴식",
      "오늘 저녁 1시간"
    ],
    "frames": 240,
    "startFrame": 2945,
    "endFrame": 3185,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-04.jpg",
    "globalStartFrame": 8526,
    "globalEndFrame": 8766,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
