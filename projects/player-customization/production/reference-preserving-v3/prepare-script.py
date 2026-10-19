"""Draft the selected Raiders/ACNH/BOTW narration; never lock before actual footage review."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/player-customization'
OLD = PROJECT / 'script/reference-preserving-v2'
NEW = PROJECT / 'script/reference-preserving-v3'
KO = {
 ('01', 2): '먼저 스플래툰 레이더스에서 장비를 고르고, 시험장에서 결과를 확인해 보죠.',
 ('02', 0): '스플래툰 레이더스는 잉크로 적을 상대하며 보물을 찾는 액션 슈팅 게임입니다. 무기와 기계 장치인 가젯을 조합하고, 시험장에서 새 조합을 써 볼 수 있습니다.',
 ('02', 2): '지금은 고른 장비와 시험장의 표적을 번갈아 보세요. 설명에서 상상했던 공격이 실제로 어떻게 나가고 어디에 닿는지 확인하는 겁니다.',
 ('03', 0): '레이더스에도 여러 종류의 무기가 있습니다. 지금은 버튼을 누르고 있는 동안 잉크를 연속으로 쏘는 슈터를 먼저 보죠.',
 ('03', 1): '차저는 버튼을 누른 채 힘을 모은 뒤 놓아서 쏩니다. 슈터의 연사와는 준비 시간과 공격 방식이 다르죠. 이 차이만으로 우열을 단정하지 말고, 장점에 어떤 제약이 따라오는지 따져야 합니다. 다음 가상 예에서는 한 발의 큰 피해와 다음 발까지 기다리는 시간을 함께 보겠습니다. 이렇게 얻는 것과 포기하는 것이 연결된 관계를 트레이드오프라고 합니다.',
 ('04', 2): '모여봐요 동물의 숲의 처음 외형을 고르는 화면도 같은 원리입니다. 머리 모양과 눈 같은 분류를 고르면 선택지가 바뀌고, 고른 모습이 캐릭터에 보입니다.',
 ('06', 1): '젤다의 전설 브레스 오브 더 와일드에서는 무기를 바꾼 뒤, 같은 장소에서 꺼내 사용할 수 있습니다. 목록에서 본 무기와 실제로 휘두르는 동작을 연결해 보면, 다음 선택에 필요한 차이를 확인할 수 있죠.',
 ('06', 2): '레이더스의 시험장도 새 조합을 실전에 나가기 전에 익힐 수 있게 해 줍니다. 메뉴에서 나와 긴 이동이나 전투를 거쳐야만 차이를 알 수 있다면, 마음에 들지 않는 조합을 고칠 때마다 같은 준비를 반복해야 하죠.',
}
EN = {
 ('01', 2): 'Let us begin by choosing equipment in Splatoon Raiders and checking the result on its test range.',
 ('02', 0): 'Splatoon Raiders is an action shooter about fighting enemies with ink and searching for treasure. Players combine weapons with mechanical gadgets and can try new setups on the test range.',
 ('02', 2): 'Look between the selected equipment and the test-range targets. The player can check how the imagined attack actually comes out and where it lands.',
 ('03', 0): 'Raiders also offers different weapon classes. First, watch a Shooter, which fires ink continuously while its fire button is held.',
 ('03', 1): 'A Charger builds a charge while the button is held, then fires when it is released. Its preparation and firing rhythm differ from a Shooter. That difference alone does not establish superiority: we must ask what constraints accompany a benefit. The next fictional example will compare high damage per shot with the wait before the next shot. A linked benefit and sacrifice is called a trade-off.',
 ('04', 2): 'Animal Crossing: New Horizons uses the same principle in its initial appearance selection. Choosing a category such as hair or eyes changes the options, and the selected appearance is shown on the character.',
 ('06', 1): 'In The Legend of Zelda: Breath of the Wild, players can change a weapon and draw it in the same location. Connecting the weapon seen in the list with its actual swing reveals differences that can inform the next choice.',
 ('06', 2): 'The Raiders test range also lets players learn a new setup before entering a real raid. If every test required leaving the menu, travelling a long distance, or fighting a battle, each unwanted combination would force the same preparation again.',
}


def main():
    selection = json.loads((Path(__file__).with_name('title-selection.json')).read_text(encoding='utf-8-sig'))
    assert selection['selectedTitles'] == ['Splatoon Raiders', 'Animal Crossing: New Horizons', 'The Legend of Zelda: Breath of the Wild']
    NEW.mkdir(parents=True, exist_ok=True)
    changes = []
    for language, edits in [('ko', KO), ('en', EN), ('spoken-ko', KO)]:
        source = json.loads((OLD / f'narration.{language}.json').read_text(encoding='utf-8-sig'))
        source['status'] = 'draft-selected-raiders-acnh-botw; actual source-specific claim review pending'
        for scene in source['scenes']:
            for index in range(len(scene['lines'])):
                key = (scene['id'], index)
                if key in edits:
                    before = scene['lines'][index]
                    scene['lines'][index] = edits[key]
                    changes.append({'language': language, 'scene': key[0], 'paragraph': index + 1,
                                    'before': before, 'after': edits[key]})
        (NEW / f'narration.{language}.json').write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    record = {'revision': 'reference-preserving-v3', 'changedParagraphCountPerLanguage': 8,
              'unchangedParagraphCountPerLanguage': 27, 'changes': changes,
              'selectedTitles': selection['selectedTitles'],
              'sourceReports': ['raiders-footage-research.json', 'botw-footage-research.json', 'script-change-map.json'],
              'draftOnly': True, 'currentProductionApproval': False,
              'internalFullTextReview': 'pending', 'userReview': 'pending-complete-current-Drive-version'}
    Path(__file__).with_name('script-revision.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared paired35-paragraph current-title draft;8 changed,27 preserved. Actual source review/lock pending.')


if __name__ == '__main__':
    main()
