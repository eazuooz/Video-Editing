"""Display current recognizer words and PCM bins for manual complete-clause review.

Candidate boundaries are proposals, never an automatic approval. Original PCM
is read only and no audio is sliced by this display helper.
"""
from pathlib import Path
import argparse, difflib, hashlib, json, re, wave
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--first', type=int, required=True)
ap.add_argument('--last', type=int, required=True)
ap.add_argument('--compact', action='store_true')
ap.add_argument('--mode', choices=['whole', 'contexts', 'targets'], default='whole')
args = ap.parse_args()
norm = lambda s: re.sub(r'[^가-힣A-Za-z0-9]', '', s).lower()
for path in sorted((BASE / f'current-{args.mode}-asr-v1').glob('[0-9]*.json')):
    index = int(path.name[:2])
    if not args.first <= index <= args.last:
        continue
    row = json.loads(path.read_text('utf-8-sig'))
    source = ROOT / row.get('contextPath', row['sourcePath'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row.get('contextSha256', row['sourceSha256'])
    words = row['words']
    spoken = ''.join(norm(w['text']) for w in words)
    expected = ''.join(norm(s) for s in row['expectedKo'])
    match = difflib.SequenceMatcher(None, expected, spoken, autojunk=False)
    differences = [dict(kind=k, expected=expected[a:b], actual=spoken[c:d])
                   for k, a, b, c, d in match.get_opcodes() if k != 'equal']
    with wave.open(str(source), 'rb') as wav:
        assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) == (24000, 1, 2)
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2')
    positions, pos = [], 0
    for word in words:
        positions.append((pos, pos + len(norm(word['text']))))
        pos = positions[-1][1]
    proposals = []
    for para in range(1, len(row['expectedKo'])):
        point = len(''.join(norm(s) for s in row['expectedKo'][:para]))
        mapping = next(((a, b, c, d) for _, a, b, c, d in match.get_opcodes()
                        if a <= point <= b and b > a), None)
        assert mapping is not None
        a, b, c, d = mapping
        approximate = c + round((point-a)*(d-c)/(b-a))
        word_index = min(range(len(positions)), key=lambda i: abs(positions[i][1]-approximate))
        before, after = words[word_index], words[word_index+1]
        start, end = before['timestamp'][1], after['timestamp'][0]
        assert start is not None and end is not None
        bins = []
        # Include edges and adjacent low-amplitude regions to inspect whether
        # word clocks leave a usable intact sentence boundary.
        for t in np.arange(max(0, start-.04), min(len(samples)/24000, end+.045), .01):
            n = round(t*24000)
            block = samples[max(0, n-120):min(len(samples), n+120)].astype(float)
            bins.append(dict(seconds=round(float(t), 5), sample=n,
                             rms=round(float(np.sqrt(np.mean(block*block))), 3),
                             peak=int(np.max(np.abs(block)))))
        shown = sorted(bins, key=lambda x: x['rms'])[:5] if args.compact else bins
        proposals.append(dict(afterParagraph=para, previousWord=before, nextWord=after,
                              candidateGap=[start, end], displayedPcm10msBins=shown,
                              allCandidateBinsDisplayed=not args.compact))
    print(json.dumps(dict(id=row['id'], expected=row['expectedKo'], actual=row['text'],
                          normalizedDifferences=differences,
                          allWords=[(w['text'].strip(), *w['timestamp']) for w in words] if args.compact else words,
                          boundaryProposals=proposals, automaticApproval=False),
                     ensure_ascii=False, separators=(',', ':')))
