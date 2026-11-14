"""Keep the teaching order and correct only claims tied to replaced demonstrations."""
import re
import shutil

from prepare import HERE, ROOT, VOICE_LOCAL, read, save
from assemble_delivery import srt

# Prior sentence, replacement, English replacement. No other narration is rewritten.
REPLACEMENTS = {
 'A05': [
  ('팔만 쓸 때와 몸 전체를 쓸 때를 비교해 보세요.', '준비 자세와 뻗은 자세를 비교해 보세요.', 'Compare the preparation and the extended pose.'),
  ('팔만 조금 내민 몸과 어깨에서 발까지 함께 기울인 몸은 작은 화면에서 다른 모양이 됩니다.', '준비하는 몸과 어깨에서 발까지 함께 뻗은 몸은 작은 화면에서 다른 모양이 됩니다.', 'The preparation and the extension from shoulder to foot create different shapes on a small screen.')],
 'A07': [
  ('그 상태에서 몸짓의 크기만 키워 보죠.', '이번에는 큰 몸짓이 담긴 부분을 보죠.', 'Now watch the part with the larger gesture.'),
  ('새로운 행동을 추가한 것이 아니라, 처음에 의도한 행동이 화면에서도 읽히도록 조정한 것입니다.', '동작에 담긴 큰 몸짓을 고르면 화면에서도 행동이 또렷해집니다.', 'Selecting the larger gesture in the performance makes the action clearer on screen.')],
 'A08': [
  ('오늘은 한 자세를 직접 고쳐 보면서 몸의 흐름, 팔과 손의 윤곽, 체중과 발의 위치를 차례로 살펴보겠습니다.', '오늘은 완성된 동작을 비교하며 몸의 흐름, 팔과 손의 윤곽, 체중과 발의 위치를 살펴보겠습니다.', 'We will compare finished animation, examining body flow, arm and hand silhouette, and weight and foot placement.'),
  ('처음 자세로 돌아가서 한 부분씩 바꾸어 보겠습니다.', '처음 자세부터 하나씩 비교해 보겠습니다.', 'Compare one part at a time from the starting pose.'),
  ('머리, 어깨, 손, 발을 하나씩 고쳤어도 서로 어울리지 않으면 좋은 자세가 되지 않습니다.', '머리, 어깨, 손, 발을 하나씩 살펴도 서로 어울려야 좋은 자세가 됩니다.', 'The head, shoulders, hands and feet must work together as a pose.'),
  ('오늘 고친 자세를 처음 모습과 다시 나란히 보겠습니다.', '처음 모습과 다시 나란히 보겠습니다.', 'Compare it with the starting pose again.'),
  ('몸을 정확히 가운데에 두고 양발로 똑같이 받치는 모습에서, 한쪽 다리가 더 받치는 모습으로 조금 바꾸어 보겠습니다.', '몸을 가운데에 둔 순간과 한쪽 다리가 더 받치는 순간을 나누어 살펴보겠습니다.', 'Compare the centered moment with the moment supported more by one leg.'),
  ('오른손이 몸 앞에서 올라가고, 왼손도 함께 따라옵니다.', '올라가는 손과 몸 사이 빈틈을 보세요.', 'Watch the negative space between the rising hand and the torso.')],
 'A10': [
  ('우리 시연에서는 카메라를 고정하고 몸통 방향만 바꿔, 같은 날아가는 자세가 얼마나 다르게 읽히는지 보겠습니다.', '같은 피격 자세를 다른 각도에서 보며, 가려졌던 팔다리가 드러나는지 살펴보겠습니다.', 'View the same hit reaction from different angles and check whether the hidden limbs become visible.'),
  ('먼저 높이만 바꾸고, 그다음 같은 높이에서 반응 크기만 바꾸면 무엇이 달라지는지 쉽게 볼 수 있습니다.', '먼저 피격 높이를 나누고, 반응의 시작과 크게 밀리는 순간을 비교하면 차이가 보입니다.', 'Separate the hit heights, then compare the reaction onset with the larger displacement.')],
 'A11': [
  ('오른쪽은 준비에 시간을 쓰고, 팔을 빠르게 올립니다.', '오른쪽은 준비에 시간을 쓰고, 주먹을 빠르게 뻗습니다.', 'The right version holds the preparation, then extends the fist quickly.'),
  ('아래에서 위로 주먹을 올리는 어퍼컷을 세 자세로 나눠 보겠습니다.', '앞으로 주먹을 뻗는 동작을 세 자세로 나눠 보겠습니다.', 'Break the forward punch into three poses.'),
  ('몸을 낮춘 자세, 주먹이 올라가는 자세, 팔을 위로 뻗은 자세입니다.', '몸을 당긴 자세, 주먹이 나가는 자세, 팔을 뻗은 자세입니다.', 'The body draws back, the fist moves out, and the arm extends.'),
  ('주먹을 뻗은 뒤에는 올라온 길을 그대로 되짚는 대신 다른 경로로 돌아오게 해 보겠습니다.', '주먹을 뻗은 뒤에는 나간 길을 되짚는 모습과 실제 회수 동작을 비교해 보겠습니다.', 'After the punch, compare retracing the outward path with the actual recovery motion.')],
 'A12': [
  ('우리 시연에서는 같은 얼굴에서 눈썹, 눈, 입을 차례로 바꿔 보겠습니다.', '같은 캐릭터의 눈썹, 눈, 입을 차례로 살펴보겠습니다.', 'Examine the same character’s brows, eyes and mouth in turn.'),
  ('우리 시연에서는 원래 얼굴, 수정 그림, 실제 조정한 얼굴을 같은 크기와 각도로 이어 보여 주겠습니다.', '원래 얼굴과 수정 방향을 그린 그림을 같은 크기로 나란히 보겠습니다.', 'Compare the original face with a drawing of the proposed changes at the same size.'),
  ('이번에는 눈을 바꿀 때 입은 고정하고, 입을 바꿀 때는 눈을 고정해 보겠습니다.', '눈을 볼 때는 입을 가리고, 입을 볼 때는 눈을 가려 보겠습니다.', 'Hide the mouth when examining the eyes, and hide the eyes when examining the mouth.'),
  ('얼굴을 풍부하게 움직이는 버전과 얼굴을 제한한 버전을 같은 행동에 놓아 보면, 필요한 정보가 어디서 전달되는지 보입니다.', '얼굴의 세부가 드러난 모습과 가려진 모습을 같은 행동에서 비교하면, 감정이 어디서 전달되는지 보입니다.', 'Compare visible and hidden facial detail within the same action to see what conveys the emotion.')],
 'A14': [
  ('우리 시연에서는 입력점을 움직일 때 캐릭터의 방어 자세가 실제로 어떻게 바뀌는지 함께 보여 주겠습니다.', '우리 도식에서는 입력점에 따라 어떤 자세를 얼마나 섞는지 함께 보여 주겠습니다.', 'Our diagram shows which poses contribute and by how much as the input point changes.')],
 'A15': [
  ('우리 시연에서는 손잡이와 카메라를 고정하고 손가락 각도를 바꿔 보겠습니다.', '완성된 잡기 동작에서 손가락이 물체를 감싸는 과정을 보겠습니다.', 'Watch the fingers wrap around the object in a finished grasp animation.')],
}


