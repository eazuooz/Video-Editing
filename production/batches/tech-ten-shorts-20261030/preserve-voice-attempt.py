"""Preserve an ended voice attempt and verify any reusable unchanged raw PCM."""
from pathlib import Path
import argparse
import json
import shutil
from scoped_context import BATCH, ROOT, make_context, now, read, sha


def preserve(slug):
    context = make_context(slug); project = context['P']; audio = context['L']
    record_path = audio / 'tts-execution.json'
    if not record_path.exists(): return {'existingAttempt': False}
    record = read(record_path); digest = sha(record_path)
    if record.get('state') not in {'failed', 'completed'}: raise RuntimeError('An active voice attempt must not be adopted or restarted.')
    current_script_matches = record.get('scriptSha256') == sha(project / 'script/narration.spoken.ko.json')
    if not current_script_matches and any((audio / 'voice/chunks').glob('*.wav')):
        raise RuntimeError('Previous script differs and raw PCM exists; inspect unchanged paragraph reuse before resuming.')
    directory = audio / 'attempt-history' / digest
    directory.mkdir(parents=True, exist_ok=True)
    for name in ['tts-execution.json', 'tts-execution.partial.json']:
        source = audio / name; target = directory / name
        if not source.exists(): continue
        if target.exists():
            if sha(target) != sha(source): raise RuntimeError('Attempt archive collision.')
        else: shutil.copy2(source, target)
    narration = read(project / 'script/narration.spoken.ko.json')
    expected = {f"{scene['id']}-{i:02}.wav": text for scene in narration['scenes'] for i, text in enumerate(scene['lines'], 1)}
    takes = {}; documented = {row['key'] + '.wav': row for row in record.get('takes', [])}
    for path in sorted((audio / 'voice/chunks').glob('*.wav')):
        row = documented.get(path.name)
        if not row or row['text'] != expected.get(path.name) or row['sha256'] != sha(path):
            raise RuntimeError('Unreceipted or changed raw take is preserved for inspection: ' + path.name)
        takes[path.name] = {'sha256': row['sha256'], 'text': row['text'], 'attemptRecordSha256': digest}
    if takes:
        (audio / 'reuse-takes.json').write_text(json.dumps(takes, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    deferred = record.get('state') == 'failed' and str(record.get('error', '')).startswith('Game/editor remains active:')
    summary = {'checkedAt': now(), 'existingAttempt': True, 'rawRecordSha256': digest, 'archive': str(directory.resolve()),
               'unchangedReusableParagraphs': len(takes), 'finalVoiceExists': context['VOICE'].exists(),
               'resourceDeferred': deferred, 'reason': record.get('error'), 'rawAttemptRecordUnmodified': True,
               'sameScriptAsCurrent': current_script_matches,
               'restartPerformed': False, 'foreignProcessesTerminated': False}
    if deferred:
        state_path = context['LOCAL'] / 'finite-pipeline-v1/state.json'
        if state_path.exists():
            state = read(state_path); old = state['stages'].get('voice')
            if old and old.get('status') != 'deferred':
                state.setdefault('history', []).append({'stage': 'voice', 'record': old.copy(), 'classificationCorrection': 'Exact ended TTS record identifies newly opened user game.'})
                old.update(status='deferred', resourceReason=record['error'], preservedAttemptSha256=digest,
                           completedRawParagraphs=len(takes), finalVoiceGenerated=context['VOICE'].exists())
                state.update(status='deferred', currentStage='voice', updatedAt=now())
                state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        checkpoint_path = project / 'production/checkpoint.json'; checkpoint = read(checkpoint_path)
        checkpoint.update(status='waiting-for-game-exit', resourceDeferred=summary, actualVoiceGenerated=False,
                          actualFullListening='pending', finalVideoGenerated=False, platformActions=False)
        checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (directory / 'preservation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('slug'); args = parser.parse_args()
    print(json.dumps(preserve(args.slug), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
