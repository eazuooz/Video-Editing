"""Record the direct60-paragraph bilingual comparison; final pixel approval stays separate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
normal = lambda text: re.sub(r'\s', '', text)
tracks = read(W / 'caption-tracks.json')
ko_path = ROOT / 'projects/making-game-sequels/script/narration.ko.json'
en_path = ROOT / 'projects/making-game-sequels/script/narration.en.json'
ko = read(ko_path)
en = {scene['id']: scene for scene in read(en_path)['scenes']}
paragraphs = []
for scene in ko['scenes']:
    for number, text in enumerate(scene['lines'], 1):
        rows_ko = [row for row in tracks['koRows'] if row['scene'] == scene['id'] and row['paragraph'] == number]
        rows_en = [row for row in tracks['enRows'] if row['scene'] == scene['id'] and row['paragraph'] == number]
        english = en[scene['id']]['lines'][number - 1]
        assert normal(' '.join(row['ko'] for row in rows_ko)) == normal(text)
        assert normal(' '.join(row['en'] for row in rows_en)) == normal(english)
        assert abs(rows_ko[0]['startSeconds'] - rows_en[0]['startSeconds']) < .002
        assert abs(rows_ko[-1]['endSeconds'] - rows_en[-1]['endSeconds']) < .002
        paragraphs.append(dict(scene=scene['id'], paragraph=number, ko=text, en=english,
            koCues=[row['index'] for row in rows_ko], enCues=[row['index'] for row in rows_en],
            start=round(rows_ko[0]['startSeconds'], 3), end=round(rows_ko[-1]['endSeconds'], 3),
            bothCompleteLiteralTextsDirectlyCompared=True, matchingMeaningOrderAndEvidenceLimits=True))
assert len(paragraphs) == 60
assert [n for row in paragraphs for n in row['koCues']] == list(range(1, 309))
assert [n for row in paragraphs for n in row['enCues']] == list(range(1, 174))
review = dict(schemaVersion=1, reviewedAt=datetime.now(timezone.utc).isoformat(),
    status='approved-semantic-paragraph-alignment', approved=True, manualSemanticReview=True,
    allParagraphTextsRetained=True, allOriginal52ParagraphsPreserved=True, independentNewGuides=8,
    inputScripts=[dict(path=rel(p), sha256=sha(p)) for p in [ko_path, en_path]],
    captions=[dict(language=language, path=rel(W / f'captions.{language}.srt'),
        sha256=sha(W / f'captions.{language}.srt'), cues=count) for language, count in [('ko', 308), ('en', 173)]],
    paragraphs=paragraphs,
    directComparisonNotes=[
        'All60 complete KO/EN paragraph pairs and their current independent cue ranges were directly read; source limitations, separate-shot continuity and hypothetical exercises are retained in both languages.',
        'The overview promises placement/combat observation, retained activity versus new decisions and a personal concept check; the body and conclusion contain each promise.',
        'Knight is the source term in both text tracks; mixed ASR 나이드/나이트 remains human-pronunciation pending rather than a caption transcription change.',
        'Resource changes, sell prompts, preview/blocked placement, card effects and internal production reuse are not upgraded into unobserved rules or developer claims.'
    ],
    finalRenderedPixelsApproved=False, finalPixelReview='pending',
    humanWholeListening='pending', humanPronunciation='pending')
path = W / 'caption-alignment-review.json'
assert not path.exists()
path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(paragraphs=60, koCues=308, enCues=173, semanticReview=True, finalPixelsApproved=False)))
