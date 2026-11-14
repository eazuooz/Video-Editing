"""Record feasibility judgments only, without authorizing a remake."""
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from audit_pictures import HERE,ROOT,WORK,DELIVERY,read,save,sha,source_catalog

# An eligible example illustrates an observed result; it does not expose hidden
# animation curves, simulation ticks, hit volumes or a shipped game's rig.
DECISIONS={
'A03':dict(verdict='영상 중심 대체 적합',games=['Monster Hunter Wilds — 대검'],
    method='한 공격을 정상 속도로 먼저 보고, 같은 공격의 대기·준비·타격·후속 자세를 정지해 한 줄에 배치. 타격 기준으로 느린 재생을 동기화.',
    preserve='공격 판정 활성 구간과 다음 조작 가능 시점은 동작 단계와 구별하는 시간표 유지.',
    finding='현재125초는 대기/현재 팔 윤곽을 겹친 엔진 시연. 실제 표적과 대검의 접촉이 있는 장면이 단계의 역할을 더 직접적으로 보여 줌.',
    caveat='원본18–23초 사이에 카메라 컷/동작 전환이 있어 전체를 한 공격으로 묶으면 안 됨.25–28초 보충 표본에서 표적 앞 연속 행동 확인; 정확한 공격 시작/끝은 조밀한 인아웃 검수 후 고정.',
    keys=['great'],priority=2),
'A04':dict(verdict='영상 중심 대체 적합',games=['Hades II — 멜리노에의 도끼','Cuphead — 연속 사격'],
    method='빠른 첫 반응과 오래 힘을 모으는 공격을 각각 정상 속도→0.5배→첫 변화 정지 화면으로 관찰. 최초로 자세가 바뀌는 부분을 표시.',
    preserve='같은 도착 시각에서 준비 구간만 바꾼 반사실 비교는 짧은 시간축/명시한 편집 실험으로 설명.',
    finding='현재110초는 두 마네킹의 팔 궤적 비교. 게임의 공격 목적과 첫 신호를 먼저 보여 주면 비교 기준이 쉬워짐.',
    caveat='서로 다른 기술을 같은 조건의 실험이라고 부르지 않음.입력 표식이 없는 녹화로 입력 지연이나 정확한 발동 프레임을 측정하지 않음.하데스 보유판본은 Early Access v0.90437.',
    keys=['hades-training','cup-first-level'],priority=2),
'A05':dict(verdict='영상 중심 대체 적합',games=['Princess Peach: Showtime! — 검객 피치','Hi-Fi RUSH — 차이'],
    method='검을 내밀기 전·뻗은 순간·정리 자세를 크게 정지 비교. 공격 팔/버티는 다리와 몸 사이 빈 공간을 윤곽선으로 표시.',
    preserve='플레이 카메라에서 보이지 않는 깊이/기준 평면은 짧은 위쪽 원리 도식 유지.영상 편집으로 골라 멈춘 자세와 게임 자체 히트 스톱을 구분.',
    finding='현재100초는 한 마네킹이 넓은 여백 속 작게 배치됨.피치17–20초 보충 표본의 무대/검/상대가 자세의 목적을 함께 보여 줌.',
    caveat='하이파이4–9초는 보스/효과가 차이를 가리는 구간이 있어 주 비교로 쓰기 약함.피치를 우선하고 차이는 윤곽이 드러나는 순간만 선택.',
    keys=['peach-sword','hifi-beat'],priority=1),
'A06':dict(verdict='대체 가능 · 기존 시연 유지 추천',games=['Street Fighter 6 — 마리사','Monster Hunter: World — 해머·헤비보우건'],
    method='맞은 뒤 팔이 더 나가는 순간→팔 회수→다음 자세를0.5배로 관찰.마리사10.5–13초 보충 표본은 측면 카메라와 몸 전체가 선명.',
    preserve='사용자가 좋다고 한 현재 시연 유지.보충이 필요하면 실제 게임 분석만 추가.조작 복귀는 입력 근거가 있을 때만 실제 수치로 표시.',
    finding='현재120초는 타격 이후/입력 분기/다음 행동을 나란히 보여 줌.다른 편보다 단계 관계가 이미 분명해 교체 우선순위가 낮음.',
    caveat='해머3.4–8.25초는 배경/몬스터/카메라 변화가 커 주 비교로는 마리사가 더 명료함.공격 종료·입력 복귀·대기 복귀를 하나로 묶지 않음.',
    keys=['marisa-follow','mhw-hammer','mhw-hbg-shots'],priority=4),
'A07':dict(verdict='영상 중심 대체 적합',games=['Luigi’s Mansion 3 — 공포 몸짓','Spiritfarer — 포옹','Clock Tower 3 — 앨리사'],
    method='한 원본을 크게/실제 플레이 크기로 동시 표시.얼굴의 세부가 작아져도 팔·어깨·전신 행동이 남는지 비교.',
    preserve='모션 캡처를 수정하는 이유는 관계도로 설명하고 실제 게임이 어떤 녹화 기술을 썼는지 추측하지 않음.',
    finding='현재140초는 중립/만세형 몸짓이 분리된 마네킹.루이지가 도망가는 이유와 포옹 상대가 보이는 실제 상황은 감정에 공감하기 쉬움.',
    caveat='주관적 감정 차이는 같은 인물·동일 장면의 크기 비교를 먼저 하고 다른 게임 비교는 보강으로 사용.',
    keys=['luigi-run','spiritfarer-embrace','clock-retained'],priority=1),
'A08':dict(verdict='영상 중심 대체 적합',games=['Ring Fit Adventure — 전사Ⅰ자세','Clair Obscur: Expedition 33 — 마엘'],
    method='링 피트의 팔을 올린 자세를 크게 정지하고 몸통의 흐름→팔 사이 공간→앞무릎/지지발을 차례로 표시.마엘의 무기/외투 윤곽으로 보강.',
    preserve='선은 포즈를 읽는 편집 가이드이며 실제 질량 중심 측정이 아님.수정 지시는 원본 위 정지 리터칭으로 분리 가능.',
    finding='현재130초의 골반/어깨에 손을 둔 마네킹은 본문의 링 머리 위 자세와 대응이 약함.링 피트 실제 전사Ⅰ자세의 팔·발 관계가 훨씬 직접적.',
    caveat='보유 원본은1920×1080/30fps.1배 또는0.5배와 정지 자세 비교를 우선;0.25배 장시간 재생은 피함.프레임을 늘려 없는 자세를 만들지 않음.',
    keys=['ringfit-warrior1','maelle-no-commentary'],priority=0),
'A09':dict(verdict='게임 영상 + 원리 도식',games=['Cuphead — 구피 르 그랑','Kirby’s Dream Land','Slime Rancher 2'],
    method='착지/눌림/도약의 실제 윤곽을0.5배와 정지3장으로 비교하고 같은 폭·높이 기준선을 붙임.',
    preserve='스케일링·넓이/부피·블렌드 셰이프의 차이는 도식 유지.손 크기 과장도 실제 게임에 그 결과가 명확히 보이는 경우에만 대체.',
    finding='현재200초는 이미 Manim 넓이/부피 도식.이 부분까지 전투 영상으로 덮으면 설명의 근거가 사라짐.',
    caveat='2D 윤곽만으로3D 깊이/질량/변형 알고리즘을 추정하지 않음.구피23.2–24.1초에 낮고 넓어진 윤곽을 확인했으나 정확한 착지 이벤트는 추가 조밀 검수 필요.',
    keys=['cup-goopy','dream-retained','slime-bounce'],priority=2),
'A10':dict(verdict='영상 중심 대체 적합',games=['Street Fighter 6 — 주리','Super Mario Odyssey — 피격/회복'],
    method='접촉 직전·첫 피격·밀림/착지·회복을 한 화면에 배치.연속 공격은 명중 순간으로 맞춰0.5배 비교하고 맞은 부위를 표시.',
    preserve='실제 루트 노드/판정 수정은 바닥 기준의 짧은 관계도로 유지.같은 캐릭터의 반응을 먼저 보고 마리오로 체형 차이를 보강.',
    finding='현재102초는 접촉 상대 없이 넘어지는 마네킹 단독 시연.누가 어디를 맞았는지 보이는 주리 장면이 원인과 결과를 직접 연결함.',
    caveat='샘플29–32.5초는 여러 차례 공격이 있으므로 한 타격씩 분리.가드/카운터/피격을 구분하고 상·중·하9종이 모두 확보됐다고 주장하지 않음.',
    keys=['juri-hit-b','odyssey-cactus-hit'],priority=0),
'A11':dict(verdict='게임 영상 + 원리 도식',games=['Dead Cells','Paper Mario: The Thousand-Year Door (2024)'],
    method='실제 원본의 주요 자세와 유지 구간을 먼저 관찰.같은 클립의 시간 배분만 바꾼 편집 비교는 명시한 편집 실험으로 A/B를 구성할 수 있음.',
    preserve='시작/끝/전체 길이를 고정한 보간·타이밍 비교와 반환 경로는 시간표/키 포즈 관계도로 남김.새 중간3D 자세 생성은 원본 영상만으로 불가.',
    finding='현재108초는 같은 회전 발차기의 두 시각 비교.원본 게임 관찰은 힘의 리듬을 더 쉽게 보여 주지만 내부 키/커브를 노출하지는 않음.',
    caveat='단순히 원본1배와0.5배를 비교하면 전체 길이가 달라져 원래 주장(동일 총시간의 다른 시간 배분)을 입증하지 못함.길티기어 독립 FHD 소스는 기존 SOURCE_HOLD를 유지.',
    keys=['deadcells-motion','paper-mario'],priority=2),
'A12':dict(verdict='영상 중심 대체 적합',games=['Animal Crossing: New Horizons — 표정','Clair Obscur: Expedition 33 — 루네'],
    method='정면/비슷한 얼굴 방향으로 맞춘 중립→변화 표정을 크게2분할.눈썹·눈꺼풀·입을 하나씩 강조하고 얼굴 크기를 줄여 재확인.',
    preserve='수정 지시 리터칭은 실제 정지 화면 위에 그린 목표 그림이라고 표시.서로 다른 표정을 눈썹 하나만 조작한 실험으로 부르지 않음.',
    finding='현재90초는 이미 루네의 실제 게임 얼굴4분할.엔진 교체보다 작은 패널/얼굴 방향 변화/미세한 차이 문제를 먼저 해결해야 함.',
    caveat='동물의 숲11.25–14.25초는 주로 깜박임과 작은 얼굴 변화.기쁨/분노/슬픔의 폭넓은 리액션 모음이 모두 확보된 것은 아님.',
    keys=['acnh-catch-expression','lune-clean-camp'],priority=1),
'A13':dict(verdict='영상 중심 대체 적합',games=['Super Street Fighter II Turbo / Ultra Street Fighter IV — 디제이','Super Mario Bros. Wonder'],
    method='같은 캐릭터의 좌/우 방향을 실제 녹화에서 따로 골라 얼굴·앞손·바지 글자를 같은 크기로 정지 비교.방향 전환은1배 후 느린 재생.',
    preserve='회전과 반전의 차이, 소품 손 교체, 플레이 카메라에서 숨겨진 방향은 짧은 도식 유지.',
    finding='현재106초는 주황 마네킹 좌우 비교.실제 디제이의 얼굴/앞손/MAXIMUM 글자는 반전이 필요한 이유를 바로 보여 줌.',
    caveat='확보 장면의 양 방향 자세는 다른 시각의 실제 원본.편집 화면 좌우 반전을 게임의 실제 동작 증거로 쓰지 않음.3D 뒷면은 카메라를 돌린 녹화 없이는 복원 불가.',
    keys=['sf2-deejay','sf4-deejay','wonder-turn'],priority=0),
'A14':dict(verdict='게임 영상 + 원리 도식',games=['Horizon Zero Dawn — 조준/이동','Splatoon 3 — 이동하며 조준'],
    method='무기/상체 동작을 유지하면서 하체가 다음 행동으로 이어지는 구간을0.5배 관찰.끊김/발 미끄러짐을 판단할 기준점을 표시.',
    preserve='두 클립의 재생 위치·가중치·전환 시간·경사 발 목표는 짧은 원리 도식으로 분리.단순 영상 디졸브는 관절 블렌딩 비교로 사용하지 않음.',
    finding='현재98초는 즉시 전환과14프레임 블렌드가 나란히 보임.실제 게임은 자연스러운 결과를 보여 주고 도식은 왜 그런지 설명하는 역할이 적합.',
    caveat='관찰 표본8.5–12.5초는 회피→조준 포함.이걸 활 내림→걷기로 잘못 설명하지 않음.게임의 실제 가중치나 전환값은 화면만으로 측정 불가.',
    keys=['hzd-aim-move','splatoon-moving-fire'],priority=2),
'A15':dict(verdict='영상 중심 대체 적합',games=['Half-Life: Alyx — 병 잡기/놓기','Ghostwire: Tokyo — 손동작'],
    method='병목을 감싼 손→놓음→병 몸통을 잡은 손을 크게 관찰하고 물체 축/손가락 방향을 표시.손 자체가 행동을 알리는 고스트와이어로 보강.',
    preserve='관절 제어와 미리 정한 손 모양 교체, 제어점 수/비용은 손 구조 도식으로 유지.서로 다른 게임의 손을 GPU 성능 비교로 해석하지 않음.',
    finding='현재85초는 허벅지 옆 펴진 손과 굽은 손 비교로, 물체와 손의 관계가 희미함.알릭스19–20.4/26초 표본은 실제 병과 손가락의 관계가 분명.',
    caveat='19–20초에는 병을 이미 잡은 상태.시작 잡기라고 부르지 않음.21.8–24.6초의 내려다보는 빈 구간은 반복 설명용으로 길게 사용하지 않음.',
    keys=['alyx-grip','ghostwire-cast'],priority=0),
'A16':dict(verdict='게임 영상 + 원리 도식',games=['Monster Hunter: World / Iceborne — 태도·랜스','Elden Ring','Metroid Dread — 근접 카운터'],
    method='실제 명중/빗나감/맞은 뒤 반응을 느리게 보고 검끝과 표적의 화면 위치를 표시.',
    preserve='히트박스/허트박스·활성 구간·측면/위쪽 깊이 비교는 명시한 원리 도식으로 유지.게임 화면 위 상자는 관찰 안내로 제한.',
    finding='현재92초는 두 마네킹이 모두 활성·미접촉 상태로 보여 차이를 즉시 읽기 어려움.실제 접촉 결과를 먼저 보면 판정 도식의 질문이 선명해짐.',
    caveat='태도14.5–18.5초는 큰 몬스터와 불꽃이 경로를 가리는 순간이 있음.효과가 적은 랜스/드레드 구간을 우선 검토.공식 디버그 없이는 실제 판정 영역을 그린 것처럼 표시 불가.',
    keys=['mhw-longsword','mhw-lance','elden-jump','dread-counter-c'],priority=1),
'A17':dict(verdict='게임 영상 + 원리 도식',games=['ARMS — 리본걸·헬릭스','Cuphead — 칼라 마리아'],
    method='늘어나는 팔과 휘어지는 윤곽을 정상 속도/느린 재생/정지로 연결하고 끝점뿐 아니라 중간 형태를 표시.',
    preserve='FK/IK의 제어 출발점, 같은 손 목표에서 팔꿈치 힌트 변경, 추가 제어점과 표면 변형은 간단한 관절 그림으로 유지.',
    finding='현재80초는 이미 관절 원리 도식과 작은 UE 손 영상.리본걸 원본의 나선형 팔은 표현 목표를 보여 주는 데 적합.',
    caveat='헬릭스 보유9–14/22–28초는 상대측이 작아 가까운 윤곽 분석에 약함.리본걸 전경 샷을 우선.완성 화면으로 실제 뼈 수나 IK 솔버 사용을 입증하지 않음.',
    keys=['arms-ribbon','arms-helix','cala-retained'],priority=2),
'A18':dict(verdict='게임 영상 + 원리 도식',games=['Luigi’s Mansion 3 — 고개/시선','Untitled Goose Game — 목/머리','The Last Guardian — 트리코'],
    method='얼굴을 크게 고정해 눈→고개→어깨의 순서를 느리게 관찰하고 숙임/옆돌림이 보이는 두 자세를 정지 비교.',
    preserve='같은 출발/도착 자세에서 한 축/두 축만 바꾼 결과, 회전 커브와 시간차는 간단한 축·곡선 도식 유지.',
    finding='현재84초는 이미 루이지 실제 원본과 회전 도식의 병행.게임 창을 확대하고 한 번에 한 축/눈동자만 표시하는 편이 효과적.',
    caveat='영상을 좌우로 뒤집거나 느리게 만든다고 한 축만 제거한 새 연기가 되지는 않음.진짜 회전값을 화면만으로 추정하지 않음.',
    keys=['luigi-lobby','goose-basket-start','trico-look'],priority=2)
}

