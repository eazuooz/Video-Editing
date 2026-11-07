"""Fixed06.02 blind ASR adapter; the approved recognizer library is unchanged.

Default is read-only. Model execution, CPU level review and child CLI are the
existing explicit flags. The exact completed96-take/25-paragraph voice must be
available before a job can be prepared. No synthesis or speech editing.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, os, sys
from pathlib import Path
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_PATH = HERE / 'run-selected-voice-qa.py'
BASE_SHA = '65983206f0e0fa81dd5a5780871605fcc2665816a9f21fc3ea3a43781437e2a9'
if hashlib.sha256(BASE_PATH.read_bytes()).hexdigest() != BASE_SHA:
    raise RuntimeError('Reviewed blind-ASR library changed; inspect before use')
spec = importlib.util.spec_from_file_location('prospect_refuge_pinned_blind_asr', BASE_PATH)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

SLUG = 'shorts-leveldesign-06-02'
TOPIC = '06.02'
PROTOCOL = 'architectural111-06-02-voice-asr-v1'
OWNER = 'architectural-111-06-02-asr'
MEDIA = qa.MEDIA
PROOF = MEDIA / '06-02-voice-evidence.json'
VOICE_STATE = MEDIA / '06-02-voice-progress.json'
STATE = MEDIA / '06-02-asr-progress.json'
WORKER = MEDIA / '06-02-asr-worker.json'
COMPONENT_PLAN = ROOT / 'projects' / SLUG / 'voice-semantic-components-v2.json'
Pending = qa.Pending
PROFILE = qa.PROFILE
MODEL = qa.MODEL


def exact_voice():
    control = qa.read(ROOT / 'shared/publishing/video-production-control.json')[qa.AUTH_KEY]
    if (control['status'] in ('paused', 'stopped', 'cancelled') or
        not control['automaticAdvanceWithinExactList'] or
        control['automaticAdvanceOutsideList'] or not control['humanFinalReviewRequired']):
        raise Pending('Selected finite batch authorization is not active')
    if not PROOF.is_file() or not VOICE_STATE.is_file():
        raise Pending('Waiting for exact completed06.02 voice evidence')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    if not state.get('completed') or qa.voice.alive(state.get('child')) or qa.voice.project_children(SLUG):
        raise Pending('Selected06.02 Qwen voice child/evidence is still active')
    out = Path(proof['output']).resolve()
    expected = (ROOT / 'shared/output/architectural-111-20261106/06-02/voice-attempts').resolve()
    if (proof.get('topicId') != TOPIC or out.parent != expected or
        out.name != proof['fingerprint'][:24] or state.get('fingerprint') != proof['fingerprint']):
        raise ValueError('Wrong selected06.02 voice/output identity')
    identity = proof['identity']
    if qa.digest(identity) != proof['fingerprint']:
        raise ValueError('Voice synthesis identity hash differs')
    current = qa.voice.verify_complete(dict(fingerprint=proof['fingerprint'], identity=identity), out)
    if current is None or any(current[k] != proof[k] for k in ('sceneWavs', 'aggregateWav', 'timing', 'paragraphMapping')):
        raise ValueError('Canonical complete voice proof differs')
    narration = ROOT / 'projects' / SLUG / 'narration-draft.json'
    draft, components = qa.read(narration), qa.read(COMPONENT_PLAN)
    groups = qa.voice.prep.components_for(draft['narrationKo'], components, qa.sha(narration))
    expected_script, expected_mapping = qa.voice.prep.make_scenes(draft, groups)
    scenes, mapping = identity['scenes'], proof['paragraphMapping']
    if (len(draft['narrationKo']) != 25 or len(draft['paragraphsEn']) != 25 or len(scenes) != 96 or
        scenes != [{'id': s['id'], 'lines': s['lines']} for s in expected_script['scenes']] or
        mapping != expected_mapping):
        raise ValueError('Current96 complete-sentence/25-paragraph mapping differs')
    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing['entries'], 0, hashlib.sha256()
    if len(entries) != len(scenes) or len(proof['sceneWavs']) != len(scenes):
        raise ValueError('Variable take count differs')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / f'{scene["id"]}-scene.wav' or
            entry['scene_id'] != scene['id'] or entry['text'] != ' '.join(scene['lines'])):
            raise ValueError('Exact raw scene/time/text binding differs')
        if (abs(entry['start'] - position / 24000) > 1 / 24000 or
            abs(entry['end'] - (position + wav['frames']) / 24000) > 1 / 24000):
            raise ValueError('Canonical take sample boundary differs')
        pcm.update(qa.pcm_bytes(wav['path']))
        position += wav['frames']
    if position != proof['aggregateWav']['frames'] or pcm.hexdigest() != proof['aggregateWav']['pcmSHA256']:
        raise ValueError('Canonical aggregate is not exact selected raw concatenation')
    return out, proof, timing, draft


_library_prepare_job = qa.prepare_job


def prepare_job():
    job = copy.deepcopy(_library_prepare_job())
    job['identity']['pinnedSelectedAsrLibrarySHA256'] = BASE_SHA
    job['fingerprint'] = qa.digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['sourcePins'].append(dict(path=str(BASE_PATH), sha256=BASE_SHA))
    return job


def child_processes():
    found = []
    names = {Path(__file__).name, BASE_PATH.name}
    for process in qa.psutil.process_iter(['pid', 'cmdline']):
        try:
            args = process.info['cmdline'] or []
            if process.pid != os.getpid() and '--recognize' in args and any(Path(a).name in names for a in args):
                found.append(qa.voice.identity(process.pid))
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied:
            raise Pending('Possible recognizer child cannot be inspected; preserve it')
    return found


# Isolated module context: child launches and source pins refer to THIS adapter.
# The old07 source file and any running07 module/process are never changed.
qa.SLUG, qa.TOPIC, qa.PROTOCOL, qa.OWNER = SLUG, TOPIC, PROTOCOL, OWNER
qa.PROOF, qa.VOICE_STATE, qa.STATE, qa.WORKER = PROOF, VOICE_STATE, STATE, WORKER
qa.raw.SLUG = SLUG
qa.runtime.PROTOCOL, qa.runtime.OWNER = PROTOCOL, OWNER
qa.__file__ = str(Path(__file__).resolve())
qa.exact_voice, qa.prepare_job, qa.child_processes = exact_voice, prepare_job, child_processes
summary, cached, raw_level_review = qa.summary, qa.cached, qa.raw_level_review
sha, digest, pin = qa.sha, qa.digest, qa.pin

if __name__ == '__main__':
    qa.main()
