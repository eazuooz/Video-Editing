# 내부 출처와 조건 — game-writing

## 참고 개념

Masahiro Sakurai의 `ssvIEm_2mYM`은 게임 글쓰기가 플레이 상태와 순서의 변화에 대응해야 한다는 개념 연구용이다. 원본 대본 전체 복사/번역, 원본 영상/음성 재사용은 하지 않는다. 우리 12장/72문단의 한영 대본, 항구 이야기와 실행 모델은 독립 제작이다.

## 이번 실제 게임/개발 후보

1. [Larian Studios 공식 DOS2 Game Master Mode Tutorial](https://www.youtube.com/watch?v=ZSh7hOZl9hg), 2017-09-18, 약31:45, 1920×1080/30fps. 원본 실제 지도/선택지/아이템 편집. 공식 설명은 개발자가 캠페인 도구를 설명하는 시연임을 확인한다. 이후 게임의 자동 조건 분기 구현을 입증한다고 해석하지 않는다.
2. [Larian Studios 공식 DOS2 Gameplay Overview](https://www.youtube.com/watch?v=YEgrKLregCw), 2018-08-16, 약3:27, 1920×1080/30fps. 인물 인식이 표현된 대화, 서로 다른 답/인물의 실제 화면. 짧은 구간은 정상 속도로 짧게 사용하고 별도 동작과 연결한다. 예고편 전투·잔혹한 장면·예약/제품 광고를 비중 채우기에 쓰지 않는다.
3. 자체 `항구의 봉인`. 우리 코드/그림/대사로 만든 실행 가능한 이야기 게임. 게시판 읽기와 정보 전달, 증표 현재 소유자와 동료 부재, 세 경로의 합류와 결과 유지, 설명 생략 후 필수 사실 회수를 직접 실행한다. 해당 동작을 보여주는 화면과 정리 도식의 시간은 별도로 분류한다.

## 사용 조건과 미완료 사항

2026-10-02 [Larian Fan Content Policy](https://larian.com/fan-content-policy)와 [공식 콘텐츠 제작자 FAQ](https://larian.com/support/faqs/intellectual-property-ip-usage-by-content-creators-for-streaming-recording-and-original-content_67)를 읽었다. 정책은 게임 기반 영상·이미지/팬 콘텐츠와 무료 접근 영상의 광고 수익에 관한 조건을 포함한다. 추가 Larian 로고/상표로 공식 채널처럼 꾸미지 않고, 기존 법적/IP 표시는 보존하고 비공식 해설임을 구분한다. 모든 구성 요소에 대한 권리/제3자 조건은 별도로 책임진다. 공식 업로더라는 사실만으로 모든 재편집·실제 공개 범위를 자동 승인하지 않는다.

이 정책은 BG3에 그대로 적용하지 않는다. [BG3 별도 약관](https://baldursgate3.game/bg3-fan-content-terms/)과 [Wizards Fan Content Policy](https://company.wizards.com/en/legal/fancontentpolicy)의 추가 조건 때문에 BG3 공식/타사 영상은 이번 후보에서 제외했다. 타사 플레이 영상도 확인되지 않은 허가를 추정하지 않는다.

Larian IP를 재현하는 생성 AI 프롬프트/학습, 인물/배우 목소리 복제, 소스 오디오의 ML 사용은 하지 않는다. 자체 그림은 별개의 항구·등대·우리 인물로 직접 코딩했다. 내레이션은 기존 승인 사용자 목소리, 음악은 기존 승인 Nimbus이며 공식 소스 오디오는 믹스에서 제외한다. 출처/권리 기록은 내부에 보존하고 공개 설명의 출처 블록은 사용자 지시에 따라 넣지 않는다. 실제 최종 공개 권리 판단, 사람 청취/이해, 원래 Nimbus 파일, 회원 잘린 핸들 원본, 외부 백업은 pending이다.

## 검토 증거와 파일

후보 선정/제외와 최근 이력은 `game-candidates.json`, 실제 source 해시는 `source-files.json`, native 관찰은 `native-review.json`, 자체 상태/실제 UI 검증은 `../production/playtest-state-proof.json`과 `../production/playtest-ui-proof.json`에 둔다. 다운로드 원본 MP4/info.json은 로컬 미디어이며 Git에 넣지 않는다. 중간 source 시트의 이름/시간 목록은 사전 검토 proof 폴더에 기록했다. source 단위 전체 디코딩과 최종 컷별 실제 동작 확인 전에는 footage 완료로 표시하지 않는다.
