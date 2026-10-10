"""Record the current readable-task comparison, without changing the baseline."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

root = Path(__file__).resolve().parents[3]
batch = root / 'production/batches/unpublished-teaching-clarity-revision'
old = json.loads((batch / 'motion-script-audit-v1.json').read_text('utf-8-sig'))
target = batch / 'motion-context-comparison-v2.json'
assert not target.exists(), 'Preserve actual completed observation'
for relative, expected in old['inputSha256'].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
intro = json.loads((batch / 'motion-opening-proposal-v2.json').read_text('utf-8'))
assert len(intro['ko']) == len(intro['en']) == 4
record = {
    'schemaVersion': 2, 'recordedAt': datetime.now(timezone.utc).isoformat(),
    'slug': 'motion-sickness-games', 'baselineVideoId': 'c18rkesgBSw',
    'status': 'read-only-context-comparison-and-independent-opening-prepared',
    'baselineFiveInputSha256Unchanged': True,
    'wholeKoEnRead': {'koParagraphs': 60, 'enParagraphs': 60, 'evidence': 'motion-script-audit-v1.json'},
    'currentStudio': {
        'title': '게임 멀미와 카메라 설계: 화면 움직임을 선택하게 만들기',
        'wholeDescriptionDirectlyRead': True, 'existingThirteenChapterNamesAndLinksRead': True,
        'actualDate': '2026-10-12', 'actualTime': '09:00', 'actualTimezone': 'GMT+0900',
        'actualStatus': '예약됨', 'sdHdComplete': True,
        'evidence': 'shared/assets/presenting-game-scores/raw/motion-studio-schedule-audit-v2.ax.txt',
        'readOnlyPopoverClosedWithEscape': True, 'settingsChanged': False,
    },
    'reference': {
        **old['reference'],
        'directlyViewedFixedVehicleFrameAtBrowserSeconds': 146.022875,
        'fixedFrameObservation': 'A vehicle-shaped foreground remains a visible frame over the moving forest view. The example is labelled Without Shake.',
        'observedDeveloperPresentationIntroAtApproxSeconds': 129,
        'conceptualSequenceCompared': True,
        'comparison': 'The reference introduces individual variation, connects a familiar vehicle example to game motion, then explains developer presentation choices and returns to options and feedback. The independent lesson keeps developer-control scope; add the viewer question and actual example order before its detailed cleaning comparison.',
        'allContinuousSourcePixelsDirectlyViewed': False,
        'finalRevisedLessonFlowApproved': False,
    },
    'normalRateNativeUiObservations': {
        'serverPid': 27140, 'serverCreationObserved': '2026-10-09T10:34:26.837781+09:00',
        'serverRestarted': False, 'sourceAudioMuted': True, 'playbackRate': 1,
        'completedBrowserWindows': [
            {'sourceId': 'PF5L_2g9UVQ', 'start': 187, 'plannedEnd': 227, 'actualAutoPause': 227.064148, 'startedAt': '2026-10-10T14:54:03.780Z'},
            {'sourceId': 'PF5L_2g9UVQ', 'start': 48, 'plannedEnd': 69, 'actualAutoPause': 69.207116, 'startedAt': '2026-10-10T14:55:50.398Z'},
            {'sourceId': 'PF5L_2g9UVQ', 'start': 99, 'plannedEnd': 118, 'actualAutoPause': 118.081055, 'startedAt': '2026-10-10T14:57:06.990Z'},
            {'sourceId': 'PF5L_2g9UVQ', 'start': 132, 'plannedEnd': 169, 'actualAutoPause': 169.155164, 'startedAt': '2026-10-10T14:57:43.144Z'},
            {'sourceId': '6slinvkF0Rs', 'start': 15.8, 'plannedEnd': 52.4, 'actualAutoPause': 52.412985, 'startedAt': '2026-10-10T14:58:56.709Z'},
            {'sourceId': 'PF5L_2g9UVQ', 'start': 169, 'plannedEnd': 187, 'actualAutoPause': 187.009094, 'startedAt': '2026-10-10T15:02:11.109Z'},
        ],
        'focusedPausedFrames': [
            {'sourceId': '6slinvkF0Rs', 'browserSeconds': 48.098293, 'observed': 'Angled stone columns, a red vertical beam, a green beam and a violet beam, and blue barriers are visible. These are game puzzle objects, not our mathematical annotations.'},
            {'sourceId': '6slinvkF0Rs', 'browserSeconds': 36.289905, 'observed': 'The view points toward a held device and overhead stone beams. This alone does not establish the complete puzzle solution or a continuous transition from the bridge shot.'},
        ],
        'sourcePixelsDirectlyObservedAtBrowserSeconds': [194.819138, 213.775215, 69.207116, 118.081055, 169.155164, 35.037676, 52.412985, 187.009094, 48.098293, 36.289905],
        'staleImmediateSeekScreenshotExcluded': 'Immediate initial132 screenshot retained old view; do not claim a native132 frame approval.',
        'browserEndpointOvershootIsNotExactCut': True,
        'allBetweenFramesViewed': False, 'allContinuousSourcePlaybackViewed': False,
    },
    'understandabilityComparison': [
        {
            'game': 'PowerWash Simulator', 'sourceId': 'PF5L_2g9UVQ',
            'taskSeen': 'A water jet reaches the roundabout surface and exposes clean blue metal through the dark dirt.',
            'firstTimeComprehension': 'Strong opening candidate after explicitly naming the cleaning goal. The target, tool and background can be identified without explaining a complex rule set.',
            'preferredOpeningCandidateSeconds': [169, 187],
            'nativeExactBoundaryAndAllUiReviewStillRequired': True,
            'mathOrRoleAnnotation': 'Red labelled spray/aim direction, a separately labelled target surface and tracked background posts; screen projections and examples must not be called measured world angles.',
            'versionLabelRequired': '2022 development demonstration',
            'sourceAdoptionApprovedThisRevision': False,
        },
        {
            'game': 'The Talos Principle 2', 'sourceId': '6slinvkF0Rs',
            'taskSeen': 'Separate trailer shots show a bridge, looking toward a device and an angled puzzle space.',
            'firstTimeComprehension': 'Requires more context than the cleaning task. Introduce the question of reading walls, floors and targets after a view change, with explicit shot transitions.',
            'annotationNeed': 'Mark the actual wall/floor landmarks and the view direction; avoid colours or labels that confuse existing game laser beams with our overlay.',
            'heldClaims': ['continuous puzzle solution', 'same gravity transition across different cuts', 'comfort outcome', 'current accessibility settings'],
            'sourceAdoptionApprovedThisRevision': False,
        },
    ],
    'streamMetadataReadOnlyProbe': {
        'powerWash': {'rFrameRate': '60/1', 'avgFrameRate': '60/1', 'timeBase': '1/15360', 'frames': 36092, 'actualProbeExitCode': 0, 'chunk': '5cbd0f'},
        'talos': {'rFrameRate': '30/1', 'avgFrameRate': '30/1', 'timeBase': '1/15360', 'frames': 2227, 'actualProbeExitCode': 0, 'chunk': 'be9648'},
        'notEveryNativeFramePtsApproval': True, 'wholeDecodeRepeated': False,
    },
    'openingProposal': {
        'path': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-proposal-v2.json',
        'koSentences': 4, 'koCharactersWithSpaces': len(' '.join(intro['ko'])),
        'plannedSeconds': [20, 30], 'actualMeasuredSeconds': None,
        'usefulOriginalParagraphsAndPcmPreserved': True,
        'independentMcCreated': False, 'ttsStarted': False,
    },
    'currentPolarReplacementMustFinishFirst': True,
    'newHeavyProducerStarted': False, 'gpuPauseOrResearchProcessChanges': 0,
    'newMediaEncoded': 0, 'baselineModified': False,
    'allFinalPixelsApproved': False, 'currentMixedAudioApproved': False,
    'privateUploadComplete': False, 'gitDelivered': False, 'scheduleChanged': False,
    'humanListeningApproved': False, 'publicRightsApproved': False,
}
target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'scriptProtected': True, 'currentStudioReadOnly': True,
                  'openingDraftSentences': 4, 'completedUiWindows': 6,
                  'nextProductionStarted': False}))
