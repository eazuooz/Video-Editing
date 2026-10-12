import {narratedScene04} from './narrated-runtime-v2';
export default narratedScene04({
  "id": "4편 · 20",
  "model": "reconstruction",
  "frames": 807,
  "currentAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "boundAudioSha256": "5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd",
  "allWholeAndIndependentContextTextCompared": true,
  "captionWordTimesDirectlyReviewed": true,
  "paragraphs": [
    {
      "fromFrame": 0,
      "toFrame": 807,
      "mode": 0,
      "title": "레이 재구성: 노이즈 제거와 업스케일링의 역할",
      "stages": [
        {
          "fromFrame": 0,
          "toFrame": 192,
          "progressFrom": 0,
          "progressTo": 0,
          "anchor": "표본이 적은 레이 결과에는 노이즈가 남습니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 209,
          "toFrame": 522,
          "progressFrom": 0,
          "progressTo": 0.5,
          "anchor": "디노이저는 이 노이즈를 줄이면서 경계와 재질의 변화, 반사 세부를 보존하려 합니다.",
          "wordTimesDirectlyReviewed": true
        },
        {
          "fromFrame": 538,
          "toFrame": 803,
          "progressFrom": 0.5,
          "progressTo": 1,
          "anchor": "단순히 주변 색을 평균 내면 노이즈뿐 아니라 진짜 세부도 사라집니다.",
          "wordTimesDirectlyReviewed": true
        }
      ]
    }
  ],
  "cues": [
    {
      "fromFrame": 0,
      "toFrame": 192,
      "text": "표본이 적은 레이 결과에는 노이즈가 남습니다."
    },
    {
      "fromFrame": 209,
      "toFrame": 522,
      "text": "디노이저는 이 노이즈를 줄이면서 경계와\n재질의 변화, 반사 세부를 보존하려 합니다."
    },
    {
      "fromFrame": 538,
      "toFrame": 803,
      "text": "단순히 주변 색을 평균 내면 노이즈뿐\n아니라 진짜 세부도 사라집니다."
    }
  ],
  "renderCaptions": false
});
