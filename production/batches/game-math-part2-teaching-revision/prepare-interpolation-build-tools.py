"""Scope proven production helpers to the interpolation revision.

Quaternion helpers, media and their review receipts are never overwritten.
Generated tools retain exact ratio/audio/caption/stale-file guards.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def replacement(text,old,new):
    assert old in text,old
    return text.replace(old,new)
plan=(B/'plan-episodes.py').read_text(encoding='utf8')
for old,new in [
 ("O=ROOT/'shared/output/game-math-part2-teaching-revision'","O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'"),
 ('quaternion-episode-flow-audit.json','interpolation-episode-flow-audit.json'),
 ("flow['all26OriginalScenesAnd155KoLinesExact']","flow['allOriginalSceneDictionariesExact'] and flow['originalOrderAndContractExact']"),
 ('game-math-quaternion-operations','game-math-rotation-interpolation'),
 ('quaternion-measured-episode-plan.json','interpolation-measured-episode-plan.json'),
 ("read(B/'baselines/game-math-rotation-interpolation/lesson.json')['scenes'][int(ident)-1]['ko']","{s['id']:s for s in read(B/'baselines/game-math-rotation-interpolation/lesson.json')['scenes']}[ident]['ko']"),
 ("source_id=='_dw9jjRpanA'","source_id=='TPkvx2W8CV8'"),
 ("scene['sourceId']=='_dw9jjRpanA'","scene['sourceId']=='TPkvx2W8CV8'")]:plan=replacement(plan,old,new)
(B/'plan-interpolation-episodes.py').write_text(plan,encoding='utf8')
timing=(B/'prepare-revision-timing.py').read_text(encoding='utf8')
start=timing.index("for version,name in [")
end=timing.index(":\n",start)
timing=timing[:start]+"for version,name in [('v2','interpolation-addition-tts-map.json')]"+timing[end:]
timing=timing.replace('game-math-quaternion-teaching-additions-','game-math-interpolation-teaching-additions-').replace("O=ROOT/'shared/output/game-math-part2-teaching-revision'","O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'").replace('quaternion-merged-alignment-progress.json','interpolation-alignment-progress.json')
timing=timing.replace("O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'", "O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation';O.mkdir(parents=True,exist_ok=True)")
(B/'prepare-interpolation-timing.py').write_text(timing,encoding='utf8')
editor=(B/'prepare-editor.py').read_text(encoding='utf8').replace("choices=['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']","choices=['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']")
(B/'prepare-interpolation-editor.py').write_text(editor,encoding='utf8')
build=(B/'build-episodes.py').read_text(encoding='utf8').replace("choices=['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']","choices=['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']").replace("O=ROOT/'shared/output/game-math-part2-teaching-revision'","O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'").replace('game-math-quaternion-operations','game-math-rotation-interpolation').replace('create-game-overlay.py','create-interpolation-overlay.py').replace('quaternion-annotation-tracks.json','interpolation-annotation-tracks.json')
build=build.replace("kind='bridges' if ident.startswith('B') else 'supplements'","kind='interpolation_additions'").replace("kind='bridges' if ident.startswith('B') else 'supplements'","kind='interpolation_additions'")
# A single independent additions module renders each measured scene separately.
(B/'build-interpolation-episodes.py').write_text(build,encoding='utf8')
print('Scoped interpolation plan/alignment/editor/build helpers generated; render sources and actual tracks still required.')
