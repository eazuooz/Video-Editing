"""Keep an explicitly requested voice revision separate from the approved baseline."""
from pathlib import Path
import json, os

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/ai-games-showcase-2026'
REVISION = os.environ.get('AI_GAMES_REVISION', '')
assert REVISION in ('', 'elevenlabs-b-v2'), 'Unknown production revision'

def paths():
    if REVISION:
        return (PROJECT / 'production/local/elevenlabs-v2',
                ROOT / 'shared/output/narration/ai-games-showcase-2026/elevenlabs-b-v2',
                PROJECT / 'production/local/elevenlabs-v2/edit-plan.json', 'ai-games-elevenlabs-v2')
    return (PROJECT / 'production/local/compact-edit',
            ROOT / 'shared/output/narration/ai-games-showcase-2026/game-tools-five-second-ppt-v1',
            PROJECT / 'production/edit-plan.json', 'ai-games-compact-v1')

def ensure_authorized():
    control = json.loads((ROOT / 'shared/publishing/video-production-control.json').read_text(encoding='utf8'))
    if not REVISION:
        assert control['selectedVideo'] == PROJECT.name
        return
    record = json.loads((PROJECT / 'production/elevenlabs-revision-v2.json').read_text(encoding='utf8'))
    assert record['revision'] == REVISION and record['fullRevisionAuthorized'] is True
    assert record['scope'] == 'ai-games-showcase-2026 only through Drive final review'
    assert not control['automaticNextVideoEnabled'] and not control['automaticBatchResumeEnabled']
    # Another chat's active selection/GPU lease is not ours to overwrite.
    # This request is separately bounded by the human's explicit revision authorization.
