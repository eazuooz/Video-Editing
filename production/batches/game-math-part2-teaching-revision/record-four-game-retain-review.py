"""Record the bounded cross-game review of two already delivered episodes.

Does not render, upload, reschedule, approve rights, or replace previous QA.
"""
from pathlib import Path
from datetime import datetime
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = B / 'cross-game-review-20261011'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(8*1024*1024), b''): h.update(part)
    return h.hexdigest()

CASES = {
 'game-math-plane-distances-v2': [
  ('Serious Sam 2', ['02'], '유한한 발판의 끝과 끝없는 평면은 다릅니다. 표면까지의 수직 거리와 실제 발판 안에 남는 검사를 구분합니다.'),
  ('Portal 2', ['PG01','PG03'], '바닥에서 튀어 올라 다시 접촉하는 동작과 기울어진 패널을 비교합니다. 면의 방향, 거리, 유한한 가장자리를 따로 봅니다.'),
  ('Noita', ['05','PG02'], '수평/기울어진 지형과 캐릭터의 접근을 비교합니다. 화면 위 설명용 방향과 게임 세계의 법선 측정은 구분합니다.'),
  ('A Story About My Uncle', ['08'], '그래플이 삼각형 표식에 연결되는 위치와 카메라 변화로 앞면 순서·투영·세 기준점을 연결합니다. 표식은 전체 바위의 메시 증거가 아닙니다.')],
 'game-math-triangle-addresses-v2': [
  ('Noita', ['11','17','19'], '세 기준점을 함께 유지하며 위치를 비교하고 높이가 다른 표면은 같은 평면으로 취급하지 않습니다.'),
  ('Portal 2', ['PG04','PG06','PG07'], '면 위와 실제 발판 내부, 공중 위치와 바닥 투영, 위치와 표면에 저장된 값을 구분합니다. 젤 효과는 색 보간의 증거가 아닙니다.'),
  ('A Story About My Uncle', ['14'], '카메라가 움직일 때 삼각형의 세 기준점도 함께 추적합니다. 화면의 가까워 보이는 정도가 세계 공간의 가중치와 같다는 주장을 피합니다.'),
  ('Serious Sam 2', ['21'], '지붕과 벽의 위치별 색을 보고 위치 찾기→속성 계산의 순서를 설명합니다. 별도 선형 RGB 계산은 정의한 예제이며 실제 엔진 색 처리로 단정하지 않습니다.')]
}
PAGES = {
 'game-math-plane-distances-v2': ['composition-review/composition-01.jpg','composition-review/composition-04.jpg','final-detail-review/PG01-02.jpg','final-detail-review/PG02-02.jpg','final-detail-review/05-02.jpg','final-detail-review/PG03-02.jpg'],
 'game-math-triangle-addresses-v2': ['composition-review/composition-01.jpg','composition-review/composition-03.jpg','composition-review/composition-05.jpg','composition-review/composition-06.jpg','final-detail-review/PG04-02.jpg','final-detail-review/PG06-02.jpg']
}

inventory_path = R/'adopted-game-inventory.json'
inventory = read(inventory_path)
results=[]
for slug, cases in CASES.items():
    P=ROOT/'projects'/slug
    m=read(P/'project.json')
    ko=read(P/'script/narration.ko.json'); en=read(P/'script/narration.en.json')
    assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
    rows={s['id']:s for s in ko['scenes']}
    source=ROOT/m['paths']['videoBurnedCaptions']; digest=sha(source)
    prior=read(P/'production/current-pixel-review.json')
    native=read(ROOT/f'shared/output/{slug}/native-final-playback.json')
    assert digest==prior['sha256']==native['sha256']
    assert native['ended'] and native['playbackRate']==1
    adopted=next(x for x in inventory['projects'] if x['slug']==slug)
    assert set(adopted['selectedDistinctGames'])=={x[0] for x in cases}
    actual={x['sceneId'] for x in adopted['adoptedActualScenes']}
    game_cases=[]
    for game, ids, reason in cases:
        assert set(ids)<=actual
        game_cases.append({'game':game,'actualScenes':ids,'viewerConnection':reason,
                           'koNarration':[line for ident in ids for line in rows[ident]['lines']]})
    proofpaths=[P/'project.json',P/'script/narration.ko.json',P/'script/narration.en.json',
                P/'production/timeline.json',P/'production/footage-cuts.json',P/'production/footage-sources.json',
                P/'production/current-pixel-review.json',ROOT/f'shared/output/{slug}/native-final-playback.json']
    viewed=[ROOT/f'shared/output/{slug}'/x for x in PAGES[slug]]
    assert all(x.exists() for x in viewed)
    report={'reviewedAt':datetime.now().astimezone().isoformat(),'slug':slug,'currentCaptionedSha256':digest,
     'decision':'retain-current-delivered-episode','crossGameRevisionNeeded':False,'minimumDistinctGames':4,
     'distinctAdoptedGames':len(game_cases),'cases':game_cases,
     'wholeKoEnScriptsDirectlyRead':True,
     'reason':'각 독립 영상에 실제 게임4종이 이미 포함되어 있고, 입력·동작·결과와 수학의 적용 범위를 다른 장면에 연결합니다. 이름만 나열한 사례가 아닙니다. 기존 설명과 납품을 유지합니다.',
     'freshPixelReviewScope':'아래에 명시한 현재 최종 파일의 구도와 움직임 표본만 새로 직접 확인했습니다. 이전 전체 자막·정상 속도 재생 기록은 같은 SHA256임을 확인하고 별도로 보존합니다.',
     'freshDirectlyViewedPages':[{'path':x.relative_to(ROOT).as_posix(),'sha256':sha(x)} for x in viewed],
     'priorFullPixelReview':prior,'priorNormalSpeedPlayback':native,
     'sourceAndScriptEvidence':[{'path':x.relative_to(ROOT).as_posix(),'sha256':sha(x)} for x in proofpaths],
     'humanWholeListening':'pending-preserved','humanRightsComplete':False,
     'newRender':False,'newUpload':False,'scheduleChanged':False,'unrelatedApprovalsGranted':False}
    dest=R/(slug+'-retain-review.json');write(dest,report)
    adopted.update(status='four-game-content-reviewed-retain-current-delivery',coverageApproved=True,
                   wholeCurrentScriptsDirectlyRead=True,currentFinalMovingPixelsReviewed=True,
                   currentMixedAudioReviewed=False,crossGameDecision=dest.relative_to(ROOT).as_posix(),
                   crossGameRevisionNeeded=False)
    results.append({'slug':slug,'decision':report['decision'],'actualGames':4})
write(inventory_path,inventory)
print(json.dumps(results,ensure_ascii=False),flush=True)
