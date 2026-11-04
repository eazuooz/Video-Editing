import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
C = HERE / 'candidates'

def source(key):
    video = C / (key + '.mp4')
    info = json.loads((C / (key + '.info.json')).read_text(encoding='utf-8'))
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height,r_frame_rate', '-of', 'json', str(video)], text=True))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert v['width'] >= 1920 and v['height'] >= 1080
    return {
        'key': key, 'sourceUrl': info['webpage_url'], 'videoId': info['id'],
        'title': info['title'], 'recordingPublisher': info['channel'],
        'recordingPublisherUrl': info.get('channel_url'), 'published': info.get('upload_date'),
        'mediaPath': str(video).replace('\\', '/'),
        'mediaSha256': hashlib.sha256(video.read_bytes()).hexdigest(),
        'metadataPath': str(C / (key + '.info.json')).replace('\\', '/'),
        'decodedProbe': probe, 'sourceFormat': info.get('format_id'),
        'sourceLicenseField': info.get('license'),
        'fullAudioListened': False, 'sourceAudioPreserved': True,
        'finalAudioRightsAndMixApproved': False, 'productionCutListApproved': False,
        'researchMediaMayBeCommitted': False
    }

tekken_grid = source('tekken8-kazuya-movelist')
tekken_grid.update({
    'game': 'TEKKEN 8', 'genre': '3D fighting', 'nintendo': False,
    'sourceClassification': 'independent-gameplay-candidate',
    'captureKind': 'In-game move-list demonstration in native red-grid training environment; third-party recording.',
    'rank': 'Best visual-fit candidate for the opening, subject to recording reuse basis.',
    'referenceSections': ['A02-S01', 'A02-S02'],
    'observedWindows': [
        {
            'sourceSeconds': [167.0, 169.9], 'timingPrecision': '8fps sampled review; final cut boundaries need source-rate verification.',
            'displayedMove': 'Roundhouse Triple Spin Kick', 'moveNameBasis': 'English in-game move-list UI visible in this recording.',
            'before': 'Kazuya and a grey training opponent face each other in guard; move-list entry is selected.',
            'action': 'Kazuya lifts into a kick, rotates through low sweeping kicks and a final extended turning kick; torso and raised/lowered legs change direction through the sequence.',
            'result': 'The opponent is launched and falls; Kazuya returns toward guard.',
            'teachingUse': 'Show whole motion first, identify torso/leg direction through selected poses, then return to native-speed motion before our amplitude illustration.',
            'claimLimit': 'This proves the visible sequence, not anatomical impossibility, joint angles, original animation intent, or the exact Tekken 7 move shown in the lesson.',
            'sceneBinding': 'A02 scene01. It can introduce the small-view readability question in scene02, but cannot prove a same-clip amplitude A/B.',
            'screenIssues': 'Native top UI and lower-left controls remain. Preserve aspect and both feet; actual fixed-caption clearance must be tested. Exclude black move-selection transitions around166.7 and170.5.',
            'motionIssues': 'Source camera follows distance and opponent launch. No fixed-camera measurement or editorial slowdown.',
            'annotations': 'Short torso-to-leg direction guides attached to visible clothing/body edges; no invented skeleton, angle measurement or detected confidence.'
        }
    ],
    'reviewEvidence': ['candidates/tekken8-movelist-survey-01.jpg', 'candidates/tekken8-movelist-survey-02.jpg', 'candidates/tekken8-movelist-survey-03.jpg', 'candidates/tekken8-movelist-166-170.jpg', 'candidates/tekken8-movelist-168-177-01.jpg', 'candidates/tekken8-movelist-168-177-02.jpg', 'candidates/tekken8-movelist-168-177-03.jpg'],
    'reviewMethod': 'Full-duration 6-second survey plus 8fps detailed samples166–177s, visually inspected. Not continuous audio listening or every-frame QA.',
    'rights': {
        'publisherPolicyUrl': 'https://www.bandainamcoent.co.jp/english/videopolicy/',
        'publisherPolicyScope': 'Policy describes individuals sharing videos of themselves playing; platform monetization permitted under conditions, third-party rights separate.',
        'recordingReusePermissionVerified': False,
        'recordingLicense': 'No reusable license or express permission found in supplied metadata/description and targeted public search.',
        'editorialUseAssessment': 'Short excerpts directly analyzed by our independent narration are a conditional editorial candidate, not a confirmed license.',
        'preferredResolution': 'Verify a recording reuse basis or reproduce the same move in a legitimately owned game capture; no message to the recorder sent.',
        'creditPlacement': 'Description bottom; any source-specific extra requirement must be honored or the source replaced.'
    }
})

