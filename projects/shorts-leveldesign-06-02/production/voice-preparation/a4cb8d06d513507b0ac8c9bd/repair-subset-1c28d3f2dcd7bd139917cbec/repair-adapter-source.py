"""Additive06.02 same-prose repair: preserve88 mapped raw takes and generate15 selected clauses;103physical/96logical. Default is read-only preparation.

The isolated existing controller retains singleton/child/launch-gap/resource
semantics. Only a new --execute invocation may stage/copy or launch. The trusted
engine sees missing scene IDs ONLY; accepted raw takes never enter its
tail-retry selection. Full canonical PCM is separately concatenated afterward.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,re,sys,time
from pathlib import Path
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE_SHA256='55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99'
REPAIR_PROTOCOL='architectural111-06-02-voice-subset-repair-v2'
SOURCE_OLD_FINGERPRINT='ef057b17e86685d6f77ce27990e30cc31d32584517998c8c99948e00e96e8bf1'
PLAN_SHA256='b61b4ff5b9a3b5a5953a10c6ad77a3d8a09e49d4e39a49efeb498bb14cc585a3'
PLAN=ROOT/'projects/shorts-leveldesign-06-02/voice-subset-repair-plan-v2.json'
SPLIT_LOGICAL_IDS={'p004-c04','p011-c01','p013-c01','p018-c02','p022-c03','p024-c02','p025-c03'}
CHANGED_LOGICAL_IDS={'p004-c01','p011-c01','p025-c03'}
REPLACED_OLD_IDS=SPLIT_LOGICAL_IDS|CHANGED_LOGICAL_IDS
DECISION_SHA256='90ad7a715cb17667eb0168d3eaf9c15ee195bc7ed85bbf7638a4b8a15211e3f5'
PREPARER_SHA256='7fc1afac8b7c44b7752f0b53620150cd0989238cc4cc5866a14f40480034a020'
COMPONENTS=ROOT/'projects/shorts-leveldesign-06-02/voice-semantic-components-v3.json'
NARRATION=ROOT/'projects/shorts-leveldesign-06-02/narration-expanded-draft-v4.json'

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
original_save=base.save


def metadata_retry_owner_token(path,obj):
    """Only this live V2 singleton's exact JSON paths; no lease/raw/foreign paths."""
    try:
        marker=Path(base.MEDIA)/'06-02-voice-worker.json'
        rec=read(marker);me=base.identity();argv=me['argv'];owner='architectural-111-06-02-voice'
        if not any(Path(a).name==Path(__file__).name for a in argv):return False
        if rec.get('protocol')!=base.PROTOCOL or rec.get('owner')!=owner or rec.get('pid')!=me['pid'] or abs(rec.get('createTime',0)-me['createTime'])>=.01 or rec.get('argv')!=argv or rec.get('commandSHA256')!=digest(argv) or not rec.get('token'):return False
        path=Path(path).resolve();media=Path(base.MEDIA).resolve()
        if path==media/'06-02-voice-progress.json':
            return rec['token']if obj.get('protocol')==base.PROTOCOL and obj.get('owner')==owner and obj.get('pid')==me['pid'] and obj.get('token')==rec['token']else False
        if CURRENT is None or CURRENT.get('repair',{}).get('identity',{}).get('protocol')!=REPAIR_PROTOCOL:return False
        if obj.get('protocol')!=base.PROTOCOL or obj.get('fingerprint')!=CURRENT['fingerprint']:return False
        if path==base.output_of(CURRENT)/'scene-progress.json':return rec['token']
        return rec['token']if path==media/'06-02-voice-evidence.json' and obj.get('topicId')=='06.02'else False
    except (OSError,ValueError,TypeError,KeyError):return False


