"""Prepare a separate Unreal worker referencing the user's installed content."""
from pathlib import Path
import json, shutil, subprocess

H = Path(__file__).resolve().parent
B = H.parent
R = B.parents[2]
L = B / 'local/real-clips-v2'
W = L / 'unreal-worker'
SOURCE = R / 'GameAnimationSample'
EXE = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')

def setup():
    batch = json.loads((B / 'batch.json').read_text('utf-8'))
    assert batch['productionAuthorized'] and batch['renderAuthorized']
    assert batch['episodeIds'] == [f'A{i:02}' for i in range(1, 19)]
    (W / 'Content').mkdir(parents=True, exist_ok=True)
    (W / 'Config').mkdir(exist_ok=True)
    template = R / 'projects/animation-assigning/production/local/unreal-kit-v2/unreal-worker'
    descriptor = json.loads((template / 'A01Worker.uproject').read_text('utf-8'))
    descriptor['Description'] = 'Isolated real animation clip revision worker A01-A18'
    (W / 'RealClipsWorker.uproject').write_text(json.dumps(descriptor, indent=2), 'utf-8')
    settings = (template / 'Config/DefaultEngine.ini').read_text('utf-8')
    settings = settings.split('[/Script/AndroidFileServerEditor.')[0]
    (W / 'Config/DefaultEngine.ini').write_text(settings, 'utf-8')
    for folder in (SOURCE / 'Content').iterdir():
        if not folder.is_dir() or folder.name in ('YamyamRealClipsV2', '__ExternalActors__', '__ExternalObjects__'):
            continue
        dst = W / 'Content' / folder.name
        if not dst.exists():
            q = lambda p: "'" + str(p).replace("'", "''") + "'"
            subprocess.run(['powershell', '-NoProfile', '-Command',
                            'New-Item -ItemType Junction -Path ' + q(dst) + ' -Target ' + q(folder) + ' | Out-Null'], check=True)
        assert dst.resolve() == folder.resolve()
    roots = ['Characters', 'FreeAnimationLibrary', 'DeadBodies_Poses_nikoff', 'FreeAnimationSet',
             'FreeAnimationsPack', 'FreeAnimationsPack2', 'FreeSampleAnimationSet', 'MC_Sample']
    (L / 'scan-roots.json').write_text(json.dumps(roots), 'utf-8')
    return W / 'RealClipsWorker.uproject'

if __name__ == '__main__':
    desc = setup()
    with (L / 'inventory-stdout.log').open('wb') as log:
        subprocess.run([EXE, desc, '-run=pythonscript', '-script=' + str(H / 'inspect_assets.py'),
                        '-nullrhi', '-unattended', '-nosound', '-nosplash', '-NoLiveCoding',
                        '-abslog=' + str(L / 'inventory-engine.log')], stdout=log, stderr=log,
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print(L / 'asset-registry.json')
