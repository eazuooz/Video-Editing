"""Display-only notation pass: keep spoken script, audio and every cue time intact."""
from pathlib import Path
import copy
import json
import re
import shutil
from prepare_full import stamp

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/renderformer-explained'
BASE = PROJECT / 'production/body-review'
RULES = PROJECT / 'script/caption-terms.ko.json'


def main():
    rules = json.loads(RULES.read_text(encoding='utf-8'))
    target = BASE / 'timing.json'
    data = json.loads(target.read_text(encoding='utf-8'))
    before = copy.deepcopy(data)
    backup = BASE / 'timing.before-paper-notation.json'
    if not backup.exists():
        shutil.copy2(target, backup)
        shutil.copy2(BASE / 'renderformer.ko.srt', BASE / 'renderformer.before-paper-notation.ko.srt')
    pairs = sorted(rules['replacements'].items(), key=lambda pair: -len(pair[0]))
    pattern = re.compile('|'.join(re.escape(a) for a, _ in pairs))
    changes = []
    for scene in data['scenes']:
        for i, cue in enumerate(scene['cues']):
            spoken = cue.get('spokenKo', cue['ko'])
            text = pattern.sub(lambda m: rules['replacements'][m.group()], spoken)
            for a, b in rules['particleCorrections'].items():
                text = text.replace(a, b)
            if text != spoken:
                changes.append({'page': scene['sourcePage'], 'cue': i, 'before': spoken, 'after': text})
            cue['spokenKo'] = spoken
            cue['ko'] = text
    # Preserve even floating point timestamps exactly (do not recompute them).
    local = [c for s in data['scenes'] for c in s['cues']]
    assert len(local) == len(data['captions']) == 533
    for cue, global_cue in zip(local, data['captions']):
        global_cue['ko'] = cue['ko']
        global_cue['spokenKo'] = cue['spokenKo']
    for a, b in zip(before['captions'], data['captions']):
        assert (a['start'], a['end']) == (b['start'], b['end'])
    assert [(s['firstFrame'], s['frames']) for s in before['scenes']] == [(s['firstFrame'], s['frames']) for s in data['scenes']]
    data['captionNotationRevision'] = rules['revision']
    payload = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    target.write_text(payload, encoding='utf-8')
    (ROOT / 'motion-canvas/src/projects/renderformer-explained/full/narrated/timing.generated.json').write_text(payload, encoding='utf-8')
    old_srt = (BASE / 'renderformer.ko.srt').read_text(encoding='utf-8')
    srt = '\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["ko"]}' for i,c in enumerate(data['captions'])) + '\n'
    assert re.findall(r'^.* --> .*$', old_srt, re.M) == re.findall(r'^.* --> .*$', srt, re.M)
    (BASE / 'renderformer.ko.srt').write_text(srt, encoding='utf-8')
    report = {'revision': rules['revision'], 'changedCues': len(changes), 'timestampsUnchanged': True, 'audioUnchanged': True, 'changes': changes}
    (BASE / 'caption-notation-changes.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Updated {len(changes)}/533 display cues; all times preserved.')


if __name__ == '__main__':
    main()
