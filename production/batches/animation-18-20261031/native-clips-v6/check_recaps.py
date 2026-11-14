"""Read the rendered summary and align its bilingual captions to the exact WAV."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import sys

from prepare import BATCH, HERE, ROOT, WORK, VOICE_LOCAL, read, save


def check(episode, recognize=None):
    os.environ.update(OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', CUDA_VISIBLE_DEVICES='-1')
    sys.path.insert(0, str(BATCH / 'contrast-v5/review-notes-20261110'))
    from read_observations import initialize
    sys.path.insert(0, str(ROOT / 'projects/animation-breaking-down-attack-animations/production/grid-v1'))
    import caption_pipeline
    import soundfile as sf
    row = next(r for r in read(HERE / 'plan.json')['episodes'] if r['id'] == episode)
    wav = VOICE_LOCAL / 'voice/chunks' / (episode + '-scene.wav')
    with wav.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    folder = WORK / episode / 'summary-captions'
    proof = VOICE_LOCAL / 'asr' / (episode + '.json')
    if not proof.exists() or read(proof).get('audio_sha256') != digest:
        if recognize is None:
            recognize = initialize()
        result = recognize(str(wav), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
                           return_timestamps='word', batch_size=1)
        save(proof, {'audio_sha256': digest, 'words': result['chunks'],
                     'text': result['text'].strip(), 'humanListened': False})
    print(episode, read(proof)['text'], flush=True)
    ko = re.split(r'(?<=[.!?])\s+', row['recapKo'])
    en = re.split(r'(?<=[.!?])\s+', row['recapEn'])
    units = [{'ko': k, 'en': e,
              'twoLineReason': 'Keep the complete summary sentence so its action and result or paired comparison remain together.'}
             for k, e in zip(ko, en, strict=True)]
    duration = sf.info(wav).duration
    assert duration <= 9.65
    def output_path(value):
        path = Path(value).resolve()
        assert path.is_relative_to(folder.resolve())
        return path

    caption_pipeline.routed_write_path = output_path
    caption_pipeline.build({'fps': 60, 'bodyEndFrame': 720, 'paragraphs': [
        {'id': episode + '-summary', 'scene': 'summary', 'start': 2.18, 'duration': duration,
         'ko': row['recapKo'], 'en': row['recapEn'], 'audioFile': str(wav),
         'asrFile': str(proof), 'captionUnits': units}]}, folder)
    return recognize


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episodes', nargs='+')
    args = parser.parse_args()
    recognizer = None
    for identity in args.episodes:
        recognizer = check(identity, recognizer)
