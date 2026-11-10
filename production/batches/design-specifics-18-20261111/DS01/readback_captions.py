"""Align a selected episode to the approved-voice WAVs and build both subtitle tracks."""

import argparse
import json
from pathlib import Path
import re
import sys

import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-notes-20261110'))
sys.path.insert(0, str(ROOT / 'projects/animation-breaking-down-attack-animations/production/grid-v1'))
from read_observations import initialize, sha
import caption_pipeline


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def display_text(scene, spellings):
    text = ' '.join(scene['lines'])
    for spoken, display in spellings.items():
        text = text.replace(spoken, display)
    return text


def units(scene, spellings=None):
    ko = re.split(r'(?<=[.!?])\s+', display_text(scene, spellings or {}))
    en = re.split(r'(?<=[.!?])\s+', scene['en'])
    return [{'ko': k, 'en': e,
             'twoLineReason': 'Preserve the complete paired sentence when its own cause or result depends on the preceding words.'}
            for k, e in zip(ko, en, strict=True)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode', default='DS01')
    parser.add_argument('--validate-script', action='store_true')
    args = parser.parse_args()
    episode = args.episode
    selected = load(ROOT / 'shared/publishing/video-production-control.json')['designSpecifics18Selected20261111']
    assert episode in selected['episodes'] and not selected['youtubeAuthorized']
    local = HERE.parent / 'local' / episode
    manifest = load(local / 'tts-manifest.json')
    narration = load(HERE.parent / episode / 'narration.json')
    script = narration['scenes']
    spellings = narration.get('captionDisplay', {})
    aliases = {display: spoken for spoken, display in spellings.items()}
    if args.validate_script:
        noto = Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
        font = caption_pipeline.measured_font(noto if noto.is_file() else Path('C:/Windows/Fonts/malgun.ttf'), 500)
        for scene in script:
            for pair in units(scene, spellings):
                for language in ('ko', 'en'):
                    if caption_pipeline.wrap(pair[language], font) is None:
                        raise ValueError(f'{episode} scene {scene["id"]} {language} caption does not fit: {pair[language]}')
        print(f'{episode} Korean and English captions fit the review layout', flush=True)
        return
    voice = local / 'voice'
    timing_file = voice / (manifest['tts']['filenameStem'] + '.timing.json')
    timing = load(timing_file)
    asr_root = local / 'asr'
    asr_root.mkdir(parents=True, exist_ok=True)
    recognize = None
    for row in script:
        name = row['id']
        audio = voice / 'chunks' / f'{name}-scene.wav'
        assert audio.is_file(), name
        digest = sha(audio)
        proof_file = asr_root / f'{name}.json'
        proof = load(proof_file) if proof_file.is_file() else {}
        if proof.get('audio_sha256') == digest:
            continue
        if recognize is None:
            recognize = initialize()
        result = recognize(str(audio), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
                           return_timestamps='word', batch_size=1)
        assert sha(audio) == digest and result.get('chunks'), name
        save(proof_file, {'audio_sha256': digest, 'words': result['chunks'],
                          'text': result['text'].strip(), 'humanListened': False})
        print(name, result['text'].strip(), flush=True)
    starts = {row['scene_id']: row['start'] for row in timing['entries']}
    paragraphs = []
    for row in script:
        name = row['id']
        audio = voice / 'chunks' / f'{name}-scene.wav'
        proof = asr_root / f'{name}.json'
        paragraphs.append({'id': episode + '-' + name, 'scene': name, 'start': 2 + starts[name],
                           'duration': sf.info(str(audio)).duration, 'ko': display_text(row, spellings), 'en': row['en'],
                           'audioFile': str(audio), 'asrFile': str(proof), 'captionUnits': units(row, spellings),
                           'aliases': aliases})
    output = (local / 'captions').resolve()

    def caption_write_path(value):
        path = Path(value).resolve()
        if not path.is_relative_to(output):
            raise ValueError(f'Caption output outside the {episode} revision: {path}')
        return path

    caption_pipeline.routed_write_path = caption_write_path
    caption_pipeline.build({'fps': 60, 'paragraphs': paragraphs,
                            'bodyEndFrame': 120 + round(timing['duration_seconds'] * 60)}, output)
    save(local / 'caption-input.json', {'fps': 60, 'paragraphs': paragraphs})
    print('ASR-aligned KO/EN tracks and boxed captions ready', flush=True)


if __name__ == '__main__':
    main()
