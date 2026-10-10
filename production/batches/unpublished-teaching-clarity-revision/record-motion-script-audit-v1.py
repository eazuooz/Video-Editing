"""Read-only audit of the next scheduled baseline; do not alter its production."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

root = Path(__file__).resolve().parents[3]
base = 'projects/motion-sickness-games'
target = root / 'production/batches/unpublished-teaching-clarity-revision/motion-script-audit-v1.json'
assert not target.exists(), 'Preserve the existing audit and inspect actual follow-up'
paths = [f'{base}/script/narration.ko.json', f'{base}/script/narration.en.json',
         f'{base}/planning/outline.md', f'{base}/sources/SOURCES.md', f'{base}/project.json']
ko = json.loads((root / paths[0]).read_text('utf-8-sig'))
en = json.loads((root / paths[1]).read_text('utf-8-sig'))
assert len(ko['scenes']) == len(en['scenes']) == 12
assert sum(len(s['lines']) for s in ko['scenes']) == sum(len(s['lines']) for s in en['scenes']) == 60
record = {
    'schemaVersion': 1, 'slug': 'motion-sickness-games',
    'recordedAt': datetime.now(timezone.utc).isoformat(),
    'status': 'read-only-script-audit-awaiting-current-studio-reference-and-native-comparison',
    'baselineVideoId': 'c18rkesgBSw',
    'fullCurrentKoEnParagraphsDirectlyRead': 60,
    'fullOutlineAndInternalSourcesDirectlyRead': True,
    'inputSha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths},
    'directReadChunks': ['25b995', 'c01eb0'],
    'opening': {
        'passed': False,
        'reason': 'The first scene starts detailed cleaning shots and gives its whole-video purpose only in paragraph six. It does not give an independent early 2–4 sentence overview and actual example order before the first detailed example.',
        'preserve': 'All six existing first-scene paragraphs, and the approved explanations/PCM throughout.',
        'revisionNeed': 'Add a post-cat overview explaining the viewer question, aim/view separation, necessary versus added movement, and reading direction after a turn; connect directly to the first cleaning task.',
        'newOverviewWritten': False, 'ttsStarted': False,
    },
    'scriptCausalChain': [
        {'from': '01', 'to': '02', 'question': 'The aim/background comparison raises which motion the player perceives; distinguish sensation theory from developer controls.'},
        {'from': '02', 'to': '03-04', 'question': 'If all motion is not one responsibility, inspect aim mode and separate view input from added shake.'},
        {'from': '04', 'to': '05-06', 'question': 'Removing added effects still leaves repositioning and looking for hidden surfaces; name the separate options and a reset.'},
        {'from': '06', 'to': '07-08', 'question': 'An option must retain spatial understanding after orientation changes; contrast transition duration with arrival cues.'},
        {'from': '08', 'to': '09-10', 'question': 'A reduced transition must still show the target and be discoverable, saved and reversible.'},
        {'from': '10', 'to': '11-12', 'question': 'Revisit the task from another position and conclude with separate responsibilities, readable targets and individual feedback.'},
    ],
    'requiredNativeComparison': {
        'firstTimeTask': 'Before relying on a nozzle/aim label, establish that water reaches a dirty surface and the objective is cleaning it.',
        'pwsCandidate': 'Compare whole-view rotation and independent nozzle/aim motion using actual stable posts/steps; retain the 2022 development-version label.',
        'talosCandidate': 'Explain the relevant puzzle target/orientation cue before short edited shots. Do not imply they are a continuous gravity transition or prove a comfort effect.',
        'screenAnnotations': 'Role-colored tracked background landmarks, red aim/spray direction, labelled target surface; distinguish projected screen movement from world angles and actual measured comfort.',
        'wholeNativePlaybackDoneThisRevision': False,
        'allFinalAnnotationsApproved': False,
    },
    'reference': {
        'videoId': 'OS4CZkBBbW4',
        'fullJaAutomaticTranscriptDirectlyRead': True,
        'transcriptReadChunk': '7eb6cd',
        'observedTitlePublisher': 'Motion Sickness in 3D Games [Planning & Game Design] / Masahiro Sakurai on Creating Games',
        'causalStructureReadFromTranscript': 'Individual differences → visual/body signal mismatch and vehicle comparison → player-side considerations → developer presentation/vertical bob/fixed frame → options and individual feedback.',
        'intentionalIndependentScope': 'Focus on developer controls and readable tasks. Do not copy the reference medication suggestions or turn developer examples into clinical outcomes.',
        'automaticTranscriptUncertainties': ['権利/原理', 'いよいよ', '歓声/慣性', '股関節', '言いにくく'],
        'exactAuthorWordingApproved': False,
        'allContinuousSourcePixelsDirectlyViewed': False,
        'referenceFlowComparisonApproved': False,
    },
    'currentStudioDirectlyReadThisAudit': False,
    'baselineProductionModified': False, 'mediaCreated': False,
    'dependentNarrationCreated': False, 'actualReplacementVideoId': None,
    'finalTimingApproved': False, 'currentMixedAudioApproved': False,
    'allFinalPixelsApproved': False, 'qaApproved': False, 'privateSettingsApproved': False,
    'gitDelivered': False, 'scheduleChanged': False,
    'humanListeningApproved': False, 'publicRightsApproved': False,
}
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'scriptParagraphsKoEnRead': 60, 'openingNeedsAddition': True,
                  'baselineModified': False, 'productionStarted': False}))
