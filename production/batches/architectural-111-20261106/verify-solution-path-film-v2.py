"""Synthetic clocks and source partitions only; no media/model/render execution."""
from __future__ import annotations
import contextlib, copy, importlib.util, io, json, re, sys, tempfile, unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_film_clock_tests', HERE / 'build-solution-path-film-timeline-v2.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
spec = importlib.util.spec_from_file_location('solution_film_router_tests', HERE / 'render-solution-path-film-v2.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


def fixture():
    narration = b.read(b.PROJECT / 'narration-final-v5.json')
    paragraphs, sentences = [], []
    for p, text in enumerate(narration['narrationKo'], 1):
        parts = re.findall(r'[^.!?]+[.!?]', text)
        assert ' '.join(v.strip() for v in parts) == text
        a, end = (p - 1) * 480000, p * 480000 + (1 if p == 14 else 0)
        # Explicit test-only sample envelopes. No production clock is made here.
        unit = 480000 // len(parts)
        for i, part in enumerate(parts):
            first, last = a + i * unit, end if i == len(parts) - 1 else a + (i + 1) * unit
            sentences.append(dict(sceneId=f'p{p:03}-c{i + 1:02}', paragraph=p, canonicalKo=part.strip(),
                                  startSample=first, endSample=last, startFrame=b.frame_of_sample(first),
                                  endFrameExclusive=b.ceil_frame(last) if p == 14 and i == len(parts) - 1 else b.frame_of_sample(last)))
        paragraphs.append(dict(paragraph=p, canonicalKo=text, canonicalEn=narration['paragraphsEn'][p - 1],
                               startSample=a, endSample=end, startFrame=b.frame_of_sample(a),
                               endFrameExclusive=b.ceil_frame(end) if p == 14 else b.frame_of_sample(end)))
    timing = dict(topicId='11.05', fps=60, totalFrames=b.ceil_frame(paragraphs[-1]['endSample']),
                  audioClock=dict(rawSampleRate=24000, totalRawSamples=paragraphs[-1]['endSample'], noAudioTailPadding=True),
                  paragraphs=paragraphs, sentences=sentences, captions={language:[dict(id=f'{language}-{i:03}',startFrame=i,endFrameExclusive=i+1)
                    for i in range(count)] for language,count in [('ko',98),('en',86)]}, subtitles={})
    cuts = b.read(b.PROJECT / 'source-footage-v2.json')['sources'][0]['selectedCuts']

    def resolve(t, p, phrase):
        if (p,phrase)==(13,'부딪혀 쓰러지죠.'):
            start=t['paragraphs'][12]['startSample']+int(6.2*24000)
            return dict(startSample=start,endSample=start+int(.7*24000),startFrame=b.frame_of_sample(start),
                        endFrameExclusive=b.frame_of_sample(start+int(.7*24000)),actualTestWordBoundary=True)
        offsets = {(4, '옆에 이어지는 지형'): 80, (4, '지역의 분위기가 바뀌면'): 160, (8, '출구 방으로'): 120}
        assert narration['narrationKo'][p - 1].count(phrase) == 1
        start = t['paragraphs'][p - 1]['startFrame'] + offsets[(p, phrase)]
        return dict(startFrame=start, endFrameExclusive=start + 12, actualTestWordBoundary=True)
    return timing, narration, cuts, resolve


class FilmClock(unittest.TestCase):
    def test_cached_builder_source_drift_blocks_before_caption_mix_or_authority(self):
        with patch.object(b,'sha',return_value='0'*64)as hashed,patch.object(b,'authority',side_effect=AssertionError('No authority/backend')), \
             patch.object(b,'module',side_effect=AssertionError('No caption/mix')):
            result=b.prepare('synthetic/caption','synthetic/audio')
        self.assertFalse(result['ready']);self.assertIn('Imported film builder source changed',result['reason'])
        self.assertEqual(hashed.call_count,1)

    def test_cached_structure_job_source_drift_blocks_before_native_or_mc_import(self):
        with patch.object(b,'sha',return_value='0'*64)as hashed,patch.object(b,'module',side_effect=AssertionError('No native/MC')):
            self.assertRaisesRegex(b.Pending,'Imported film builder source changed',b.structure_job,{})
            self.assertRaises(b.Pending,b.self_pin)
        self.assertEqual(hashed.call_count,2)

    def test_renderer_requires_fresh_reviewed_atlas_producer_manifest(self):
        t=dict(structureAtlas=dict(path='synthetic/atlas.json'),picturePlan=dict(captionTiming=dict(path='synthetic/caption.json'),audioBuild=dict(path='synthetic/audio.json')))
        prov=dict(ready=True,synthetic=True);calls=[]
        producer=SimpleNamespace(Pending=r.Pending,prepare=lambda *args:prov,validate_manifest=lambda *args:calls.append(args))
        with patch.object(r,'module',return_value=producer)as loaded,patch.object(r,'read',return_value=dict(job=dict(path='synthetic/job.json'))):r.verify_atlas_producer(t)
        self.assertEqual(calls,[(t['structureAtlas']['path'],prov)])
        self.assertEqual(loaded.call_args.args[1].name,'run-solution-path-structure-atlas-v1.py')

    def test_atlas_producer_pending_or_changed_manifest_blocks_renderer(self):
        t=dict(structureAtlas=dict(path='synthetic/atlas.json'),picturePlan=dict(captionTiming=dict(path='synthetic/caption.json'),audioBuild=dict(path='synthetic/audio.json')))
        def wrong(*_):raise r.Pending('Changed atlas producer/staged source')
        for producer in (SimpleNamespace(Pending=r.Pending,prepare=lambda *_:dict(ready=False),validate_manifest=wrong),
                          SimpleNamespace(Pending=r.Pending,prepare=lambda *_:dict(ready=True),validate_manifest=wrong)):
            with patch.object(r,'module',return_value=producer),patch.object(r,'read',return_value=dict(job=dict(path='synthetic/job.json'))):
                self.assertRaises(r.Pending,r.verify_atlas_producer,t)

    def test_current_source_versions_and_frozen_physical_helpers_are_pinned(self):
        for name, expected in b.SOURCE_PINS.items(): self.assertEqual(b.sha(b.PROJECT / name), expected)
        for name, expected in b.PINS.items(): self.assertEqual(b.sha(b.HERE / name), expected)
        for name, expected in b.MC_PINS.items(): self.assertEqual(b.sha(b.MC_SOURCE / name), expected)
        self.assertEqual(b.CAPTION_FILE, 'build-solution-path-caption-timing-v6.py')
        self.assertEqual(b.MIX_FILE, 'verified-solution-path-audio-build-v5.py')

    def test_default_pending_before_backend_import_and_no_real_prepare(self):
        with patch.object(b, 'authority', return_value={}), patch.object(b, 'SOURCE_PINS', {}), \
             patch.object(b, 'PINS', {}), patch.object(b, 'MC_PINS', {}), \
             patch.object(b, 'module', side_effect=AssertionError('No backend/profile/model import')):
            result = b.prepare()
        self.assertFalse(result['ready']); self.assertFalse(result['jobLaunched'])
        self.assertIn('caption timing', result['reason'])

    def test_backend_pending_remains_truthful_pending_not_a_speech_pass(self):
        class BackendPending(RuntimeError):pass
        def missing(*_):raise BackendPending('Current actual word evidence missing')
        fake=SimpleNamespace(Pending=BackendPending,verify_existing=missing,verified_audio_build=missing)
        with patch.object(b,'authority',return_value={}),patch.object(b,'SOURCE_PINS',{}),patch.object(b,'PINS',{}), \
             patch.object(b,'MC_PINS',{}),patch.object(b,'module',return_value=fake):
            result=b.prepare('synthetic/caption.json','synthetic/audio.json')
        self.assertFalse(result['ready']);self.assertFalse(result['jobLaunched'])
        self.assertIn('word evidence missing',result['reason'])

    def test_full_synthetic_backend_wiring_has_exact_body_only_audio_mapping(self):
        timing,narration,cuts,resolve=fixture()
        fakepin=lambda path:dict(path=str(Path(path).resolve()),sha256='a'*64)
        timing.update(schemaVersion='11.05-selected-caption-timing-v6',inputs=dict(narration=fakepin(b.PROJECT/'narration-final-v5.json')))
        raw=dict(path='synthetic/raw.wav',sha256='b'*64)
        voice=dict(fingerprint='synthetic-current-repaired-voice',aggregateWav=raw,timing=fakepin('synthetic/raw-timing.json'))
        mix=dict(schemaVersion='11.05-audio-build-v5',rawVoiceFingerprint=voice['fingerprint'],rawVoice=raw,
                 canonicalTiming=voice['timing'],mixWav=dict(path='synthetic/mix.wav',sha256='c'*64,
                 frames=timing['audioClock']['totalRawSamples']*2,sampleRate=48000,channels=2))
        cap=SimpleNamespace(Pending=b.Pending,verify_existing=lambda _:dict(timing=timing,voice=voice),resolve_literal_interval=resolve)
        audio=SimpleNamespace(Pending=b.Pending,verified_audio_build=lambda _:mix)
        def load(name,*_):return cap if 'caption' in name else audio
        with patch.object(b,'authority',return_value={}),patch.object(b,'SOURCE_PINS',{}),patch.object(b,'PINS',{}), \
             patch.object(b,'MC_PINS',{}),patch.object(b,'module',side_effect=load),patch.object(b,'pin',side_effect=fakepin), \
             patch.object(b,'bound',return_value=Path('synthetic/source.mp4')),patch.object(b,'verify_atlas'),patch.object(b,'verify_moving_guides'):
            result=b.prepare('synthetic/caption.json','synthetic/audio.json','synthetic/atlas.json','synthetic/guides.json')
        self.assertTrue(result['ready']);t=result['timeline'];mapping=t['encodedAudioMapping']
        self.assertEqual(mapping,dict(reference='accepted-body-mix',bodyStartSample=0,bodyEndSample=mix['mixWav']['frames'],
                         wholeAudioFrames=mix['mixWav']['frames'],rate=48000,noAudioPadding=True))
        self.assertEqual(t['formatReporting']['actualAudioDurationSeconds'],timing['audioClock']['totalRawSamples']/24000)
        self.assertFalse(t['formatReporting']['formalShortsDurationEligible'])
        self.assertFalse(t['actualPixelQaPassed']);self.assertFalse(t['humanApproval'])
        self.assertEqual(t['assemblyProfile']['introAudioSamples'],0);self.assertEqual(t['assemblyProfile']['outroAudioSamples'],0)

    def test_immutable_write_rejects_escape_and_preserves_foreign_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'owned';foreign=Path(temp)/'foreign.json';foreign.write_bytes(b'foreign')
            self.assertRaises(b.Pending,b.immutable_json,foreign,{},root)
            root.mkdir();existing=root/'artifact.json';existing.write_bytes(b'foreign')
            self.assertRaises(b.Pending,b.immutable_json,existing,{},root)
            self.assertEqual(existing.read_bytes(),b'foreign')
            self.assertEqual(foreign.read_bytes(),b'foreign')

    def test_changed_proof_chain_blocks_timeline_write_before_any_output(self):
        with tempfile.TemporaryDirectory() as temp:
            result=dict(ready=True,output=str(Path(temp)/'new/timeline.json'),timeline=dict(picturePlan=dict(
                captionTiming=dict(path='synthetic/caption'),audioBuild=dict(path='synthetic/mix')),
                structureAtlas=dict(path='synthetic/atlas'),movingGuides=dict(path='synthetic/guides')))
            with patch.object(b,'prepare',return_value=dict(ready=False,reason='Changed input')):
                self.assertRaises(b.Pending,b.write_timeline,result)
            self.assertFalse((Path(temp)/'new').exists())

    def test_p13_actual_word_overlap_is_numeric_gate_not_speech_approval(self):
        t = b.plan(*fixture()); row = t['sourceSpeechTimingWatches'][0]
        self.assertEqual((row['sourceLastIntactFrame'], row['sourceFirstImpactBurstFrame']), (853, 854))
        self.assertTrue(row['numericSpeechOverlapsVisibleEventOrAftermath'])
        self.assertFalse(row['actualWordEventAlignmentReviewed']); self.assertFalse(row['automaticSpeechOrActionPass'])
        start = Fraction(*t['sourceCuts'][1]['sourceStartTime'])
        self.assertEqual(Fraction(*row['sourceEventOnsetSeconds'][0]) - start, Fraction(373373,60000))
        self.assertEqual(Fraction(*row['sourceEventOnsetSeconds'][1]) - start, Fraction(374374,60000))

    def test_p13_early_or_late_impact_word_requires_explicit_picture_solution(self):
        args = fixture(); timing, _, cuts, resolve = args
        cut = b.source_cut(cuts[1],timing['paragraphs'][12]['startSample'])
        for offset in (2,9):
            def wrong(t,p,phrase):
                start=t['paragraphs'][12]['startSample']+offset*24000
                return dict(startSample=start,endSample=start+2400)
            self.assertRaisesRegex(b.Pending,'impact-word/source-event',b.word_event_contract,timing,cut,wrong)

    def test_p13_merged_or_unavailable_word_clock_never_guesses(self):
        timing,_,cuts,_=fixture();cut=b.source_cut(cuts[1],timing['paragraphs'][12]['startSample'])
        self.assertRaises(b.Pending,b.word_event_contract,timing,cut,lambda *_:dict(startSample=None,endSample=None))
        def unsupported(*_):raise b.Pending('Whole-word boundary needs explicit evidence or cue reflow')
        self.assertRaisesRegex(b.Pending,'explicit evidence',b.word_event_contract,timing,cut,unsupported)

    def test_actual_source_rate_crop_loop_or_fractional_sample_cannot_be_changed(self):
        cut=fixture()[2][0]
        for key,value in [('playbackSpeed',.5),('playbackSpeed',True),('loop',True),('audioAdopted',True),
                          ('repeatOtherSelectedFrames',True),('fullOriginalAspect',False),('imageCrop',[0,0,100,100])]:
            self.assertRaises(b.Pending,b.source_cut,dict(cut,**{key:value}),0)
        for value in (True,1.5,-1):self.assertRaises(b.Pending,b.source_cut,cut,value)

    def test_complete_raw_take_clock_text_or_caption_partition_changes_rejected(self):
        args=fixture()
        for key,value in [('canonicalKo','changed'),('startSample',1),('endSample',args[0]['sentences'][0]['endSample']-1),('sceneId','p001-c99')]:
            timing=copy.deepcopy(args[0]);timing['sentences'][0][key]=value
            self.assertRaises(b.Pending,b.clock_contract,timing,args[1])
        timing=copy.deepcopy(args[0]);timing['captions']['en'][1]['id']=timing['captions']['en'][0]['id']
        self.assertRaises(b.Pending,b.clock_contract,timing,args[1])

    def test_source_kind_classes_and_observer_unknown_are_explicit(self):
        t=b.plan(*fixture());policy=t['sourceKindPolicy']
        self.assertEqual(policy['actualGame'],'Spelunky (HD) · 실제 플레이')
        self.assertEqual(policy['native'],'Classic 1.1 원리 · 자체 구현')
        self.assertEqual(policy['structure'],'생성 규칙 설명도 · 자체 모형')
        self.assertTrue(policy['observerPixelVisibilityUnknown'])
        self.assertEqual(policy['greenBrokenRouteMeaning'],'의도한 입력 경로')

    def test_unknown_native_mode_and_diagram_or_cat_layout_rejected(self):
        original=b.plan(*fixture())
        for key,value in [('modes',['not-selected']),('layout','stretched')]:
            bad=copy.deepcopy(original);bad['sections'][1]['native'][key]=value
            self.assertRaises(b.Pending,b.validate_plan,bad)
        bad=copy.deepcopy(original);section=next(s for s in bad['sections'] if s['kind']=='native' and s['native']['layout']=='ab-player')
        section['structuralCompanion']=True;self.assertRaises(b.Pending,b.validate_plan,bad)
        bad=copy.deepcopy(original);section=next(s for s in bad['sections'] if s['kind']=='native' and s['native']['layout']=='observer')
        section['catAllowed']=True;self.assertRaises(b.Pending,b.validate_plan,bad)

    def guide_case(self,mutate=None):
        path=b.PROJECT/'footage-moving-guides-v1.json';guide=b.read(path)
        timing=dict(actualGameSource=copy.deepcopy(guide['sourceMedia']),captionTiming=dict(path='synthetic/current.json',sha256='a'*64))
        if mutate:mutate(guide)
        with patch.object(b,'read',return_value=guide),patch.object(b,'bound',return_value=Path('synthetic-bound-proof')):
            return b.verify_moving_guides(path,timing)

    def test_reviewed_per_frame_guide_is_source_only_not_caption_clock(self):
        guide=self.guide_case()
        self.assertIsNone(guide['captionTiming'])
        self.assertEqual(sum(bool(r['marks']) for r in guide['sourceFrameRows']),217)
        self.assertEqual(len(guide['sourceFrameRows']),901)

    def test_guide_wrong_narration_source_timing_or_row_change_rejected(self):
        changes=[lambda g:g['sourceNarration'].update(sha256='0'*64),
                 lambda g:g.update(captionTiming={'path':'guessed','sha256':'0'*64}),
                 lambda g:g['sourceMedia'].update(sha256='0'*64),
                 lambda g:g['sourceFrameRows'][0].update(sourceFrame=61),
                 lambda g:g['sourceFrameRows'][0]['marks'][0].update(labelKo='changed')]
        for change in changes:self.assertRaises(b.Pending,self.guide_case,change)

    def test_visual_cache_excludes_only_nondrawn_state_with_exact_aliases(self):
        packet = dict(mode='construction', nativeFrame=10, fingerprint='a' * 64, sourceKindLabel='생성 규칙 설명도 · 자체 모형',
                      rooms=[dict(id=0, label='R00', center=[220, 230], role='side', entrance=False, exit=False, templateVariant=0)],
                      ports=[dict(a=0, b=1, open=True, role='side', center=[320, 230], broken=False)],
                      route=[dict(a=0, b=1, connected=True)], routeMeaning='currently-open-mandatory-ports', routeLabel='현재 열린 통로',
                      phase='a', actualPlayerPoint=[100, 100])
        changed = copy.deepcopy(packet)
        changed.update(nativeFrame=11, fingerprint='b' * 64, phase='b', actualPlayerPoint=[200, 100])
        changed['rooms'][0]['templateVariant'] = 1
        packets, aliases = b.atlas_layout([packet, changed], [dict(path='style.tsx', sha256='c' * 64)])
        self.assertEqual(len(packets), 1)
        self.assertEqual([v['atlasIndex'] for v in aliases], [0, 0])
        self.assertEqual([v['packetFingerprint'] for v in aliases], ['a' * 64, 'b' * 64])
        self.assertEqual([v['nativeFrame'] for v in aliases], [10, 11])
        changed['ports'][0]['open'] = False
        packets, aliases = b.atlas_layout([packet, changed], [])
        self.assertEqual(len(packets), 2)

    def test_visual_cache_invalidates_drawn_exit_label_or_style_changes(self):
        a = dict(sourceKindLabel='생성 규칙 설명도 · 자체 모형', rooms=[], ports=[], route=[],
                 routeMeaning='intended-input-only', routeLabel='닫힘')
        old = b.digest(b.visual_identity(a, ['font-old']))
        for key, value in [('routeLabel', '연결됨'), ('sourceKindLabel', '실제 플레이')]:
            changed = dict(a, **{key: value})
            self.assertNotEqual(b.digest(b.visual_identity(changed, ['font-old'])), old)
        self.assertNotEqual(b.digest(b.visual_identity(a, ['font-new'])), old)

    def test_structure_definition_focus_excludes_companion(self):
        t = b.plan(*fixture())
        # Output-frame requests are compiled from actual native clocks only.
        requests = b.structure_requests(t)
        self.assertEqual(len(requests), len({(v['mode'], v['nativeFrame']) for v in requests}))
        self.assertTrue(all(0 <= v['nativeFrame'] < 3120 for v in requests))
        self.assertIn(dict(mode='construction', nativeFrame=239), requests)
        self.assertIn(dict(mode='construction', nativeFrame=240), requests)

    def test_exact_contact_name_preserves_actual_source_domain(self):
        self.assertFalse(r.enemy_contact(dict(contactColliderNames=[])))
        self.assertTrue(r.enemy_contact(dict(contactColliderNames=['Own patrol/contact actor'])))
        self.assertFalse(r.enemy_contact(dict(contactColliderNames=['EnemyBody', 'template-spike-trigger'])))

    def test_unknown_source_mark_does_not_carry_across_frame(self):
        rows = [dict(sourceFrame=i, marks=[]) for i in range(60, 961)]
        rows[0]['marks'] = [dict(kind='ellipse')]
        self.assertTrue(r.manual_mark(rows, 60))
        self.assertFalse(r.manual_mark(rows, 61))
        self.assertRaises(r.Pending, r.manual_mark, rows, 961)

    def test_sample_without_execute_starts_no_worker(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['render', '--sample-frame=510']), patch.object(r, 'execute', side_effect=AssertionError('No implicit work')), contextlib.redirect_stdout(output):
            self.assertEqual(r.main(), 0)
        self.assertFalse(json.loads(output.getvalue())['jobLaunched'])

    def test_actual_final_sample_requires12721(self):
        self.assertEqual(b.ceil_frame(5088001), 12721)
        self.assertEqual(b.ceil_frame(5088000), 12720)

    def test_full14_picture_partition_has_no_audio_or_visual_gap(self):
        t = b.plan(*fixture())
        self.assertEqual(t['sections'][0]['startFrame'], 0)
        self.assertEqual(t['sections'][-1]['endFrameExclusive'], t['totalFrames'])
        self.assertEqual([v['paragraph'] for v in t['paragraphs']], list(range(1, 15)))
        self.assertTrue(b.validate_plan(t)['completeFramePartition'])

    def test_common_clock_uses_no_independent_source_ceils(self):
        cuts=fixture()[2]
        a=b.source_cut(cuts[0],0)
        end=Fraction(*a['selectedSourceElapsedEnd'])
        bb=b.source_cut(cuts[1],5000196,end)
        self.assertEqual(a['endFrameExclusive']-a['startFrame'],421)
        self.assertEqual(bb['endFrameExclusive']-bb['startFrame'],481)
        self.assertEqual(len(a['sourceIndexSequence'])+len(bb['sourceIndexSequence']),902)
        independent=sum((c['displayedFrameCount']*1001+999)//1000 for c in cuts)
        self.assertEqual(independent,903)
        for start in (1, 12345, 24041, 5080000):
            row=b.source_cut(cuts[0],start)
            self.assertEqual(row['endFrameExclusive']-row['startFrame'],421)
            self.assertLess(abs(Fraction(*row['startQuantizationError'])),Fraction(1,60))
            self.assertLess(abs(Fraction(*row['endQuantizationError'])), Fraction(1, 60))

    def test_cumulative_cfr_visits_all901_native_inputs_at_nonzero_body_phases(self):
        cuts=fixture()[2];a=b.source_cut(cuts[0],0)
        for phase in (0,1,196,199,200,201,399,12345,24041):
            bb=b.source_cut(cuts[1],5000000+phase,Fraction(*a['selectedSourceElapsedEnd']))
            indices=a['sourceIndexSequence']+bb['sourceIndexSequence']
            self.assertEqual(len(indices),902);self.assertEqual(sorted(set(indices)),list(range(60,961)))
            self.assertEqual(indices,sorted(indices));self.assertEqual(indices[420],479);self.assertEqual(indices[421],480)
            self.assertEqual(indices[-1],960)
            for cut in (a,bb):
                self.assertLess(Fraction(*cut['cfrCoverage']['maxPresentationError']),Fraction(1,60))
                self.assertLess(abs(Fraction(*cut['endQuantizationError'])),Fraction(1,60))

    def test_old_nearest_only_sampler_reproduces_phase_sensitive960_omission(self):
        cuts=fixture()[2];a=b.source_cut(cuts[0],0)
        bb=b.source_cut(cuts[1],5000196,Fraction(*a['selectedSourceElapsedEnd']))
        last=bb['endFrameExclusive']-1
        elapsed=Fraction(last,60)-Fraction(*bb['sourceStartTime'])
        old=480+b.nearest(elapsed*Fraction(60000,1001))
        self.assertEqual(old,959);self.assertEqual(b.source_index(bb,last),960)

    def test_source_cut_clears_marks_even_at_cfr_repeated_endpoint(self):
        cuts=fixture()[2];a=b.source_cut(cuts[0],0)
        bb=b.source_cut(cuts[1],5000196,Fraction(*a['selectedSourceElapsedEnd']))
        rows=[dict(sourceFrame=i,marks=[]) for i in range(60,961)]
        rows[479-60]['marks']=[dict(id='synthetic-A-only')]
        self.assertTrue(r.manual_mark(rows,b.source_index(a,a['endFrameExclusive']-1)))
        self.assertFalse(r.manual_mark(rows,b.source_index(bb,bb['startFrame'])))

    def test_nearest_pinned_pts_keeps_source_order_and_endpoints(self):
        for source in fixture()[2]:
            cut = b.source_cut(source, 0)
            rows = [b.source_index(cut, f) for f in range(cut['startFrame'], cut['endFrameExclusive'])]
            self.assertEqual(rows, sorted(rows))
            self.assertEqual(rows[0], source['startFrame'])
            self.assertEqual(rows[-1], source['endFrameExclusive'] - 1)
            self.assertTrue(all(a <= c <= a + 1 for a, c in zip(rows, rows[1:])))

    def test_only_two_official_ranges_appear_once_without_retiming(self):
        t = b.plan(*fixture())
        cuts = [s['actualGame'] for s in t['sections'] if s['kind'] == 'actual-game']
        self.assertEqual([v['sourceRange'] for v in cuts], [[60, 480], [480, 961]])
        self.assertTrue(all(v['speed'] == [1, 1] and not v['loop'] for v in cuts))

    def test_no_fallback_for_short_actual_game_paragraph(self):
        args = list(fixture()); args[0]['paragraphs'][0]['endFrameExclusive'] = 400
        self.assertRaises(b.Pending, b.plan, *args)

    def test_gap_overlap_or_missing_last_frame_rejected(self):
        original = b.plan(*fixture())
        for field, value in [('startFrame', original['sections'][1]['startFrame'] + 1),
                             ('startFrame', original['sections'][1]['startFrame'] - 1),
                             ('endFrameExclusive', original['sections'][1]['startFrame'])]:
            t = copy.deepcopy(original); t['sections'][1][field] = value
            self.assertRaises(b.Pending, b.validate_plan, t)
        t = copy.deepcopy(original); t['sections'][-1]['endFrameExclusive'] -= 1
        self.assertRaises(b.Pending, b.validate_plan, t)

    def test_purposeful_holds_do_not_replay_motion(self):
        t = b.plan(*fixture())
        for s in t['sections']:
            if s['kind'] != 'native': continue
            first, last = b.native_index(s, s['startFrame']), b.native_index(s, s['endFrameExclusive'] - 1)
            self.assertEqual(last - first, s['endFrameExclusive'] - s['startFrame'] - 1 if s['native']['playback'] == 'native1x' else 0)
            if s['native']['playback'] == 'held': self.assertTrue(s['native']['holdReason'])

    def test_unlabelled_hold_missing_native_tail_and_late_broken_player_rejected(self):
        t = b.plan(*fixture())
        hold = next(i for i, v in enumerate(t['sections']) if v['kind'] == 'native' and v['native']['playback'] == 'held')
        for field, value in [('holdReason', None), ('startFrame', 3120)]:
            bad = copy.deepcopy(t); bad['sections'][hold]['native'][field] = value
            self.assertRaises(b.Pending, b.validate_plan, bad)
        bad = copy.deepcopy(t)
        row = next(v for v in bad['sections'] if v['paragraph'] == 7 and v.get('reviewedClosedPortGuide'))
        row['native']['startFrame'] = 2880
        self.assertRaises(b.Pending, b.validate_plan, bad)

    def test_ab_pairs_share_one_native_frame_and_distinct_modes(self):
        t = b.plan(*fixture())
        for s in t['sections']:
            if s['kind'] == 'native' and s['native']['layout'].startswith('ab-'):
                self.assertEqual(len(set(s['native']['modes'])), 2)
                self.assertIsInstance(b.native_index(s, s['startFrame']), int)
        bad = copy.deepcopy(t)
        row = next(v for v in bad['sections'] if v['kind'] == 'native' and v['native']['layout'].startswith('ab-'))
        row['native']['modes'] = ['branches-a', 'branches-a']
        self.assertRaises(b.Pending, b.validate_plan, bad)

    def test_held1560_observer_rule_cannot_be_propagated(self):
        original = b.plan(*fixture())
        row = next(v for v in original['sections'] if v.get('reviewedClosedPortGuide'))
        self.assertEqual(row['native']['startFrame'], 1560)
        for key, value in [('startFrame', 1561), ('layout', 'observer'), ('modes', ['branches-a'])]:
            t = copy.deepcopy(original)
            next(v for v in t['sections'] if v.get('reviewedClosedPortGuide'))['native'][key] = value
            self.assertRaises(b.Pending, b.validate_plan, t)

    def test_missing_word_anchor_cannot_use_character_ratio(self):
        args = list(fixture())
        def unavailable(*_): raise b.Pending('Actual literal boundary unavailable')
        args[3] = unavailable
        self.assertRaisesRegex(b.Pending, 'literal boundary', b.plan, *args)

    def test_all_six_term_definitions_use_complete_take_envelopes(self):
        t = b.plan(*fixture())
        self.assertEqual(len(t['termCues']), 6)
        for term in t['termCues']:
            sentence = next(v for v in t['sentences'] if v['sceneId'] == term['sourceSceneId'])
            self.assertGreaterEqual(term['startFrame'], sentence['startFrame'])
            self.assertEqual(term['endFrameExclusive'], sentence['endFrameExclusive'])

    def test_conservative_structure_bounds_include_full_stroke(self):
        left, top, width, height = b.STRUCTURE_CONTENT_BOXES[1]
        self.assertLessEqual(left, 220 - 75 - 2.5)
        self.assertLessEqual(top, 230 - 58 - 2.5)
        self.assertGreaterEqual(left + width, 820 + 75 + 2.5)
        self.assertGreaterEqual(top + height, 725 + 58 + 2.5)


class Lifecycle(unittest.TestCase):
    def run_case(self, folder, first_reason, post_reason=None, foreign=False, worker_busy=False):
        root = Path(folder); lease = root / 'lease.json'; state = root / 'state.json'
        state.write_text('{"previous":"preserve"}', encoding='utf8')
        if foreign: lease.write_text('{"owner":"foreign","token":"foreign-token"}', encoding='utf8')
        old_state, old_lease = state.read_bytes(), lease.read_bytes() if foreign else None
        events = []
        class Worker:
            previous = None
            def acquire(self):
                if worker_busy: raise r.Pending('Live exact existing worker')
                events.append('acquire'); return self
            def update(self, **_): events.append('update')
            def close(self, **_): events.append('close')
        worker = Worker()
        rt = SimpleNamespace(LEASE=lease, SingleWorker=lambda path: worker,
                             identity=lambda: dict(pid=1234, create_time=12., argv=['synthetic-render', '--execute']),
                             alive=lambda _: False, archive=lambda *_: events.append('archive'))
        rt.ours = lambda row: row.get('owner') == rt.OWNER
        class Controller:
            def __init__(self, *_): events.append('controller')
            def terminate_owned(self): events.append('terminate-owned-handles-only')
        def save(path, value):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(json.dumps(value), encoding='utf8')
        lib = SimpleNamespace(reclaimable_lease=lambda *_: False, pending_child=lambda *_: False,
                              OwnedController=Controller, CONTROLLER=None, save=save)
        resource = SimpleNamespace(rt=rt, busy_reason=lambda token=None: post_reason if token else first_reason)
        def load(_name, path, _sha): return resource if Path(path).name == 'run-solution-path-native-v4.py' else lib
        timeline = dict(picturePlan=dict(totalFrames=100, sections=[dict(startFrame=0, endFrameExclusive=100)]))
        bfake = SimpleNamespace(authority=lambda: {'localFinalReviewOnly': True})
        target = root / 'timeline.json'; target.write_text('{}', encoding='utf8')
        with patch.object(r, 'verify_timeline', return_value=(timeline, bfake)), patch.object(r, 'module', side_effect=load), \
             patch.object(r, 'MEDIA', root), patch.object(r, 'OUTPUT', root / 'attempts'), patch.object(r, 'STATE', state), \
             patch.object(r, 'WORKER', root / 'worker.json'), patch.object(r.shutil, 'disk_usage', return_value=SimpleNamespace(free=8 * 1024**3)), \
             patch.object(r, '_render', side_effect=AssertionError('No media job may start')):
            try: result = r.execute(target)
            except r.Pending as error: result = dict(error=str(error))
        return result, state, lease, old_state, old_lease, events

    def test_foreign_activity_declines_before_attempt_or_state_write(self):
        with tempfile.TemporaryDirectory() as temp:
            result, state, lease, old_state, _, events = self.run_case(temp, 'foreign activity')
            self.assertEqual(result['exitCode'], 75)
            self.assertEqual(state.read_bytes(), old_state)
            self.assertFalse(lease.exists())
            self.assertNotIn('controller', events)

    def test_foreign_lease_race_preserves_foreign_bytes_and_previous_state(self):
        with tempfile.TemporaryDirectory() as temp:
            result, state, lease, old_state, old_lease, events = self.run_case(temp, None, foreign=True)
            self.assertEqual(result['exitCode'], 75)
            self.assertEqual(lease.read_bytes(), old_lease)
            self.assertEqual(state.read_bytes(), old_state)
            self.assertNotIn('archive', events)

    def test_postlease_race_launches_nothing_preserves_partial_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            result, state, lease, _, _, events = self.run_case(temp, None, 'foreign arrived')
            self.assertIn('Resources changed', result['error'])
            self.assertFalse(lease.exists())
            self.assertEqual(json.loads(state.read_text(encoding='utf8'))['status'], 'failed-preserved')
            self.assertIn('terminate-owned-handles-only', events)

    def test_live_worker_cannot_overwrite_previous_state(self):
        with tempfile.TemporaryDirectory() as temp:
            result, state, lease, old_state, _, events = self.run_case(temp, None, worker_busy=True)
            self.assertIn('Live exact existing worker', result['error'])
            self.assertEqual(state.read_bytes(), old_state)
            self.assertFalse(lease.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
