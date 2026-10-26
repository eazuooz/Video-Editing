"""Read-only scope/resource check for the four explicitly selected Shorts.

This does not start a queue, voice model, renderer, server or any platform action.
"""
from pathlib import Path
import argparse
import json
import sys

R = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
AUTH = 'explicit-cuphead-teardown-splatoon-20261026'

def read(path): return json.loads(Path(path).read_text(encoding='utf8'))

def check(slug, require_ready=False):
    batch = read(B / 'batch.json')
    control = read(R / 'shared/publishing/video-production-control.json')
    permit = control.get('finiteBatchAuthorizations', {}).get(batch['id'], {})
    assert batch['authorization']['id'] == AUTH
    assert permit.get('id') == AUTH and permit.get('localProductionAuthorized') is True
    chosen = [x for x in batch['projects'] if x['slug'] == slug]
    assert len(chosen) == 1, 'Outside the explicit four-item selection.'
    project = read(R / 'projects' / slug / 'project.json')
    assert project['slug'] == slug
    assert project['currentRevision'] == chosen[0]['revision']
    auth = project['authorization']
    assert auth.get('fullProductionAuthorized') is True
    assert auth.get('id') == AUTH
    if require_ready:
        plan = read(R / 'projects' / slug / 'planning/production-plan.json')
        assert plan.get('scriptFinalized') is True, 'Finalize narration only after matching footage is actually viewed.'
        assert plan.get('independentFootageViewed') is True
    media = Path(batch['mediaRoot']) / slug / 'local'
    local = R / 'projects' / slug / 'production/local'
    assert local.resolve() == media.resolve() and media.is_dir()
    if (R / 'shared/output/GPU_HANDOFF.json').exists():
        raise RuntimeError('Foreign GPU lease exists; preserve it and its job.')
    import psutil
    busy = []
    for process in psutil.process_iter(['name','exe','cmdline']):
        try:
            p = process.info
            name = (p.get('name') or '').casefold()
            executable = (p.get('exe') or '').replace('\\','/').casefold()
            args = p.get('cmdline') or []
            if name == 'unity.exe' and executable == 'c:/program files/unity hub/resources/unity.exe' and len(args) == 2 and args[1].casefold() == 'serve':
                continue
            if name == 'unity.exe' and executable == 'c:/users/1/appdata/local/unity/bin/unity.exe' and len(args) == 2 and args[1] == '--internal-auth-broker-serve':
                parent = process.parent()
                if parent and parent.exe().replace('\\','/').casefold() == 'c:/program files/unity hub/unity hub.exe':
                    continue
            if name in {'overwatch.exe','unity.exe','unrealeditor.exe','d2r.exe','diablo ii.exe','duckov.exe','escapefromduckov.exe','escape from duckov.exe','monsterhunterwilds.exe'}:
                busy.append({'name':p['name'],'pid':process.pid})
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            raise RuntimeError('Cannot verify user game/editor process; no GPU launch.')
    if busy:
        raise RuntimeError('User game/editor active; GPU production waits: '+json.dumps(busy))
    return {'slug':slug,'revision':chosen[0]['revision'],'scope':'verified','games':'none observed','jobsStarted':0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--require-ready',action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(args.slug,args.require_ready),ensure_ascii=False))
