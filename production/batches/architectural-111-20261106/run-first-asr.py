"""Finite blind ASR of exact first03.02 PCM. Never synthesizes or edits audio."""
from __future__ import annotations
import argparse, copy, difflib, hashlib, importlib.util, json, os, re, subprocess, sys, time, unicodedata, uuid
from pathlib import Path
import psutil
from initialize import HERE, ROOT, MEDIA, AUTH_KEY, read, save


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


voice=module('asr_first_voice_tools',HERE/'run-first-voice.py');native=voice.native
SLUG='shorts-leveldesign-03-02';PROJECT=ROOT/'projects'/SLUG
PROOF=MEDIA/'first-voice-evidence.json';VOICE_STATE=MEDIA/'first-voice-progress.json'
STATE=MEDIA/'first-asr-progress.json';WORKER=MEDIA/'first-asr-worker.json'
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
TRUSTED=ROOT/'production/batches/game-math-remaining-20261104/review-source-voice.py'
MODEL=Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
GUARD=ROOT/'qwen3-tts/gpu_handoff_guard.py'
PROFILE=dict(model='whisper-large-v3-turbo',device='cuda',dtype='float16',attention='eager',
             minimumFreeMiB=9216,allocationCapGiB=7,language='korean',task='transcribe',
             timestamps='word',chunkLengthSeconds=28,strideLengthSeconds=4,boundaryRadiusSeconds=4,
             expectedPrompt=None,hotwords=None,aliases=None)
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)


class Pending(RuntimeError):pass


class PreModelResourceDeclined(Pending):
    def __init__(self,reason,origin):
        super().__init__(reason);self.origin=origin


class ResourceRetry(Pending):
    def __init__(self,record):
        super().__init__(record['reason']);self.record=record


def acquire_guard_before_model(guard):
    # The existing guard remains the sole lease owner. If its last-moment lease
    # race would wait, return to the finite parent instead of blocking past its
    # deadline. Do not alter the shared time module or any foreign lease.
    original_time=guard.time
    class FiniteGuardTime:
        def __getattr__(self,name):return getattr(original_time,name)
        def sleep(self,seconds):
            raise PreModelResourceDeclined('The existing GPU guard deferred this job before model load','existing-guard-wait')
    guard.time=FiniteGuardTime()
    try:
        guard.schedule_gpu_handoff(SLUG,'cuda:0',False,9216)
    except SystemExit as error:
        message=str(error.code)
        known=(message.startswith('GPU capacity is insufficient for this profile:') or
            message=='Unregistered GPU activity is present. Inspect its safe completion/resume interface before GPU TTS; current work was preserved.' or
            message=='GPU is reserved for a cooperative training/TTS handoff. Preserve this narration checkpoint and wait for the lease to finish.')
        if known:raise PreModelResourceDeclined(message,'existing-guard-resource-decline') from error
        raise  # Unknown stale ownership, guard defects and coordinator failures are real errors.
    finally:guard.time=original_time


def recognize_entry(path,decline_path):
    try:
        recognize_job(path);return 0
    except PreModelResourceDeclined as error:
        job=read(path);destination=Path(decline_path).resolve() if decline_path else None
        assert destination is not None and destination.parent==Path(job['output']).resolve()
        assert destination.name.startswith('resource-decline-') and destination.suffix=='.json'
        record=dict(protocol='architectural111-first-asr-resource-decline-v1',fingerprint=job['fingerprint'],
            temporary=True,phase='before-model',modelLoaded=False,origin=error.origin,reason=str(error),checkedAt=time.time())
        save(destination,record);print(json.dumps(record,ensure_ascii=False),flush=True);return 75


def accept_child_exit(code,decline_path,job,log_path):
    if code==0:return
    if code==75 and Path(decline_path).exists():
        record=read(decline_path)
        assert (record.get('protocol')=='architectural111-first-asr-resource-decline-v1'
            and record.get('fingerprint')==job['fingerprint'] and record.get('phase')=='before-model'
            and record.get('temporary') is True and record.get('modelLoaded') is False),'Invalid temporary-decline receipt'
        raise ResourceRetry(record)
    raise RuntimeError(f'ASR child failed with exit {code}; inspect preserved log {log_path}. Model/recognition errors are not retried as resource waits.')


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def folded(text):
    # Diagnostic formatting-only view. No phonetic, spelling, acronym or word aliases.
    return re.sub(r'[^가-힣A-Za-z0-9]','',unicodedata.normalize('NFC',text)).lower()


