from pathlib import Path
P=Path(__file__).parent
def adapt(t):
 return t.replace("BASE/'final-v1'", "BASE/'revision-balatro60-v2/final-v3'").replace('19052','19988').replace('18452','19388').replace('18451','19387').replace('18512','19448').replace('18752','19688').replace('18992','19928').replace('19051','19987')
clock=adapt((P/'prepare-current-pair-caption-clock-v1.py').read_text('utf-8')).replace('(168,68)','(175,70)').replace('koCueCount=168','koCueCount=175').replace('enCueCount=68','enCueCount=70').replace('ko=168,en=68','ko=175,en=70')
dest=P/'prepare-revision-current-caption-clock-v3.py';assert not dest.exists();dest.write_text(clock,'utf-8')
t=adapt((P/'extract-encoded-caption-qa-v1.py').read_text('utf-8'))
t=t.replace("shared/output/presenting-game-scores/final-encoded-caption-qa-v1", "shared/output/presenting-game-scores/revision-balatro60-v2/final-encoded-caption-qa-v3")
t=t.replace('(168,68,19988)','(175,70,19988)').replace('len(segments)==26','len(segments)==33').replace('len(cues)==168','len(cues)==175').replace('range(1,169)','range(1,176)')
t=t.replace("assert len(preflight['samples'])==651", "assert len(preflight['samples'])>0 and preflight['allSamplePtsVerified']")
t=t.replace('1137,1138','1401,1402').replace('koCueCount=168','koCueCount=175').replace('enCueCount=68','enCueCount=70')
t=t.replace('cutCount=24','cutCount=31').replace('actualCutCount=12','actualCutCount=18').replace('explanationCutCount=12','explanationCutCount=13')
t=t.replace('completeClauseOnsets=40','completeClauseOnsets=42').replace('pcmPlacements=30',"pcmPlacements=len(plan['voicePlacements'])")
t=t.replace('all651ApprovedInputAnchorsRetained','allCurrentApprovedInputAnchorsRetained').replace('koCues=168,cuts=24,clauses=40','koCues=175,cuts=31,clauses=42')
dest=P/'extract-revision-encoded-caption-qa-v3.py';assert not dest.exists();dest.write_text(t,'utf-8')
print('Prepared current full-video clock and guarded final-pixel extraction only.')
