"""Map independent KO/EN text onto preserved PCM placements for pixel review.

Recognizer text is only timing evidence. Cue text always comes from the current
reviewed scripts, including uncertain recognizer words. This is not caption QA.
"""
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib, json, re, bisect, math, sys
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(WORK / 'plan.json')
assert not (WORK / 'caption-tracks-v1.json').exists(), 'Preserve prior caption candidate.'
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
norm = lambda t: ''.join(c.lower() for c in t if c.isalnum())
ko_rows, en_rows, reviews, overlap_reviews = [], [], [], []
single_line_contexts = {(s['id'],p['paragraph']) for s in plan['scenes'] if any(c['classification']=='actual-existing-game' for c in s['segments']) for p in s['speechEvidence']} # Fixed lower captions: narrow single-line trials on gameplay.
force_single_line = False

def source_to_output(s, t, ending=False):
    sample = min(s['samples'], max(0, round(t * s['sampleRate'])))
    pieces = [p for p in s['pcmPlacement'] if p['kind'] == 'preserved-current-PCM']
    for p in (pieces if ending else reversed(pieces)):
        if p['fromSample'] <= sample <= p['toSample']:
            return s['startFrame'] / 60 + (p['outputFromSample'] + sample - p['fromSample']) / s['sampleRate']
    raise AssertionError(f'Unmapped sample {s["id"]}:{sample}')

def wrap(text):
    if font.getlength(text) <= 650:
        return [text]
    if force_single_line:
        return None
    words = text.split(' ')
    choices = []
    for k in range(1, len(words)):
        lines = [' '.join(words[:k]), ' '.join(words[k:])]
        widths = [font.getlength(t) for t in lines]
        if max(widths) <= 650:
            choices.append((abs(widths[0] - widths[1]), lines))
    return min(choices, key=lambda x: x[0])[1] if choices else None

def cue_chunks(text):
    # Explicit script spaces and punctuation are preserved; split at word ends.
    tokens = list(re.finditer(r'\S+', text))
    chunks, first = [], 0
    while first < len(tokens):
        best = first
        for k in range(first + 1, len(tokens) + 1):
            t = text[tokens[first].start():tokens[k - 1].end()]
            if not wrap(t):
                break
            best = k
            if re.search(r'[.!?]$', t):
                break
        assert best > first, 'A single script token needs editorial splitting.'
        a, z = tokens[first].start(), tokens[best - 1].end()
        chunks.append((a, z, text[a:z], wrap(text[a:z])))
        first = best
    return chunks

for s in plan['scenes']:
    evidence = ROOT / s['asrEvidence']['path']
    assert sha(evidence) == s['asrEvidence']['sha256']
    asr = read(evidence)
    words = asr['words']
    for p in s['speechEvidence']:
        force_single_line = (s['id'],p['paragraph']) in single_line_contexts
        script = p['ko']
        script_norm = norm(script)
        time_chars, recognized = [], ''
        for w in words:
            a, z = w['timestamp']
            if a is None or z is None or z <= a:
                continue
            if not p['speechStart'] - .06 <= (a + z) / 2 <= p['speechEnd'] + .06:
                continue
            n = norm(w['text'])
            for k, c in enumerate(n):
                recognized += c
                time_chars.append((a + (z - a) * k / len(n), a + (z - a) * (k + 1) / len(n)))
        matcher = SequenceMatcher(None, script_norm, recognized, autojunk=False)
        mapped = {}
        for a, b, n in matcher.get_matching_blocks():
            for k in range(n):
                mapped[a + k] = time_chars[b + k]
        assert matcher.ratio() >= .78, f'Timing evidence needs direct inspection {s["id"]}p{p["paragraph"]}: {matcher.ratio():.3f}'
        keys = sorted(mapped)
        # Unmatched recognizer characters retain literal reviewed script text.
        # Interpolation stays between neighboring time anchors; every cue remains
        # flagged for direct timing/pixel review.
        for k in range(len(script_norm)):
            if k in mapped:
                continue
            before = [v for v in keys if v < k]
            after = [v for v in keys if v > k]
            lo = before[-1] if before else -1
            hi = after[0] if after else len(script_norm)
            ta = mapped[lo][1] if lo >= 0 else p['speechStart']
            tz = mapped[hi][0] if hi < len(script_norm) else p['speechEnd']
            ta, tz = min(ta, tz), max(ta, tz)
            unit = (tz - ta) / (hi - lo - 1)
            mapped[k] = (ta + (k - lo - 1) * unit, ta + (k - lo) * unit)
        chunks = cue_chunks(script)
        cue_start = len(ko_rows)
        for a, z, text, lines in chunks:
            na, nz = len(norm(script[:a])), len(norm(script[:z]))
            speech_a, speech_z = mapped[na][0], mapped[nz - 1][1]
            speech_a = max(p['speechStart'], speech_a)
            speech_z = min(p['speechEnd'], max(speech_a + .04, speech_z))
            start = source_to_output(s, speech_a)
            end = source_to_output(s, speech_z, ending=True)
            assert end > start
            ko_rows.append({'index': len(ko_rows) + 1, 'scene': s['id'], 'paragraph': p['paragraph'],
                            'ko': text, 'lines': lines, 'startSeconds': start, 'endSeconds': end,
                            'sourceSpeechFromSeconds': speech_a, 'sourceSpeechToSeconds': speech_z,
                            'textSource': 'current-independent-reviewed-script', 'asrCharacterMatch': matcher.ratio(),
                            'timingApproved': False, 'pixelsApproved': False})
        assert norm(' '.join(c['ko'] for c in ko_rows[cue_start:])) == script_norm
        reviews.append({'scene': s['id'], 'paragraph': p['paragraph'], 'koMatch': matcher.ratio(),
                        'scriptCharacters': len(script_norm), 'recognizerCharacters': len(recognized),
                        'unmatchedScriptCharacters': len(script_norm) - sum(x.size for x in matcher.get_matching_blocks()),
                        'recognizerTextCopiedAsCaption': False, 'directFinalTimingReview': False})
        sentence_pattern = r'.+?(?:[.?](?=\s|$)|(?<!Die)!(?=\s|$)|$)'
        ko_sentences = list(re.finditer(sentence_pattern, script))
        en_sentences = list(re.finditer(sentence_pattern, p['en']))
        if (s['id'],p['paragraph']) in [('03',2),('04',4),('12',3)]:
            # Independent English uses a colon for the Korean setup sentence.
            # Split the literal first clause, preserving every character; this
            # is semantic correspondence, never an automatic script rewrite.
            first = en_sentences[0].group()
            en_sentences = list(re.finditer(r'^.+?:|(?<=:)\s*.+$', first)) + en_sentences[1:]
            reviews[-1]['englishClauseCorrespondence'] = 'Literal English colon follows the Korean setup sentence; following fields/question and conclusion keep their independent original wording.'
        assert len(ko_sentences) == len(en_sentences), f'Independent sentence correspondence requires review: {s["id"]}p{p["paragraph"]}'
        for ks, es in zip(ko_sentences, en_sentences):
            en_text = es.group().strip()
            tokens = en_text.split()
            spans = []
            current = []
            for token in tokens:
                if current and len(' '.join(current + [token])) > 84:
                    spans.append(' '.join(current));current = []
                current.append(token)
            if current:
                spans.append(' '.join(current))
            a = len(norm(script[:ks.start()]))
            z = len(norm(script[:ks.end()]))
            ta, tz = mapped[a][0], mapped[z - 1][1]
            weights = [len(t) for t in spans];total = sum(weights);cursor = ta
            for text, weight in zip(spans, weights):
                stop = cursor + (tz - ta) * weight / total
                start, end = source_to_output(s, cursor), source_to_output(s, stop, ending=True)
                assert end > start
                en_rows.append({'index': len(en_rows) + 1, 'scene': s['id'], 'paragraph': p['paragraph'],
                                'en': text, 'startSeconds': start, 'endSeconds': end,
                                'meaningAndTimingApproved': False, 'textSource': 'independent-reviewed-English-script'})
                cursor = stop

