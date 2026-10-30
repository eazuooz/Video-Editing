"""Finite sequential local-review runner. Default action is read-only validation.

Expensive work requires --execute and an exact code/input readiness receipt.
No platform operation, process termination, source revision or implicit approval.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import html
import json
import os
import subprocess
import sys
import uuid

from batch_job_lock import SerialJobLock, JobBusy, inspect_lock
from scoped_context import (BATCH, ROOT, MEDIA, REVISION, Deferred, authorization,
                            inventory, make_context, now, process_snapshot, read, sha)

PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
STAGES = ['voice', 'voice-asr', 'captions', 'visual-preparation', 'native-capture',
          'header', 'visual-render', 'audio-mix', 'audio-report', 'mix-asr',
          'video-pair', 'integrity', 'qa', 'review']
INPUT_NAMES = ['project.json', 'planning/production-plan.json', 'sources/selected-footage.json',
               'script/narration.spoken.ko.json', 'script/caption-clauses.json',
               'production/tts-manifest.json', 'production/section-plan.json',
               'production/visual-config.json', 'production/visual-pipeline.json',
               'publishing/metadata.json', 'script/narration.ko.txt']


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    os.replace(temporary, path)


def artifact(path):
    path = Path(path)
    if not path.is_file():
        raise RuntimeError('Required artifact missing: ' + str(path))
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def verify(rows):
    for row in rows:
        path = Path(row['path'])
        if not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise RuntimeError('Previous successful artifact changed; preserve and inspect: ' + str(path))


def code_paths(project):
    files = [BATCH / 'run-batch.py', BATCH / 'batch_job_lock.py', BATCH / 'scoped_context.py',
             BATCH / 'scoped_pipeline.py', BATCH / 'template-sources.json']
    files += sorted((project / 'production').glob('*.py'))
    for record in read(BATCH / 'template-sources.json')['templates'].values():
        target = ROOT / record['path']
        if sha(target) != record['sha256']:
            raise RuntimeError('Hash-pinned source algorithm changed: ' + str(target))
        files.append(target)
    pipeline_path = project / 'production/visual-pipeline.json'
    if pipeline_path.exists():
        files += [ROOT / p for p in read(pipeline_path).get('codePaths', [])]
    return sorted(set(files), key=str)


def fingerprints(project):
    return {'code': [artifact(p) for p in code_paths(project)],
            'inputs': [artifact(project / p) for p in INPUT_NAMES]}


def readiness(slug):
    ctx = make_context(slug); ctx['guard']()
    project = ctx['P']; pipeline = read(project / 'production/visual-pipeline.json')
    if pipeline.get('revision') != REVISION:
        raise RuntimeError('Visual pipeline must identify the current exact revision.')
    for key in ['prepareCommand', 'renderCommand', 'visualOutput']:
        if not pipeline.get(key):
            raise RuntimeError('Missing scoped visual pipeline field: ' + key)
    native = pipeline.get('nativeCaptureCommand')
    if pipeline.get('usesUnity') is True and not native:
        raise RuntimeError('Unity scene choice requires an actual native capture command.')
    plan = read(project / 'planning/production-plan.json')
    if plan.get('rightsAndFhdReady') is not True:
        raise Deferred('Source rights and decoded native FHD checks are incomplete.')
    metadata = read(project / 'publishing/metadata.json')
    if not metadata.get('title') or not metadata.get('description'):
        raise RuntimeError('Metadata requires exact title and description fields.')
    document = read(BATCH / 'readiness.json').get('projects', {}).get(slug, {})
    if document.get('codeReadyForActualProduction') is not True:
        raise Deferred('Actual production code readiness has not been recorded for ' + slug)
    current = fingerprints(project)
    if document.get('fingerprints') != current:
        raise Deferred('Reviewed production code or selected inputs changed; inspect before updating readiness.')
    return ctx, pipeline, current


def safe_resources(ctx, stage):
    authorization(ctx['SLUG']); ctx['assert_no_game_apps']()
    if (ROOT / 'shared/output/GPU_HANDOFF.json').exists():
        raise Deferred('Existing GPU job lease is active; preserved without overlap.')
    import psutil
    for drive, minimum in [('C:/', 3 * 1024**3), ('D:/', 250 * 1024**2)]:
        if psutil.disk_usage(drive).free < minimum:
            raise Deferred('Insufficient workspace storage on ' + drive)
    return {'stage': stage, 'checkedAt': now(), 'foreignProcessesUntouched': True}


class Pipeline:
    def __init__(self, slug, lock, retry=False):
        self.ctx, self.visual, self.input_fingerprints = readiness(slug)
        self.slug = slug; self.project = self.ctx['P']; self.local = self.ctx['LOCAL']
        self.audio = self.ctx['L']; self.lock = lock; self.retry = retry
        self.folder = self.local / 'finite-pipeline-v1'; self.folder.mkdir(parents=True, exist_ok=True)
        self.state_path = self.folder / 'state.json'
        self.state = read(self.state_path) if self.state_path.exists() else {
            'slug': slug, 'revision': REVISION, 'createdAt': now(), 'stages': {},
            'fingerprints': self.input_fingerprints, 'platformActionsPerformed': False}
        if self.state.get('fingerprints') != self.input_fingerprints:
            passed = {name: value for name, value in self.state['stages'].items() if value.get('status') == 'pass'}
            if not set(passed).issubset({'voice', 'voice-asr', 'captions'}):
                raise RuntimeError('Previous visual attempt inputs differ. Preserve old outputs before an explicit version change.')
            for name, previous in passed.items():
                verify(previous['artifacts'])
                if previous.get('dependencies') != self.dependencies(name):
                    raise RuntimeError('Reviewed change affects already completed audio stage: ' + name)
            self.state.setdefault('fingerprintHistory', []).append({'previous': self.state['fingerprints'],
                'replacedAt': now(), 'reason': 'Explicitly reviewed future visual/input changes; completed speech dependencies and output hashes unchanged.',
                'reusedStages': sorted(passed)})
            self.state['fingerprints'] = self.input_fingerprints

    def dependencies(self, stage):
        if stage not in {'voice', 'voice-asr', 'captions'}:
            return self.input_fingerprints
        names = {'voice': ['render-voice', 'assemble-paragraphs'],
                 'voice-asr': ['transcribe'], 'captions': ['time-captions']}[stage]
        files = [BATCH / 'scoped_context.py', BATCH / 'scoped_pipeline.py',
                 self.project / 'script/narration.spoken.ko.json', self.project / 'script/narration.ko.txt']
        pins = read(BATCH / 'template-sources.json')['templates']
        for name in names:
            files += [ROOT / pins[name]['path'], self.project / 'production' / (name + '.py')]
        if stage == 'voice':
            manifest_path = self.project / 'production/tts-manifest.json'; manifest = read(manifest_path)
            files += [manifest_path, ROOT / manifest['tts']['reference'], ROOT / manifest['tts']['referenceText']]
        else:
            files += [self.ctx['VOICE'], self.project / 'script/caption-clauses.json']
        if stage == 'captions':
            files += [self.audio / ('asr-voice-' + sha(self.ctx['VOICE'])[:12] + '.json')]
        return {'slug': self.slug, 'revision': REVISION, 'algorithmStage': stage,
                'files': [artifact(p) for p in sorted(set(files), key=str)]}

    def write(self):
        self.state['updatedAt'] = now(); save(self.state_path, self.state)

    def stage(self, name, function):
        previous = self.state['stages'].get(name)
        if previous and previous.get('status') == 'pass':
            verify(previous['artifacts'])
            if previous.get('dependencies') != self.dependencies(name):
                raise RuntimeError('Successful stage dependencies changed: ' + name)
            return previous.get('result', {})
        if previous and previous.get('status') in {'running', 'failed'} and not self.retry:
            raise Deferred('Prior incomplete stage requires inspection then --retry-failed: ' + name)
        self.current = name; self.lock.set_stage(name)
        resources = safe_resources(self.ctx, name)
        if previous:
            self.state.setdefault('history', []).append({'stage': name, 'record': previous})
        self.state['stages'][name] = {'status': 'running', 'startedAt': now(), 'resources': resources,
                                     'dependencies': self.dependencies(name)}
        self.state.update(status='running', currentStage=name); self.write()
        try:
            result, paths = function()
            self.state['stages'][name].update(status='pass', endedAt=now(), result=result,
                                             artifacts=[artifact(p) for p in paths])
            self.write(); return result
        except BaseException as error:
            self.state['stages'][name].update(status='deferred' if isinstance(error, Deferred) else 'failed',
                                             endedAt=now(), error=str(error))
            self.state['status'] = self.state['stages'][name]['status']; self.write(); raise

    def command(self, command):
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            raise RuntimeError('Commands must be explicit argv arrays, never shell text.')
        replacements = {'{ROOT}': str(ROOT), '{PROJECT}': str(self.project), '{LOCAL}': str(self.local.resolve()),
                        '{SLUG}': self.slug, '{PYTHON}': str(PYTHON)}
        if (self.project / 'script/captions.json').exists():
            replacements['{FRAMES}'] = str(read(self.project / 'script/captions.json')['frames'])
        args = []
        for item in command:
            for key, value in replacements.items(): item = item.replace(key, value)
            if '{' in item or '}' in item: raise RuntimeError('Unresolved argv token: ' + item)
            args.append(item)
        log = self.folder / ('log-' + self.current + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6] + '.txt')
        self.state['stages'][self.current].setdefault('commands', []).append({'argv': args, 'log': str(log)})
        self.write(); print('START', self.slug, self.current, flush=True)
        with log.open('x', encoding='utf8') as stream:
            process = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
                env={**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
        if process.returncode:
            raise RuntimeError(f'{self.current} exited {process.returncode}; retained {log}')
        return log

    def py(self, name, *args):
        return [str(PYTHON), '-B', '-X', 'utf8', str(self.project / 'production' / (name + '.py')), *args]

    def simple(self, command, paths, result=None):
        self.command(command); return result or {}, paths

    def voice(self):
        if self.ctx['VOICE'].exists():
            # A successful assembly receipt, not mere file existence, permits reuse.
            self.command(self.py('assemble-paragraphs'))
        else:
            self.ctx['assert_gpu_available'](); self.command(self.py('render-voice'))
        return {'actualListening': 'pending'}, [self.ctx['VOICE'], self.audio / 'line-levels.json', self.audio / 'voice/narration.timing.json']

    def asr(self, role):
        self.command(self.py('transcribe', role))
        source = self.ctx['VOICE'] if role == 'voice' else self.audio / 'final-mix.m4a'
        path = self.audio / f'asr-{role}-{sha(source)[:12]}.json'; data = read(path)
        if (data.get('sha256') != sha(source) or data.get('role') != role or not data.get('fullInput')
            or not data.get('chunks') or data.get('expectedTextPromptUsed') is not False
            or data.get('rawRecognitionUnmodified') is not True
            or data.get('expectedSourceSha256') != sha(self.project / 'script/narration.spoken.ko.json')):
            raise RuntimeError('ASR requires exact current full-input unprompted evidence.')
        if data.get('normalizedMatch') is not True:
            raise RuntimeError('Raw ASR differs from narration; inspect actual PCM. Do not silently create aliases.')
        return {'normalizedMatch': True, 'actualListening': 'pending'}, [path]

    def captions(self):
        self.command(self.py('time-captions')); c = read(self.project / 'script/captions.json')
        if c.get('fps') != 60 or c.get('timingInputs', {}).get('voiceSha256') != sha(self.ctx['VOICE']):
            raise RuntimeError('Captions must match actual current PCM at 60fps.')
        return {'frames': c['frames']}, [self.project / 'script/captions.json', self.audio / 'caption-alignment.json',
            self.audio / 'caption-layout.json', self.audio / 'captions.ko.ass', self.audio / 'captions.ko.srt', self.audio / 'captions.en.srt']

    def path(self, value):
        for token, replacement in {'{ROOT}': str(ROOT), '{PROJECT}': str(self.project), '{LOCAL}': str(self.local.resolve()), '{SLUG}': self.slug}.items():
            value = value.replace(token, replacement)
        path = Path(value)
        return path if path.is_absolute() else ROOT / path

    def visual_prep(self):
        self.command(self.visual['prepareCommand'])
        p = self.project / 'production/visual-timing.json'; t = read(p)
        if t != read(self.local / 'visual-timing.json') or t.get('revision') != REVISION or t.get('previewOnly') is not False:
            raise RuntimeError('Visuals need one matching final-PCM timeline.')
        if t.get('frames') != read(self.project / 'script/captions.json')['frames']:
            raise RuntimeError('Visual and caption frame counts differ.')
        return {'frames': t['frames']}, [p, self.local / 'visual-timing.json']

    def native(self):
        if self.visual.get('usesUnity') is not True:
            return {'kind': 'purposeful-2d-diagram', 'unityClaimed': False}, []
        self.ctx['assert_gpu_available'](); self.command(self.visual['nativeCaptureCommand'])
        receipt = self.path(self.visual['nativeCaptureReceipt'])
        data = read(receipt)
        if data.get('success') is not True or data.get('voiceSha256') != sha(self.ctx['VOICE']):
            raise RuntimeError('Native capture needs exact-PCM successful receipt.')
        if not data.get('artifacts'):
            raise RuntimeError('Native capture receipt must include hashed generated frame artifacts.')
        verify(data['artifacts'])
        return {'kind': 'actual-native-unity-capture', 'humanMovingReview': 'pending'}, [receipt]

    def header(self):
        path = self.local / 'static-header-v1.png'; receipt = self.local / 'header-build.json'
        if not path.exists(): self.command(self.py('prepare-header'))
        h = read(receipt)
        if h.get('sha256') != sha(path) or h.get('text') != read(self.project / 'production/visual-config.json')['head']:
            raise RuntimeError('Existing header differs from exact selected title.')
        return {}, [path, receipt]

    def render(self):
        output = self.path(self.visual['visualOutput']); receipt = self.path(self.visual['renderReceipt'])
        if not output.exists(): self.command(self.visual['renderCommand'])
        r = read(receipt)
        if r.get('done') is not True or r.get('result') != 0 or r.get('errors') or r.get('outputSha256') != sha(output):
            raise RuntimeError('Visual master requires an error-free hash-bound render receipt.')
        return {'visual': str(output)}, [output, receipt]

    def pair(self):
        final = self.project / read(self.project / 'project.json')['currentFinalDirectory']
        visual = self.path(self.visual['visualOutput']); record = final / 'pair-build.json'
        if not (final / 'clean.mp4').exists() and not (final / 'captioned.mp4').exists():
            self.command(self.py('finish-video', 'pair', '--visual', str(visual)))
        data = read(record)
        for key, path in {'visual': visual, 'audio': self.audio / 'final-mix.m4a', 'ass': self.audio / 'captions.ko.ass',
                          'clean': final / 'clean.mp4', 'captioned': final / 'captioned.mp4'}.items():
            if data.get(key) != sha(path): raise RuntimeError('Existing pair differs from exact current inputs.')
        return {'directory': str(final)}, [record, final / 'clean.mp4', final / 'captioned.mp4', final / 'captions.ko.srt', final / 'captions.en.srt']

    def run(self, through):
        final = self.project / read(self.project / 'project.json')['currentFinalDirectory']
        actions = {
            'voice': self.voice, 'voice-asr': lambda: self.asr('voice'), 'captions': self.captions,
            'visual-preparation': self.visual_prep, 'native-capture': self.native, 'header': self.header,
            'visual-render': self.render,
            'audio-mix': lambda: self.simple(self.py('finish-audio', 'mix'), [self.audio / 'audio-build.json', self.audio / 'final-mix.m4a']),
            'audio-report': lambda: self.simple(self.py('finish-audio', 'report'), [self.audio / 'audio-continuity.json']),
            'mix-asr': lambda: self.asr('mix'), 'video-pair': self.pair,
            'integrity': lambda: self.simple(self.py('finish-video', 'integrity'), [final / 'integrity.json']),
            'qa': lambda: self.qa(final),
            'review': lambda: self.simple(self.py('build-review'), [final / 'index.html', final / 'SHA256SUMS.txt', final / 'delivery.json'],
                {'generatedForReview': True, 'actualHumanReview': 'pending', 'actualFullListening': 'pending', 'fullMovingReview': 'pending'})}
        for name in STAGES[:STAGES.index(through) + 1]: self.stage(name, actions[name])
        self.state['status'] = 'review-files-generated-internal-review-pending' if through == 'review' else 'paused-after-' + through
        self.write(); return self.state

    def qa(self, final):
        self.command(self.py('finish-video', 'qa'))
        return {'generatedOnly': True, 'humanViewed': False}, [final / 'mobile-review.mp4', final / ('qa-sequential-' + sha(final / 'captioned.mp4')[:12]) / 'index.json']


def overview():
    _, rows = inventory(); items = []
    for row in rows:
        project = ROOT / 'projects' / row['slug']; local = project / 'production/local'
        path = local / 'finite-pipeline-v1/state.json'; state = read(path) if path.exists() else {}
        final = project / read(project / 'project.json')['currentFinalDirectory']
        items.append({'slug': row['slug'], 'title': row['title'], 'status': state.get('status', 'preproduction'),
                      'review': str((final / 'index.html').resolve()) if (final / 'index.html').exists() else None,
                      'captioned': artifact(final / 'captioned.mp4') if (final / 'captioned.mp4').exists() and state.get('stages', {}).get('integrity', {}).get('status') == 'pass' else None,
                      'humanReview': 'pending'})
    target = MEDIA / 'batch-local'; target.mkdir(parents=True, exist_ok=True)
    save(target / 'status.json', {'revision': REVISION, 'updatedAt': now(), 'projects': items, 'platformActionsPerformed': False})
    cards = []
    for item in items:
        link = '<a href="' + Path(item['review']).as_uri() + '">전체 영상 검수</a>' if item['review'] else '제작 중'
        cards.append('<li><b>' + html.escape(item['title']) + '</b><p>' + html.escape(item['status']) + ' · ' + link + '</p></li>')
    (target / 'review-ten.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임 개발 기술 쇼츠 10편</title><style>body{background:#080b0a;color:white;font:17px sans-serif;max-width:950px;margin:auto;padding:24px}a{color:#73d7cd}li{margin:24px 0}h1{color:#ffd25a}</style><h1>게임 개발 기술 쇼츠 10편</h1><p>생성 및 기술 검사 상태입니다. 실제 전체 청취·화면 검수·사용자 최종검수는 별도로 남아 있습니다. 업로드하지 않았습니다.</p><ol>' + ''.join(cards) + '</ol></html>', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true'); parser.add_argument('--slug', action='append')
    parser.add_argument('--through', choices=STAGES, default='review'); parser.add_argument('--retry-failed', action='store_true')
    parser.add_argument('--resources', action='store_true'); parser.add_argument('--fingerprints', action='store_true')
    args = parser.parse_args(); _, rows = inventory(); slugs = args.slug or [r['slug'] for r in rows]
    if len(set(slugs)) != len(slugs) or not set(slugs).issubset({r['slug'] for r in rows}): parser.error('Select only exact unique batch slugs.')
    if args.resources:
        print(json.dumps({'apps': process_snapshot(), 'lock': inspect_lock(), 'gpuLeaseExists': (ROOT / 'shared/output/GPU_HANDOFF.json').exists()}, ensure_ascii=False, indent=2)); return
    if args.fingerprints:
        for slug in slugs:
            print(json.dumps({'slug': slug, 'fingerprints': fingerprints(ROOT / 'projects' / slug)}, ensure_ascii=False, indent=2))
        return
    if not args.execute:
        checks = []
        for slug in slugs:
            try: readiness(slug); checks.append({'slug': slug, 'ready': True})
            except Exception as error: checks.append({'slug': slug, 'ready': False, 'reason': str(error)})
        print(json.dumps(checks, ensure_ascii=False, indent=2)); return
    for slug in slugs:
        try:
            with SerialJobLock(slug, 'preflight') as lock:
                Pipeline(slug, lock, args.retry_failed).run(args.through)
        except (Deferred, JobBusy) as error:
            print(json.dumps({'slug': slug, 'status': 'deferred', 'reason': str(error)}, ensure_ascii=False)); break
        except Exception as error:
            print(json.dumps({'slug': slug, 'status': 'failed', 'reason': str(error)}, ensure_ascii=False)); break
        finally: overview()


if __name__ == '__main__': main()
