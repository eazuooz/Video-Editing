import {narratedScene04} from './narrated-runtime-v2';
export default narratedScene04({
  "id": "4편 · 18v",
  "model": "vsm",
  "frames": 829,
  "currentAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "boundAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "allWholeAndIndependentContextTextCompared": true,
  "captionWordTimesDirectlyReviewed": true,
  "paragraphs": [
    {
      "fromFrame": 0,
      "toFrame": 829,
      "mode": 4,
      "title": "가상 그림자 맵: 필요한 페이지에 깊이를 저장하기",
      "stages": [
        {
          "fromFrame": 7,
          "toFrame": 209,
          "progressFrom": 0,
          "progressTo": 0.35,
          "anchor": "카메라가 움직여 새로운 부분을 보면 다른 페이지가 필요해집니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 219,
          "toFrame": 512,
          "progressFrom": 0.35,
          "progressTo": 0.7,
          "anchor": "광원과 물체가 그대로라면 이미 계산한 페이지를 캐시에 남겨 재사용할 수 있습니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 531,
          "toFrame": 818,
          "progressFrom": 0.7,
          "progressTo": 1,
          "anchor": "광원이 움직이거나 그림자를 만드는 물체가 바뀌면 관련 페이지를 다시 계산해야 합니다.",
          "wordTimesDirectlyReviewed": true
        }
      ]
    }
  ],
  "cues": [
    {
      "fromFrame": 7,
      "toFrame": 209,
      "text": "카메라가 움직여 새로운 부분을\n보면 다른 페이지가 필요해집니다."
    },
    {
      "fromFrame": 219,
      "toFrame": 512,
      "text": "광원과 물체가 그대로라면 이미 계산한\n페이지를 캐시에 남겨 재사용할 수 있습니다."
    },
    {
      "fromFrame": 531,
      "toFrame": 818,
      "text": "광원이 움직이거나 그림자를 만드는 물체가\n바뀌면 관련 페이지를 다시 계산해야 합니다."
    }
  ],
  "renderCaptions": false
});
