"""Fixed06.02 V2 blind ASR adapter for103physical/96logical units; the approved recognizer library is unchanged.

Default is read-only. Model execution, CPU level review and child CLI are the
existing explicit flags. The exact completed103-take/25-paragraph voice must be
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
PROTOCOL = 'architectural111-06-02-voice-asr-v2'
OWNER = 'architectural-111-06-02-asr-v2'
MEDIA = qa.MEDIA
PROOF = MEDIA / '06-02-voice-evidence.json'
VOICE_STATE = MEDIA / '06-02-voice-progress.json'
STATE = MEDIA / '06-02-asr-v2-progress.json'
WORKER = MEDIA / '06-02-asr-v2-worker.json'
COMPONENT_PLAN = ROOT / 'projects' / SLUG / 'voice-semantic-components-v3.json'
Pending = qa.Pending
PROFILE = qa.PROFILE
MODEL = qa.MODEL


SPLIT_LOGICAL_IDS={'p004-c04','p011-c01','p013-c01','p018-c02','p022-c03','p024-c02','p025-c03'}

def component_groups(draft, plan, narration_sha):
    """Independent exact103physical/96logical source-char/prosody validation."""
    ko=draft.get('narrationKo',[])
    if draft.get('topicId')!='06.02' or len(ko)!=25 or len(draft.get('paragraphsEn',[]))!=25 or plan.get('topicId')!='06.02' or plan.get('sourceNarrationSHA256')!=narration_sha:
        raise Pending('Current exact25paragraph103component source binding required')
    paragraphs=plan.get('paragraphs',[]);logical=plan.get('logicalGroups',[])
    if len(paragraphs)!=25 or [r.get('paragraph')for r in paragraphs]!=list(range(1,26)) or len(logical)!=96:
        raise Pending('Exactly25orderedphysical paragraphs/96logical groups required')
    groups={};parts_by_id={};physical_order=[]
    for n,row in enumerate(paragraphs,1):
        components=row.get('components',[]);cursor=0
        if len(components)<2:raise Pending('Explicit physical components required in every paragraph')
        for j,item in enumerate(components,1):
            text=item.get('text');sid=f'p{n:03}-c{j:02}'
            if not isinstance(text,str)or not text or text!=text.strip()or not str(item.get('reason','')).strip():raise Pending('Exact nonempty physical text and reason required')
            end=cursor+len(text)
            if ko[n-1][cursor:end]!=text or item.get('sourceCharRange')!=[cursor,end]or item.get('physicalSceneId')!=sid:raise Pending('Physical scene/text/paragraph-char range differs')
            parts_by_id[sid]=dict(item,paragraph=n);physical_order.append(sid);cursor=end+1
        if ' '.join(i['text']for i in components)!=ko[n-1]:raise Pending('Physical components omit/repeat/change canonical prose')
        groups[n]=components
    if len(physical_order)!=103 or len(parts_by_id)!=103:raise Pending('Exactly103unique sequential physical units required')
    used=[];split=set();previous=(0,-1);logical_cursor={n:0 for n in range(1,26)}
    for g in logical:
        n=g.get('paragraph');index=g.get('logicalSentenceIndexZeroBased');sid=g.get('logicalSceneId');ids=g.get('physicalSceneIds',[]);text=g.get('canonicalText')
        if type(n)is not int or not 1<=n<=25 or type(index)is not int or index<0 or (n,index)<=previous or sid!=f'p{n:03}-c{index+1:02}':raise Pending('Logical96IDs/order/index differs')
        if previous[0]==n and index!=previous[1]+1 or previous[0]!=n and index!=0:raise Pending('Logical sentence index gap')
        previous=(n,index)
        if len(ids)not in(1,2)or any(i not in parts_by_id for i in ids)or g.get('canonicalInterComponentJoiner')!=' ':raise Pending('Logical group must contain one/two exact ordered physical units')
        if g.get('id')!=sid or g.get('groupId')!=f'P{n}{chr(97+index)}'or g.get('beatId')!=f'06.02-P{n:02}-S{index+1:02}':raise Pending('Stable logical group/beat identifiers differ')
        parts=[parts_by_id[i]for i in ids];span=[parts[0]['sourceCharRange'][0],parts[-1]['sourceCharRange'][1]]
        if any(p['paragraph']!=n for p in parts)or g.get('sourceCharRange')!=span or span[0]!=logical_cursor[n]or text!=' '.join(p['text']for p in parts)or ko[n-1][span[0]:span[1]]!=text:raise Pending('Logical group does not exactly reconstruct physical/source text')
        for j,p in enumerate(parts,1):
            if p.get('logicalSceneId')!=sid or p.get('logicalSentenceIndexZeroBased')!=index or p.get('logicalPartIndex')!=j or p.get('logicalPartCount')!=len(parts):raise Pending('Physical/logical cross mapping differs')
            if p.get('logicalSourceCharRange')!=[p['sourceCharRange'][0]-span[0],p['sourceCharRange'][1]-span[0]]or p.get('canonicalJoinerAfter')!=(' 'if j<len(parts)else''):raise Pending('Exact logical part character/joiner mapping differs')
        expected_parts=[dict(physicalSceneId=ids[j],sourceCharRange=p['sourceCharRange'],logicalSourceCharRange=p['logicalSourceCharRange'],logicalPartIndex=j+1)for j,p in enumerate(parts)]
        if g.get('physicalParts')!=expected_parts:raise Pending('Logical physicalParts metadata differs from exact components')
        if len(parts)==2:
            split.add(sid)
            if not parts[0]['text'].endswith(',')or parts[1]['sourceCharRange'][0]!=parts[0]['sourceCharRange'][1]+1:raise Pending('Only authored complete comma-clause boundary can split a logical sentence')
        logical_cursor[n]=span[1]+1;used+=ids
    if used!=physical_order or split!=SPLIT_LOGICAL_IDS or any(logical_cursor[n]!=len(ko[n-1])+1 for n in range(1,26)):raise Pending('Exact seven approved splits and whole103/96/25source coverage required')
    return groups,logical

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
    if len(proof.get('identity',{}).get('scenes',[]))!=103 or len(proof.get('paragraphMapping',[]))!=103:
        raise Pending('Waiting for exact completed103physical-component voice; previous96 proof remains preserved')
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
    narration = ROOT / 'projects' / SLUG / 'narration-expanded-draft-v4.json'
    draft, components = qa.read(narration), qa.read(COMPONENT_PLAN)
    declared = Path(components.get('sourceNarrationPath',''))
    if not declared.is_absolute():declared=ROOT/declared
    if declared.resolve()!=narration.resolve():raise ValueError('103 source plan must name the selected immutable V4 narration')
    groups, logical = component_groups(draft, components, qa.sha(narration))
    expected_script, expected_mapping = qa.voice.prep.make_scenes(draft, groups)
    scenes, mapping = identity['scenes'], proof['paragraphMapping']
    if (len(draft['narrationKo']) != 25 or len(draft['paragraphsEn']) != 25 or len(scenes) != 103 or
        scenes != [{'id': s['id'], 'lines': s['lines']} for s in expected_script['scenes']] or
        mapping != expected_mapping):
        raise ValueError('Current103physical/96logical/25-paragraph mapping differs')
    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing['entries'], 0, hashlib.sha256()
    if len(entries) != len(scenes) or len(proof['sceneWavs']) != len(scenes):
        raise ValueError('Variable take count differs')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / f'{scene["id"]}-scene.wav' or
            entry['scene_id'] != scene['id'] or entry['text'] != ' '.join(scene['lines'])):
            raise ValueError('Exact raw scene/time/text binding differs')
        if (abs(entry['start'] - position / 24000) > 1e-9 or
            abs(entry['end'] - (position + wav['frames']) / 24000) > 1e-9):
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
    job['identity']['physicalComponentCount']=103
    job['identity']['logicalGroupCount']=96
    job['identity']['semanticPlan']=qa.pin(COMPONENT_PLAN)
    job['fingerprint'] = qa.digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['sourcePins'].append(dict(path=str(BASE_PATH), sha256=BASE_SHA))
    job['sourcePins'].append(qa.pin(COMPONENT_PLAN))
    job['sourcePins'].append(qa.pin(ROOT/'projects'/SLUG/'narration-expanded-draft-v4.json'))
    return job


def child_processes():
    found = []
    names = {Path(__file__).name, BASE_PATH.name, 'run-prospect-refuge-voice-qa.py'}
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
