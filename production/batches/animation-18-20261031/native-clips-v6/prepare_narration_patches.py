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
  ('오른손이 몸 앞에서 올라가고, 왼손도 함께 따라옵니다.', '한 손이 올라갈 때, 팔과 몸통 사이의 빈 공간을 보세요.', 'As one hand rises, watch the negative space between the arm and the torso.')],
 'A10': [
  ('우리 시연에서는 카메라를 고정하고 몸통 방향만 바꿔, 같은 날아가는 자세가 얼마나 다르게 읽히는지 보겠습니다.', '같은 피격 자세를 다른 각도에서 보며, 가려졌던 팔다리가 드러나는지 살펴보겠습니다.', 'View the same hit reaction from different angles and check whether the hidden limbs become visible.'),
  ('먼저 높이만 바꾸고, 그다음 같은 높이에서 반응 크기만 바꾸면 무엇이 달라지는지 쉽게 볼 수 있습니다.', '먼저 피격 높이를 나누고, 반응의 시작과 크게 밀리는 순간을 비교하면 차이가 보입니다.', 'Separate the hit heights, then compare the reaction onset with the larger displacement.')],
 'A11': [
  ('오른쪽은 준비에 시간을 쓰고, 팔을 빠르게 올립니다.', '오른쪽은 준비에 시간을 쓰고, 주먹을 빠르게 뻗습니다.', 'The right version holds the preparation, then extends the fist quickly.'),
  ('아래에서 위로 주먹을 올리는 어퍼컷을 세 자세로 나눠 보겠습니다.', '앞으로 주먹을 뻗는 동작을 세 자세로 나눠 보겠습니다.', 'Break the forward punch into three poses.'),
  ('몸을 낮춘 자세, 주먹이 올라가는 자세, 팔을 위로 뻗은 자세입니다.', '몸을 당긴 자세, 주먹이 나가는 자세, 팔을 뻗은 자세입니다.', 'The body draws back, the fist moves out, and the arm extends.')],
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
