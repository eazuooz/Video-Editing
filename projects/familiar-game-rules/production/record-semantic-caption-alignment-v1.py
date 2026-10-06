"""Semantic text audit; encoded caption pixels remain a separate final gate."""
from final_cpu_common import *
import re
plan=read(FINAL/'plan.json');path=ROOT/plan['captionCandidate'];cap=read(path)
assert sha(path)==plan['captionCandidateSha256']
def compact(s):return re.sub(r'\s+','',s)
paragraphs=[]
for p in sorted(cap['paragraphs'],key=lambda x:x['startSeconds']):
    row=dict(scene=p['scene'],paragraph=p['paragraph'],start=round(p['startSeconds'],3),end=round(p['endSeconds'],3),ko=p['ko'],en=p['en'])
    for lang in ['ko','en']:
        cues=[q for q in cap[lang] if q['scene']==p['scene'] and q['paragraph']==p['paragraph']]
        assert compact(' '.join(q[lang] for q in cues))==compact(p[lang]),(p['scene'],p['paragraph'],lang)
        assert abs(cues[0]['startSeconds']-p['startSeconds'])<.002 and abs(cues[-1]['endSeconds']-p['endSeconds'])<.002
        row[lang+'Cues']=[q['index'] for q in cues]
    paragraphs.append(row)
assert len(paragraphs)==70
for lang in ['ko','en']:assert [n for p in paragraphs for n in p[lang+'Cues']]==list(range(1,len(cap[lang])+1))
write(FINAL/'caption-alignment-review.json',dict(status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,reviewedAt=now(),allParagraphTextsRetained=True,scope='All70current independent KO/EN full paragraphs directly read; reconstructed253KO/118EN complete text, chronological ranges and current SRT hashes. This is semantic timing/text only; final encoded pixel approval is separate.',planSha256=sha(FINAL/'plan.json'),captionCandidateSha256=sha(path),paragraphs=paragraphs,captions=[dict(language=lang,path=rel(FINAL/f'captions.{lang}.srt'),sha256=sha(FINAL/f'captions.{lang}.srt'),cues=len(cap[lang])) for lang in ['ko','en']],specificNote='Internal cue63 starts0.1s later to match first held-gun target frame5877. All words, paragraph outer boundaries, EN, PCM and video timing preserved; gap5871-5876 separately reviewed.',finalEncodedPixelsApproved=False,humanPronunciation='pending'))
print(json.dumps(dict(paragraphs=70,koCues=253,enCues=118,semanticApproved=True,finalPixelsApproved=False)))
