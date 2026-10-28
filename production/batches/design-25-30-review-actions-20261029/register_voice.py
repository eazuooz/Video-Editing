"""Bind a real browser download to one authorized, immutable clarity-v3 take."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil

R = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('slug', choices=['limited-color-world', 'kind-to-beginners'])
ap.add_argument('download')
ap.add_argument('--text', required=True)
ap.add_argument('--credits-before', type=int, required=True)
ap.add_argument('--credits-after', type=int, required=True)
a = ap.parse_args()
auth = json.loads((H/'authorization.json').read_text('utf-8-sig'))
assert a.slug in [x['slug'] for x in auth['revisions']]
control = json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
assert control['finiteBatchAuthorizations'][H.name]['status'].startswith('active')
src = Path(a.download).resolve()
assert src.is_relative_to(Path('C:/Users/1/Downloads')) and src.is_file()
script = (R/a.text).resolve()
assert script.is_relative_to(R/'projects'/a.slug) and script.is_file()
physical = Path('C:/Users/1/.codex/video-production')/H.name/a.slug/'clarity-v3'
logical = R/'projects'/a.slug/'production/local/clarity-v3'
assert logical.resolve() == physical.resolve()
dest = logical/'voice/elevenlabs-sample-b-take-01.mp3'
assert not dest.exists(), 'Preserve prior take'
dest.parent.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(src, dest)
assert sha(src) == sha(dest)
record = dict(createdAt=datetime.now(timezone.utc).isoformat(), provider='ElevenLabs',
    approvedSample='B', voiceId='jIRSnF8OWAsWEChVwCuK', model='Eleven v4',
    settings=dict(stability=.5, similarity=.75, speed=1, audioTags=False),
    format='MP3 44.1kHz 192kbps', script=dict(path=script.relative_to(R).as_posix(),
    sha256=sha(script), submittedTextSha256=hashlib.sha256(script.read_text('utf8').strip().encode()).hexdigest(),
    submittedCharacters=len(script.read_text('utf8').strip())),
    source=dict(path=dest.relative_to(R).as_posix(), sha256=sha(dest), bytes=dest.stat().st_size),
    browserDownload=str(src), uiVoiceAndModelVerified=True,
    creditsBefore=a.credits_before, creditsAfter=a.credits_after,
    creditsConsumed=a.credits_before-a.credits_after, planChanged=False, purchasePerformed=False,
    humanListening='pending', technicalVerification='pending', oldTakesPreserved=True)
for path in [dest.parent/'voice-generation.json', R/'projects'/a.slug/'production/clarity-v3/voice-generation-record.json']:
    assert not path.exists(), 'Preserve generation receipt'
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
(dest.parent/'raw-inputs.json').write_text(json.dumps(dict(sources=[record['source']], joinSilenceSeconds=.2), indent=2)+'\n', 'utf8')
print(json.dumps(record, ensure_ascii=False))