tekken_official = source('tekken8-kazuya-official')
tekken_official.update({
    'game': 'TEKKEN 8', 'genre': '3D fighting', 'nintendo': False,
    'sourceClassification': 'independent-gameplay-promotional-candidate',
    'captureKind': 'Publisher gameplay trailer, full-screen combat portion.',
    'rank': 'Secondary visual candidate; background, coat, impact effects and camera weaken clean torso analysis.',
    'referenceSections': ['A02-S01'],
    'officialProvenance': 'https://tekken.com/media',
    'observedWindows': [{
        'sourceSeconds': [38.0, 39.5],
        'before': 'Kazuya and Jin face each other in close guard.',
        'action': 'Kazuya drops into a sweeping strike, rotates, then follows with an extended kick.',
        'result': 'Jin is launched, struck again and falls while Kazuya settles toward guard.',
        'claimLimit': 'Visible whole-body direction only. Coat obscures waist and effects obscure contacts; do not label exact body-joint angles or current build frame data.',
        'screenIssues': 'Busy neon background and camera framing; native grid absent. The following cut needs annotation reset.'
    }],
    'reviewEvidence': ['candidates/tekken8-kazuya-contact.jpg', 'candidates/tekken8-kazuya-detail-01.jpg', 'candidates/tekken8-kazuya-detail-02.jpg', 'candidates/tekken8-kazuya-detail-03.jpg', 'candidates/tekken8-kazuya-38-39p5.jpg'],
    'reviewMethod': 'Full-duration 3-second survey;4fps details34–46s and20fps38–39.5s. Not continuous audio listening.',
    'rights': {
        'publisherPolicyUrl': 'https://www.bandainamcoent.co.jp/english/videopolicy/',
        'recordingPublisherVerified': True,
        'confirmedReusableLicense': False,
        'editorialUseAssessment': 'Conditional short publisher-footage excerpt with original analytical commentary. General policy covers own gameplay and does not by itself prove a broad trailer-reuse license.',
        'audio': 'Music and voice have not been audited; preserve source track in research, final mix decision pending.'
    }
})

vf = source('vf5revo-lau-official')
vf.update({
    'game': 'Virtua Fighter 5 R.E.V.O.', 'genre': '3D fighting', 'nintendo': False,
    'sourceClassification': 'independent-gameplay-promotional-candidate',
    'captureKind': 'Official character guide contains separately assessable full-screen gameplay18–43s, followed by guide text and inset gameplay.',
    'rank': 'Useful S04 continuation candidate retaining Lau and an independently observed modern same-series example.',
    'referenceSections': ['A02-S04'],
    'officialProvenance': 'https://virtua-fighter.com/revo/en/guide/',
    'officialLinkEvidence': 'The official guide page links the Lau Chan thumbnail directly to youtube.com/embed/N2W1hzi6kks.',
    'observedWindows': [
        {'sourceSeconds': [30.5, 31.65], 'before': 'Lau faces the crouching/recovering opponent.', 'action': 'Lau lifts into a turning kick, brings the striking leg around, then continues into another kick.', 'result': 'The opponent recoils while Lau lowers the leg and returns toward stance.', 'teachingUse': 'Whole motion with clear changes in chest, hip and leg direction. An analytical freeze is explanation time and must reconnect to this real moving sequence.'},
        {'sourceSeconds': [32.0, 35.6], 'before': 'Lau faces the opponent at close range.', 'action': 'Lau lowers his body into a forward strike, drives the opponent upward, then follows with kicks and punches while feet and torso turn.', 'result': 'The opponent lands and Lau regains a guarded posture.', 'teachingUse': 'Confirmation of coordinated upper/lower-body changes in a second game; not a demonstration of the exact historical VF pose in the source.'}
    ],
    'equivalenceAndDifferences': 'Retains the source role of a separate established fighting-game example and the character Lau. This is a modern VF5 R.E.V.O. capture, not the original historical recording or proof of identical skeletal constraints.',
    'screenIssues': 'Use only the actual gameplay target being discussed. Do not copy guide narration, instructional text, comparison diagrams or authored lesson framing. Gameplay after about48s is inset with existing English explanations and is not preferred. The proposed30–38s interval has native camera cuts and needs annotation resets.',
    'gridSuitability': 'No native grid. Preserve real stage background; do not remove character edges merely to force a grid. Our adjacent Unity explanation supplies the shared controlled grid.',
    'reviewEvidence': ['candidates/vf5revo-lau-survey-01.jpg', 'candidates/vf5revo-lau-survey-02.jpg', 'candidates/vf5revo-lau-survey-03.jpg', 'candidates/vf5revo-lau-survey-04.jpg', 'candidates/vf5revo-lau-30-38-01.jpg', 'candidates/vf5revo-lau-30-38-02.jpg'],
    'reviewMethod': 'Full-duration2-second survey and8fps30–38s details visually inspected; not complete original-audio listening or source-frame timing QA.',
    'rights': {
        'publisherPolicyUrl': 'https://www.sega.co.jp/streaming_guideline/',
        'publisherPolicyCheckedRevision': '2026-10-19',
        'englishPolicyUrl': 'https://support.sega.com/hc/en-us/articles/44194402112529-STREAMING-GUIDELINES',
        'recordingPublisherVerified': True,
        'confirmedReusableLicense': False,
        'editorialUseAssessment': 'Conditional publisher-footage use with our original commentary; no ownership transfer or unconditional license claimed.',
        'conditions': ['Check title-specific rules before final adoption.', 'Add original commentary and keep edits faithful to the game.', 'Platform monetization is a conditional exception, not general commercial licensing.', 'Third-party music/other rights remain separate.', 'No copied guide instruction or standalone extracted assets.'],
        'audio': 'Source track present; actual listening, music/voice identification and final mix remain pending.'
    }
})

