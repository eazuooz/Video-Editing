"""Validate current display→speech inputs and paragraph/caption ownership, no media jobs."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import re
import unicodedata

from audio_revision import P, R, L, VOICE, REVISION, read, guard


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(text):
    return re.sub(r'[^0-9a-z가-힣]', '', unicodedata.normalize('NFC', text).lower())


def main():
    guard()
    raw = read(P / 'script/narration.ko.json')
    cl = read(P / 'script/clauses.json')
    aliases = cl.get('pronunciationAliases', {})
    assert aliases == {'3D': '쓰리디', '2D': '투디', 'RGB': '알지비'}

    def spoken(text):
        for display, speech in sorted(aliases.items(), key=lambda item: -len(item[0])):
            text = re.sub(re.escape(display), lambda match: speech, text, flags=re.I)
        return text

    original = [line for scene in raw['scenes'] for line in scene['lines']]
    lines = [spoken(line) for line in original]
    assert norm((P / 'script/narration.ko.txt').read_text(encoding='utf8')) == norm(''.join(original))
    assert len(raw['scenes']) == 1 and len(lines) >= 2, 'Use meaningful paragraphs within one continuous Short.'
    assert not any(re.search('[0-9]', line) for line in lines), 'Use explicit Hangul speech numbers.'
    clauses = cl['clauses']
    assert clauses and len({x['id'] for x in clauses}) == len(clauses)
    assert [x['lineIndex'] for x in clauses] == sorted(x['lineIndex'] for x in clauses)
    for index, line in enumerate(lines):
        owned = [x for x in clauses if x['lineIndex'] == index]
        assert owned and norm(''.join(x['spoken'] for x in owned)) == norm(line), f'Spoken paragraph{index} changed'
        assert norm(''.join(x['ko'] for x in owned)) == norm(original[index]), f'Display paragraph{index} changed'
    for item in clauses:
        emphasis = item.get('emphasis')
        if emphasis:
            assert item['ko'].count(emphasis['text']) == 1 and emphasis['role'] in ['term', 'result', 'problem']
    doc = copy.deepcopy(raw)
    for scene in doc['scenes']:
        scene['lines'] = [spoken(line) for line in scene['lines']]
    doc['derivation'] = {'revision': REVISION, 'displayScript': 'script/narration.ko.json',
        'displayScriptSha256': sha(P / 'script/narration.ko.json'), 'clausesSha256': sha(P / 'script/clauses.json'),
        'pronunciationAliases': aliases, 'displayWordingPreserved': True, 'speechSpeed': 1,
        'renderUnit': 'meaningful-concept-paragraph', 'sceneGapSeconds': 0, 'forcedObservationHolds': 0}
    target = P / 'script/narration.spoken.ko.json'
    text = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'
    if VOICE.exists() and (not target.exists() or target.read_text(encoding='utf8') != text):
        raise RuntimeError('Preserve generated v2 PCM; do not silently change its input.')
    target.write_text(text, encoding='utf8')
    (P / 'script/narration.spoken.ko.txt').write_text('\n'.join(lines) + '\n', encoding='utf8')
    spec = importlib.util.spec_from_file_location('caption_preflight', P / 'production/time-captions.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from PIL import ImageFont
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 60)
    layout = [{'id': x['id'], 'koLines': module.wrap(x['ko'], font), 'enLines': module.wrap(x['en'], font)} for x in clauses]
    manifest = read(P / 'production/tts-manifest.json')
    assert manifest['revision'] == REVISION and manifest['tts']['renderMode'] == 'line'
    assert manifest['paths']['script'] == target.relative_to(R).as_posix()
    assert (R / manifest['tts']['outputDir']).resolve() == VOICE.parent.resolve()
    report = {'revision': REVISION, 'status': 'current-full-paragraphs-and-caption-clauses-validated; synthesis-not-started-by-preflight',
        'displayScriptSha256': sha(P / 'script/narration.ko.json'), 'derivedSpokenSha256': sha(target),
        'clausesSha256': sha(P / 'script/clauses.json'), 'ttsManifestSha256': sha(P / 'production/tts-manifest.json'),
        'approvedReferenceSha256': sha(R / manifest['tts']['reference']),
        'approvedReferenceTextSha256': sha(R / manifest['tts']['referenceText']),
        'paragraphs': len(lines), 'clauses': len(clauses), 'sceneCount': 1,
        'paragraphTakeNormalization': manifest['tts']['paragraphLevelNormalization'], 'pronunciationAliases': aliases,
        'spokenHangulSyllables': len(re.findall('[가-힣]', ''.join(lines))), 'captionLayoutPreflight': layout,
        'fixedCaptionCenter': [510, 1380], 'captionMaxLines': 2, 'gpuAllocatorCapMiB': 6144,
        'gpuMinimumFreeMiB': 7500, 'costlyJobsStarted': 0, 'actualPaceHumanListening': 'pending',
        'sourcePcmGenerated': VOICE.exists()}
    L.mkdir(parents=True, exist_ok=True)
    (L / 'audio-input-preflight.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ['status', 'paragraphs', 'clauses', 'spokenHangulSyllables', 'costlyJobsStarted']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
