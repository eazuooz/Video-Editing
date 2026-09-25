# 출처와 검증 범위

확인일: 2026-09-25.

## 주 자료

- 사용자가 작성하고 영상화를 요청한 `D:/OneDrive/문서/RenderFormer_v0.4_한글본문.pdf`.
- 88쪽, 960×540pt, 16:9. 모든 페이지의 텍스트를 추출하고 1200px 렌더 기반 11개 contact sheet로 화면을 확인했다.
- 영상은 페이지 순서를 모두 유지한다. 제공된 PDF는 수정하거나 공개 저장소로 복사하지 않았다.
- PDF 속 연구 그림·개념도와 사용자의 해설을 구분한다. 아래 논문의 저자/출처를 게시 설명란에 유지한다. 출처가 PDF 안에서 식별되지 않는 교육용 그림의 원 제작자는 추가 확인 대상으로 남긴다.

## 원 논문

- T1: Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017. [본문](https://arxiv.org/html/1706.03762v7).
- R1: Zeng, Dong, Peers, Wu, Tong, [RenderFormer: Transformer-based Neural Rendering of Triangle Meshes with Global Illumination](https://arxiv.org/abs/2505.21925), SIGGRAPH 2025. [v1 본문](https://arxiv.org/html/2505.21925v1). 이 영상의 연구 범위는 이 원 논문이며, 후속 V2/다른 이름의 연구 결과를 섞지 않는다.

## 공식 공개 코드

검토 커밋: `c51f87083d0eebb806803fe32a357b8d9aefb085`. 브랜치가 변해도 재확인할 수 있도록 고정 링크를 사용한다. 전체 모델을 실행하거나 논문의 벤치마크를 재현한 것은 아니며 코드 구조와 식을 읽어 검증했다. MIT 라이선스 코드의 구현과 원 논문의 기술 세부가 다른 곳은 별도로 표시했다.

- C1: [공식 저장소와 입력 조건](https://github.com/microsoft/renderformer/tree/c51f87083d0eebb806803fe32a357b8d9aefb085).
- C2: [models/config.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/models/config.py). 기본 768차원, 12+6층, 6헤드, 16 registers, RoPE, RMSNorm, SwiGLU, 13채널 32×32 패치.
- C3: [models/renderformer.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/models/renderformer.py). `tri_token`, `reg_tokens`, `construct_seq`의 RoPE/NeRF 분기, 위치·법선·재질 입력 구분.
- C4: [models/view_transformer.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/models/view_transformer.py) 및 [layers/attention.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/layers/attention.py). 레이 쿼리와 장면 K/V, Pre-Norm, 게이트 FFN, ELU 출력 경로.
- C5: [encodings/rope.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/encodings/rope.py). 회전 적용과 실제 텐서 차원.
- C6: [scene_processor/to_h5.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/scene_processor/to_h5.py). 13채널 순서, 32×32 반복과 삼각형 외부 마스크.
- C7: [pipelines/rendering_pipeline.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/pipelines/rendering_pipeline.py). 카메라 변환, 레이 생성, 기본 HDR의 log10 인코딩과 `10**output - 1` 디코딩.
- C8: [scene_processor/scene_mesh.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/scene_processor/scene_mesh.py). 선택적 메시 정규화 함수의 실제 분모 `2*max(norm(...))`.
- C9: [layers/dpt.py](https://github.com/microsoft/renderformer/blob/c51f87083d0eebb806803fe32a357b8d9aefb085/renderformer/layers/dpt.py). 다중 스케일 특징·융합·합성곱·보간.

## 연산 정의

- P1: [PyTorch LayerNorm](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.normalization.LayerNorm.html). `normalized_shape`에 해당하는 마지막 차원의 통계 사용.
- P2: [PyTorch RMSNorm](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.normalization.RMSNorm.html). RMS 기반 스케일 정규화.
- P3: [PyTorch GELU](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.activation.GELU.html). 결정론적인 `x * Φ(x)` 정의.

## 화면 사용 범위

이번 요청은 제공된 발표 페이지 중심의 긴 설명 영상이다. 외부 YouTube B-roll을 임의로 끼우지 않는다. 페이지별 독립 씬, 기존 목소리 방향, 별도 KO/EN SRT·무자막/한국어 자막판 관리 방식은 유지한다. 2026-09-25 사용자가 BGM 없음으로 선택했다. 이전 편의 Discovery 등을 사용하지 않는다. 이번 프리뷰에는 사용자 PDF 페이지, 자체 편집 가능한 강조·도식, 사용자 기준 목소리로 합성한 내레이션만 포함된다.
