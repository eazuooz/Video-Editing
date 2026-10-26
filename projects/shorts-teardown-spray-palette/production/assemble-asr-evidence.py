"""Select whole measured paragraphs from two unmodified ASR reports of one PCM.

Recognized text is copied unchanged. The only permitted timestamp correction is
paragraph1's final word ending inside a hash-verified, assembler-inserted all-zero
PCM join. Its raw time is preserved alongside its effective source-PCM end.
No model, recognition, audio editing or expected-text prompt runs here.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import math
import hashlib
from audio_revision import P, R, L, VOICE, REVISION, CAPTION_CLAUSES, guard, read, sha, normalize_speech


def verified_zero_join(timing, entry, next_entry, raw_timestamp):
    """Read actual float samples; never infer silence from ASR or an amplitude gate."""
    import numpy as np
    import soundfile as sf
    rate = timing['sample_rate']
    if rate != 24000:
        raise RuntimeError('Only the current approved24k mono PCM join can be checked.')
    first, last = round(entry['end'] * rate), round(next_entry['start'] * rate)
    joins = [j for j in timing['joins'] if j['afterLineIndex'] == entry['lineIndex']]
    if (len(joins) != 1 or joins[0]['insertedSamples'] != last - first
            or joins[0]['seconds'] != entry['end'] or joins[0].get('speechOrBreathTrimmed') is not False
            or not entry['start'] <= raw_timestamp[0] < entry['end'] < raw_timestamp[1] <= next_entry['start']):
        raise RuntimeError('The crossing estimate does not lie exclusively in the recorded inserted join.')
    levels_path = L / 'line-levels.json'
    levels = read(levels_path)
    row = levels['paragraphs'][entry['lineIndex']]
    if (levels['voiceSha256'] != sha(VOICE)
            or row['destinationSampleRange'][1] != first or row.get('trimmedSamples') != 0
            or row.get('rawSamplesRetained') is not True
            or sha(R / row['rawTake']) != row['rawTakeSha256']
            or sha(R / row['normalizedTake']) != row['normalizedTakeSha256']):
        raise RuntimeError('Original paragraph sample-preservation evidence changed.')
    samples, actual_rate = sf.read(VOICE, start=first, stop=last, dtype='float32', always_2d=False)
    if (actual_rate != rate or samples.ndim != 1 or len(samples) != last - first
            or len(samples) == 0 or np.count_nonzero(samples) != 0):
        raise RuntimeError('Actual join is not entirely exact-zero PCM; no boundary correction allowed.')
    removed_end = round(raw_timestamp[1] * rate)
    removed = samples[:removed_end - first]
    return {'policy': 'source-pcm-end-clamp-inside-proven-zero-assembler-join',
            'voiceSha256': sha(VOICE), 'lineLevelsSha256': sha(levels_path),
            'timingSha256': sha(VOICE.with_suffix('.timing.json')),
            'rawTimestamp': list(raw_timestamp), 'effectiveTimestamp': [raw_timestamp[0], entry['end']],
            'correctionSeconds': raw_timestamp[1] - entry['end'],
            'entireInsertedJoinSampleRange': [first, last], 'insertedSamples': len(samples),
            'adjustedIntervalSampleRange': [first, removed_end], 'adjustedIntervalSamples': len(removed),
            'sampleRate': rate, 'nonzeroSampleCount': int(np.count_nonzero(samples)),
            'maximumAbsoluteSampleValue': float(np.max(np.abs(samples))),
            'entireJoinDecodedFloat32LESha256': hashlib.sha256(samples.astype('<f4').tobytes()).hexdigest(),
            'adjustedIntervalDecodedFloat32LESha256': hashlib.sha256(removed.astype('<f4').tobytes()).hexdigest(),
            'originalRawTakeSha256': row['rawTakeSha256'],
            'originalNormalizedTakeSha256': row['normalizedTakeSha256'],
            'audioFileModified': False, 'actualListening': 'pending',
            'exactAcousticWordBoundaryClaimed': False,
            'reason': 'ASR word-end estimate extends into exact inserted zero samples. Effective caption end is limited to the preserved source paragraph PCM endpoint; no audio sample is removed.'}


def build_derived():
    from asr_selection import select_asr
    voice_hash = sha(VOICE)
    full_path, full, _ = select_asr()
    paragraph_path = L / f'asr-voice-paragraphs-{voice_hash[:12]}.json'
    _, paragraphs, _ = select_asr(paragraph_path,
        'Independent recognition of all current PCM paragraphs; original complete-run ASR preserved.')
    timing_path = VOICE.with_suffix('.timing.json')
    timing = read(timing_path)
    entries = timing['entries']
    if len(entries) != 7 or len(paragraphs['paragraphs']) != 7:
        raise RuntimeError('Exactly seven current source paragraphs must be covered.')
    norm = lambda text: normalize_speech(text, {})
    chunks, provenance, selections, corrections = [], [], [], []
    first = entries[0]
    next_start = entries[1]['start']
    # First identify all original words in paragraph1's slot, then strictly check
    # the recorded raw-take bounds. Do not silently drop a crossing final word.
    first_indices = [i for i, word in enumerate(full['chunks'])
                     if word.get('timestamp') and word['timestamp'][0] is not None
                     and first['start'] <= word['timestamp'][0] < next_start]
    for position, entry in enumerate(entries):
        if position == 0:
            source_path, source = full_path, full
            selected = [(i, full['chunks'][i]) for i in first_indices]
            row_index = None
        else:
            source_path, source = paragraph_path, paragraphs
            row_index = position
            offset = sum(len(row['adjusted']) for row in paragraphs['paragraphs'][:position])
            selected = [(offset + i, word) for i, word in enumerate(paragraphs['paragraphs'][position]['adjusted'])]
        if not selected:
            raise RuntimeError('No recognized words cover paragraph' + str(position + 1))
        for source_index, word in selected:
            timestamp = word.get('timestamp')
            if (not isinstance(timestamp, (list, tuple)) or len(timestamp) != 2
                    or any(type(t) not in (int, float) or not math.isfinite(t) for t in timestamp)
                    or not entry['start'] <= timestamp[0] < timestamp[1]):
                raise RuntimeError('Measured word crosses actual paragraph PCM bounds; no derived ASR written: ' +
                    json.dumps({'paragraph': position + 1, 'pcmBounds': [entry['start'], entry['end']],
                                'source': str(source_path.resolve()), 'sourceIndex': source_index,
                                'word': word}, ensure_ascii=False))
            correction = None
            effective = list(timestamp)
            if timestamp[1] > entry['end']:
                if position != 0 or source_index != selected[-1][0]:
                    raise RuntimeError('Only paragraph1 final-word overhang into exact inserted zero PCM is eligible.')
                correction = verified_zero_join(timing, entry, entries[1], timestamp)
                effective = correction['effectiveTimestamp']
                corrections.append(dict(correction, sourceReportSHA256=sha(source_path), sourceChunkIndex=source_index))
            if source['chunks'][source_index] != word:
                raise RuntimeError('Selected chunk differs from its unmodified source index.')
            copied = {'text': word['text'], 'timestamp': effective}
            provenance.append({'derivedChunkIndex': len(chunks), 'paragraphIndex': position + 1,
                               'sourceReportPath': str(source_path.resolve()), 'sourceReportSHA256': sha(source_path),
                               'sourceChunkIndex': source_index, 'paragraphRowIndex': row_index,
                               'pcmSampleRange': [round(entry['start'] * 24000), round(entry['end'] * 24000)],
                               'rawSourceChunk': word, 'effectiveChunk': copied,
                               'textCopiedWithoutChange': True,
                               'timestampCopiedWithoutChange': correction is None,
                               'timestampCorrection': correction})
            chunks.append(copied)
        text = ''.join(word['text'] for _, word in selected)
        if position == 0 and norm(text) != norm(entry['text']):
            raise RuntimeError('Selected paragraph1 differs from current source; names and words cannot be changed.')
        selections.append({'paragraphIndex': position + 1, 'lineIndex': entry['lineIndex'],
                           'pcmStart': entry['start'], 'pcmEnd': entry['end'], 'selectedText': text,
                           'sourceReportSHA256': sha(source_path), 'sourceChunkIndices': [i for i, _ in selected],
                           'selectionReason': ('Full-run paragraph1 retained because the independent first paragraph differs.'
                             if position == 0 else 'Independent whole-paragraph recognition retained; complete raw report preserved.')})
    text = ''.join(word['text'] for word in chunks)
    lines = [entry['text'] for entry in entries]
    spec = importlib.util.spec_from_file_location('teardown_numeric_audit', P / 'production/reconcile-numeral-spellings.py')
    audit_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_module)
    audit_module.build_audit(lines, read(CAPTION_CLAUSES)['clauses'], {'text': text, 'chunks': chunks}, timing['duration_seconds'])
    script = R / read(P / 'production/tts-manifest.json')['paths']['script']
    return {
        'schemaVersion': 1, 'revision': REVISION, 'role': 'voice',
        'recordKind': 'derived-paragraph-selection', 'input': str(VOICE.resolve()),
        'sha256': voice_hash, 'completePcmSha256': voice_hash, 'fullInput': True,
        'inputDurationSeconds': timing['duration_seconds'], 'text': text, 'chunks': chunks,
        'expected': ' '.join(lines), 'expectedSourceSha256': sha(script),
        'rawRecognitionUnmodified': False, 'sourceRecognitionsUnmodified': True,
        'textCopiedWithoutEdits': True, 'allTimestampsCopiedWithoutEdits': not corrections,
        'timestampCorrections': corrections, 'expectedTextPromptUsed': False,
        'normalizationAliases': {}, 'timingSha256': sha(timing_path),
        'sourceReports': [{'path': str(path.resolve()), 'sha256': sha(path)} for path in [full_path, paragraph_path]],
        'paragraphSelections': selections, 'chunkProvenance': provenance,
        'method': 'All seven actual PCM paragraphs; full-run paragraph1 plus independent paragraphs2–7. '
                  'No word/number edits or audio trimming. One possible ASR word-end overhang is clamped only '
                  'inside a verified exact-zero assembler join, with raw and effective times both retained. Numeric equivalence is separate.',
        'reason': 'Full-run and independent raw reports disagree; select complete independently verified paragraph evidence.',
        'originalRawReportsPreserved': True, 'humanListening': 'pending',
        'acousticPronunciationVerified': False, 'sourceCoverage': 'All seven PCM paragraph sample ranges in order; interparagraph silence remains in PCM.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()
    guard(require_current_selection=args.write)
    document = build_derived()
    output = L / f"asr-voice-evidence-{document['sha256'][:12]}.json"
    if args.write:
        if output.exists():
            if read(output) != document:
                raise RuntimeError('Existing derived evidence differs; preserve it for review.')
        else:
            with output.open('x', encoding='utf8') as stream:
                stream.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'checked': True, 'paragraphs': 7, 'chunks': len(document['chunks']),
                      'output': str(output.resolve()), 'written': args.write, 'mediaJobs': 0,
                      'actualListening': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
