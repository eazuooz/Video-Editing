"""Review raw number meaning independently of the character timing gate.

This records an ASR-assisted review, never a human listening approval.
Raw transcripts remain unchanged, including the joined Korean pronunciation.
"""
from pathlib import Path
import json, datetime

B = Path(__file__).parent
p = B / 'lines-numeric-v6-unprompted-readback.json'
d = json.loads(p.read_text(encoding='utf8'))
assert not d['suppliedTranscriptPrompt'] and not d['audioModified']
rows = {r['line']: r for r in d['records']}
assert '3을 제곱하면 9' in rows['12-03']['raw']['text']
assert '2의 제곱인 4' in rows['12-03']['raw']['text']
assert '숫자 하나를 더합니다' in rows['19-02']['raw']['text']
assert '음수이라는 수를 곱하겠습니다' in rows['19-02']['raw']['text']
center, half, scale, translation = 5, 2, -2, 1
ends = sorted((scale*(center-half)+translation, scale*(center+half)+translation))
assert center*scale+translation == -9 and abs(scale)*half == 4
assert ends == [-13, -5]
d.update(reviewedAt=datetime.datetime.now().astimezone().isoformat(),
    reviewMethod='Unprompted line-context beam5 ASR compared with unchanged scene-context ASR and authored numerical calculation; no forced numeral correction.',
    semanticChecks={'12-03':'distance3 squared9 exceeds radius2 squared4',
        '19-02':'center5, half2, interval3..7, multiply negative2, finally add number one',
        '19-result':{'center':-9,'halfSize':4,'interval':ends}},
    pronunciationNote='Raw 음수이라는 joins the spoken number 이 with 라는. This is recorded as a Korean spacing/phonetic join; the raw text is preserved. The rewritten final instruction explicitly says 숫자 하나, resolving the rejected earlier +2 readback.',
    earlierRejectedAudio='V5 19-02 independent/whole readback said +2; retained as rejected evidence.',
    humanListeningComplete=False,
    audioQaScope='ASR-assisted numerical meaning and current-hash timing only; whole human listening pending')
for r in d['records']:
    r['meaningReviewed'] = True
    r['humanListeningComplete'] = False
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('V6 numerical meaning reviewed without modifying raw transcripts; human listening pending.')
