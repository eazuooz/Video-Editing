"""Two short independent PCM contexts for observed ASR-only extra endings.

Existing34 full/context windows and generated narration remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import os
import datetime
import psutil
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'projects/game-lighting-history-02/production/local/asr-tail-anomalies-v2'
EXPECTED_SHA = 'f8d4b3d3eb7940f91b0f5172f4f8d3fa85b3507826713973f73ede91a2405f86'


def main():
    import numpy as np
    import soundfile as sf
    import torch
    import torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    manifest = json.loads((ROOT / 'projects/game-lighting-history-02/project.json').read_text(encoding='utf-8'))
    output = ROOT / manifest['tts']['outputDir']
    stem = manifest['tts']['filenameStem']
    path = output / (stem + '.wav')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED_SHA
    if OUT.exists():
        raise RuntimeError('Preserve existing diagnostic results; no repeat run.')
    OUT.mkdir(parents=True)
    pcm, rate = sf.read(path, dtype='float32')
    timing = json.loads((output / (stem + '.timing.json')).read_text(encoding='utf-8'))
    model_dir = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_dir), dtype=torch.float32,
                low_cpu_mem_usage=True, use_safetensors=True, local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(str(model_dir), local_files_only=True)
    asr = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                   feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
    for scene in ['11m', '11l']:
        entries = [x for x in timing['entries'] if x['scene_id'] == scene]
        end = entries[-1]['end']
        start = max(entries[0]['start'], end - 24)
        part = pcm[round(start * rate):round(end * rate)]
        result = asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part), rate, 16000).numpy(),
                          sampling_rate=16000), return_timestamps='word',
                     generate_kwargs={'language': 'korean', 'task': 'transcribe'})
        # Energy summaries are evidence about samples, not pronunciation approval.
        energies = []
        for second in range(5):
            p = part[max(0, len(part)-(second+1)*rate):len(part)-second*rate]
            energies.append(dict(secondsBeforeEnd=second, rms=float(np.sqrt(np.mean(p*p))),
                                 peak=float(np.max(np.abs(p)))))
        record = dict(scene=scene, sourceFromSeconds=start, sourceToSeconds=end,
                      mode='independent-unprompted24second-final-complete-context',
                      audioSha256=EXPECTED_SHA, pcmSha256=hashlib.sha256(part.tobytes()).hexdigest(),
                      expectedFinalParagraph=entries[-1]['text'], expectedTextUsedAsPrompt=False,
                      completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      cpuThreads=2, gpuJobs=0, actualPid=os.getpid(),
                      createTime=psutil.Process().create_time(), finalFiveSecondEnergy=energies,
                      currentNarrationApproved=False, humanListeningApproved=False, **result)
        (OUT / (scene + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print('DONE targeted tail ' + scene, flush=True)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED_SHA


if __name__ == '__main__':
    main()
