"""Retain directly reviewed literal73-paragraph captions; final mixed/pixel QA is separate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()


def save(p, value):
    temp = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(temp, p)
            return
        except OSError:
            if attempt == 59:
                raise
            time.sleep(.15)


target = W / 'caption-alignment-review.json'
assert not target.exists(), 'Read the current sealed semantic map rather than repeating it.'
plan = read(W / 'plan.json')
clock = read(W / 'caption-clock-adoption.json')
captions = read(ROOT / clock['sourceCaptionCandidate'])
assert sha(ROOT / clock['sourceCaptionCandidate']) == clock['sourceCaptionSha256']
assert captions['allLiteralKoEnParagraphsPreserved'] and len(captions['paragraphs']) == 73
assert len(captions['ko']) == 400 and len(captions['en']) == 148
review = read(ROOT / plan['selectedInputReview'])
assert sha(ROOT / plan['selectedInputReview']) == plan['selectedInputReviewSha256']
assert review['allBoardsDirectlyRead'] and not review['unresolvedDefects']
scenes = {scene['id']: scene for scene in plan['scenes']}
normal = lambda text: re.sub(r'\s+', '', text)
paragraphs = []
for paragraph in captions['paragraphs']:
    original = scenes[paragraph['scene']]['paragraphs'][paragraph['paragraph'] - 1]
    tracks = {lang: [row for row in captions[lang] if row['scene'] == paragraph['scene'] and row['paragraph'] == paragraph['paragraph']]
              for lang in ['ko', 'en']}
    for lang in ['ko', 'en']:
        assert normal(''.join(row[lang] for row in tracks[lang])) == normal(paragraph[lang]) == normal(original[lang])
        assert abs(tracks[lang][0]['startSeconds'] - paragraph['startSeconds']) < .001
        assert abs(tracks[lang][-1]['endSeconds'] - paragraph['endSeconds']) < .001
    paragraphs.append(dict(scene=paragraph['scene'], paragraph=paragraph['paragraph'], start=round(paragraph['startSeconds'], 3),
                           end=round(paragraph['endSeconds'], 3), ko=paragraph['ko'], en=paragraph['en'],
                           koCues=[row['index'] for row in tracks['ko']], enCues=[row['index'] for row in tracks['en']],
                           allParagraphTextsRetained=True))
for lang in ['ko', 'en']:
    assert [index for paragraph in paragraphs for index in paragraph[lang + 'Cues']] == list(range(1, len(captions[lang]) + 1))
alignment = dict(schemaVersion=1, slug='similar-game-design', createdAt=now(), status='approved-semantic-paragraph-alignment',
                 approved=True, manualSemanticReview=True, allParagraphTextsRetained=True, paragraphs=paragraphs,
                 captions=[dict(language=lang, path=rel(W / f'captions.{lang}.srt'), sha256=sha(W / f'captions.{lang}.srt'), cues=len(captions[lang]))
                           for lang in ['ko', 'en']], currentLiteralCaptionSourceSha256=clock['sourceCaptionSha256'],
                 currentPlanSha256=sha(W / 'plan.json'), inputPixelsReview=plan['selectedInputReview'],
                 scope='Complete literal73 KOEN paragraph and cue coverage retained from direct input/text review; final encoded pixels and current mixed ASR approval remain separate.',
                 finalMixedAsrApproved=False, allFinalPixels=False, collected=False, uploaded=False)
save(target, alignment)
manifest_path = BASE.parent / 'project.json'
manifest = read(manifest_path)
manifest['paths'].update(captionAlignmentReview=rel(target), captionsKo=rel(W / 'captions.ko.srt'), captionsEn=rel(W / 'captions.en.srt'),
                          measuredPublishingPreparation=rel(BASE.parent / 'publishing/prepared-publishing-v1.json'))
manifest['updatedAt'] = now()
save(manifest_path, manifest)
print(json.dumps(dict(semanticParagraphs=73, ko=400, en=148, allFinalPixels=False, finalMixedAsrApproved=False)))
