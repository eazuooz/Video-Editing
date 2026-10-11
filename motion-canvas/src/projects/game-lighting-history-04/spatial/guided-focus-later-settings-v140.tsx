import {guidedSourceScene} from './guided-source-runtime-v140';
export default guidedSourceScene({
  "role": "focus-later-settings",
  "title": "흐림을 거리 영역으로 나누기",
  "frames": 1100,
  "sourceSha256": "9c24fd9899a798ef046e3ee3ccdd7ff857b2378d7790234ade066bd4ead5b2af",
  "boundSourceSha256": "9c24fd9899a798ef046e3ee3ccdd7ff857b2378d7790234ade066bd4ead5b2af",
  "wholeAndContextCompared": true,
  "stages": [
    {
      "fromFrame": 0,
      "toFrame": 208,
      "progressFrom": 0,
      "progressTo": 0.25,
      "anchor": "같은 상자 기준"
    },
    {
      "fromFrame": 226,
      "toFrame": 475,
      "progressFrom": 0.25,
      "progressTo": 0.52,
      "anchor": "가까운 면과 먼 면"
    },
    {
      "fromFrame": 488,
      "toFrame": 778,
      "progressFrom": 0.52,
      "progressTo": 0.75,
      "anchor": "달라진 거리 영역"
    },
    {
      "fromFrame": 794,
      "toFrame": 1098,
      "progressFrom": 0.75,
      "progressTo": 1,
      "anchor": "초점 기준과 앞뒤 위치"
    }
  ]
});
