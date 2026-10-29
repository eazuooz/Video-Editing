"""Prepare selected Buckshot paragraph takes and paired EN text; no TTS/GPU."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SLUG = PROJECT.name

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

english = [
    ["In Buckshot Roulette, you aim at yourself and fire a blank. You take no damage, and you can choose again. The same weapon leads to a different next step depending on whom you choose. What rules connect those decisions? Today, we will find those rules in the installed game's structure and implement a small game with a new look. We will go from reading files to checking behavior, then connect the result to a moving scene."],
    ["First, I checked what the game contains. Using REA, a package-structure analysis tool, to inspect the executable revealed 3,572 internal files. Among them were 195 GDScript files describing game behavior.",
     "The script files in this build were readable text. Rather than turning machine code back into source, the important task was following which functions change which values. I connected the parts that handle shots, hand over turns, and use items to organize the rules."],
    ["The first question was about the ammunition. Does the game pick a live round or a blank each time you pull the trigger? In the code I inspected, it builds the ammunition sequence when loading, then uses one round at a time from the front.",
     "Think of a row of cards. If the first card is a blank, the next result is a blank. Once it is used, that slot disappears and the second card moves to the front. The magnifying glass checks that front slot. Looking does not consume the round. Beer ejects the front round, moving the sequence forward without dealing damage.",
     "Picking a fresh result each time and consuming a prepared sequence may look similar on screen, but they are different rules. That distinction also connects the rounds already used to the next decision."],
    ["Is an ammunition sequence enough to make the game? We still have to decide whose turn comes next. Shooting a blank at yourself lets you act again without damage, but shooting it at your opponent gives you no such benefit. The round is still a blank, yet the next state depends on your target.",
     "Handcuffs add another condition: the opponent skips the next turn entry. But using the last round also requires a transition to reloading. If health reaches zero, the game must not accept another ordinary action. Ammunition count, health, turn ownership, and handcuff state all have to work together to produce the flow we see on screen.",
     "The saw changes a different value. A live round's base damage is one, and using the saw raises it to two. That does not turn a blank into a damaging round. Separating changes to ammunition, damage, and information makes the item combinations easier to understand."],
    ["The opponent also needs to read the state. Here, the dealer's decisions were built from conditions and random choices, rather than a trained model. When the current round is known, the dealer chooses the player for a live round and itself for a blank.",
     "The branch for uncertain information differs by mode. The ordinary mode chooses a target at random. Endless mode compares the remaining live rounds and blanks, choosing randomly if their counts are equal. Item conditions connect to that decision too: for example, the magnifying glass reveals information, and a saw can then be combined with a known live round. Breaking the decision down into available information and actions made the structure visible."],
    ["Using that structure, I wrote separate code for ammunition and turns in a new project. For example, set up a blank at the front and choose yourself. Does the ammunition count decrease, does health stay the same, and does the turn remain yours? The same input should produce the expected result before we move on.",
     "The independently written rules code passed 374 checks. Connecting the screen revealed additional issues to check. Another input had to be blocked while an item animation was still running, and a message that attributed a handcuff-driven repeat turn to a self-targeted blank needed to distinguish those causes. After those fixes, 32 integration checks passed for the rules and scene working together. Instead of looking only at a count, we also checked which input was blocked and which message changed."],
    ["Now it is time to show the rules with a different appearance. I created a new table, robot dealer, ammunition, and tools in Blender. After setting up the hands and head as separately movable parts, I brought them into a Godot scene. Instead of taking models and textures from the original game, I created shapes and materials for this experiment.",
     "The head moves while thinking, and the selected tool moves forward into view. I connected the sound and result message to the moment of firing. When inspecting or ejecting a round, the viewer should be able to follow the selected action and what changed. This step goes beyond replacing the picture: it connects rule changes with movement in the scene."],
    ["The self-targeted blank and next selection we saw at the start led us to rules for ammunition order and turn handling. We moved core behaviors into independent code and new graphics. The 374 checks cover our own rules model; they do not establish that every part of the original game behaves identically. The result is a prototype that implements the core rules we examined.",
     "AI and tools can help connect file investigation with implementation. To trust the result, though, we need to connect what we read, which inputs we tested, and which changes appeared on screen. This small game is the result of tracing those connections."]
]

def main():
    draft = PROJECT / 'planning/narration-draft.md'
    text = draft.read_text(encoding='utf-8')
    parts = re.split(r'^## (\d{2})\. (.+)$', text, flags=re.M)
    scenes = []
    for i in range(1, len(parts), 3):
        sid, title, content = parts[i:i+3]
        content = content.split('## 편집 시 지킬 근거 경계')[0].strip()
        lines = [line.strip() for line in content.split('\n\n') if line.strip()]
        scenes.append({'id': sid, 'title': title, 'lines': lines, 'displayLines': [line.replace('알이에이', 'REA').replace('지디스크립트', 'GDScript').replace('고도 엔진', 'Godot 엔진') for line in lines]})
    assert len(scenes) == len(english) == 8
    assert all(len(s['lines']) == len(en) for s, en in zip(scenes, english))
    common = {'schemaVersion': 1, 'slug': SLUG, 'status': 'prepared-for-selected-documentary; source capture in/out review pending', 'draftSource': 'planning/narration-draft.md', 'draftSha256': hashlib.sha256(draft.read_bytes()).hexdigest(), 'actualDurationSeconds': None}
    ko = dict(common, language='Korean', scenes=scenes)
    en = dict(common, language='English', translationPurpose='Semantic subtitle counterpart, not an English voice request', scenes=[{'id': s['id'], 'title': s['title'], 'lines': lines} for s, lines in zip(scenes, english)])
    write(PROJECT / 'script/narration.ko.json', ko)
    write(PROJECT / 'script/narration.en.json', en)
    out = f'projects/{SLUG}/production/local/audio-v1'
    tts = {
        'engine': 'qwen3-tts', 'model': 'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',
        'language': 'Korean', 'reference': 'shared/voice-reference/reference-15-35s.wav',
        'referenceText': 'shared/voice-reference/reference-15-35s.ko.txt',
        'outputDir': out, 'filenameStem': 'narration', 'renderMode': 'scene',
        'lineGapSeconds': 0.28, 'sceneGapSeconds': 0.72, 'maxNewTokens': 2048,
        'maxRenderAttempts': 1, 'edgeFadeSeconds': 0.006,
        'tailRatioThreshold': 0.07, 'tailDecayMsThreshold': 70,
        'gpuMinimumFreeMiB': 8192,
        'gpuProfileReason': 'Selected-project paragraph-as-one-line-scene jobs, batch1, same local 1.7B model/reference. Bound allocation to8GiB with700MiB spare; inspect actual resources and obtain root coordination before synthesis. No historical GPU grant inherited.',
        'lineLevelEqualization': {'targetSpeechFrameMedianDbfs': -22, 'frameMs': 50, 'gateBelowPeakDb': 25, 'maxGainDb': 12, 'record': 'line-levels.json'},
        'status': 'prepared-not-generated', 'paidApi': False
    }
    manifest = {'schemaVersion': 1, 'slug': SLUG, 'paths': {'script': f'projects/{SLUG}/script/narration.ko.json', 'scriptEn': f'projects/{SLUG}/script/narration.en.json'}, 'editing': {'narrationPlacement': 'continuous-across-all-three-segments', 'exampleSeconds': 0}, 'tts': tts}
    write(PROJECT / 'production/tts-manifest.json', manifest)
    print(json.dumps({'scenes': len(scenes), 'paragraphTakes': sum(len(s['lines']) for s in scenes), 'characters': sum(len(line) for s in scenes for line in s['lines']), 'ttsGenerated': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
