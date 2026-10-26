"""Read-only selection of an immutable complete-current-PCM recognition record."""
from pathlib import Path
import math
from audio_revision import P, R, L, VOICE, REVISION, read, sha


def select_asr(explicit_path=None, reason=None):
    voice_hash = sha(VOICE)
    default = L / f'asr-voice-{voice_hash[:12]}.json'
    selected = default
    if explicit_path:
        selected = Path(explicit_path)
        if not selected.is_absolute():
            selected = (L if selected.parent == Path('.') else R) / selected
    if (selected.suffix.lower() != '.json' or selected.resolve().parent != L.resolve()
            or not selected.is_file()):
        raise RuntimeError('ASR selection must be an existing JSON directly inside current audio attempt.')
    alternative = selected.resolve() != default.resolve()
    if alternative and (not isinstance(reason, str) or len(reason.strip()) < 10):
        raise RuntimeError('Record an explicit --asr-reason for the alternative; original raw ASR is preserved.')
    current = read(selected)
    original = read(default)
    derived = current.get('recordKind') == 'derived-paragraph-selection'
    for name, document in [('selected', current), ('original full', original)]:
        if (document.get('sha256') != voice_hash or document.get('role') != 'voice'
                or document.get('revision') != REVISION or document.get('fullInput') is not True
                or (document.get('rawRecognitionUnmodified') is not True and not (name == 'selected' and derived))
                or document.get('expectedTextPromptUsed') is not False
                or not document.get('chunks') or not isinstance(document.get('text'), str)):
            raise RuntimeError(name + ' ASR must cover the complete unchanged current PCM with unmodified recognition.')
        source = Path(document.get('input', ''))
        if not source.is_absolute(): source = R / source
        if source.resolve() != VOICE.resolve():
            raise RuntimeError(name + ' recognition input path differs from current PCM.')
    script = R / read(P / 'production/tts-manifest.json')['paths']['script']
    if derived:
        import importlib.util
        spec = importlib.util.spec_from_file_location('teardown_evidence_assembly', P / 'production/assemble-asr-evidence.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if current != module.build_derived():
            raise RuntimeError('Derived recognition must reproduce the exact unedited source chunk evidence.')
        verification = 'All seven PCM paragraph ranges and both raw report hashes reproduce the derived chunks exactly.'
    elif 'paragraphs' in current:
        timing_path = VOICE.with_suffix('.timing.json')
        timing = read(timing_path)
        rows = current['paragraphs']
        entries = timing['entries']
        if (current.get('completePcmSha256') != voice_hash
                or current.get('timingSha256') != sha(timing_path)
                or timing.get('voiceSha256') != voice_hash
                or current.get('originalFullAsrPreserved') is not True
                or len(rows) != len(entries)):
            raise RuntimeError('Alternative paragraph ASR must bind every current PCM paragraph and immutable timing.')
        rate = 24000
        for row, entry in zip(rows, entries):
            if (row.get('index') != entry['index']
                    or row.get('startSample') != round(entry['start'] * rate)
                    or row.get('endSample') != round(entry['end'] * rate)
                    or len(row['raw']['chunks']) != len(row['adjusted'])):
                raise RuntimeError('Paragraph recognition coverage differs from actual complete PCM entries.')
            for raw, adjusted in zip(row['raw']['chunks'], row['adjusted']):
                if raw['text'] != adjusted['text']:
                    raise RuntimeError('Paragraph recognized text has been edited.')
                expected_times = [None if t is None else max(entry['start'], min(entry['end'], t - .3 + entry['start']))
                                  for t in raw['timestamp']]
                if adjusted['timestamp'] != expected_times:
                    raise RuntimeError('Paragraph word times must retain the documented300ms-pad offset only.')
        if (''.join(row['raw']['text'] for row in rows) != current['text']
                or [word for row in rows for word in row['adjusted']] != current['chunks']
                or current.get('expected') != ' '.join(entry['text'] for entry in entries)):
            raise RuntimeError('Paragraph text/chunks are not the complete original recognition in order.')
        verification = 'All current PCM paragraph sample ranges and unedited raw words/timestamp offsets verified.'
    else:
        if current.get('expectedSourceSha256') != sha(script):
            raise RuntimeError('Selected whole-voice ASR refers to another expected source.')
        verification = 'Complete current PCM and expected-source hashes verified.'
    return selected, current, {
        'selection': 'explicit-alternative' if alternative else 'original-full-voice',
        'selectedPath': str(selected.resolve()), 'selectedSha256': sha(selected),
        'originalFullAsrPath': str(default.resolve()), 'originalFullAsrSha256': sha(default),
        'voiceSha256': voice_hash, 'reason': (reason.strip() if alternative else 'Default original complete-voice recognition.'),
        'bothRawRecordsPreserved': True, 'selectedRecordModified': False,
        'selectedRecordKind': current.get('recordKind', 'raw-recognition'),
        'derivedFromUnmodifiedSources': derived,
        'sourceReports': current.get('sourceReports', []) if derived else [],
        'timestampCorrections': current.get('timestampCorrections', []) if derived else [],
        'verification': verification, 'actualListening': 'pending',
        'recognitionContentMatches': 'Must still pass strict whole-text validation; selection does not establish accuracy.',
    }
