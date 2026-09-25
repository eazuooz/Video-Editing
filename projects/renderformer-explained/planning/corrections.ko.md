# 원본 슬라이드 보완·교체표

검토일: 2026-09-25. 대상: 사용자가 작성한 `RenderFormer_v0.4_한글본문.pdf` 88쪽.

사용자 승인: “보완내용은 너가 따로 수정해서 작업해도 좋아 확인해보고”. 아래 보완은 내레이션에 반영했다. PDF 원본을 덮어쓰지 않는다. 2026-09-25 본편 제작 승인 후 `production/slide-overlays.json`과 Motion Canvas `full/slide.tsx`로 영상용 문구·도표를 교체했다. 원본 페이지 순서·주요 그림은 유지한다. **88페이지 화면 검수본은 렌더했으며 전체 음성·최종 게시 영상은 제작 중이다.**

기준 자료는 [출처 문서](../sources/SOURCES.md)의 T1, R1, C1~C9, P1~P3이다. 원 논문의 Base 설명과 공개 코드의 입력·출력 경로를 분리한다. 다른 버전의 모델 설정까지 동일하다고 일반화하지 않는다.

## 필수 내용 수정

| 페이지 | 원문 또는 문제 | 영상용 교체 문구·도식 | 확인 근거 |
|---|---|---|---|
| 3 | ‘오직 어텐션’이 FFN까지 없다는 의미로 읽힐 수 있음 | ‘토큰 간 관계 처리를 어텐션 중심으로 구성. 선형층·FFN·정규화도 포함.’ | T1 §3 |
| 4 | 동일한 층 6개를 동일 가중치로 오해 가능 | ‘구조가 같은 층 6개. 층별 파라미터는 별도.’ | T1 §3.1 |
| 6 | “How are you” → “I am changed” 오기, 디코더 입력/정답 혼동 | ‘예제 답변: I am fine / Encoder: [5,8,9] / Decoder input: [SOS,I,am]=[0,6,3] / Target: [I,am,fine]=[6,3,4]’ | PDF p5·32·44, T1 shifted-right |
| 8 | 11개 단어를 하나의 6차원 벡터로 압축하는 듯한 표현 | ‘어휘 크기 11, 토큰별 임베딩 차원 6. 길이 3 입력의 출력: [3,6].’ | T1 embedding; 표의 shape |
| 10 | 짝수·홀수 판정 기준 i 표현 혼동 | ‘짝수 특징 차원 2i: sin, 홀수 특징 차원 2i+1: cos.’ | T1 §3.5 |
| 15 | 학습 후 완전한 최적화·모든 문장 관계를 정확히 파악 | ‘손실을 줄이는 유용한 표현을 학습. 문맥 파악의 완벽함은 보장되지 않음.’ | 학습 목표와 정확도 보장의 구분 |
| 19 | √dk를 거리로 설명 | ‘dk는 헤드의 키 특징 차원. 점수의 스케일 조절.’ | T1 eq.1 |
| 20 | ‘단어 간 상관 확률’, ‘인코더에는 마스크 없음’ | ‘행별 합이 1인 학습된 정보 결합 가중치. 인코더에는 인과 마스크가 없지만 패딩 마스크는 가능.’ | T1 attention, padding vs causal 구분 |
| 21 | 가중치 행렬과 최종 어텐션 출력을 혼동할 여지 | ‘Attention weights × V = context-aware output features’ | T1 eq.1 |
| 26·72 | 잔차 연결이 정보 손실·기울기 소실을 완전히 방지한다고 단정 | ‘입력에 변화량을 더하는 직접 경로. 깊은 모델의 학습과 정보 흐름을 도움.’ | residual 식 X+F(X); 절대 보장 삭제 |
| 27 | 각 열의 평균/표준편차라고 서술 | ‘토큰별 특징 차원에서 정규화. 이 도표에서는 한 행의 통계 사용. γ, β, ε 포함.’ | P1 |
| 31 | 인코더 한 층 출력과 전체 인코더 최종 출력의 혼동 | ‘한 인코더 블록의 출력. N개 층을 지나 최종 인코더 출력 구성.’ | T1 §3.1 |
| 35~39 | 미래 토큰을 볼 ‘필요가 없다’로 약하게 설명 | ‘학습에서 미래 정답 유출을 막는 인과 제약. shifted-right 입력과 함께 사용.’ | T1 decoder masking |
| 46 | 전처리 전혀 없음 / 모든 GI 정확성 보장 / NeRF 전체를 단일화 | ‘메시·재질·광원·카메라 입력. 장면별 추가 학습 없이 추론. 입력 변환은 필요하며 GI는 학습된 예측.’ | R1, C1, C7 |
| 47 | RenderFormer 흐름 페이지에 NeRF 설명만 기재 | ‘Triangle sequence → scene features → ray-bundle sequence → image patches. NeRF는 입력·학습 방식 비교로 한정.’ | R1, C1 |
| 48 | 도식 영역이 비어 있음 | 기존 빈 영역 안에 ‘Mesh + Material + Light → Triangle Tokens → Scene Features → Camera Ray Tokens → Image’ 편집 가능 텍스트 도식 추가 | 원본 전체 페이지 시각 확인; 앞뒤 문맥 보충 |
| 49·74·76 | 12층을 직접광→간접광의 물리적 반사 횟수로 해석 | ‘Base: 시점 독립 12층, 시점 의존 6층. 층 수 ≠ 광선 반사 횟수.’ | R1, C2 |
| 50·55·56 | 위치가 항상 tri_emb에 더해지는 듯한 설명 | 기본 `pe_type='rope'`: `tri_emb = tri_token + tri_tex_emb + vn_emb`; 좌표는 어텐션의 Q/K 회전에 사용 | C2, C3 construct_seq |
| 51 | ‘5,696개 삼각형 정점’으로 개수 단위 혼재 | ‘메시의 각 삼각형: 꼭짓점 3개 + 꼭짓점 법선.’ 5,696은 실제 메시 파일 확인 전 삭제 | 원본 메시 파일 미제공; triangle/vertex 구분 |
| 52 | 13개 재질 수치를 반복하는 목적을 W 파라미터 증대라고 단정 | ‘공개 코드: 13채널 32×32 패치. diffuse3+specular3+roughness1+normal3+emission3. 단색은 반복, 삼각형 외부는 마스크. 패치 입력 형식과 호환.’ | C2, C6 save_to_h5 |
| 52 | 논문의 10D와 코드의 13채널 혼용 | ‘원 논문 10D 반사·발광 속성 / 공개 코드 normal-map 포함 13채널 패치’ 표기 | R1 §3.1, C2·C6 |
| 53·54 | RMSNorm이 모든 크기 차이를 없애고 방향만 비교하게 보장 | ‘RMS 기반 특징 스케일 조절. 평균 제거 없음. ε와 학습 scale 포함.’ | P2, C3 |
| 54 | 법선 임베딩 페이지에 재질 설명 반복; 표 라벨이 position처럼 보임 | ‘세 꼭짓점 법선 [9] → 주파수 인코딩 → projection → RMSNorm.’ 법선과 위치를 다른 입력으로 명시 | C3 use_vn_encoder |
| 55·57 | tri_token을 의미가 확정된 타입 라벨로 단정 | ‘모든 삼각형에 공유하는 학습 가능한 오프셋. 타입 정보로 해석할 수 있으나 차원별 의미는 미확정.’ | C3 nn.Parameter와 broadcast |
| 56 | NeRF-PE 분기 식을 기본 모델 식으로 제시 | RoPE/NeRF-PE 두 분기 표로 교체. NeRF-PE 쪽에만 normalized position projection 추가 | C3 construct_seq |
| 58 | zeros/ones로 시작하면 모든 gradient 동일, 768차원도 1차원 | 아래 ‘초기화 교체 표’로 전체 표 교체. 이 주장은 공유 벡터에 일반적으로 성립하지 않음 | C3는 randn 선택만 입증. 아래 수학적 반례 |
| 59 | 각 차원에 고정된 물리·기능 의미 부여 | ‘특징은 여러 차원에 분산될 수 있음. dim 12/47/203 역할은 검증된 분석이 아님.’ 예시 차원 역할 목록 삭제 | C3에서 해당 의미를 정의하지 않음 |
| 60 | BERT도 똑같이 torch.randn을 사용하는 듯한 표 | 공통 적용 방식과 학습 가능성만 비교. 초기화 코드 동일성 행 삭제 | 비유 범위 제한; BERT 구현별 차이 |
| 61 | reg_tokens + tri_emb가 덧셈으로 보임; register를 type embedding과 혼동 | `seq = concat(reg_tokens, tri_emb, token_axis)` / [B,16+N,768]. 공유 tri_token과 register sequence 구분 | C3 torch.cat |
| 63 | 최대 반지름으로 나눠 반지름 1로 만든다고 설명 | 코드 해당 함수: `v'=(v-mean(v))/(2*max(norm(v-mean(v))))`; 최대 반지름 0.5. 물체 transform normalize 옵션임을 표시 | C8 normalize_to_unit_sphere 실제 식 |
| 64 | register 없으면 전역 소통 불가; 하나의 완전한 전역 요약 | ‘삼각형도 전역 self-attention. 16개 register는 전역 정보 처리에 사용할 보조 토큰이며 완전 요약 보장 아님.’ | R1, C3 |
| 65·66 | 다중 주파수가 없으면 공간이 1차원이 된다고 설명 | ‘좌표를 여러 공간 스케일로 표현. 원시 좌표 사용이 곧 1차원 인식을 뜻하지 않음.’ | 입력은 여전히 9D; R1 RoPE |
| 66 | 설정 필드 개수와 실제 유효 회전 쌍 혼용 | 원 논문 Base 예시 9×6×2=108, head_dim=128, 나머지 20. 코드 config 숫자만 보고 주파수 수를 단정하지 않음 | R1, C5 |
| 67 | sin/cos를 쓰면 모든 토큰 크기가 같아진다고 오해 가능 | ‘회전은 해당 벡터 성분쌍의 길이를 보존. 서로 다른 벡터를 동일 길이로 정규화하는 연산은 아님.’ | 회전행렬 성질, C5 |
| 69·70 | 어텐션 점수=물리적 영향량; 가깝고 재질 같으면 반드시 큰 가중치 | ‘내용과 공간 위치가 함께 반영된 학습 가중치. 거리·재질 유사도만으로 순위가 정해지지 않음.’ | C4·C5 attention 연산 |
| 71 | K 회전식에 Q가 들어간 오기 | `Q'=Q*cosθQ+rotate(Q)*sinθQ`, `K'=K*cosθK+rotate(K)*sinθK`; 실제 성분 pairing은 구현과 일치시킴 | C5 |
| 73·76 | RenderFormer에 Post-LayerNorm을 그대로 적용, N(0,1)로 만든다고 설명 | ‘기본 RMSNorm / Pre-Norm. X + Attention(RMSNorm(X)), 이후 X + FFN(RMSNorm(X))의 개념도.’ | C2·C4; P1·P2 |
| 75 | 실제 RenderFormer FFN을 GELU로 설명, 확률적으로 음수 통과 | ‘기본 활성화 SwiGLU. 두 투영 경로 중 하나에 SiLU, 원소별 곱, 출력 투영.’ GELU 보충은 결정론적 `xΦ(x)`로 한정 | C2·C4 FeedForwardSwiGLU, P3 |
| 77·78 | ray 입력을 실제 ray-tracing 수행으로 오해 | ‘카메라 방향을 나타내는 ray bundle. 교차/바운스를 직접 추적하는 고정 알고리즘이 아님.’ | C7 ray generation, C4 cross attention |
| 78 | triangle/ray를 하나의 sequence로 무조건 통합 | ‘ray sequence가 Q, 장면 sequence가 K/V가 되어 cross-attention으로 연결.’ | C4 |
| 79 | 정확한 교차 삼각형을 찾는다 / 픽셀 연속성과 블로킹 제거 보장 | ‘학습된 가시성·외관 관련 특징 조회. ray self-attention은 품질 개선을 돕지만 artifact 제거 보장 없음.’ | R1, C4 |
| 80 | 삼각형 토큰에서 최종 색을 바로 꺼낸다고 설명 | ‘V는 학습된 장면 특징. 후속 transformer와 decoder를 거쳐 픽셀 값으로 변환.’ | C4, C7 |
| 81 | cross-attention 출력에 camera 정보 전혀 없음, residual 없으면 반드시 붕괴 | ‘출력도 Q의 영향을 받음. residual은 원래 ray 표현과 새 특징을 함께 활용하고 학습을 도움.’ | C4 |
| 83·85 | HDR을 sigmoid나 tone mapping의 대안 중 하나로 생성한다고 설명 | ‘기본 HDR 모델: log-encoded output → inverse log → HDR radiance. 표시용 tone mapping은 별도.’ | C4 ELU 출력, C7 `10**output - 1` |
| 84·85 | DPT에도 convolution이 없는 순수 attention이라고 오해 가능 | ‘Transformer 특징을 여러 공간 크기로 복원·융합. DPT head는 convolution/interpolation 포함.’ | C9 |
| 85 | decoder 모든 단계에 고정된 1/8·1/4 비율 단정 | ‘서로 다른 공간 해상도의 특징을 융합. 정확한 크기는 patch 및 DPT 구현 설정에 따름.’ | C9 |
| 87 | 결과 이미지에서 정확도나 실시간 성능을 일반화할 위험 | ‘Reference / Prediction / Error×5를 구분. 특정 결과를 모든 장면·장치의 정확도/속도로 확장하지 않음.’ | R1 결과 그림 |
| 88 | To do만 있는 미완성 한계 | ‘토큰 수 증가에 따른 계산 비용 / 학습 분포 밖 일반화 / 물리적 정확성의 한계’와 결론으로 보충 | R1 한계, C1 scene setting tips |

