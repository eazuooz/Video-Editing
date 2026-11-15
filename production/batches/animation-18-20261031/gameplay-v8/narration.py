"""Rephrase only demonstrations that would otherwise promise unseen engine edits."""
from common import *
PATCHES={
'A03':[(97,'초당 예순 프레임인 시간표에서','On a timeline running at sixty frames per second,'),
       (133,'실제 동작과 시간표를 함께 다시 보겠습니다.','Review the recorded action alongside the timeline.')],
'A04':[(27,'왼쪽은 자세를 고르게 이어 봅니다.','The left version shows the poses at even intervals.'),
       (29,'편집 비교에서는 두 쪽의 도착 시점을 열두 프레임으로 맞췄습니다.','In this edited comparison, both versions arrive at frame twelve.')],
'A05':[(29,'깊이를 보는 도식에 두 캐릭터가 싸우는 기준 평면을 표시했습니다.','The depth diagram marks the plane in which the two characters fight.')],
'A07':[(40,'이번에는 같은 원본을 크게 보고 작게 보겠습니다.','Now compare the same recording at a large and small size.')],
'A08':[(21,'한 부분씩 살펴보겠습니다.','Examine one part at a time.'),
       (34,'먼저 몸의 양쪽이 어떻게 다른 역할을 맡는지 보겠습니다.','First, examine how the two sides of the body play different roles.'),
       (35,'정면에서 본 몸과, 돌아선 몸의 고개 방향을 살펴봅니다.','Compare the direction of the head in frontal and turned poses.'),
       (70,'발끝의 방향과 앞뒤 발의 배치를 함께 살펴보죠.','Look at the toe directions and the placement of the front and rear feet.'),
       (71,'바닥에 붙인 표시로 어느 발이 앞인지 확인합니다.','The floor guides identify the front foot.')],
'A10':[(29,'주리의 평소 자세와 맞은 직후 자세를 같은 크기로 놓고, 몸의 윤곽이 얼마나 달라졌는지 보겠습니다.','Compare Juri before and just after the hit at the same size, observing the change in her silhouette.'),
       (35,'실제 영상의 시작과 도착 자세를 나누어, 그 사이 동작을 살펴보겠습니다.','Separate the start and end poses in the recording and examine the movement between them.'),
       (50,'아래 도식에서는 바닥 기준점을 두고, 몸의 자세와 전체 이동을 나누어 보겠습니다.','The diagram uses a floor reference to distinguish posing from whole-character displacement.')],
'A11':[(28,'설명 그림에서는 공격까지의 길이를 여덟 프레임으로 맞춰 보겠습니다.','In the illustration, set the time to the attack to eight frames.'),
       (40,'아래 편집 비교에서도 그 자세가 얼마나 남는지 보세요.','Watch how long that pose remains in the edited comparison.'),
       (44,'이 편집 비교에서는 주요 자세와 전체 길이를 두고, 시간 배분 하나만 바꿔 보겠습니다.','This edited comparison keeps the key poses and total duration, changing only the allocation of time.')],
'A13':[(21,'디제이가 양쪽을 향한 실제 자세를 비교해 보죠.','Compare the actual poses of Dee Jay facing both directions.'),
       (22,'몸이 돌아선 모습과 포즈가 반전된 모습을 구분해 보겠습니다.','Distinguish turning the body from mirroring the pose.'),
       (23,'얼굴과 앞쪽 주먹이 양쪽 화면에서 어떻게 남는지 보면, 반전 동작을 고려하는 이유가 보입니다.','The face and leading fist in both views show why mirrored poses matter.'),
       (36,'소품 도식에서 손과 손잡이에 표시를 붙여, 함께 바뀔 부분을 보겠습니다.','The prop diagram marks the hand and handle to show what must change together.'),
       (39,'그래서 손잡이를 어느 손에 놓을지 그림으로 구분했습니다.','The illustration distinguishes which hand holds the handle.'),
       (52,'실제 플레이 화면과 위에서 보는 방향 도식을 함께 보겠습니다.','Compare the actual player view with the top-view direction diagram.')],
'A14':[(25,'원리 그림에서 같은 두 자세를 두고, 즉시 교체한 경우와 잠깐 섞는 경우를 비교하겠습니다.','The principle diagram uses the same two poses to compare an immediate switch with a brief blend.'),
       (26,'걷기 전에 남아 있던 자세가 달라지는 경우도 보겠습니다.','Also examine what happens when the pose before walking changes.'),
       (33,'설명 도식에서 걷기 비중이 영이면 이전 자세만, 일이면 걷기 자세만 사용합니다.','In the diagram, a walk weight of zero uses only the previous pose, and one uses only the walk pose.'),
       (45,'도식에서는 두 자세를 두고 전환 시간만 바꿔 보겠습니다.','The diagram keeps the two poses and varies only the transition duration.')],
'A15':[(34,'실제 손의 연속 동작과, 준비한 손 모양을 바꾸는 도식을 나란히 보겠습니다.','Compare the recorded continuous hand motion with a diagram that switches prepared hand shapes.')],
'A16':[(20,'원리 그림에서 같은 검의 경로를 두고 판정 범위만 바꿔 보겠습니다.','The principle diagram keeps the sword path and varies only the hit area.'),
       (27,'위쪽 도식에 캐릭터와 상대가 놓인 기준 평면을 표시하겠습니다.','The top-view diagram marks the reference plane of the character and target.'),
       (41,'이 도식에서는 같은 검의 경로에서 활성 구간만 옮겨 보겠습니다.','In this diagram, keep the sword path and shift only the active interval.')],
'A17':[(28,'관절 그림에서는 어깨부터 돌리는 경우와, 손 목표에서 자세를 구하는 경우를 비교하겠습니다.','The joint diagram compares rotating from the shoulder with solving the pose from the hand target.'),
       (43,'도식에서 손 목표를 두고, 굽힘 방향을 알리는 힌트를 움직여 보겠습니다.','Keep the hand target in the diagram and move the hint that specifies the bend direction.'),
       (59,'도식에서 추가 제어점이 중간 윤곽을 바꾸는 모습을 보겠습니다.','The diagram shows how additional control points change the intermediate contour.')],
'A18':[(25,'회전 도식에서 숙임과 좌우 돌림, 옆 기울임을 하나씩 보여 주겠습니다.','The rotation diagram separates pitch, yaw, and sideways tilt.'),
       (38,'회전 도식의 최종 좌우 각도를 육십 도로 정했다면, 세 버전 모두 그 값은 유지하겠습니다.','If the diagram sets the final yaw to sixty degrees, all three versions retain that value.')]
}
def prepare():
    plan=read(HERE/'plan.json');records=[];scenes=[]
    for ep,changes in PATCHES.items():
        row=next(r for r in plan['episodes'] if r['id']==ep)
        assert ep in SCOPE
        for index,new,en in changes:
            cue=row['bodyNarrationCues'][index];identity=ep+'-gameplay-'+str(index).zfill(3)
            assert cue['start']>=row['opening']['endFrame']/60 and cue['end']<=row['summaryAt']
            records.append(dict(id=identity,episode=ep,captionIndex=index,old=cue['text'],ko=new,en=en,
                start=cue['start'],end=cue['end'],reason='Bind narration to observed game footage or an explicit principle diagram; preserve claim and teaching order.'))
            scenes.append(dict(id=identity,title=row['title'],lines=[new]))
    save(HERE/'narration-changes.json',dict(records=records,unchangedAudioOutsidePatches=True,overviewAndRecapSpeechPreserved=True))
    local=HERE/'local';save(local/'voice-script.json',dict(scenes=scenes))
    m=read(BATCH/'local/native-clips-v6/patches-manifest.json')
    m.update(slug='animation-gameplay-v8',revision='gameplay-v8')
    m['paths']['script']=(local/'voice-script.json').relative_to(ROOT).as_posix()
    m['tts'].update(outputDir=(local/'voice').relative_to(ROOT).as_posix(),filenameStem='gameplay-patches',maxNewTokens=512)
    save(HERE/'tts-manifest.json',m)
    print('Rewritten speech cues:',len(records))
if __name__=='__main__':prepare()
