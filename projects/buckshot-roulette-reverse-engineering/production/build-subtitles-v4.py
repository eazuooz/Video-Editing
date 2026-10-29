"""Prepare reviewed KO/EN meaning groups and build additive v4 clause captions.

CPU only. Five new paragraphs use current whole-source ASR word timestamps.
Fourteen unchanged paragraphs retain the reviewed v1 cue text and relative
timing, after exact stored PCM and script comparisons. No baseline is modified.
This script does not claim human listening or final audiovisual approval.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / 'production/local/audio-v1'
OUT = PROJECT / 'production/local/audio-v4'
KO = PROJECT / 'script/revision-v4/narration.ko.json'
EN = PROJECT / 'script/revision-v4/narration.en.json'
PLAN = PROJECT / 'planning/revision-v4-workflow.json'
MAP = PROJECT / 'planning/caption-semantic-map-v4.json'

spec = importlib.util.spec_from_file_location('buckshot_baseline_captions', PROJECT / 'production/build-clause-subtitles.py')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

NEW_IDS = {'01-01', '01-02', '02-01', '02-02', '08-01'}
NEW_REVIEW = {
    '01-01': 'Same opening question, original/prototype left-right comparison, and REA + AI + 3D toolchain goal. Quickly is a qualitative thesis, not a measured speedup.',
    '01-02': 'Same five steps: overview; executable/data; code/resource branches; agent implementation and new visuals; engine assembly into a playable prototype. This is the generic workflow.',
    '02-01': 'Same REA name, analysis role, agent definition, request/evidence loop, and use of evidence for implementation. REA is not described as the AI model.',
    '02-02': 'Same CLI/MCP distinction, MCP definition, optional Ghidra/resource tools, optional Tripo/Blender, engine destinations, and transition into the actual experiment. Optional tools must remain visually distinct from tools actually used.',
    '08-01': 'Same return to REA, readable scripts, independently written code, Blender/Godot playable result, reduced guessing and earlier idea testing, and foundation-prototype conclusion. No numeric speedup or full-original equivalence claim.',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def key(scene, paragraph):
    return f'{scene}-{int(paragraph):02}'


def compact(text):
    return re.sub(r'\s+', '', text)


def normalized(text):
    """Only explicit equivalent names/numbers; retain raw ASR beside alignment."""
    text = re.sub(r'\s+', ' ', text.lower()).strip()
    pairs = [
        ('reverse engineer anything', '리버스 엔지니어 애니씽'),
        ('reverse', '리버스'), ('engineer', '엔지니어'), ('anything', '애니씽'),
        ('gdscript', '지디스크립트'), ('ghidra', '기드라'),
        ('blender', '블렌더'), ('godot', '고도'), ('unity', '유니티'),
        ('unreal', '언리얼'), ('tripo', '트리포'), ('트라이포', '트리포'),
        ('mcp', '엠씨피'), ('rea', '알이에이'), ('ai', '인공지능'),
        ('3d', '쓰리디'),
    ]
    for canonical, spoken in pairs:
        text = text.replace(canonical, spoken)
    return base.review.normalized(text)


def display(text):
    replacements = [
        ('리버스 엔지니어 애니씽', 'Reverse Engineer Anything'),
        ('인공지능 에이전트', 'AI 에이전트'),
        ('인공지능이 외부 도구', 'AI가 외부 도구'),
        ('인공지능가 외부 도구', 'AI가 외부 도구'),
        ('트라이포', 'Tripo'), ('트리포', 'Tripo'), ('엠씨피', 'MCP'),
        ('기드라', 'Ghidra'), ('쓰리디', '3D'), ('블렌더', 'Blender'),
        ('유니티', 'Unity'), ('언리얼', 'Unreal'), ('고도', 'Godot'),
    ]
    for spoken, canonical in replacements:
        text = text.replace(spoken, canonical)
    return base.display(text)


def sentences(text):
    return [value.strip() for value in re.split(r'(?<=[.!?])\s+', text.strip()) if value.strip()]


def planned_rows():
    ko, en, workflow = read(KO), read(EN), read(PLAN)
    assert [(s['id'], len(s['lines'])) for s in ko['scenes']] == [(s['id'], len(s['lines'])) for s in en['scenes']]
    mapping = {key(m['scene'], m['paragraph']): m for m in workflow['audioReuseMapping']}
    old_plan = read(PROJECT / 'planning/caption-semantic-map.json')
    old_groups = {key(r['scene'], r['paragraph']): r['semanticGroups'] for r in old_plan['groups']}
    old_timing = {key(e['scene_id'], e['paragraph']): e for e in read(BASE / 'narration.timing.json')['entries']}
    rows = []
    for scene, translated in zip(ko['scenes'], en['scenes']):
        for number, (spoken, english) in enumerate(zip(scene['lines'], translated['lines']), 1):
            ident = key(scene['id'], number)
            rule = mapping[ident]
            row = {'id': ident, 'scene': scene['id'], 'paragraph': number, 'ko': spoken, 'en': english, 'mode': rule['mode']}
            if rule['mode'] == 'reuse':
                old_id = key(rule['baselineScene'], rule['baselineParagraph'])
                old = old_timing[old_id]
                assert old['text'] == spoken and old['text_en'] == english, ('Changed retained text', ident)
                groups = copy.deepcopy(old_groups[old_id])
                assert compact(' '.join(g['koText'] for g in groups)) == compact(spoken)
                assert compact(' '.join(g['enText'] for g in groups)) == compact(english)
                row.update(baselineId=old_id, semanticGroups=groups, semanticReview='Direct complete KO/EN reread; exact previously reviewed meaning groups retained.')
            else:
                assert ident in NEW_IDS
                korean_sentences, english_sentences = sentences(spoken), sentences(english)
                assert len(korean_sentences) == len(english_sentences), ('New semantic pairing requires review', ident)
                groups, cursor = [], 0
                for index, (ks, es) in enumerate(zip(korean_sentences, english_sentences)):
                    length = len(normalized(ks))
                    groups.append({'koSentenceIndices': [index], 'enSentenceIndices': [index], 'koText': ks, 'enText': es,
                                   'koCharacterStart': cursor, 'koCharacterEnd': cursor + length,
                                   'enClauses': base.clauses(es, 46), 'mappingReview': NEW_REVIEW[ident]})
                    cursor += length
                assert cursor == len(normalized(spoken))
                row.update(semanticGroups=groups, semanticReview=NEW_REVIEW[ident], koClauses=base.clauses(spoken, 32))
                if ident == '02-01':
                    # Keep the named concept AI agent together across cues.
                    for index in range(len(row['koClauses']) - 1):
                        if row['koClauses'][index].endswith(' 인공지능') and row['koClauses'][index + 1].startswith('에이전트'):
                            row['koClauses'][index] = row['koClauses'][index][:-len(' 인공지능')]
                            row['koClauses'][index + 1] = '인공지능 ' + row['koClauses'][index + 1]
                expected_display = scene.get('displayLines', scene['lines'])[number - 1]
                assert compact(display(spoken)) == compact(base.display(expected_display)), ('Display alias mismatch', ident, display(spoken), expected_display)
                assert compact(' '.join(row['koClauses'])) == compact(spoken)
                row['displayText'] = display(spoken)
                assert compact(' '.join(display(c) for c in row['koClauses'])) == compact(row['displayText']), ('Display alias crossed a clause boundary', ident)
            rows.append(row)
    assert len(rows) == 19 and sum(r['mode'] == 'reuse' for r in rows) == 14
    assert {r['id'] for r in rows if r['mode'] != 'reuse'} == NEW_IDS
    return rows


def write_semantic_map(rows):
    payload = {'schemaVersion': 1, 'revision': 'v4', 'reviewedAt': datetime.now(timezone.utc).isoformat(),
               'status': 'complete-KO-EN-text-meaning-reviewed-timing-pending',
               'reviewer': 'assistant direct complete reading of all 19 KO/EN paragraphs and the primary-source REA fact record',
               'manualSemanticReview': True, 'humanListening': False, 'userApproval': False,
               'audioTimingVerified': False, 'finalAudiovisualReview': 'pending',
               'koScriptSha256': digest(KO), 'enScriptSha256': digest(EN), 'workflowSha256': digest(PLAN),
               'primaryFacts': 'planning/rea-explainer-v4.json', 'newParagraphs': 5, 'reusedParagraphs': 14,
               'newScriptFactReview': {
                   'status': 'suitable-for-selected-workflow-documentary',
                   'reviewedParagraphs': sorted(NEW_IDS),
                   'primaryFactsSha256': digest(PROJECT / 'planning/rea-explainer-v4.json'),
                   'reaNameAndRoleCorrect': True, 'agentMcpCliRolesCorrect': True,
                   'genericToolsSeparatedFromActualRoute': True,
                   'coreThesis': 'Use analysis evidence and AI-connected production tools to reach a playable foundation prototype; rule examples support that workflow.',
                   'speedClaimScope': 'Qualitative question and workflow benefit; no measured numeric speedup asserted.',
                   'requiredVisualBoundary': 'Diagrams and summarized evidence screens must be labeled as our explanation or analysis results, never presented as captured REA software UI or a previously recorded tool action.',
                   'actualRoute': 'REA CLI, shipped readable GDScript, independently written code, Blender Python, Godot.',
                   'notUsedInThisCase': ['Ghidra', 'Tripo MCP', 'Blender MCP'],
                   'speechCorrectionsVerified': '인공지능가 was corrected to 인공지능이; Tripo pronunciation is 트리포.',
               },
               'groups': rows,
               'timingPolicy': 'New paragraphs: word-aligned current ASR. Unchanged paragraphs: old clause text and relative timing retained only after exact PCM validation. English clauses stay inside the reviewed Korean sentence-meaning interval; inner English boundaries are estimated.',
               'displayAliases': {'알이에이': 'REA', '리버스 엔지니어 애니씽': 'Reverse Engineer Anything', '인공지능 에이전트': 'AI 에이전트', '엠씨피': 'MCP', '기드라': 'Ghidra', '트리포 / 트라이포': 'Tripo', '쓰리디': '3D', '블렌더': 'Blender', '유니티': 'Unity', '언리얼': 'Unreal', '고도': 'Godot'},
               'grammarAlias': 'Spoken 인공지능이 외부 도구 and displayed AI가 외부 도구 express the same subject with the correct Korean particle.'}
    save(MAP, payload)
    return payload


def append_cue(cues, language, cue):
    cue['id'] = len(cues[language]) + 1
    cues[language].append(cue)
    return cue['id']


def read_srt(path):
    def seconds(stamp):
        hour, minute, rest = stamp.replace(',', '.').split(':')
        return int(hour) * 3600 + int(minute) * 60 + float(rest)
    cues = []
    for block in re.split(r'\n\s*\n', Path(path).read_text(encoding='utf-8-sig').strip()):
        lines = block.splitlines()
        begin, end = lines[1].split(' --> ')
        cues.append({'id': int(lines[0]), 'start': seconds(begin), 'end': seconds(end), 'text': '\n'.join(lines[2:])})
    assert [c['id'] for c in cues] == list(range(1, len(cues) + 1))
    return cues


def finalize_alignment():
    """Only actual final files plus a separate direct text review can approve."""
    source = read(OUT / 'review/caption-alignment-review.json')
    direct = read(OUT / 'review/caption-direct-review.json')
    assert direct['manualSemanticReview'] is True and direct['allParagraphTextsRetained'] is True
    assert direct['koSha256'] == source['koSha256'] == digest(OUT / 'narration.ko.clauses.srt')
    assert direct['enSha256'] == source['enSha256'] == digest(OUT / 'narration.en.clauses.srt')
    assert direct['sourceAudioSha256'] == source['sourceWavSha256'] == digest(OUT / 'narration.wav')
    root = ROOT / 'output/buckshot-roulette-reverse-engineering-v4'
    tracks, captions_by_language = [], {}
    for language in ['ko', 'en']:
        final = root / f'{PROJECT.name}.{language}.srt'
        assert final.is_file(), 'Final captions do not exist yet; approval remains pending.'
        original = read_srt(OUT / f'narration.{language}.clauses.srt')
        current = read_srt(final)
        assert len(original) == len(current)
        for before, after in zip(original, current):
            assert compact(before['text']) == compact(after['text'])
            assert abs(after['start'] - before['start'] - 2.0) < .002
            assert abs(after['end'] - before['end'] - 2.0) < .002
        captions_by_language[language] = current
        tracks.append({'language': language, 'path': final.relative_to(ROOT).as_posix(), 'sha256': digest(final), 'cues': len(current)})
    paragraphs, covered = [], {'ko': [], 'en': []}
    for paragraph in source['paragraphMapping']:
        boundaries, texts = [], {}
        item = {'id': paragraph['id'], 'scene': paragraph['scene'], 'paragraph': paragraph['paragraph'],
                'semanticMeaningReviewed': True, 'allTextRetained': True}
        for language in ['ko', 'en']:
            ids = paragraph[language + 'CueIds']
            track = captions_by_language[language]
            selected = [track[i - 1] for i in ids]
            assert all(c['id'] == ident for c, ident in zip(selected, ids))
            boundaries.append((selected[0]['start'], selected[-1]['end']))
            texts[language] = ' '.join(c['text'].replace('\n', ' ') for c in selected)
            item[language + 'Cues'] = ids
            item[language + 'Text'] = texts[language]
            covered[language].extend(ids)
        assert abs(boundaries[0][0] - boundaries[1][0]) <= .002 and abs(boundaries[0][1] - boundaries[1][1]) <= .002
        item.update(start=boundaries[0][0], end=boundaries[0][1])
        paragraphs.append(item)
    for language, ids in covered.items():
        assert ids == list(range(1, len(captions_by_language[language]) + 1))
    assert len(paragraphs) == 19
    report = {'schemaVersion': 1, 'status': 'approved-semantic-paragraph-alignment', 'approved': True,
              'manualSemanticReview': True, 'reviewedAt': datetime.now(timezone.utc).isoformat(),
              'reviewer': 'assistant: direct complete KO/EN cue and paragraph meaning review, with exact final file verification',
              'reviewScope': 'Semantic caption alignment only; not human listening, moving-picture review, or user approval.',
              'humanListening': False, 'humanViewing': False, 'userApproval': False, 'allParagraphTextsRetained': True,
              'sourceCaptionReview': (OUT / 'review/caption-direct-review.json').relative_to(ROOT).as_posix(),
              'sourceAudioSha256': source['sourceWavSha256'], 'brandingOffsetSeconds': 2,
              'paragraphCount': 19, 'captions': tracks, 'paragraphs': paragraphs}
    save(PROJECT / 'production/caption-alignment-v4.json', report)
    print(json.dumps({'status': report['status'], 'paragraphs': 19, 'tracks': tracks, 'humanListening': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true', help='Prepare the meaning map without audio or GPU work')
    parser.add_argument('--finalize-alignment', action='store_true', help='Require actual final SRT files and direct cue review, then write collector alignment evidence')
    parser.add_argument('--asr', type=Path, default=OUT / 'review/source-full-asr.timestamps.json')
    args = parser.parse_args()
    if args.finalize_alignment:
        assert not args.preflight
        finalize_alignment()
        return
    rows = planned_rows()
    if args.preflight:
        payload = write_semantic_map(rows)
        print(json.dumps({'status': payload['status'], 'paragraphs': len(rows), 'new': 5, 'retained': 14, 'semanticGroups': sum(len(r['semanticGroups']) for r in rows), 'gpuUsed': False}))
        return
    meaning = read(MAP)
    assert meaning['koScriptSha256'] == digest(KO) and meaning['enScriptSha256'] == digest(EN), 'Stale semantic review; inspect changed text before updating it.'
    assert meaning['workflowSha256'] == digest(PLAN)
    voice = OUT / 'narration.wav'
    timing, asr = read(OUT / 'narration.timing.json'), read(args.asr)
    assert asr['audio_sha256'] == digest(voice), 'ASR is not bound to the current v4 WAV.'
    assert asr['timestampMode'] == 'word' and asr['language'] == 'korean'
    old_voice = BASE / 'narration.wav'
    old_report, old_cues = read(BASE / 'review/caption-alignment-review.json'), read(BASE / 'review/clause-cues.json')
    assert old_report['sourceWavSha256'] == digest(old_voice)
    for language in ['ko', 'en']:
        assert old_report[language + 'Sha256'] == digest(BASE / f'narration.{language}.clauses.srt')
    old_paragraphs = {key(r['scene'], r['paragraph']): r for r in old_report['paragraphMapping']}
    old_entries = {key(e['scene_id'], e['paragraph']): e for e in read(BASE / 'narration.timing.json')['entries']}
    import numpy as np
    import soundfile as sf
    new_pcm, rate = sf.read(voice, dtype='float32', always_2d=True)
    old_pcm, old_rate = sf.read(old_voice, dtype='float32', always_2d=True)
    assert rate == old_rate == timing['sample_rate']
    assert len(timing['entries']) == len(rows)
    base.aligner.normalized = normalized
    cues, paragraphs = {'ko': [], 'en': []}, []
    for row, entry in zip(rows, timing['entries']):
        assert key(entry['scene_id'], entry['paragraph']) == row['id'] and entry['text'] == row['ko'] and entry['text_en'] == row['en']
        origin, end = float(entry['start']), float(entry['end'])
        words = [{'text': w['text'], 'timestamp': [max(0, float(w['timestamp'][0]) - origin), min(end - origin, float(w['timestamp'][1]) - origin)]}
                 for w in asr['chunks'] if None not in w['timestamp'] and origin <= sum(w['timestamp']) / 2 < end]
        paragraph = {'id': row['id'], 'scene': row['scene'], 'paragraph': row['paragraph'], 'mode': row['mode'],
                     'sourcePcmStart': origin, 'sourcePcmEnd': end, 'rawExpected': row['ko'], 'rawRecognized': ' '.join(w['text'] for w in words),
                     'koCueIds': [], 'enCueIds': [], 'semanticGroups': [], 'humanListening': False}
        if row['mode'] == 'reuse':
            old = old_entries[row['baselineId']]
            proof = entry['reuse']
            old_a, old_b = int(proof['baselineStartSample']), int(proof['baselineEndSample'])
            new_a, new_b = int(entry['startSample']), int(entry['segmentEndSample'])
            assert np.array_equal(new_pcm[new_a:new_b], old_pcm[old_a:old_b]), ('Retained PCM changed', row['id'])
            offset = origin - float(old['start'])
            old_mapping = old_paragraphs[row['baselineId']]
            remap = {'ko': {}, 'en': {}}
            for language in ['ko', 'en']:
                wanted = set(old_mapping[language + 'CueIds'])
                selected = [c for c in old_cues[language] if c['id'] in wanted]
                assert len(selected) == len(wanted)
                for old_cue in selected:
                    cue = copy.deepcopy(old_cue)
                    cue.update(start=old_cue['start'] + offset, end=old_cue['end'] + offset, scene=row['scene'], paragraph=row['paragraph'],
                               alignment='retained ASR cue shifted with exact unchanged PCM', baselineCueId=old_cue['id'])
                    remap[language][old_cue['id']] = append_cue(cues, language, cue)
                    paragraph[language + 'CueIds'].append(cue['id'])
            for group in old_mapping['semanticGroups']:
                shifted = copy.deepcopy(group)
                shifted.update(start=group['start'] + offset, end=group['end'] + offset,
                               enCueIds=[remap['en'][i] for i in group['enCueIds']])
                paragraph['semanticGroups'].append(shifted)
            paragraph.update(baselineId=row['baselineId'], offsetSeconds=offset, reusedPcmBitExact=True,
                             speechStart=old_mapping['speechStart'] + offset, speechEnd=old_mapping['speechEnd'] + offset,
                             matchingCharacterCoverage=old_mapping['matchingCharacterCoverage'])
        else:
            starts, ends, coverage = base.aligner.align_characters(row['ko'], words, end - origin)
            cursor = 0
            for clause in row['koClauses']:
                length = len(normalized(clause))
                cue = {'start': origin + float(starts[cursor]), 'end': origin + float(ends[cursor + length - 1]),
                       'text': '\n'.join(base.wrapped_lines(display(clause), 32)), 'scene': row['scene'], 'paragraph': row['paragraph'],
                       'alignment': 'current v4 whole-source ASR word matched'}
                paragraph['koCueIds'].append(append_cue(cues, 'ko', cue))
                cursor += length
            assert cursor == len(normalized(row['ko']))
            for group in row['semanticGroups']:
                group_start = origin + float(starts[group['koCharacterStart']])
                group_end = origin + float(ends[group['koCharacterEnd'] - 1])
                weights = [base.weight(c) for c in group['enClauses']]
                total, used, ids = sum(weights), 0, []
                for clause, size in zip(group['enClauses'], weights):
                    begin = group_start + (group_end - group_start) * used / total
                    used += size
                    finish = group_start + (group_end - group_start) * used / total
                    cue = {'start': begin, 'end': finish, 'text': '\n'.join(base.wrapped_lines(clause, 46)),
                           'scene': row['scene'], 'paragraph': row['paragraph'], 'alignment': 'reviewed matching KO sentence group; estimated inner EN clause boundary'}
                    ids.append(append_cue(cues, 'en', cue))
                paragraph['enCueIds'].extend(ids)
                paragraph['semanticGroups'].append(dict(group, start=group_start, end=group_end, enCueIds=ids))
            paragraph.update(speechStart=origin + float(starts[0]), speechEnd=origin + float(ends[-1]), matchingCharacterCoverage=coverage)
        for language in ['ko', 'en']:
            selected = [c for c in cues[language] if c['id'] in set(paragraph[language + 'CueIds'])]
            expected = (row.get('displayText') or base.display(row['ko'])) if language == 'ko' else row['en']
            assert compact(' '.join(c['text'] for c in selected)) == compact(expected), ('Caption text loss', row['id'], language)
        paragraphs.append(paragraph)
    flags = []
    duration = float(timing['duration_seconds'])
    for language, items in cues.items():
        previous = 0
        for cue in items:
            assert 0 <= cue['start'] < cue['end'] <= duration + .002 and cue['start'] >= previous - .002, ('Invalid cue', language, cue)
            assert len(cue['text'].splitlines()) <= 2
            previous = cue['end']
            span = cue['end'] - cue['start']
            cps = len(compact(cue['text'])) / span
            if span < .65 or cps > (18 if language == 'ko' else 23):
                flags.append({'language': language, 'cue': cue['id'], 'seconds': span, 'charactersPerSecond': cps, 'review': 'Inspect actual readability; no automatic content deletion or speech speedup.'})
        (OUT / f'narration.{language}.clauses.srt').write_text('\n\n'.join(f"{c['id']}\n{base.timestamp(c['start'])} --> {base.timestamp(c['end'])}\n{c['text']}" for c in items) + '\n', encoding='utf-8')
    report = {'schemaVersion': 1, 'revision': 'v4', 'status': 'caption-candidate-awaiting-current-audiovisual-review',
              'sourceWavSha256': digest(voice), 'sourceAsrSha256': digest(args.asr), 'semanticMapSha256': digest(MAP),
              'koSha256': digest(OUT / 'narration.ko.clauses.srt'), 'enSha256': digest(OUT / 'narration.en.clauses.srt'),
              'paragraphCount': 19, 'newParagraphs': 5, 'exactPcmRetainedParagraphs': 14,
              'koCueCount': len(cues['ko']), 'enCueCount': len(cues['en']), 'allTextPreserved': True,
              'manualSemanticReview': True, 'humanListening': False, 'userApproval': False,
              'paragraphMapping': paragraphs, 'readingSpeedFlags': flags,
              'englishTimingLimit': 'Sentence meaning is directly reviewed. New English inner clause times are estimated within actual Korean sentence bounds, not English speech timestamps.',
              'finalVisualReview': 'pending actual 1080p and 375px frames with encoded captions'}
    save(OUT / 'review/caption-alignment-review.json', report)
    save(OUT / 'review/clause-cues.json', cues)
    save(OUT / 'review/paragraph-cue-anchors.json', {'schemaVersion': 1, 'sourceWavSha256': digest(voice), 'timeBase': 'body narration seconds, before 2-second branding',
         'paragraphs': [{'id': p['id'], 'start': p['sourcePcmStart'], 'end': p['sourcePcmEnd'], 'speechStart': p['speechStart'], 'speechEnd': p['speechEnd'],
                         'sentences': [{'ko': g['koText'], 'en': g['enText'], 'start': g['start'], 'end': g['end']} for g in p['semanticGroups']]} for p in paragraphs]})
    print(json.dumps({'status': report['status'], 'koCues': len(cues['ko']), 'enCues': len(cues['en']), 'readabilityFlags': len(flags), 'gpuUsed': False}))


if __name__ == '__main__':
    main()
