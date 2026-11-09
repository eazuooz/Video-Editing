"""Finite current-batch audio readiness sync, called only between CPU ASR jobs.

No model, TTS, render, browser, or platform operations. Unknown readback differences
remain pending; only explicit reviewed aliases in review_readbacks are permitted.
"""
from pathlib import Path
import json,hashlib,runpy,traceback,importlib,sys
H=Path(__file__).resolve().parent
L=H/'local/asr-changed'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def signature(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def synchronize(jobs,done,ready):
    final_module=sys.modules.get('asr_final_aac')
    if final_module:
        final_sha=sha(Path(final_module.__file__))
        if getattr(final_module,'_readinessCodeSha',None)!=final_sha:
            final_module=importlib.reload(final_module);final_module._readinessCodeSha=final_sha
    import prepare_final_audio as audio
    audio_code_sha=sha(Path(audio.__file__))
    if getattr(audio,'_readinessCodeSha',None)!=audio_code_sha:
        audio=importlib.reload(audio);audio._readinessCodeSha=audio_code_sha
    source_sha=sha(audio.SOURCE)
    state_path=L/'audio-sync-state.json'
    state=read(state_path)if state_path.exists()else{}
    helper=H/'review_changed_readbacks.py'
    inputs={}
    for j in jobs:
        p=ready(j)
        inputs.setdefault(j['episode'],[]).append({'key':j['key'],'audioSha256':p['audioSha256']if p else None})
    readbacks={}
    for d in done:readbacks.setdefault(d['episode'],[]).append({'sentenceId':d['sentenceId'],'audioSha256':d['audioSha256'],'asrSha256':d['asrSha256']})
    signatures={ep:signature({'takes':v,'readbacks':readbacks.get(ep,[]),'reviewRulesSha256':sha(helper)})for ep,v in inputs.items()}
    fresh_source=state.get('sourceRevisionsSha256')!=source_sha or state.get('audioCodeSha256')!=audio_code_sha
    changed=[ep for ep,sig in signatures.items()if state.get('episodes',{}).get(ep)!=sig]
    if not fresh_source and not changed:return
    try:
        runpy.run_path(str(helper),run_name='__main__')
        clauses=audio.L/'caption-clauses.json'
        if not clauses.exists()or read(clauses)['sourceRevisionsSha256']!=source_sha:
            runpy.run_path(str(H/'build_changed_clauses.py'),run_name='__main__')
        audio.prepare(None if fresh_source else changed)
        audio.align_ready()
        audio.save(state_path,{'sourceRevisionsSha256':source_sha,'audioCodeSha256':audio_code_sha,'episodes':signatures,
            'mode':'Sequential current-batch sync between ASR jobs; no new TTS/render/model',
            'semanticPolicy':'Only exact text and explicitly reviewed spelling aliases; pending differences retained',
            'humanListening':False})
        print('AUDIO READY SYNC',','.join(sorted(inputs)if fresh_source else changed),flush=True)
    except Exception as e:
        # Do not mark an unprepared input signature complete. The next pass retries.
        audio.save(L/'audio-sync-error.json',{'error':repr(e),'traceback':traceback.format_exc(),'sourceRevisionsSha256':source_sha,'episodes':changed})
        print('Audio readiness sync pending:',repr(e),flush=True)
