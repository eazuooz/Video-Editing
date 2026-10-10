import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
LOCAL = ROOT / 'shared/output/character-parameters/preflight'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def record(path):
    p = ROOT / path
    return {'path': path, 'sha256': sha(p), 'bytes': p.stat().st_size}

def save(name, data):
    p = PROOF / name
    if p.exists():
        if name == 'source-research-direct-review-v1.json':
            old = json.loads(p.read_text(encoding='utf-8'))
            if old['researchTranscript'] == data['researchTranscript'] and old['pageAX'] == data['pageAX']:
                return
        raise RuntimeError(f'Preserve existing proof: {p}')
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now = datetime.now(timezone.utc).isoformat()
inventory_path = 'production/batches/sakurai-planning-game-design/preflight/character-parameters.json'
inventory = json.loads((ROOT / inventory_path).read_text(encoding='utf-8-sig'))
changed = [r['path'] for r in inventory['inputFiles'] if sha(ROOT / r['path']) != r['sha256']]
if changed:
    raise RuntimeError(f'Inventory changed; read changed complete contents before refreshing: {changed}')

pairs = {
    'player-customization': ('script/narration.ko.v3.json', 'script/narration.en.v2.json', 'Selection, preview/testing and appearance expression; character ability design is not the central question.'),
    'jump-physics': ('script/narration.ko.json', None, 'Integration, jump timing and air control across games; one movement system rather than a roster of strategically distinct roles.'),
    'counting-animation-frames': ('production/final-v3/script.ko.json', 'production/final-v3/script.en.json', 'Animation and hit clocks, startup/active/recovery and hitstop measurement; not shaping character identity through asymmetric roles.'),
    'deconstruct-analyze-rebuild': ('production/final-v2/script.ko.json', 'production/final-v2/script.en.json', 'Observing and testing one variable before recombination; not character-specific strengths, weaknesses and interactions.'),
    'game-writing': ('script/final-v1.ko.json', 'script/final-v1.en.json', 'Knowledge ownership, possession and branching story state; fictional personalities do not replace performance identity.'),
    'familiar-game-rules': ('script/narration.ko.json', 'script/narration.en.json', 'Input conventions, remapping and devices; not differentiated character rule sets.'),
    'one-button-game-design': ('script/narration.ko.json', 'script/narration.en.json', 'Timing, repetition, reaction and held input on one button; not a roster and its matchups.'),
    'game-reward-planning': ('script/narration.ko.json', 'script/narration.en.json', 'Reward function, prerequisites, caps and production scope; not designer-created role asymmetry.'),
    'making-game-sequels': ('script/narration.ko.json', 'script/narration.en.json', 'Preserved core activities and new decisions in a sequel; character roster identity is a different design question.'),
    'similar-game-design': ('script/narration.current.ko.json', 'script/narration.current.en.json', 'Why choose another game in a genre, space, purpose, atmosphere and cooperation; distinguish from roles within the same game.'),
    'praise-player': ('production/final-v2/script.ko.json', 'production/final-v2/script.en.json', 'Success feedback timing, cause, intensity and truthful display; not ability differentiation.'),
    'presenting-game-scores': ('production/revision-balatro60-v2/script/narration-v2.ko.json', 'production/revision-balatro60-v2/script/narration-v2.en.json', 'Score naming, unit, contribution, hand versus accumulated totals and comparison; not distributing strengths and limitations among characters.'),
    'picking-sides': ('script/narration.ko.json', 'script/narration.en.json', 'Spectator recognition, reason to care and readable risk/result; explicitly separate visual recognition from gameplay role differentiation.'),
    'responsive-game-feedback': ('production/final-v2/script.ko.json', 'production/final-v2/script.en.json', 'Acknowledgement, refusal, selected state, processing and actual completion; traits in menus are incidental observations, not design of distinct abilities.'),
}
reviewed = []
for slug, (ko, en, difference) in pairs.items():
    paths = [f'projects/{slug}/{ko}'] + ([f'projects/{slug}/{en}'] if en else [])
    reviewed.append({'slug': slug, 'reviewScope': 'complete current KO/EN scene paragraphs directly read; KO only where EN is absent', 'files': [record(p) for p in paths], 'difference': difference})
for lang in ['ko', 'en']:
    reviewed[-3]['currentOnsetRepair'] = reviewed[-3].get('currentOnsetRepair', []) + [record(f'projects/presenting-game-scores/production/revision-balatro60-v2/script/onset-repair-v3.{lang}.json')]

