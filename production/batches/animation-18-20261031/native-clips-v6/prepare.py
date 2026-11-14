"""Prepare the user-selected native-clip revision without replacing earlier deliveries."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BATCH = HERE.parent
WORK = Path('C:/Users/1/Videos/YamyamProduction/animation-native-clips-v6')
VOICE_LOCAL = BATCH / 'local/native-clips-v6'
OUTPUT = Path('C:/Users/1/Videos/YamyamCoding/animation-native-clips-v6')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


RECAPS = {
    'A03': ('준비로 알리고, 공격으로 힘을 펼친 뒤 후속 동작으로 정리합니다. 공격 판정과 다음 입력 시점도 함께 확인하세요.',
            'Signal with anticipation, deliver the attack, and settle with follow-through. Check hit detection and when the next input becomes available.'),
    'A04': ('준비 동작은 공격 방향과 힘을 미리 알려 줍니다. 첫 변화를 또렷하게 만들고, 필요한 시간만 남겨 보세요.',
            'Anticipation signals direction and force. Make the first change clear and keep the time the player needs to read it.'),
    'A05': ('공격하는 팔과 받치는 몸이 함께 자세를 만듭니다. 공격 방향과 실루엣을 확인하고, 타격 순간의 형태를 살펴보세요.',
            'The striking arm and supporting body shape the pose together. Check direction, silhouette, and the form at impact.'),
    'A06': ('후속 동작은 타격 뒤에도 힘의 흐름을 보여 줍니다. 몸이 정리되는 시간과 다음 입력이 가능한 시점을 나눠 보세요.',
            'Follow-through carries force beyond impact. Distinguish the settling movement from when another input becomes possible.'),
    'A07': ('작은 화면에서는 미세한 몸짓이 사라집니다. 실제 플레이 크기로 확인하고, 전달할 움직임을 더 또렷하게 만들어 주세요.',
            'Small screens hide subtle gestures. Check the actual gameplay size and strengthen the motion you want to communicate.'),
    'A08': ('포즈는 몸의 흐름과 빈 공간, 체중을 받치는 발을 함께 봅니다. 참고 동작을 여러 시점에서 확인해 보세요.',
            'Read the body line, negative space, and supporting foot together. Inspect the reference motion from several angles.'),
    'A09': ('눌림과 늘어남은 힘과 속도를 더 분명하게 보여 줍니다. 부피와 실루엣을 함께 확인하며, 필요한 순간에 변형을 집중하세요.',
            'Squash and stretch communicate force and speed. Check volume and silhouette, concentrating the deformation where it matters.'),
    'A10': ('피격 동작은 맞은 위치와 충격 방향을 전달합니다. 반응의 시작과 몸의 이동, 원래 자세로 돌아오는 흐름을 확인하세요.',
            'A hit reaction shows the contact point and force direction. Check its onset, body displacement, and recovery.'),
    'A11': ('같은 주요 자세라도 중간 시간에 따라 동작의 인상이 달라집니다. 준비와 타격, 돌아오는 경로를 따로 비교하세요.',
            'The same key poses can feel different with different timing. Compare anticipation, strike, and the return path separately.'),
    'A12': ('표정은 눈썹과 눈, 입이 함께 전달합니다. 얼굴 가까이에서 확인한 뒤 실제 게임 화면 크기에서도 감정이 읽히는지 보세요.',
            'Brows, eyes, and mouth communicate together. Inspect the face closely, then check whether the emotion reads at gameplay size.'),
    'A13': ('좌우 반전은 동작의 인상을 바꾸지만 손과 장비도 함께 뒤집습니다. 방향과 소품, 글자가 의도대로 보이는지 확인하세요.',
            'Mirroring changes how a motion reads and also flips hands and equipment. Check direction, props, and lettering.'),
    'A14': ('블렌딩은 두 동작의 자세를 섞습니다. 재생 위치와 섞는 비율을 나누고, 발이 미끄러지거나 몸이 끊기는지 확인하세요.',
            'Blending combines two poses. Check playback position and weight separately, watching for foot sliding or abrupt movement.'),
    'A15': ('손가락은 잡는 물체와 손의 역할을 보여 줍니다. 가까이 보이는 손부터 자세를 살리고, 화면 크기에 맞춰 세부를 조절하세요.',
            'Fingers show the object being held and the hand’s role. Prioritize visible hands and match detail to their screen size.'),
    'A16': ('공격 동작과 판정은 함께 설계합니다. 무기의 경로와 유효 구간을 겹쳐 보고, 보이는 접촉과 결과가 이어지는지 확인하세요.',
            'Design animation and hit detection together. Compare the weapon path with its active interval and connect visible contact to the result.'),
    'A17': ('관절 회전만으로 모든 형태를 만들 수는 없습니다. 뼈대의 움직임과 표면 변형을 나눠 보고, 필요한 표현을 선택하세요.',
            'Joint rotation cannot make every shape. Separate skeletal motion from surface deformation and choose what the expression needs.'),
    'A18': ('고개와 손목은 한 축만 돌리면 기계적으로 보일 수 있습니다. 두 축의 타이밍을 나누고, 시선까지 함께 확인하세요.',
            'A head or wrist can look mechanical with one-axis rotation. Offset the timing on two axes and check the gaze as well.'),
}


def main():
    baseline = BATCH / 'contrast-v5/review-notes-20261110/review-manifest.json'
    old = read(baseline)
    records = {row['id']: row for row in old['records'] + [old['preservedA03']]}
    stamp = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
    plan = {
        'revision': 'native-clips-v6', 'selectedAt': stamp,
        'userEvidence': '이미 잘 동작하는 애니메이션을 사용해서 비교. A06은 굉장히 잘했네. 각 영상 끝에 10초 정리 추가. 이미 업로드된 것은 제외.',
        'baselineManifest': str(baseline.relative_to(ROOT)),
        'excludedUploaded': [{'id': 'A01', 'youtubeId': 'YrbHxv4F8gE', 'state': 'public'},
                             {'id': 'A02', 'youtubeId': 'VW4Bj-qmIZg', 'state': 'public'}],
        'platformEvidence': '2026-11-14 Chrome Studio channel content visible public rows, matched upload receipts. No other A-series upload receipts found.',
        'scope': list(RECAPS), 'keepApprovedStudy': 'A06',
        'animationContract': 'Use genuine installed animation sequences with unchanged bone motion. Comparisons may change camera, timing, playback position, whole-object display, blend weights or labels. Inspect original-speed motion first. Show essential abstract diagrams with the relevant clip. No fabricated humanoid motion as the comparison baseline.',
        'summaryContract': 'Exactly 600 frames at 60fps after the body and before the existing membership end. Narrated topic summary with relevant motion and no new coaching speech. Preserve source narration and the lesson order.',
        'resourcePolicy': 'Discord encoder is active. CPU voice and isolated WARP captures until the existing GPU protection rules permit use. Costly jobs serialized.',
        'episodes': [{'id': ep, 'title': records[ep]['title'], 'baseline': records[ep],
                      'status': 'native-clip-audit-and-recap-preparation',
                      'recapKo': ko, 'recapEn': en} for ep, (ko, en) in RECAPS.items()],
        'outputFolder': str(OUTPUT), 'humanReviewed': False, 'platformChanged': False,
        'youtubeAuthorized': False, 'driveAuthorized': False,
    }
    save(HERE / 'plan.json', plan)
    save(HERE / 'checkpoint.json', {'stage': 'selected-source-audit', 'updatedAt': stamp,
                                  'remaining': list(RECAPS), 'completed': []})
    save(VOICE_LOCAL / 'recaps.json', {'scenes': [{'id': ep, 'title': records[ep]['title'], 'lines': [ko], 'en': en}
                                        for ep, (ko, en) in RECAPS.items()]})
    voice = read(BATCH / 'contrast-v5/review-notes-20261110/local/tts-manifest.json') if (
        BATCH / 'contrast-v5/review-notes-20261110/local/tts-manifest.json').exists() else None
    if voice is None:
        voice = read(ROOT / 'production/batches/design-specifics-18-20261111/local/DS18/tts-manifest.json')
    voice['slug'] = 'animation-native-clips-v6'
    voice['paths']['script'] = (VOICE_LOCAL / 'recaps.json').relative_to(ROOT).as_posix()
    voice['tts'].update(outputDir=(VOICE_LOCAL / 'voice').relative_to(ROOT).as_posix(), filenameStem='recaps', maxRenderAttempts=3)
    save(VOICE_LOCAL / 'tts-manifest.json', voice)
    control_path = ROOT / 'shared/publishing/video-production-control.json'
    control = read(control_path)
    control['animationNativeClipsRevision20261114'] = {
        'status': 'selected-source-audit', 'selectedAt': stamp, 'episodes': list(RECAPS),
        'excludedUploaded': ['A01', 'A02'], 'keepApprovedStudy': 'A06',
        'plan': str((HERE / 'plan.json').relative_to(ROOT)),
        'checkpoint': str((HERE / 'checkpoint.json').relative_to(ROOT)),
        'renderAuthorized': True, 'ttsAuthorized': True, 'youtubeAuthorized': False,
        'driveAuthorized': False, 'humanFinalReviewRequired': True,
    }
    save(control_path, control)
    print(HERE / 'plan.json')


if __name__ == '__main__':
    main()