## 58쪽 초기화 교체 표

| 구분 | 정확한 설명 |
|---|---|
| 사용 중 공유 | 한 forward에서 모든 삼각형에 같은 `tri_token`을 더한다. |
| 학습 가능 | `nn.Parameter`이므로 optimizer가 공유 벡터를 갱신할 수 있다. |
| 공개 구현의 시작값 | `torch.randn(1,1,D)`로 초기화한다. |
| 0 또는 1 초기화 | 주변 가중치·입력·손실에 따라 차원별 기울기는 달라질 수 있다. 동일 초기값만으로 학습 실패를 증명할 수 없다. |
| 검증되지 않은 주장 | 이 벡터의 랜덤 초기화가 다른 초기화보다 항상 우수하다는 비교 실험 결과는 이 코드만으로 알 수 없다. |

간단한 반례: 공유 벡터 `t=(0,0)`가 서로 다른 가중치를 거쳐 `y=t1+2*t2`를 만들고 `L=(y-1)^2`라면, 초기점의 gradient는 `(-2,-4)`다. 초기 두 성분이 같아도 기울기는 다르다. 이 예시는 원 논문의 실험이 아니라 오류를 확인하기 위한 수학적 반례다.

## 빈 페이지·미완성 페이지 보충용 텍스트

48쪽 도식은 기존 둥근 빈 영역 안에서 편집 가능한 텍스트와 화살표로 만든다. 제목과 페이지는 유지한다. 원본에 영상이 임베드되어 있었는지는 이 PDF만으로 확인할 수 없으며, PDF에는 빈 영역으로 보인다. 존재하지 않는 영상을 있다고 가정하지 않는다.

