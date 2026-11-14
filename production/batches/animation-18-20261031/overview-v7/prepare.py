"""Integrate narrated conceptual openings; preserve all v6 speech and recaps."""
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE.parent / 'native-clips-v6'
SOURCE = Path('C:/Users/1/Videos/YamyamCoding/animation-native-clips-v6')
WORK = Path('C:/Users/1/Videos/YamyamProduction/animation-overview-v7')
OUTPUT = Path('C:/Users/1/Videos/YamyamCoding/animation-overview-v7')
KEY = 'animationOverviewRevision20261114'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def stamp(): return datetime.now(ZoneInfo('Asia/Seoul')).isoformat()

# start/end follow existing sentences; roadmap appears with the spoken overview.
# None of these illustrations asserts measured internal retail-game data.
DATA = {
 'A03': (19.2,34.95,27.75,'Attack Phases · 공격 동작의 단계',
         ['한 번의 공격에도', '서로 다른 역할의 동작이 있습니다.'],
         ['대기 자세','준비 → 타격','후속 동작과 조작'], 'phases'),
 'A04': (19.06,28.14,22.36,'Anticipation · 준비 동작',
         ['공격 전에 보이는 작은 변화가', '다음 행동과 힘을 미리 알려 줍니다.'],
         ['첫 변화 읽기','힘을 모으는 자세','무기에 맞는 준비'], 'anticipation'),
 'A05': (31.40,52.20,47.15,'Impact Poses · 타격 순간의 자세',
         ['타격 순간을 멈춰 보아도', '공격의 방향과 힘이 읽혀야 합니다.'],
         ['크기와 방향','몸의 비대칭','분명한 실루엣'], 'pose'),
 'A06': (21.19,32.35,24.47,'Follow-Through · 후속 동작',
         ['타격 뒤 이어지는 움직임이', '남은 힘과 몸의 무게를 전달합니다.'],
         ['왜 이어지는가','얼마나 남길까','다음 조작과 연결'], 'follow'),
 'A07': (23.14,35.20,26.86,'Readable Motion · 읽히는 동작',
         ['실제 몸짓을 그대로 옮겨도', '작은 게임 화면에서는 사라집니다.'],
         ['사라지는 정보','게임 동작으로 보완','실제 화면 크기'], 'readability'),
 'A08': (20.54,34.00,27.40,'Readable Poses · 읽히는 포즈',
         ['좋은 포즈는 몸 전체가', '같은 행동을 또렷하게 전달합니다.'],
         ['몸의 흐름','팔과 손의 윤곽','체중을 받치는 발'], 'body'),
 'A09': (19.45,35.45,27.15,'Squash and Stretch · 눌림과 늘어남',
         ['위치 이동에 형태 변화를 더하면', '힘과 속도가 더 분명해집니다.'],
         ['크기 변환','눌림과 늘어남','모양 직접 수정'], 'squash'),
 'A10': (36.45,54.47,45.05,'Hit Reactions · 피격 동작',
         ['맞은 뒤의 자세와 움직임이', '충격의 위치와 방향을 알려 줍니다.'],
         ['맞은 직후의 자세','동작 연결과 판정','다양한 상황의 읽힘'], 'reaction'),
 'A11': (41.80,62.36,53.60,'In-Betweening · 동작 사이의 연결',
         ['같은 시작과 끝 자세도', '사이의 시간과 경로에 따라 달라집니다.'],
         ['두 자세 사이','발차기의 시간 배분','주먹이 돌아오는 길'], 'timing'),
 'A12': (29.39,42.40,32.79,'Facial Animation · 표정 애니메이션',
         ['작게 보이는 얼굴에서도', '눈썹·눈·입이 감정을 전해야 합니다.'],
         ['감정이 읽히는가','그림으로 수정 방향','부위와 표현 범위'], 'face'),
 'A13': (21.09,43.80,35.90,'Mirroring · 좌우 반전',
         ['같은 동작도 보이는 방향에 따라', '전달되는 정보가 달라집니다.'],
         ['반전하는 방법','손과 장비의 변화','카메라에서 읽힘'], 'mirror'),
 'A14': (29.60,43.70,35.20,'Animation Blending · 애니메이션 블렌딩',
         ['두 동작의 자세를 섞어서', '움직임이 끊기지 않게 연결합니다.'],
         ['자세 섞기','비율과 재생 시간','방향과 공간의 조합'], 'blend'),
 'A15': (21.57,49.61,42.03,'Finger Animation · 손가락 애니메이션',
         ['잡는 물체의 모양과 두께에 따라', '손가락의 자세도 달라집니다.'],
         ['자연스러운 그립','손가락의 제작 비용','보이는 곳에 배분'], 'grip'),
 'A16': (19.10,42.00,34.29,'Animation and Hit Detection · 동작과 판정',
         ['보이는 접촉과 게임의 결과가', '서로 납득되게 이어져야 합니다.'],
         ['무기와 판정의 차이','이동 경로','명중 순간의 자세'], 'detection'),
 'A17': (11.03,23.60,16.39,'Rigging and Deformation · 뼈대와 변형',
         ['관절을 돌리는 것만으로', '모든 형태를 만들 수는 없습니다.'],
         ['관절을 다루는 방법','과장과 제약','표현에 맞게 선택'], 'rig'),
 'A18': (29.80,46.77,39.15,'Rotation Axes · 회전축',
         ['고개와 손목의 자연스러운 궤적은', '여러 축의 회전이 함께 만듭니다.'],
         ['회전축','축별 경로와 타이밍','시선과 함께 확인'], 'axes'),
}

