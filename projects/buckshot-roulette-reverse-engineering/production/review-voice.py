"""Whole-current-audio Korean Whisper review. Default is a no-GPU readiness check.

Root may pass --run after the current TTS/render GPU job exits. The existing
transcribe_reference.py performs one whole recording pass with word timestamps.
Same-audio cached evidence is reused. This creates evidence, never listening QA.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SLUG = PROJECT.name
LOCAL_MODEL = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
if not (LOCAL_MODEL/'model.safetensors').exists():
    # Existing read-only HF snapshot verified on this host; no network fetch or
    # model copy is required. Keep the provider cache intact.
    candidate = Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
    if (candidate/'model.safetensors').exists() and (candidate/'tokenizer.json').exists():
        LOCAL_MODEL = candidate
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalized(text):
    # Only equivalent technical spellings and the four spoken test/file counts.
    # Raw expected/recognized text is always kept beside this comparison.
    text = text.lower()
    for displayed, spoken in [('gdscript', '지디스크립트'), ('godot', '고도'), ('rea', '알이에이'), ('ai', '인공지능')]:
        text = text.replace(displayed, spoken)
    text = re.sub(r'[^가-힣a-z0-9]', '', text)
    for aliases, spoken in [(['3572','삼천오백칠십이'], '삼천오백일흔두'), (['195','백구십오'], '백아흔다섯'), (['374','삼백칠십사'], '삼백일흔네'), (['32','삼십이'], '서른두')]:
        for alias in aliases:
            text = text.replace(alias, spoken)
    return text

def resource_state(allow_idle_editors):
    import psutil
    # Reuse the exact tested selected-project resource classifier, including
    # Windows WDDM GUI rows and verified Unity AssetImportWorker children.
    guard_command = [sys.executable,'-X','utf8',str(PROJECT/'production/render-voice.py'),'--check-resources']
    if allow_idle_editors:
        guard_command.append('--allow-idle-editors')
    subprocess.run(guard_command,cwd=ROOT,check=True,creationflags=CREATE_NO_WINDOW)
    preflight = read(PROJECT/'production/local/audio-v1/resource-preflight.json')
    assert preflight['status'] == 'resource-preflight-passed-no-synthesis'
    me = psutil.Process()
    assert not LEASE.exists(), 'Preserve existing GPU lease; await the current owner.'
    return me, preflight['baselineProcesses'], preflight['gpuSamples']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--kind', choices=['source','mix'], default='source')
    parser.add_argument('--audio', type=Path, help='Required for mix: actual decoded final audio WAV; source defaults to narration.wav')
    parser.add_argument('--allow-idle-editors', action='store_true', help='Same root-coordinated selected-project resource choice as TTS')
    args = parser.parse_args()
    manifest = read(PROJECT/'production/tts-manifest.json')
    folder = ROOT/manifest['tts']['outputDir']
    if args.kind == 'mix' and args.audio is None:
        parser.error('--kind mix requires --audio pointing to the actual decoded final mix')
    audio = args.audio.resolve() if args.audio else folder/'narration.wav'
    audio.resolve().relative_to(ROOT.resolve())
    assert (LOCAL_MODEL/'model.safetensors').exists(), 'Local Whisper model must exist; do not download implicitly.'
    output = folder/'review'/f'{args.kind}-full-asr.txt'
    cache = output.with_suffix('.timestamps.json')
    status = {'kind':args.kind,'audio':str(audio),'model':str(LOCAL_MODEL),'language':'korean','timestamps':'word','audioExists':audio.exists(),'readyToRun':audio.exists(),'gpuLoaded':False,'humanListening':False}
    if not args.run:
        print(json.dumps(dict(status, status='preflight-only'), ensure_ascii=False))
        return
    assert audio.exists(), audio
    auth = read(ROOT/'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][SLUG]
    assert auth['productionAllowedNow'] is True
    audio_sha = digest(audio)
    current_cache = cache.exists() and read(cache).get('audio_sha256') == audio_sha and read(cache).get('language') == 'korean' and read(cache).get('timestampMode') == 'word'
    if not current_cache:
        if cache.exists():
            suffix = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
            for old in [output,cache]:
                if old.exists():
                    old.rename(old.with_name(f'{old.stem}-previous-{suffix}{old.suffix}'))
        me, observed, samples = resource_state(args.allow_idle_editors)
        token = str(uuid.uuid4())
        state = {'schemaVersion':1,'token':token,'project':SLUG,'state':'asr_running','purpose':f'One current whole {args.kind} audio Korean ASR','coordinator':{'pid':me.pid,'createTime':me.create_time()},'startedAt':time.time(),'foreignProcessesPaused':[],'baselineProcesses':observed,'gpuSamples':samples,'rootExplicitInvocation':'--run'+(' --allow-idle-editors' if args.allow_idle_editors else '')}
        LEASE.parent.mkdir(parents=True,exist_ok=True)
        with LEASE.open('x',encoding='utf-8') as handle:
            json.dump(state,handle,ensure_ascii=False,indent=2)
        receipt = folder/'review'/f'{args.kind}-asr-execution.json'
        save(receipt,state)
        try:
            output.parent.mkdir(parents=True,exist_ok=True)
            env = os.environ.copy()
            env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
            command = [str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'qwen3-tts/transcribe_reference.py'),str(audio),'--output',str(output),'--model',str(LOCAL_MODEL),'--language','korean','--device','cuda','--timestamps','word']
            with output.with_suffix('.log').open('w',encoding='utf-8') as log:
                completed = subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE_NO_WINDOW)
            if completed.returncode:
                raise RuntimeError(f'Whole audio ASR failed ({completed.returncode}); inspect {output.with_suffix(".log")}')
            state.update(state='finished',exitCode=0,finishedAt=time.time(),audioSha256=audio_sha)
        except BaseException as error:
            state.update(state='failed',error=repr(error),finishedAt=time.time())
            raise
        finally:
            save(receipt,state)
            # Child has fully exited, so no ASR model retains GPU allocations.
            if LEASE.exists() and read(LEASE).get('token') == token:
                LEASE.unlink()
    cached = read(cache)
    assert cached['audio_sha256'] == audio_sha
    script = read(ROOT/manifest['paths']['script'])
    expected = ' '.join(line for scene in script['scenes'] for line in scene['lines'])
    recognized = cached['text']
    a,b = normalized(expected),normalized(recognized)
    matcher = difflib.SequenceMatcher(None,a,b,autojunk=False)
    differences = [{'kind':kind,'expected':a[i:j],'recognized':b[k:l],'expectedCharacterRange':[i,j],'recognizedCharacterRange':[k,l]} for kind,i,j,k,l in matcher.get_opcodes() if kind!='equal']
    report = {'kind':args.kind,'audioSha256':audio_sha,'scriptSha256':digest(ROOT/manifest['paths']['script']),'wholeCurrentAudioAsr':True,'cacheReused':current_cache,'language':'korean','expected':expected,'recognized':recognized,'similarity':matcher.ratio(),'differences':differences,'reviewStatus':'pending direct full-text reading and listening of flagged ranges','humanListening':False,'paceVerified':False}
    save(folder/'review'/f'{args.kind}-text-comparison.json',report)
    print(json.dumps({'status':'current-whole-asr-ready-for-review','kind':args.kind,'similarity':matcher.ratio(),'differences':len(differences),'audioSha256':audio_sha,'humanListening':False},ensure_ascii=False))

if __name__ == '__main__':
    main()