def comparison(expected,recognized):
    a,b=folded(expected),folded(recognized)
    chars=difflib.SequenceMatcher(None,a,b,autojunk=False)
    words=difflib.SequenceMatcher(None,expected.split(),recognized.split(),autojunk=False)
    return dict(expectedLiteral=expected,recognizedLiteral=recognized,rawCharacterSimilarity=chars.ratio(),
        characterDifferences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in chars.get_opcodes() if t!='equal'],
        wordDifferences=[dict(kind=t,expected=expected.split()[i:j],recognized=recognized.split()[k:l]) for t,i,j,k,l in words.get_opcodes() if t!='equal'],
        normalization='NFC, punctuation/spacing removal, Latin case only; raw literal strings retained',
        aliasesApplied=False,automaticSpeechPass=False,humanListening=False)


def exact_voice():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘' and control['status'] not in ('paused','stopped','cancelled')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']
    if not PROOF.exists() or not VOICE_STATE.exists():raise Pending('Waiting for exact completed first-voice evidence')
    state=read(VOICE_STATE);evidence=read(PROOF)
    if not state.get('completed') or native.alive(state.get('child')):raise Pending('Qwen child/evidence is not finished')
    manifest=read(PROJECT/'voice-manifest.json');output=(ROOT/manifest['tts']['outputDir']).resolve()
    assert output==voice.OUTPUT.resolve(),'First ASR output scope changed'
    receipt=read(output/'voice-inputs.json');identity=receipt['identity']
    assert receipt['fingerprint']==evidence['fingerprint']==state['fingerprint']
    scenes=identity['scenes'];ids=[s['id'] for s in scenes];texts=[' '.join(s['lines']) for s in scenes]
    assert ids==[f's{i:02}' for i in range(1,7)]
    assert texts==[s.strip() for s in read(PROJECT/'narration-draft.json')['narrationKo']],'Selected spoken text changed'
    prov=dict(fingerprint=receipt['fingerprint'],identity=identity,sceneIds=ids,spokenLines=texts,
              sceneGapSeconds=float(identity['tts']['sceneGapSeconds']),audit=evidence['audit'])
    actual=voice.verify_voice(prov)
    assert actual['aggregateWav']['sha256']==evidence['aggregateWav']['sha256']
    assert actual['aggregateWav']['pcmSHA256']==evidence['aggregateWav']['pcmSHA256']
    assert actual['timing']['sha256']==evidence['timing']['sha256']
    assert [x['sha256'] for x in actual['sceneWavs']]==[x['sha256'] for x in evidence['sceneWavs']]
    return output,evidence,read(output/'narration.timing.json')


def pcm_identity(info):
    """Exact WAV bytes and decoded integer PCM identity; no audio transformation."""
    return {key:info[key] for key in ('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames')}


def archived_file(snapshot,archive,relative):
    # The user/root supplies one exact snapshot receipt. Never search other
    # projects, archives, jobs or models for a recognition that happens to fit.
    relative=Path(relative)
    assert not relative.is_absolute() and '..' not in relative.parts,'Unsafe archived relative path'
    path=(snapshot/relative).resolve()
    assert path.is_relative_to(snapshot) and path.is_file(),'Archived file escaped snapshot or is missing'
    entries=archive['files'];indexed={entry['path']:entry['sha256'] for entry in entries}
    assert len(indexed)==len(entries),'Duplicate archive manifest paths'
    key=relative.as_posix()
    assert key in indexed and voice.sha(path)==indexed[key],f'Archived evidence hash mismatch: {key}'
    return path


