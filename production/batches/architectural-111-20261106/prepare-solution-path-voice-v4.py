"""Thin11.05 V4 CPU voice preparation; default prints readiness without writing.

No model/import of Torch, subprocess, GPU/lease, ASR, media or Unity execution.
--stage writes only immutable request JSON, after current final narration and
all eight actual native-mode/agent-view proofs pass. Original drafts stay intact.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH_ID='architectural-111-20261106';TOPIC='11.05';SLUG='shorts-leveldesign-11-05'
PROJECT=ROOT/'projects'/SLUG;MEDIA=Path('C:/Users/1/Videos/YamyamProduction')/BATCH_ID;BASE=MEDIA/SLUG
CORE=HERE/'prepare-selected-voice.py';CORE_SHA='7fc1afac8b7c44b7752f0b53620150cd0989238cc4cc5866a14f40480034a020'
CONFIG=HERE/'solution-path-unity-source-v4/config.json';PROTOCOL='architectural111-11-05-voice-preparation-v4'
def sha(p):
 with Path(p).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def need(v,why):
 if not v:raise Pending(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
if sha(CORE)!=CORE_SHA:raise RuntimeError('Reviewed generic voice preparation source changed')
spec=importlib.util.spec_from_file_location('solution_voice_v4_private_generic',CORE);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
Pending=core.Pending
def project_file(value):
 p=Path(value);p=(ROOT/p).resolve()if not p.is_absolute()else p.resolve()
 need(p.is_relative_to(PROJECT.resolve()),'Input must belong to selected11.05 project');return p
def media_file(value):
 p=Path(value).resolve();need(p.is_relative_to(BASE.resolve()),'Native QA/media must belong to selected11.05 media');return p
def checked(row,scope=None):
 p=Path(row.get('path','')).resolve()
 if scope:need(p.is_relative_to(Path(scope).resolve()),'Evidence pin escaped selected scope')
 need(p.is_file()and re.fullmatch('[0-9a-f]{64}',row.get('sha256',''))and sha(p)==row['sha256'],'Missing or changed evidence input: '+str(p));return p
def authority():
 need(sha(CORE)==CORE_SHA,'Generic helper changed during preparation')
 c=read(ROOT/'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106'];b=read(HERE/'batch.json')
 need(c.get('userEvidence')=='111개 전체 제작 들어가줘'and c.get('status')not in('paused','stopped','cancelled')and c.get('automaticAdvanceWithinExactList')and not c.get('automaticAdvanceOutsideList')and not c.get('youtubeAuthorized')and c.get('humanFinalReviewRequired'),'Exact111 local authority is inactive')
 need(b.get('localFinalReviewOnly')and len(b['projects'])==111 and any(r['topicId']==TOPIC and r['slug']==SLUG and not r.get('productionComplete')for r in b['projects']),'Selected topic is not active in exact111')
 need(sha(ROOT/b['sourceCatalog'])==b.get('sourceCatalogSHA256'),'Authorized topic catalog changed')
 need(read(HERE/'checkpoint.json').get('currentTopicId')==TOPIC,'11.05 is not currently selected')
 cp=read(PROJECT/'checkpoint.json');need(cp.get('topicId')==TOPIC,'Project checkpoint topic differs');return cp
def current_inputs(narration=None):
 cp=authority();r=cp.get('expandedNarrationDraft',{});p=project_file(narration or r.get('path',''))
 need(p==project_file(r.get('path',''))and pin(p)=={k:r[k]for k in('path','sha256')},'Narration path/hash is not the actual checkpoint current pin')
 current=cp.get('currentProduction',{});need(current.get('expandedNarrationDraft')==pin(p)and cp.get('narrationDraftSHA256')==sha(p),'Checkpoint narration pins disagree')
 d=read(p);need(d.get('topicId')==TOPIC,'Narration topic differs')
 source=project_file(d.get('sourceFootage',{}).get('path',''));need(pin(source)==d.get('sourceFootage')==cp.get('sourceFootage')==current.get('sourceFootage'),'Actual narration/checkpoint source-footage pins disagree')
 return cp,p,d,source
def sentence_plan(d,narration_sha):
 ko=d.get('narrationKo');en=d.get('paragraphsEn');need(isinstance(ko,list)and len(ko)==14 and isinstance(en,list)and len(en)==14,'Complete14KO/EN paragraphs required')
 for text in ko+en:need(isinstance(text,str)and text and text==text.strip()and not core.PLACEHOLDER.search(text),'Empty/noncanonical/pending narration paragraph')
 rows=[]
 for n,text in enumerate(ko,1):
  parts=re.split(r'(?<=[.!?])\s+',text);need(' '.join(parts)==text,'Sentence splitting must reconstruct exact source spaces')
  if len(parts)>1:rows.append(dict(paragraph=n,components=[dict(text=t,reason='Exact complete canonical sentence; natural ending, no time/word quota')for t in parts]))
 groups=core.components_for(ko,dict(topicId=TOPIC,sourceNarrationSHA256=narration_sha,paragraphs=rows),narration_sha)
 script,mapping=core.make_scenes(d,groups)
 need(all(' '.join(r['canonicalText']for r in mapping if r['paragraph']==n)==text for n,text in enumerate(ko,1)),'14 paragraph reconstruction differs')
 return script,mapping
def final_narration(d,cp):
 current=cp.get('currentProduction',{});need(d.get('narrationFinalized')is True and d.get('ttsReady')is True and cp.get('expandedNarrationDraft',{}).get('finalized')is True and current.get('narrationFinalized')is True and current.get('ttsReady')is True,'Current narration is provisional, not finalized/TTS-ready; preserve false flags')
 view=copy.deepcopy(d);view['readyForDraftIntegration']=view['preTtsEligibility']=True
 core.validate_narration(view);return view  # Normalize only legacy API flags from actual true finality.
def source_rows(path):
 s=read(path);need(s.get('topicId')==TOPIC,'Footage topic differs');selected=[r for r in s.get('sources',[])if r.get('selectedForCut')is True];need(selected,'No actual adopted gameplay')
 out=[]
 for row in selected:
  need(isinstance(row.get('sourceId'),str)and bool(row['sourceId']),'Actual sourceId missing');alias=dict(row)
  need('id'not in alias or alias['id']==alias['sourceId'],'Conflicting source identity');alias['id']=alias['sourceId']
  out.append(core.validate_source_row(alias,SLUG))  # Alias never rewrites the original ledger.
 return out
def sample_proof(sample,mode,folder,cfg,index,global_previews):
 # Read-only pixel provenance: booleans or another mode/topic's previews are insufficient.
 camera=sample.get('camera');f=sample.get('frame');need(camera in('player','observer')and type(f)is int and 0<=f<cfg['frames'],'Actual camera/frame index required')
 image_path=checked(sample['nativeImage'],BASE);need(image_path==(Path(folder)/camera/f'{f:04}.jpg').resolve(),'QA image does not belong to this current mode/frame')
 row=index.get(str(image_path));need(row and row['mode']==mode and row['camera']==camera and row['sha256']==sample['nativeImage']['sha256'],'Actual viewed source image not in current native hash set')
 phone=checked(sample['mobilePreview'],BASE);need(global_previews.get(str(phone))==sample['mobilePreview']['sha256'],'Mobile sample missing from actual QA preview pins')
 crop=sample.get('sourceCropXYXY',[0,0,1920,1080]);allowed=[[0,0,1920,1080]]+([cfg['observerMeaningfulCropXYXY']]if camera=='observer'else[]);need(crop in allowed,'Unreviewed native preview crop')
 from PIL import Image,ImageChops
 with Image.open(image_path)as im:
  need(im.size==(1920,1080),'Native source image is not FHD');a=im.convert('RGB').crop(tuple(crop));height=round(a.height*375/a.width);expected=a.resize((375,height),Image.Resampling.LANCZOS)
 with Image.open(phone)as im:actual=im.convert('RGB');need(actual.size==expected.size and ImageChops.difference(actual,expected).getbbox()is None,'375 preview pixels do not derive from the claimed native mode/frame/crop')
 return[pin(image_path),pin(phone)]
def native_qa(evidence_path,qa_path):
 e=read(evidence_path);q=read(qa_path);cfg=read(CONFIG);modes=[r['id']for r in cfg['modes']]
 need(len(modes)==8 and len(set(modes))==8 and(cfg.get('frames'),cfg.get('fps'),cfg.get('width'),cfg.get('height'))==(3120,60,1920,1080),'Exact current V4 native mode/clock set required')
 need(e.get('topicId')==TOPIC and e.get('captureComplete')is True and set(e.get('capturedModes',[]))==set(modes)and len(e.get('capturedModes',[]))==8 and e.get('remainingModes')==[] and set(e.get('modeSources',{}))==set(modes),'All8 actual modes required; a subsetpilot is not voice readiness')
 staged=read(PROJECT/'native-controller-preparation-v4.json');need(staged.get('sourceStageComplete')is True and e.get('physicalInputFingerprint')==staged.get('fingerprint')and staged.get('config')==cfg,'Actual native source/config fingerprint differs')
 for r in staged.get('files',[]):checked(dict(path=str(ROOT/r['source']),sha256=r['sha256']),ROOT)
 native=core.validate_native(e,q,evidence_path,SLUG)
 need(q.get('topicId')==TOPIC and len(q.get('reviewedModes',[]))==8 and set(q.get('reviewedModes',[]))==set(modes),'All8 agent-reviewed native modes required')
 need(e.get('frameHashManifest')in e.get('captureProofs',[]),'Native frame hash manifest must be a captured evidence pin')
 frame_path=checked(e['frameHashManifest'],BASE);frames=read(frame_path);need(frames.get('physicalInputFingerprint')==e['physicalInputFingerprint'],'Native frame hash manifest fingerprint differs')
 index={str(Path(r['path']).resolve()):r for r in frames['frames']};need(len(index)==len(frames['frames']),'Duplicate native image pin')
 need(len(index)==len(modes)*2*cfg['frames'],'Full8-mode source frame hash coverage required')
 for mode in modes:
  attempt=media_file(e['modeSources'][mode]['attempt']);need(attempt.is_relative_to((BASE/'native-attempts').resolve()),'Actual native attempt escaped selected media')
  for camera in('player','observer'):
   for f in range(cfg['frames']):
    path=str((attempt/'capture'/mode/camera/f'{f:04}.jpg').resolve());row=index.get(path);need(row and row.get('mode')==mode and row.get('camera')==camera and re.fullmatch('[0-9a-f]{64}',row.get('sha256','')),'Current mode/camera source frame hash coverage differs')
 reviews=q.get('modeReviews',[]);need(len(reviews)==8 and {r.get('mode')for r in reviews}==set(modes),'Per-mode actual agent1080/375 evidence required')
 global_previews={str(checked(r,BASE)):r['sha256']for r in q.get('previewFiles',[])};proofs=[]
 for review in reviews:
  mode=review['mode'];need(review.get('actual1080Viewed')is True and review.get('actual375Viewed')is True,'Agent native/mobile viewing not recorded')
  attempt=media_file(e['modeSources'][mode]['attempt']);folder=attempt/'capture'/mode;need(attempt.is_relative_to((BASE/'native-attempts').resolve()),'Actual mode attempt escaped selected native source')
  samples=review.get('samples',[]);need(samples and {s.get('camera')for s in samples}=={'player','observer'},'Both actual native views required per mode')
  for s in samples:
   proofs.extend(sample_proof(s,mode,folder,cfg,index,global_previews))
 return native,proofs
def draft_plan(narration=None):
 cp,path,d,source=current_inputs(narration);script,mapping=sentence_plan(d,sha(path))
 return dict(topicId=TOPIC,ready=False,voiceReady=False,draftPlanOnly=True,sourceNarration=pin(path),sourceFootage=pin(source),paragraphCount=14,componentCount=len(script['scenes']),script=script,paragraphMapping=mapping,modelLoaded=False,jobLaunched=False),cp,d,path,source
def prepare(topic=TOPIC,native_path=None,native_qa_path=None,component_path=None,narration=None):
 need(topic==TOPIC,'This adapter only prepares selected11.05');need(component_path is None,'11.05 derives complete sentences; no old06/07 clause-policy input')
 plan,cp,d,path,source=draft_plan(narration);ep=project_file(native_path or PROJECT/'native-evidence-v4.json');qp=project_file(native_qa_path or PROJECT/'native-visual-qa-v4.json')
 missing=[]
 if not ep.is_file():missing.append('actual all8-mode native evidence missing')
 if not qp.is_file():missing.append('actual all8-mode agent1080/375 QA missing')
 try:eligible=final_narration(d,cp)
 except Pending as error:missing.append(str(error))
 need(not missing,'; '.join(missing))
 footage=source_rows(source);native,preview_proofs=native_qa(ep,qp)
 profile=core.validate_profile()  # Only after real script/source/native gates; no model import.
 script,mapping=sentence_plan(eligible,sha(path));identity=dict(protocol=PROTOCOL,topicId=TOPIC,scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']],tts={k:v for k,v in profile['tts'].items()if k not in('filenameStem','gpuMinimumFreeMiB','gpuProfileReason')},modelPins=profile['modelPins'],referenceSHA256=profile['referenceSHA256'],referenceTextSHA256=profile['referenceTextSHA256'],engine=profile['engine'],guard=profile['guard'],rawPcmPolicy=profile['rawPcmPolicy']);identity_fp=core.fp(identity)
 inputs=[pin(p)for p in[path,source,ep,qp,CONFIG,PROJECT/'checkpoint.json',PROJECT/'native-controller-preparation-v4.json',core.PROFILE,CORE,Path(__file__)]]+native['captureArtifacts']+native['sampledPreviewArtifacts']+preview_proofs
 inputs += [pin(ROOT/profile[k])for k in('reference','referenceText','python')]+[pin(ROOT/profile[k]['path'])for k in('engine','guard')]+[dict(path=str(ROOT/profile['model']/r['path']),sha256=r['sha256'])for r in profile['modelPins']]+[dict(path=r['path'],sha256=r['sha256'])for r in footage]
 inputs=list({r['path']:r for r in inputs}.values());prep_fp=core.fp(dict(synthesisIdentity=identity_fp,inputs=inputs,script=script,paragraphMapping=mapping));target=PROJECT/'production/voice-preparation'/prep_fp[:24];manifest_path=target/'voice-manifest.json';output=ROOT/'shared/output'/BATCH_ID/'11-05/voice-attempts'/identity_fp[:24]
 manifest=dict(schemaVersion=2,slug=SLUG,revision=PROTOCOL,paths=dict(script=(target/'narration-qwen.json').relative_to(ROOT).as_posix()),editing=dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation'),tts=dict(profile['tts'],reference=profile['reference'],referenceText=profile['referenceText'],model=profile['model'],outputDir=output.relative_to(ROOT).as_posix()),sourceNarrationSHA256=sha(path),synthesisIdentity=identity_fp,rawPcmPolicy=profile['rawPcmPolicy'])
 command=[str(ROOT/profile['python']),'-u','-X','utf8',str(ROOT/profile['engine']['path']),'--project',SLUG,'--manifest',manifest_path.relative_to(ROOT).as_posix(),'--batch-size','1','--device','cuda:0']
 return dict(topicId=TOPIC,slug=SLUG,ready=True,voiceReady=True,fingerprint=identity_fp,preparationFingerprint=prep_fp,identity=identity,inputs=inputs,sourceNarration=pin(path),nativeEvidence=pin(ep),nativeVisualQa=pin(qp),footage=footage,native=native,script=script,manifest=manifest,paragraphMapping=mapping,stagingDirectory=str(target),voiceOutputDirectory=str(output),qwenDryRunArgv=command+['--dry-run'],qwenSynthesisArgv=command,launchAuthorizedByThisTool=False,modelLoaded=False,jobLaunched=False,actualSpeechListening=False,humanFinalReview=False)
def immutable_stage(result):
 authority();need(result.get('topicId')==TOPIC and result.get('voiceReady')is True,'Unready draft cannot stage voice inputs')
 fresh=prepare(native_path=result['nativeEvidence']['path'],native_qa_path=result['nativeVisualQa']['path'],narration=result['sourceNarration']['path'])
 need(all(result[k]==fresh[k]for k in('fingerprint','preparationFingerprint','identity','inputs','script','manifest','paragraphMapping')),'Prepared request changed or bypassed current evidence gates')
 return core.immutable_stage(fresh)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--narration');p.add_argument('--native-evidence');p.add_argument('--native-qa');p.add_argument('--draft-plan',action='store_true');p.add_argument('--stage',action='store_true');a=p.parse_args()
 try:
  if a.draft_plan:result=draft_plan(a.narration)[0];need(not a.stage,'Draft planning never stages')
  else:
   result=prepare(native_path=a.native_evidence,native_qa_path=a.native_qa,narration=a.narration)
   if a.stage:result['stagedFiles']=immutable_stage(result)
  if not a.draft_plan:result={k:result[k]for k in('topicId','ready','voiceReady','fingerprint','preparationFingerprint','modelLoaded','jobLaunched')}|dict(staged=a.stage)
 except (Pending,OSError,ValueError,KeyError)as error:
  result=dict(topicId=TOPIC,ready=False,voiceReady=False,notReadyReason=str(error),staged=False,modelLoaded=False,jobLaunched=False)
  try:
   plan=draft_plan(a.narration)[0];result['draftPlanSummary']={k:plan[k]for k in('sourceNarration','sourceFootage','paragraphCount','componentCount','draftPlanOnly')}
  except (Pending,OSError,ValueError,KeyError):pass
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