ADDITIONAL = {
 'A08': [
  ('먼저 똑바로 세운 자세와 조정한 자세를 나란히 보겠습니다.', '먼저 처음 자세와 동작 속 다음 자세를 나란히 보겠습니다.', 'Compare the starting pose with the next pose in the animation.'),
  ('완성된 쪽에서는 머리와 몸통이 같은 정면만 바라보지 않고, 두 팔과 발에도 서로 다른 역할이 생깁니다.', '다음 자세에서는 머리와 몸통이 서로 다른 방향을 보고, 두 팔과 발도 다른 역할을 맡습니다.', 'In the next pose, the head and torso face different directions, and the arms and feet take different roles.')],
 'A10': [
  ('우리 시연에서는 시작 자세와 도착 자세를 옅게 남겨 두고 실제 캐릭터가 그 사이를 어떻게 지나가는지 보겠습니다.', '우리 시연에서는 시작과 도착 자세를 나누어 놓고 실제 동작이 그 사이를 어떻게 지나가는지 보겠습니다.', 'Our demonstration separates the starting and ending poses to examine how the actual animation moves between them.')],
 'A12': [
  ('한 번에 하나씩 바꿔야 무엇이 표정을 바꿨는지 알 수 있습니다.', '한 번에 한 부위씩 살펴야 무엇이 표정을 만드는지 알 수 있습니다.', 'Examine one facial region at a time to see what creates the expression.')],
 'A14': [
  ('우리 시연에서는 같은 무대에 경사면만 추가하고, 상체 행동과 하체 이동을 구분해 보겠습니다.', '실제 걷기 동작을 보고, 도식에서 경사면과 상체, 하체의 관계를 나누어 보겠습니다.', 'Watch the actual walk, then separate the slope, upper body and legs in the diagram.'),
  ('발을 지면에 맞추는 제어를 켰을 때와 껐을 때도 같은 시점에서 비교하겠습니다.', '도식에서 발 목표를 지면에 맞추기 전과 후를 비교하겠습니다.', 'The diagram compares the foot targets before and after aligning them to the ground.')],
 'A15': [
  ('그래서 우리 시연에서도 손 모델 자체를 바꾸기 전에 카메라 거리와 화면 속 캐릭터 수를 바꿔 보겠습니다.', '손 모델 자체를 바꾸기 전에 카메라 거리와 화면 속 캐릭터 수도 함께 고려해야 합니다.', 'Consider camera distance and the number of on-screen characters before changing the hand model itself.')],
 'A17': [
  ('우리 비교에서는 같은 목표 포즈를 단순한 리그와 추가 제어가 있는 리그로 만들어 보겠습니다.', '우리 도식에서는 같은 손 목표에 팔꿈치 방향 정보를 더했을 때의 차이를 보겠습니다.', 'Our diagram shows the difference when elbow-direction information is added to the same hand target.')],
 'A18': [
  ('같은 손잡이에서 손목만 돌려 보고, 기울임을 더하고, 마지막에는 어깨까지 이어서 움직여 보겠습니다.', '완성된 손목 동작을 보고, 도식에서 회전과 기울임이 만드는 경로를 나누어 보겠습니다.', 'Watch the finished wrist motion, then separate the paths created by rotation and tilt in the diagram.'),
  ('어느 부위를 더했을 때 몸 전체의 연속성이 생기는지 같은 카메라에서 보겠습니다.', '실제 동작에서는 손목과 팔이 어떻게 이어지는지도 함께 보겠습니다.', 'Also observe how the wrist and arm connect in the actual animation.'),
  ('우리 화면에서는 고개 숙임과 좌우 회전의 곡선을 따로 놓고, 재생 위치가 움직일 때 실제 자세도 같은 순간을 가리키게 하겠습니다.', '우리 도식에서는 숙임과 좌우 회전의 곡선을 따로 놓고, 재생 위치와 방향 표시를 같은 순간에 맞추겠습니다.', 'Our diagram separates pitch and yaw curves, with the playback cursor and direction marker synchronized.'),
  ('우리 시연에서는 목표 위치를 고정한 채 눈의 시선을 켜고 끄겠습니다.', '도식에서 머리만 돌릴 때와 눈도 움직일 때를 보세요.', 'Our diagram compares aiming at the same target with the head alone and with both head and eyes.')],
}
for _ep,_lines in ADDITIONAL.items():REPLACEMENTS.setdefault(_ep,[]).extend(_lines)


