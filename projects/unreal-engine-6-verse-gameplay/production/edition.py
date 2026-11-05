"""Route files for the original report and its separately authored engine comparison."""
from pathlib import Path
import os
import hashlib
import json

PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / "production/local/v1"
EDITION = os.environ.get("UE6_EDITION", "v1")
if EDITION not in {"v1", "engine-comparison-v2"}:
    raise ValueError(f"Unknown UE6 production edition: {EDITION}")
EXTENDED = EDITION == "engine-comparison-v2"
LOCAL = PROJECT / "production/local" / EDITION
SCRIPT = PROJECT / "script/engine-comparison-v2" if EXTENDED else PROJECT / "script"


def voice_dir(scene_id):
    if EXTENDED and int(scene_id) > 12:
        if not 13 <= int(scene_id) <= 17:
            raise ValueError(f"Unexpected comparison scene {scene_id}")
        return LOCAL / "voice"
    return BASE / "voice"


def sealed_voice_batch(voice,stem,ids):
    """Bind final assembly, current chunks and ASR. A provisional take cannot pass."""
    import soundfile as sf
    import numpy as np
    timing_file=voice/(stem+'.timing.json')
    joined_file=voice/(stem+'.wav')
    if not timing_file.exists() or not joined_file.exists():return None
    assembly=json.loads(timing_file.read_text(encoding='utf-8'))
    entries=assembly['entries']
    if [e['scene_id'] for e in entries]!=ids:return None
    rate=assembly['sample_rate']
    evidence={}
    with sf.SoundFile(joined_file) as combined:
        if combined.samplerate!=rate or abs(len(combined)-round(assembly['duration_seconds']*rate))>1:return None
        for e in entries:
            sid=e['scene_id']; chunk=voice/'chunks'/f'{sid}-scene.wav'
            cache=voice/'asr'/f'{sid}.json'
            if not chunk.is_file() or not cache.is_file():return None
            with chunk.open('rb') as f: sha=hashlib.file_digest(f,'sha256').hexdigest()
            if json.loads(cache.read_text(encoding='utf-8'))['audio_sha256']!=sha:return None
            raw,sr=sf.read(chunk,dtype='int16')
            start=round(e['start']*rate);end=round(e['end']*rate)
            if sr!=rate or end-start!=len(raw):return None
            combined.seek(start);joined=combined.read(len(raw),dtype='int16')
            # Qwen applies a 6 ms edge fade to its assembled WAV.
            guard=round(.008*rate)
            if not np.array_equal(raw[guard:-guard],joined[guard:-guard]):return None
            evidence[sid]={'pcmSha256':sha,'samples':len(raw),'sampleRate':rate,'asrMatchesFinalTake':True}
    return evidence
