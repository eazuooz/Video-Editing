"""Additive06.02 same-prose repair: preserve81 raw takes and generate15 selected takes. Default is read-only preparation.

The isolated existing controller retains singleton/child/launch-gap/resource
semantics. Only a new --execute invocation may stage/copy or launch. The trusted
engine sees missing scene IDs ONLY; accepted raw takes never enter its
tail-retry selection. Full canonical PCM is separately concatenated afterward.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,sys
from pathlib import Path
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE_SHA256='55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99'
REPAIR_PROTOCOL='architectural111-06-02-voice-subset-repair-v1'
SOURCE_OLD_FINGERPRINT='8ecdc01bbf34e2a8183ba5547033ec4ee0ca80a3ffb5d85bdb99b95d4f810927'
PLAN_SHA256='b087a51735472b1566540cd08b2187bf0f62186e0ed2411dc6ffbbb04dcccb90'
PLAN=ROOT/'projects/shorts-leveldesign-06-02/voice-subset-repair-plan-v1.json'
REPAIR_OLD_IDS={'p004-c01','p004-c04','p010-c04','p011-c01','p012-c02','p013-c01','p016-c03','p018-c02','p019-c02','p021-c03','p022-c03','p023-c01','p023-c02','p024-c02','p025-c03'}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

if sha(HERE/'run-selected-voice.py')!=BASE_SHA256:raise RuntimeError('Trusted selected-voice controller changed; review additive adapter before use')
base=load('selected_voice_subset_isolated_base',HERE/'run-selected-voice.py')
original={name:getattr(base,name)for name in ['prepared','initialize_output','validate_receipt','register_scenes','validate_engine_outputs','canonical_outputs','verify_complete','validate_launch_request','immutable_json']}
original_stage=base.prep.immutable_stage

def pin(row,role):
    if not isinstance(row,dict)or not isinstance(row.get('path'),str)or not isinstance(row.get('sha256'),str):raise ValueError('Missing pinned '+role)
    p=Path(row['path']).resolve()
    if not p.is_file()or sha(p)!=row['sha256']:raise ValueError('Changed '+role)
    return dict(path=str(p),sha256=row['sha256'])

def validate_reuse(prov,plan):
    """All81 same-ID/text raw copies bind exact old immutable96scene proof."""
    if prov['topicId']!='06.02'or plan.get('topicId')!='06.02'or plan.get('schemaVersion')!='06-02-voice-subset-repair-plan-v1':raise ValueError('Only exact selected06.02 repair supported')
    if plan.get('sourceNarrationSHA256')!=prov['manifest']['sourceNarrationSHA256']:raise ValueError('Repair narration plan is stale')
    if len(plan.get('repairSceneIds',[]))!=15 or set(plan['repairSceneIds'])!=REPAIR_OLD_IDS or (plan.get('expectedFullComponentCount'),plan.get('expectedMissingComponentCount'),plan.get('expectedReuseComponentCount'))!=(96,15,81):raise ValueError('Frozen15/81 repair selection changed')
    oldpin=pin(plan['oldVoiceEvidence'],'old immutable voice proof');old=read(oldpin['path'])
    if old.get('topicId')!='06.02'or old.get('fingerprint')!=SOURCE_OLD_FINGERPRINT or old.get('fingerprint')==prov['fingerprint']or digest(old['identity'])!=old['fingerprint']:raise ValueError('Old immutable voice identity differs or collides with repair')
    expected_proof=(ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/old['fingerprint'][:24]/'voice-complete-proof.json').resolve()
    if Path(oldpin['path'])!=expected_proof:raise ValueError('Source proof must be immutable old selected output, not mutable publication pointer')
    for key in ('tts','modelPins','referenceSHA256','referenceTextSHA256','engine','guard','rawPcmPolicy'):
        if key not in old['identity']or old['identity'][key]!=prov['identity'].get(key):raise ValueError('Accepted old profile/reference differs: '+key)
    oldscenes=old['identity']['scenes'];oldrows=old['sceneWavs'];newscenes=prov['identity']['scenes']
    if len(oldscenes)!=96 or len(oldrows)!=96 or newscenes!=oldscenes or len({s['id']for s in oldscenes})!=96:raise ValueError('Exact96 unchanged source scenes/text/order required')
    oldmap={s['id']:(s,w)for s,w in zip(oldscenes,oldrows)};safe=set(oldmap)-REPAIR_OLD_IDS;rows=plan.get('subsetReuse')
    if not REPAIR_OLD_IDS<=set(oldmap)or not isinstance(rows,list)or len(rows)!=81 or {r.get('oldSceneId')for r in rows}!=safe:raise ValueError('Exactly81 safe old raw IDs must be reused; targets cannot reenter')
    selected=[];seen=set()
    for row in rows:
        oldid,newid=row['oldSceneId'],row['newSceneId']
        if newid!=oldid or newid in seen or oldid not in safe:raise ValueError('Duplicate/remapped/targeted reuse scene')
        seen.add(newid);scene,wav=oldmap[oldid];text=row['canonicalText']
        if scene['lines']!=[text]or not row.get('reuseReason'):raise ValueError('Reused canonical sentence differs')
        source=pin(row['sourceWav'],'reused raw WAV');actual=base.wav_info(source['path'])
        for key in ('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames'):
            if actual[key]!=row['sourceWav'].get(key)or actual[key]!=wav.get(key):raise ValueError('Reused raw PCM metadata differs: '+key)
        expected=expected_proof.parent/'chunks'/(oldid+'-scene.wav')
        if Path(wav['path']).resolve()!=Path(source['path'])or Path(source['path'])!=expected:raise ValueError('Reuse is not the exact old selected raw chunk')
        rp=pin(row['sourceVoiceEvidence'],'row old proof')
        if rp!=oldpin or row['sourceVoiceEvidence'].get('fingerprint')!=old['fingerprint']:raise ValueError('Row old immutable evidence differs')
        selected.append(dict(row,sourceWav=actual,sourceVoiceEvidence=dict(oldpin,fingerprint=old['fingerprint'])))
    selected.sort(key=lambda row:list(oldmap).index(row['newSceneId']));return selected,oldpin,old['fingerprint']

def reselect_full(full,plan,path):
    """Same text needs explicit new lineage BEFORE output/staging derivation."""
    if full['fingerprint']!=SOURCE_OLD_FINGERPRINT or digest(full['identity'])!=full['fingerprint']:raise ValueError('Original current96 prose/profile no longer matches selected old source')
    oldpin=pin(plan['oldVoiceEvidence'],'old immutable voice proof')
    selection=dict(protocol=REPAIR_PROTOCOL,plan=pin(dict(path=str(path),sha256=sha(path)),'frozen repair plan'),sourceVoiceEvidence=oldpin,sourceVoiceFingerprint=SOURCE_OLD_FINGERPRINT,repairSceneIds=plan['repairSceneIds'],expectedFullCount=96,expectedNewCount=15,expectedByteReusedCount=81,adapterSHA256=sha(__file__),baseControllerSHA256=BASE_SHA256)
    identity=dict(full['identity'],repairSelection=selection);fp=digest(identity)
    if fp==SOURCE_OLD_FINGERPRINT:raise ValueError('Repair must not collide with old same-text synthesis output')
    inputs=full['inputs']+[selection['plan'],oldpin,dict(path=str(Path(__file__).resolve()),sha256=sha(__file__))]+[pin(plan[k],k)for k in ('semanticComponents','oldAsrReview','oldLevelReview','rootContentReview')]+[pin(r['sourceWav'],'reused source')for r in plan['subsetReuse']]
    inputs=[{k:r[k]for k in ('path','sha256')}for r in inputs]
    preparation=digest(dict(synthesisIdentity=fp,inputs=inputs,script=full['script'],paragraphMapping=full['paragraphMapping']))
    folder=ROOT/'projects'/full['slug']/'production/voice-preparation'/preparation[:24];output=ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/fp[:24]
    manifest=copy.deepcopy(full['manifest']);manifest['paths']['script']=(folder/'narration-qwen.json').relative_to(ROOT).as_posix();manifest['tts']['outputDir']=output.relative_to(ROOT).as_posix();manifest['synthesisIdentity']=fp;manifest['repairSelection']=selection
    command=list(full['qwenSynthesisArgv']);command[8]=(folder/'voice-manifest.json').relative_to(ROOT).as_posix()
    return dict(full,identity=identity,fingerprint=fp,preparationFingerprint=preparation,inputs=inputs,stagingDirectory=str(folder),voiceOutputDirectory=str(output),manifest=manifest,qwenSynthesisArgv=command,qwenDryRunArgv=command+['--dry-run'])

def repair_spec(prov,plan,path):
    rows,oldpin,oldfp=validate_reuse(prov,plan);reused={r['newSceneId']for r in rows};missing=[s for s in prov['identity']['scenes']if s['id']not in reused]
    if len(missing)!=15 or {s['id']for s in missing}!=REPAIR_OLD_IDS:raise ValueError('Engine must synthesize exactly frozen15 missing scenes')
    evidence={k:pin(plan[k],k)for k in ('semanticComponents','oldAsrReview','oldLevelReview','rootContentReview')}
    if evidence['semanticComponents']not in prov['inputs']:raise ValueError('Repair semantic components are not current source input')
    old=read(oldpin['path']);asr=read(evidence['oldAsrReview']['path']);levels=read(evidence['oldLevelReview']['path']);content=read(evidence['rootContentReview']['path'])
    if asr.get('voiceFingerprint')!=oldfp or asr.get('aggregateSHA256')!=old['aggregateWav']['sha256']or asr.get('timingSHA256')!=old['timing']['sha256']or len(asr.get('takes',[]))!=96 or len(asr.get('boundaryWindows',[]))!=95:raise ValueError('Prior ASR not exact complete96/95 old voice/timing')
    if levels.get('voiceFingerprint')!=oldfp or levels.get('canonicalWav')!=old['aggregateWav']or levels.get('asrReview')!=evidence['oldAsrReview']or len(levels.get('takes',[]))!=96 or len(levels.get('paragraphs',[]))!=25 or len(levels.get('joins',[]))!=95:raise ValueError('Prior numerical level review not exact old voice/ASR scope')
    if any(f.get('kind')=='sustained-take-word-body-decline'and f.get('sceneId')in reused for f in levels.get('flags',[])):raise ValueError('Numerically declining take cannot enter accepted81 reuse')
    if content.get('schemaVersion')!='06-02-root-raw-voice-content-review-v1'or content.get('topicId')!='06.02'or content.get('oldVoiceEvidence')!=oldpin or content.get('rawAsrReview')!=evidence['oldAsrReview']or content.get('rawLevelReview')!=evidence['oldLevelReview']or content.get('repairSceneIds')!=plan['repairSceneIds']:raise ValueError('Root repair disposition differs from exact old proofs/selection')
    identity=dict(protocol=REPAIR_PROTOCOL,fullVoiceFingerprint=prov['fingerprint'],repairSelection=prov['identity']['repairSelection'],oldVoiceEvidence=dict(oldpin,fingerprint=oldfp),previousReviewPins=evidence,reuse=rows,missingScenes=missing,plan=pin(dict(path=str(path),sha256=sha(path)),'frozen repair plan'),adapterSHA256=sha(__file__),baseWorkerSHA256=BASE_SHA256)
    fp=digest(identity);folder=Path(prov['stagingDirectory'])/('repair-subset-'+fp[:24]);script=copy.deepcopy(prov['script']);script['scenes']=[s for s in script['scenes']if s['id']not in reused]
    manifest=copy.deepcopy(prov['manifest']);manifest['paths']['script']=(folder/'narration-missing-only.json').relative_to(ROOT).as_posix();manifest.update(engineSceneScope='missing-subset-only',fullSynthesisIdentity=prov['fingerprint'],repairFingerprint=fp,engineSceneIds=[s['id']for s in missing])
    command=list(prov['qwenSynthesisArgv']);command[8]=(folder/'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
    return dict(fingerprint=fp,identity=identity,rows=rows,missing=missing,stagingDirectory=str(folder),script=script,manifest=manifest,command=command)

def prepared(args):
    full=original['prepared'](args);path=Path(args.repair_plan or PLAN).resolve()
    if path!=PLAN.resolve()or not path.is_file()or sha(path)!=PLAN_SHA256:raise base.prep.Pending('Exact frozen06.02 15/81 repair plan changed/missing')
    plan=read(path);full=reselect_full(full,plan,path);repair=repair_spec(full,plan,path)
    prov=dict(full);prov['_basePrepared']=full;prov['repair']=repair;prov['qwenSynthesisArgv']=repair['command'];prov['qwenDryRunArgv']=repair['command']+['--dry-run'];return prov

def repair_receipt(prov):return dict(protocol=REPAIR_PROTOCOL,fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=prov['repair']['fingerprint'],repairIdentity=prov['repair']['identity'])
def validate_receipt(prov,out):
    result=original['validate_receipt'](prov,out);p=Path(out)/'repair-inputs.json'
    if not p.is_file()or read(p)!=repair_receipt(prov):raise RuntimeError('Existing output lacks matching immutable subset-repair identity; preserve it')
    return result
def initialize_output(prov):
    out=base.output_of(prov);existed=out.exists()and any(out.iterdir())
    if existed:validate_receipt(prov,out);return out
    out=original['initialize_output'](prov);original['immutable_json'](out/'repair-inputs.json',repair_receipt(prov));return out

def subset_pins(prov):
    folder=Path(prov['repair']['stagingDirectory'])
    return [dict(path=str(folder/n),sha256=sha(folder/n))for n in ['narration-missing-only.json','voice-missing-only-manifest.json','subset-repair-preparation.json','repair-adapter-source.py']]

def stage(prov):
    """Executed only by the base controller after current resource checks."""
    original_stage(prov['_basePrepared']);out=base.output_of(prov);validate_receipt(prov,out)
    for row in prov['repair']['rows']:
        src=row['sourceWav'];actual=base.wav_info(src['path'])
        if actual!=src:raise RuntimeError('Accepted reuse source changed before staging')
        base.immutable(out/'chunks'/(row['newSceneId']+'-scene.wav'),Path(src['path']).read_bytes())
    folder=Path(prov['repair']['stagingDirectory']);r=prov['repair']
    for name,obj in [('narration-missing-only.json',r['script']),('voice-missing-only-manifest.json',r['manifest']),('subset-repair-preparation.json',dict(protocol=REPAIR_PROTOCOL,fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=r['fingerprint'],repairIdentity=r['identity'],command=r['command']))]:original['immutable_json'](folder/name,obj)
    base.immutable(folder/'repair-adapter-source.py',Path(__file__).read_bytes())
    return subset_pins(prov)

def immutable_json(path,obj):
    if Path(path).name=='request.json'and obj.get('protocol')==base.PROTOCOL:
        # The immutable outer request is itself in pending.requestPins. These
        # nested pins bind subset files transitively through that exact request.
        obj=dict(obj,repairFingerprint=CURRENT['repair']['fingerprint'],engineSceneScope='missing-subset-only',engineSceneIds=[s['id']for s in CURRENT['repair']['missing']],subsetPins=subset_pins(CURRENT))
    return original['immutable_json'](path,obj)

CURRENT=None
def active_prepared(args):
    global CURRENT
    CURRENT=prepared(args);return CURRENT

def validate_launch_request(prov,out,pending):
    attempt=Path(pending['attempt']).resolve();request_path=attempt/'request.json'
    if not attempt.is_relative_to((Path(out)/'engine-attempts').resolve()):raise RuntimeError('Subset pending attempt escaped selected output')
    outer={Path(p['path']).resolve():p['sha256']for p in pending['requestPins']}
    if request_path not in outer or sha(request_path)!=outer[request_path]:raise RuntimeError('Subset request not bound by pending launch')
    req=read(request_path);r=prov['repair']
    if req.get('protocol')!=base.PROTOCOL or req.get('fingerprint')!=prov['fingerprint']or req.get('identity')!=prov['identity']or req.get('repairFingerprint')!=r['fingerprint']:raise RuntimeError('Subset pending synthesis/repair identity differs')
    command=req.get('command',[]);expected=r['command']
    if len(command)!=len(expected)or command[:8]!=expected[:8]or command[9:]!=expected[9:]or req.get('engineSceneScope')!='missing-subset-only'or req.get('engineSceneIds')!=[s['id']for s in r['missing']]:raise RuntimeError('Engine must receive only exact missing scene IDs')
    wanted=req.get('subsetPins',[]);names=['narration-missing-only.json','voice-missing-only-manifest.json','subset-repair-preparation.json','repair-adapter-source.py']
    if not isinstance(wanted,list)or [Path(p['path']).name for p in wanted]!=names:raise RuntimeError('Exact subset input pin set required')
    files=[Path(pin(p,'pending subset input')['path'])for p in wanted];folder=files[0].parent
    if sha(files[3])!=r['identity']['adapterSHA256']:raise RuntimeError('Pinned repair adapter snapshot differs from selected repair identity')
    if any(p.parent!=folder for p in files)or folder.name!='repair-subset-'+r['fingerprint'][:24]or not folder.is_relative_to((ROOT/'projects'/prov['slug']/'production/voice-preparation').resolve()):raise RuntimeError('Pending subset escaped immutable selected staging')
    if (ROOT/command[8]).resolve()!=folder/'voice-missing-only-manifest.json':raise RuntimeError('Subset command does not name its pinned manifest')
    script=read(files[0]);manifest=read(files[1]);preparation=read(files[2])
    if [{'id':s['id'],'lines':s['lines']}for s in script['scenes']]!=r['missing']:raise RuntimeError('Subset script differs from exact missing chunks')
    if (ROOT/manifest['paths']['script']).resolve()!=files[0]or manifest.get('slug')!=prov['slug']or manifest.get('tts')!=r['manifest']['tts']or manifest.get('editing')!=r['manifest']['editing']or manifest.get('rawPcmPolicy')!=r['manifest'].get('rawPcmPolicy')or manifest.get('repairFingerprint')!=r['fingerprint']or manifest.get('fullSynthesisIdentity')!=prov['fingerprint']or manifest.get('engineSceneScope')!='missing-subset-only'or manifest.get('engineSceneIds')!=[s['id']for s in r['missing']]:raise RuntimeError('Subset profile/output/full identity differs')
    if preparation.get('repairFingerprint')!=r['fingerprint']or preparation.get('fullVoiceFingerprint')!=prov['fingerprint']or preparation.get('repairIdentity')!=r['identity']or preparation.get('command')!=command:raise RuntimeError('Pending subset preparation identity differs')
    if set(s['id']for s in script['scenes'])&set(x['newSceneId']for x in r['rows']):raise RuntimeError('Engine subset includes an accepted reused take')
    return attempt

def register_scenes(prov,out,attempt):
    result=original['register_scenes'](prov,out,attempt);byid={r['newSceneId']:r for r in prov['repair']['rows']}
    for sid,row in result['scenes'].items():
        if sid in byid:
            r=byid[sid]
            if row['sha256']!=r['sourceWav']['sha256']or row['pcmSHA256']!=r['sourceWav']['pcmSHA256']:raise RuntimeError('A reused accepted raw take was modified/retried')
            row.update(attempt=None,pcmOrigin='Exact byte-copy of accepted old selected raw take; not generated by this subset engine',reusedFrom=r)
        else:row['pcmOrigin']='New selected raw take from missing-only engine request'
    base.save(Path(out)/'scene-progress.json',result);return result

def validate_engine_outputs(prov,out):
    subset=dict(prov,identity=dict(prov['identity'],scenes=prov['repair']['missing']))
    chunks,engine=original['validate_engine_outputs'](subset,out)
    pointer=Path(out)/'pending-launch.json'
    if pointer.is_file():
        pending=read(pointer);attempt=validate_launch_request(prov,out,pending);actual_pins=read(attempt/'request.json')['subsetPins']
    else:actual_pins=subset_pins(prov)
    engine.update(engineSceneScope='missing-subset-only',engineSceneIds=[s['id']for s in prov['repair']['missing']],engineSceneCount=len(chunks),fullCanonicalSceneCount=len(base.scenes(prov)),reusedSceneIds=[r['newSceneId']for r in prov['repair']['rows']],subsetInputs=actual_pins,subsetAggregateAndTimingValidated=True)
    return [base.wav_info(Path(out)/'chunks'/(s['id']+'-scene.wav'))for s in base.scenes(prov)],engine

def canonical_outputs(prov,out,engine):
    if engine.get('engineSceneScope')!='missing-subset-only'or engine.get('subsetAggregateAndTimingValidated')is not True:raise RuntimeError('Full canonical proof requires validated missing-only engine aggregate/timing; preserve interrupted chunks without pretending completion')
    proof=original['canonical_outputs'](prov,out,engine)
    proof.update(repairProtocol=REPAIR_PROTOCOL,repairFingerprint=prov['repair']['fingerprint'],repairIdentity=prov['repair']['identity'],reusedRawScenes=prov['repair']['rows'],newlyGeneratedSceneIds=[s['id']for s in prov['repair']['missing']],rawSceneCount=len(base.scenes(prov)),engineSpokeFullCombinedScript=False,canonicalPcmOrigin='Exact full-order concatenation of authorized accepted old raw PCM chunks and new missing-only raw PCM chunks; no samples inserted/trimmed/faded/scaled/time-warped')
    return proof

def verify_complete(prov,out):
    proof=original['verify_complete'](prov,out)
    if proof is None:return None
    if proof.get('repairFingerprint')!=prov['repair']['fingerprint']or proof.get('repairIdentity')!=prov['repair']['identity']or proof.get('engineSpokeFullCombinedScript')is not False:raise RuntimeError('Completed repair proof differs; preserve existing PCM')
    for row in prov['repair']['rows']:
        now=base.wav_info(Path(out)/'chunks'/(row['newSceneId']+'-scene.wav'))
        if now['sha256']!=row['sourceWav']['sha256']or now['pcmSHA256']!=row['sourceWav']['pcmSHA256']:raise RuntimeError('Completed reused raw take differs')
    engine=proof['engineOutputsPreserved']
    if engine.get('engineSceneIds')!=[s['id']for s in prov['repair']['missing']]or engine.get('subsetAggregateAndTimingValidated')is not True:raise RuntimeError('Completed subset engine scope differs')
    for row in engine.get('subsetInputs',[]):pin(row,'preserved subset input')
    return proof

def install_hooks():
    base.prepared=active_prepared;base.prep.immutable_stage=stage;base.initialize_output=initialize_output;base.validate_receipt=validate_receipt
    for name in ['register_scenes','validate_engine_outputs','canonical_outputs','verify_complete','validate_launch_request','immutable_json']:setattr(base,name,globals()[name])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--topic',default='06.02');p.add_argument('--semantic-components',default='projects/shorts-leveldesign-06-02/voice-semantic-components-v2.json');p.add_argument('--repair-plan',default=str(PLAN));p.add_argument('--native-evidence',default='projects/shorts-leveldesign-06-02/voice-native-bundle-v1.json');p.add_argument('--native-qa',default='projects/shorts-leveldesign-06-02/native-voice-qa-v2.json');p.add_argument('--execute',action='store_true');p.add_argument('--wait-hours',type=float,default=6);a=p.parse_args()
    if a.topic!='06.02'or not math.isfinite(a.wait_hours)or not 0<a.wait_hours<=6:raise ValueError('Only finite selected06.02 repair supported')
    install_hooks()
    if a.execute:return base.execute(a)
    try:
        prov=active_prepared(a);out=base.output_of(prov);proof=verify_complete(prov,out)if (out/'voice-complete-proof.json').exists()else None
        print(json.dumps(dict(ready=True,topicId=a.topic,fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=prov['repair']['fingerprint'],fullSceneCount=len(base.scenes(prov)),missingOnlyCount=len(prov['repair']['missing']),reuseCount=len(prov['repair']['rows']),engineSceneIds=[s['id']for s in prov['repair']['missing']],existingComplete=bool(proof),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
    except (base.prep.Pending,FileNotFoundError)as e:print(json.dumps(dict(ready=False,reason=str(e),staged=False,reuseCopied=False,modelStarted=False),ensure_ascii=False))
if __name__=='__main__':main()
