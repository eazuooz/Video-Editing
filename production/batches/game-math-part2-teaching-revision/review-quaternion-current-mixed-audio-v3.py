"""Read every complete current final-AAC scene on CPU; no automatic approval."""
from pathlib import Path
from datetime import datetime
import argparse, ctypes, hashlib, json, os, subprocess, traceback

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = B / 'cross-game-review-20261011/quaternion-four-game-v3'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()
def now(): return datetime.now().astimezone().isoformat()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('slug', choices=['game-math-quaternion-foundations-v3','game-math-quaternion-calculations-v3'])
    args = p.parse_args()
    P = ROOT/'projects'/args.slug
    m = read(P/'project.json'); t = read(P/'production/timeline.json')
    script = read(P/'script/narration.ko.json')
    source = ROOT/m['paths']['videoClean']
    digest = sha(source); plan_digest = sha(P/'production/timeline.json')
    assert source.exists() and t['ratioErrorFrames'] == 0
    assert not m['lecture']['backgroundMusic']
    O = ROOT/'shared/output'/args.slug/'mixed-asr-v3'
    O.mkdir(parents=True, exist_ok=True)
    state_path = R/(args.slug+'-mixed-asr-v3-execution.json')
    import psutil
    resources = {'cpuPercent':psutil.cpu_percent(interval=1), 'availableMemory':psutil.virtual_memory().available}
    assert resources['availableMemory'] > 8_000_000_000 and resources['cpuPercent'] < 90
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']: os.environ[key] = '2'
    os.environ.update(CUDA_VISIBLE_DEVICES='', TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    if os.name == 'nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    worker = psutil.Process()
    state = {'startedAt':now(), 'pid':worker.pid, 'createTime':worker.create_time(),
             'command':worker.cmdline(), 'cwd':str(ROOT), 'source':source.relative_to(ROOT).as_posix(),
             'sha256':digest, 'timelineSha256':plan_digest, 'resources':resources,
             'cpuThreads':2, 'gpuJobs':0, 'researchControlsModified':0,
             'status':'decode-current-AAC', 'completed':0, 'total':len(t['scenes']),
             'expectedTextUsedAsPrompt':False, 'automaticApproval':False,
             'humanListening':'pending', 'fullDirectComparisonComplete':False, 'exitCode':None}
    def save(): state['updatedAt']=now(); write(state_path, state)
    save()
    try:
        import soundfile as sf
        decoded = O/'current-final-aac.wav'; receipt = O/'decoded.json'
        if not receipt.exists() or read(receipt).get('sourceSha256') != digest:
            subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-v','error','-threads','2','-i',str(source),
                            '-map','0:a:0','-ac','2','-ar','48000','-c:a','pcm_s16le',str(decoded)], check=True)
            write(receipt, {'sourceSha256':digest, 'decodedSha256':sha(decoded)})
        assert sha(decoded) == read(receipt)['decodedSha256']
        texts = {s['id']:s['lines'] for s in script['scenes']}
        recognizer = None; rows = []
        # Prioritize the newly inserted passages so their current final-AAC
        # words can guide direct scene review while all retained scenes finish.
        for slot in sorted(t['scenes'], key=lambda row: bool(row['preservedOriginal'])):
            ident = slot['id']; dest = O/(ident+'.json')
            start = round(slot['start']*48000); count = slot['frames']*800
            with sf.SoundFile(decoded) as f:
                assert f.samplerate == 48000 and f.channels == 2
                f.seek(start); pcm = f.read(count, dtype='float32', always_2d=True)
            assert len(pcm) == count
            pcm_digest = hashlib.sha256(pcm.tobytes()).hexdigest()
            cached = read(dest) if dest.exists() else {}
            if cached.get('finalAudioPcmSliceSha256') != pcm_digest:
                if recognizer is None:
                    state['status']='loading-local-CPU2-model'; save()
                    import torch
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                    torch.set_num_threads(2); torch.set_num_interop_threads(1)
                    modelpath = ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
                    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath), dtype=torch.float32,
                      low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
                    proc = AutoProcessor.from_pretrained(str(modelpath), local_files_only=True)
                    recognizer = pipeline('automatic-speech-recognition', model=model, tokenizer=proc.tokenizer,
                      feature_extractor=proc.feature_extractor, dtype=torch.float32, device='cpu')
                wav = O/(ident+'.wav'); sf.write(wav, pcm, 48000, subtype='PCM_16')
                state.update(status='transcribing-complete-final-scene', activeScene=ident); save()
                raw = recognizer(str(wav), generate_kwargs={'language':'korean','task':'transcribe'},
                                 chunk_length_s=30, stride_length_s=5, return_timestamps='word')
                cached = {'scene':ident, 'expectedKo':texts[ident], 'text':raw['text'], 'words':raw['chunks'],
                          'finalAudioPcmSliceSha256':pcm_digest, 'fromSample':start, 'samples':count,
                          'wavSha256':sha(wav), 'expectedTextUsedAsPrompt':False, 'directlyCompared':False}
                write(dest, cached)
            assert cached['expectedKo'] == texts[ident]
            rows.append(cached); state['completed']=len(rows); save()
            print('Complete final-AAC scene read back:', ident, flush=True)
        assert sha(source) == digest and sha(P/'production/timeline.json') == plan_digest
        write(O/'all-scenes.json', {'source':state['source'], 'sha256':digest, 'timelineSha256':plan_digest,
              'complete':True, 'scenes':rows, 'fullDirectComparisonComplete':False, 'humanListening':'pending'})
        state.update(status='completed-await-full-direct-comparison', exitCode=0, finishedAt=now(), activeScene=None); save()
    except Exception:
        state.update(status='failed', exitCode=1, error=traceback.format_exc(), finishedAt=now()); save(); raise

if __name__ == '__main__': main()