def metadata_save(path,obj):
    token=metadata_retry_owner_token(path,obj)
    if not token:return original_save(path,obj)
    last_error=None
    for attempt in range(10):
        if attempt and metadata_retry_owner_token(path,obj)!=token:raise last_error
        try:return original_save(path,obj)
        except PermissionError as error:
            last_error=error
            if getattr(error,'winerror',None)!=5 or attempt==9 or metadata_retry_owner_token(path,obj)!=token:raise
            time.sleep(min(.05*(attempt+1),.25))

def pin(row,role):
    if not isinstance(row,dict)or not isinstance(row.get('path'),str)or not isinstance(row.get('sha256'),str):raise ValueError('Missing pinned '+role)
    p=Path(row['path']).resolve()
    if not p.is_file()or sha(p)!=row['sha256']:raise ValueError('Changed '+role)
    return dict(path=str(p),sha256=row['sha256'])

def component_contract(ko,plan,narration_sha):
    """103 exact physical clauses, seven declared comma splits, 96 logical beats."""
    if plan.get('topicId')!='06.02' or plan.get('sourceNarrationSHA256')!=narration_sha or len(ko)!=25:raise ValueError('Exact current06.02 source required')
    paragraphs=plan.get('paragraphs',[]);logical=plan.get('logicalGroups',[])
    if [p.get('paragraph')for p in paragraphs]!=list(range(1,26)) or len(logical)!=96:raise ValueError('Exact25 paragraphs/96 logical groups required')
    groups={};physical=[];bylogical={}
    for n,row in enumerate(paragraphs,1):
        parts=row.get('components',[]);cursor=0
        if not parts:raise ValueError('Empty physical paragraph')
        for j,item in enumerate(parts,1):
            text=item.get('text');sid=f'p{n:03d}-c{j:02d}';lid=item.get('logicalSceneId');li=item.get('logicalSentenceIndexZeroBased')
            if not isinstance(text,str) or not text or text!=text.strip() or not str(item.get('reason','')).strip():raise ValueError('Physical clause text/reason missing')
            if item.get('physicalSceneId')!=sid or type(li)is not int or li<0 or lid!=f'p{n:03d}-c{li+1:02d}':raise ValueError('Physical/logical ID or order differs')
            end=cursor+len(text)
            if not isinstance(item.get('sourceCharRange'),list) or any(type(x)is not int for x in item['sourceCharRange']) or item['sourceCharRange']!=[cursor,end] or ko[n-1][cursor:end]!=text:raise ValueError('Physical paragraph char span differs')
            physical.append(dict(item,paragraph=n));bylogical.setdefault(lid,[]).append(dict(item,paragraph=n));cursor=end+1
        if ' '.join(x['text']for x in parts)!=ko[n-1]:raise ValueError('Physical clauses do not exactly reconstruct paragraph')
        groups[n]=parts
    if len(physical)!=103 or len({p['physicalSceneId']for p in physical})!=103 or len(bylogical)!=96:raise ValueError('Exactly103 unique physical clauses required')
    if [g.get('logicalSceneId',g.get('id'))for g in logical]!=list(bylogical):raise ValueError('Logical group order differs from physical source')
    split=set()
    for group in logical:
        lid=group.get('logicalSceneId',group.get('id'));parts=bylogical[lid];n=parts[0]['paragraph'];count=len(parts);text=group.get('canonicalText');start=parts[0]['sourceCharRange'][0];end=parts[-1]['sourceCharRange'][1]
        if group.get('id',lid)!=lid or group.get('paragraph')!=n or group.get('logicalSentenceIndexZeroBased')!=parts[0]['logicalSentenceIndexZeroBased'] or group.get('sourceCharRange')!=[start,end] or group.get('physicalSceneIds')!=[p['physicalSceneId']for p in parts] or group.get('canonicalInterComponentJoiner')!=' ':raise ValueError('Logical group mapping/source span differs')
        if text!=' '.join(p['text']for p in parts) or ko[n-1][start:end]!=text or count!=(2 if lid in SPLIT_LOGICAL_IDS else 1):raise ValueError('Logical group canonical text or allowed split differs')
        cursor=0
        for i,item in enumerate(parts,1):
            last=cursor+len(item['text'])
            if type(item.get('logicalPartIndex'))is not int or type(item.get('logicalPartCount'))is not int or item['logicalPartIndex']!=i or item['logicalPartCount']!=count or not isinstance(item.get('logicalSourceCharRange'),list) or any(type(x)is not int for x in item['logicalSourceCharRange']) or item['logicalSourceCharRange']!=[cursor,last] or item.get('canonicalJoinerAfter')!=(' 'if i<count else ''):raise ValueError('Exact physical-to-logical clause span/joiner differs')
            cursor=last+1
        if count==2:
            split.add(lid)
            if not parts[0]['text'].endswith(',') or not parts[1]['text'] or parts[1]['text'].startswith(','):raise ValueError('Only exact existing grammatical comma/breath splits allowed')
    if split!=SPLIT_LOGICAL_IDS:raise ValueError('Seven selected logical comma splits required')
    for n in range(1,26):
        if ' '.join(g['canonicalText']for g in logical if g['paragraph']==n)!=ko[n-1]:raise ValueError('Logical beats omit/repeat canonical prose')
    return groups,logical,physical


