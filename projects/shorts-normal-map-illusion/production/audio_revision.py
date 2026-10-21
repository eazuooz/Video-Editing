"""Finite audio paths and authorization for the selected Normal Mapping revision."""
from pathlib import Path
import json

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
REVISION = 'normal-map-v2-grid-rgb-deadcells'
L = P / 'production/local/audio-v2'
VOICE = L / 'voice/normal-map-v2.wav'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def guard():
    control = read(R / 'shared/publishing/video-production-control.json')
    selection = control.get('shortsDirectSelection', {})
    project = read(P / 'project.json')
    if (control.get('selectedShortVideo') != P.name
            or selection.get('selectedRevision') != REVISION
            or not selection.get('fullProductionAuthorized')
            or project.get('currentRevision') != REVISION):
        raise RuntimeError('Current selected audio revision changed; preserve outputs.')
    return control
