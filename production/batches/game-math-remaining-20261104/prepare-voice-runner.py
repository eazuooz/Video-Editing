"""Adapt the previously used paragraph-take renderer to this exact finite math batch."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
source=ROOT/'projects/buckshot-roulette-reverse-engineering/production/render-voice.py'
text=source.read_text(encoding='utf-8')
def replace(old,new):
    global text
    assert text.count(old)==1,(old[:80],text.count(old))
    text=text.replace(old,new)
replace('PROJECT = Path(__file__).resolve().parents[1]\nSLUG = PROJECT.name\nMANIFEST = PROJECT / \'production/tts-manifest.json\'', '''BOOT = argparse.ArgumentParser(add_help=False)
BOOT.add_argument('--project', required=True)
BOOTARGS, _ = BOOT.parse_known_args()
SLUG = BOOTARGS.project
if not __import__('re').fullmatch(r'game-math-[a-z0-9-]+', SLUG):
    raise ValueError('Invalid selected math project')
PROJECT = ROOT / 'projects' / SLUG
MANIFEST = PROJECT / 'production/tts-manifest.json' ''')
replace("    parser = argparse.ArgumentParser(description=__doc__)","    parser = argparse.ArgumentParser(description=__doc__)\n    parser.add_argument('--project', required=True)")
replace("    authorization = read(ROOT / 'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][SLUG]\n    assert authorization['productionAllowedNow'] is True and authorization['projectPath'] == f'projects/{SLUG}'",'''    authorization = read(ROOT / 'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert authorization['productionAllowedNow'] is True and SLUG in authorization['projectSlugs']
    plan = read(PROJECT / 'planning/production-plan.json')
    if args.synthesize:
        assert all(plan.get(k) is True for k in ['sourceFinal','narrationFinal','sceneBindingsFinal']), 'Finish actual source, narration and inspected gameplay binding before synthesis.' ''')
replace("        actual_game = name in ['buckshot roulette.exe', 'buckshot roulette_windows.exe', 'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe']", "        actual_game = '/steamapps/common/' in exe or name in ['overwatch.exe','buckshot roulette.exe','buckshot roulette_windows.exe','monsterhunterwilds.exe','d2r.exe','diablo ii.exe']")
replace("def unity_import_worker(info, process):", '''def shared_capture_idle():
    library = ROOT / 'unity/VideoEditing/Library'
    status = library / 'AnimationGridV1.status.json'
    if not status.is_file() or list(library.glob('*.request')) or list(library.glob('*.request.json')):
        return False
    current = read(status)
    return (current.get('status')=='complete' and current.get('completed')==current.get('frames')
            and current.get('slug')=='animation-exaggeration')

def unity_import_worker(info, process):''')
replace("and '-batchmode' not in parent_args", "and ('-batchmode' not in parent_args or (shared_capture_idle() and Path(value(parent_args,'-projectpath') or '').resolve() == (ROOT/'unity/VideoEditing').resolve()))")
# Idle shared watcher exception is narrowly proved on every invocation. A new
# request or unfinished capture blocks this task; it never stops another job.
needle="        hub = name == 'unity.exe' and exe.endswith('/unity hub/resources/unity.exe') and 'serve' in arguments"
replace(needle,needle+'''
        idle_capture_server = False
        if name == 'unity.exe' and '-projectpath' in arguments and '-batchmode' in arguments:
            i = arguments.index('-projectpath')
            shared = ROOT / 'unity/VideoEditing'
            if i+1 < len(arguments) and Path(arguments[i+1]).resolve() == shared.resolve():
                status = shared / 'Library/AnimationGridV1.status.json'
                pending = list((shared/'Library').glob('*.request')) + list((shared/'Library').glob('*.request.json'))
                if status.is_file() and not pending:
                    current = read(status)
                    idle_capture_server = (current.get('status')=='complete' and current.get('completed')==current.get('frames') and current.get('slug')=='animation-exaggeration')
        if idle_capture_server and args.allow_idle_editors:
            gui_allow.add(name)
''')
replace("'editor-background-render' if editor and batch_flags and not import_worker", "'editor-background-render' if editor and batch_flags and not import_worker and not idle_capture_server")
text=text.replace('selected Buckshot documentary only','explicit M21–M33 local review batch')
text=text.replace('Buckshot\'s selected, paragraph-level own-voice render.', 'Finite M21–M33 batch paragraph-level approved-voice renderer.')
text=text.replace('Root coordinator must explicitly pass --synthesize after capture/render GPU work\nhas finished.', 'Root passes --project and --synthesize after source/script/footage review and resource checks.')
target=BATCH/'render-voice.py'
text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
target.write_text(text,encoding='utf-8')
compile(text,str(target),'exec')
print('Prepared batch-scoped paragraph renderer; no synthesis or GPU allocation.')