def source_eligibility_view(draft,qa,narration_pin,components_pin,conformance):
    """External source-bound authorization, never a mutation of candidate flags."""
    if qa.get('sourceNarration')!=narration_pin or qa.get('semanticComponents')!=components_pin or qa.get('logicalGroupCount')!=96 or qa.get('physicalComponentCount')!=103 or qa.get('preTtsEligible')is not True or qa.get('voicePreparationAllowed')is not True:raise base.prep.Pending('Exact V4/103source eligibility and96logical mapping not authorized byV3 QA')
    if conformance.get('schemaVersion')!='06-02-source-clause-remediation-conformance-v1' or conformance.get('topicId')!='06.02' or conformance.get('logicalSentenceGroups')!=96 or conformance.get('physicalVoiceUnits')!=103 or conformance.get('exactReuseTextCandidates')!=88 or conformance.get('newPhysicalUnits')!=15 or conformance.get('rootDecision',{}).get('sha256')!=DECISION_SHA256:raise base.prep.Pending('Root source conformance count/decision scope differs')
    if narration_pin not in conformance.get('newArtifacts',[]) or components_pin not in conformance.get('newArtifacts',[]) or any(conformance.get(k)is not True for k in('internalSourceReviewed','manualSourceSemanticReview','exactParagraphAndLogicalCharReconstruction','canonicalInterComponentSpacesOnly','all14SourceLearningRolesAndOrderRetained')):raise base.prep.Pending('Whole-source semantic/char reconstruction review missing or stale')
    eligible=copy.deepcopy(draft);eligible['readyForDraftIntegration']=True;eligible['preTtsEligibility']=True
    return eligible


