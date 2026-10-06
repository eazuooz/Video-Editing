"""Honor the user's batch pause before launching another lecture job."""
from pathlib import Path
import json

def require_current_authorization(slug,operation):
    queue=json.loads(Path(__file__).with_name('queue.json').read_text(encoding='utf-8-sig'))
    if not any(item['slug']==slug for item in queue['items']):return
    control=queue.get('executionControl',{})
    if control.get('mode')=='paused' or (control.get('nextVideoMayStart') is False and slug!=control.get('currentVideo')):
        raise SystemExit(f'PART2 {operation} paused by the user to prioritize paper experiments. Preserve checkpoints; resume only after a later user instruction.')
