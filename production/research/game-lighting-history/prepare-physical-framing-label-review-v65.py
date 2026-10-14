"""Prepare scoped verification of two repaired scenes; preserve all prior attempts."""
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root / 'production/research/game-lighting-history'
target = base / 'build-physical-framing-label-review-v65.py'
assert not target.exists()
text = (base / 'build-physical-framing-review-pair-v60.py').read_text('utf-8')
changes = {
    'episode04-physical-framing-v59': 'episode04-physical-framing-label-repair-v64',
    'episode04-physical-framing-v60': 'episode04-physical-framing-label-review-v65',
    'physical-framing-review-execution-v60': 'physical-framing-label-review-execution-v65',
    'physical-framing-review-build-v60': 'physical-framing-label-review-build-v65',
    'episode04PhysicalFramingReviewV60': 'episode04PhysicalFramingLabelReviewV65',
    'CPU-physical-framing-source-review-v60': 'CPU-physical-framing-label-review-v65',
    '.physical-framing-v60.tmp': '.physical-framing-label-v65.tmp',
    'N == 5320': 'N == 2314',
    'len(cues) == 28': 'len(cues) == 11',
    'all28': 'all11',
    'Five physical-episode framing source scenes only': 'Two repaired physical-episode framing source scenes only',
    'v59 video copied': 'v64 video copied',
}
for old, new in changes.items():
    assert old in text, old
    text = text.replace(old, new)
old = "assert review['sourceSceneReviewRenderingAllowed']"
text = text.replace(old, old + "\nassert sha(ROOT / plan['pixelRepairReview']['path']) == plan['pixelRepairReview']['sha256']\nassert read(ROOT / plan['pixelRepairReview']['path'])['permittedRepair'] == [s['id'] for s in plan['scenes']]")
text = text.replace("'-movflags', '+faststart', clean]", "'-movie_timescale', '48000', '-movflags', '+faststart', clean]")
text = text.replace("'-movflags', '+faststart', cap]", "'-movie_timescale', '48000', '-movflags', '+faststart', cap]")
text = text.replace('duration,sample_rate,channels:format', 'duration,duration_ts,start_pts,sample_rate,channels:format')
old = "assert abs(float(a['duration']) - N / 60) < 1 / 48000"
text = text.replace(old, old + "\n    assert int(a['duration_ts']) == N * 800 and int(a.get('start_pts', 0)) == 0")
old = "return {'path': rel(file)"
text = text.replace(old, "assert ap[-1]['pts'] + ap[-1]['duration'] == N * 800\n    " + old)
old = "'execution': rel(SP), 'outputs': outputs"
text = text.replace(old, "'execution': rel(SP), 'captionLayout': {'path': rel(OUT / 'caption-layout.json'), 'sha256': sha(OUT / 'caption-layout.json')}, 'outputs': outputs")
target.write_text(text, 'utf-8')
extract = base / 'extract-physical-framing-label-qa-v66.py'
assert not extract.exists()
text = (base / 'extract-physical-framing-qa-v62.py').read_text('utf-8')
changes = {
    'episode04-physical-framing-qa-v62': 'episode04-physical-framing-label-qa-v66',
    'physical-framing-review-build-v61': 'physical-framing-label-review-build-v65',
    'physical-framing-review-execution-v61': 'physical-framing-label-review-execution-v65',
    'episode04PhysicalFramingExtractionV62': 'episode04PhysicalFramingLabelExtractionV66',
    'CPU-physical-framing-local-qa-v62': 'CPU-physical-framing-label-qa-v66',
    '.framing-qa-v62.tmp': '.framing-label-qa-v66.tmp',
    'len(layout[\'cues\'])==28': 'len(layout[\'cues\'])==11',
    'frame<5320': 'frame<2314',
    'all28': 'all11',
    'and5 motion-stage': 'and2 motion-stage',
}
for old, new in changes.items():
    assert old in text, old
    text = text.replace(old, new)
extract.write_text(text, 'utf-8')
print('Prepared v65 pair and v66 scoped extraction; no media or approvals created.')