def load_reuse_source(job_path,archive_path,new_voice_fingerprint):
    assert bool(job_path)==bool(archive_path),'Reuse requires both exact job and archive-proof paths'
    if not job_path:return None
    path=Path(job_path).resolve();proof=Path(archive_path).resolve()
    preserve=(voice.VOICE_PARENT/'voice-preserved').resolve();snapshot=proof.parent
    assert snapshot.parent==preserve and snapshot!=preserve,'Reuse is limited to one selected first-voice snapshot'
    assert proof.name.startswith('archive-proof-') and proof.suffix=='.json' and proof.is_file(),'Unknown archive receipt'
    assert path.is_relative_to(snapshot),'ASR job is outside the supplied voice snapshot'
    archive=read(proof)
    assert Path(archive['original']).resolve()==voice.OUTPUT.resolve(),'Archive is not selected03.02 voice-v1'
    assert archive['newFingerprint']==new_voice_fingerprint,'Archive is not the predecessor of this voice version'
    archived_file(snapshot,archive,path.relative_to(snapshot))
    old=read(path)
    assert old.get('protocol')=='architectural111-first-asr-v1' and digest(old['identity'])==old['fingerprint'],'Unknown old ASR identity'
    assert Path(old['modelPath']).resolve()==MODEL.resolve(),'Archived model location changed'
    expected_rel=Path('review/independent-asr-v1')/old['fingerprint'][:24]/'job.json'
    assert path.relative_to(snapshot)==expected_rel,'Old ASR job path does not match its own fingerprint'
    assert Path(old['output']).resolve()==(voice.OUTPUT/expected_rel.parent).resolve(),'Old ASR output was outside selected voice'
    assert archive['oldFingerprint']==old['identity']['voiceFingerprint'],'Archive voice fingerprint mismatch'
    receipt=read(archived_file(snapshot,archive,'voice-inputs.json'))
    assert receipt['protocol']==voice.PROTOCOL and receipt['fingerprint']==archive['oldFingerprint'],'Archived voice receipt mismatch'
    assert digest(receipt['identity'])==receipt['fingerprint'],'Archived voice identity changed'
    timing_path=archived_file(snapshot,archive,'narration.timing.json');timing=read(timing_path)
    aggregate=archived_file(snapshot,archive,'narration.wav')
    assert voice.sha(timing_path)==old['identity']['timingSHA256'],'Archived ASR timing changed'
    assert voice.sha(aggregate)==old['identity']['aggregateSHA256'],'Archived aggregate changed'
    scenes=receipt['identity']['scenes'];entries=timing['entries']
    assert [s['id'] for s in scenes]==[f's{i:02}' for i in range(1,7)]
    assert [e['scene_id'] for e in entries]==[s['id'] for s in scenes]
    assert [e['text'] for e in entries]==[' '.join(s['lines']) for s in scenes],'Archived expected literals changed'
    paragraphs=[task for task in old['identity']['tasks'] if task['kind']=='paragraph']
    assert [task['sceneId'] for task in paragraphs]==[e['scene_id'] for e in entries],'Archived paragraph task set changed'
    for task,entry in zip(paragraphs,entries):
        assert task['key']=='paragraph-'+task['sceneId'] and task['expected']==entry['text']
        assert task['offsetSeconds']==float(entry['start'])
        assert abs(task['durationSeconds']-(float(entry['end'])-float(entry['start'])))<2/24000
        expected_audio=(voice.OUTPUT/'chunks'/(task['sceneId']+'-scene.wav')).resolve()
        assert Path(task['path']).resolve()==expected_audio,'Archived scene path left selected voice'
    return dict(snapshot=snapshot,archive=archive,job=old,jobPath=path,proofPath=proof,
        pins=dict(protocol='architectural111-raw-asr-reuse-v1',jobPath=str(path),jobSHA256=voice.sha(path),
                  archiveProofPath=str(proof),archiveProofSHA256=voice.sha(proof),
                  oldVoiceFingerprint=old['identity']['voiceFingerprint'],oldAsrFingerprint=old['fingerprint']))


def checked_reuse_source(job):
    pins=job['identity'].get('reuseSource')
    if not pins:return None
    source=load_reuse_source(pins['jobPath'],pins['archiveProofPath'],job['identity']['voiceFingerprint'])
    assert source['pins']==pins,'Explicit reuse provenance changed'
    old=source['job']['identity'];new=job['identity']
    for key in ('modelPins','trustedUtilitySHA256','profile'):
        assert old[key]==new[key],f'Recognizer {key} differs; raw recognition cannot be reused'
    assert Path(source['job']['modelPath']).resolve()==MODEL.resolve(),'Archived model location changed'
    return source


