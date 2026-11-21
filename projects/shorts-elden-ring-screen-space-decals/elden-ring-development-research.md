# 엘든 링 개발 자료집

2026-11-21 공개 자료 검토. 본편 『ELDEN RING』을 중심으로, 본편 확장팩 『황금 나무의 그림자』의 제작 사례도 버전을 표시해 실었다. 『NIGHTREIGN』 사례는 제외했다. 공개 발표의 소개 페이지, 개발자 직접 인터뷰, 현장 취재, 독립 캡처를 함께 확인했다. 로그인 뒤 열리는 슬라이드와 온라인에 전문이 없는 지면은 확인 범위를 따로 적었다.

## 쇼츠에서 쓸 첫 근거

| 쓸 수 있는 주장 | 근거와 범위 |
| --- | --- |
| 엘든 링의 PC 프레임에서 진흙 발자국이 데칼로 그려지는 사례가 관찰됐다. | 그래픽스 프로그래머의 독립 D3D12 캡처. 진흙 장면에서 데칼 단계의 색, 법선, 표면 속성 버퍼를 비교했다. [프레임 분석의 Decals 절](https://mamoniem.com/behind-the-pretty-frames-elden-ring/#decals) |
| 분석에서 확인한 일부 데칼은 불투명 표면 정보가 든 디퍼드 G-버퍼에 그려졌다. | 캡처에 데칼 드로와 투영 관련 상수, 텍스처가 나타난다. 일부 혈흔 투영 볼륨은 잘린 각기둥 형태로 관찰됐다. 같은 무늬의 결과가 다른 예시가 있다. [프레임 분석](https://mamoniem.com/behind-the-pretty-frames-elden-ring/#decals) |
| 캐릭터 생성의 상처와 화상에도 데칼이 사용됐다. | 제작진이 제공한 메이킹은 마스크와 법선 텍스처를 설명한다. 제작 자료로 확인한 얼굴 데칼의 범위는 재질 입력까지다. [CGWORLD 캐릭터 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring01.html) |
| 화면 좌표와 깊이로 표면 위치를 계산하고, 투영 상자 안에서 무늬를 읽을 수 있다. | 일반적인 깊이 기반 데칼 원리와 자체 시연. 자체 시연의 상자 크기, 법선 조건, 색상과 3D 좌표는 시연의 값이다. [Unity 월드 위치 복원 예제](https://docs.unity.cn/Manual/urp/writing-shaders-urp-reconstruct-world-position.html) · [Unity URP 데칼 문서](https://docs.unity.cn/Manual/urp/renderer-feature-decal-reference.html) |

독립 분석에는 가려진 발자국 드로가 다수 남은 캡처도 있다. 이는 그 캡처의 드로 관찰이다. 전체 게임에 걸친 개수나 밀리초까지 전달하려면 플랫폼, 패치, 장면, 그래픽 설정과 프로파일링 결과가 더 필요하다. Unity URP의 Screen Space는 일반 원리와 제품 사용 예시를 설명하는 데 사용했다. [프레임 분석](https://mamoniem.com/behind-the-pretty-frames-elden-ring/#decals) · [Unity URP 데칼 문서](https://docs.unity.cn/Manual/urp/renderer-feature-decal-reference.html)

## 1. 월드와 레벨을 어떻게 설계했나

- **오픈 필드와 레거시 던전.** 필드에서는 목적지, 이동 속도, 재도전 시기를 플레이어가 선택한다. 레거시 던전은 입체적인 동선과 전투 간격을 세밀하게 조절한다. 스톰빌 성의 정문·지붕·지하처럼 서로 다른 경로와 공간 인상이 사례다. 자유도를 늘리면서 진행 순서, 필드 이동 감각, 보스와 이벤트의 배치를 함께 조정하는 일이 중요했다. [미야자키 인터뷰](https://blog.ja.playstation.com/2022/01/29/20220129-eldenring/) · [CGWORLD 환경 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring02.html)
- **랜드마크 세 크기.** 먼 곳의 성이나 황금 나무는 큰 방향을 만든다. 이동 중 보이는 교회나 요새는 중간 목표가 된다. 야영지, 폐허, 동굴 입구의 불빛 등은 가까워진 뒤 새 선택지가 된다. 포장도로, 여러 위치에서 보이는 실루엣, 조사하면 빛이 뻗는 석상 등 유도 신호가 서로 다른 거리에서 작동한다. [CEDEC+KYUSHU 공식 세션](https://www.cedec-kyushu.jp/2022/session/05.html) · [현장 취재](https://www.4gamer.net/games/463/G046388/20221115054/)
- **변화의 간격.** 지역마다 대표 색과 식생이 달라진다. 같은 지역에서도 호수, 숲, 해안으로 인상을 바꾸고, 더 가까이에서는 물의 탁도와 파편, 동물 등을 달리했다. 아트 팀과 기획은 시야가 트이는 순간과 풍경에 주목하는 방향을 논의해 뷰포인트를 정했다. [CEDEC+KYUSHU 현장 취재](https://www.4gamer.net/games/463/G046388/20221115054/) · [CGWORLD 환경 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring02.html)
- **난관도 진행 단서가 된다.** 미야자키는 적이 너무 어렵게 느껴지면 플레이어가 다른 경로를 찾을 수 있다고 설명했다. 나중에 돌아오기, 은신, 영체, 협력 등 여러 해결 루트를 둔 이유와 이어진다. 네트워크 테스트에서는 익숙하다고 가정한 소환 풀의 사용 방식이 일부 플레이어에게 혼동을 줬다는 피드백을 받았다. [D.I.C.E. 현장 개발자 문답](https://www.gamedeveloper.com/design/hidetaka-miyazaki-s-advice-for-challenging-game-design-trust-players-) · [PlayStation 개발자 인터뷰](https://blog.ja.playstation.com/2022/01/29/20220129-eldenring/)
- **세계 설정은 제작 입력으로 쓰였다.** 조지 R. R. 마틴은 플레이어가 도착하기 이전의 신화·역사와 인물의 바탕을 만들었다. 제작진은 이를 게임 속 현재의 인물, 환경, 사건으로 발전시켰다. 고드릭은 위엄 있는 반신의 역사와 몰락 이후 뒤틀린 모습을 연결하는 사례다. [Xbox Wire 개발자 인터뷰](https://news.xbox.com/en-us/2019/06/09/hidetaka-miyazaki-and-george-rr-martin-present-elden-ring/) · [PlayStation 개발자 인터뷰](https://blog.ja.playstation.com/2022/01/29/20220129-eldenring/)

## 2. 오픈 필드를 구현하고 검사한 방법

- **오픈 그리드.** 자유 이동을 지원하도록 오픈 필드를 격자로 관리하고 주변 구역을 읽는다. 현장 취재에는 기본 셀과 512m·1024m 단위, 큰 보스나 빠른 이동에 대응한 배치가 소개된다. 밀집한 레거시 맵의 데이터 관리와 오픈 필드의 필요가 달랐다. 여기서 셀 크기는 데이터 단위 사례이며 플레이어 주변의 항상 고정된 로딩 반경을 뜻하지 않는다. [CEDEC 2022 공식 발표 개요](https://cedil.cesa.or.jp/cedil_sessions/view/2542) · [패미통 현장 취재](https://www.famitsu.com/news/202208/26273425.html) · [전격 인디게임 현장 취재](https://news.denfaminicogamer.jp/kikakuthetower/220825m)
- **지형과 오브젝트의 분리.** 기본 지형과 반복 배치하는 건물·바위 같은 에셋을 나눴다. 회전과 크기 차이로 적은 원본에서 다양한 바위 구성을 만든 사례가 있다. 제작 과정에서는 필요한 단차를 세밀하게 편집하려고 초기 하이트맵 방식에서 폴리곤 메시 작업으로 옮겼다고 설명했다. [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/) · [CEDEC+KYUSHU 현장 취재](https://www.4gamer.net/games/463/G046388/20221115054/)
- **거리별 에셋 표현.** 가까이에서는 여러 부품이 있는 모델을 쓰고, 멀리에서는 여러 부품을 하나로 묶어 표면 특성을 구운 가벼운 모델로 대체한 사례가 있다. 풀·작은 돌·잔해·뼈 등의 배치에는 지형에 칠한 버텍스 값, 밀도와 종류 파라미터를 이용했다. 플랫폼별로 배치량을 조절할 수 있었다. [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/)
- **내비게이션.** 보행 가능한 영역인 내비메시를 만들고, 점프와 낙하로 넘을 수 있는 높이 차이는 별도의 이동 연결로 생성했다. 큰 적에게는 몸집과 지형 조건을 반영한 별도 경로가 있었다. 경로 탐색 구현과 공격 의사결정 AI는 서로 다른 층이다. [CEDEC 2022 공식 발표 개요](https://cedil.cesa.or.jp/cedil_sessions/view/2542) · [패미통 현장 취재](https://www.famitsu.com/news/202208/26273425.html)
- **정보 지도와 자동 순회.** 배치물과 데이터를 개발용 웹 지도에서 보고, 클릭해 상세 정보를 확인하거나 디버그 위치로 이동했다. 자동으로 맵을 돌며 부하와 오류 데이터를 수집하고 위치와 연결했다. 리소스 의존성 데이터베이스는 변경 영향, 미사용 데이터와 네트워크 테스트 범위 검토에 활용됐다. 레거시 맵에서 벽 뒤의 표시를 줄이기 위한 가시성 설정도 자동 생성한 사례가 있다. [CEDEC 2022 공식 발표 개요](https://cedil.cesa.or.jp/cedil_sessions/view/2542) · [패미통 현장 취재](https://www.famitsu.com/news/202208/26273425.html)

## 3. 렌더링, 하늘과 안개

- **화풍을 먼저 정했다.** 하늘은 반구형 메시와 여러 평면 층으로 만들어 시간대에 따른 색과 구름을 제어했다. 시간의 구간마다 대표 상태를 만들고 그 사이를 이어 아트 작업량을 관리했다. 시프라 강의 별처럼 지역 고유의 장면에는 별도의 환경 연출을 적용했다. [CEDEC 2022 대기 발표 개요](https://cedil.cesa.or.jp/cedil_sessions/view/2567) · [4Gamer 현장 취재](https://www.4gamer.net/games/463/G046388/20220826111/)
- **가까운 안개와 먼 안개.** 가까운 구간의 광선 경로는 여러 지점에서 밀도와 빛을 샘플링하는 레이 마칭으로 근사하고, 먼 범위는 더 가벼운 해석적 안개로 보완했다. 글로벌 안개 위에 국소 볼륨을 배치하고 3D 노이즈로 형태를 조절했다. 아티스트는 그림자 쪽의 환경광 색과 직사광 색, 빛줄기를 활용해 공간별 분위기를 바꿨다. [CEDEC 2022 대기 발표 개요](https://cedil.cesa.or.jp/cedil_sessions/view/2567) · [현장 취재](https://www.4gamer.net/games/463/G046388/20220826111/)
- **PC의 독립 캡처.** 해당 분석은 D3D12, 디퍼드 G-버퍼, 표면 속성에 적용하는 데칼, 환경 큐브맵과 베이크된 조명 볼륨 등을 관찰한다. G-버퍼에는 색, 법선, 깊이와 금속성·거칠기 같은 표면 정보가 들어간다. 캡처에서 관찰된 흐름을 근거로 사용하고, 제작진의 의도와 모든 플랫폼의 파이프라인은 별도 근거가 필요한 항목으로 둔다. [Behind the Pretty Frames](https://mamoniem.com/behind-the-pretty-frames-elden-ring/)
- **패치와 성능 해석.** 1.09 패치에서 지원 기종에 레이 트레이싱 옵션이 추가됐다. 2022년 PC 출시 초기의 프레임타임 문제는 Digital Foundry와 ComputerBase가 직접 관찰했다. 출시판 성능과 이후 버전의 옵션을 섞으면 비교가 틀어진다. 현상·테스트 조건과 엔진 내부 원인 가설을 함께 구분해야 한다. [공식 1.09 변경 사항](https://en.bandainamcoent.eu/elden-ring/news/elden-ring-patch-notes-version-109) · [Digital Foundry 초기 측정](https://www.youtube.com/watch?v=5EtcrUrsl38) · [ComputerBase 초기 벤치마크](https://www.computerbase.de/artikel/grafikkarten/elden-ring-benchmark-test.79799/seite-2)

## 4. 모형, 애니메이션과 VFX

- **캐릭터 생성과 재질.** 몸 비율 조절에서 인접 부위 차이가 큰 경우 값을 연동한다. 아이라인 등은 마스크를 이용하고, 상처·화상은 데칼에 법선 정보를 더해 빛에 요철이 읽히도록 했다. 얼굴 텍스처의 채널에는 색, 법선, 매끄러움과 서로 다른 마스킹 용도가 나뉜다. [CGWORLD 캐릭터 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring01.html) · [CEDEC 2022 캐릭터 제작 발표](https://cedec.cesa.or.jp/2022/session/detail/127.html)
- **리카드의 팔과 얼굴.** 리카드의 검에서 뻗는 팔과 일부 몸 움직임은 프레임별 버텍스 데이터를 텍스처에 저장하는 VAT로 제작됐다. 검의 팔에는 위치와 법선용 자료가 공개돼 있다. 개별 팔에 뼈를 구성하는 부담을 줄이면서 실루엣과 팔 개수를 조절할 수 있었다. 얼굴이 올라오는 컷신에도 VAT가 사용됐다. [CGWORLD 캐릭터 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring01.html)
- **플라키두삭스의 재 변환.** 폴리곤 조각을 분리해 움직이는 VAT와, 조각의 가장자리를 투명하게 만드는 처리를 결합했다. 입자가 떠나는 인상과 원래 실루엣의 소멸이 같은 변화로 읽힌다. [CGWORLD 캐릭터 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring01.html)
- **장비의 물성.** 갑옷의 판을 리벳으로 연결한 형태, 손이 닿는 가장자리의 마감 등 가상의 장인이 어떻게 만들었을지 먼저 생각했다. 같은 판금 갑옷도 입체 돌출과 새김을 달리해 서로 다른 인상을 만들었다. [CGWORLD 캐릭터 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring01.html)
- **무기와 적의 모션.** 한손·양손·쌍수·기승과 전회 조합으로 동작 수가 늘었다. 각 무기의 무게·길이·사용 방식이 보이게 포즈와 효과를 조정했다. 라단은 공격이 시작된다는 예고와 대기 자세의 위압감이 각각 설계 대상이었다. [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/) · [CEDEC+KYUSHU 현장 취재](https://www.4gamer.net/games/463/G046388/20221115054/) · [FromSoftware 모션 담당 인터뷰](https://careers.fromsoftware.jp/jp/interview_017.html)
- **리그 선택.** 3ds Max Biped가 운영과 모션 이식의 기본 도구 중 하나였다. 레날라의 떠 있는 천에는 전용 리그가, 신의 살갗 두 인물의 늘어나거나 팽창하는 움직임에는 Spline IK를 이용한 리그가 소개됐다. [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/)
- **VFX 제작 파이프라인.** 동작 초안을 바탕으로 효과와 사운드 작업을 시작한 주문 사례가 있다. 자체 FX Editor로 소재와 파라미터를 만들고 실기에서 확인했다. Time Act Editor는 동작과 효과 시작 시각을 연결했고, MovieSequencer는 컷신에 쓰였다. 작은 주문인 휘석의 돌팔매는 색·크기·발광을 반복 수정해 힘의 인상을 조절했다. [CGWORLD VFX 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring03.html)
- **VFX 세부 단계와 해상도.** 전부 같은 품질을 낮추는 대신 효과별로 거리에 따른 표시 방식을 정했다. 예를 들어 먼 아이템 표시에서 발광의 존재감은 살리고 일부 광원과 글로를 덜어 비용을 낮췄다. 축소 버퍼도 작업 사례로 소개된다. [CGWORLD VFX 메이킹](https://cgworld.jp/article/202206-cgw286-eldenring03.html)

## 5. 사운드와 제작 운영

- **음악의 브리프와 재녹음.** 음악 담당은 디렉터 브리프, 캐릭터 배경, 콘셉트와 게임 스크린샷을 바탕으로 곡을 만들고 피드백을 받았다. 라단 축제의 「Song of Honor」는 능숙한 합창 느낌을 피하려고 금관 연주자들이 부르는 버전을 사용한 사례다. [리드 사운드 디자이너 사이토 쓰카사의 직접 설명](https://blog.playstation.com/?p=369262)
- **필드의 음향 작업량.** 개발자는 환경음, 영마, 타격음 등을 만들고, 효과음 및 잔향 설정을 더 효율적으로 배치하도록 엔지니어와 자동화 작업도 했다고 밝혔다. 이 인터뷰는 사운드 배치와 잔향 설정을 위한 협업까지 설명한다. [FromSoftware 사운드 담당 인터뷰](https://careers.fromsoftware.jp/jp/interview_018.html)
- **프로토타입 → 플레이 가능 버전 → 양산.** 과거 에셋을 이용해 필드 규모, 제작비와 작업량을 먼저 가늠했다. 점프, 기승, 영체와 던전 연결을 플레이 가능한 버전에서 시험하고 필드를 임시로 연결해 메모리 제약을 확인했다. 제작 세미나에서는 도쿄·후쿠오카 협업, 파트별 검토와 외부 리뷰가 뒤따랐다고 설명했다. [Too 주최 측 세미나 기록](https://www.too.com/dc/report/elden_ring_220708/) · [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/) · [Xbox Wire 개발 초기 인터뷰](https://news.xbox.com/en-us/2019/06/09/hidetaka-miyazaki-and-george-rr-martin-present-elden-ring/)
- **제작 도구의 역할.** 발표에서 3ds Max는 모델링·배치·동작, MotionBuilder는 캡처와 컷신 프리비즈, ZBrush는 조형, Marvelous Designer는 의상·천, Substance 도구는 재질·텍스처 작업에 사용했다고 소개했다. 이는 DCC 제작 도구 목록이며 런타임 엔진의 이름이나 구성을 뜻하지 않는다. [제작 세미나 현장 취재](https://www.4gamer.net/games/463/G046388/20220715099/)
- **라이브 밸런스.** 1.07은 PvP 피해 보정을 별도로 추가했다. 확장팩 1.12.2에서는 그림자 나무의 가호의 공격·대미지 경감 곡선 앞부분을 높이고 뒷부분의 증가를 완만하게 조정했다. 사용 사례 동영상에 수치를 넣을 때는 해당 게임 버전을 화면과 맞춘다. [공식 1.07](https://en.bandainamcoent.eu/elden-ring/news/elden-ring-patch-notes-107) · [공식 1.12.2](https://en.bandainamcoent.eu/elden-ring/news/elden-ring-calibration-update-1122)

## 6. 확장팩의 환경 배치

- **청해안.** 배경 동선의 직선에 곡선을 섞고, 시선을 중앙으로 보내기 위해 높이와 좌우 배치를 조정했다. 일반 식생은 자동 배치하더라도 중요한 뷰포인트의 빛나는 꽃은 손으로 놓고 먼 꽃밭은 텍스처로 조율했다.
- **묘지 평원.** 넓게 트인 첫인상을 유지해야 해 근경에 큰 나무를 늘리는 시안을 버리고, 원경의 강한 실루엣과 거대한 베일을 사용했다. 플레이 조건을 고정한 채 시각적 변화를 다른 깊이 층으로 옮긴 사례다.
- **그림자 알터.** 해당 발표에서 예시로 다룬 세 번째 지역이다. 전체 방법은 반복되는 모양, 좌우 대칭, 단조로운 밝기와 목적지 가시성을 점검하고, 특정 뷰포인트에 작업을 집중하는 흐름으로 이해할 수 있다.

[CEDEC 2025 공식 발표](https://cedec.cesa.or.jp/2025/timetable/detail/s67af327dba680/) · [4Gamer 확장팩 사례 취재](https://www.4gamer.net/games/866/G086614/20250724066/) · [CGWORLD 발표 정리](https://cgworld.jp/article/202508-cedec-eldenring.html)

## 발표와 후속 대본에 쓰는 순서

| 발표·자료 | 확인 범위 | 대본 후보 |
| --- | --- | --- |
| [CEDEC 2022 오픈 필드 엔지니어링](https://cedil.cesa.or.jp/cedil_sessions/view/2542) | 공식 소개와 현장 취재. 발표 PPTX는 로그인 필요. | 말 타고 이동해도 다음 지역이 이어지는 이유 |
| [CEDEC 2022 대기 표현](https://cedil.cesa.or.jp/cedil_sessions/view/2567) | 공식 소개와 현장 취재. 발표 PPTX는 로그인 필요. | 안개를 가까운 곳과 먼 곳에서 다르게 그리는 이유 |
| [CEDEC 2022 캐릭터 모델 제작](https://cedec.cesa.or.jp/2022/session/detail/127.html) | 공식 소개와 별도의 제작진 메이킹 기사. | 리카드의 검에 달린 팔을 VAT로 움직이는 법 |
| [CEDEC+KYUSHU 2022 오픈 필드](https://www.cedec-kyushu.jp/2022/session/05.html) | 공식 세션, 개발자의 랜드마크와 모션 사례를 전한 취재. | 성을 보고 걷다가 왜 교회로 새는가 |
| [CEDEC 2025 배경 레이아웃](https://cedil.cesa.or.jp/cedil_sessions/view/3156.html) | 공식 소개, 확장팩 사례 취재. 함께 발표된 별도 게임의 사례는 범위 밖. | 묘지 평원에서 가까운 나무 대신 먼 베일을 택한 이유 |
| [GDC Vault 성장과 게임 디자인](https://www.gdcvault.com/play/1028842/Fair-Play-Summit-Promoting-Growth) · [GDC Vault 친사회적 멀티플레이](https://gdcvault.com/play/1034865/Fair-Play-Summit-Kind-Games) | 외부 발표자가 게임 사례로 분석. FromSoftware의 자체 렌더링 공개 세션은 확인 범위에서 찾지 못했다. | 선택지를 넓혀 재도전하는 경험을 비교 분석할 때 참고 |
| [D.I.C.E. 현장 미야자키 인터뷰](https://www.gamedeveloper.com/design/hidetaka-miyazaki-s-advice-for-challenging-game-design-trust-players-) | 현장에서 디렉터가 답한 설계 관점. | 적의 난도가 다음 길을 알려 주는 방식 |
| [CGWORLD 286호 목차](https://cgworld.jp/magazine/cgw286.html) | 52쪽 메이킹 특집 안내와 인터넷 공개 분량 3편. 지면 전체에 대한 확인은 남아 있다. | 캐릭터의 재질·환경 아트·효과의 실제 제작 과정 |

커뮤니티 글은 직접 캡처, 측정 조건, 버전 또는 원본 발표가 연결된 항목을 먼저 따라갔다. 재게시된 추측만으로 엘든 링의 정확한 엔진 명칭, 데칼 처리의 전체 성능, 셰이더 소스, 지역별 메모리 예산, 네트워크 내부 프로토콜을 확정할 수는 없다. 프레임 분석의 캡처와 발표 슬라이드는 대본의 참고 자료로 사용했고, 영상 시연은 자체 제작했다.
