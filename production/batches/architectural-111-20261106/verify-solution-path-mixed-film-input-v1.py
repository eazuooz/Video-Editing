"""Read-only actual mix3 qualification for film; no models, decoders or writes."""
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2] / 'projects/shorts-leveldesign-11-05'
ANALYZER = HERE / 'review-solution-path-mixed-audio-v3.py'
ANALYZER_SHA = 'd0fe902e2acc25ff66bf6eb739f1ba17d2752845f58423aa4d80eac3aa8f76ac'
P3_SHA = '130749fadde42c02a033780df91bac24b1834824889de0ad802bace107dfde06'
BUILD_SHA = '4104787d298372ec8dc5ebfee8324f4e162d36ec2066f4f6860565332e9fb155'
FP = '042d632e5009caa997e9abb838acc127c2eb19c722e68be2a1b0b01aa3892751'
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

class Pending(ValueError): pass
def need(value, reason):
    if not value: raise Pending(reason)
def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def pin(path): return dict(path=str(Path(path).resolve()),sha256=sha(path))
def same(a,b):
    return isinstance(a,dict) and a.get('sha256') == b['sha256'] and Path(a.get('path','')).resolve() == Path(b['path']).resolve()
def bound(row):
    path = Path(row['path']).resolve()
    need(sha(path) == row['sha256'], 'Changed exact mixed-review evidence')
    return path
def load_analyzer():
    need(sha(ANALYZER) == ANALYZER_SHA, 'Reviewed numerical analyzer changed')
    spec = importlib.util.spec_from_file_location('film_actual_mix3_analysis',ANALYZER)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def qualify(record, numerical):
    """Explicit content disposition plus exact recomputed numerical evidence.

    A raw-only paragraph3 context diagnostic may remain visible after its
    existing scalar provenance review. Every output-stage, whole-explanation,
    boundary or invalid-word flag blocks this production qualification.
    """
    need(record.get('schemaVersion') == 3 and record.get('topicId') == '11.05'
         and record.get('finalMixAccepted') is True
         and record.get('disposition') == 'qualified-for-film-production-not-listening'
         and record.get('actualListening') is False and record.get('humanApproval') is False,
         'Explicit current technical mixed3 disposition required')
    need(record['exactCounts'] == dict(physical=51,wholeParagraphs=14,joins=13,coveredMixSamples=10579202)
         and numerical['actualMixedRecognitionComplete'] and numerical['fullActualMixCoverage'],
         'All51 takes and27 actual mixed windows required')
    need(record['retainedLiteralDifferences'] == numerical['retainedLiteralDifferences']
         and record.get('literalDifferencesExplicitlyReviewed') is True and record.get('aliasesApplied') is False,
         'Actual literal differences require explicit review without aliases')
    need(record.get('retainedFlags') == numerical['flags'], 'Preserve every actual mixed flag')
    for flag in numerical['flags']:
        need(flag['kind'] == 'sustained-word-body-decline' and flag.get('scope') == 'paragraph'
             and flag.get('paragraph') == 3 and flag.get('stage') == 'raw',
             'Unresolved mixed output/range/boundary/word flag blocks production')
        need(same(record.get('rawP3Disposition'),pin(PROJECT/'raw-p3-cross-context-level-review-v1.json'))
             and sha(PROJECT/'raw-p3-cross-context-level-review-v1.json') == P3_SHA
             and record.get('rawParagraphDiagnosticRetained') is True,
             'Retain explicit raw-only P3 context diagnostic and scalar provenance')
    need([g['paragraph'] for g in numerical['wholeExplanations']] == [8,13], 'Both whole rewritten explanations required')
    for group in numerical['wholeExplanations']:
        need(set(group['trends']) == {'raw','normalized','prepared','voice','mix'}, 'All current PCM stages required')
        for trend in group['trends'].values():
            need(trend['words'] >= 9 and trend['spanSeconds'] >= 6 and not trend['suspect'],
                 'Whole P8/P13 fails unchanged nine-word/six-second/decline criterion')
    return True

def verify(audio_build):
    need(sha(__file__) == SELF_SHA, 'Imported mixed-film qualifier changed')
    path = PROJECT/'mixed-asr-content-review-v3.json'
    need(path.is_file(), 'Pending actual mixed-ASR3 numerical/content disposition; observe existing coordinator')
    record = read(path)
    need(same(record.get('audioBuild'),pin(audio_build)) and sha(audio_build) == BUILD_SHA,
         'Mixed3 disposition belongs to another actual build')
    analyzer = load_analyzer()
    need(Path(audio_build).resolve() == analyzer.BUILD.resolve(), 'Exact current mix8 path required')
    for key, expected in [('actualJob',analyzer.JOB),('actualReview',analyzer.REVIEW)]:
        need(bound(record[key]) == expected.resolve(), 'Exact new mixed3 job/review required')
    need(read(analyzer.JOB)['fingerprint'] == FP, 'Old mixed recognition cannot qualify')
    numerical_path = bound(record['wordLevels'])
    need(numerical_path.is_relative_to(analyzer.JOB.parent/'mixed-stage-word-level-review-v3'), 'New numerical review namespace required')
    numerical = read(numerical_path)
    need(numerical == analyzer.analyze(), 'Saved numerical report differs from actual blind caches and PCM')
    qualify(record,numerical)
    need(sha(__file__) == SELF_SHA and sha(ANALYZER) == ANALYZER_SHA, 'Qualification sources changed during review')
    return dict(content=pin(path),job=record['actualJob'],review=record['actualReview'],wordLevels=record['wordLevels'],
                rawP3Disposition=record.get('rawP3Disposition'),actualListening=False,humanApproval=False)