def prepare_job(reuse_from=None,reuse_archive_proof=None):
    output,evidence,timing=exact_voice()
    model_pins=[dict(path=p.name,sha256=voice.sha(p)) for p in sorted(MODEL.iterdir())
                if p.is_file() and (p.suffix=='.safetensors' or p.name.endswith('.json') or p.name in ('merges.txt','vocab.json'))]
    assert any(p['path']=='model.safetensors' for p in model_pins),'Trusted local ASR weights missing'
    tasks=[]
    for entry,chunk in zip(timing['entries'],evidence['sceneWavs']):
        tasks.append(dict(key='paragraph-'+entry['scene_id'],kind='paragraph',sceneId=entry['scene_id'],
            path=chunk['path'],audioSHA256=chunk['sha256'],pcmIdentity=pcm_identity(chunk),
            offsetSeconds=float(entry['start']),durationSeconds=chunk['durationSeconds'],expected=entry['text']))
    total=evidence['aggregateWav']['durationSeconds']
    for left,right in zip(timing['entries'],timing['entries'][1:]):
        boundary=float(right['start']);start=max(0,boundary-4);end=min(total,boundary+4)
        tasks.append(dict(key='join-'+left['scene_id']+'-'+right['scene_id'],kind='boundary',path=evidence['aggregateWav']['path'],
            audioSHA256=evidence['aggregateWav']['sha256'],offsetSeconds=start,durationSeconds=end-start,
            beginSample=round(start*evidence['aggregateWav']['sampleRate']),endSample=round(end*evidence['aggregateWav']['sampleRate']),
            boundarySeconds=boundary,previousScene=left['scene_id'],nextScene=right['scene_id'],
            expectedContextOnly=dict(previousEnding=' '.join(left['text'].split()[-8:]),nextBeginning=' '.join(right['text'].split()[:8]))))
    identity=dict(voiceFingerprint=evidence['fingerprint'],aggregateSHA256=evidence['aggregateWav']['sha256'],
        timingSHA256=evidence['timing']['sha256'],modelPins=model_pins,trustedUtilitySHA256=voice.sha(TRUSTED),profile=PROFILE,tasks=tasks)
    source=load_reuse_source(reuse_from,reuse_archive_proof,evidence['fingerprint'])
    if source:
        identity['reuseSource']=source['pins']
        for key in ('modelPins','trustedUtilitySHA256','profile'):
            assert source['job']['identity'][key]==identity[key],f'Recognizer {key} differs; refuse reuse'
    fp=digest(identity);folder=output/'review/independent-asr-v1'/fp[:24]
    return dict(protocol='architectural111-first-asr-v1',fingerprint=fp,identity=identity,voiceEvidenceSHA256=voice.sha(PROOF),
                modelPath=str(MODEL),output=str(folder),humanListening=False,pcmModified=False,finalApproval=False)


def words_from_raw(raw,task):
    """Translate unchanged recognizer-relative times into this aggregate timeline."""
    assert isinstance(raw,dict) and isinstance(raw['text'],str)
    words=[];flags=[]
    for chunk in raw.get('chunks',[]):
        start,end=chunk['timestamp']
        if start is None or end is None:flags.append('unknown-word-boundary')
        elif start<0 or end>task['durationSeconds']+.08 or end<start:flags.append('word-timestamp-outside-PCM')
        words.append(dict(text=chunk['text'],timestamp=[None if start is None else task['offsetSeconds']+float(start),
                                                     None if end is None else task['offsetSeconds']+float(end)]))
    return words,sorted(set(flags))


def recognition_record(job,task,raw):
    words,flags=words_from_raw(raw,task)
    data=dict(fingerprint=job['fingerprint'],task=task,text=raw['text'],rawRecognition=copy.deepcopy(raw),
        globalWords=words,boundaryFlags=flags,expectedPrompt=None,aliasesApplied=False,humanListening=False,
        pcmModified=False,device='cuda',recognizer=str(MODEL))
    if task['kind']=='paragraph':data['comparison']=comparison(task['expected'],raw['text'])
    else:data['comparison']=dict(expectedContextOnly=task['expectedContextOnly'],recognizedLiteral=raw['text'],automaticSpeechPass=False,
        warning='Window edges may cut words; review actual paragraph endings/beginnings without trimming PCM.')
    return data


