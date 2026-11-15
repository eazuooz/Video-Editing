"""Record the observed final Kart pilot samples, preserving the source and audio."""
from pathlib import Path
import json, subprocess
import numpy as np
from PIL import Image

H = Path(__file__).resolve().parent
M = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
R = M / 'production-resume-20261115T055255Z'
slug = 'shorts-mariokart8-spin-boost'
B = M / slug / 'film-v10/pilot-encoded-qa-v1'
files = sorted(B.glob('cue-*-375.jpg'))
assert len(files) == 29
ref = np.asarray(Image.open(files[0]).convert('RGB'), dtype=np.float32)[30:100, :345]
checks = []
for p in files:
    pixels = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)[30:100, :345]
    mse = float(np.mean((pixels - ref) ** 2))
    assert mse < 2, (p, mse)
    checks.append(dict(file=p.name, titleHeaderMse=mse))
ref = np.asarray(Image.open(B / 'cue-014-375.jpg').convert('RGB'), dtype=np.float32)[140:510, :345]
body = []
for i in [15, 16, 17, 20, 21, 22, 23]:
    pixels = np.asarray(Image.open(B / f'cue-{i:03}-375.jpg').convert('RGB'), dtype=np.float32)[140:510, :345]
    mse = float(np.mean((pixels - ref) ** 2))
    assert mse < 2, (i, mse)
    body.append(dict(cue=i, bodyMse=mse))
note = R / 'kart-pilot-observed-notes-v63.json'
assert not note.exists()
note.write_text(json.dumps(dict(
    project=slug, actualEncodedSamplesInspected=29,
    allCaptionSamplesOpened=True, sourceOrderAndAspectReviewed=True,
    captionMarginsAndSubjectVisibilityReviewed=True,
    titlePixelChecks=checks, contactArtifactBodyChecks=body,
    findings=[
        'All29 actual375px caption samples were inspected in the four contact sheets, with individual cues022 and017 additionally opened. Repeated title and static diagram pixels were checked against intact samples; the files retain the same complete graphics despite omissions in the displayed repeated-image preview.',
        'The lesson follows the source order: anti-gravity condition, changed meaning of contact, Nintendo spin-turbo rule, eligible objects, then route-choice recap. The generic two-kart comparison is explicitly labelled as an authored explanatory model rather than original speed/input telemetry.',
        'The acquired Mario Kart8 footage remains separate from the simplified comparison. The single cyan-post contact around source227 seconds is used once in the fourth paragraph; the unrelated coin-loss event is excluded. The narration states that only some objects qualify and does not call every wall a boost device.',
        'The condition diagram and captions remain readable with margins. The source remains in its original aspect, and the approved cat appears without hiding the compared karts. No source replay, freeze, speed change, or voice processing was added.'
    ]), ensure_ascii=False, indent=2) + '\n', 'utf8')
res = subprocess.run([
    str(H.parents[2] / 'qwen3-tts/.venv/Scripts/python.exe'), '-u', '-X', 'utf8',
    str(H / 'record-inspected-pilot-v46.py'), '--project', slug, '--notes-file', str(note)
], cwd=H.parents[2])
assert res.returncode == 0