def selected_full(args,plan):
    """New-source-only preparation; reuse frozen generic validators, never its07 clause override."""
    prep=base.prep
    if sha(HERE/'prepare-selected-voice.py')!=PREPARER_SHA256:raise prep.Pending('Reviewed generic preparation primitives changed')
    if args.topic!='06.02' or Path(args.semantic_components).resolve()!=COMPONENTS.resolve():raise prep.Pending('Only scoped103 component source supported')
    comp_pin=pin(plan['semanticComponents'],'current103 components');component_plan=read(comp_pin['path'])
    if Path(comp_pin['path'])!=COMPONENTS.resolve() or Path(component_plan.get('sourceNarrationPath','')).resolve()!=NARRATION.resolve() or sha(NARRATION)!=plan.get('sourceNarrationSHA256'):raise prep.Pending('Exact versionedV4 narration/V3 components required')
    control=read(ROOT/'shared/publishing/video-production-control.json')[prep.AUTH];batch=read(HERE/'batch.json');slug='shorts-leveldesign-06-02'
    if control.get('status')in('paused','cancelled','stopped') or control.get('userEvidence')!='111개 전체 제작 들어가줘' or control.get('automaticAdvanceOutsideList') or not control.get('humanFinalReviewRequired') or control.get('youtubeAuthorized'):raise prep.Pending('Current finite production authorization inactive')
    selected=[r for r in batch['projects']if r['topicId']=='06.02'and r['slug']==slug]
    if len(batch['projects'])!=111 or len(selected)!=1 or not batch.get('localFinalReviewOnly') or selected[0].get('productionComplete')is True or sha(prep.repo(batch['sourceCatalog']))!=batch['sourceCatalogSHA256']:raise prep.Pending('Topic outside selected exact111 local-review scope')
    np=prep.selected_path(args.native_evidence,slug);qp=prep.selected_path(args.native_qa,slug)
    if qp!=(ROOT/'projects'/slug/'native-voice-qa-v3.json').resolve():raise prep.Pending('New source-bound native-voice-qa-v3 required; oldV2 does not authorize103 speech')
    qa=read(qp)
    if pin(plan['sourceNarration'],'selectedV4 narration')!=prep.pin(NARRATION) or pin(plan['nativeVoiceQa'],'selectedV3 source/native QA')!=prep.pin(qp) or pin(plan['nativeEvidence'],'selected unchanged native bundle')!=prep.pin(np):raise prep.Pending('Exact frozen root source/native eligibility inputs differ')
    conformance=pin(qa.get('sourceConformance'),'root source conformance')
    if Path(conformance['path'])!=(ROOT/'projects'/slug/'source-clause-remediation-conformance-v1.json').resolve():raise prep.Pending('Exact source-clause conformance record required')
    root_readthrough=pin(plan['rootReadthrough'],'root25KO/EN source readthrough')
    if conformance!=pin(plan['sourceConformance'],'selected source conformance') or qa.get('rootConformance')!=root_readthrough:raise prep.Pending('Root source conformance/readthrough differs from frozen plan')
    draft=read(NARRATION);eligible=source_eligibility_view(draft,qa,prep.pin(NARRATION),comp_pin,read(conformance['path']))
    # Root V3 source-bound authorization is external to the immutable V4 draft.
    # Only an in-memory eligibility view enters the unchanged text/placeholder
    # validator; source flags/files are never rewritten or claimed as hearing.
    ko=prep.validate_narration(eligible)
    if draft.get('topicId')!='06.02':raise prep.Pending('Narration topic differs')
    groups,logical,physical=component_contract(ko,component_plan,sha(NARRATION));script,mapping=prep.make_scenes(draft,groups)
    sources_path=ROOT/'projects'/slug/'source-footage.json';adopted=[r for r in read(sources_path).get('sources',[])if r.get('selectedForCut')is True]
    if not adopted:raise prep.Pending('No adopted independent footage')
    footage=[prep.validate_source_row(r,slug)for r in adopted]
    native=prep.validate_native(read(np),qa,np,slug);profile=prep.validate_profile()
    inputs=[prep.pin(q)for q in [NARRATION,COMPONENTS,sources_path,np,qp,prep.PROFILE,HERE/'prepare-selected-voice.py',Path(__file__)]]
    inputs += [conformance,root_readthrough]+[dict(path=row['path'],sha256=row['sha256'])for row in footage]+native['captureArtifacts']+native['sampledPreviewArtifacts']
    inputs += [prep.pin(prep.repo(profile[name]))for name in ['reference','referenceText','python']]
    inputs += [dict(path=str(prep.repo(profile[name]['path'])),sha256=profile[name]['sha256'])for name in ['engine','guard']]
    inputs += [dict(path=str(prep.repo(profile['model'])/row['path']),sha256=row['sha256'])for row in profile['modelPins']]
    inputs=list({row['path']:row for row in inputs}.values())
    identity=dict(protocol=prep.PROTOCOL,topicId='06.02',scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']],tts={k:v for k,v in profile['tts'].items()if k not in ['filenameStem','gpuMinimumFreeMiB','gpuProfileReason']},modelPins=profile['modelPins'],referenceSHA256=profile['referenceSHA256'],referenceTextSHA256=profile['referenceTextSHA256'],engine=profile['engine'],guard=profile['guard'],rawPcmPolicy=profile['rawPcmPolicy'])
    fp=digest(identity);preparation=digest(dict(synthesisIdentity=fp,inputs=inputs,script=script,paragraphMapping=mapping));folder=ROOT/'projects'/slug/'production/voice-preparation'/preparation[:24];output=ROOT/'shared/output'/prep.BATCH_ID/'06-02/voice-attempts'/fp[:24]
    manifest=dict(schemaVersion=2,slug=slug,revision=prep.PROTOCOL,paths=dict(script=(folder/'narration-qwen.json').relative_to(ROOT).as_posix()),editing=dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation'),tts=dict(profile['tts'],reference=profile['reference'],referenceText=profile['referenceText'],model=profile['model'],outputDir=output.relative_to(ROOT).as_posix()),sourceNarrationSHA256=sha(NARRATION),synthesisIdentity=fp,rawPcmPolicy=profile['rawPcmPolicy'])
    command=[str(prep.repo(profile['python'])),'-u','-X','utf8',str(prep.repo(profile['engine']['path'])),'--project',slug,'--manifest',(folder/'voice-manifest.json').relative_to(ROOT).as_posix(),'--batch-size','1','--device','cuda:0']
    return dict(topicId='06.02',slug=slug,ready=True,fingerprint=fp,preparationFingerprint=preparation,identity=identity,inputs=inputs,footage=footage,native=native,script=script,manifest=manifest,paragraphMapping=mapping,stagingDirectory=str(folder),voiceOutputDirectory=str(output),qwenSynthesisArgv=command,qwenDryRunArgv=command+['--dry-run'],logicalGroups=logical,physicalSourceComponents=physical)


def validate_reuse(prov,plan):
    if prov['topicId']!='06.02' or plan.get('topicId')!='06.02' or plan.get('schemaVersion')!='06-02-voice-subset-repair-plan-v2':raise ValueError('Only exact selected06.02 V2 repair supported')
    if plan.get('sourceNarrationSHA256')!=prov['manifest']['sourceNarrationSHA256'] or (plan.get('expectedFullComponentCount'),plan.get('expectedMissingComponentCount'),plan.get('expectedReuseComponentCount'))!=(103,15,88):raise ValueError('Current103/15/88 source plan required')
    oldpin=pin(plan['oldVoiceEvidence'],'old immutable V2 voice proof');old=read(oldpin['path']);expected_proof=(ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/SOURCE_OLD_FINGERPRINT[:24]/'voice-complete-proof.json').resolve()
    if Path(oldpin['path'])!=expected_proof or old.get('topicId')!='06.02' or old.get('fingerprint')!=SOURCE_OLD_FINGERPRINT or digest(old['identity'])!=old['fingerprint'] or old['fingerprint']==prov['fingerprint']:raise ValueError('Exact old immutableV2 identity required; never a mutable pointer')
    for key in ('tts','modelPins','referenceSHA256','referenceTextSHA256','engine','guard','rawPcmPolicy'):
        if old['identity'].get(key)!=prov['identity'].get(key):raise ValueError('Old profile/reference/model/engine/guard/raw policy differs: '+key)
    oldscenes=old['identity']['scenes'];oldrows=old['sceneWavs'];newscenes=prov['identity']['scenes'];logical=prov['logicalGroups'];newmap={s['id']:s for s in newscenes};oldmap={s['id']:(s,w)for s,w in zip(oldscenes,oldrows)}
    if len(oldscenes)!=96 or len(oldrows)!=96 or len(oldmap)!=96 or len(newscenes)!=103 or len(newmap)!=103 or len(logical)!=96:raise ValueError('Exact96old/103new/96logical scope required')
    if [g['logicalSceneId']for g in logical]!=[s['id']for s in oldscenes]:raise ValueError('Stable96 logical IDs/order changed')
    revised={g['logicalSceneId']:g for g in logical}
    for sid,(scene,_)in oldmap.items():
        before=scene['lines'][0];after=revised[sid]['canonicalText']
        expected=before.removeprefix('지금 ')if sid=='p004-c01'else '아래층과 위층을 이어 주는 경사로인 램프를 따라 올라가면, 아래의 열린 공간을 점점 더 넓게 바라볼 수 있습니다.'if sid=='p011-c01'else before.replace('숨을 곳을','은신처를',1)if sid=='p025-c03'else before
        if after!=expected:raise ValueError('Only three exact root-selected logical wording changes allowed: '+sid)
    safe=set(oldmap)-REPLACED_OLD_IDS;rows=plan.get('subsetReuse',[])
    if len(rows)!=88 or len(safe)!=88 or {r.get('oldSceneId')for r in rows}!=safe:raise ValueError('Exactly88 old raw IDs must be reused')
    selected=[];seen=set()
    for row in rows:
        oldid,newid=row['oldSceneId'],row['newSceneId'];scene,wav=oldmap[oldid];group=revised[oldid]
        if newid in seen or group['physicalSceneIds']!=[newid] or newid not in newmap or newmap[newid]['lines']!=scene['lines'] or row.get('canonicalText')!=scene['lines'][0] or not row.get('reuseReason'):raise ValueError('Explicit old-to-new ID/text reuse map differs')
        seen.add(newid);source=pin(row['sourceWav'],'old raw WAV');actual=base.wav_info(source['path'])
        for key in ('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames'):
            if actual[key]!=row['sourceWav'].get(key)or actual[key]!=wav.get(key):raise ValueError('Reused PCM proof differs: '+key)
        if Path(source['path'])!=(expected_proof.parent/'chunks'/(oldid+'-scene.wav')).resolve() or Path(wav['path']).resolve()!=Path(source['path']):raise ValueError('Reuse source escaped exact old immutable chunk')
        if pin(row['sourceVoiceEvidence'],'row immutable old proof')!=oldpin or row['sourceVoiceEvidence'].get('fingerprint')!=old['fingerprint']:raise ValueError('Reused row proof differs')
        selected.append(dict(row,sourceWav=actual,sourceVoiceEvidence=dict(oldpin,fingerprint=old['fingerprint'])))
    selected.sort(key=lambda row:list(newmap).index(row['newSceneId']))
    missing=[sid for sid in newmap if sid not in seen];wanted=[sid for g in logical if g['logicalSceneId']in REPLACED_OLD_IDS for sid in g['physicalSceneIds']]
    if missing!=wanted or missing!=plan.get('repairSceneIds') or len(missing)!=15:raise ValueError('Exactly15 mapped new clauses must be generated')
    return selected,oldpin,old['fingerprint']


def reselect_full(full,plan,path):
    if len(full['identity']['scenes'])!=103 or digest(full['identity'])!=full['fingerprint']:raise ValueError('Exact current103 base synthesis identity required')
    oldpin=pin(plan['oldVoiceEvidence'],'old immutableV2 proof')
    selection=dict(protocol=REPAIR_PROTOCOL,plan=pin(dict(path=str(path),sha256=sha(path)),'frozen103 repair plan'),sourceVoiceEvidence=oldpin,sourceVoiceFingerprint=SOURCE_OLD_FINGERPRINT,repairSceneIds=plan['repairSceneIds'],expectedFullCount=103,expectedNewCount=15,expectedByteReusedCount=88,logicalGroupCount=96,adapterSHA256=sha(__file__),baseControllerSHA256=BASE_SHA256)
    identity=dict(full['identity'],repairSelection=selection);fp=digest(identity)
    if fp in(SOURCE_OLD_FINGERPRINT,full['fingerprint']):raise ValueError('New repair lineage must own a fresh output')
    inputs=full['inputs']+[selection['plan'],oldpin,dict(path=str(Path(__file__).resolve()),sha256=sha(__file__))]+[pin(plan[k],k)for k in ('semanticComponents','oldAsrReview','oldLevelReview','repairDecision')]+[pin(r['sourceWav'],'reused source')for r in plan['subsetReuse']]
    inputs=[{k:r[k]for k in ('path','sha256')}for r in inputs];preparation=digest(dict(synthesisIdentity=fp,inputs=inputs,script=full['script'],paragraphMapping=full['paragraphMapping']))
    folder=ROOT/'projects'/full['slug']/'production/voice-preparation'/preparation[:24];output=ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/fp[:24]
    manifest=copy.deepcopy(full['manifest']);manifest['paths']['script']=(folder/'narration-qwen.json').relative_to(ROOT).as_posix();manifest['tts']['outputDir']=output.relative_to(ROOT).as_posix();manifest['synthesisIdentity']=fp;manifest['repairSelection']=selection
    command=list(full['qwenSynthesisArgv']);command[8]=(folder/'voice-manifest.json').relative_to(ROOT).as_posix()
    return dict(full,identity=identity,fingerprint=fp,preparationFingerprint=preparation,inputs=inputs,stagingDirectory=str(folder),voiceOutputDirectory=str(output),manifest=manifest,qwenSynthesisArgv=command,qwenDryRunArgv=command+['--dry-run'])


def repair_spec(prov,plan,path):
    rows,oldpin,oldfp=validate_reuse(prov,plan);reused={r['newSceneId']for r in rows};old_reused={r['oldSceneId']for r in rows};missing=[s for s in prov['identity']['scenes']if s['id']not in reused]
    evidence={k:pin(plan[k],k)for k in ('semanticComponents','oldAsrReview','oldLevelReview','repairDecision')}
    if evidence['semanticComponents']not in prov['inputs'] or evidence['repairDecision']['sha256']!=DECISION_SHA256:raise ValueError('Current semantic source/exact root decision required')
    old=read(oldpin['path']);asr=read(evidence['oldAsrReview']['path']);levels=read(evidence['oldLevelReview']['path']);decision=read(evidence['repairDecision']['path'])
    if asr.get('voiceFingerprint')!=oldfp or asr.get('aggregateSHA256')!=old['aggregateWav']['sha256'] or asr.get('timingSHA256')!=old['timing']['sha256'] or len(asr.get('takes',[]))!=96 or len(asr.get('paragraphs',[]))!=25 or len(asr.get('boundaryWindows',[]))!=95:raise ValueError('Prior ASR not exact96/25/95 oldV2 voice')
    if levels.get('voiceFingerprint')!=oldfp or levels.get('canonicalWav')!=old['aggregateWav'] or levels.get('asrReview')!=evidence['oldAsrReview'] or len(levels.get('takes',[]))!=96 or len(levels.get('paragraphs',[]))!=25 or len(levels.get('joins',[]))!=95:raise ValueError('Prior level review differs from exact oldV2')
    flags={f.get('sceneId')for f in levels.get('flags',[])if f.get('kind')=='sustained-take-word-body-decline'}
    if flags & old_reused or flags!=SPLIT_LOGICAL_IDS-{'p011-c01'}:raise ValueError('All six actual old sustained holds must be replaced')
    split={f"p{r['paragraph']:03d}-c{r['sentenceIndexZeroBased']+1:02d}"for r in decision.get('splitLogicalGroups',[])}
    if decision.get('schemaVersion')!='06-02-root-clause-remediation-decision-v1' or decision.get('topicId')!='06.02' or split!=SPLIT_LOGICAL_IDS or (decision.get('viewerLogicalBeats'),decision.get('paragraphs'),decision.get('targetPhysicalVoiceComponents'),decision.get('targetExactRawReuseCount'),decision.get('targetNewComponents'))!=(96,25,103,88,15) or decision.get('currentAsr')!=evidence['oldAsrReview'] or decision.get('currentLevels')!=evidence['oldLevelReview'] or set(decision.get('remainingSustainedTakeFlags',[]))!=flags:raise ValueError('Root103/88/15 decision scope differs')
    # decision.currentVoice is a historical mutable publication-pointer reference;
    # operative old PCM is independently bound by immutable D proof above. Never
    # re-pin that live pointer after publishing this new voice.
    identity=dict(protocol=REPAIR_PROTOCOL,fullVoiceFingerprint=prov['fingerprint'],repairSelection=prov['identity']['repairSelection'],oldVoiceEvidence=dict(oldpin,fingerprint=oldfp),previousReviewPins=evidence,reuse=rows,missingScenes=missing,logicalGroups=prov['logicalGroups'],plan=pin(dict(path=str(path),sha256=sha(path)),'frozen103 repair plan'),adapterSHA256=sha(__file__),baseWorkerSHA256=BASE_SHA256)
    fp=digest(identity);folder=Path(prov['stagingDirectory'])/('repair-subset-'+fp[:24]);script=copy.deepcopy(prov['script']);script['scenes']=[s for s in script['scenes']if s['id']not in reused]
    manifest=copy.deepcopy(prov['manifest']);manifest['paths']['script']=(folder/'narration-missing-only.json').relative_to(ROOT).as_posix();manifest.update(engineSceneScope='missing-subset-only',fullSynthesisIdentity=prov['fingerprint'],repairFingerprint=fp,engineSceneIds=[s['id']for s in missing])
    command=list(prov['qwenSynthesisArgv']);command[8]=(folder/'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
    return dict(fingerprint=fp,identity=identity,rows=rows,missing=missing,stagingDirectory=str(folder),script=script,manifest=manifest,command=command)


def prepared(args):
    path=Path(args.repair_plan or PLAN).resolve()
    if PLAN_SHA256 is None or path!=PLAN.resolve() or not path.is_file() or sha(path)!=PLAN_SHA256:raise base.prep.Pending('Exact frozen06.02 103/88/15 repair plan pending/missing/changed')
    plan=read(path);full=reselect_full(selected_full(args,plan),plan,path);repair=repair_spec(full,plan,path)
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
    base.save=metadata_save
    for name in ['register_scenes','validate_engine_outputs','canonical_outputs','verify_complete','validate_launch_request','immutable_json']:setattr(base,name,globals()[name])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--topic',default='06.02');p.add_argument('--semantic-components',default='projects/shorts-leveldesign-06-02/voice-semantic-components-v3.json');p.add_argument('--repair-plan',default=str(PLAN));p.add_argument('--native-evidence',default='projects/shorts-leveldesign-06-02/voice-native-bundle-v1.json');p.add_argument('--native-qa',default='projects/shorts-leveldesign-06-02/native-voice-qa-v3.json');p.add_argument('--execute',action='store_true');p.add_argument('--wait-hours',type=float,default=6);a=p.parse_args()
    if a.topic!='06.02'or not math.isfinite(a.wait_hours)or not 0<a.wait_hours<=6:raise ValueError('Only finite selected06.02 repair supported')
    install_hooks()
    if a.execute:return base.execute(a)
    try:
        prov=active_prepared(a);out=base.output_of(prov);proof=verify_complete(prov,out)if (out/'voice-complete-proof.json').exists()else None
        print(json.dumps(dict(ready=True,topicId=a.topic,fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=prov['repair']['fingerprint'],fullSceneCount=len(base.scenes(prov)),missingOnlyCount=len(prov['repair']['missing']),reuseCount=len(prov['repair']['rows']),engineSceneIds=[s['id']for s in prov['repair']['missing']],existingComplete=bool(proof),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
    except (base.prep.Pending,FileNotFoundError)as e:print(json.dumps(dict(ready=False,reason=str(e),staged=False,reuseCopied=False,modelStarted=False),ensure_ascii=False))
if __name__=='__main__':main()