def reusable_paragraph(job,task,source):
    if task['kind']!='paragraph':return None
    matches=[old for old in source['job']['identity']['tasks'] if old['key']==task['key'] and old['kind']=='paragraph']
    assert len(matches)==1,'Archived paragraph key missing or duplicated'
    old_task=matches[0]
    if old_task['expected']!=task['expected'] or old_task['audioSHA256']!=task['audioSHA256']:return None
    assert old_task['sceneId']==task['sceneId']
    old_wav=archived_file(source['snapshot'],source['archive'],'chunks/'+task['sceneId']+'-scene.wav')
    old_pcm=pcm_identity(voice.wav_info(old_wav));new_pcm=pcm_identity(voice.wav_info(task['path']))
    assert old_pcm==new_pcm==task['pcmIdentity'],'Exact scene WAV/PCM identity does not match'
    assert old_pcm['sha256']==old_task['audioSHA256'] and task['durationSeconds']==old_task['durationSeconds']
    if 'pcmIdentity' in old_task:assert old_task['pcmIdentity']==old_pcm
    relative=Path('review/independent-asr-v1')/source['job']['fingerprint'][:24]/(task['key']+'.json')
    old_path=archived_file(source['snapshot'],source['archive'],relative);data=read(old_path)
    assert data['fingerprint']==source['job']['fingerprint'] and data['task']==old_task,'Archived ASR task/result mismatch'
    assert data['expectedPrompt'] is None and data['aliasesApplied'] is False and data['pcmModified'] is False
    assert data['recognizer']==str(MODEL) and data['device']=='cuda','Archived recognition implementation mismatch'
    assert data['text']==data['rawRecognition']['text']
    assert data['comparison']==comparison(old_task['expected'],data['text']),'Archived literal differences changed'
    old_words,old_flags=words_from_raw(data['rawRecognition'],old_task)
    assert data['globalWords']==old_words and data['boundaryFlags']==old_flags,'Archived raw/global timestamps differ'
    receipt=dict(protocol='architectural111-raw-asr-reuse-v1',sourceJobPath=str(source['jobPath']),
        sourceJobSHA256=source['pins']['jobSHA256'],sourceJobFingerprint=source['job']['fingerprint'],
        sourceArchiveProofPath=str(source['proofPath']),sourceArchiveProofSHA256=source['pins']['archiveProofSHA256'],
        sourceResultPath=str(old_path),sourceResultSHA256=voice.sha(old_path),sourceWavPath=str(old_wav),
        pcmIdentity=old_pcm,expectedLiteralSHA256=digest(task['expected']),rawRecognitionSHA256=digest(data['rawRecognition']),
        sourceOffsetSeconds=old_task['offsetSeconds'],destinationOffsetSeconds=task['offsetSeconds'],
        sourceHumanListening=data.get('humanListening'),modelLoadedForThisTask=False,
        boundaryWindowsReused=False,sourceFilesModified=False)
    return data,receipt


def apply_paragraph_reuse(job):
    """Read-only old evidence, new cache files only; all join windows stay fresh."""
    source=checked_reuse_source(job)
    if not source:return []
    assert digest(job['identity'])==job['fingerprint'],'New aggregate ASR identity changed'
    assert Path(job['output']).resolve()==(voice.OUTPUT/'review/independent-asr-v1'/job['fingerprint'][:24]).resolve(),'New cache output escaped selected first voice'
    reused=[]
    for task in job['identity']['tasks']:
        if task['kind']!='paragraph':continue
        candidate=reusable_paragraph(job,task,source)
        if candidate is None:continue
        old,receipt=candidate
        destination=Path(job['output'])/(task['key']+'.json')
        data=recognition_record(job,task,old['rawRecognition']);data['reuse']=receipt
        if destination.exists():
            existing=read_cache(job,task)
            # A freshly recognized same-task result is also valid; never overwrite it.
            if 'reuse' in existing:assert existing==data,'Different reused cache must be preserved'
        else:save(destination,data)
        assert voice.sha(receipt['sourceResultPath'])==receipt['sourceResultSHA256'],'Source result was modified'
        reused.append(task['key'])
    return reused


def read_cache(job,task):
    p=Path(job['output'])/(task['key']+'.json')
    if not p.exists():return None
    data=read(p)
    assert data['fingerprint']==job['fingerprint'] and data['task']==task,'Preserve different ASR evidence'
    assert data['expectedPrompt'] is None and not data['aliasesApplied']
    if 'reuse' in data:
        source=checked_reuse_source(job);assert source is not None,'Reused cache lacks pinned history'
        candidate=reusable_paragraph(job,task,source);assert candidate is not None,'Reused paragraph is no longer identical'
        old,receipt=candidate
        assert data['reuse']==receipt and data['rawRecognition']==old['rawRecognition'],'Reused raw evidence changed'
        expected=recognition_record(job,task,old['rawRecognition']);expected['reuse']=receipt
        assert data==expected,'Reused timeline or literal comparison changed'
    return data


