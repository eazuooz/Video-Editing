"""Read-only source/paragraph/caption geometry preflight before expensive voice."""
from pathlib import Path
import argparse
import importlib.util
import json
from PIL import ImageFont
from scoped_context import BATCH, make_context, normalize_speech, read
from scoped_pipeline import load_template


def inspect(slug):
    context = make_context(slug); project = context['P']
    lines = [line for scene in read(project / 'script/narration.spoken.ko.json')['scenes'] for line in scene['lines']]
    clauses = read(project / 'script/caption-clauses.json'); aliases = clauses.get('pronunciationAliases', {})
    normalize = lambda text: normalize_speech(text, aliases)
    if any(normalize(line) != normalize(''.join(q['spoken'] for q in clauses['clauses'] if q['lineIndex'] == i)) for i, line in enumerate(lines)):
        raise RuntimeError('Spoken clauses do not exactly cover paragraphs.')
    if normalize(' '.join(lines)) != normalize((project / 'script/narration.ko.txt').read_text(encoding='utf8')):
        raise RuntimeError('Text narration differs from paragraph script.')
    caption_module, _, _ = load_template(slug, 'time-captions'); font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 60)
    errors = []
    for clause in clauses['clauses']:
        try: caption_module.wrap(clause['ko'], font)
        except Exception as error: errors.append({'id': clause['id'], 'text': clause['ko'], 'error': str(error)})
    spec = importlib.util.spec_from_file_location('current_visual_preparer', BATCH / 'prepare-visual.py')
    visual = importlib.util.module_from_spec(spec); spec.loader.exec_module(visual)
    config = read(project / 'production/visual-config.json')
    sources = visual.source_inventory(context, config, read(project / 'sources/selected-footage.json'))
    source_windows = []
    for group_id, group in config.get('cuts', {}).items():
        for i, cut in enumerate(group.get('sequence', [group])):
            source_id = cut.get('source', 'game-master')
            source_windows.append({'id': group_id + '-' + str(i), 'kind': 'game', 'source': source_id,
                'sourceStart': cut['in'], 'sourceEnd': min(cut['in'] + cut['maxDuration'], sources[source_id]['decodedDurationSeconds'])})
    annotations = visual.remap_source_annotations(source_windows, config, sources)
    result = {'slug': slug, 'paragraphs': len(lines), 'clauses': len(clauses['clauses']), 'spokenCoverage': 'pass',
              'captionLayoutErrors': errors, 'sourceProbe': {k: {x: v[x] for x in ['decodedWidth', 'decodedHeight', 'decodedDurationSeconds']} for k, v in sources.items()},
              'sourceAnnotationPreflight': {'mappedSourceWindowSegments': sum(len(v) for v in annotations.values()),
                    'actualPCMAlignedTiming': 'not-claimed-by-this-preflight', 'geometryBasis': 'decoded-source-pixels'}}
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('slug'); args = parser.parse_args()
    result = inspect(args.slug); print(json.dumps(result, ensure_ascii=False, indent=2))
    if result['captionLayoutErrors']: raise SystemExit(1)


if __name__ == '__main__': main()
