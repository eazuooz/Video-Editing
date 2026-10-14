"""CPU-only current mix recognition; full outputs require direct human/agent review."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
import importlib.util, traceback
from pathlib import Path
import soundfile as sf
import psutil
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD = m.ROOT, m.PROD
plan_path = PROD / 'measured-native-timeline-candidate-v15.json'
settings_path = PROD / 'review-mix-settings-v15.json'
plan, settings = m.read(plan_path), m.read(settings_path)
mix = ROOT / settings['wav']
assert m.sha(mix) == settings['wavSha256'] and settings['planSha256'] == m.sha(plan_path)
assert m.read(PROD / 'review-mix-execution-v15.json')['exitCode'] == 0
assert m.read(PROD / 'explanation-framing-execution-v15.json')['exitCode'] == 0
assert sf.info(mix).frames == plan['totals']['finalFrames'] * 800
observation = m.resources()
slots = plan['slots']
chapters = list(dict.fromkeys(s['scene'] for s in slots))
def expected(parts):
    texts, seen = [], set()
    for s in parts:
        key = s.get('originalIndex', s['id'])
        if key in seen: continue
        seen.add(key); texts.append(s['text'])
    return texts
windows = []
for scene in chapters:
    parts = [s for s in slots if s['scene'] == scene]
    windows.append(dict(label='whole-' + scene, scene=scene, mode='whole-chunked-30-stride5',
                        fromFrame=parts[0]['fromFrame'], toFrame=parts[-1]['toFrame'],
                        expectedKo=expected(parts), scope='Entire current mixed chapter, including inserted guides.'))
for scene in chapters:
    parts = [s for s in slots if s['scene'] == scene]
    original_ids = list(dict.fromkeys(s['originalIndex'] for s in parts if s['kind'] == 'original-paragraph'))[-3:]
    first = next(s['fromFrame'] for s in parts if s.get('originalIndex') == original_ids[0])
    context = [s for s in parts if s['fromFrame'] >= first]
    windows.append(dict(label='context-' + scene, scene=scene, mode='independent-sequential-long-form',
                        fromFrame=first, toFrame=parts[-1]['toFrame'], expectedKo=expected(context),
                        scope='Last three complete original paragraphs, with all inserted complete guides between them.'))
for g in [s for s in slots if s['kind'] == 'native-guide']:
    windows.append(dict(label='guide-' + g['id'], scene=g['scene'], mode='independent-sequential-long-form',
                        fromFrame=g['fromFrame'], toFrame=g['toFrame'], expectedKo=[g['text']],
                        scope='Entire complete current guide in the Nimbus mix; all tail samples retained.'))
for left, right in [(31,32),(51,52),(59,60),(63,64),(64,65),(80,81)]:
    first = next(s['fromFrame'] for s in slots if s.get('originalIndex') == left)
    last = max(s['toFrame'] for s in slots if s.get('originalIndex') == right)
    parts = [s for s in slots if first <= s['fromFrame'] < last]
    windows.append(dict(label=f'join-{left:02d}-{right:02d}', scene=parts[0]['scene'],
                        mode='independent-sequential-long-form', fromFrame=first, toFrame=last,
                        expectedKo=expected(parts), scope='Complete neighboring paragraphs at a zero recognized-gap original boundary.'))
assert len(chapters) == 14 and len(windows) == 54
out = ROOT / 'production/research/game-lighting-history/local/review-mixed-asr-v15'
out.mkdir(parents=True, exist_ok=True)
request_path = PROD / 'review-mixed-asr-request-v15.json'
request = dict(preparedAt=m.stamp(), mixSha256=settings['wavSha256'], planSha256=m.sha(plan_path),
               windows=windows, device='cpu', threads=2, expectedTextUsedAsPrompt=False,
               wholeChapters=14, chapterContexts=14, wholeGuideContexts=20, completeJoinContexts=6,
               automaticApproval=False, humanWholeListening='pending', humanPronunciation='pending')
if request_path.exists():
    old = m.read(request_path)
    assert old['mixSha256'] == request['mixSha256'] and old['planSha256'] == request['planSha256'] and old['windows'] == windows
else: m.save(request_path, request)
state_path = PROD / 'review-mixed-asr-execution-v15.json'
if state_path.exists():
    old = m.read(state_path); w = old.get('worker')
    if w and psutil.pid_exists(w['pid']):
        assert abs(psutil.Process(w['pid']).create_time() - w['createTime']) > .01, 'Previous ASR worker alive'
    assert old['status'] != 'complete', 'Completed ASR preserved; do not rerun'
state = dict(startedAt=m.stamp(), status='loading-local-CPU-model', worker=m.worker(), active=None,
             resourceObservation=observation, results=[], total=54, cpuThreads=2, gpuJobs=0,
             mixSha256=settings['wavSha256'], planSha256=m.sha(plan_path),
             expectedTextUsedAsPrompt=False, automaticApproval=False, finalMixedAsrApproved=False,
             humanWholeListening='pending', humanPronunciation='pending')
m.save(state_path, state)
try:
    import numpy as np, torch, torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2); torch.set_num_interop_threads(1)
    model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
                low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
    recognizer = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
    for w in windows:
        dest = out / (w['label'] + '.json')
        if dest.exists():
            row = m.read(dest)
            assert row['mixSha256'] == state['mixSha256'] and row['window'] == w
        else:
            with sf.SoundFile(mix) as source:
                assert source.samplerate == 48000 and source.channels == 2
                source.seek(w['fromFrame'] * 800)
                audio = source.read((w['toFrame'] - w['fromFrame']) * 800, dtype='float32', always_2d=True).mean(axis=1)
            wav = out / (w['label'] + '.wav'); assert not wav.exists(), 'Uncompleted window preserved; inspect before retry'
            sf.write(wav, audio, 48000, subtype='FLOAT')
            state.update(status='transcribing-' + w['label'], currentWindow=w)
            m.save(state_path, state)
            resampled = torchaudio.functional.resample(torch.from_numpy(audio), 48000, 16000).numpy()
            options = dict(generate_kwargs={'language':'korean','task':'transcribe'}, return_timestamps='word')
            if w['mode'].startswith('whole-'): options.update(chunk_length_s=30, stride_length_s=5)
            result = recognizer(dict(raw=resampled, sampling_rate=16000), **options)
            row = dict(completedAt=m.stamp(), mixSha256=state['mixSha256'], planSha256=state['planSha256'],
                       window=w, windowSha256=m.sha(wav), sourceSamples=len(audio), sampleRate=48000,
                       expectedTextUsedAsPrompt=False, text=result['text'], words=result['chunks'],
                       directFullTextCompared=False, wordEndingsAndTimestampsCompared=False,
                       contentApproved=False, humanWholeListening='pending', humanPronunciation='pending')
            m.save(dest, row)
        state['results'].append(dict(label=w['label'], path=m.rel(dest), sha256=m.sha(dest)))
        state['status'] = 'between-windows'; m.save(state_path, state)
        print(m.json.dumps(dict(done=len(state['results']), total=54, label=w['label'], text=row['text']), ensure_ascii=False), flush=True)
    assert m.sha(mix) == state['mixSha256']
    state.update(status='complete', exitCode=0, completedAt=m.stamp(), currentWindow=None)
    m.save(state_path, state)
except BaseException:
    state.update(status='failed', exitCode=1, failedAt=m.stamp(), error=traceback.format_exc())
    m.save(state_path, state)
    raise