def main():
    rows=[]
    for old in read(BASE/'plan.json')['episodes']:
        ep=old['id']; start,end,cue,term,definition,steps,diagram=DATA[ep]
        receipt=read(SOURCE/ep/'delivery.json')
        assert not receipt['visualReviewPending'] and receipt['summaryFrames']==600
        rows.append(dict(id=ep,title=old['title'],sourceReceipt=str(SOURCE/ep/'delivery.json'),
            sourceFiles=receipt['files'],sourceFrames=receipt['frames'],summaryAt=receipt['summaryAt'],
            startFrame=round(start*60),endFrame=round(end*60),roadmapFrame=round(cue*60),
            term=term,definition=definition,steps=steps,diagram=diagram,
            screenKind='explanation-overview',renderer='Editable Pillow diagram + FFmpeg same-clock native video compositing',
            reason='Existing spoken opening already defines the question and learning order. Add visible prerequisites, relationship and roadmap without repeating speech.',
            boundary='Retain actual-game hook, carry its question into the overview, return to the original next example. No audio interruption or extra title reset.',
            sourceLessonOrderPreserved=True, approvedAudioStrategy='copy original AAC exactly; no TTS',
            captionStrategy='unchanged SRT; redraw only opening cues in the same fixed boxed-white-forest geometry',
            speechVisualMapping={'definition':'Concrete question / observed result immediately preceding the existing overview sentence',
                                 'relationship':'Visible during the same narrated concept; schematic, not measured retail-game data',
                                 'roadmap':'Reveal at roadmapFrame, synchronized to existing 오늘은 / 이번에는 speech'},
            protected=[960,970,48,2], baselineHumanResponse='좋은데?',humanWholeVideoReviewed=False))
    plan=dict(revision='overview-v7',selectedAt=stamp(),scope=[r['id'] for r in rows],excludedUploaded=['A01','A02'],
              userEvidence='각 영상 앞에 개론 설명부분도 추가. 전부 개론 정리는 규칙에 추가해두고 앞으로 적용.',
              episodes=rows, audioChanged=False, newTtsAuthorized=False,
              policy='Opening easy meaning + concept relationship + 2–3 learning steps, integrated with existing spoken overview. Preserve v6 body and 600-frame recap; future explicitly selected videos use overview and recap by default.',
              resources='Serial CPU4 software encoding; no GPU voice/capture; preserve v6 and unrelated work.',
              platformBoundary='Local final review only; no upload, scheduling, deletion or Drive mutation.')
    save(HERE/'plan.json',plan)
    save(HERE/'checkpoint.json',dict(stage='opening-layout-preflight',updatedAt=stamp(),scope=plan['scope'],completed=[],remaining=plan['scope'],humanReviewed=False,platformChanged=False))
    print(f'Prepared {len(rows)} scoped conceptual openings; all original audio retained.')
if __name__=='__main__':main()
