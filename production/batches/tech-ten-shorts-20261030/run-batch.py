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
import re
import struct
import subprocess
import sys
import uuid

from batch_job_lock import SerialJobLock, JobBusy, inspect_lock
from scoped_context import (BATCH, ROOT, MEDIA, REVISION, Deferred, authorization,
                            inventory, make_context, now, normalize_speech, process_snapshot, read, sha)

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


def reconciliation_file(audio, role):
    return Path(audio) / ('asr-reconciliation.json' if role == 'voice' else 'asr-mix-reconciliation.json')


def evidence_path(record):
    path = Path(record['path'])
    return path if path.is_absolute() else ROOT / path


def reconciliation_dependencies(path):
    """Declared files are dependencies as well as verified acceptance artifacts."""
    path = Path(path)
    if not path.exists():
        return []
    files = [path]
    for item in read(path).get('independentEvidence', []):
        files.append(evidence_path(item))
        for key in ['sourceVoice', 'priorLineLevels', 'currentLineLevels']:
            if key in item:
                files.append(evidence_path(item[key]))
        for selection in item.get('unchangedParagraphs', []):
            if 'priorNormalizedTake' in selection:
                files.append(evidence_path(selection['priorNormalizedTake']))
    return files


def float32_mono_wav_data(path):
    """Return exact IEEE FLOAT32 samples; PEAK creation time is not audio."""
    data = Path(path).read_bytes()
    if len(data) < 12 or data[:4] != b'RIFF' or data[8:12] != b'WAVE' or struct.unpack_from('<I', data, 4)[0] + 8 != len(data):
        raise RuntimeError('ASR reuse requires a complete RIFF/WAVE container')
    position, chunks = 12, {}
    while position < len(data):
        if position + 8 > len(data):
            raise RuntimeError('ASR reuse encountered a truncated WAV chunk')
        name, size = data[position:position + 4], struct.unpack_from('<I', data, position + 4)[0]
        position += 8
        if position + size > len(data) or (name in {b'fmt ', b'data'} and name in chunks):
            raise RuntimeError('ASR reuse requires complete unique WAV format/data chunks')
        chunks[name] = data[position:position + size]
        position += size + size % 2
    fmt, samples = chunks.get(b'fmt ', b''), chunks.get(b'data', b'')
    if len(fmt) < 16:
        raise RuntimeError('ASR reuse WAV format is missing')
    code, channels, rate, byte_rate, align, bits = struct.unpack_from('<HHIIHH', fmt)
    if (code, channels, rate, byte_rate, align, bits) != (3, 1, 24000, 96000, 4, 32) or not samples or len(samples) % 4:
        raise RuntimeError('ASR reuse requires exact mono24kHz IEEE FLOAT32 data')
    return fmt, samples


