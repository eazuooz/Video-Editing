"""Single metadata read for each newly discovered official source, local only."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
META = V / 'source-research-v1'
PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
SOURCES = [
    dict(game='Manor Lords', videoId='gVkhhrLARU8', expectedChannel='Hooded Horse'),
    dict(game='Timberborn', videoId='Jsc7003gSu0', expectedChannel='Timberborn'),
    dict(game='Against the Storm', videoId='qaK2FWQB7DE', expectedChannel='Eremite Games')]
META.mkdir(exist_ok=True)
assert not (META / 'metadata-observation-v1.json').exists(), 'Continue the recorded source metadata'
records = []
for source in SOURCES:
    sid = source['videoId']
    output = META / (sid + '.info.json')
    assert not output.exists(), 'Do not refetch a completed source metadata read'
    command = [str(PYTHON), '-X', 'utf8', '-m', 'yt_dlp', '--dump-single-json', '--skip-download',
        '--no-playlist', '--js-runtimes', 'node:' + NODE, 'https://www.youtube.com/watch?v=' + sid]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    (META / (sid + '.metadata.log.txt')).write_text(result.stderr, 'utf-8')
    if result.returncode:
        records.append(dict(**source, actualMetadataExitCode=result.returncode, success=False))
        continue
    info = json.loads(result.stdout)
    output.write_text(result.stdout, 'utf-8')
    assert info['id'] == sid and info.get('channel') == source['expectedChannel'], (sid, info.get('channel'))
    records.append(dict(**source, success=True, actualMetadataExitCode=0,
        title=info['title'], channel=info.get('channel'), channelId=info.get('channel_id'),
        uploadDate=info.get('upload_date'), duration=info.get('duration'), license=info.get('license'),
        chapters=info.get('chapters'), sourceAudioAdoptionAllowed=False, actionSelectionApproved=False))
(META / 'metadata-observation-v1.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    sources=records, phase='metadata only; no media acquired; no new narration; no action approval'),
    ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(records, ensure_ascii=False))