boundary_corrections = []

for rows in [ko_rows, en_rows]:
    for a, z in zip(rows, rows[1:]):
        if a['endSeconds'] > z['startSeconds']:
            assert a['endSeconds'] - z['startSeconds'] < .4, f'ASR cue anchors overlap materially: {a} / {z}'
            boundary = (a['endSeconds'] + z['startSeconds']) / 2
            overlap_reviews.append({'language': 'ko' if rows is ko_rows else 'en', 'scene': a['scene'],
                                    'previousCue': a['index'], 'nextCue': z['index'],
                                    'recognizerOverlapSeconds': a['endSeconds'] - z['startSeconds'],
                                    'candidateSharedBoundary': boundary,
                                    'method': 'Midpoint of overlapping recognizer timestamps; literal text preserved. This is a candidate requiring direct final timing inspection.',
                                    'directTimingApproved': False})
            a['endSeconds'] = z['startSeconds'] = boundary

def timestamp(t):
    n = round(t * 1000)
    return f'{n // 3600000:02}:{n // 60000 % 60:02}:{n // 1000 % 60:02},{n % 1000:03}'

def write_srt(rows, lang):
    text = '\n\n'.join(f'{r["index"]}\n{timestamp(r["startSeconds"])} --> {timestamp(r["endSeconds"])}\n' +
                       ('\n'.join(r['lines']) if lang == 'ko' else r['en']) for r in rows) + '\n'
    (WORK / f'captions.{lang}.candidate.srt').write_text(text, encoding='utf-8')

write_srt(ko_rows, 'ko');write_srt(en_rows, 'en')
(WORK / 'caption-tracks-v1.json').write_text(json.dumps({
    'schemaVersion': 1, 'createdAt': datetime.now(timezone.utc).isoformat(),
    'planSha256': sha(WORK / 'plan.json'), 'status': 'literal-script-caption-candidates-all-final-cue-pixels-pending',
    'style': 'boxed-white-forest-v1', 'centerPx': [960, 970], 'koRows': ko_rows, 'enRows': en_rows,
    'paragraphTimingEvidence': reviews, 'all52ParagraphsIncluded': len(reviews) == 52,
    'recognizerAnchorOverlapCandidates': overlap_reviews,
    'actualPcmBoundaryCorrections': boundary_corrections,
    'everyCurrentScriptCharacterPreserved': True, 'allTimingApproved': False, 'allPixelsApproved': False,
    'humanWholeListening': 'pending', 'humanPronunciationApproval': 'pending',
    'targetedSingleLineContexts': [list(x) for x in sorted(single_line_contexts)],
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'koCues': len(ko_rows), 'enCues': len(en_rows), 'paragraphs': len(reviews),
                  'minCharacterMatch': min(r['koMatch'] for r in reviews), 'allFinalPixelsApproved': False}))
