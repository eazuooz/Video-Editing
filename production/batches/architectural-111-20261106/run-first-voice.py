"""Finite voice worker for architectural111 topic03.02 only; Qwen owns its lease."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, time, uuid, wave
from pathlib import Path
import psutil
from initialize import HERE, ROOT, MEDIA, AUTH_KEY, read, save

spec=importlib.util.spec_from_file_location('architectural_first_native',HERE/'run-first-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
SLUG='shorts-leveldesign-03-02'
PROTOCOL='architectural111-first-voice-v1'
PROJECT_DIR=ROOT/'projects'/SLUG
MANIFEST=PROJECT_DIR/'voice-manifest.json'
NARRATION=PROJECT_DIR/'narration-draft.json'
QA=PROJECT_DIR/'native-visual-qa-v1.json'
NATIVE_EVIDENCE=HERE/'first-native-evidence.json'
ENGINE=ROOT/'qwen3-tts/render_narration.py'
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
VOICE_PARENT=ROOT/'shared/output/architectural-111-20261106/03-02'
OUTPUT=VOICE_PARENT/'voice-v1'
STATE=MEDIA/'first-voice-progress.json'
WORKER=MEDIA/'first-voice-worker.json'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
_HASH_CACHE={}


class PreparationPending(RuntimeError): pass


def sha(path):
    path=Path(path);s=path.stat();key=(str(path.resolve()),s.st_size,s.st_mtime_ns)
    if key not in _HASH_CACHE:
        with path.open('rb') as f:_HASH_CACHE[key]=hashlib.file_digest(f,'sha256').hexdigest()
    return _HASH_CACHE[key]


def repo_path(value):
    path=(ROOT/value).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise ValueError('Voice input escapes repository')
    return path


def synthesis_identity(scenes,tts,editing,model_pins,reference_sha,reference_text_sha):
    # Labels, full-manifest hashes, visual/native evidence and scheduling are audit only.
    profile_keys=('engine','language','renderMode','lineGapSeconds','sceneGapSeconds','tailRatioThreshold',
                  'tailDecayMsThreshold','maxRenderAttempts','maxNewTokens','edgeFadeSeconds','paragraphLevelNormalization')
    profile={k:tts[k] for k in profile_keys if k in tts}
    for key in ('lineGapSeconds','sceneGapSeconds','tailRatioThreshold','tailDecayMsThreshold','edgeFadeSeconds'):
        if key in profile:profile[key]=float(profile[key])
    for key in ('maxRenderAttempts','maxNewTokens'):
        if key in profile:profile[key]=int(profile[key])
    semantic=dict(protocol=PROTOCOL,scenes=[dict(id=s['id'],lines=[x.strip() for x in s['lines'] if x.strip()]) for s in scenes],
        tts=profile,modelPins=model_pins,
        referenceSHA256=reference_sha,referenceTextSHA256=reference_text_sha,
        editing=dict(exampleSeconds=float(editing.get('exampleSeconds',0)),narrationPlacement=editing.get('narrationPlacement')))
    fp=hashlib.sha256(json.dumps(semantic,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    return dict(fingerprint=fp,identity=semantic)


def preparation():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘'
    assert control['status'] not in ('paused','cancelled','stopped')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']
    batch=read(HERE/'batch.json');assert batch['localFinalReviewOnly'] and len(batch['projects'])==111
    assert native.sha(ROOT/batch['sourceCatalog'])==batch['sourceCatalogSHA256']
    assert any(x['topicId']=='03.02' and x['slug']==SLUG for x in batch['projects'])
    if not QA.exists():raise PreparationPending('Native sample/mobile QA file has not been delivered')
    qa=read(QA)
    if qa.get('voicePreparationAllowed') is not True:raise PreparationPending('Native geometry/sample/mobile QA has not allowed voice preparation')
    evidence=read(NATIVE_EVIDENCE);native_pin=native.authorize()['fingerprint']
    if evidence['fingerprint']!=native_pin or qa.get('nativeFingerprint',qa.get('fingerprint'))!=native_pin:
        raise PreparationPending('Native QA is not bound to the current native fingerprint')
    if qa.get('nativeEvidenceSHA256') and qa['nativeEvidenceSHA256']!=sha(NATIVE_EVIDENCE):
        raise PreparationPending('Native QA evidence hash is stale')
    for mode,expected in evidence['traceSHA256'].items():
        assert sha(Path(evidence['output'])/mode/'trace.csv')==expected,'Native trace changed'
    assert evidence['narrowLast']['blocked']=='1' and evidence['wideLast']['blocked']=='0'
    sources=read(PROJECT_DIR/'source-footage.json')
    selected=[x for x in sources['sources'] if x.get('selectedForCut')]
    assert selected,'No verified independent gameplay selected'
    footage=[]
    for item in selected:
        assert item['rightsReviewed'] and item['decodedDimensionsVerified'] and item['visualSequenceInspected']
        assert item['width']>=1080 and item['height']>=1080 and item['editorialRole']=='independent-gameplay'
        assert sha(item['path'])==item['sha256'],'Selected source footage changed'
        footage.append(dict(id=item['id'],sha256=item['sha256']))
    additional=read(PROJECT_DIR/'additional-footage-search-v1.json')['source']
    assert additional['rightsReviewed'] and additional['decoded']['allDecodedFramesFHD']
    assert sha(additional['localPath'])==additional['sha256'],'Additional source footage changed'
    footage.append(dict(id=additional['id'],sha256=additional['sha256']))
    manifest=read(MANIFEST);assert manifest['slug']==SLUG
    tts=manifest['tts'];assert tts['engine']=='qwen3-tts' and tts['renderMode']=='scene'
    assert tts['language']=='Korean' and tts['filenameStem']=='narration'
    assert repo_path(tts['outputDir'])==OUTPUT.resolve(),'Fixed first-voice output scope changed'
    reference=repo_path(tts['reference']);reference_text=repo_path(tts['referenceText'])
    assert reference==repo_path('shared/voice-reference/reference-15-35s.wav')
    assert reference_text==repo_path('shared/voice-reference/reference-15-35s.ko.txt')
    model=repo_path(tts['model']);assert model==repo_path('qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base')
    script=repo_path(manifest['paths']['script']);scenes=read(script)['scenes']
    assert [x['id'] for x in scenes]==[f's{i:02}' for i in range(1,7)]
    assert all(len(s['lines']) in ((1,2) if s['id']=='s03' else (1,)) and all(x.strip() for x in s['lines']) for s in scenes)
    assert [' '.join(x.strip() for x in s['lines'] if x.strip()) for s in scenes]==[x.strip() for x in read(NARRATION)['narrationKo']], 'Voice speech differs from current canonical narration'
    model_files=[p for p in sorted(model.rglob('*')) if p.is_file() and '.cache' not in p.parts
                 and (p.suffix in ('.safetensors','.bin') or p.name in ('config.json','configuration.json','generation_config.json','preprocessor_config.json','tokenizer_config.json','vocab.json','merges.txt','tokenizer.model'))]
    assert any(p.suffix=='.safetensors' for p in model_files),'Approved local model weights missing'
    model_pins=[dict(path=p.relative_to(model).as_posix(),sha256=sha(p)) for p in model_files]
    result=synthesis_identity(scenes,tts,manifest.get('editing',{}),model_pins,sha(reference),sha(reference_text))
    result.update(sceneIds=[s['id'] for s in scenes],spokenLines=[' '.join(x.strip() for x in s['lines']) for s in scenes],
        sceneGapSeconds=float(tts.get('sceneGapSeconds',.72)),
        audit=dict(narrationSHA256=sha(NARRATION),scriptPath=str(script),scriptSHA256=sha(script),
                   manifestSHA256=sha(MANIFEST),manifestSourceHashMatches=(manifest.get('sourceNarrationSHA256')==sha(NARRATION)),
                   engineSHA256=sha(ENGINE),gpuGuardSHA256=sha(ROOT/'qwen3-tts/gpu_handoff_guard.py'),
                   nativeFingerprint=native_pin,nativeEvidenceSHA256=sha(NATIVE_EVIDENCE),nativeQaSHA256=sha(QA),
                   sourceLedgerSHA256=sha(PROJECT_DIR/'source-footage.json'),additionalLedgerSHA256=sha(PROJECT_DIR/'additional-footage-search-v1.json'),footage=footage))
    assert PYTHON.is_file()
    return result


def same_project_children():
    found=[]
    for p in psutil.process_iter(['pid','name','cmdline']):
        try:
            args=p.info['cmdline'] or []
            if p.pid==os.getpid() or '--project' not in args:continue
            i=args.index('--project')
            if i+1>=len(args) or args[i+1]!=SLUG:continue
            if not any('render_narration.py' in a.replace('\\','/') for a in args):continue
            found.append(native.identity(p.pid))
        except psutil.NoSuchProcess:continue
        except psutil.AccessDenied:raise RuntimeError('A possible project voice child cannot be inspected; preserve it')
    return found


def checked_output_paths():
    parent=VOICE_PARENT.resolve();output=OUTPUT.resolve()
    assert output.parent==parent and output.name=='voice-v1','Voice output left selected03-02 directory'
    assert parent.is_relative_to((ROOT/'shared/output/architectural-111-20261106').resolve())
    return parent,output


def reusable_chunks(old,prov,output):
    """Only proven unchanged speech under exactly the same synthesis conditions."""
    none=dict(chunks=[],reason='No matching old voice receipt/evidence',evidence=None,evidencePath=None)
    if not old or old.get('protocol')!=PROTOCOL or not isinstance(old.get('identity'),dict):return none
    previous=old['identity'];current=prov['identity']
    encode=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    if encode(previous)!=old.get('fingerprint'):return none
    previous_common={k:v for k,v in previous.items() if k!='scenes'}
    current_common={k:v for k,v in current.items() if k!='scenes'}
    candidates=[]
    for path in (MEDIA/'first-voice-evidence.json',HERE/'first-voice-evidence.json'):
        if not path.exists():continue
        evidence=read(path)
        if evidence.get('fingerprint')!=old['fingerprint'] or Path(evidence.get('output','')).resolve()!=output:continue
        candidates.append((path,evidence))
    if not candidates:return none
    source_path,evidence=candidates[0]
    if any(e.get('sceneWavs')!=evidence.get('sceneWavs') for _,e in candidates[1:]):
        raise ValueError('Matching old voice proofs disagree; preserve and inspect')
    base=dict(none,evidence=evidence,evidencePath=str(source_path),evidenceSHA256=sha(source_path))
    if previous_common!=current_common:return dict(base,reason='Non-scene synthesis identity/profile/model/reference changed')
    old_scenes=previous.get('scenes',[]);new_scenes=current.get('scenes',[])
    if [s['id'] for s in old_scenes]!=[s['id'] for s in new_scenes]:return dict(base,reason='Scene ID/order changed')
    previous_engine=evidence.get('audit',{}).get('engineSHA256')
    if not previous_engine or previous_engine!=prov.get('audit',{}).get('engineSHA256'):
        return dict(base,reason='Old/current synthesis-engine source pin is absent or differs')
    proof_by_path={Path(p['path']).resolve():p for p in evidence.get('sceneWavs',[])}
    rows=[]
    for prior,now in zip(old_scenes,new_scenes):
        if prior!=now:continue
        sid=now['id'];path=(output/'chunks'/f'{sid}-scene.wav').resolve()
        assert path.is_relative_to(output),'Reusable scene escaped selected output'
        pin=proof_by_path.get(path)
        if pin is None:continue  # No proof is never permission to reuse.
        actual=wav_info(path)
        keys=('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames','durationSeconds')
        if any(actual[k]!=pin.get(k) for k in keys):raise ValueError('Reusable old chunk does not match its voice evidence: '+sid)
        rows.append(dict(sceneId=sid,file=path.relative_to(output).as_posix(),originalPath=str(path),sha256=actual['sha256'],pcmSHA256=actual['pcmSHA256'],
            sampleRate=actual['sampleRate'],frames=actual['frames'],spokenLines=now['lines']))
    return dict(chunks=rows,reason='Verified unchanged scene text and all non-scene synthesis pins',evidence=evidence,
        evidencePath=str(source_path),evidenceSHA256=sha(source_path),commonIdentitySHA256=encode(current_common))


def prepare_output(prov):
    parent,output=checked_output_paths();receipt=output/'voice-inputs.json'
    try:old=read(receipt) if receipt.exists() else None
    except (OSError,ValueError):old=None
    if not isinstance(old,dict):old=None
    compatible=bool(old and old.get('protocol')==PROTOCOL and old.get('fingerprint')==prov['fingerprint'] and old.get('identity')==prov['identity'])
    reused=[];reuse_record=None
    if output.exists() and any(output.iterdir()) and not compatible:
        if same_project_children():raise RuntimeError('Do not archive outputs while an existing Qwen child runs')
        reuse_plan=reusable_chunks(old,prov,output)
        proof=[]
        for p in sorted(output.rglob('*')):
            if p.is_file():
                assert p.resolve().is_relative_to(output),'Output contains an external link; preserve and inspect'
                proof.append(dict(path=p.relative_to(output).as_posix(),sha256=sha(p)))
        old_name=str((old or {}).get('fingerprint') or 'unassigned')[:12]
        if not old_name.isalnum():old_name='unassigned'
        dest=(parent/'voice-preserved'/(time.strftime('%Y%m%d-%H%M%S')+'-'+old_name+'-'+uuid.uuid4().hex[:8])).resolve()
        assert dest.is_relative_to(parent) and dest!=output and not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);os.replace(output,dest)
        save(dest/('archive-proof-'+uuid.uuid4().hex+'.json'),dict(original=str(output),preservedAt=time.time(),
             oldFingerprint=(old or {}).get('fingerprint'),newFingerprint=prov['fingerprint'],files=proof))
        evidence_copy=None
        if reuse_plan['evidence'] is not None:
            evidence_copy=dest/('reuse-source-voice-evidence-'+uuid.uuid4().hex[:8]+'.json')
            save(evidence_copy,reuse_plan['evidence'])
        if reuse_plan['chunks']:
            output.mkdir(parents=True,exist_ok=True)
            for row in reuse_plan['chunks']:
                source=(dest/row['file']).resolve();target=(output/row['file']).resolve()
                assert source.is_relative_to(dest) and target.is_relative_to(output) and not target.exists()
                assert sha(source)==row['sha256'],'Archived reuse source changed before copying'
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
                actual=wav_info(target)
                if actual['sha256']!=row['sha256'] or actual['pcmSHA256']!=row['pcmSHA256']:
                    raise ValueError('Copied unchanged chunk failed its WAV/PCM proof')
                reused.append(dict(**row,sourceArchive=str(dest),preservedPath=str(source),reusedPath=str(target),sourceFingerprint=old['fingerprint']))
            reuse_record=dict(protocol='architectural111-verified-scene-reuse-v1',oldFingerprint=old['fingerprint'],
                newFingerprint=prov['fingerprint'],sourceArchive=str(dest),oldVoiceEvidence=str(evidence_copy),
                oldVoiceEvidenceSHA256=sha(evidence_copy),sourceEvidencePath=reuse_plan['evidencePath'],
                sourceEvidenceSHA256=reuse_plan['evidenceSHA256'],commonIdentitySHA256=reuse_plan['commonIdentitySHA256'],
                reusedScenes=reused,aggregateCopied=False,timingCopied=False,srtCopied=False,asrCopied=False,
                humanListening=False,automaticSpeechPass=False)
            save(output/'verified-scene-reuse.json',reuse_record)
        old=None
    output.mkdir(parents=True,exist_ok=True)
    record=old or dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],createdAt=time.time(),initialAudit=prov['audit'])
    if reuse_record:record['verifiedSceneReuse']=reuse_record
    record['latestAudit']=prov['audit'];save(receipt,record)
    return output


def wav_info(path):
    pcm=hashlib.sha256()
    with wave.open(str(path),'rb') as w:
        frames=w.getnframes();rate=w.getframerate();channels=w.getnchannels();width=w.getsampwidth()
        if w.getcomptype()!='NONE' or frames<=0 or rate<=0:raise ValueError('Invalid PCM WAV')
        total=0
        while True:
            chunk=w.readframes(65536)
            if not chunk:break
            total+=len(chunk);pcm.update(chunk)
        if total!=frames*channels*width:raise ValueError('Truncated PCM data')
    return dict(path=str(path),sha256=sha(path),pcmSHA256=pcm.hexdigest(),sampleRate=rate,channels=channels,
                sampleWidthBytes=width,frames=frames,durationSeconds=frames/rate)


def verify_voice(prov):
    _,output=checked_output_paths()
    receipt=read(output/'voice-inputs.json')
    if receipt.get('protocol')!=PROTOCOL or receipt.get('fingerprint')!=prov['fingerprint'] or receipt.get('identity')!=prov['identity']:
        raise ValueError('Voice receipt does not match spoken/reference/profile pins')
    chunks=[wav_info(output/'chunks'/f'{sid}-scene.wav') for sid in prov['sceneIds']]
    by_scene=dict(zip(prov['sceneIds'],chunks))
    for reused in receipt.get('verifiedSceneReuse',{}).get('reusedScenes',[]):
        actual=by_scene[reused['sceneId']]
        if any(actual[key]!=reused[key] for key in ('sha256','pcmSHA256','sampleRate','frames')):
            raise ValueError('Qwen output changed a proven unchanged scene chunk: '+reused['sceneId'])
    aggregate=wav_info(output/'narration.wav');timing=read(output/'narration.timing.json')
    entries=timing['entries']
    if [x['scene_id'] for x in entries]!=prov['sceneIds'] or [x['text'] for x in entries]!=prov['spokenLines']:
        raise ValueError('Timing is not aligned to these six scene texts')
    if timing.get('render_mode')!='scene' or timing['sample_rate']!=aggregate['sampleRate']:raise ValueError('Wrong timing output format')
    expected=sum(x['durationSeconds'] for x in chunks)+(len(chunks)-1)*prov['sceneGapSeconds']
    tolerance=2/aggregate['sampleRate']
    if abs(expected-aggregate['durationSeconds'])>tolerance or abs(timing['duration_seconds']-aggregate['durationSeconds'])>tolerance:
        raise ValueError('Aggregate/timing duration does not equal preserved scene PCM')
    position=0.0
    for entry,chunk in zip(entries,chunks):
        if abs(float(entry['start'])-position)>tolerance or abs(float(entry['end'])-position-chunk['durationSeconds'])>tolerance:
            raise ValueError('Timing boundaries do not match the scene PCM')
        if chunk['sampleRate']!=aggregate['sampleRate']:raise ValueError('Scene sample rate differs')
        position+=chunk['durationSeconds']+prov['sceneGapSeconds']
    srt=output/'narration.srt'
    if not srt.is_file() or not srt.read_text(encoding='utf-8').strip():raise ValueError('Engine SRT missing')
    return dict(status='voice-generated-review-pending',fingerprint=prov['fingerprint'],output=str(output),sceneWavs=chunks,
                aggregateWav=aggregate,timing=dict(path=str(output/'narration.timing.json'),sha256=sha(output/'narration.timing.json')),
                engineSrt=dict(path=str(srt),sha256=sha(srt)),audit=prov['audit'],
                asrPerformedByThisWorker=False,listeningPerformedByThisWorker=False,finalApprovalGrantedByThisWorker=False,
                finalMovieCompletedByThisWorker=False)


def complete_record(proof):
    save(MEDIA/'first-voice-evidence.json',proof)
    pre_voice={'preproduction-in-progress','script-preparation','source-mapped-script-draft','native-captured-review-pending',
               'voice-manifest-prepared','waiting-for-voice','voice-generating','voice-generated-review-pending'}
    def attach(p,stage_key):
        previous=p.get('voiceCapture',{});merged=dict(previous) if previous.get('fingerprint')==proof['fingerprint'] else {}
        merged.update(proof)
        if previous.get('fingerprint')==proof['fingerprint']:
            for key in ('asrReviewStatus','listeningReviewStatus','humanApproval','reviewReady'):
                if key in previous:merged[key]=previous[key]
            if previous.get('status') and previous['status'] not in pre_voice:merged['status']=previous['status']
        p['voiceCapture']=merged;p['voiceGenerated']=True;p.setdefault('finalMovieComplete',False)
        if p.get(stage_key) in pre_voice:p[stage_key]='voice-generated-review-pending'
        if stage_key=='stage':
            p['completedStages']=list(dict.fromkeys(p.get('completedStages',[])+['voice-generated-structural-check']))
    native.update_json(PROJECT_DIR/'project.json',lambda p:attach(p,'status'))
    native.update_json(PROJECT_DIR/'checkpoint.json',lambda p:attach(p,'stage'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6)
    args=parser.parse_args()
    if not args.execute:
        try:
            prov=preparation();dedicated=any(s['id']=='s03' and len(s['lines'])==2 for s in prov['identity']['scenes'])
            print(json.dumps(dict(ready=not dedicated,fingerprint=prov['fingerprint'],requiresDedicatedS03Repair=dedicated,modelStarted=False)))
        except PreparationPending as error:print(json.dumps(dict(ready=False,reason=str(error),modelStarted=False)))
        return
    worker=native.SingleWorker(WORKER).acquire();worker.update(stage='voice',stageOwner=PROTOCOL,topicId='03.02')
    child=None;state=None;log_handle=None
    try:
        old=read(STATE) if STATE.exists() else {}
        if old.get('pid')!=os.getpid() and (native.alive(old) or native.alive(old.get('child'))):raise RuntimeError('Existing voice worker/child remains alive')
        if same_project_children():raise RuntimeError('An existing Qwen project child must finish; do not start a duplicate')
        state=dict(protocol=PROTOCOL,stage='voice',topicId='03.02',**native.identity(),child=None,status='waiting-for-preparation',
                   gpuStarted=False,completed=False,externalGpuLeaseAcquired=False,engineOwnsGpuLease=True)
        save(STATE,state);deadline=time.monotonic()+max(0,args.wait_hours)*3600
        while True:
            try:
                prov=preparation()
                if any(s['id']=='s03' and len(s['lines'])==2 for s in prov['identity']['scenes']):
                    raise RuntimeError('Selected S03 requires run-first-s03-level-repair.py; generic scene rendering would merge its two semantic takes')
                if same_project_children():raise PreparationPending('Existing project Qwen child is still running')
                output=prepare_output(prov);state['fingerprint']=prov['fingerprint'];state['output']=str(output)
                try:proof=verify_voice(prov)
                except (OSError,ValueError,KeyError,EOFError,wave.Error):proof=None
                if proof:
                    complete_record(proof);state.update(status='voice-generated-review-pending',completed=True,reusedCompleteVoice=True);break
                reason=native.busy_reason()
                if reason:raise PreparationPending(reason)
                current=preparation()
                if current['fingerprint']!=prov['fingerprint']:continue
                if same_project_children():raise PreparationPending('Project Qwen child appeared before launch')
                # Qwen's existing guard acquires/owns the lease; wrapping it would deadlock.
                command=[str(PYTHON),'-u','-X','utf8',str(ENGINE),'--project',SLUG,'--manifest',MANIFEST.relative_to(ROOT).as_posix(),
                         '--batch-size','1','--device','cuda:0']
                log_path=output/('engine-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.log')
                log_handle=log_path.open('ab');child=subprocess.Popen(command,cwd=ROOT,stdout=log_handle,stderr=subprocess.STDOUT,creationflags=CREATE)
                child_id=native.identity(child.pid);worker.update(child=child_id)
                state.update(status='voice-generating',child=child_id,childPid=child.pid,gpuStarted=True,log=str(log_path),launchAudit=current['audit'])
                save(STATE,state)
                if child.wait()!=0:raise RuntimeError('Qwen child failed or its resource guard declined; preserve pinned chunks/log')
                after=preparation()
                if after['fingerprint']!=prov['fingerprint']:raise RuntimeError('Spoken/reference/profile inputs changed during synthesis; preserve and version before retry')
                proof=verify_voice(after);complete_record(proof)
                state.update(status='voice-generated-review-pending',completed=True);break
            except PreparationPending as error:
                state.update(status='waiting-for-preparation-or-resources',reason=str(error),checkedAt=time.time());save(STATE,state)
                if time.monotonic()>=deadline:raise RuntimeError('Finite voice wait ended; existing apps/jobs preserved')
                time.sleep(10)
    except BaseException as error:
        if state is not None:state.update(status='failed-or-resource-blocked',error=repr(error))
        raise
    finally:
        live=bool(child and child.poll() is None) or bool(state and native.alive(state.get('child')))
        if state is not None:
            state.update(finishedOrYieldedAt=time.time(),childStillAlive=live)
            if live:state['status']='voice-worker-yielded-child-still-running'
            save(STATE,state)
        if log_handle:log_handle.close()
        worker.close(remove=not live)
        # No lease deletion: engine guard alone owns/releases its cooperative lease.
    print('Six scene WAVs and aggregate/timing verified; ASR, listening and final film remain separate.',flush=True)


if __name__=='__main__':main()
