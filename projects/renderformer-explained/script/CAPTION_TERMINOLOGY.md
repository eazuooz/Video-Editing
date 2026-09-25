# 논문 용어 자막 표기

사용자 요청(2026-09-25): 한국어로 읽더라도 기술 명칭은 통상적인 영문 철자·약어로 표시한다.

- 활성화: `ReLU`, `GELU`, `SwiGLU`.
- 피드포워드 네트워크: `FFN` (영어 자막 첫 등장에서는 풀네임 병기).
- 어텐션: `Attention`, `Self-Attention`, `Cross-Attention`, `Multi-Head Attention`.
- 정규화·위치: `LayerNorm`, `RMSNorm`, `BatchNorm`, `Pre-Norm`, `RoPE`.
- 기호·명칭: `Q`, `K`, `V`, `Transformer`, `RenderFormer`, `BERT`, `tri_token`.
- 디코더·출력·지표: `DPT`, `HDR`, `PSNR`, `SSIM`, `LPIPS`, `FLIP`.

일반적인 설명은 한국어로 유지한다. 원본 PDF와 승인된 TTS 발화 대본은 변경하지 않는다.
`caption-terms.ko.json`이 표시 전용 변환 기준이며 `production/apply_caption_terms.py`로 적용한다.
변환 전 발화는 각 cue의 `spokenKo`에 보존한다. 기존 cue 번호·시작·종료·페이지 길이를 유지하며,
`FFN이`, `FFN은`, `FFN을`처럼 영문 약어 뒤 조사도 확인한다.

재생성 순서: 실측 타이밍/ASR 보정 완료 → 표시 용어 적용 → 영어 SRT 생성 → 자막판 합성.
현재 승인된 타이밍을 변경하는 ASR 정렬기를 단순 자막 표기 수정 때문에 다시 실행하지 않는다.
무자막 영상·WAV·AAC는 재생성하지 않고 자막판의 오디오는 무자막판에서 패킷 복사한다.
