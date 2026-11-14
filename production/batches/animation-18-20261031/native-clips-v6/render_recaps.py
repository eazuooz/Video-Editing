"""Generate only missing ten-second-summary narration on a bounded CPU."""
import os
import runpy
import sys

from prepare import ROOT, VOICE_LOCAL, read


def main():
    scope = read(ROOT / 'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
    assert scope['ttsAuthorized'] and scope['episodes'] == [f'A{i:02}' for i in range(3, 19)]
    os.environ.update(OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', CUDA_VISIBLE_DEVICES='-1')
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    set_threads = torch.set_num_threads
    torch.set_num_threads = lambda number: set_threads(min(4, number))
    pretrained = Qwen3TTSModel.from_pretrained
    Qwen3TTSModel.from_pretrained = staticmethod(
        lambda *args, **kwargs: pretrained(*args, **dict(kwargs, dtype=torch.bfloat16)))
    sys.path.insert(0, str(ROOT / 'qwen3-tts'))
    runtime = runpy.run_path(str(ROOT / 'qwen3-tts/render_narration.py'), run_name='native_summary_voice')
    runtime['configure_project'].__globals__['INFERENCE_DEVICE'] = 'cpu'
    runtime['configure_project']('animation-native-clips-v6', str((VOICE_LOCAL / 'tts-manifest.json').relative_to(ROOT)))
    runtime['load_tts_dependencies']()
    jobs = runtime['load_jobs']()
    runtime['render_chunks'](runtime['build_render_items'](jobs), 3, set())


if __name__ == '__main__':
    main()
