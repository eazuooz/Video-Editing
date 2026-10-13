# 현재 원본과 사용 경계

기술 근거는 `production/research/game-lighting-history/research-pack.json`의 개발사 원문·코드·버전 문서를 사용한다. 원본 참고 대본의 모든 문장을 번역하는 대신 독립 KO/EN 설명을 작성했다. 일부 원문의 정확한 베이크 시간/성능 숫자는 검증 전 보류했다.

현재 확보한 QuakeII RTX는 NVIDIA 공식2019현대 렌더 소개이며1997원작 bake의 증거가 아니다. 전체40.874167초 decode0,21표본4판을 직접 읽었다. 비교 토글은 보이지 않았으며 서로 다른 컷을 on/off 결과로 편집하지 않는다. 이 원본은 3편 후보로 유지한다.

HL2 wall.mpeg는 독립 ValveArchive에 보관된2003년 파일이다. SoftimageXSI의 고해상도 바위→법선 텍스처→평면 재질→Source 게임 공간이 보인다. 전체338.233467초 decode0,35표본6판을 직접 읽었지만 원저자/배포 계보/영상 권리와 낮은352×240화질은 미확정이다. 메뉴·dialogs·동작 없는 구간은 actual quota가 아니다. 이 영상만으로 RNM 세 방향 bake를 구현했다고 주장하지 않는다.

Epic UE4.27의 Use Cascaded Shadows 문서에 연결된 공식6.940267초 시연은1280×720/30000÷1001fps,208프레임,video-only 원본으로 확보했고 decode0와15표본3판 직접 검토를 마쳤다. 바닥에서는 캐릭터 그림자가 보이고 CSM수신이 꺼진 계단에서는 보이지 않는다. 이것은 수신 설정 예이며 cascade 경계/frustum 디버그가 아니다. 원본에 두 달리기 사이클이 포함되어 있으므로 같은 행동을 반복 삽입해 분량을 늘리지 않는다.

DOOM3 Macworld2001엔진 시연은 Bethesda공식 회고에 연결된 제3자 아카이브다.236.466667초720p60/decode0/25표본5판을 직접 읽었으며, 움직이는 구조·캐릭터의 조명 반응을48–108/158–185초 후보로 좁혔다. 발표자·제품화면·프로젝터프레임·검은전환은 제외한다.2001기술시연과2004출시 구현을 구별하며, Bethesda의 링크가 제3자 녹화물 재사용 허가를 뜻하지는 않는다.

DOOM+DOOMII Steam공식2024트레일러는59.709650초1080p60000/1001fps/decode0/20표본4판 검토했다. 재발매·Legacy of Rust·온라인홍보·메뉴·타이틀이 섞여 있으며 원작1993알고리즘의 직접 증거가 아니다.1993구현은id원본 코드로 설명한다.

Epic공식2017 `Lighting Techniques & Guides`는4660.766667초1080p30/video-only 원본이다. 전체decode0,57넓은표본10판에 더해13후보구간163표본32판과 설정창35표본9판을 직접 읽었다. Far Shadow Cascade Count0/1/4, Num Dynamic Shadow Cascades4/1/3, Dynamic Shadow Distance·Distribution Exponent 변화와 실제 그림자/색 경계가 보였다. 라이트맵128/256/512/1024는 서로 다른 작성된 방을 방문하는 비교이며 같은 물체의 토글이 아니다. 움직이는 물체·공간 캐시·floor shadow는 후속UE4예시이고Quake나HL2의 내부 구현으로 바꿔 설명하지 않는다. 후보487초에는 추가 대기 제거와 완결 동작·최종 자막 crop 검수가 필요하다. 설정tooltip·UV/PPT·빌드대기는actual분량으로 승인하지 않았다.

Epic공식 `The Art of Robo Recall`는3901.966667초720p60 원본이다.37표본7판에서 대부분 정적슬라이드와 진행자가 보여 연구/설명자료로 분류했다. Forward/MSAA/최적화 주장 근거로 읽었지만, 강의 전체나 영상플레이어의 한스크린샷을 실제 움직이는 게임 분량으로 셈하지 않는다.

Epic공식 `Getting Started with Post Processing`는2017-07-06방송/2017-07-11업로드의 UE4.16.2 시연이다.4074.433333초720p60/video-only/전체decode0다.29넓은표본5판과37AO표본10판을 직접 읽었다.3085–3103초에는AO Power/Bias와큐브접촉,3105–3128초에는카메라 이동이 보인다. 여러 변수와카메라가바뀌므로모든변화를단일AO값효과로주장하지않는다. SSR플랫폼·CustomDepth·브라우저문서는현재AO후보에서제외한다. 별도CSM메뉴15표본4판에서Show→Advanced→Shadow Frustums의선택과색경계를직접확인했다. 공식방송outline PDF3페이지의전체텍스트도읽었다.

현재 원본10개 합계13442.240885초와 엔진 후보528초는 최종 채택714초 계획을 달성했다는 의미가 아니다. 최종actual승인0초다. 자세한 인아웃·시선·주장·도식연결·제외이유는 `game-candidates.json`, `../production/native-interval-review-v2.json`과 `../production/postprocess-native-review-v2.json`을 따른다.

Valve의 게임 콘텐츠 동영상 정책은 교육/playthrough와 조건부YPP를 허용하나, 제3자 영상의 녹화 저작권을 자동 허용하지 않는다. Epic/NVIDIA 원본 기술 시연의 재사용 조건과 제3자 자산도 별도 확인한다. 최종 공개 권리는 현재 승인하지 않았다.

Bethesda Fan Video Policy와 Epic Fan Content Policy의 조건부 동영상/YPP 맥락을 읽었다. 제3자 음악·자산·녹화권리는 별도다. Epic사용 시 비공식/비보증 고지 의무도 반영해야 하며, 공개 설명의 출처블록 생략이 고지 의무를 없애지 않는다. 다운로드 성공이나 내부검수 준비를 최종 공개 권리 승인으로 표시하지 않는다.

모든 원본/info/서명URL/추출/보드/렌더는 local-only다. `game-candidates.json`의 precise source/sha/review/status를 따른다. 자료 다운로드를 시도한 실패와 부분 파일도 보존했고, 실패한 파일을 확보 완료나 사용 승인으로 기록하지 않았다.

추가 공식 소스: DOOM3 스토어 원본156.866667초와 Quake2021 강화판99.399311초를 확보하고 두 전체decode0,64표본12판을 직접 검토했다. Quake2021은1996원본 출력 증거로 쓰지 않는다. 모든 원본/표본은local-only이고 선택 완결구간·crop·자막·권리 검토는 별도다. 전체 연구 원본12개13698.506863초는 채택 분량이 아니다. 근거: `production/research/game-lighting-history/local/steam-historical-acquisition-v1.json`.

공식UE4 재질 시연: https://www.youtube.com/watch?v=WaM_owaUpbE .2017-06-13방송/2017-06-20업로드를 구별.3744.233333초1080p30 원본 SHA256 bbc1cf65bc5f2fe7bcccad87450698d79547ff4c8a78a38913031b55a257e616, 전체decode0,53표본10판 직접 읽음. 재질 평탄화/버퍼 출력은 조명 베이크나 포워드/디퍼드 성능 비교가 아님. 원본은video-only이며 외국어 해설/원곡을 최종믹스로 가져오지 않고 fallback을 별도로 기록. Epic조건과 필수비공식고지는 유지; 공개권리·사람검토는pending. 원본/이미지local-only.
