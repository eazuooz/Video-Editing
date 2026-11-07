"""Synthetic CPU-only routing/provenance fixtures. No media/model processes."""
import contextlib,copy,hashlib,importlib.util,io,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
from types import SimpleNamespace
HERE=pathlib.Path(__file__).resolve().parent
def load(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
builder=load('build-prospect-refuge-film-timeline-v2');renderer=load('render-prospect-refuge-film-v2')

def fixture():
 selection=builder.read(builder.PROJECT/'native-teaching-selection-v3.json');decisions=builder.read(builder.PROJECT/'film-asbuilt-decisions-v2.json');rows=[];cursor=0;sample=0
 for p in selection['paragraphs']:
  for r in p['sentences']:
   lengths=[v['sourceFrameRange'][1]-v['sourceFrameRange'][0]for v in r['visuals']if v['sourceFrameRange']is not None];n=max(lengths or[300]);text=r['canonicalKo'];boundaries=[]
   if(p['paragraph'],r['sentenceIndexZeroBased'])==(5,2):boundaries=[dict(charOffset=text.index('적이 볼 수 있는 캐릭터의 몸은'),frame=cursor+100,sample=sample+40000,method='synthetic-fixture-exact-word')]
   if(p['paragraph'],r['sentenceIndexZeroBased'])==(25,3):boundaries=[dict(charOffset=text.index('달라지면')+len('달라지면'),frame=cursor+100,sample=sample+40000,method='synthetic-fixture-exact-word')]
   rows.append(dict(paragraph=p['paragraph'],sentenceIndexZeroBased=r['sentenceIndexZeroBased'],canonicalKo=text,startFrame=cursor,endFrameExclusive=cursor+n,startSample=sample,endSample=sample+n*400,canonicalWordBoundaries=boundaries));cursor+=n;sample+=n*400
 voice_plan=builder.read(builder.PROJECT/'voice-semantic-components-v3.json');physical=[]
 for r,g in zip(rows,voice_plan['logicalGroups']):
  parts=[c for p in voice_plan['paragraphs']for c in p['components']if c['logicalSceneId']==g['id']];position=r['startSample'];r['sceneId']=g['id'];r['physicalSceneIds']=g['physicalSceneIds']
  for index,c in enumerate(parts):
   end=r['endSample']if index+1==len(parts)else position+(r['endSample']-r['startSample'])//len(parts)
   physical.append(dict(sceneId=c['physicalSceneId'],paragraph=g['paragraph'],canonicalKo=c['text'],paragraphCharRange=c['sourceCharRange'],logicalSceneId=c['logicalSceneId'],logicalSentenceIndexZeroBased=c['logicalSentenceIndexZeroBased'],logicalPartIndex=c['logicalPartIndex'],logicalPartCount=c['logicalPartCount'],logicalSourceCharRange=c['logicalSourceCharRange'],canonicalJoinerAfter=c['canonicalJoinerAfter'],startSample=position,endSample=end,startFrame=round(position/400),endFrameExclusive=round(end/400),rawWav={'syntheticFixture':True}));position=end
 timing=dict(topicId='06.02',sentences=rows,totalFrames=cursor,captions=dict(ko=[],en=[]),paragraphs=[],physicalComponents=physical,audioClock=dict(rawSampleRate=24000,totalRawSamples=sample,mixedAudioTimingAccepted=False,finalMix=None));mc={}
 for p in(4,25):
  group=[r for r in rows if r['paragraph']==p];a,b=group[0]['startFrame'],group[-1]['endFrameExclusive'];mc[p]=dict(contract=dict(frames=b-a),actualCaptionBinding=dict(startFrame=a,endFrameExclusive=b),output=dict(path='synthetic-MC-not-a-media-file',sha256='a'*64),_pin=dict(path='synthetic-manifest-not-a-file',sha256='b'*64))
 return selection,timing,mc,decisions

class ClockRouting(unittest.TestCase):
 def setUp(self):self.s,self.t,self.mc,self.d=fixture()
 def plan(self):
  out=builder.plan(self.s,self.t,self.mc,self.d);out['sourceRegistry']=self.s['sourceRegistry'];return out
 def shift_first_physical(self,delta):
  parts=self.t['physicalComponents'];parts[0]['endSample']+=delta;parts[0]['endFrameExclusive']=round(parts[0]['endSample']/400)
  for p in parts[1:]:
   for k in('startSample','endSample'):p[k]+=delta
   p['startFrame']=round(p['startSample']/400);p['endFrameExclusive']=round(p['endSample']/400)
  self.t['audioClock']['totalRawSamples']+=delta
 def test_full96_exact_order_and_selected_three_games(self):
  p=self.plan();self.assertEqual(len(p['sentenceClocks']),96);self.assertEqual(renderer.validate_structure(p)['actualGameClips'],3)
 def test_clock_reordering_rejected(self):
  self.t['sentences'][0],self.t['sentences'][1]=self.t['sentences'][1],self.t['sentences'][0]
  with self.assertRaises(builder.Pending):self.plan()
 def test_clock_gap_rejected(self):
  self.t['sentences'][1]['startSample']+=1
  with self.assertRaises(builder.Pending):self.plan()
 def test_float_frame_rejected(self):
  self.t['sentences'][0]['startFrame']=0.
  with self.assertRaises(builder.Pending):self.plan()
 def test_actual_game_longer_speech_never_autofrozen(self):
  # Extend all later clocks coherently; the mismatch itself must stop routing.
  self.t['sentences'][0]['endFrameExclusive']+=1;self.t['sentences'][0]['endSample']+=400
  for r in self.t['sentences'][1:]:
   for key in('startFrame','endFrameExclusive'):r[key]+=1
   for key in('startSample','endSample'):r[key]+=400
  self.t['totalFrames']+=1
  self.shift_first_physical(400)
  with self.assertRaisesRegex(builder.Pending,'automaticfreeze'):self.plan()
 def test_actual_game_shorter_speech_never_speeded(self):
  self.t['sentences'][0]['endFrameExclusive']-=1;self.t['sentences'][0]['endSample']-=400
  for r in self.t['sentences'][1:]:
   for key in('startFrame','endFrameExclusive'):r[key]-=1
   for key in('startSample','endSample'):r[key]-=400
  self.t['totalFrames']-=1
  self.shift_first_physical(-400)
  with self.assertRaisesRegex(builder.Pending,'never speed'):self.plan()
 def test_camera_then_full_body_at_actual_word_boundary(self):
  sections=[s for s in self.plan()['sections']if(s['paragraph'],s.get('sentenceIndexZeroBased'))==(5,2)]
  self.assertEqual([len(s['panels'])for s in sections],[2,1]);self.assertEqual(sections[0]['endFrameExclusive'],sections[1]['startFrame']);self.assertEqual(sections[1]['panels'][0]['sourceRef'],'close')
 def test_camera_unknown_word_boundary_not_interpolated(self):
  next(r for r in self.t['sentences']if(r['paragraph'],r['sentenceIndexZeroBased'])==(5,2))['canonicalWordBoundaries']=[]
  with self.assertRaisesRegex(builder.Pending,'never interpolate'):self.plan()
 def test_closing_map_prefix_then_two_proven_heroes(self):
  p=self.plan();mc=next(s for s in p['sections']if s['kind']=='mc'and s['paragraph']==25);hero=[s for s in p['sections']if s.get('closingHero')]
  self.assertEqual(mc['endFrameExclusive'],hero[0]['startFrame']);self.assertEqual([s['panels'][0]['mode']for s in hero],['baseline','shifted','shifted']);self.assertEqual(hero[1]['endFrameExclusive']-hero[1]['startFrame'],12);self.assertEqual(hero[-1]['endFrameExclusive'],p['totalFrames'])
 def test_closing_unknown_word_end_never_guessed(self):
  self.t['sentences'][-1]['canonicalWordBoundaries']=[]
  with self.assertRaises(builder.Pending):self.plan()
 def test_no_cat_over_dense_map_or_AB(self):
  p=self.plan()
  for cue in p['catCues']:
   for s in p['sections']:
    if max(cue['startFrame'],s['startFrame'])<min(cue['endFrameExclusive'],s['endFrameExclusive']):self.assertNotEqual(s['kind'],'mc');self.assertEqual(len(s['panels']),1)
 def test_injected_cat_over_map_rejected(self):
  p=self.plan();m=next(x for x in p['sections']if x['kind']=='mc');p['catCues']=[dict(startFrame=m['startFrame'],endFrameExclusive=m['startFrame']+1,pose='relief')]
  with self.assertRaisesRegex(renderer.Pending,'cat OFF'):renderer.validate_structure(p)
 def test_mc_actualclock_mismatch_rejected(self):
  self.mc[4]['actualCaptionBinding']['endFrameExclusive']-=1
  with self.assertRaises(builder.Pending):self.plan()
 def test_mc_extra_source_provenance_is_retained(self):
  self.mc[4]['actualCaptionBinding']['source']='Verified current word/sample anchors';p=self.plan();s=next(s for s in p['sections']if s['kind']=='mc'and s['paragraph']==4);self.assertEqual(s['actualCaptionBinding']['source'],'Verified current word/sample anchors')
 def test_mc_missing_manifest_field_is_honestly_derived(self):
  row=self.mc[4];binding=row.pop('actualCaptionBinding');row['_currentProvenance']=dict(actualCaptionBinding=dict(binding,source='verified recipe'));p=self.plan();s=next(s for s in p['sections']if s['kind']=='mc'and s['paragraph']==4);self.assertFalse(s['rawManifestContainedCaptionBinding']);self.assertTrue(s['captionBindingDerivedFromCurrentRecipe'])
 def test_native_out_of_range_rejected(self):
  p=self.plan();s=next(s for s in p['sections']if s['kind']=='native'and s['panels'][0]['sourceRef']=='main');s['sourceStartFrame']=600
  with self.assertRaises(renderer.Pending):renderer.validate_structure(p)
 def test_actual_game_only_full_original_aspect(self):
  p=self.plan()
  for s in p['sections']:
   if s['kind']=='gameplay':self.assertIsNone(s['panels'][0]['cropXYXY']);self.assertEqual(s['rate'],1);self.assertEqual(s['frameCount'],s['endFrameExclusive']-s['startFrame'])
 def test_103raw_units_do_not_duplicate96logical_native_beats(self):
  p=self.plan();self.assertEqual(p['logicalSentenceGroupCount'],96);self.assertEqual(p['physicalVoiceUnitCount'],103);self.assertEqual(len(p['physicalVoiceComponents']),103);ramp=[s for s in p['sections']if(s['paragraph'],s.get('sentenceIndexZeroBased'))==(11,0)and s['rate']==1];self.assertEqual(len(ramp),1);self.assertEqual((ramp[0]['sourceStartFrame'],ramp[0]['frameCount']),(420,300))
 def test_physical_source_renumbering_cannot_change_literal(self):
  self.t['physicalComponents'][0]['canonicalKo']+='changed'
  with self.assertRaisesRegex(builder.Pending,'order/text/characters'):self.plan()
 def test_physical_clock_gap_rejected_separately_from96logical_clock(self):
  self.t['physicalComponents'][1]['startSample']+=1
  with self.assertRaisesRegex(builder.Pending,'103 sample clock'):self.plan()
 def test_logical_group_cannot_bind_wrong_physicalpart(self):
  self.t['sentences'][0]['physicalSceneIds']=['p001-c02']
  with self.assertRaisesRegex(builder.Pending,'one/two physical'):self.plan()
 def test_geometry_bridge_cannot_hide_new_source_geometry(self):
  a=builder.read(builder.PROJECT/'source-annotation-plan-v2.json');changed=copy.deepcopy(self.s);changed['sourceRegistry']['main']['contract']['frames']=601
  with self.assertRaisesRegex(builder.Pending,'changed native sources'):builder.annotation_geometry_base(a,changed)

class SeparateMixClockBridge(unittest.TestCase):
 def setUp(self):
  self.voice=dict(fingerprint='fixture-voice',aggregateWav=dict(frames=1234),timing={'fixtureTiming':True});self.mix=dict(mixWav={'fixtureMix':True},pcmLineage={'fixturePcmLineage':True});self.timing=dict(audioClock=dict(totalRawSamples=1234,mixedAudioTimingAccepted=False));self.pin=dict(path='fixture-clock',sha256='a'*64)
  lineage=dict(componentCount=103,logicalGroupCount=96,rawSampleRate=24000,rawFrames=1234,mixSampleRate=48000,mixFrames=2468,rawToMixSampleRatio=[2,1],voiceOffsetSamples=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1,wholeAggregateResampleOnce=True,perComponentConstantScalarOnly=True,uniformMixGainDb=0,pcmLineage=self.mix['pcmLineage'])
  self.proof=dict(schemaVersion='06-02-raw-mix-clock-proof-v2',topicId='06.02',status='verified-raw-to-mix-sample-clock',rawVoiceFingerprint=self.voice['fingerprint'],rawVoice=self.voice['aggregateWav'],canonicalTiming=self.voice['timing'],mixWav=self.mix['mixWav'],rawMixClockAccepted=True,rawCaptionClockModified=False,mixedAsrAccepted=False,actualListening=False,actualRealtimePlayback=False,automaticSpeechPass=False,humanApproval=False,lineage=lineage)
 def accept(self):return builder.clock_acceptance(self.proof,self.timing,self.voice,self.mix,self.pin)
 def test_separate_sample_acceptance_does_not_change_rawcaption_or_accept_mixedASR(self):
  original=copy.deepcopy(self.timing);r=self.accept();self.assertTrue(r['rawMixClockAccepted']);self.assertFalse(r['mixedAsrAccepted']);self.assertEqual(self.timing,original)
 def test_old_voice_or_mix_proof_rejected(self):
  self.proof['rawVoiceFingerprint']='old-voice'
  with self.assertRaisesRegex(builder.Pending,'another voice or mix'):self.accept()
 def test_sample_proof_cannot_imply_human_or_mixedspeech_approval(self):
  self.proof['mixedAsrAccepted']=True
  with self.assertRaisesRegex(builder.Pending,'infer speech'):self.accept()
 def test_wrong_2x_or_padded_clock_rejected(self):
  self.proof['lineage']['mixFrames']+=1
  with self.assertRaisesRegex(builder.Pending,'103/2x'):self.accept()

class ProjectionAndVisibility(unittest.TestCase):
 def badge_font(self):return renderer.primitives().style_adapter().font(32)
 def test_section_badge_is_inside_actual_observer_crop_and_clear_of_headers(self):
  font=self.badge_font();p=dict(camera='observer')
  for crop,dest in [([430,230,1510,1080],[48,992,880,495]),([430,230,1510,1080],[0,500,1080,850]),([0,0,1920,1080],[48,410,880,495])]:
   tr=renderer.fit(crop,dest);b=renderer.section_badge_layout(p,tr,font);x,y,w,h=b['rectXYWH'];self.assertTrue(tr['x']<=x<x+w<=tr['x']+tr['width']);self.assertTrue(tr['y']<=y<y+h<=tr['y']+tr['height']);header=[200,dest[1]-52,780,dest[1]-16]
   self.assertFalse(renderer.overlap(b['rectXYWH'],header));self.assertFalse(renderer.overlap(b['rectXYWH'],[48,285,936,392]));self.assertFalse(renderer.overlap(b['rectXYWH'],[48,1520,936,1690]))
 def test_old_global_section_tag_reproduces_header_overlap_negative(self):
  self.assertTrue(renderer.overlap([382,347,212,36],[260,360,716,392]));tr=renderer.fit([430,230,1510,1080],[48,992,880,495]);b=renderer.section_badge_layout(dict(camera='observer'),tr,self.badge_font());self.assertFalse(renderer.overlap(b['rectXYWH'],[260,360,716,392]))
 def test_section_badge_avoids_actual_frame300_roof_anchor_bounds(self):
  selection=builder.read(builder.PROJECT/'native-teaching-selection-v3.json');folder=pathlib.Path(selection['sourceRegistry']['c-refuge']['modeFolder']);row=json.loads((folder/'projected-anchors.jsonl').read_text(encoding='utf8').splitlines()[300]);self.assertEqual(row['frame'],300)
  anchors=[a for a in row['anchors']if a['id'].startswith('interior-ceiling')];self.assertGreaterEqual(len(anchors),5)
  for dest in [[48,992,880,495],[0,500,1080,850]]:
   tr=renderer.fit([430,230,1510,1080],dest);b=renderer.section_badge_layout(dict(camera='observer'),tr,self.badge_font());points=[renderer.point(a['observerViewport'],tr)for a in anchors];box=[min(p[0]for p in points),min(p[1]for p in points),max(p[0]for p in points),max(p[1]for p in points)];self.assertFalse(renderer.overlap(b['rectXYWH'],box))
 def test_section_tag_never_floats_over_player_and_rejects_tiny_slot(self):
  font=self.badge_font();self.assertIsNone(renderer.section_badge_layout(dict(camera='player'),renderer.fit([0,0,1920,1080],[48,410,880,495]),font))
  with self.assertRaisesRegex(renderer.Pending,'readable section-badge slot'):renderer.section_badge_layout(dict(camera='observer'),dict(x=0,y=0,width=100,height=50),font)
 def test_refuge_crop_uses_identical_affine_transform(self):
  t=renderer.fit([430,230,1510,1080],[0,500,1080,850]);self.assertEqual(t['scale'],1)
  for a,b in zip(renderer.point(dict(x=430/1920,y=1-230/1080),t),(0,500)):self.assertAlmostEqual(a,b)
  for a,b in zip(renderer.point(dict(x=1510/1920,y=0),t),(1080,1350)):self.assertAlmostEqual(a,b)
 def test_no_upscale_or_stretch(self):
  t=renderer.fit([0,0,1920,1080],[48,410,880,495]);self.assertAlmostEqual(t['scale'],880/1920);self.assertAlmostEqual(t['width']/t['height'],16/9)
 def test_invalid_crop_rejected(self):
  with self.assertRaises(renderer.Pending):renderer.fit([430,230,1930,1080],[0,500,1080,850])
 def test_behind_near_and_offscreen_are_hidden(self):
  self.assertFalse(renderer.visible_depth(dict(x=.5,y=.5,z=.01)));self.assertFalse(renderer.visible_depth(dict(x=1.01,y=.5,z=3)))
 def test_frustum_alone_cannot_claim_visibility(self):
  a=dict(id='item',playerViewport=dict(x=.5,y=.5,z=2),playerInFrustum=True);self.assertFalse(renderer.guide_visible(a,dict(camera='player',sourceRef='alcove',mode='alcove'),479,{}))
 def test_target_selfhit_distinct_from_wall(self):
  p=dict(camera='player',sourceRef='alcove',mode='alcove');a=dict(id='item',playerViewport=dict(x=.5,y=.5,z=2),playerInFrustum=True,playerCameraRay=dict(blocked=True,hitCollider='Chestlid',actualEndpoint=dict(x=1,y=1,z=1),desiredEndpoint=dict(x=1,y=1,z=1)));rule=dict(sourceRef='alcove',camera='player',anchorId='item',method='recorded-camera-ray',targetSurfaceColliders=['Chestlid'],targetSurfaceTolerance=.001);self.assertTrue(renderer.guide_visible(a,p,479,dict(nativeGuidePolicies=[rule])));a['playerCameraRay']['hitCollider']='Projectingwall';self.assertFalse(renderer.guide_visible(a,p,478,dict(nativeGuidePolicies=[rule])))
 def test_inspected_frame_policy_does_not_extend_to_unviewed(self):
  a=dict(id='ceiling',observerViewport=dict(x=.5,y=.5,z=2),observerInFrustum=True);p=dict(camera='observer',sourceRef='c-refuge',mode='refuge');rule=dict(sourceRef='c-refuge',camera='observer',anchorId='ceiling',method='reviewed-frame-set',visibleFrames=[300]);self.assertTrue(renderer.guide_visible(a,p,300,dict(nativeGuidePolicies=[rule])));self.assertFalse(renderer.guide_visible(a,p,301,dict(nativeGuidePolicies=[rule])))
 def test_section_cutaway_exception_cannot_prove_object_visibility(self):
  a=dict(id='floor',observerViewport=dict(x=.5,y=.5,z=2),observerInFrustum=True);p=dict(camera='observer',sourceRef='c-refuge',mode='refuge');rule=dict(sourceRef='c-refuge',camera='observer',anchorId='floor',method='reviewed-frame-set',visibleFrames=[300],allowedGuideKinds=['height-leader','section-label']);plan=dict(nativeGuidePolicies=[rule]);self.assertTrue(renderer.guide_visible(a,p,300,plan,'height-leader'));self.assertFalse(renderer.guide_visible(a,p,300,plan,'anchor-label'));self.assertFalse(renderer.guide_visible(a,p,300,plan,'native-ray'))
 def test_section_policy_not_swallowed_by_physical_blocked_ray_policy(self):
  a=dict(id='floor',observerViewport=dict(x=.5,y=.5,z=2),observerInFrustum=True,observerCameraRay=dict(blocked=True,hitCollider='Physicalceiling',actualEndpoint=dict(x=0,y=2,z=0),desiredEndpoint=dict(x=0,y=0,z=0)));p=dict(camera='observer',sourceRef='c-refuge',mode='refuge');common=dict(sourceRef='c-refuge',camera='observer',anchorId='floor');policies=[dict(common,method='recorded-camera-ray'),dict(common,method='reviewed-frame-set',visibleFrames=[300],allowedGuideKinds=['height-leader'],requiresMeaningfulHeldSourceFrame=True)];self.assertTrue(renderer.guide_visible(a,p,300,dict(nativeGuidePolicies=policies),'height-leader',True));self.assertFalse(renderer.guide_visible(a,p,300,dict(nativeGuidePolicies=policies),'anchor-label',True));self.assertFalse(renderer.guide_visible(a,p,300,dict(nativeGuidePolicies=policies),'height-leader',False))

class FileProofs(unittest.TestCase):
 def make(self,root,frames=None):
  p=root/'player/0000.jpg';p.parent.mkdir();p.write_bytes(b'synthetic-fixture-not-an-image');r=dict(path='player/0000.jpg',sha256=builder.sha(p),bytes=p.stat().st_size);mp=root/'frame-hashes.json';mp.write_text(json.dumps(dict(captureFingerprint='fp',frames=frames if frames is not None else[r])),encoding='utf8');return p,dict(captureFingerprint='fp',frameHashManifest=builder.pin(mp))
 def test_native_bytes_bound_before_image_decode(self):
  with tempfile.TemporaryDirectory()as d:
   p,s=self.make(pathlib.Path(d));self.assertEqual(renderer.NativeFrameProofs().verify(s,p)['sha256'],builder.sha(p))
 def test_modified_native_bytes_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   p,s=self.make(pathlib.Path(d));p.write_bytes(b'changed')
   with self.assertRaises(renderer.Pending):renderer.NativeFrameProofs().verify(s,p)
 def test_wrong_capture_fingerprint_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   p,s=self.make(pathlib.Path(d));s['captureFingerprint']='other'
   with self.assertRaises(renderer.Pending):renderer.NativeFrameProofs().verify(s,p)
 def test_duplicate_and_escape_native_paths_rejected(self):
  for rows in[[dict(path='../outside.jpg',sha256='a'*64,bytes=1)],[dict(path='player/0000.jpg',sha256='a'*64,bytes=1)]*2]:
   with tempfile.TemporaryDirectory()as d:
    p,s=self.make(pathlib.Path(d),rows)
    with self.assertRaises(renderer.Pending):renderer.NativeFrameProofs().verify(s,p)

class ContextOverrides(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=pathlib.Path(self.tmp.name);proof=root/'synthetic-proof.json';proof.write_text('{"syntheticFixture":true}',encoding='utf8');self.proof=builder.pin(proof)
  self.selection=dict(sourceRegistry=dict(main=dict(sourceKind='our-authored-implementation',output=str(root),contract=dict(frames=600),frameHashManifest=self.proof)))
  self.timing=dict(totalFrames=900,sentences=[dict(paragraph=5,sentenceIndexZeroBased=0,canonicalKo='같은 입력입니다.',startFrame=0,endFrameExclusive=390),dict(paragraph=5,sentenceIndexZeroBased=1,canonicalKo='엄폐 위치만 바꿉니다.',startFrame=390,endFrameExclusive=595),dict(paragraph=5,sentenceIndexZeroBased=2,canonicalKo='카메라와 적이 볼 수 있는 몸을 구별합니다.',startFrame=595,endFrameExclusive=900,canonicalWordBoundaries=[dict(charOffset=5,frame=730,sample=292000)])])
  self.row=dict(id='main-run',start=dict(paragraph=5,sentenceIndexZeroBased=0,boundary='sentence-start'),end=dict(boundary='source-duration'),playback='native-1x',sourceFrameRange=[0,600],allowedSpokenContext=[[5,0],[5,1],[5,2]],visuals=[dict(sourceRef='main',camera='AB-dual')],viewCuts=[dict(at=dict(paragraph=5,sentenceIndexZeroBased=1,boundary='sentence-start'),visuals=[dict(sourceRef='main',camera='AB-observer')])],actualSourceInspection=self.proof,sourceProofs=[self.proof],reason='Synthetic fixture: exact600source frames carry briefly into next related sentence; no media job')
 def compile(self,rows=None,status='adopted-actual-clock'):return builder.compile_picture_overrides(dict(schemaVersion='06-02-picture-overrides-v1',topicId='06.02',status=status,overrides=rows or[self.row]),self.selection,self.timing)
 def test_provisional_context_carry_is_not_adopted(self):
  with self.assertRaisesRegex(builder.Pending,'Provisional'):self.compile(status='provisional-not-adopted')
 def test_native_clock_carries_across_actual_sentences_and_camera_cut(self):
  rows=self.compile();self.assertEqual([(r['startFrame'],r['endFrameExclusive'],r['sourceStartFrame'])for r in rows],[(0,390,0),(390,600,390)]);self.assertEqual([len(r['panels'])for r in rows],[4,2])
 def test_context_must_name_partial_next_sentence(self):
  self.row['allowedSpokenContext']=[[5,0],[5,1]]
  with self.assertRaisesRegex(builder.Pending,'exactly the actual sentences'):self.compile()
 def test_mismatched_actual_boundary_cannot_speedup(self):
  self.row['end']=dict(paragraph=5,sentenceIndexZeroBased=1,boundary='sentence-end')
  with self.assertRaisesRegex(builder.Pending,'no padding'):self.compile()
 def test_stale_source_proof_is_not_reused(self):
  self.row['sourceProofs']=[]
  with self.assertRaisesRegex(builder.Pending,'exactly the selected source'):self.compile()
 def test_after_native_run_purposeful_still_uses_real_word_boundary(self):
  hold=dict(id='camera-detail',start=dict(afterOverrideId='main-run'),end=dict(paragraph=5,sentenceIndexZeroBased=2,boundary='phrase-start',exactKoPhrase='적이 볼 수 있는 몸을'),playback='purposeful-still',allowedSpokenContext=[[5,2]],visuals=[dict(sourceRef='main',camera='baseline-dual',sourceFrame=599)],actualSourceInspection=self.proof,sourceProofs=[self.proof],reason='Synthetic held actualsource result while camera eye is explained')
  rows=self.compile([self.row,hold]);self.assertEqual((rows[-1]['startFrame'],rows[-1]['endFrameExclusive']),(600,730));self.assertEqual(rows[-1]['panels'][0]['sourceFrame'],599)
 def test_unknown_word_boundary_is_not_char_interpolated(self):
  self.row['start']=dict(paragraph=5,sentenceIndexZeroBased=2,boundary='phrase-start',exactKoPhrase='카메라')
  with self.assertRaisesRegex(builder.Pending,'never interpolate'):self.compile()
 def test_native_trim_must_stay_in_captured_range(self):
  self.row['sourceFrameRange']=[0,601]
  with self.assertRaisesRegex(builder.Pending,'captured frame range'):self.compile()
 def test_whole_native_motion_can_end_on_actual_sentence_end(self):
  self.row.update(start=dict(boundary='source-duration-before-end'),end=dict(paragraph=5,sentenceIndexZeroBased=1,boundary='sentence-end'),sourceFrameRange=[90,360],allowedSpokenContext=[[5,0],[5,1]],viewCuts=[])
  rows=self.compile();self.assertEqual((rows[0]['startFrame'],rows[0]['endFrameExclusive'],rows[0]['sourceStartFrame']),(325,595,90));self.assertEqual(rows[0]['frameCount'],270)
 def test_two_unanchored_duration_endpoints_rejected(self):
  self.row['start']=dict(boundary='source-duration-before-end')
  with self.assertRaisesRegex(builder.Pending,'real sentence/word boundary'):self.compile()
 def test_overlay_removes_only_covered_conflicts_and_preserves_other_pixels_clock(self):
  base=[dict(id='a',startFrame=0,endFrameExclusive=595,rate=1,sourceStartFrame=0,frameCount=600,pendingTimingConflict='too long'),dict(id='b',startFrame=595,endFrameExclusive=900,rate=None,sourceStartFrame=None,frameCount=1,panels=[dict(sourceFrame=0)])];rows=builder.apply_picture_overrides(base,self.compile());self.assertEqual(rows[-1]['startFrame'],600);self.assertEqual(rows[-1]['endFrameExclusive'],900);self.assertEqual(rows[-1]['panels'][0]['sourceFrame'],0)
 def test_uncovered_timing_conflict_still_blocks(self):
  base=[dict(startFrame=0,endFrameExclusive=900,rate=1,sourceStartFrame=0,frameCount=1200,pendingTimingConflict='unresolved')]
  with self.assertRaisesRegex(builder.Pending,'Unresolved'):builder.apply_picture_overrides(base,self.compile())
 def test_additional_samefile_H_window_is_available_not_implicitly_adopted(self):
  p=builder.PROJECT/'additional-source-window-review-v1.json';selection=builder.read(builder.PROJECT/'native-teaching-selection-v3.json');windows=builder.additional_source_windows(dict(additionalSourceSelections=[builder.pin(p)]),selection);self.assertEqual(windows['H'][0]['frameRange'],[1320,1652]);self.assertEqual(windows['H'][0]['record']['sha256'],'83404d267123d19b6e1d373c427cf0238aadced3345083503bf08de57187deb7')
 def test_additional_window_wrong_source_sha_rejected(self):
  d=builder.read(builder.PROJECT/'additional-source-window-review-v1.json');d['sourceFile']['sha256']='0'*64;p=pathlib.Path(self.tmp.name)/'badwindow.json';p.write_text(json.dumps(d),encoding='utf8')
  with self.assertRaisesRegex(builder.Pending,'same selected source'):builder.additional_source_windows(dict(additionalSourceSelections=[builder.pin(p)]),builder.read(builder.PROJECT/'native-teaching-selection-v3.json'))
 def test_additional_window_pts_sample_mismatch_rejected(self):
  d=builder.read(builder.PROJECT/'additional-source-window-review-v1.json');d['sourceFramePtsProofs'][0]['pts']+=1;p=pathlib.Path(self.tmp.name)/'badpts.json';p.write_text(json.dumps(d),encoding='utf8')
  with self.assertRaisesRegex(builder.Pending,'decoded60fps'):builder.additional_source_windows(dict(additionalSourceSelections=[builder.pin(p)]),builder.read(builder.PROJECT/'native-teaching-selection-v3.json'))

class GuideAndDefaults(unittest.TestCase):
 def test_actual_V3_SRT_API_bridge_preserves_both_existing_literal_files(self):
  cp=HERE/'build-prospect-refuge-caption-timing-v3.py';self.assertEqual(builder.sha(cp),renderer.CAPTION_SHA);cap=builder.module('actual_caption_v3_srt_regression',cp)
  # The precise failure was an assumed cap.base field. V3 delegates to V2,
  # whose old.base is also V3's own existing immutable SRT output primitive.
  self.assertFalse(hasattr(cap,'base'));self.assertIs(cap.old.base.srt,cap.previous.old.base.srt)
  folder=builder.MEDIA/'caption-timing-v3/340e246acfb0badde148ed76';timing=builder.read(folder/'caption-timing.json')
  for lang,count in [('ko',190),('en',234)]:
   cues=timing['captions'][lang];self.assertEqual(len(cues),count);expected=(folder/f'captions.{lang}.srt').read_text(encoding='utf8');self.assertEqual(renderer.caption_srt(cap,cues,lang),expected)
 def test_actual_native_annotation_literals_and_visibility_load_with_synthetic_clock_only(self):
  class Caption:
   def resolve_literal_start(self,r,phrase):
    if r['canonicalKo'].count(phrase)!=1:raise RuntimeError('unknown exact phrase')
    return dict(frame=r['startFrame']+1,sample=r['startSample']+400,method='synthetic-fixture-only')
   def resolve_literal_interval(self,r,phrase):
    if r['canonicalKo'].count(phrase)!=1:raise RuntimeError('unknown exact phrase')
    return dict(endFrameExclusive=r['endFrameExclusive']-1)
  selection,timing,mc,decisions=fixture();annotations=builder.read(builder.PROJECT/'source-annotation-plan-v2.json');cues=builder.verify_annotations(annotations,selection,timing,Caption());self.assertEqual(len(cues),42);self.assertEqual(len(annotations['nativeGuidePolicies']),72);self.assertEqual(len(annotations['pendingNativeGuidePolicies']),63);self.assertEqual(len({c['id']for c in cues}),42);self.assertTrue(all(c['actualTimestampStatus'].startswith('pending')for c in cues))
 def test_source_pts_cannot_hold_duplicate_vfr_frames(self):
  renderer.verify_native60_source_pts([n/60 for n in range(20)],3,10)
  bad=[n/60 for n in range(20)];bad[7]=bad[6]
  with self.assertRaisesRegex(renderer.Pending,'never duplicate'):renderer.verify_native60_source_pts(bad,3,10)
 def mc_recipe_fixture(self,change=None):
  path=builder.MEDIA/'mc-render-attempts-v3/synthetic/render-manifest.json';caption=builder.MEDIA/'caption-timing/synthetic/caption-timing.json';cue=builder.MEDIA/'diagram-cue-plans-v3/synthetic/p04.json';h=builder.MC_RUNNER_SHA;out=path.parent/'p04.silent.mp4';pins=[dict(path=str(cue.resolve()),sha256=h),dict(path=str(caption.resolve()),sha256=h)];contract=dict(width=1080,height=900,fps=60,frames=400,audio=False,alpha=False);prov=dict(ready=True,fingerprint='current-fp',segment='p04',contract=contract,inputPins=pins,actualCaptionBinding=dict(startFrame=800,endFrameExclusive=1200,source='actual word clock'));manifest=dict(schemaVersion='06-02-mc-crop-render-v3',topicId='06.02',segment='p04',complete=True,fingerprint='current-fp',contract=contract,inputPins=pins,output=dict(path=str(out),sha256=h),encoded=dict(width=1080,height=900,fps='60/1',frames=400,audioStreams=0,fullDecodePassed=True,ptsStrictlyIncreasing=True))
  if change:change(manifest)
  runner=SimpleNamespace(prepare=lambda q:copy.deepcopy(prov))
  def digest(path):return {'build-prospect-refuge-diagram-cues-v3.py':builder.MC_CUE_SHA,'render-prospect-refuge-diagrams-v3.cjs':builder.MC_NODE_SHA}.get(pathlib.Path(path).name,h)
  with patch.object(builder,'sha',side_effect=digest),patch.object(builder,'read',return_value=manifest),patch.object(builder,'bound',side_effect=lambda r:pathlib.Path(r['path']).resolve()),patch.object(builder,'module',return_value=runner):return builder.verify_mc_manifest(path,caption)
 def test_mc_recipe_fresh_recomputed_not_only_existing_pins(self):
  row=self.mc_recipe_fixture();self.assertEqual(row['_currentProvenance']['fingerprint'],'current-fp');self.assertNotIn('actualCaptionBinding',row)
 def test_mc_old_cue_fingerprint_rejected(self):
  with self.assertRaisesRegex(builder.Pending,'freshly verified'):self.mc_recipe_fixture(lambda r:r.update(fingerprint='old-fp'))
 def test_mc_false_decode_claim_rejected(self):
  def change(r):r['encoded']['fullDecodePassed']=False
  with self.assertRaisesRegex(builder.Pending,'decode/PTS'):self.mc_recipe_fixture(change)
 def test_current_topic_boundary_rejects_stale_selected06_cli(self):
  original=renderer.read
  def read(path):
   if pathlib.Path(path)==renderer.HERE/'checkpoint.json':return dict(currentTopicId='01.01')
   return original(path)
  with patch.object(renderer,'read',side_effect=read):
   with self.assertRaisesRegex(renderer.Pending,'current06.02'):renderer.fresh_authorization()
 def manual(self):
  return[dict(sourceRef='D',reviewedTemporalCoverage=dict(sourceFrameRange=[100,121],visibilityOffRanges=[]),marks=[dict(id='window',type='rectangle',label='관찰',keyframes=[dict(frame=100,visible=True,bboxXYXY=[100,100,200,200]),dict(frame=120,visible=True,bboxXYXY=[200,100,300,200])])])]
 def test_manual_region_interpolates_only_between_inspected_keys(self):
  r=renderer.manual_regions(self.manual(),'D',110)[0];self.assertEqual(r['bboxXYXY'],[150,100,250,200]);self.assertFalse(r['exactInspectedKeyframe']);self.assertFalse(r['continuousTrackerVerified'])
 def test_manual_region_no_extrapolation(self):
  self.assertEqual(renderer.manual_regions(self.manual(),'D',99),[]);self.assertEqual(renderer.manual_regions(self.manual(),'D',121),[])
 def test_manual_region_uncertain_range_off(self):
  r=self.manual();r[0]['reviewedTemporalCoverage']['visibilityOffRanges']=[[105,115]];self.assertEqual(renderer.manual_regions(r,'D',110),[])
 def test_manual_region_hidden_endpoint_clears_interpolation(self):
  r=self.manual();r[0]['marks'][0]['keyframes'][1]['visible']=False;self.assertEqual(renderer.manual_regions(r,'D',110),[]);self.assertEqual(renderer.manual_regions(r,'D',120),[])
 def test_manual_region_exact_key_not_claimed_interpolated(self):
  r=renderer.manual_regions(self.manual(),'D',100)[0];self.assertTrue(r['exactInspectedKeyframe']);self.assertEqual(r['bboxXYXY'],[100,100,200,200])
 def test_manual_label_uses_reviewed_safe_anchor(self):
  style=renderer.manual_label_style(dict(labelDisplayAnchor=[240,980],labelFontPx=40,color='#50d6b0',strokeWidthOutputPixels=8));self.assertEqual(style,dict(anchor=(240,980),fontSize=40,color='#50d6b0',stroke=8))
 def actual_guide(self,mutate=None):
  data=builder.read(builder.PROJECT/'source-game-guides-v1.json')
  if mutate:mutate(data)
  with tempfile.TemporaryDirectory()as d:
   p=pathlib.Path(d)/'guide.json';p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8');return builder.manual_game_guides(dict(gameGuidesFile=builder.pin(p)),builder.read(builder.PROJECT/'native-teaching-selection-v3.json'))
 def test_actual_four_source_guides_and58_rgb_proofs_load(self):
  rows=self.actual_guide();self.assertEqual(len(rows),4);unique={(r['sourceRef'],q['frame'],q['rgbSHA256'])for r in rows for q in r['reviewedTemporalCoverage']['inspectedKeyframes']};self.assertEqual(len(unique),58)
 def test_actual_guide_stale_per_row_review_rejected(self):
  def change(d):d['guides'][0]['actualSourceReview']['sha256']='0'*64
  with self.assertRaisesRegex(builder.Pending,'source review identity'):self.actual_guide(change)
 def test_actual_guide_wrong_fhd_metadata_rejected(self):
  def change(d):d['guides'][0]['sourceDimensions']=[1280,720]
  with self.assertRaisesRegex(builder.Pending,'FHD60'):self.actual_guide(change)
 def test_actual_guide_false_tracker_claim_rejected(self):
  def change(d):d['continuousTrackerVerified']=True
  with self.assertRaisesRegex(builder.Pending,'honest review'):self.actual_guide(change)
 def test_actual_guide_unsafe_label_location_rejected(self):
  def change(d):d['guides'][0]['marks'][0]['labelDisplayAnchor']=[240,1700]
  with self.assertRaisesRegex(builder.Pending,'safe area'):self.actual_guide(change)
 def test_guide_uses_actual_word_boundary_api(self):
  class Caption:
   def resolve_literal_start(self,s,phrase):self.phrase=phrase;return dict(frame=17,sample=6800,method='actual-word-boundary')
  c=Caption();t=dict(sentences=[dict(paragraph=1,sentenceIndexZeroBased=0,startFrame=10,endFrameExclusive=40)]);a=dict(cueTriggers=[dict(paragraph=1,sentenceIndexZeroBased=0,revealPhraseKo='실내 천장',clearAt='sentence-end',kind='height-leader',sourceRef='c-refuge',anchorIds=['ceiling','floor'])]);r=builder.compile_guide_cues(a,t,c);self.assertEqual((r[0]['startFrame'],r[0]['endFrameExclusive']),(17,40));self.assertEqual(c.phrase,'실내 천장')
 def test_unsupported_actual_word_boundary_stays_pending(self):
  class Caption:
   def resolve_literal_start(self,s,p):raise RuntimeError('ASR merged this word')
  with self.assertRaises(builder.Pending):builder.compile_guide_cues(dict(cueTriggers=[dict(paragraph=1,sentenceIndexZeroBased=0,revealPhraseKo='x')]),dict(sentences=[dict(paragraph=1,sentenceIndexZeroBased=0)]),Caption())
 def test_default_builder_and_renderer_do_not_launch(self):
  for m in(builder,renderer):
   with patch.object(sys,'argv',[str(m.__file__)]),patch('subprocess.Popen')as popen,contextlib.redirect_stdout(io.StringIO())as out:m.main();popen.assert_not_called();self.assertFalse(json.loads(out.getvalue())['ready'])
 def test_sample_requires_explicit_execute(self):
  with patch.object(sys,'argv',['renderer','--timeline','nonexistent','--sample-frame','10']),patch('subprocess.Popen')as popen:
   with self.assertRaisesRegex(renderer.Pending,'require explicit'):renderer.main()
   popen.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