source_file = 'shared/output/character-parameters/preflight/source-zwiS1L6QVY0-ja-research-v1.txt'
save('source-research-direct-review-v1.json', {
    'schemaVersion': 1, 'observedAt': now, 'sourceVideoId': 'zwiS1L6QVY0',
    'url': 'https://www.youtube.com/watch?v=zwiS1L6QVY0',
    'channelObserved': 'Masahiro Sakurai on Creating Games / @sora_sakurai_en',
    'durationObserved': '3:36', 'pagePausedAtObserved': '0:04',
    'fullDescriptionDirectlyRead': True, 'fullExportedJapaneseAutoTranscriptDirectlyRead': True,
    'researchTranscript': record(source_file),
    'pageAX': record('shared/output/character-parameters/preflight/source-zwiS1L6QVY0-page-v1.ax.txt'),
    'concepts': ['Deliberate strengths and limitations rather than tiny uniform variation', 'Avoid unusable abilities and retain a meaningful role', 'Distinguish playable roles from enemy behavior', 'Enemy placement and combinations can give a simple rule tactical meaning', 'Describe gameplay identity concisely; special rules also impose implementation cost', 'Repair harmful extremes without flattening every difference'],
    'uncertainties': ['Autogenerated JA corrupts some DLC names and mechanism words; do not adopt those exact details without independent official verification'],
    'wholeContinuousSourceVideoWatched': False, 'allSourcePixelsReviewed': False,
    'sourceFootageOrAudioAdopted': False, 'translationCopyAsNewNarration': False,
    'researchTranscriptGitAllowed': False,
})

metadata = json.loads((LOCAL / 'studio-current-read-metadata-v1.json').read_text(encoding='utf-8'))
save('content-studio-direct-review-v1.json', {
    'schemaVersion': 1, 'reviewedAt': now, 'slug': 'character-parameters',
    'inventory': {'report': record(inventory_path), 'projects': len(inventory['existingProjects']), 'inputs': len(inventory['inputFiles']), 'inputsDigest': inventory['inputsDigest'], 'allInputHashesCurrentlyMatch': True},
    'broadReviewScope': 'All existing project concepts, titles, viewer questions and chapter scope were compared; full paragraphs were directly read for the related projects listed below. This is not a claim that every unrelated project full KO/EN script was read.',
    'relatedCompleteScriptReviews': reviewed,
    'missingInputs': [{'path': 'projects/jump-physics/script/narration.en.json', 'exists': False, 'claimedRead': False}],
    'candidateViewerQuestion': '캐릭터가 이름과 외형을 넘어 플레이 방식으로 기억되려면, 강점·약점과 고유 규칙을 어떻게 설계해야 할까요?',
    'candidateIndependentChapterClaims': ['A baseline defines common play possibilities', 'A strength must change a useful decision and a limitation should preserve a role', 'A rule or resource interaction can differentiate a character beyond stat scaling', 'An enemy has meaning through its placement and combinations', 'Balance checks remove unusable or dominant extremes while preserving a concise role'],
    'actualStudioReadMetadata': record('shared/output/character-parameters/preflight/studio-current-read-metadata-v1.json'),
    'actualStudioRecords': [{'videoId': r['videoId'], 'slug': r['slug'], 'url': r['url'], 'ax': record(r.get('axFile', f"shared/output/character-parameters/preflight/studio-{r['slug']}-v1.ax.txt")), 'status': r['status']} for r in metadata['records']],
    'channelSearch': {'characterTitle': record('shared/output/character-parameters/preflight/studio-character-title-search-v1.ax.txt'), 'characterMatches': ['QnrKPMXAR54', 'W1s_Om_5FU4'], 'bothCompleteDescriptionsRead': True, 'difference': 'Animation research and sequencer operation, not gameplay strengths and weaknesses', 'statTitle': record('shared/output/character-parameters/preflight/studio-stat-title-search-v1.ax.txt'), 'statTitleNoMatchObserved': True, 'emptySearchAloneEstablishesDistinct': False},
    'verdict': 'distinct',
    'reason': 'The complete source research concerns deliberately distinct character performance, special rules and enemy context. Full related KO/EN scripts and current Studio metadata cover selection/appearance, movement physics, frame measurement, feedback, scoring, spectator recognition and inter-game appeal. The candidate instead addresses designer-created role asymmetry within a game, useful counterplay and preserving identity while correcting extremes. This decision relies on content comparison, not IDs or empty exactMatches.',
    'platformWrites': 0, 'newProjectOrNarrationCreated': False, 'newTTSOrMCOrAdoptedFootage': False,
    'nextGate': 'Run distinct with this evidence and current --check, then inspect official footage before dependent narration.',
})
print(json.dumps({'saved': ['source-research-direct-review-v1.json', 'content-studio-direct-review-v1.json'], 'digest': inventory['inputsDigest'], 'relatedProjects': len(reviewed)}, ensure_ascii=False))