def normalized(text):
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', text)


def main():
    plan = read(HERE / 'plan.json')
    records, scenes = [], []
    for ep, replacements in REPLACEMENTS.items():
        base = next(r['baseline'] for r in plan['episodes'] if r['id'] == ep)
        ko = srt(ROOT / next(r['path'] for r in base['files'] if r['kind'] == 'ko.srt'))
        for i, (old, new, en) in enumerate(replacements, 1):
            matches = [(j, cue) for j, cue in enumerate(ko) if normalized(cue[2]) == normalized(old)]
            assert matches, (ep, old)
            for occurrence, (j, (a, b, _)) in enumerate(matches):
                identity = f'{ep}-native-{i:02}-{occurrence:02}'
                records.append({'id': identity, 'episode': ep, 'old': old, 'ko': new, 'en': en,
                                'start': a, 'end': b, 'captionIndex': j,
                                'reason': 'Match the inspected native animation or editorial diagram, preserving the source lesson and order.'})
                scenes.append({'id': identity, 'title': base['title'], 'lines': [new]})
    old_file=HERE/'narration-patches.json'
    old={r['id']:r for r in read(old_file)['records']} if old_file.exists() else {}
    for r in records:
        if r['id'] in old and r['ko']!=old[r['id']]['ko']:
            wav=VOICE_LOCAL/'patch-voice/chunks'/(r['id']+'-scene.wav')
            if wav.exists():
                preserved=VOICE_LOCAL/'patch-voice/preserved-before-length-retake'/wav.name
                preserved.parent.mkdir(parents=True,exist_ok=True)
                if not preserved.exists(): shutil.copyfile(wav,preserved)
                wav.unlink()
    save(old_file, {'records': records, 'scope': 'Only demonstration-dependent sentences; all other narration retained.'})
    save(VOICE_LOCAL / 'patches.json', {'scenes': scenes})
    manifest = read(VOICE_LOCAL / 'tts-manifest.json')
    manifest['paths']['script'] = (VOICE_LOCAL / 'patches.json').relative_to(ROOT).as_posix()
    manifest['tts'].update(outputDir=(VOICE_LOCAL / 'patch-voice').relative_to(ROOT).as_posix(), filenameStem='native-patches')
    save(VOICE_LOCAL / 'patches-manifest.json', manifest)
    print('Native-demo narration corrections:', len(records))


if __name__ == '__main__':
    main()
