"""Seal the directly read 85 bilingual paragraphs against current SRT bytes."""
from pathlib import Path
import importlib.util, re
spec = importlib.util.spec_from_file_location('common', Path(__file__).with_name('review-media-common-v15.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
P = m.ROOT / 'projects/game-lighting-history-04/production'
PP = P / 'part3-final-input-plan-v145.json'
plan = m.read(PP); layout = m.read(P / 'part3-caption-layout-v147.json')
def cues(path):
    rows=[]
    for block in path.read_text('utf-8-sig').strip().split('\n\n'):
        lines=block.splitlines(); clocks=lines[1].split(' --> ')
        def seconds(t):
            h,n,s=re.split('[:,]',t)[:3]; ms=t.rsplit(',',1)[1]
            return int(h)*3600+int(n)*60+int(s)+int(ms)/1000
        rows.append(dict(id=int(lines[0]), start=seconds(clocks[0]), end=seconds(clocks[1]), text=''.join(lines[2:])))
    return rows
tracks={t['language']:cues(m.ROOT/t['path']) for t in layout['tracks']}
compact=lambda s: re.sub(r'\s+', '', s)
paragraphs=[]
for p in sorted(plan['paragraphs'], key=lambda x:min(q['fromFrame'] for q in x['koCues'])):
    ids={lang:[q['id'] for q in p[lang+'Cues']] for lang in ['ko','en']}
    a=tracks['ko'][ids['ko'][0]-1]['start']; b=tracks['ko'][ids['ko'][-1]-1]['end']
    for lang in ['ko','en']:
        selected=[tracks[lang][n-1] for n in ids[lang]]
        assert compact(''.join(q['text'] for q in selected))==compact(p[lang]), p['id']
        assert abs(selected[0]['start']-a)<=.002 and abs(selected[-1]['end']-b)<=.002, p['id']
    paragraphs.append(dict(id=p['id'], start=a, end=b, koCues=ids['ko'], enCues=ids['en'],
        ko=p['ko'], en=p['en'], directlyReadBothFullTexts=True,
        semanticReview='Independent translation retains the paragraph claim, qualification, operation and connection; clause counts may differ.'))
for lang in ['ko','en']:
    assert [n for p in paragraphs for n in p[lang+'Cues']]==list(range(1,len(tracks[lang])+1))
out=dict(reviewedAt=m.stamp(), status='approved-semantic-paragraph-alignment', approved=True,
    manualSemanticReview=True, allParagraphTextsRetained=True, planSha256=m.sha(PP),
    paragraphs=paragraphs, captions=[dict(language=t['language'],path=t['path'],sha256=m.sha(m.ROOT/t['path']),cues=t['cueCount']) for t in layout['tracks']],
    scope='All 85 full KO/EN paragraphs reread directly in this continuation; 1–66 before compaction, 67–85 afterwards. Structural checks only bind those readings to actual SRT bytes.',
    englishWordTimingMeasured=False, allFinalPixelsReviewed=False, qaApproved=False, uploaded=False,
    humanWholeListening='pending', humanPronunciation='pending', newImages=0)
m.save(P/'part3-semantic-caption-review-v155.json',out)
print(m.json.dumps({'directFullPairs':85,'koCues':330,'enCues':386,'semanticApproved':True,'pixelApproved':False}))