def summary(job):
    records=[read_cache(job,t) for t in job['identity']['tasks']]
    if any(r is None for r in records):return None
    paragraphs=[r for r in records if r['task']['kind']=='paragraph'];joins=[r for r in records if r['task']['kind']=='boundary']
    boundary=[]
    for a,b in zip(paragraphs,paragraphs[1:]):
        previous=[w for w in a['globalWords'] if w['timestamp'][1] is not None]
        following=[w for w in b['globalWords'] if w['timestamp'][0] is not None]
        gap=None if not previous or not following else following[0]['timestamp'][0]-previous[-1]['timestamp'][1]
        boundary.append(dict(previous=a['task']['sceneId'],next=b['task']['sceneId'],recognizedWordGapSeconds=gap,
            conclusion='Timing observation only; distinguish preserved quiet lead/tail from missing words by literal transcript and listening. No trim/retake authorized.'))
    result=dict(status='independent-asr-complete-content-review-pending',fingerprint=job['fingerprint'],voiceFingerprint=job['identity']['voiceFingerprint'],
        aggregateSHA256=job['identity']['aggregateSHA256'],profile=PROFILE,paragraphs=paragraphs,boundaryWindows=joins,boundaryObservations=boundary,
        aliasesApplied=False,expectedPrompt=None,automaticSpeechPass=False,humanListening=False,pcmModified=False,finalApproval=False)
    save(Path(job['output'])/'review.json',result);return result


def resource_reason():
    reason=native.busy_reason()
    if reason:return reason
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
    free,use=map(int,raw.splitlines()[0].split(','))
    return 'Trusted ASR profile requires9GiB idle memory/utilization<15%' if free<9216 or use>=15 else None


