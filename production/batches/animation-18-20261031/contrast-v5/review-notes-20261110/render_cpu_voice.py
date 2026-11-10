"""Resume missing observation takes using the approved Qwen voice on CPU."""
import argparse
import os
import runpy
import sys

from plan_observations import ROOT, WORK, load, relative, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', nargs='+')
    parser.add_argument('--retake', nargs='+')
    parser.add_argument('--batch-size', type=int, default=3)
    parser.add_argument('--float32', action='store_true')
    args = parser.parse_args()
    os.environ.update(OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', CUDA_VISIBLE_DEVICES='-1')
    original = load(WORK / 'observations.ko.json')
    chunks = WORK / 'voice/chunks'
    import soundfile as sf

    def finished(scene):
        path = chunks / f'{scene["id"]}-scene.wav'
        if not path.exists():
            return False
        try:
            info = sf.info(path)
            return info.channels == 1 and info.samplerate == 24000 and info.frames >= 7200
        except RuntimeError:
            return False

    scenes = [scene for scene in original['scenes']
              if (not args.episodes or scene['id'][:3] in args.episodes)
              and (scene['id'] in args.retake if args.retake else not finished(scene))]
    if not scenes:
        return
    scope = '-'.join(args.retake or args.episodes or ['remaining'])
    script = WORK / f'voice-{scope}.ko.json'
    manifest = WORK / f'voice-{scope}-manifest.json'
    data = load(WORK / 'tts-manifest.json')
    data['paths']['script'] = relative(script)
    data['tts']['filenameStem'] = f'observation-notes-{scope}'
    save(script, {'scenes': scenes})
    save(manifest, data)
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    original_threads = torch.set_num_threads
    torch.set_num_threads = lambda n: original_threads(min(4, n))
    if not args.float32:
        pretrained = Qwen3TTSModel.from_pretrained
        Qwen3TTSModel.from_pretrained = staticmethod(
            lambda *a, **k: pretrained(*a, **dict(k, dtype=torch.bfloat16)))
    tool = ROOT / 'qwen3-tts/render_narration.py'
    sys.path.insert(0, str(tool.parent))
    engine = runpy.run_path(str(tool), run_name='observation_voice_runtime')
    engine['configure_project'].__globals__['INFERENCE_DEVICE'] = 'cpu'
    engine['configure_project'](data['slug'], relative(manifest))
    engine['load_tts_dependencies']()
    jobs = engine['load_jobs']()
    engine['render_chunks'](engine['build_render_items'](jobs), args.batch_size, set(args.retake or ()))


if __name__ == '__main__':
    main()
