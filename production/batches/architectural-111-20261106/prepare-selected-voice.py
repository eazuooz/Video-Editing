"""Read-only selected111 voice preflight; --stage only writes immutable Qwen input JSON.

No engine/model import, subprocess, TTS worker, GPU lease, output audio or platform action.
The caller owns later singleton/resource checks and actual synthesis. Current07.04 opener
placeholder must be resolved, footage adopted and native capture sampled before staging.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BATCH_ID='architectural-111-20261106'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction')/BATCH_ID
PROFILE=HERE/'approved-selected-voice-profile-v1.json'
AUTH='explicitArchitectural111Batch20261106'
APPROVED_PROFILE_SHA256='378e12edc96c5d006ca9407ed36da13d1eff7e882cdc2670acdfd749b15b0075'
_HASH_CACHE={}
PROTOCOL='architectural111-selected-voice-preparation-v1'
PLACEHOLDER=re.compile(r'^\s*\[|미확정|작성\s*대기|actual.game opening pending|TODO|TBD|placeholder',re.I)
MODEL_SUFFIXES={'.safetensors','.bin'}
MODEL_NAMES={'config.json','configuration.json','generation_config.json','preprocessor_config.json','tokenizer_config.json','vocab.json','merges.txt','tokenizer.model'}

class Pending(RuntimeError):pass

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    path=Path(path);stat=path.stat();key=(str(path.resolve()),stat.st_size,stat.st_mtime_ns)
    if key not in _HASH_CACHE:
        with path.open('rb') as handle:_HASH_CACHE[key]=hashlib.file_digest(handle,'sha256').hexdigest()
    return _HASH_CACHE[key]
def fp(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
def pin(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def repo(value):
    p=(ROOT/value).resolve()
    if not p.is_relative_to(ROOT.resolve()):raise ValueError('Input escapes repository')
    return p

def selected_path(value,slug):
    p=Path(value)
    if not p.is_absolute():p=repo(value)
    p=p.resolve()
    if not (p.is_relative_to(ROOT.resolve()) or p.is_relative_to((MEDIA/slug).resolve())):raise ValueError('Evidence/media input escapes selected repository/media scope')
    return p

def verify_pin(row,slug):
    p=selected_path(row['path'],slug)
    if not p.is_file() or not row.get('sha256') or sha(p)!=row['sha256']:raise Pending('Missing or changed evidence artifact: '+str(p))
    return pin(p)

def validate_narration(draft):
    if draft.get('readyForDraftIntegration') is not True or draft.get('preTtsEligibility') is not True:raise Pending('Narration is not finalized for TTS')
    if draft.get('placeholderParagraphs'):raise Pending('Narration still declares placeholder paragraphs')
    ko=draft.get('narrationKo');en=draft.get('paragraphsEn')
    if not isinstance(ko,list) or not ko or not isinstance(en,list) or len(ko)!=len(en):raise Pending('Matching complete KO/EN paragraphs are required')
    for n,(a,b) in enumerate(zip(ko,en),1):
        if not isinstance(a,str) or not isinstance(b,str) or not a.strip() or not b.strip() or a!=a.strip() or b!=b.strip():raise Pending(f'Empty or uncanonical paragraph{n}')
        if PLACEHOLDER.search(a) or PLACEHOLDER.search(b):raise Pending(f'Pending/placeholder text in paragraph{n}')
    return ko

def validate_source_row(row,slug):
    if row.get('selectedForCut') is not True:raise Pending('Footage is not actually adopted')
    if row.get('rightsVerified') is not True and row.get('rightsReviewed') is not True:raise Pending('Adopted footage rights are not explicitly verified')
    if row.get('decodedDimensionsVerified') is not True or min(row.get('width',0),row.get('height',0))<1080:raise Pending('Adopted footage is not actual FHD')
    if row.get('visualSequenceInspected') is not True:raise Pending('Adopted footage has not been actually viewed')
    role=row.get('editorialRole',row.get('sourceRole',row.get('sourceKind')))
    if role!='independent-gameplay':raise Pending('Adopted source is not independent gameplay')
    actual=verify_pin(row,slug)
    return dict(id=row['id'],sourceUrl=row.get('sourceUrl'),sourceRole=role,**actual)

def validate_native(evidence,qa,evidence_path,slug):
    if evidence.get('topicId')!=slug.removeprefix('shorts-leveldesign-').replace('-','.') or evidence.get('captureComplete') is not True:raise Pending('Actual selected native capture is not complete')
    native_fp=evidence.get('fingerprint')
    if not isinstance(native_fp,str) or not re.fullmatch('[0-9a-f]{64}',native_fp):raise Pending('Native fingerprint missing')
    if qa.get('voicePreparationAllowed') is not True or qa.get('nativeFingerprint')!=native_fp or qa.get('nativeEvidenceSHA256')!=sha(evidence_path):raise Pending('Sampled native QA is missing or stale')
    captures=evidence.get('captureProofs',[])
    if not captures:raise Pending('Actual capture/config/trace artifact pins are required')
    capture_pins=[verify_pin(p,slug) for p in captures]
    if not qa.get('sampledFrames') or not qa.get('sampledNativeViews') or qa.get('phonePreviewWidth')!=375:raise Pending('Native frame/view and375px sample QA is required')
    previews=qa.get('previewFiles',[])
    if not previews:raise Pending('Sampled visual QA must bind actual preview images')
    return {'fingerprint':native_fp,'captureArtifacts':capture_pins,'sampledPreviewArtifacts':[verify_pin(p,slug) for p in previews]}

def components_for(ko,plan,narration_sha):
    if plan is None:return {i:[{'text':t,'reason':'Canonical complete paragraph; no component split requested'}] for i,t in enumerate(ko,1)}
    if plan.get('sourceNarrationSHA256')!=narration_sha:raise Pending('Semantic component plan narration hash is stale')
    result={i:[{'text':t,'reason':'Canonical complete paragraph; no component split requested'}] for i,t in enumerate(ko,1)};seen=set()
    for row in plan.get('paragraphs',[]):
        n=row.get('paragraph');parts=row.get('components',[])
        if not isinstance(n,int) or n in seen or n not in result or len(parts)<2:raise Pending('Invalid semantic component paragraph')
        seen.add(n);canonical=ko[n-1];sentences=re.split(r'(?<=[.!?])\s+',canonical)
        boundary={0};position=0
        for i,sentence in enumerate(sentences):position+=len(sentence);boundary.add(position);position+=1
        cursor=0
        for item in parts:
            text=item.get('text');reason=item.get('reason','')
            if not isinstance(text,str) or not text or not reason.strip() or text!=text.strip():raise Pending('Each semantic component needs exact text and a reason')
            end=cursor+len(text)
            if canonical[cursor:end]!=text or (cursor and cursor-1 not in boundary) or end not in boundary:raise Pending('Semantic component bisects a sentence or changes canonical prose')
            cursor=end+1
        if ' '.join(x['text'] for x in parts)!=canonical:raise Pending('Semantic components omit, repeat or change canonical prose')
        result[n]=parts
    return result

def make_scenes(draft,groups):
    scenes=[];mapping=[]
    for n,text in enumerate(draft['narrationKo'],1):
        parts=groups[n];cursor=0;ids=[]
        for j,item in enumerate(parts,1):
            sid=f'p{n:03d}'+(f'-c{j:02d}' if len(parts)>1 else '')
            scenes.append({'id':sid,'title':draft['titleKo'],'lines':[item['text']]});ids.append(sid)
            mapping.append({'paragraph':n,'sceneId':sid,'component':j,'componentCount':len(parts),'sourceCharRange':[cursor,cursor+len(item['text'])],'canonicalText':item['text'],'reason':item['reason']});cursor+=len(item['text'])+1
        if ' '.join(s['lines'][0] for s in scenes if s['id'] in ids)!=text:raise AssertionError('Canonical paragraph reconstruction failed')
    return {'scenes':scenes},mapping

def validate_profile():
    if sha(PROFILE)!=APPROVED_PROFILE_SHA256:raise Pending('Approved profile file changed; explicit source review is required')
    profile=read(PROFILE)
    if profile['model']!='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base' or profile['reference']!='shared/voice-reference/reference-15-35s.wav' or profile['referenceText']!='shared/voice-reference/reference-15-35s.ko.txt':raise Pending('Approved model/reference paths changed')
    for name in ['engine','guard']:verify_pin(profile[name],'unused')
    for name in ['reference','referenceText']:
        if sha(repo(profile[name]))!=profile[name+'SHA256']:raise Pending('Approved reference changed')
    model=repo(profile['model']);files=[p for p in sorted(model.rglob('*')) if p.is_file() and '.cache' not in p.parts and (p.suffix in MODEL_SUFFIXES or p.name in MODEL_NAMES)]
    actual=[{'path':p.relative_to(model).as_posix(),'sha256':sha(p)} for p in files]
    if actual!=profile['modelPins']:raise Pending('Approved model/tokenizer files changed')
    if not repo(profile['python']).is_file():raise Pending('Approved Qwen Python missing')
    tts=profile['tts']
    if tts['engine']!='qwen3-tts' or tts['renderMode']!='scene' or tts['language']!='Korean' or float(tts['edgeFadeSeconds'])!=0 or float(tts['sceneGapSeconds'])!=0:raise Pending('Natural scene profile changed')
    if profile['rawPcmPolicy']['speechSpeed']!=1 or profile['rawPcmPolicy']['timeStretch'] or profile['rawPcmPolicy']['trimSpeechOrBreath']:raise Pending('Speech PCM preservation policy changed')
    return profile

def prepare(topic,native_path,native_qa,component_path=None):
    if not re.fullmatch(r'\d{2}\.\d{2}',topic):raise ValueError('Use an exact catalog topicId')
    slug='shorts-leveldesign-'+topic.replace('.','-');project=ROOT/'projects'/slug
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH];batch=read(HERE/'batch.json')
    if control.get('status') in ['paused','cancelled','stopped'] or control.get('userEvidence')!='111개 전체 제작 들어가줘' or control.get('automaticAdvanceOutsideList') or not control.get('humanFinalReviewRequired') or control.get('youtubeAuthorized'):raise Pending('Current finite production authorization is not active')
    selected=[r for r in batch['projects'] if r['topicId']==topic and r['slug']==slug]
    if len(batch['projects'])!=111 or len(selected)!=1 or not batch.get('localFinalReviewOnly'):raise Pending('Topic is outside the exact111 local-review batch')
    if selected[0].get('productionComplete') is True:raise Pending('Completed film is not selected for a new synthesis')
    if sha(repo(batch['sourceCatalog']))!=batch['sourceCatalogSHA256']:raise Pending('Authorized topic catalog changed')
    narration_path=project/'narration-draft.json';draft=read(narration_path);ko=validate_narration(draft)
    if draft.get('topicId')!=topic:raise Pending('Narration topic mismatch')
    sources_path=project/'source-footage.json';sources=read(sources_path);adopted=[r for r in sources.get('sources',[]) if r.get('selectedForCut') is True]
    if not adopted:raise Pending('No independent footage is adopted')
    footage=[validate_source_row(r,slug) for r in adopted]
    np=selected_path(native_path,slug);qp=selected_path(native_qa,slug)
    if not np.is_file() or not qp.is_file():raise Pending('Actual native capture and sampled QA records are required')
    native=validate_native(read(np),read(qp),np,slug)
    comp=selected_path(component_path,slug) if component_path else None
    if comp and not comp.is_file():raise Pending('Semantic component plan missing')
    groups=components_for(ko,read(comp) if comp else None,sha(narration_path));script,mapping=make_scenes(draft,groups)
    profile=validate_profile()
    inputs=[pin(narration_path),pin(sources_path),pin(np),pin(qp),pin(PROFILE),pin(Path(__file__))]
    inputs += [dict(path=row['path'],sha256=row['sha256']) for row in footage]
    inputs += native['captureArtifacts']+native['sampledPreviewArtifacts']
    inputs += [pin(repo(profile[name])) for name in ['reference','referenceText','python']]
    inputs += [dict(path=str(repo(profile[name]['path'])),sha256=profile[name]['sha256']) for name in ['engine','guard']]
    inputs += [dict(path=str(repo(profile['model'])/row['path']),sha256=row['sha256']) for row in profile['modelPins']]
    inputs=list({row['path']:row for row in inputs}.values())
    if comp:inputs.append(pin(comp))
    identity={'protocol':PROTOCOL,'topicId':topic,'scenes':[{'id':s['id'],'lines':s['lines']} for s in script['scenes']],'tts':{k:v for k,v in profile['tts'].items() if k not in ['filenameStem','gpuMinimumFreeMiB','gpuProfileReason']},'modelPins':profile['modelPins'],'referenceSHA256':profile['referenceSHA256'],'referenceTextSHA256':profile['referenceTextSHA256'],'engine':profile['engine'],'guard':profile['guard'],'rawPcmPolicy':profile['rawPcmPolicy']}
    identity_fp=fp(identity)
    preparation_fp=fp({'synthesisIdentity':identity_fp,'inputs':inputs,'script':script,'paragraphMapping':mapping})
    prepared=project/'production/voice-preparation'/preparation_fp[:24]
    script_path=prepared/'narration-qwen.json';manifest_path=prepared/'voice-manifest.json';output=ROOT/'shared/output'/BATCH_ID/topic.replace('.','-')/'voice-attempts'/identity_fp[:24]
    manifest={'schemaVersion':2,'slug':slug,'revision':PROTOCOL,'paths':{'script':script_path.relative_to(ROOT).as_posix()},'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-example-and-explanation'},'tts':dict(profile['tts'],reference=profile['reference'],referenceText=profile['referenceText'],model=profile['model'],outputDir=output.relative_to(ROOT).as_posix()),'sourceNarrationSHA256':sha(narration_path),'synthesisIdentity':identity_fp,'rawPcmPolicy':profile['rawPcmPolicy']}
    command=[str(repo(profile['python'])),'-u','-X','utf8',str(repo(profile['engine']['path'])),'--project',slug,'--manifest',manifest_path.relative_to(ROOT).as_posix(),'--batch-size','1','--device','cuda:0']
    return {'topicId':topic,'slug':slug,'ready':True,'fingerprint':identity_fp,'preparationFingerprint':preparation_fp,'identity':identity,'inputs':inputs,'footage':footage,'native':native,'script':script,'manifest':manifest,'paragraphMapping':mapping,'stagingDirectory':str(prepared),'voiceOutputDirectory':str(output),'qwenDryRunArgv':command+['--dry-run'],'qwenSynthesisArgv':command,'launchAuthorizedByThisTool':False,'resourcePolicy':'Later caller must revalidate current inputs, existing singleton/child and user-game/Unity state; trusted Qwen guard owns its own GPU lease. This preparation creates no worker or lease.','actualSpeechListening':False,'humanFinalReview':False}

def immutable_stage(result):
    if result.get('ready') is not True:raise Pending('Unready narration/evidence cannot be staged')
    if fp(result['identity'])!=result['fingerprint'] or result['manifest']['synthesisIdentity']!=result['fingerprint']:raise Pending('Prepared synthesis identity changed')
    target=Path(result['stagingDirectory']).resolve()
    if not target.is_relative_to((ROOT/'projects'/result['slug']/'production/voice-preparation').resolve()):raise ValueError('Staging path escaped selected project')
    files={'narration-qwen.json':result['script'],'voice-manifest.json':result['manifest'],'paragraph-mapping.json':{'topicId':result['topicId'],'sourceNarrationSHA256':result['manifest']['sourceNarrationSHA256'],'entries':result['paragraphMapping']},'preparation.json':result}
    rendered={name:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8') for name,value in files.items()}
    for name,data in rendered.items():
        p=target/name
        if p.exists() and p.read_bytes()!=data:raise Pending('Existing immutable staged request differs; preserve and inspect')
    for row in result['inputs']:
        if sha(row['path'])!=row['sha256']:raise Pending('Preparation inputs changed before staging')
    target.mkdir(parents=True,exist_ok=True)
    for name,data in rendered.items():
        p=target/name
        if not p.exists():
            try:
                with p.open('xb') as handle:handle.write(data)
            except FileExistsError:
                if p.read_bytes()!=data:raise Pending('Concurrent staged input collision')
    return [{'path':str(target/name),'sha256':sha(target/name)} for name in files]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--topic',default='07.04');parser.add_argument('--stage',action='store_true');parser.add_argument('--native-evidence');parser.add_argument('--native-qa');parser.add_argument('--semantic-components');args=parser.parse_args()
    slug='shorts-leveldesign-'+args.topic.replace('.','-')
    evidence=args.native_evidence or f'projects/{slug}/native-evidence-v1.json';qa=args.native_qa or f'projects/{slug}/native-visual-qa-v1.json'
    try:
        result=prepare(args.topic,evidence,qa,args.semantic_components)
        staged=immutable_stage(result) if args.stage else []
        print(json.dumps({k:result[k] for k in ['topicId','ready','fingerprint','stagingDirectory','qwenDryRunArgv','qwenSynthesisArgv','launchAuthorizedByThisTool']}|{'stagedFiles':staged,'readOnly':not args.stage},ensure_ascii=False,indent=2))
    except (Pending,FileNotFoundError) as error:
        print(json.dumps({'topicId':args.topic,'ready':False,'reason':str(error),'stagedFiles':[],'modelLoaded':False,'jobLaunched':False},ensure_ascii=False,indent=2))
        if args.stage:raise SystemExit(2)

if __name__=='__main__':main()
