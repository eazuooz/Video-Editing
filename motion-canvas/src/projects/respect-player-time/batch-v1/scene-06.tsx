import {type View2D} from '@motion-canvas/2d';
import {explain,type Cue} from './visuals';
const cues: Cue[]=[
  {
    "id": "06-01",
    "scene": "06",
    "purpose": "phone",
    "title": "손 닿는 곳의 낮은 시작 문턱",
    "labels": [
      "짧은 글",
      "사진과 영상",
      "바로 시작할 선택지"
    ],
    "frames": 840,
    "startFrame": 4117,
    "endFrame": 4957,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-06.jpg",
    "globalStartFrame": 11988,
    "globalEndFrame": 12828,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  },
  {
    "id": "06-03",
    "scene": "06",
    "purpose": "barriers",
    "title": "게임이 요구하는 준비를 살핀다",
    "labels": [
      "시간 확보",
      "플레이 환경",
      "집중과 기억"
    ],
    "frames": 540,
    "startFrame": 4957,
    "endFrame": 5497,
    "sourceImage": "/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/respect-player-time/batch-v1/diagram-assets/scene-06.jpg",
    "globalStartFrame": 13668,
    "globalEndFrame": 14208,
    "pictureKind": "게임 스크린샷 + 원리 도식",
    "variant": 0,
    "metrics": null
  }
];
export function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }
