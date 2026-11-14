"""Current actual clocks plus synthetic rejection cases; no media/model jobs."""
from __future__ import annotations
import copy, importlib.util, sys, tempfile, unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
def load(name):
    spec=importlib.util.spec_from_file_location('film3_test_'+name.replace('-','_'),HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module
b=load('build-solution-path-film-timeline-v3')
c=load('build-solution-path-caption-timing-v7')
q=load('verify-solution-path-mixed-film-input-v1')
a=load('run-solution-path-structure-atlas-v2')
r=load('render-solution-path-film-v3')
TIMING=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05/caption-timing-v7/94ecaaa91980f03f7e33ab00/caption-timing.json')
timing=b.read(TIMING);narration=b.read(b.PROJECT/'narration-final-v7.json')
source=b.read(b.PROJECT/'source-footage-v2.json')['sources'][0]
def plan():return b.plan(timing,narration,source['selectedCuts'],c.resolve_literal_interval)
def mixed_fixture():
    trend=dict(words=18,spanSeconds=7,suspect=False)
    levels=dict(actualMixedRecognitionComplete=True,fullActualMixCoverage=True,retainedLiteralDifferences=[],flags=[],
        wholeExplanations=[dict(paragraph=p,trends={stage:dict(trend) for stage in ('raw','normalized','prepared','voice','mix')})for p in (8,13)])
    content=dict(schemaVersion=3,topicId='11.05',finalMixAccepted=True,disposition='qualified-for-film-production-not-listening',
        actualListening=False,humanApproval=False,exactCounts=dict(physical=51,wholeParagraphs=14,joins=13,coveredMixSamples=10579202),
        retainedLiteralDifferences=[],literalDifferencesExplicitlyReviewed=True,aliasesApplied=False,retainedFlags=[])
    return content,levels

class CurrentFilm(unittest.TestCase):
    def test_new_source_pins_and_preserved_old_builder(self):
        for name,value in b.SOURCE_PINS.items():self.assertEqual(b.sha(b.PROJECT/name),value)
        for name,value in b.PINS.items():self.assertEqual(b.sha(HERE/name),value)
        for name,value in b.MC_PINS.items():self.assertEqual(b.sha(b.MC_SOURCE/name),value)
        self.assertEqual(b.sha(HERE/'build-solution-path-film-timeline-v2.py'),'013eacc0b8e5ebf36cfd410775d33a3a6b74213bb33ea045597922391f6d9c1e')
        self.assertEqual(r.BUILDER_SHA,b.sha(HERE/'build-solution-path-film-timeline-v3.py'))
        a.checked_sources()

    def test_actual_sample_clock_all51_takes_no_dropped_tail(self):
        t=plan();report=b.validate_plan(t)
        self.assertEqual(report['totalFrames'],13225)
        self.assertEqual(t['audioClock']['totalRawSamples'],5289601)
        self.assertEqual(len(t['sentences']),51)
        self.assertEqual(t['sections'][-1]['endFrameExclusive'],13225)
        self.assertFalse(t['actualMovingCompositeReviewed']);self.assertFalse(t['humanReviewed'])

    def test_legacy_ids_or_displaced_samples_rejected(self):
        for field,value in [('sceneId','p008-c01'),('startSample',timing['sentences'][0]['startSample']+1)]:
            t=copy.deepcopy(timing);row=next(s for s in t['sentences']if s['sceneId']=='p008-c01a');row[field]=value
            self.assertRaises(b.Pending,b.clock_contract,t,narration)
        t=copy.deepcopy(timing);t['sentences'].pop();self.assertRaises(b.Pending,b.clock_contract,t,narration)

    def test_actual_game_order_native_rate_and_single_required_duplicate(self):
        t=plan();cuts=t['sourceCuts']
        self.assertEqual([x['sourceRange']for x in cuts],[[60,480],[480,961]])
        indices=[i for x in cuts for i in x['sourceIndexSequence']]
        self.assertEqual(len(indices),902);self.assertEqual(len(set(indices)),901)
        self.assertEqual(sorted(set(indices)),list(range(60,961)))
        self.assertTrue(all(x['speed']==[1,1] and x['loop'] is False for x in cuts))

    def test_native_speed_aspect_audio_and_source_extent_reject_changes(self):
        cut=source['selectedCuts'][0]
        for key,value in [('playbackSpeed',.5),('loop',True),('audioAdopted',True),('fullOriginalAspect',False),('imageCrop',[0,0,100,100])]:
            self.assertRaises(b.Pending,b.source_cut,dict(cut,**{key:value}),0)

    def test_whole_word_reentry_has_continuous_labeled_prior_model(self):
        t=plan();cut=t['sourceCuts'][1]
        self.assertEqual(cut['startFrame'],10753)
        p13=[s for s in t['sections']if s['paragraph']==13]
        self.assertEqual(p13[0]['kind'],'native');self.assertEqual(p13[0]['native']['modes'],['threats-a','threats-b'])
        self.assertEqual(p13[0]['endFrameExclusive'],cut['startFrame'])
        self.assertEqual(p13[1]['startFrame'],cut['startFrame']);self.assertEqual(p13[1]['kind'],'actual-game')

    def test_whole_impact_and_fall_fit_without_claiming_moving_review(self):
        t=plan();watch=t['sourceSpeechTimingWatches'][0]
        self.assertEqual([w['exactSpokenPhraseKo']for w in watch['exactSpokenPhrases']],['부딪힙니다.','쓰러지고,'])
        self.assertTrue(watch['numericSpeechOverlapsVisibleEventOrAftermath'])
        self.assertFalse(watch['actualWordEventAlignmentReviewed']);self.assertFalse(watch['automaticSpeechOrActionPass'])
        onset=Fraction(*watch['sourceEventOnsetSeconds'][0]);impact=watch['exactSpokenPhrases'][0]['actualWordInterval']
        self.assertLess(onset,Fraction(impact['endSample'],24000))

    def test_lost_fall_word_or_premature_source_onset_blocks(self):
        cut=plan()['sourceCuts'][1]
        def wrong(t,p,phrase):
            return dict(startSample=1,endSample=100) if phrase=='쓰러지고,' else c.resolve_literal_interval(t,p,phrase)
        self.assertRaisesRegex(b.Pending,'impact-word/source-event',b.word_event_contract,timing,cut,wrong)

    def test_exit_and_connectivity_bind_new_literal_and_physical_ids(self):
        t=plan();exit_frame=c.resolve_literal_interval(timing,8,'출구로')['startFrame']
        p8=[s for s in t['sections']if s['paragraph']==8]
        self.assertEqual(p8[0]['endFrameExclusive'],exit_frame)
        term=next(v for v in t['termCues']if v['english']=='Connectivity')
        self.assertEqual(term['sourceSceneId'],'p013-c04')

    def test_source_inspection_reused_exactly_no_new_viewing_claim(self):
        t=plan();t['actualGameSource']=source['sourceMedia']
        guide=b.verify_moving_guides(b.PROJECT/'footage-moving-guides-v2.json',t)
        self.assertEqual(len(guide['sourceFrameRows']),901)
        self.assertFalse(guide['sourceFrameInspectionRepeated']);self.assertFalse(guide['currentCompositeMovingInspection'])
        changed=copy.deepcopy(guide);changed['sourceFrameRows'][0]['marks']=[{}]
        original=b.read
        with patch.object(b,'read',side_effect=lambda path:changed if Path(path).name=='footage-moving-guides-v2.json' else original(path)):
            self.assertRaisesRegex(b.Pending,'altered',b.verify_moving_guides,b.PROJECT/'footage-moving-guides-v2.json',t)

    def test_missing_current_disposition_cannot_start_analyzer(self):
        with tempfile.TemporaryDirectory()as temp,patch.object(q,'PROJECT',Path(temp)),patch.object(q,'load_analyzer',side_effect=AssertionError('No backend')):
            self.assertRaisesRegex(q.Pending,'Pending actual mixed-ASR3',q.verify,'synthetic-build.json')

    def test_missing_mix_review_blocks_source_job_write(self):
        picture=dict(captionTiming=dict(path='synthetic-caption'),audioBuild=dict(path='synthetic-build'))
        with patch.object(b,'prepare',return_value=dict(picturePlanReady=True,mixedReviewReady=False,picturePlan=picture)),patch.object(b,'immutable_json',side_effect=AssertionError('No artifact write')):
            self.assertRaises(b.Pending,b.write_structure_job,picture)

    def test_no_boolean_acceptance_bypasses_output_flags(self):
        content,levels=mixed_fixture();self.assertTrue(q.qualify(content,levels))
        for stage in ('normalized','prepared','voice','mix'):
            flag=dict(kind='sustained-word-body-decline',scope='paragraph',paragraph=3,stage=stage)
            levels['flags']=[flag];content['retainedFlags']=[flag]
            self.assertRaisesRegex(q.Pending,'Unresolved',q.qualify,content,levels)

    def test_current_whole_explanations_keep_original_range_criteria(self):
        for key,value in [('words',8),('spanSeconds',5.99),('suspect',True)]:
            content,levels=mixed_fixture();levels['wholeExplanations'][0]['trends']['raw'][key]=value
            self.assertRaisesRegex(q.Pending,'nine-word/six-second',q.qualify,content,levels)

    def test_raw_p3_warning_requires_visible_exact_provenance(self):
        content,levels=mixed_fixture();flag=dict(kind='sustained-word-body-decline',scope='paragraph',paragraph=3,stage='raw')
        levels['flags']=[flag];content['retainedFlags']=[flag]
        self.assertRaises(q.Pending,q.qualify,content,levels)
        content.update(rawP3Disposition=q.pin(q.PROJECT/'raw-p3-cross-context-level-review-v1.json'),rawParagraphDiagnosticRetained=True)
        self.assertTrue(q.qualify(content,levels))
        content['retainedFlags']=[];self.assertRaises(q.Pending,q.qualify,content,levels)

    def test_boundary_flags_aliases_and_incomplete_counts_cannot_qualify(self):
        for flag in [dict(kind='mixed-boundary-window-flag'),dict(kind='nonpositive-mixed-word-not-used-as-anchor')]:
            content,levels=mixed_fixture();levels['flags']=[flag];content['retainedFlags']=[flag]
            self.assertRaises(q.Pending,q.qualify,content,levels)
        for key,value in [('aliasesApplied',True),('exactCounts',{}),('actualListening',True),('humanApproval',True)]:
            content,levels=mixed_fixture();content[key]=value;self.assertRaises(q.Pending,q.qualify,content,levels)

    def test_readonly_defaults_never_invoke_resource_or_backend(self):
        with patch.object(a,'libraries',side_effect=AssertionError('No resources')),patch.object(a,'load',side_effect=AssertionError('No builder')):
            self.assertFalse(a.prepare()['ready'])
        with patch.object(b,'module',side_effect=AssertionError('No backend')):
            self.assertFalse(b.prepare()['ready'])

    def test_new_renderer_atlas_and_resource_namespaces(self):
        self.assertEqual(r.OUTPUT.name,'render-attempts-v3');self.assertEqual(a.ATTEMPTS.name,'structure-attempts-v3')
        self.assertEqual(a.SDK.name,'render-solution-path-structure-atlas-v2.cjs')
        self.assertIn('solution-path-postrepair-resource-v1.py',r.PINS)
        resource=load('solution-path-postrepair-resource-v1')
        self.assertIsNot(resource.qualifier,resource.native.qualifier)
        self.assertIsNot(resource.scope,resource.native.busy_reason.__globals__)
        self.assertIs(resource.scope['process_reason'].__globals__,resource.scope)
        for name in ['unity.exe','unrealeditor.exe','ffmpeg.exe','factorio.exe']:
            self.assertIsNotNone(resource.scope['process_reason'](dict(pid=-1,name=name,exe='synthetic',cmdline=[]),999))

if __name__=='__main__':unittest.main()
