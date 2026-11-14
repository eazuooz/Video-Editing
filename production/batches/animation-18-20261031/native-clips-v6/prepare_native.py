"""Prepare an isolated worker and exact installed native animation candidates."""
import hashlib
import shutil
import subprocess

from prepare import BATCH, HERE, ROOT, WORK, read, save


def main():
    selected = read(ROOT / 'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
    assert selected['renderAuthorized'] and selected['excludedUploaded'] == ['A01', 'A02']
    catalog = read(BATCH / 'real-clips-v2/source-motion-catalog.json')
    names = ['AS_ComboHands', 'AS_Spear_Attack_01', 'AS_Spear_Attack_02', 'AS_Spear_Attack_04',
             'AS_LevitatingFireballCharge2', 'am_Stand_React_Excited_01',
             'am_Stand_Emotion_Frustrated_01_GrabHead', 'am_Ready_Fight_01_Knockdown_A',
             'af_Ready_Fight_01_Knockdown_B', 'am_Stand_Wave_02_LHand',
             'A_Flashlight_Idle_01_R', 'anim_GrabValve_R', 'anim_OpeningValve_R',
             'MM_Walk_Fwd', 'MM_Run_Fwd', 'am_Stand_Idle_03_LookAround']
    clips = [dict(row, yaws=[-70, -25]) for row in catalog if row['id'] in names]
    assert len(clips) == len(names)
    base = next(row for row in catalog if row['id'] == 'am_Stand_Idle_03_LookAround')
    clips.append(dict(id='am_SitPiano_Play_01', clip='/Game/MC_Sample/Animations/Piano/am_SitPiano_Play_01',
                      mesh=base['mesh'], yaws=[-70, -25]))
    for row in clips:
        asset = ROOT / 'GameAnimationSample/Content' / (row['clip'].removeprefix('/Game/') + '.uasset')
        assert asset.is_file(), asset
        with asset.open('rb') as stream:
            row['vendorSourceSha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    save(HERE / 'native-candidates.json', {'clips': clips,
         'constraint': 'Direct native playback. Final topic adoption requires moving audition and narration match.'})
    worker = WORK / 'unreal-worker'
    for folder in ('Content', 'Config'):
        (worker / folder).mkdir(parents=True, exist_ok=True)
    template = ROOT / 'projects/animation-assigning/production/local/unreal-kit-v2/unreal-worker'
    shutil.copyfile(template / 'A01Worker.uproject', worker / 'NativeClipsV6.uproject')
    shutil.copyfile(template / 'Config/DefaultEngine.ini', worker / 'Config/DefaultEngine.ini')
    for source in (ROOT / 'GameAnimationSample/Content').iterdir():
        if not source.is_dir() or source.name in ('YamyamNativeClipsV6', '__ExternalActors__', '__ExternalObjects__'):
            continue
        destination = worker / 'Content' / source.name
        if not destination.exists():
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            command = 'New-Item -ItemType Junction -Path ' + quote(destination) + ' -Target ' + quote(source) + ' | Out-Null'
            subprocess.run(['powershell', '-NoProfile', '-Command', command], check=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        assert destination.resolve() == source.resolve()
    save(worker / 'native-job.json', {'work': str(WORK), 'clips': clips})
    engine = 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
    with (WORK / 'build.log').open('wb') as stream:
        subprocess.run([engine, str(worker / 'NativeClipsV6.uproject'), '-run=pythonscript',
                        '-script=' + str(HERE / 'build_native.py'), '-nullrhi', '-unattended',
                        '-nosound', '-nosplash', '-NoLiveCoding', '-NoShaderWorker',
                        '-abslog=' + str(WORK / 'build.engine.log')],
                       stdout=stream, stderr=subprocess.STDOUT, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)


if __name__ == '__main__':
    main()