88쪽 `To do…`는 아래 문구로 바꾼다.

1. 토큰 수: 삼각형·출력 패치가 많아질수록 어텐션 비용 증가.
2. 일반화: 학습한 재질·광원·카메라·메시 조건 밖에서는 품질 저하 가능.
3. 정확도: 물리 효과의 학습된 예측이며 모든 조건에서 정답 보장 없음.
4. 결론: Triangle tokens → Scene features → Ray-bundle queries → HDR image.

## 편집 시 확인할 점

- 틀린 문구를 그대로 화면에 남기고 올바른 내레이션만 덧붙이지 않는다. 해당 본문·라벨을 영상용 사본에서 교체한다.
- 27·58·63·73·75·85쪽은 도식이나 수식에도 수정이 필요하다. 작은 정정 각주만으로 처리하지 않는다.
- 기존 출처, 발표자 표기, 논문 그림의 Reference/Prediction/Error 표기를 임의로 제거하지 않는다.
- 문법 오기 `Archetecture`, `Dependant`, `frequancy`, `Meterial`은 사본에서 각각 Architecture, Dependent, frequency, Material로 정리한다.
- 학습된 값처럼 보이는 소형 행렬은 설명용 수치다. 원본 전체 행렬의 개별 산술값을 모두 재계산한 상태는 아니므로, 대본은 그 값들을 정답으로 읽지 않는다. 실제 영상 제작 시 강조하는 계산은 재현 가능한 예시로 통일하고 검산한다.
- 84~85쪽 `dpt_decoder.html`은 PDF에 포함된 정적 스크린샷으로만 확인했다. 원 HTML의 동작을 확인했다거나 실제 실행 영상이라고 표현하지 않는다.
