"""Finite audio paths and authorization for the selected Interior Mapping revision."""
from pathlib import Path
import json
import re
import unicodedata

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
REVISION = 'portal-camera-guides-v3'
L = P / 'production/local/audio-v1'
VOICE = L / 'voice/narration.wav'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def normalize_speech(text, aliases):
    for display, speech in sorted(aliases.items(), key=lambda item: -len(item[0])):
        text = re.sub(re.escape(display), lambda match: speech, text, flags=re.I)
    # Mathematical signs are semantic data. Do not turn −1 and +1 into the same
    # comparison token while reconciling Whisper's numeric writing with speech.
    text = re.sub(r'[−-]\s*(?=\d)', '마이너스', text)
    text = re.sub(r'\+\s*(?=\d)', '플러스', text)
    return re.sub(r'[^0-9a-z가-힣]', '', unicodedata.normalize('NFC', text).lower())


def guard():
    control=read(R/'shared/publishing/video-production-control.json')
    auth=control.get('portalTraversalShortsAuthorization',{})
    project=read(P/'project.json')
    if (auth.get('id')!='portal-traversal-two-shorts-20261025' or auth.get('status')!='active'
        or P.name not in auth.get('slugs',[]) or not auth.get('fullProductionAuthorized')
        or project.get('currentRevision')!=REVISION):
        raise RuntimeError('Finite five-Short authorization changed; preserve work.')
    plan=read(P/'planning/production-plan.json')
    if not plan.get('independentFootageViewed') or not plan.get('scriptFinalized'):
        raise RuntimeError('Review selected footage and narration before media generation.')
    return control