def main():
    evidence=read(HERE/'evidence.json');catalog=source_catalog();rows=[]
    for e in evidence['episodes']:
        d=DECISIONS[e['id']]
        sources=[]
        for key in d['keys']:
            s=catalog[key]
            sources.append(dict(key=key,url=s.get('sourceUrl',s.get('url')),localFile=s.get('file'),
                existingEvidence='contrast-v5/footage/game-coverage-team-a.json or team-b/game-coverage.json; source-specific rights/audio records retained'))
        rows.append(dict(**e,**d,sources=sources,sampledPicturesInternallyInspected=True,
            narrationAction='When/if revision is selected, rewrite demo-specific phrases (same mannequin, controlled values, input timings) to match observed footage or an explicitly labeled diagram; retain lesson claims/order.',
            finalSourceCutLocked=False))
    supplements=[]
    for key,times in [('great',[25,26,27,28]),('peach-sword',[17,18,19,20]),('marisa-follow',[10.5,11.3,12.1,13]),
                      ('sf4-deejay',[1.5,2.5,6.5,8]),('arms-ribbon',[0,4,8,12]),('arms-helix',[22,24,26,28])]:
        source=catalog[key];file=Path(source['file']);digest=sha(file)
        if source.get('sha256'):assert digest==source['sha256']
        picture=WORK/(key+'-supplement.jpg')
        supplements.append(dict(key=key,sourceFile=str(file),sourceSha256=digest,sampleTimes=times,
            sheet=str(picture),sheetSha256=sha(picture),internallyInspected=True))
    result=dict(id='animation-footage-substitution-audit-20261115',requestedOn='2026-11-15',
        userRequest='언리얼 시연 대신 실제 영상의 느린 재생/프레임 비교로 대체 가능한 편별 목록 검수',
        scope=[r['id'] for r in rows],excludedUploaded=['A01','A02'],
        status='feasibility-audit-complete-no-production-authorized',episodes=rows,supplementaryDecodedSamples=supplements,
        summary={'gameAnalysisSuitable':10,'gamePlusPrincipleDiagram':6,'priority':['A08','A15','A10','A13','A05','A07','A12'],
                 'retainUserLikedDemo':'A06','notAllUnreal':['A09','A12','A17','A18']},
        editing=dict(sequence='Existing overview/relationship → normal-speed action with narration → same event0.5x or selected freeze → aligned phase comparison → normal-speed confirmation → existing recap',
            speed='Choose speed from real source cadence. Ring Fit currently30fps: favor1x/0.5x and frozen poses.59.94/60fps material permits clearer0.5x;0.25x only when needed.',
            sync='Align meaningful action events, keep source/output frame references. Do not confuse recording frame number with engine simulation or animation keyframe.',
            interpolation='Do not use invented motion-interpolated poses as evidence about original animation. Keep native frames/intentional held poses.',
            causalComparison='Different games/attacks show observed examples. Same-variable counterfactual claims require explicit edited experiments or a controlled diagram.',
            speech='Continue relevant explanation over observation; no automatic silent repeats. Do not replace a full lesson with gameplay highlights.',
            borders='Source aspect/UI/watermarks and fixed caption center remain protected; one large view or2panels, phase board held long enough to read.'),
        technicalSources=[
          dict(url='https://ffmpeg.org/ffmpeg-filters.html#setpts_002c-asetpts',checkedOn='2026-11-15',supports='Recorded video timestamps can be changed for slow motion.'),
          dict(url='https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect',checkedOn='2026-11-15',supports='Select frames/time ranges from decoded video.'),
          dict(url='https://www.bandainamcoent.com/news/tekken-8-patch-notes-v1-10-01',checkedOn='2026-11-15',supports='Official Photo Mode frame advancement up to60frames in Practice/Versus; not a claim of generic replay rewind/control.')],
        allMastersUnchanged=True,newTtsStarted=False,newEngineCaptureStarted=False,newVideoRenderStarted=False,
        platformChanged=False,sourceClearance='Existing rights evidence preserved; feasibility does not certify new edits/publication or pending sources.',
        auditMethod='Current KO master captions/body claims;16 current-master samples;16×6 ordered source frames;6 supplementary4frame sheets and existing hashed source observations. Not a whole-playback/listening audit.',
        updatedAt=datetime.now(ZoneInfo('Asia/Seoul')).isoformat())
    save(HERE/'report.json',result)
    html=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
          '<title>애니메이션 실제 영상 대체 검수</title><style>body{background:#080c0a;color:#f3f5ef;font:17px/1.7 system-ui;margin:0}main{max-width:1400px;margin:auto;padding:24px}h1,h2{color:#f2d787}a{color:#94d8c9}td,th{padding:14px;vertical-align:top;text-align:left;border-bottom:1px solid #34463b}table{border-collapse:collapse;width:100%}summary{cursor:pointer;color:#94d8c9}.scroll{overflow-x:auto}small{color:#b5c4b8}</style><main>',
          '<a href="index.html">기존 통합 검수본</a><h1>애니메이션 — 실제 게임 영상 대체 검수</h1>',
          '<p>16편 검수: 영상 분석 중심10편 / 게임 영상+원리 도식6편. 이번에는 검수만 했고 기존 완성본은 수정하지 않았습니다.</p>',
          '<p>우선 추천: A08 포즈 · A15 손가락 · A10 피격 · A13 반전. A06은 사용자가 좋다고 한 시연을 유지하는 편을 추천합니다.</p>',
          '<p>기본 속도에서 전체 행동을 먼저 이해한 뒤0.5배/필요한 정지 화면으로 분석합니다. 녹화된 프레임은 골라 볼 수 있지만, 화면에 없는 새 자세·내부 판정·혼합값은 복원할 수 없습니다.</p>',
          '<div class="scroll"><table><tr><th>편·주제</th><th>판정</th><th>추천 실제 게임</th><th>비교 방법·검수 근거</th></tr>']
    for r in rows:
        ep=r['id'];file=Path(r['currentMaster']['path']).name
        urls=' / '.join('<a href="'+escape(s['url'])+'">'+escape(s['key'])+'</a>' for s in r['sources'])
        html.append('<tr><td>'+ep+'<br>'+escape(r['title'].split('|')[0])+'<br><a href="'+ep+'/'+file+'#t='+str(r['currentDemoTime'])+'">현재 시연 '+str(r['currentDemoTime'])+'초</a></td>'
          '<td>'+escape(r['verdict'])+'</td><td>'+escape(' / '.join(r['games']))+'<br><small>보유 주 후보 '+str(r['sourceWidth'])+'×'+str(r['sourceHeight'])+' · '+str(r['containerFps'])+'fps</small><br>'+urls+'</td>'
          '<td>'+escape(r['method'])+'<details><summary>유지할 설명·관찰·추가 확인</summary><p>'+escape(r['finding'])+'</p><p>'+escape(r['preserve'])+'</p><p>'+escape(r['caveat'])+'</p></details></td></tr>')
    html+=['</table></div><h2>편집 방식</h2><p>개론/관계도 → 정상 속도 행동과 설명 → 핵심 구간 느린 재생 → 단계 정지 비교 → 정상 속도 재확인 → 기존 핵심 정리. 조용한 자동 반복을 늘리지 않습니다.</p>',
           '<p>다른 기술·다른 게임 비교는 관찰 예시이며, 동일 조건 실험으로 부르지 않습니다. 시간이 같은 보간 비교·가중치·판정·FK/IK는 실제 영상과 짧은 원리 그림으로 나눕니다.</p>',
           '<p><a href="https://ffmpeg.org/ffmpeg-filters.html#setpts_002c-asetpts">FFmpeg 느린 재생</a> · <a href="https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect">프레임 선택</a> · <a href="https://www.bandainamcoent.com/news/tekken-8-patch-notes-v1-10-01">철권8 공식 포토 모드 프레임 진행</a></p>',
           '<p><small>검수 범위: 현재 대사와 시연 표본, 후보 원본의 연속 시각6장씩 및 보충 표본. 실시간 전체 시청/청취나 새 편집본 완성으로 표시하지 않습니다. 기존 독립 녹화 출처와 권리 기록을 보존하며 정확한 제작 인아웃은 아직 확정하지 않았습니다.</small></p></main></html>']
    page=''.join(html);(HERE/'review.html').write_text(page,encoding='utf-8')
    (DELIVERY/'footage-audit.html').write_text(page,encoding='utf-8')
    save(HERE/'checkpoint.json',dict(stage='feasibility-audit-delivered',scope=result['scope'],report='report.json',
        localReview='http://127.0.0.1:9301/footage-audit.html',productionStarted=False,platformChanged=False,
        nextAction='User reviews replacement choices; do not infer authorization for a remake from this audit request.'))
    print('16 feasibility judgments;10 gameplay-led /6 gameplay+diagram. Masters unchanged.')
if __name__=='__main__':main()
