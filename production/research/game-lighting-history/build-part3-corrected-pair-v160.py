"""Encode the current pair once after the two observed input fixes are reviewed."""
from pathlib import Path
source=Path(__file__).with_name('build-part3-reviewed-pair-v149.py').read_text('utf-8')
source=source.replace('v149','v160').replace('V149','V160')
source=source.replace("part3-annotated-visual-build-v148.json", "part3-annotated-visual-build-v159.json")
gate="""moving=m.read(P/'part3-two-repaired-input-moving-review-v159.json')
assert moving['allTwoCorrectedInputsActuallyPlayedAtRate1'] and moving['observedDefectsResolved']
assert moving['visualBuildSha256']==m.sha(P/'part3-annotated-visual-build-v159.json')
assert len(moving['records'])==2 and all(r['actualMovingPixelsReviewed'] for r in moving['records'])
resources=m.resources();"""
source=source.replace('resources=m.resources();',gate)
assert "'-reinit_filter','0'" in source
exec(compile(source,str(Path(__file__)), 'exec'))