report = {
    'schemaVersion': 1, 'episode': 'A02',
    'checkedAtKst': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
    'status': 'reviewed-candidates-not-final-source-binding',
    'scope': 'Independent footage candidate research only; no TTS, GPU, Unity, final cut, upload, or platform mutation.',
    'sources': [tekken_grid, tekken_official, vf],
    'nintendoCandidateRecord': 'production/batches/animation-18-20261031/research/A02/nintendo-footage-candidates.json',
    'gameSetProposal': {
        'status': 'provisional-not-adopted',
        'games': ['TEKKEN 8', 'Virtua Fighter 5 R.E.V.O.', "Kirby's Adventure"],
        'roles': ['Opening pronounced rotation and readable action in native move-list grid.', 'Separate-game confirmation of upper/lower-body opposition in continuous motion.', '2D expansion overshoot followed by smaller settled Needle shape.'],
        'nintendoIfAllAdopted': {'numerator': 1, 'denominator': 3, 'targetNearestInteger': 1},
        'genreMix': ['3D fighting', '2D platform action'],
        'countReason': 'Three distinct teaching roles from the source, not a quota. Tekken and VF are the same broad genre; Kirby provides the actual genre change. If one role is fulfilled differently, recount meaningfully taught games rather than padding a third game.',
        'priorSeriesEpisodeChecked': 'A01 current source pool: New VF Project, Smash Ultimate, Untitled Goose Game. Prefer new recorded moves; new title alone is not a genre change.',
        'previousCompletedGameDesignAudit': 'Parent final scene plan must verify the immediately preceding completed episode; this candidate pass only compared the current A01 pool.'
    },
    'controlledIllustrationsStillRequired': [
        'S02 same clip at large/small presentation, then fixed camera/time with only amplitude changed.',
        'S03 fixed shoulder pivot versus permitted shoulder translation using our editable rig.',
        'S04 our conservative versus expressive pose change, without pretending the commercial game was modified.',
        'S05 own0→100cm versus0→110→100cm overshoot, with numbers labelled illustrative.'
    ],
    'excludedOrDeferred': [
        {'url': 'https://www.youtube.com/watch?v=KkGmeofGSw0', 'reason': 'Native grid is attractive, but A01 already uses it; sampled33–37.75s has reaction/effect/camera emphasis. Do not automatically reuse it as A02 torso-distortion proof. No A01 files changed.'},
        {'url': 'https://wavu.wiki/t/File:T8-p2-kazuya-b%2B4.mp4', 'reason': 'File page reports640×360 and no higher resolution. Exclude as production footage. Page license also explicitly excludes game recordings from its general CC0 text license.'},
        {'url': 'https://www.youtube.com/watch?v=zNBKzLzDKtM', 'reason': 'Original selected lesson: research-reference-only; no clip, character extraction, slide, text or audio may enter production.'},
        {'reason': 'Unrelated intros, logos, portrait title cards, guide slides and long quiet stance intervals are not padding for the60:40 contract.'}
    ],
    'remainingBeforeNarrationLock': [
        'Resolve conditional recording reuse basis for selected footage without inventing license permission.',
        'Finish Kirby exact Needle expansion/settling observation and Nintendo official attribution.',
        'Verify final source-rate in/out and native-speed meaning, original game UI and fixed-caption clearance.',
        'Inspect source audio and necessary sound-effect/music rights.',
        'Bind each narrated claim to the actual source window or explicitly labelled own illustration.',
        'Measure useful actual/explanation duration after source binding; no loops, slowdown or unrelated footage to fill60:40.'
    ]
}
(HERE / 'footage-candidates.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'reviewedCandidates': len(report['sources']), 'decodedFhd': True, 'allStillCandidates': True, 'path': str(HERE / 'footage-candidates.json')}, ensure_ascii=False))
