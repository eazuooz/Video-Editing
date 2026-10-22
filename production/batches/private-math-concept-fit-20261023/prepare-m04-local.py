"""Prepare preservation maps and evidence without starting another costly job."""
from common import *
import shutil
P=R/'projects/game-math-euler-axis-angle';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
authorized('M04');O.mkdir(exist_ok=True)
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst)
save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(src),kind='Original private lesson recovered AAC reused; not original uncompressed PCM',originalMathClipReceipt=rel(P/'production/private-polish-v1/assembly.json'),oldFullMastersPreserved=True))
s=(B/'assemble-m03-audio.py').read_text(encoding='utf8').replace('M03-original','M04').replace('m03-narration-edits.json','m04-narration-edits.json').replace('game-math-orientation-matrices','game-math-euler-axis-angle').replace('the 25 authorized','the 30 authorized').replace('newTtsParagraphs=25','newTtsParagraphs=30').replace('unchangedParagraphs=115','unchangedParagraphs=126').replace('changed=25,unchanged=115','changed=30,unchanged=126')
s=s.replace("{'02':14.,'05':11.,'08':9.,'11':5.}","{'02':11.,'14':6.5,'20':11.}")
(B/'assemble-m04-audio.py').write_text(s,encoding='utf8')
s=(B/'asr-m03.py').read_text(encoding='utf8').replace('M03-original','M04').replace('m03-narration-edits.json','m04-narration-edits.json').replace('game-math-orientation-matrices','game-math-euler-axis-angle')
(B/'asr-m04.py').write_text(s,encoding='utf8')
s=(B/'captions-m03.py').read_text(encoding='utf8').replace('m03-narration-edits.json','m04-narration-edits.json').replace('game-math-orientation-matrices','game-math-euler-axis-angle').replace('sourceParagraphs=140','sourceParagraphs=156')
s='\n'.join(x for x in s.splitlines() if "if sid=='02' and j==2:esent=" not in x)+'\n'
(B/'captions-m04.py').write_text(s,encoding='utf8')
source=R/'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm'
meta=probe(source);v=next(x for x in meta['streams'] if x['codec_type']=='video');assert v['width']>=1920 and v['height']>=1080
save(H/'source-evidence.json',dict(checkedAt=now(),sources=[
 dict(id='dorfromantik-official-trailer',path=rel(source),sha256=sha(source),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioStreams=[x['codec_name'] for x in meta['streams'] if x['codec_type']=='audio'],sourceUrl='https://www.toukana.com/dorfromantik/presskit',rightsUrl='https://steamcommunity.com/games/1455840/announcements/detail/3033708020180412858',rightsObservation='Official FAQ question about showing/using gameplay for content creation answered affirmatively. Directly read in browser2026-10-23. Official presskit explicitly provides Explanation Trailer. Not CC0; use bounded gameplay excerpt with our teaching.',viewedRanges=[dict(start=38,end=56,step=.5,sheets=['sheet-38-01.jpg','sheet-38-02.jpg','sheet-38-03.jpg'],observed='Map static; house tile turns40–41; windmill tile turns50–51; placement follows',candidateFolder='shared/output/private-math-concept-fit-20261023/candidates/dorf-rotation')],selected=[46.5,53],actualAudioListening=False),
 dict(id='YNQ20CKbY8U',sourceUrl='https://www.youtube.com/watch?v=YNQ20CKbY8U',rightsEvidence='Same recording-specific permission verified in M03; commercial/noncommercial transformative use, Nintendo IP separate',observedRanges=[dict(start=280,end=291,meaning='Detach/reorient hook; opening changes; attach'),dict(start=293,end=304,meaning='Translate assembled hook/board onto rail; release')],directFramesViewed=True,priorM03RangesExcluded=[[237.5,246.5],[996,1010]],screenGuides='Editorial contour/point; no inferred measured 3D axes')],humanReview='pending'))
print('Prepared M04:30 changed paragraphs,126 preserved;2 games/3 distinct actions; no TTS started')