def recognize_job(path):
    path=Path(path).resolve();job=read(path)
    assert path.is_relative_to(voice.OUTPUT.resolve()/'review/independent-asr-v1')
    assert digest(job['identity'])==job['fingerprint'] and job['identity']['profile']==PROFILE
    assert path.name=='job.json' and path.parent==Path(job['output']).resolve()
    assert path.parent==(voice.OUTPUT/'review/independent-asr-v1'/job['fingerprint'][:24]).resolve()
    output,evidence,_=exact_voice();assert evidence['aggregateWav']['sha256']==job['identity']['aggregateSHA256']
    for pin in job['identity']['modelPins']:assert voice.sha(MODEL/pin['path'])==pin['sha256']
    assert voice.sha(TRUSTED)==job['identity']['trustedUtilitySHA256']
    apply_paragraph_reuse(job)  # CPU-only proof checks happen before any GPU/model request.
    pending=[t for t in job['identity']['tasks'] if read_cache(job,t) is None]
    if not pending:return
    reason=resource_reason()
    if reason:raise PreModelResourceDeclined(reason,'child-resource-check')
    os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    sys.path.insert(0,str(ROOT/'qwen3-tts'))
    guard=module('first_asr_existing_gpu_guard',GUARD)
    acquire_guard_before_model(guard)  # This child alone owns/releases the existing guard lease.
    trusted=module('trusted_full_paragraph_recognizer',TRUSTED)
    assert trusted.MODEL==MODEL
    recognizer=trusted.load_recognizer('cuda')
    import soundfile as sf
    for task in pending:
        assert voice.sha(task['path'])==task['audioSHA256'],'Exact PCM changed before recognition'
        if task['kind']=='boundary':pcm,sr=sf.read(task['path'],start=task['beginSample'],stop=task['endSample'],dtype='float32')
        else:pcm,sr=sf.read(task['path'],dtype='float32')
        assert pcm.ndim==1
        raw=trusted.recognize(recognizer,pcm,sr)  # No expected text, prompt, prefix or hotwords.
        assert abs(len(pcm)/sr-task['durationSeconds'])<2/sr,'Recognized PCM duration differs from pinned task'
        data=recognition_record(job,task,raw)
        save(Path(job['output'])/(task['key']+'.json'),data)
        print('Recognized',task['key'],flush=True)
    exact_voice()  # Revalidate the same untouched voice proof after the model job.


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-hours',type=float,default=6)
    ap.add_argument('--recognize',action='store_true');ap.add_argument('--job');ap.add_argument('--resource-decline')
    ap.add_argument('--reuse-from',help='Exact job.json in the selected03.02 voice-preserved snapshot (read only)')
    ap.add_argument('--reuse-archive-proof',help='Exact archive-proof JSON beside that snapshot; no directory search')
    args=ap.parse_args()
    assert bool(args.reuse_from)==bool(args.reuse_archive_proof),'Supply both --reuse-from and --reuse-archive-proof'
    prepare=lambda:prepare_job(args.reuse_from,args.reuse_archive_proof)
    if args.recognize:
        assert args.job and not args.reuse_from,'Recognizer reads pinned reuse paths from its exact job'
        raise SystemExit(recognize_entry(args.job,args.resource_decline))
    if not args.execute:
        try:job=prepare();print(json.dumps(dict(ready=True,asrFingerprint=job['fingerprint'],modelLoaded=False,
            explicitReuseSource=job['identity'].get('reuseSource'))))
        except Pending as e:print(json.dumps(dict(ready=False,reason=str(e),modelLoaded=False)))
        return
    worker=native.SingleWorker(WORKER).acquire();worker.update(stage='asr',stageOwner='architectural111-first-asr-v1',topicId='03.02')
    child=None;log=None;state=dict(**native.identity(),stage='asr',topicId='03.02',status='waiting-for-exact-voice',child=None,modelLoadedByWrapper=False)
    try:
        old=read(STATE) if STATE.exists() else {}
        if old.get('pid')!=os.getpid() and (native.alive(old) or native.alive(old.get('child'))):raise RuntimeError('Prior ASR worker/child still active')
        deadline=time.monotonic()+max(0,args.wait_hours)*3600
        while True:
            try:
                job=prepare();folder=Path(job['output']);folder.mkdir(parents=True,exist_ok=True)
                job_path=folder/'job.json'
                if job_path.exists():assert read(job_path)['identity']==job['identity']
                else:save(job_path,job)
                reused=apply_paragraph_reuse(job)
                state['reusedParagraphTasks']=reused
                if summary(job):break
                reason=resource_reason()
                if reason:raise Pending(reason)
                assert prepare()['fingerprint']==job['fingerprint']
                if time.monotonic()>=deadline:raise RuntimeError('Finite ASR wait ended before another model launch; other work preserved')
                attempt_id=uuid.uuid4().hex[:8]
                log_path=folder/('recognition-'+attempt_id+'.log');decline_path=folder/('resource-decline-'+attempt_id+'.json');log=log_path.open('ab')
                child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(Path(__file__).resolve()),'--recognize','--job',str(job_path),'--resource-decline',str(decline_path)],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE)
                ident=native.identity(child.pid);worker.update(child=ident);state.update(status='independent-ASR-running',child=ident,asrFingerprint=job['fingerprint'],job=str(job_path),log=str(log_path))
                save(STATE,state)
                code=child.wait();log.close();log=None
                accept_child_exit(code,decline_path,job,log_path)
                assert prepare()['fingerprint']==job['fingerprint']
                if not summary(job):raise RuntimeError('ASR did not complete every paragraph/boundary window')
                break
            except Pending as e:
                if isinstance(e,ResourceRetry):
                    assert child is not None and child.poll() is not None,'Never clear a live recognizer child'
                    state.setdefault('resourceDeclines',[]).append(dict(child=state.get('child'),receipt=str(decline_path),
                        log=str(log_path),exitCode=75,diagnostic=e.record))
                    child=None;worker.update(child=None)
                    state.update(child=None,childStillAlive=False)
                state.update(status='waiting-for-resources',reason=str(e),checkedAt=time.time());save(STATE,state)
                if time.monotonic()>=deadline:raise RuntimeError('Finite ASR wait ended; other work preserved')
                time.sleep(10)
        state.update(status='independent-asr-complete-content-review-pending',completed=True,review=str(Path(job['output'])/'review.json'),
                     humanListening=False,pcmModified=False,automaticSpeechPass=False)
    except BaseException as error:state.update(status='failed-or-resource-blocked',error=repr(error));raise
    finally:
        live=bool(child and child.poll() is None);state.update(childStillAlive=live,finishedOrYieldedAt=time.time())
        if live:state['status']='asr-worker-yielded-child-still-running'
        save(STATE,state)
        if log:log.close()
        worker.close(remove=not live)
        # GPU lease belongs to the recognizer's existing guard, never this wrapper.


if __name__=='__main__':main()