def validate_asr_reconciliation(path, report_path, source, voice, script, expected, pronunciation_aliases):
    """Accept only complete, evidence-bound orthographic reconciliation.

    The original recognizer report and its false normalizedMatch remain intact.
    This is machine-content evidence, never a claim of actual human listening.
    """
    path, report_path, source, voice, script = map(Path, [path, report_path, source, voice, script])
    review, report = read(path), read(report_path)
    def require(condition, message):
        if not condition:
            raise RuntimeError('ASR reconciliation rejected: ' + message)
    require(review.get('status') == 'reviewed-orthography-only', 'explicit bounded review is missing')
    require(review.get('role') == report.get('role'), 'role differs')
    for key, file in [('inputSha256', source), ('voiceSha256', voice), ('asrSha256', report_path), ('scriptSha256', script)]:
        require(review.get(key) == sha(file), key + ' differs')
    require(report.get('sha256') == sha(source) and report.get('expectedSourceSha256') == sha(script), 'raw input/script binding differs')
    require(report.get('fullInput') is True and report.get('expectedTextPromptUsed') is False
            and report.get('rawRecognitionUnmodified') is True, 'raw unprompted full-input evidence is missing')
    require(type(review.get('unresolvedCount')) is int and review['unresolvedCount'] == 0
            and review.get('unresolved') == [], 'unresolved differences remain')
    require(review.get('rawAsrPreserved') is True and review.get('actualListening') == 'pending'
            and review.get('humanListening') == 'pending', 'raw preservation/listening boundary differs')
    aliases = review.get('aliases')
    require(isinstance(aliases, dict) and bool(aliases), 'nonempty explicit mappings are required')
    norm = lambda value: normalize_speech(value, pronunciation_aliases)
    paths, evidence_text = [path, report_path], {}
    def checked_file(record):
        file = evidence_path(record)
        require(file.is_file() and record.get('sha256') == sha(file), 'independent evidence file changed: ' + str(file))
        paths.append(file)
        return file
    evidence_rows = review.get('independentEvidence', [])
    require(isinstance(evidence_rows, list) and bool(evidence_rows), 'independent recognition evidence is required')
    for item in evidence_rows:
        identifier = item.get('id')
        require(isinstance(identifier, str) and identifier and identifier not in evidence_text, 'evidence IDs must be unique')
        evidence = read(checked_file(item))
        require(evidence.get('expectedTextPromptUsed') is False and evidence.get('rawRecognitionUnmodified') is True,
                'independent recognition was prompted or modified')
        evidence_voice = evidence.get('voiceSha256', evidence.get('sha256'))
        if evidence_voice == sha(voice):
            texts = [evidence.get('text', '')] + [row.get('raw', {}).get('text', '') for row in evidence.get('paragraphs', [])]
        else:
            # A prior report remains useful only for PCM paragraphs proven unchanged
            # through the preserved assembly receipts, never for the repaired line.
            for key in ['sourceVoice', 'priorLineLevels', 'currentLineLevels']:
                require(isinstance(item.get(key), dict), 'prior-voice evidence requires ' + key)
            prior_voice = checked_file(item['sourceVoice'])
            prior = read(checked_file(item['priorLineLevels']))
            current = read(checked_file(item['currentLineLevels']))
            require(sha(prior_voice) == evidence_voice == prior.get('voiceSha256')
                    and current.get('voiceSha256') == sha(voice), 'prior/current assembly binding differs')
            reused = item.get('unchangedParagraphs', [])
            require(isinstance(reused, list) and bool(reused), 'prior evidence requires exact unchanged paragraphs')
            texts = []
            for selection in reused:
                index = selection.get('lineIndex')
                require(type(index) is int, 'paragraph index must be an integer')
                previous = [row for row in prior['paragraphs'] if row['lineIndex'] == index]
                present = [row for row in current['paragraphs'] if row['lineIndex'] == index]
                observed = [row for row in evidence.get('paragraphs', []) if row.get('id') == selection.get('evidenceParagraphId')]
                require(len(previous) == len(present) == len(observed) == 1, 'paragraph evidence is missing or ambiguous')
                old, new, observed = previous[0], present[0], observed[0]
                require(all(old.get(key) == new.get(key) for key in ['text', 'rawTakeSha256', 'samples', 'rate']),
                        'reused paragraph text/PCM changed')
                require(old.get('destinationSampleRange') == [observed.get('startSample'), observed.get('endSample')]
                        and old.get('rate') == observed.get('sampleRate'), 'independent crop does not identify the prior paragraph')
                for key in ['rawTake', 'normalizedTake']:
                    checked_file({'path': new[key], 'sha256': new[key + 'Sha256']})
                if old.get('normalizedTakeSha256') != new.get('normalizedTakeSha256'):
                    previous_take = selection.get('priorNormalizedTake')
                    require(isinstance(previous_take, dict) and previous_take.get('sha256') == old.get('normalizedTakeSha256'),
                            'different normalized containers need the preserved prior take')
                    previous_file = checked_file(previous_take)
                    old_fmt, old_pcm = float32_mono_wav_data(previous_file)
                    new_fmt, new_pcm = float32_mono_wav_data(evidence_path({'path': new['normalizedTake']}))
                    require(old_fmt == new_fmt and old_pcm == new_pcm and len(new_pcm) // 4 == new['samples']
                            and hashlib.sha256(old_pcm).hexdigest() == observed.get('decodedFloat32LeSha256'),
                            'normalized audio samples changed; metadata-only reuse is not proven')
                texts.append(observed.get('raw', {}).get('text', ''))
        evidence_text[identifier] = norm(' '.join(texts))
        require(bool(evidence_text[identifier]), 'independent report contains no recognized text')
    changes = review.get('changes', [])
    require(isinstance(changes, list) and len(changes) == len(aliases), 'every mapping requires one documented change')
    normalized_aliases, seen = {}, set()
    raw, target = norm(report['text']), norm(expected)
    for change in changes:
        before, after = change.get('source'), change.get('target')
        require(isinstance(before, str) and isinstance(after, str) and aliases.get(before) == after and before not in seen,
                'documented mapping differs from aliases')
        seen.add(before)
        a, b = norm(before), norm(after)
        require(a and b and a != b and a not in normalized_aliases, 'empty, duplicate or no-op normalized mapping')
        kind = change.get('kind')
        if kind == 'mesh-loanword-orthography':
            require(a.count('메쉬') == 1 and a.replace('메쉬', '메시') == b, 'not a bounded Mesh spelling variant')
        elif kind == 'contextual-possessive-pronunciation':
            differing = [i for i, pair in enumerate(zip(a, b)) if pair[0] != pair[1]]
            require(len(a) == len(b) and len(differing) == 1, 'not one contextual possessive variant')
            at = differing[0]
            require(2 <= at < len(a) - 2 and a[at] == '에' and b[at] == '의', 'possessive variant needs both surrounding contexts')
        elif kind == 'contextual-bridge-liaison-orthography':
            # Korean 달이 and 다리 both surface as /다리/. Only this exact
            # inspected bridge sentence is admitted; not a general noun alias.
            require((a, b) == ('이스타크래프트달이대각선으로놓여있죠',
                               '이스타크래프트다리대각선으로놓여있죠'),
                    'not the exact bridge liaison context')
        elif kind == 'contextual-locative-pronunciation':
            # 의 can be pronounced 에. The authored locative is established by
            # the complete same-area grid sentence, not by a global reversal.
            require((a, b) in {('같은넓이의가로네칸', '같은넓이에가로네칸'),
                              ('새게임사이의통역기를둔다면어떨까요', '새게임사이에통역기를둔다면어떨까요')},
                    'not an exact reviewed locative context')
        elif kind == 'contextual-method-liaison-orthography':
            require((a, b) == ('그값을찾아주는시기죠', '그값을찾아주는식이죠'),
                    'not the exact value-lookup method liaison context')
        else:
            raise RuntimeError('ASR reconciliation rejected: unsupported orthographic kind; names and semantic replacements are forbidden')
        require(isinstance(change.get('reason'), str) and bool(change['reason'].strip()), 'review rationale is missing')
        refs = change.get('evidenceIds', [])
        require(isinstance(refs, list) and bool(refs) and all(ref in evidence_text and
                (a in evidence_text[ref] or (kind in ['contextual-bridge-liaison-orthography',
                 'contextual-locative-pronunciation', 'contextual-method-liaison-orthography'] and b in evidence_text[ref])) for ref in refs),
                'documented variant is not present in its independent evidence')
        require(type(change.get('occurrences')) is int and change['occurrences'] > 0
                and raw.count(a) == change['occurrences'] and b in target, 'mapping count/context differs')
        normalized_aliases[a] = b
    expression = re.compile('|'.join(re.escape(key) for key in sorted(normalized_aliases, key=lambda key: (-len(key), key))))
    require(expression.sub(lambda match: normalized_aliases[match.group()], raw) == target,
            'complete canonical content still differs; no partial acceptance')
    require(norm(''.join(chunk['text'] for chunk in report.get('chunks', []))) == raw, 'raw full text and chunks differ')
    return {'rawNormalizedMatch': report.get('normalizedMatch'), 'reconciledContentMatch': True,
            'orthographicChanges': len(changes), 'actualListening': 'pending',
            'reconciliationSha256': sha(path)}, sorted(set(paths), key=str)


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
        if stage in {'voice-asr', 'captions'}:
            files += reconciliation_dependencies(reconciliation_file(self.audio, 'voice'))
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
        script = self.project / 'script/narration.spoken.ko.json'
        expected = ' '.join(line for scene in read(script)['scenes'] for line in scene['lines'])
        aliases = read(self.project / 'script/caption-clauses.json').get('pronunciationAliases', {})
        raw_match = normalize_speech(data['text'], aliases) == normalize_speech(expected, aliases)
        if data.get('normalizedMatch') is True and raw_match:
            return {'normalizedMatch': True, 'rawNormalizedMatch': True, 'actualListening': 'pending'}, [path]
        receipt = reconciliation_file(self.audio, role)
        if not receipt.exists():
            raise RuntimeError('Raw ASR differs from narration; inspect actual PCM. Do not silently create aliases.')
        return validate_asr_reconciliation(receipt, path, source, self.ctx['VOICE'], script, expected, aliases)

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
