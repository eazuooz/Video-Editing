/* Preparation only: paragraph-specific projected geometry, no rendered approval. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rows = {
  '03': {
    overview: ['alley-input-layers', '깊이 평면에서 벽 뒤 정보를 숨기고 거리장 층과 레이 상자를 드러낸 뒤 기하 선택과 조명 캐시의 다른 화살표를 연결하기'],
    '12a': ['scene-representations', '같은 벽 옆에 카메라 깊이·거리장·복셀을 공간적으로 배치하기;카메라 이동으로 깊이 평면 정보 바꾸기;표면 안팎 거리 층을 펼치기;복셀의 기하 점유와 저장한 빛을 다른 레이어로 보여주기;AO 가림량과 붉은 벽의 GI 색 운반을 분리하기;카메라 밖 물체를 옮겨 입력 범위 비교하기;얇은 벽이 성긴 셀에서 합쳐지는 오류 보이기;삼각형 질의와 후보 상자로 연결하기'],
    '13a': ['ray-slab-bvh', 'o+t*d 레이를 실제 삼각형 방향으로 전진시키기;겹친 경계 상자와 계층 가지를 선택·제외 색으로 구분하기;x,y,z 구간을 깊이별 레일 위로 펼치기;[2,6] [3,5] [4,7] 교집합[4,5]를 표시한 뒤 한 축을[8,9]로 이동하기;상자는 통과하지만 삼각형은 빗나가는 보수적 후보 보이기;closest-hit 거리 갱신과 any-hit 조기 종료를 비교하기;성긴 상자로 불필요한 하위 방문이 늘어나는 모습;교차·셰이딩·구조 갱신의 서로 다른 비용 층'],
    '13b': ['blas-tlas-hybrid', '동일 메시 BLAS 하나에서 여러 배치 TLAS 상자로 연결하기;강체 변환과 스키닝 변형의 갱신 범위 비교하기;늘어난 상자 겹침과 재구축 비용 저울;래스터 가시성 평면 뒤에서 반사·그림자 레이만 이어 붙이기;역사적 DXR 반사와 이후 전체 경로 계산을 서로 다른 프레임 레이어로 표시하기;찾은 표면과 적은 표본의 거친 노이즈를 구별하기'],
    '14a': ['sampling-reprojection', '후보 기여와 선택 확률을 다른 높이의 막대로 표시하기;값2,8의 균등 평균5와 편향 선택의 미보정 결과 비교하기;기여/p 가중치를 후보 위치와 연결하기;N,4N의 표준오차1,1/2 비교를 조건 문구와 함께 애니메이션하기;정지·이동 표면의 누적 좌표를 비교하기;현재·과거 평면에서 카메라와 물체의 다른 이동 화살표'],
    '14b': ['upscale-history', '저해상도 현재·모션·과거 출력 평면을 고해상도 출력으로 연결하기;레이 계산 층과 복원 층을 분리하기;가로세로1/2→픽셀1/4 격자와 남은 기하·복원 비용을 별도 표시하기;여러 물체의 각각 다른 모션 벡터를 그리기;가림이 풀린 빈 과거 대응을 거부하기;얇은 선·작은 글자·가림 경계의 이동 비교하기;관측 입력과 결과 범위만 표시하고 내부 신경망 설명은 넣지 않기'],
    '15a': ['ddgi-probe-update', '공간 프로브에서 레이를 쏘고 별도 조명 저장 층으로 수집하기;카메라 이동과 고정된 공간 프로브를 분리하고 여러 표면의 조회 연결하기;주변 프로브 가중치와 거리·가림 정보를 분리하기;벽 양쪽 프로브의 무조건 보간과 가림을 고려한 기여를 비교하기;프로브 간격·저장량·분할 갱신에서 오래된 값의 나이를 표시하기;빠르게 움직이는 광원에서 지연·빛샘·갱신량을 서로 다른 관찰점으로 보여주기'],
    '15b': ['reservoir-selection', '동적 직접광 후보와 후속GI 변형의 별도 범위;작은 저장소에 선택 후보와 요약만 남기고 나머지 후보는 보내기;가중치1→3의 합4와 교체확률3/4를 움직이는 토큰으로 보여주기;선택 확률과 최종 추정 보정·대표 후보 수를 분리하기;이웃·과거 후보를 서로 다른 평면에서 빌리고 법선·위치 변화 비교하기;문이 닫히며 재사용 후보의 현재 가시성을 다시 검사하기;표본 선택과 영상 필터링을 서로 다른 화살표로 연결하기'],
    '16aa': ['visibility-hiz', '카메라 절두체 밖 물체를 제외하기;절두체 안이지만 큰 벽 뒤에 가린 물체 표시하기;깊이 검사와 셰이딩 순서·조건을 비교하기;깊이 요약 mip 평면에서 보수적 영역 테스트하기;문이 열리며 이전 깊이 판단이 오래된 것을 보이기;래스터 컬링과 BVH 질의를 서로 다른 실행 층으로 표시하기'],
    '16ab': ['geometry-shading-pages', '메시 묶음이 기하 파이프라인으로 들어가는 단계;출력 픽셀과 셰이딩 위치를 다른 깊이 레이어로 표시하기;2x2 픽셀에 한 평가 표본을 연결하고 성능배수 주장은 생략하기;가상 텍스처 전체와 상주 페이지 일부를 분리하기;요구 표시·전송 중·상주 완료를 서로 다른 상태로 보여주기;메시·셰이딩·텍스처의 서로 다른 예산을 비교하기'],
    '16a': ['nanite-cluster-hierarchy', '원본 기하에서 현재 필요한 부분을 공간적으로 선택하기;분할·묶음·단순화·재분할의 클러스터 계층;카메라 거리 변화로 같은 세계 오차의 투영 크기를 줄이기;근사 e_px=f*e_world/z를 수치와 투영 선으로 비교하기;이웃 수준 경계의 균열과 일관된 그룹 경계를 대조하기;선택과 메모리 공급을 다른 화살표·지연 상태로 표시하기;기하 공급 결과를 조명 추적 입력으로 연결하기'],
    '17a': ['lumen-trace-cache', '화면 추적·장면 표현·저장된 조명을 서로 다른 평면에 놓기;screen hit/miss에서 장면 추적으로 이어가기;거리장 경로와 삼각형 경로를 버전·모드와 함께 분리하기;실제 벽 주변의 캡처 카드들을 별도 공간 표현으로 배치하기;벽 교차 화살표와 조명 캐시 조회 화살표를 분리하기;확인한 초기 UE5 ON/OFF 후보를 연결하되 정량AB로 표시하지 않기;기하 캡처 지원과 조명 갱신의 관계'],
    '17b': ['cache-age-response', '광원 끄기와 직접광·간접 캐시의 갱신 시점을 분리하기;history weight 변화에 따른 잔상·노이즈·반응 속도 비교하기;커버리지 없는 표면을 마젠타 누락 영역으로 표시하기;얇은 벽·작은 광원이 성긴 표현과 표본에 빠지는 사례;카메라 고정·광원 변경과 광원 고정·카메라 변경을 분리하기;추적·저장·분할 갱신이 한 프레임에 연결되는 흐름'],
    conclusion: ['resource-question', 'BVH 후보·프로브 저장·reservoir 선택의 세 공간 비교;나나이트 기하와 루멘 조명을 다른 출력층으로 연결하기;그림자 페이지·경로 표본·복원·후처리의 다음 편 입력 펼치기'],
  },
  '04': {
    overview: ['final-frame-layers', '그림자 페이지·경로 표본·복원·표시 프레임·최종 색의 깊이 레이어를 순서대로 열기'],
    '18v': ['virtual-shadow-pages', '광원 관점 깊이와 수신 표면의 대응;넓은 공간의 균일 고밀도와 현재 필요한 부분의 밀도 비교;가상 격자와 물리 상주 페이지를 다른 깊이로 분리하기;예시16칸에서 요구5칸만 물리 슬롯으로 연결하기;카메라 이동의 요구와 광원·물체 이동의 무효화를 분리하기;SMRT의 그림자 깊이 추적과 실제 삼각형 레이를 분리하기;새 페이지·재사용 페이지·무효화 영역의 비용 비교'],
    '18t': ['rendered-display-timeline', '낮은 내부 격자와 현재·이전 프레임에서 높은 출력 격자로 연결하기;TSR과DLSS SR의 같은 역할·다른 조건을 나란히 배치하기;가로세로1/2→픽셀1/4와 남은 고정 비용 비교;물체·카메라·지터의 일치·잘못된 대응 비교;새 표면·입자·투명도·UI의 과거 정보 빈칸 표시;2022FG의 렌더 프레임 사이 표시 프레임과 시뮬레이션 시점을 분리하기;내부 해상도·실제 프레임·표시 프레임·지연의 서로 다른 축'],
    '18a': ['visibility-buffer-identity', '넓은 G-buffer 속성과 작은 triangle/instance 신원 버퍼 비교;식별자→원래 기하→속성 조회를 깊이 레이어로 연결하기;예시삼각형7의 세 꼭짓점과 보간 가중치에서UV복원하기;삼각형 경계에서 미분·MIP 선택의 잘못된 결과 비교;저장 대역폭 절감과 원래 자료 접근·복원 비용의 교환;공식 샘플 시점과 발명·게임채택 시점을 구별하기'],
    '18m': ['mobile-tile-memory', '화면 타일 내부 저장과 재질→조명의 다른 분류축;하드웨어 타일과Forward/Deferred·소프트웨어 광원 목록을 분리하기;타일 내G-buffer와 외부메모리의 다른 높이·화살표;API·기기·패스 구조가 달라지며 외부 쓰기가 필요한 경우;불투명 전면 저장 뒤 별도 투명 Forward 경로;재질·광원·투명도·대역폭에 따른 경로 공존'],
    '19': ['path-budget', '2023패치1.62Overdrive 기술미리보기의 실제 게임 조건;카메라→표면→재질방향의 여러 바운스와 기여;확산·광택 방향분포와 기여/PDF의 다른 가중치;기여2,8의 평균5와 올바른 확률 보정 비교;광원 선택·BRDF 선택의MIS 가중치를 다른 경로로 연결;생존확률0.8의 roulette 종료와 살아남은1/0.8 보정;확률 종료와 항상 절단·최대 바운스 편향을 구별하기;독립표본N→4N의 오차1→1/2와 상관조건;표본 배정·재사용·남은 노이즈 복원의 단계 연결'],
    '20': ['ray-reconstruction-inputs', '단순 색 평균에서 진짜 경계·세부까지 지워지는 모습;깊이·법선·재질과 유효한 과거 대응으로 필터 범위 제한;2023RR의 여러 디노이저 대체 복원 역할;SR·FG·RR의 다른 입력과 출력 깊이층;반사 글자·가는선·이동 물체의 시간 안정성 비교;같은 카메라·해상도·노출·조명 조건과 홍보·측정 근거 분리'],
    '21m': ['many-light-selection', '2024UE5.5실험 데모의 많은 직접광과 유용한 표본 집중;후보 선택과 실제 가시성 레이를 분리하기;Forward+후보 목록 평가와 확률 표본·재사용·노이즈 처리의 차이;복잡한 가림·빠른 기여 변화에서 표본 부족 비교;MegaLights직접광과Lumen간접광의 다른 책임;2025UE5.7실험 NaniteFoliage의 기하 확장과 간접광을 분리하기'],
    '21a': ['transparent-hair-layers', '가장 앞의 깊이 뒤에도 여러 투명 표면 배치하기;alpha 합성과 실제 매질 흡수의 다른 의미;검정 바탕 alpha0.5빨강·파랑 두층의 앞0.5·뒤0.25를 뒤집기;교차 표면에서 물체 중심 정렬과 픽셀 깊이 순서 비교;깊이 필링 패스와 픽셀 연결목록 저장·정렬 비교;weighted OIT근사와 정확 정렬의 높은alpha·색대비 차이;머리카락의 피복·방향반사·자료구조를 다른 층으로 분리;제작발표 시점과 발명·비공개구현 근거를 구별하기'],
    '22': ['dlss-feature-io', 'SR·RR·FG·MFG 기능을 서로 다른 입출력층에 놓기;4/4.5의 복원·생성 변경을 시뮬레이션과 구별하기;DLSS5 색·모션 기반 외관 출력의 범위;개발자 제어와 개별 기능 설정;공식 NBA2K27 후보의 ON/OFF와 표시 프레임을 구분하기'],
    '22p': ['exposure-tonemap', '선형 HDR 조명 값과 최종 표시 범위를 다른 평면에 놓기;노출 배율과 비선형 tone mapping곡선을 분리하기;블룸의 화면 번짐과 실제 GI 색 운반의 차이;초점·거리의DOF와 노출시간 운동의 motion blur;텍스처 입력변환→선형조명→최종색 변환의 누락·중복 비교;기하·가시성·재질·복원·후처리의 최종 픽셀 연결'],
    '22r': ['frame-resource-inspector', '엔진 버전·경로마다 다른 실제 이벤트와 자원 화살표;반사·그림자 페이지·G-buffer를 확인할 비교 목적 선택;API·경로·내부/출력 해상도·카메라 설정 기록;자원의 크기·형식·층·MIP와 실제 사용 관계;비선형 깊이와 reversedZ의 값규약;normal시각화와 표면 색·인코딩을 분리;광원→그림자자원→읽는패스·분할/페이지 선택;SSR miss에서 probe·다른 추적으로 이어지는 대체 입력'],
    '22rb': ['history-final-output', '볼륨 밀도·조명·투과율의 서로 다른 공간 격자;이전·현재 입력과 속도·깊이의 대응 거부;실제 HDR→노출→톤매핑·복원·UI의 순서와 준비 도식 구별;출력 명령에서 입력 생산자와 뒤 소비자로 거꾸로 연결;캡처 추가비용과 실제GPU반복측정의 구분;평균·실행횟수·변동·로딩·캐시 상태의 측정조건;관찰한 현상과 자원·구현을 확인한 근거의 별도 기록'],
    conclusion: ['four-episode-input-map', '밝기 숫자→베이크→실시간 그림자→공간표현→레이→복원의 공존;서로 다른 저장 정보가 답하는 질문;화면 깊이·공간 근사·삼각형의 검사범위;표본·페이지·캐시·과거프레임의 비용과오류;입력→저장→검사→갱신→출력으로 좋아지는 이유·깨지는 이유 연결'],
  },
};
const result = {schemaVersion:1,status:'prepared-only',createdAt:new Date().toISOString(),
  actualAnimatedPixelsReviewed:false,measuredTimingAttached:false,finalUseApproved:false,
  bodyRatioApproved:false,sourceRightsApproved:false,newRasterImagesCreated:0,
  rules:{explanationStyle:'research-black-v1; current01-04 explicit user revision; black background, white body, yellow headings and semantic vectors',
    projection:'real top/side faces, spatial occlusion, separate depth planes and meaningful motion',
    caption:'boxed-white-forest-v1; fixed960,970/MC0,430; keep diagrams above narration zone',
    source:'all original algorithm models are explanation; approved actual game/engine footage inserted separately',
    timing:'each paragraph beat follows measured narration; proportional paragraph timing remains provisional'},episodes:[]};
for (const episode of ['03','04']) {
  const file=path.join(root,`projects/game-lighting-history-${episode}/script/narration.ko.json`);
  const script=read(file);
  if(Object.keys(rows[episode]).length!==script.scenes.length)throw Error('Scene count changed');
  const scenes=script.scenes.map(scene=>{
    const row=rows[episode][scene.id];if(!row)throw Error('Missing model'+scene.id);
    const beats=row[1].split(';');if(beats.length!==scene.lines.length)throw Error('Missing paragraph beats '+scene.id);
    return {id:scene.id,model:row[0],paragraphs:scene.lines.map((text,i)=>({number:i+1,text,
      projectedMotion:beats[i],actualTiming:null,pixelsReviewed:false}))};
  });
  result.episodes.push({slug:`game-lighting-history-${episode}`,scriptSha256:sha(file),sceneCount:scenes.length,
    paragraphs:scenes.reduce((n,s)=>n+s.paragraphs.length,0),scenes});
}
const output=path.join(__dirname,'local/spatial-paragraph-plan-v1.json');
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,episodes:result.episodes.map(e=>({slug:e.slug,scenes:e.sceneCount,paragraphs:e.paragraphs})),images:0}));
