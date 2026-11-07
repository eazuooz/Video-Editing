"""Synthetic CPU fixtures for the bounded103/88/15 voice adapter. No production staging/models."""
import argparse,copy,hashlib,importlib.util,json,struct,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prospect103_repair_cpu',HERE/'run-prospect-refuge-voice-repair-v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return dict(path=str(p),sha256=m.sha(p))
def wav(p,value,n=48):
 p.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,n,'NONE','not compressed'));w.writeframes(struct.pack('<h',value)*n)
 return m.base.wav_info(p)

class Repair103Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory(prefix='06-103-voice-repair-cpu-');c.root=Path(c.tmp.name);c.original=(m.ROOT,m.base.ROOT,m.SOURCE_OLD_FINGERPRINT,m.DECISION_SHA256);m.ROOT=c.root;m.base.ROOT=c.root
  c.oldscenes=[]
  for para in range(1,26):
   for j in range(4 if para<=18 or para>=23 else 3):
    sid=f'p{para:03d}-c{j+1:02d}';text=f'Synthetic first clause {sid}, second complete clause.'if sid in m.SPLIT_LOGICAL_IDS else f'Synthetic complete sentence {sid}.'
    if sid=='p004-c01':text='지금 머무는 은신처와 바로 앞의 조망 공간이 현재의 기준입니다.'
    if sid=='p011-c01':text='층과 층을 잇는 램프를 따라 올라가면, 아래의 열린 공간을 점점 더 넓게 바라볼 수 있습니다.'
    if sid=='p025-c03':text='중요한 것은 숨을 곳을 많이 놓는 것이 아니라, 어디에서 무엇을 읽고 다음 어디로 움직일 수 있는지를 연결하는 겁니다.'
    c.oldscenes.append(dict(id=sid,lines=[text]))
  profile=dict(protocol='synthetic-profile',topicId='06.02',tts=dict(language='Korean',speechSpeed=1),modelPins=[dict(path='model',sha256='1'*64)],referenceSHA256='2'*64,referenceTextSHA256='3'*64,engine=dict(path='engine',sha256='4'*64),guard=dict(path='guard',sha256='5'*64),rawPcmPolicy=dict(noFade=True,speechSpeed=1))
  oldidentity=dict(profile,scenes=c.oldscenes);oldfp=m.digest(oldidentity);m.SOURCE_OLD_FINGERPRINT=oldfp;c.oldout=c.root/'shared/output/architectural-111-20261106/06-02/voice-attempts'/oldfp[:24]
  for i,scene in enumerate(c.oldscenes):wav(c.oldout/'chunks'/(scene['id']+'-scene.wav'),i+1)
  oldprov=dict(topicId='06.02',fingerprint=oldfp,identity=oldidentity,paragraphMapping=[dict(sceneId=s['id'],paragraph=int(s['id'][1:4]),canonicalText=s['lines'][0])for s in c.oldscenes]);c.old=m.original['canonical_outputs'](oldprov,c.oldout,{});c.oldpin=dump(c.oldout/'voice-complete-proof.json',c.old)
  paragraphs=[];logical=[];c.ko=[]
  for n in range(1,26):
   components=[];cursor=0;texts=[]
   for li,old in enumerate([s for s in c.oldscenes if int(s['id'][1:4])==n]):
    lid=old['id'];text=old['lines'][0]
    if lid=='p004-c01':text=text.removeprefix('지금 ')
    if lid=='p011-c01':text='아래층과 위층을 이어 주는 경사로인 램프를 따라 올라가면, 아래의 열린 공간을 점점 더 넓게 바라볼 수 있습니다.'
    if lid=='p025-c03':text=text.replace('숨을 곳을','은신처를',1)
    pieces=[text]
    if lid in m.SPLIT_LOGICAL_IDS:a,b=text.split(', ',1);pieces=[a+',',b]
    start=cursor;partcursor=0;ids=[]
    for part,textpart in enumerate(pieces,1):
     sid=f'p{n:03d}-c{len(components)+1:02d}';ids.append(sid);components.append(dict(text=textpart,reason='Synthetic approved semantic breath clause',physicalSceneId=sid,logicalSceneId=lid,logicalSentenceIndexZeroBased=li,logicalPartIndex=part,logicalPartCount=len(pieces),sourceCharRange=[cursor,cursor+len(textpart)],logicalSourceCharRange=[partcursor,partcursor+len(textpart)],canonicalJoinerAfter=' 'if part<len(pieces)else''));cursor+=len(textpart)+1;partcursor+=len(textpart)+1
    logical.append(dict(id=lid,logicalSceneId=lid,paragraph=n,logicalSentenceIndexZeroBased=li,canonicalText=text,sourceCharRange=[start,start+len(text)],physicalSceneIds=ids,canonicalInterComponentJoiner=' '));texts.append(text)
   paragraphs.append(dict(paragraph=n,components=components));c.ko.append(' '.join(texts))
  c.semantic=dict(topicId='06.02',sourceNarrationSHA256='a'*64,paragraphs=paragraphs,logicalGroups=logical);groups,logical,physical=m.component_contract(c.ko,c.semantic,'a'*64);script,mapping=m.base.prep.make_scenes(dict(titleKo='Synthetic test',narrationKo=c.ko),groups);c.scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']];semantic=dump(c.root/'semantic-v3.json',c.semantic)
  asr=dump(c.root/'old-asr.json',dict(voiceFingerprint=oldfp,aggregateSHA256=c.old['aggregateWav']['sha256'],timingSHA256=c.old['timing']['sha256'],takes=[{}]*96,paragraphs=[{}]*25,boundaryWindows=[{}]*95));levels=dump(c.root/'old-levels.json',dict(voiceFingerprint=oldfp,canonicalWav=c.old['aggregateWav'],asrReview=asr,takes=[{}]*96,paragraphs=[{}]*25,joins=[{}]*95,flags=[dict(kind='sustained-take-word-body-decline',sceneId=s)for s in sorted(m.SPLIT_LOGICAL_IDS-{'p011-c01'})]))
  decision=dump(c.root/'root-decision.json',dict(schemaVersion='06-02-root-clause-remediation-decision-v1',topicId='06.02',viewerLogicalBeats=96,paragraphs=25,targetPhysicalVoiceComponents=103,targetExactRawReuseCount=88,targetNewComponents=15,currentAsr=asr,currentLevels=levels,currentVoice=dict(path='historical-mutable-pointer-not-read',sha256='b'*64),remainingSustainedTakeFlags=sorted(m.SPLIT_LOGICAL_IDS-{'p011-c01'}),splitLogicalGroups=[dict(paragraph=int(s[1:4]),sentenceIndexZeroBased=int(s[6:])-1)for s in sorted(m.SPLIT_LOGICAL_IDS)]));m.DECISION_SHA256=decision['sha256']
  oldmap={s['id']:(s,w)for s,w in zip(c.oldscenes,c.old['sceneWavs'])};reuse=[]
  for g in logical:
   lid=g['logicalSceneId']
   if lid not in m.REPLACED_OLD_IDS:
    source,w=oldmap[lid];reuse.append(dict(oldSceneId=lid,newSceneId=g['physicalSceneIds'][0],canonicalText=source['lines'][0],sourceWav=w,sourceVoiceEvidence=dict(c.oldpin,fingerprint=oldfp),reuseReason='Synthetic exact text/raw/profile reuse with explicit renumbering'))
  reused={q['newSceneId']for q in reuse};newidentity=dict(profile,scenes=c.scenes);basefp=m.digest(newidentity);stage=c.root/'projects/shorts-leveldesign-06-02/production/voice-preparation/initial';out=c.root/'shared/output/architectural-111-20261106/06-02/voice-attempts'/basefp[:24]
  c.plan=dict(schemaVersion='06-02-voice-subset-repair-plan-v2',topicId='06.02',sourceNarrationSHA256='a'*64,semanticComponents=semantic,oldVoiceEvidence=c.oldpin,oldAsrReview=asr,oldLevelReview=levels,repairDecision=decision,repairSceneIds=[s['id']for s in c.scenes if s['id']not in reused],expectedFullComponentCount=103,expectedMissingComponentCount=15,expectedReuseComponentCount=88,subsetReuse=reuse);c.planpath=c.root/'plan-v2.json';dump(c.planpath,c.plan)
  c.full=dict(topicId='06.02',slug='shorts-leveldesign-06-02',fingerprint=basefp,identity=newidentity,logicalGroups=logical,physicalSourceComponents=physical,inputs=[semantic],script=script,paragraphMapping=mapping,manifest=dict(slug='shorts-leveldesign-06-02',sourceNarrationSHA256='a'*64,paths=dict(script='old.json'),tts=dict(model='same-approved',outputDir=out.relative_to(c.root).as_posix()),editing=dict(exampleSeconds=0),rawPcmPolicy=profile['rawPcmPolicy'],synthesisIdentity=basefp),stagingDirectory=str(stage),voiceOutputDirectory=str(out),qwenSynthesisArgv=['python','-u','-X','utf8','render_narration.py','--project','shorts-leveldesign-06-02','--manifest','old.json','--batch-size','1','--device','cuda:0'])
  c.new=m.reselect_full(c.full,c.plan,c.planpath);c.repair=m.repair_spec(c.new,c.plan,c.planpath);c.prov=dict(c.new,repair=c.repair);c.out=Path(c.new['voiceOutputDirectory']);c.folder=Path(c.repair['stagingDirectory']);c.folder.mkdir(parents=True)
  for name,obj in [('narration-missing-only.json',c.repair['script']),('voice-missing-only-manifest.json',c.repair['manifest']),('subset-repair-preparation.json',dict(repairFingerprint=c.repair['fingerprint'],fullVoiceFingerprint=c.prov['fingerprint'],repairIdentity=c.repair['identity'],command=c.repair['command']))]:dump(c.folder/name,obj)
  (c.folder/'repair-adapter-source.py').write_bytes(Path(m.__file__).read_bytes());c.attempt=c.out/'engine-attempts/synthetic';c.attempt.mkdir(parents=True);c.req=dict(protocol=m.base.PROTOCOL,fingerprint=c.prov['fingerprint'],identity=c.prov['identity'],repairFingerprint=c.repair['fingerprint'],command=c.repair['command'],engineSceneScope='missing-subset-only',engineSceneIds=[s['id']for s in c.repair['missing']],subsetPins=m.subset_pins(c.prov));rp=dump(c.attempt/'request.json',c.req);c.pending=dict(attempt=str(c.attempt),requestPins=[rp])
 @classmethod
 def tearDownClass(c):m.ROOT,m.base.ROOT,m.SOURCE_OLD_FINGERPRINT,m.DECISION_SHA256=c.original;c.tmp.cleanup()
 def reject_contract(self,edit):
  plan=copy.deepcopy(self.semantic);edit(plan)
  with self.assertRaises((ValueError,KeyError)):m.component_contract(self.ko,plan,'a'*64)
 def test_exact103physical96logical25paragraphs(self):self.assertEqual((len(self.scenes),len(self.new['logicalGroups']),len(self.ko)),(103,96,25))
 def eligibility_fixture(self):
  np=dict(path='immutable-v4.json',sha256='a'*64);cp=dict(path='components-v3.json',sha256='b'*64);qa=dict(sourceNarration=np,semanticComponents=cp,logicalGroupCount=96,physicalComponentCount=103,preTtsEligible=True,voicePreparationAllowed=True);con=dict(schemaVersion='06-02-source-clause-remediation-conformance-v1',topicId='06.02',logicalSentenceGroups=96,physicalVoiceUnits=103,exactReuseTextCandidates=88,newPhysicalUnits=15,rootDecision=dict(sha256=m.DECISION_SHA256),newArtifacts=[np,cp],internalSourceReviewed=True,manualSourceSemanticReview=True,exactParagraphAndLogicalCharReconstruction=True,canonicalInterComponentSpacesOnly=True,all14SourceLearningRolesAndOrderRetained=True);draft=dict(readyForDraftIntegration=False,preTtsEligibility=dict(actualNewAudioUnverified=True),ttsReady=False)
  return draft,qa,np,cp,con
 def test_external_v3_eligibility_does_not_rewrite_immutable_candidate(self):
  draft,qa,np,cp,con=self.eligibility_fixture();before=copy.deepcopy(draft);view=m.source_eligibility_view(draft,qa,np,cp,con);self.assertTrue(view['preTtsEligibility']);self.assertEqual(draft,before);self.assertFalse(draft['ttsReady'])
 def test_old_v2_native_permission_cannot_authorize103_source(self):
  draft,qa,np,cp,con=self.eligibility_fixture();qa.pop('sourceNarration')
  with self.assertRaises(m.base.prep.Pending):m.source_eligibility_view(draft,qa,np,cp,con)
 def test_unreviewed_or_stale_source_conformance_rejects(self):
  for field in('manualSourceSemanticReview','internalSourceReviewed','exactParagraphAndLogicalCharReconstruction'):
   draft,qa,np,cp,con=self.eligibility_fixture();con[field]=False
   with self.assertRaises(m.base.prep.Pending):m.source_eligibility_view(draft,qa,np,cp,con)
 def test_exact_seven_comma_splits(self):self.assertEqual({g['logicalSceneId']for g in self.new['logicalGroups']if len(g['physicalSceneIds'])==2},m.SPLIT_LOGICAL_IDS)
 def test_new_lineage_changes_base_and_old_output(self):self.assertNotEqual(self.new['fingerprint'],self.full['fingerprint']);self.assertNotEqual(self.new['fingerprint'],m.SOURCE_OLD_FINGERPRINT);self.assertNotEqual(self.new['voiceOutputDirectory'],self.full['voiceOutputDirectory'])
 def test_wrong_source_char_range_rejected(self):self.reject_contract(lambda p:p['paragraphs'][0]['components'][0].update(sourceCharRange=[1,2]))
 def test_wrong_logical_char_range_rejected(self):self.reject_contract(lambda p:p['paragraphs'][3]['components'][3].update(logicalSourceCharRange=[1,2]))
 def test_wrong_part_joiner_rejected(self):self.reject_contract(lambda p:p['paragraphs'][3]['components'][3].update(canonicalJoinerAfter=''))
 def test_wrong_physical_id_rejected(self):self.reject_contract(lambda p:p['paragraphs'][0]['components'][0].update(physicalSceneId='p001-c02'))
 def test_wrong_logical_id_rejected(self):self.reject_contract(lambda p:p['paragraphs'][0]['components'][0].update(logicalSceneId='p001-c02'))
 def test_missing_logical_group_rejected(self):self.reject_contract(lambda p:p['logicalGroups'].pop())
 def test_unapproved_part_count_rejected(self):self.reject_contract(lambda p:p['paragraphs'][0]['components'][0].update(logicalPartCount=2))
 def test_exact88reuse15missing(self):self.assertEqual((len(self.repair['rows']),len(self.repair['missing'])),(88,15))
 def test_renumbered_closing_reuse_is_explicit(self):self.assertTrue(any(r['oldSceneId']=='p025-c04'and r['newSceneId']=='p025-c05'for r in self.repair['rows']))
 def test_reused88_never_enter_engine(self):self.assertFalse({r['newSceneId']for r in self.repair['rows']}&{s['id']for s in self.repair['missing']})
 def test_profile_ref_model_guard_rawpolicy_unchanged(self):
  for k in('tts','modelPins','referenceSHA256','referenceTextSHA256','engine','guard','rawPcmPolicy'):self.assertEqual(self.new['identity'][k],self.old['identity'][k])
 def test_wrong_reuse_new_id_rejected(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['newSceneId']='p004-c01'
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_reused_pcm_metadata_rejected(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['sourceWav']['pcmSHA256']='0'*64
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_reference_rejected(self):
  prov=copy.deepcopy(self.new);prov['identity']['referenceSHA256']='0'*64
  with self.assertRaises(ValueError):m.validate_reuse(prov,self.plan)
 def test_changed_unselected_word_rejected(self):
  prov=copy.deepcopy(self.new);prov['logicalGroups'][0]['canonicalText']+=' wrong'
  with self.assertRaises(ValueError):m.validate_reuse(prov,self.plan)
 def test_mutable_oldproof_pointer_rejected(self):
  p=copy.deepcopy(self.plan);p['oldVoiceEvidence']=dump(self.root/'mutable.json',self.old)
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_missing15_plan_order_rejected(self):
  p=copy.deepcopy(self.plan);p['repairSceneIds'].reverse()
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_historical_mutable_decision_pointer_not_reopened(self):self.assertEqual(len(m.repair_spec(self.new,self.plan,self.planpath)['rows']),88)
 def test_frozen_old96_asr_scope_required(self):
  p=copy.deepcopy(self.plan);a=m.read(p['oldAsrReview']['path']);a['takes'].pop();p['oldAsrReview']=dump(self.root/'bad-asr.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_root_scope_counts_cannot_change(self):
  p=copy.deepcopy(self.plan);d=m.read(p['repairDecision']['path']);d['targetNewComponents']=16;p['repairDecision']=dump(self.root/'bad-decision.json',d)
  with patch.object(m,'DECISION_SHA256',p['repairDecision']['sha256']):
   with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_incomplete_old_paragraph_asr_scope_rejected(self):
  p=copy.deepcopy(self.plan);a=m.read(p['oldAsrReview']['path']);a['paragraphs'].pop();p['oldAsrReview']=dump(self.root/'bad-paragraph-asr.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_boolean_part_count_is_not_an_integer_contract(self):self.reject_contract(lambda p:p['paragraphs'][0]['components'][0].update(logicalPartCount=True))
 def test_pending_cannot_expand_to103_engine_scenes(self):
  req=copy.deepcopy(self.req);req['engineSceneIds']=[s['id']for s in self.scenes];original=(self.attempt/'request.json').read_bytes();rp=dump(self.attempt/'request.json',req)
  try:
   with self.assertRaises(RuntimeError):m.validate_launch_request(self.prov,self.out,dict(self.pending,requestPins=[rp]))
  finally:(self.attempt/'request.json').write_bytes(original)
 def test_unfrozen_plan_is_pending_before_privatepreparer(self):
  args=argparse.Namespace(topic='06.02',repair_plan=str(self.planpath))
  with patch.object(m,'PLAN_SHA256',None),patch.object(m,'selected_full',side_effect=AssertionError('no source stage/model')):
   with self.assertRaises(m.base.prep.Pending):m.prepared(args)
 def metadata_case(self,failures,kind='scene',winerror=5,lose_owner=False):
  media=self.root/'metadata-fixtures';media.mkdir(exist_ok=True);me=dict(pid=7654,createTime=1234.,argv=['python',str(Path(m.__file__))]);me['commandSHA256']=m.digest(me['argv']);marker=media/'06-02-voice-worker.json';owner='architectural-111-06-02-voice';rec=dict(protocol=m.base.PROTOCOL,owner=owner,token='fixture-owner-token',**me);dump(marker,rec)
  obj=dict(protocol=m.base.PROTOCOL,fingerprint=self.prov['fingerprint'],topicId='06.02',owner=owner,token=rec['token'],**me)
  path=self.out/'scene-progress.json'if kind=='scene'else media/'06-02-voice-progress.json'if kind=='state'else media/'06-02-voice-evidence.json'if kind=='evidence'else self.root/'shared/output/GPU_HANDOFF.json'if kind=='lease'else self.root/'foreign'/'metadata.json';calls=[];real_save=m.original_save
  def injected(path,obj):
   calls.append(str(path))
   if len(calls)<=failures:
    if lose_owner is True:dump(marker,dict(rec,token='changed-owner'))
    error=PermissionError('Injected Windows metadata sharing denial');error.winerror=winerror;raise error
   return real_save(path,obj)
  with patch.object(m.base,'MEDIA',media),patch.object(m.base,'identity',return_value=me),patch.object(m,'CURRENT',self.prov),patch.object(m,'original_save',side_effect=injected),patch.object(m.time,'sleep')as sleep:
   if lose_owner=='sleep':sleep.side_effect=lambda delay:dump(marker,dict(rec,token='changed-during-backoff'))
   try:m.metadata_save(path,obj);error=None
   except PermissionError as caught:error=caught
  return calls,sleep.call_args_list,error,path
 def test_single_metadata_sharing_decline_retries(self):
  calls,sleeps,error,path=self.metadata_case(1);self.assertIsNone(error);self.assertEqual(len(calls),2);self.assertEqual(len(sleeps),1);self.assertEqual(m.read(path)['fingerprint'],self.prov['fingerprint'])
 def test_multiple_transient_state_declines_retries(self):
  calls,sleeps,error,path=self.metadata_case(4,'state');self.assertIsNone(error);self.assertEqual(len(calls),5);self.assertEqual(len(sleeps),4)
 def test_owned_evidence_metadata_retry_does_not_touch_raw(self):
  source=Path(self.old['sceneWavs'][0]['path']);before=m.sha(source);calls,sleeps,error,path=self.metadata_case(1,'evidence');self.assertIsNone(error);self.assertEqual(m.sha(source),before)
 def test_persistent_metadata_declines_stop_at_ten(self):
  calls,sleeps,error,path=self.metadata_case(100);self.assertIsNotNone(error);self.assertEqual(len(calls),10);self.assertEqual(len(sleeps),9);self.assertLess(sum(x.args[0]for x in sleeps),2)
 def test_foreign_metadata_path_never_gains_retry(self):
  calls,sleeps,error,path=self.metadata_case(1,'foreign');self.assertIsNotNone(error);self.assertEqual(len(calls),1);self.assertEqual(len(sleeps),0)
 def test_non_winerror5_never_retried(self):
  calls,sleeps,error,path=self.metadata_case(1,winerror=32);self.assertIsNotNone(error);self.assertEqual(len(calls),1);self.assertEqual(len(sleeps),0)
 def test_gpu_lease_path_never_gains_metadata_retry(self):
  calls,sleeps,error,path=self.metadata_case(1,'lease');self.assertIsNotNone(error);self.assertEqual(len(calls),1);self.assertEqual(len(sleeps),0)
 def test_lost_singleton_ownership_stops_retry(self):
  calls,sleeps,error,path=self.metadata_case(2,lose_owner=True);self.assertIsNotNone(error);self.assertEqual(len(calls),1);self.assertEqual(len(sleeps),0)
 def test_ownership_is_rechecked_after_backoff_before_next_write(self):
  calls,sleeps,error,path=self.metadata_case(2,lose_owner='sleep');self.assertIsNotNone(error);self.assertEqual(len(calls),1);self.assertEqual(len(sleeps),1)
 def test_pending_exact_subset_pins(self):self.assertEqual(m.validate_launch_request(self.prov,self.out,self.pending),self.attempt)
 def test_pending_adapter_snapshot_tamper_rejected(self):
  f=self.folder/'repair-adapter-source.py';old=f.read_bytes();reqold=(self.attempt/'request.json').read_bytes();f.write_bytes(b'changed adapter');req=copy.deepcopy(self.req);req['subsetPins']=m.subset_pins(self.prov);rp=dump(self.attempt/'request.json',req)
  try:
   with self.assertRaises(RuntimeError):m.validate_launch_request(self.prov,self.out,dict(self.pending,requestPins=[rp]))
  finally:f.write_bytes(old);(self.attempt/'request.json').write_bytes(reqold)
 def test_full_canonical_requires_validated_subset_engine(self):
  with self.assertRaises(RuntimeError):m.canonical_outputs(self.prov,self.out,{})
 def test_canonical103_concat_preserves88_original_pcm(self):
  reuse={r['newSceneId']:r for r in self.repair['rows']};parts=[]
  for i,scene in enumerate(self.scenes):
   target=self.out/'chunks'/(scene['id']+'-scene.wav');target.parent.mkdir(parents=True,exist_ok=True)
   if scene['id']in reuse:target.write_bytes(Path(reuse[scene['id']]['sourceWav']['path']).read_bytes());self.assertEqual(m.sha(target),reuse[scene['id']]['sourceWav']['sha256'])
   else:wav(target,1000+i)
   with wave.open(str(target),'rb')as w:parts.append(w.readframes(w.getnframes()))
  proof=m.canonical_outputs(self.prov,self.out,dict(engineSceneScope='missing-subset-only',subsetAggregateAndTimingValidated=True,engineSceneIds=[s['id']for s in self.repair['missing']],subsetInputs=[]));self.assertEqual(proof['rawSceneCount'],103);self.assertEqual(len(proof['reusedRawScenes']),88);self.assertEqual(proof['aggregateWav']['pcmSHA256'],hashlib.sha256(b''.join(parts)).hexdigest());self.assertFalse(proof['engineSpokeFullCombinedScript'])
 def test_readonly_preparation_cannot_stage_or_launch(self):
  args=argparse.Namespace(topic='06.02',repair_plan=str(self.planpath),semantic_components='unused',native_evidence='unused',native_qa='unused')
  with patch.object(m,'PLAN',self.planpath),patch.object(m,'PLAN_SHA256',m.sha(self.planpath)),patch.object(m,'selected_full',return_value=self.full),patch.object(m.base.subprocess,'Popen',side_effect=AssertionError('no launch')),patch.object(m.base.prep,'immutable_stage',side_effect=AssertionError('no stage')):self.assertEqual(len(m.prepared(args)['repair']['missing']),15)

if __name__=='__main__':unittest.main(verbosity=2)
