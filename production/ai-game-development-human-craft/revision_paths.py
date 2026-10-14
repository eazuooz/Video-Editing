"""Resolve the selected revision's artifacts without overwriting earlier deliveries."""
import json
def workroot(root,slug='ai-game-development-human-craft'):
    manifest=json.loads((root/'projects'/slug/'project.json').read_text(encoding='utf-8-sig'))
    relative=manifest.get('revision',{}).get('workDir',f'shared/output/{slug}')
    path=(root/relative).resolve();path.relative_to((root/'shared/output'/slug).resolve())
    path.mkdir(parents=True,exist_ok=True)
    return path
