"""Prepare the explicitly requested visual-only D27/D28 revision.

This does not render, change any frozen input, or start Unity. The resulting
plan is a cut-exact brief for the single shared Unity capture worker.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REV = 'unity-visual-v2'
REQUEST = '설명 ppt 부분이 조금 글로만 되어있어서 공감이 잘안되 ... 유니티 ... 에셋 ... 설명 ppt 부분 보완해주고 다시 만들어줘~ 영상전부'

# Labels are deliberately brief. The frozen narration supplies the detail.
BRIEFS = {
    'in-game-cutscenes': {
        'cut002': ('conversation', '컷신이 이어 주는 것', ['이야기', '휴식', '다음 행동'], '두 인물이 마주 보는 장면에서 한 인물이 길 쪽으로 몸을 돌린다. 이야기의 시선이 다음 행동으로 이어진다.'),
        'cut004': ('formats', '같은 장면, 두 가지 방식', ['실시간 컷신', '프리렌더링 영상'], '같은 두 인물의 동작을 왼쪽 엔진 장면과 오른쪽 프레임 띠에 동시에 보인다. 오른쪽은 이미 저장된 순서의 그림이라는 차이만 표시한다.'),
        'cut005': ('frame-rate', '1초 동안 보여 주는 그림', ['60장', '30장'], '동일한 캐릭터가 같은 거리를 걷는 두 화면. 왼쪽은 매 프레임, 오른쪽은 2프레임마다 동작 상태를 갱신한다. 동일 시간의 위치는 같고 새 그림의 빈도만 다르다. 저장 영상 품질 일반화는 하지 않는다.'),
        'cut006': ('quality', '전환 순간의 차이', ['선명한 실시간 화면', '낮은 해상도의 저장 영상'], '같은 캐릭터와 카메라 구도를 유지한 선명/의도적으로 낮은 해상도 예시를 나란히 보여 준다. 예시 구현이라고 표시하며 모든 저장 영상이 낮은 품질이라고 암시하지 않는다.'),
        'cut016': ('viewing-reward', '장면만 따로 볼 수 있다면', ['돌파한 뒤 보는 장면', '영상만 따로 보기'], '왼쪽 캐릭터가 장애물을 넘어 장면의 화면 앞에 도착한다. 오른쪽은 같은 연출 화면으로 곧장 연결된다. 도전의 과정과 영상에 도달한 경로 차이를 눈으로 보여 준다.'),
        'cut020': ('advance', '끝내기와 속도 맞추기는 다르다', ['다음 구간', '빠르게 재생', '전체 건너뛰기'], '움직이는 인물 대화 장면 아래 3개의 작은 구간을 표시한다. 현재 구간에서 다음 구간으로 이동하고 속도를 높인 뒤, 전체를 건너뛰면 인물이 다음 길로 이동하는 세 결과를 짧게 비교한다.'),
        'cut021': ('playback-controls', '진행 속도를 고르게', ['1×', '1.5×', '구간 이동'], '동일 장면이 이어지는 동안 진행점이 일정 속도→더 빠른 속도로 움직인다. 구간을 선택하면 인물의 대응 장면 상태로 이동한다. 사용자가 고르는 조절을 보여 준다.'),
        'cut023': ('skip-scope', '건너뛰는 선택을 남기기', ['컷신', '스태프 크레디트', '다음 플레이'], '장면을 보는 인물 앞 화면에서 대화→크레디트 표현으로 넘어간다. 두 경우 모두 같은 건너뛰기 입력과 다음 길로 연결한다.'),
        'cut024': ('known-scene', '새 저장 파일 ≠ 첫 시청', ['처음 만든 저장', '이미 본 사람'], '같은 캐릭터가 다른 기기의 화면에서 같은 대화를 본 뒤 새 저장 슬롯 앞에 선다. 저장 파일은 비어 있지만 인물이 이미 본 장면을 가리킨다. 파일/사람을 명확히 나란히 놓는다.'),
        'cut026': ('skip-choice', '실수는 확인 입력으로 줄이기', ['계속 보기', '건너뛰기'], '두 선택을 같은 무게로 보여 주고 건너뛰기 선택 뒤 짧은 확인 표시가 생긴다. 캐릭터가 다음 길로 돌아간다.'),
        'cut027': ('qte', '보던 중 갑자기 입력을 요구하면', ['알림', '입력 기회', '실패 부담'], '인물이 편하게 장면을 보다가 버튼 알림과 짧아지는 입력 창이 뜬다. 첫 예시는 놓쳐 인물이 멈추고, 뒤 예시는 사전 알림→충분한 입력 창→누름→다음 행동으로 이어진다. 수치는 예시 구현이며 실제 게임 측정이 아니다.'),
    },
    'start-with-climax': {
        'cut001': ('opening-overview', '계속할 이유를 먼저 경험하게', ['첫 행동', '첫 위협', '첫 판단'], '한 캐릭터가 걷기/목표에 반응하기/두 단서 중 고르기를 이어서 수행한다. 세 행동에 해당하는 작은 사물과 표식만 보여 주며 세 개 텍스트 카드로 대체하지 않는다.'),
        'cut003': ('early-peak', '작은 절정을 앞에 놓기', ['첫 조작', '매력이 드러나는 순간'], '캐릭터가 시작 지점에서 멀리 있는 최종 결전 모형을 바라본다. 가까운 첫 장애물을 넘어 성취하는 지점을 먼저 밝힌다. 마지막 대결 자체를 앞으로 옮긴다는 뜻으로 보이지 않게 한다.'),
        'cut005': ('control', '조작 → 반응 → 목표', ['조준', '맞음', '위협 감소'], '이전 DOOM 실제 화면을 유지한 작은 증거 삽입 옆에서 자체 캐릭터가 연습 표적을 조준하고 표적이 뒤로 반응한다. 실제 DOOM 내부 구현이라고 표시하지 않는다.'),
        'cut008': ('information-order', '사건 순서와 전달 순서', ['배경 → 사건', '사건 → 필요한 배경'], '상단은 마을/친구/사건의 세 미니 장면. 하단은 같은 장면 조각을 사건/왜?/배경 순서로 옮긴다. 사건 자체는 바뀌지 않고 보여 주는 순서만 달라진다. 11.933초 발화에 맞춰 재배열한다.'),
        'cut010': ('participation', '궁금증은 행동에서 생긴다', ['직접 해보기', '왜 이런 일이?'], '캐릭터가 막힌 길을 발견하고 옆의 표지/단서를 살펴본다. 먼저 행동한 결과가 배경 설명을 듣는 이유로 연결된다.'),
        'cut012': ('control', '시작한 사람에게 조작을', ['내가 움직인다'], '이전 프레임의 게임 증거와 함께 입력 화살표에 맞춰 캐릭터가 한 번 직접 이동한다. 2.16초 안에 단 하나의 원인/결과만 보여 준다.'),
        'cut019': ('information-order-return', '경험 뒤에 생기는 질문', ['어떤 적?', '왜?', '어디로?'], '앞서 움직인 캐릭터와 막힌 길을 다시 보여 준다. 상대, 사건 흔적, 다음 길을 차례로 강조하며 필요한 설명이 목표에 붙는다.'),
        'cut024': ('early-peak-fallback', '큰 사건을 옮길 수 없다면', ['설명 구간', '첫 조작'], '시작과 첫 조작 사이에 놓인 길고 작은 배경 설명 판들을 줄여 첫 조작까지의 거리가 짧아진다. 도입의 필요한 학습을 없애지 않고 바로 쓸 규칙은 남긴다.'),
        'cut025': ('rule-use', '바로 쓸 규칙부터', ['알려주기', '써보기'], '기존 독립 게임의 스핀 전후 증거 이미지는 유지하고 옆의 자체 캐릭터가 방향 표식대로 돌아서 수정 모형을 깨뜨린다. 실제 게임 스핀 기능으로 오인하지 않게 자체 설명 장면임을 표시한다.'),
        'cut028': ('first-act', '첫 재판에서 역할을 경험', ['변호하기', '사건 따져보기'], '기존 역전재판 첫 재판 스크린샷을 함께 유지한다. 자체 테이블의 단서 물건과 인물 두 명을 보여 주고, 캐릭터가 증거 쪽을 가리키며 말/증거의 대응을 드러낸다.'),
        'cut029': ('evidence-selection', '말과 증거를 맞춰 보기', ['증인의 말', '고른 증거', '맞는가?'], '검증된 첫 재판 전후 스크린샷 옆에서 자체 테이블의 사진/물건 단서를 하나 고른다. 선택된 물건이 증인 말 표시 옆으로 이동해 비교된다. 특정 게임의 정답이나 없는 사실을 만들지 않는다.'),
        'cut032': ('closing-actions', '재미를 먼저 경험시키기', ['첫 행동', '첫 위협', '첫 판단'], '처음 본 자체 캐릭터와 같은 구도에서 이동/장애물 반응/단서 선택을 차례로 다시 연결한다. 전체 대본의 결론을 행동으로 회수하며 첫 재판 증거도 마지막에 유지한다.'),
    },
}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def main():
    for slug,brief in BRIEFS.items():
        p=ROOT/'projects'/slug
        project=json.loads((p/'project.json').read_text(encoding='utf-8-sig'))
        old=json.loads((p/'production/batch-v1/edit-plan.json').read_text(encoding='utf-8-sig'))
        narration=json.loads((p/'script/batch-v1/narration.ko.json').read_text(encoding='utf-8-sig'))
        paragraphs={f"{s['id']}-p{i:02d}": t for s in narration['scenes'] for i,t in enumerate(s['lines'],1)}
        cuts=[]
        for c in old['cuts']:
            if c['kind']!='explanation': continue
            mode,title,labels,action=brief[c['id']]
            cuts.append({
                'id':c['id'],'scene':c['scene'],'globalStartFrame':c['startFrame'],
                'globalEndFrame':c['endFrame'],'frames':c['frames'],
                'startSeconds':c['startFrame']/60,'endSeconds':c['endFrame']/60,
                'originalMode':c['mode'],'mode':mode,'title':title,'labels':labels,
                'paragraphIds':c['paragraphIds'],'narration':[paragraphs[x] for x in c['paragraphIds']],
                'speechCuesSeconds':c.get('visualCues',[]),'visibleBeforeActionResult':action,
                'oldDiagramOptions':c.get('diagramOptions',{}),
                'renderer':'Unity asset-based demonstration + readable editorial labels',
                'kind':'explanation','notCommercialGameFootage':True,
                'scenePath':f'Assets/VideoScenes/{slug}/{REV}/{c["scene"]}-{c["id"]}.unity',
                'sceneSaved':False,'actualCaptureReviewed':False,
            })
        dest=p/'production'/REV; dest.mkdir(parents=True,exist_ok=True)
        output={
            'schemaVersion':1,'slug':slug,'episode':project['seriesOrder'],'revision':REV,
            'status':'cut-exact-visual-plan-awaiting-shared-unity-capture',
            'userEvidence':REQUEST,'scope':'All explanation cuts in selected D25–D30; this plan owns D27/D28 only.',
            'preserve':['story','claim and chapter order','narration PCM','final mixed AAC','all independent-gameplay cuts','exact cut frames','KO/EN SRT','original masters'],
            'baselinePlan':'projects/'+slug+'/production/batch-v1/edit-plan.json',
            'baselinePlanSha256':sha(p/'production/batch-v1/edit-plan.json'),
            'baselineCaptioned':project['paths']['videoBurnedCaptions'],
            'baselineClean':project['paths']['videoClean'],
            'baselineSha256':project['localFinalReview']['sha256'],
            'fps':60,'width':1920,'height':1080,'totalFrames':old['totalFrames'],
            'explanationFrames':sum(c['frames'] for c in cuts),'cuts':cuts,
            'sharedAssetsRequested':[
                {'productId':'011','purpose':'Recurring recognizable rigged player and speaking partner; inspect actual rig/material/animation before capture.','preferredPrefab':'Assets/ThirdParty/YamyamAssetLibrary/011-cartoon-city-massive-pack-characters-unity-godot-fbx/Generated/Prefabs/Character_1_1_1_f0ff54f64441.prefab'},
                {'productId':'081','purpose':'Visible practice target, props and stage objects that change after player action; exact chosen assets/rights resolved by shared capture owner.'},
                {'productId':'076','purpose':'Optional blaster only for D28 cause/action/target response; avoid extra visual violence.'},
            ],
            'layout':{'background':'black','heading':'warm yellow','body':'white','maxLabelLines':2,'captionProtectedRect':[150,892,1784,1060], 'heroArea':[140,200,1780,820],'mobileWidth':375,'type':'우리 구현'},
            'sourceAudioStrategy':'Copy the current frozen final AAC unchanged into both new masters; no new mix or TTS.',
            'review':{'required':['actual chosen prefabs/rig/animation','frame exact new captures','all explanation action/reveal states at 1080p and375px','caption clearance','unchanged gameplay proof','paired final full decode','same AAC and SRT proof'], 'humanWholeReview':'new revision pending'},
            'platformMutationAuthorized':False,
        }
        (dest/'plan.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(slug,len(cuts),output['explanationFrames'])

if __name__=='__main__':main()
