"""Run one authorized episode to the encoded sample check."""

import argparse
from datetime import datetime
import os
import subprocess
import sys
import time

from assemble_planned import HERE, common
from build_review_index import main as build_review_index


ROOT = common.ROOT
VOICE_PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
GPU_BUSY = ('Unregistered GPU activity is present.', 'GPU capacity is insufficient')


def run(*args, env=None):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env, check=True)


def idle_gpu():
    try:
        raw = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=encoder.stats.sessionCount,memory.free,utilization.gpu',
             '--format=csv,noheader,nounits'], cwd=ROOT, text=True, timeout=10)
        encoders, free, utilization = map(int, raw.splitlines()[0].split(','))
    except (OSError, IndexError, ValueError, subprocess.SubprocessError):
        return False
    return encoders == 0 and free >= 8192 and utilization < 15


def render_voice(episode, local, retake=None):
    command = [str(VOICE_PYTHON), '-X', 'utf8', '-u', 'qwen3-tts/render_narration.py',
               '--project', f'design-specifics-{episode[2:]}',
               '--manifest', str(local / 'tts-manifest.json'), '--batch-size', '1']
    if retake:
        command.extend(['--force-scenes', retake])
    env = os.environ | {'OMP_NUM_THREADS': '8', 'MKL_NUM_THREADS': '8'}
    # Wait briefly for a safe opening. The voice renderer's own lease and activity checks still decide.
    for _ in range(24):
        if idle_gpu():
            with subprocess.Popen(command + ['--device', 'cuda:0'], cwd=ROOT, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  encoding='utf-8', errors='replace') as process:
                busy = False
                for line in process.stdout:
                    print(line, end='', flush=True)
                    busy = busy or any(message in line for message in GPU_BUSY)
                result = process.wait()
            if result == 0:
                return
            if not busy:
                raise subprocess.CalledProcessError(result, command)
        time.sleep(2)
    run(*command, '--device', 'cpu', env=env | {'CUDA_VISIBLE_DEVICES': '-1'})


def checkpoint(episode, stage, next_step):
    path = HERE / 'batch.json'
    batch = common.load(path)
    row = next(item for item in batch['episodes'] if item['id'] == episode)
    row.update(stage=stage, status=stage, next=next_step)
    batch['updatedAt'] = datetime.now().astimezone().isoformat()
    common.save(path, batch)
    build_review_index()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', choices=[f'DS{number:02}' for number in range(5, 19)])
    parser.add_argument('--use-rendered-inputs', action='store_true',
                        help='Reuse the voice and studies already rendered for the current plan.')
    parser.add_argument('--retake', help='Replace these comma-separated voice scenes before review.')
    parser.add_argument('--time', type=float, action='append', default=[])
    args = parser.parse_args()
    episode = args.episode
    control = common.load(ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert episode in control['episodes'] and not control['youtubeAuthorized']
    batch = common.load(HERE / 'batch.json')
    prior = next(item for item in batch['episodes'] if item['order'] == int(episode[2:]) - 1)
    assert prior['stage'] == 'local-final-review-ready', f"{prior['id']} still needs its encoded review"
    local = HERE / 'local' / episode
    assert (local / 'tts-manifest.json').is_file(), f'{episode} is missing the voice manifest'
    row = next(item for item in batch['episodes'] if item['id'] == episode)
    assert row['stage'] != 'local-final-review-ready', f'{episode} already has a review'
    captions = [VOICE_PYTHON, '-X', 'utf8', '-u', HERE / 'DS01/readback_captions.py', '--episode', episode]
    run(*captions, '--validate-script')
    if not args.use_rendered_inputs:
        run('node', HERE / 'render_motion.cjs', episode)
    if args.retake or not args.use_rendered_inputs:
        checkpoint(episode, 'tts-in-progress-with-reviewed-footage', 'Generate the selected narration and verify it.')
        render_voice(episode, local, args.retake)
    checkpoint(episode, 'voice-generated-readback-pending', 'Align captions and inspect the final encoded sample.')
    alignment_env = os.environ | {'OMP_NUM_THREADS': '2', 'MKL_NUM_THREADS': '2', 'CUDA_VISIBLE_DEVICES': '-1'}
    run(*captions, env=alignment_env)
    run(sys.executable, '-X', 'utf8', '-u', HERE / 'assemble_planned.py', episode)
    timings = [item for seconds in args.time for item in ('--time', str(seconds))]
    run(sys.executable, '-X', 'utf8', '-u', HERE / 'sample_final_review.py', episode, *timings)


if __name__ == '__main__':
    main()
