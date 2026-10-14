import {narratedScene04} from './narrated-runtime-v1';
export default narratedScene04({
  "id": "4편 · 18v",
  "model": "vsm",
  "frames": 880,
  "currentAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "boundAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "allWholeAndIndependentContextTextCompared": true,
  "captionWordTimesDirectlyReviewed": true,
  "paragraphs": [
    {
      "fromFrame": 0,
      "toFrame": 880,
      "mode": 2,
      "title": "가상 그림자 맵: 필요한 페이지에 깊이를 저장하기",
      "stages": [
        {
          "fromFrame": 9,
          "toFrame": 317,
          "progressFrom": 0,
          "progressTo": 0.15,
          "anchor": "언리얼 엔진의 가상 그림자 맵은 큰 가상 주소 공간을 작은 페이지로 나눕니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 330,
          "toFrame": 629,
          "progressFrom": 0.15,
          "progressTo": 1,
          "anchor": "실제 화면에 필요한 페이지를 찾아 물리 메모리에 배정하고, 그 부분의 깊이를 그립니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 644,
          "toFrame": 870,
          "progressFrom": 1,
          "progressTo": 1,
          "anchor": "주소 공간의 크기와 실제로 배정된 메모리 크기를 구별해야 합니다.",
          "wordTimesDirectlyReviewed": true
        }
      ]
    }
  ],
  "cues": [
    {
      "fromFrame": 9,
      "toFrame": 317,
      "text": "언리얼 엔진의 가상 그림자 맵은 큰 가상\n주소 공간을 작은 페이지로 나눕니다."
    },
    {
      "fromFrame": 330,
      "toFrame": 629,
      "text": "실제 화면에 필요한 페이지를 찾아 물리\n메모리에 배정하고, 그 부분의 깊이를 그립니다."
    },
    {
      "fromFrame": 644,
      "toFrame": 870,
      "text": "주소 공간의 크기와 실제로 배정된\n메모리 크기를 구별해야 합니다."
    }
  ]
});
