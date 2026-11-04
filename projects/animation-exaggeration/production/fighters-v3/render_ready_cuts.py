from pathlib import Path
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3'
ap.require_authorized('video-cuts');p=ap.read(H/'edit-plan.json')
selected=[c['id'] for c in p['cuts'] if not c.get('unrealCapture')]
vp.render_cuts(p,L/'edit',selected)
