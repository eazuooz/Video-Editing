"""Current selected-video production authority; this never authorizes publication."""
import json
from pathlib import Path


def require_selected_production():
    root = Path(__file__).resolve().parents[4]
    control = json.loads((root / 'shared/publishing/video-production-control.json').read_text(encoding='utf-8'))
    checkpoint = json.loads((root / 'projects/game-lighting-history-01/production/checkpoint.json').read_text(encoding='utf-8'))
    assert control['selectedVideo'] == 'game-lighting-history-01', 'A different video is selected.'
    assert control['mode'] == 'one-video-autonomous-until-drive-final-review'
    assert control['newProductionAuthorization']['fullProductionAuthorized']
    assert checkpoint['beginnerRevision']['driveFinalReviewAuthorized']
    assert not control['automaticNextVideoEnabled']
    return control
