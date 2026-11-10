"""Capture the isolated Unreal studies on the CPU-only Direct3D WARP adapter."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess

from plan_observations import BATCH, ROOT, load, save
from pose_studies import WORK


ENGINE = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
TEMPLATE = BATCH.parent / 'local/contrast-v5/a08-cumulative/unreal-worker'
BUILDER = BATCH.parent / 'native/build_level.py'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(local, project, label, args):
    engine_log = local / f'{label}.engine.log'
    with (local / f'{label}.log').open('wb') as stream:
        subprocess.run([str(ENGINE), str(project), *map(str, args), '-unattended', '-nosound', '-nosplash',
                        '-NoLiveCoding', '-NoScreenMessages', '-NoLoadingScreen', '-notexturestreaming',
                        '-NoShaderWorker', '-abslog=' + str(engine_log)],
                       stdout=stream, stderr=subprocess.STDOUT, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    return engine_log


def inspect_study(local, key, digest):
    log = local / f'capture-{key}.engine.log'
    text = log.read_text(encoding='utf8', errors='replace') if log.exists() else ''
    adapter_id = re.search(r'Chosen D3D12 Adapter Id = (\d+)', text)
    assert adapter_id and 'D3D10Warp Version:' in text
    adapter = next(line.strip() for line in text.splitlines()
                   if f'Found D3D12 adapter {adapter_id[1]}: Microsoft Basic Render Driver' in line)
    definition = load(local / f'{key}-build.json')
    files = sorted((local / 'frames' / key).glob('*.png'))
    assert len(files) == definition['frames'], (key, len(files))
    return {'sourceDefinitionSha256': digest, 'adapter': adapter,
            'frames': len(files), 'sampleHashes': {str(i): sha(files[i]) for i in (0, 48, 88, 179)},
            'level': definition['level'], 'sequence': definition['sequence']}


def capture(ep):
    scope = load(ROOT / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert scope['renderAuthorized'] and ep.split('-')[0] in scope['episodes']
    local = WORK / ep
    job = load(local / 'study-job.json')
    worker = local / 'unreal-worker'
    for folder in ('Content', 'Config'):
        (worker / folder).mkdir(parents=True, exist_ok=True)
    project = worker / f'{ep}Review.uproject'
    shutil.copyfile(TEMPLATE / 'A08ContrastV5.uproject', project)
    shutil.copyfile(TEMPLATE / 'Config/DefaultEngine.ini', worker / 'Config/DefaultEngine.ini')
    for source in (ROOT / 'GameAnimationSample/Content').iterdir():
        if not source.is_dir() or source.name == 'YamyamAnimationSeries':
            continue
        destination = worker / 'Content' / source.name
        if not destination.exists():
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            subprocess.run(['powershell', '-NoProfile', '-Command',
                            f'New-Item -ItemType Junction -Path {quote(destination)} -Target {quote(source)} | Out-Null'],
                           check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        assert destination.resolve() == source.resolve()
    definitions = {key: sha(local / 'poses' / f'{key}.json') for key in job['keys']}
    receipt_path = local / 'capture-receipt.json'
    old = load(receipt_path) if receipt_path.exists() else {}
    save(worker / 'build-job.json', job)
    if old.get('definitions') == definitions and all(len(list((local/'frames'/k).glob('*.png'))) == 180 for k in definitions):
        print(ep, 'matching WARP captures reused', flush=True)
        return
    build_input = local / 'build-input.json'
    if not build_input.exists() or load(build_input) != definitions:
        print(ep, 'building editable tracks and levels without an RHI', flush=True)
        run(local, project, 'build', ['-run=pythonscript', '-script=' + str(BUILDER), '-nullrhi'])
        save(build_input, definitions)
    receipts = old.get('studies', {})
    for key, digest in definitions.items():
        definition = load(local / f'{key}-build.json')
        input_stamp = local / f'capture-{key}-input.json'
        if input_stamp.exists() and load(input_stamp)['definitionSha256'] == digest:
            try:
                receipts[key] = inspect_study(local, key, digest)
                print(ep, key, 'matching WARP capture reused', flush=True)
                continue
            except (AssertionError, StopIteration):
                pass
        save(input_stamp, {'definitionSha256': digest})
        print(ep, key, 'capturing via software WARP', flush=True)
        run(local, project, f'capture-{key}', [definition['level'], '-game',
                  '-LevelSequence=' + definition['sequence'], '-MoviePipelineConfig=' + definition['config'],
                  '-d3d12', '-warp', '-AllowSoftwareRendering', '-RenderOffscreen', '-resx=1920', '-resy=1080',
                  '-ExecCmds=r.DynamicGlobalIlluminationMethod 0,r.ReflectionMethod 0,r.Shadow.Virtual.Enable 0'])
        receipts[key] = inspect_study(local, key, digest)
    save(receipt_path, {'episode': ep, 'engine': 'UE 5.8', 'definitions': definitions,
                        'studies': receipts, 'captureResolution': [1920, 1080], 'captureFps': 60})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episodes', nargs='+', choices=('A08', 'A11', 'A08-motion'))
    for episode in parser.parse_args().episodes:
        capture(episode)
