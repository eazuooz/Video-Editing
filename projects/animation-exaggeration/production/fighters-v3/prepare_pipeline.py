"""Isolated revision helpers; never edit the completed v2 pipeline."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;old=H.parent/'fighters-v2'
for name in ['audio_pipeline.py','video_pipeline.py','caption_pipeline.py','storage_paths.py','recognize_additions.py','review_encoded_audio.py','review_frames.py','update_status.py','commit_delivery.py','register_script.py']:
 target=H/name
 if not target.exists():target.write_text((old/name).read_text(encoding='utf-8').replace('fighters-v2','fighters-v3'),encoding='utf-8')
grant=json.loads((old/'execution-grant.json').read_text());grant['revision']='fighters-v3'
(H/'execution-grant.json').write_text(json.dumps(grant,indent=2)+'\n')
print('Scoped v3 helpers prepared')
