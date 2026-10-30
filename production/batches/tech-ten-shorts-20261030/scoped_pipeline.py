"""Bind hash-pinned reviewed pipeline algorithms to one new selected project.

No source project is imported or executed with its original __file__ context.
All pipeline-local paths resolve through the current project's thin wrapper.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import types

from scoped_context import BATCH, ROOT, REVISION, authorization, inventory, make_context, read, sha


def load_template(slug, name):
    pins = read(BATCH / 'template-sources.json')['templates']
    if name not in pins:
        raise RuntimeError('Unregistered shared algorithm: ' + name)
    record = pins[name]
    template = ROOT / record['path']
    if sha(template) != record['sha256']:
        raise RuntimeError('Reviewed template changed; inspect and re-pin before reuse: ' + name)
    context = make_context(slug)
    wrapper = context['P'] / 'production' / (name + '.py')
    if not wrapper.is_file():
        raise RuntimeError('Missing scoped project wrapper: ' + str(wrapper))
    source = template.read_text(encoding='utf-8-sig')
    if name in {'time-captions', 'transcribe'}:
        if 'script/clauses.json' not in source:
            raise RuntimeError('Caption source-path adaptation no longer matches reviewed code.')
        source = source.replace('script/clauses.json', 'script/caption-clauses.json')
    if name == 'finish-video':
        old = "Path('C:/Users/1/Videos/YamyamProduction/daily-shorts-20261026/shorts-factorio-belt-gaps').resolve()"
        if source.count(old) != 1:
            raise RuntimeError('Owned-output scope adaptation no longer matches reviewed code.')
        source = source.replace(old, "Path(" + repr(str(context['MEDIA_ROOT'])) + ").resolve()")
    if name == 'build-review':
        source = source.replace('팩토리오 쇼츠 검수', '게임 기술 쇼츠 검수')
    audio_module = types.ModuleType('audio_revision')
    audio_module.__dict__.update(context)
    sys.modules['audio_revision'] = audio_module
    module = types.ModuleType('yamyam_tech_ten_' + name.replace('-', '_'))
    module.__file__ = str(wrapper)
    module.__package__ = None
    exec(compile(source, str(template), 'exec'), module.__dict__)
    if name == 'prepare-header':
        module.EXPECTED = context['MEDIA_ROOT'] / 'local'
    if hasattr(module, 'DEFAULT_VOICE'):
        module.DEFAULT_VOICE = context['media_reference'](context['VOICE'])
    return module, context, record


def dispatch(slug, name, argv=None):
    authorization(slug)
    module, context, record = load_template(slug, name)
    args = list(sys.argv[1:] if argv is None else argv)
    original_argv = sys.argv
    sys.argv = [str(context['P'] / 'production' / (name + '.py'))] + args
    try:
        if name == 'finish-video':
            parser = argparse.ArgumentParser()
            parser.add_argument('command', choices=['pair', 'integrity', 'qa'])
            parser.add_argument('--visual')
            parsed = parser.parse_args(args)
            context['assert_no_game_apps']()
            if parsed.command == 'pair':
                if not parsed.visual:
                    raise RuntimeError('Pass the exact current visual output.')
                result = module.pair(parsed.visual)
            else:
                result = getattr(module, parsed.command)()
        else:
            if name not in {'prepare-header', 'build-review', 'time-captions', 'assemble-paragraphs'}:
                context['assert_no_game_apps']()
            result = module.main()
        receipt_dir = context['LOCAL'] / 'adapter-source-receipts'
        receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt = {'revision': REVISION, 'slug': slug, 'algorithm': name,
                   'template': record, 'wrapperSha256': sha(Path(sys.argv[0])),
                   'adapterSha256': sha(Path(__file__)), 'contextSha256': sha(BATCH / 'scoped_context.py'),
                   'argv': args, 'sourceProjectWritten': False}
        digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()[:12]
        target = receipt_dir / (name + '-' + digest + '.json')
        if not target.exists():
            target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return result
    finally:
        sys.argv = original_argv
