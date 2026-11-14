"""Capture one verified vendor clip with the isolated software-rendering worker."""
import argparse
import hashlib
import subprocess

from prepare import ROOT, WORK, read, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key')
    args = parser.parse_args()
    control = read(ROOT / 'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
    assert control['renderAuthorized'] and args.key.replace('_', '').isalnum()
    row = read(WORK / (args.key + '-build.json'))
    assert row['originalSequenceBoundDirectly'] and not row['boneTracksEdited']
    source = ROOT / 'GameAnimationSample/Content' / (row['clip'].removeprefix('/Game/') + '.uasset')
    with source.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['vendorSourceSha256']
    log = WORK / ('capture-' + args.key + '.engine.log')
    frames = WORK / 'frames' / args.key
    receipt = WORK / (args.key + '-capture.json')
    movie = WORK / (args.key + '.mp4')
    if receipt.is_file() and movie.is_file():
        old = read(receipt)
        if old['sourceSha256'] == row['vendorSourceSha256'] and old.get('builderSha256') == row['builderSha256']:
            with movie.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() == old['movieSha256']:
                    print(args.key, 'verified existing capture reused', flush=True)
                    return
    engine = 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
    command = [engine, str(WORK / 'unreal-worker/NativeClipsV6.uproject'), row['level'], '-game',
               '-LevelSequence=' + row['sequence'], '-MoviePipelineConfig=' + row['config'],
               '-d3d12', '-warp', '-AllowSoftwareRendering', '-RenderOffscreen', '-unattended',
               '-nosound', '-nosplash', '-NoLiveCoding', '-NoScreenMessages', '-NoLoadingScreen',
               '-notexturestreaming', '-NoShaderWorker', '-resx=1920', '-resy=1080',
               '-ExecCmds=r.DynamicGlobalIlluminationMethod 0,r.ReflectionMethod 0,r.Shadow.Virtual.Enable 0',
               '-abslog=' + str(log)]
    with (WORK / ('capture-' + args.key + '.log')).open('wb') as stream:
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    text = log.read_text(encoding='utf-8', errors='replace')
    assert 'D3D10Warp Version:' in text and 'Microsoft Basic Render Driver' in text
    pictures = sorted(frames.glob('*.png'))
    assert len(pictures) == row['frames'], (args.key, len(pictures), row['frames'])
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '2', '-framerate', '60',
                    '-start_number', str(int(pictures[0].stem)), '-i', str(frames / '%06d.png'),
                    '-c:v', 'libx264', '-threads', '4', '-preset', 'veryfast', '-crf', '17',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(movie)], check=True)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(movie), '-f', 'null', 'NUL'], check=True)
    with movie.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    save(receipt, {'sourceSha256': row['vendorSourceSha256'], 'sourceClip': row['clip'],
                  'movie': str(movie), 'movieSha256': digest, 'frames': len(pictures),
                  'resolution': [1920, 1080], 'fps': 60, 'renderer': 'UE 5.8 software WARP',
                  'originalSequenceBoundDirectly': True, 'boneTracksEdited': False,
                  'builderSha256': row['builderSha256'],
                  'staging':{k:row.get(k) for k in ('yaws','cameraWidth','cameraHeight','focusOrigin','actorSpacing','sourceStartSeconds','sourceEndSeconds')},
                  'visualReviewPending': True})
    print(args.key, 'native motion capture ready for visual review', flush=True)


if __name__ == '__main__':
    main()
