"""Meaningful CPU fixtures only. Synthetic word times are NEVER production ASR."""
import copy, importlib.util, math, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_timeline_cpu_test',HERE/'build-first-timeline.py')
timeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(timeline)


class FirstTimelineTests(unittest.TestCase):
    def setUp(self):
        self.n=timeline.read(timeline.PROJECT/'narration-editorial-v1.json')
        self.plan=timeline.read(timeline.PROJECT/'edit-plan-v1.json')
        self.normal,self.bold,_=timeline.fonts()

    def fixture(self,wrong_metrics=True):
        durations=[18.56,19.2,24,19.52,20.4,18.08];entries=[];records=[];position=0
        for i,(text,duration) in enumerate(zip(self.n['narrationKo'],durations),1):
            spoken=text.replace('메트릭스','매트릭스') if i==5 and wrong_metrics else text
            words=spoken.split();weights=[len(timeline.asr.folded(w)) for w in words];total=sum(weights)
            raw=[];cursor=position+.1
            for word,weight in zip(words,weights):
                end=cursor+(duration-.2)*weight/total
                raw.append(dict(text=word,timestamp=[cursor,end]));cursor=end
            entry=dict(scene_id=f's{i:02}',text=text,start=position,end=position+duration)
            record=dict(task=dict(expected=text),text=spoken,rawRecognition={'text':spoken},globalWords=raw,
                        comparison=timeline.asr.comparison(text,spoken))
            entries.append(entry);records.append(record);position+=duration
        return dict(entries=entries,duration_seconds=position),records

    def aligned(self):
        timing,records=self.fixture()
        return timing,records,timeline.caption_and_beat_frames(self.n,self.plan,timing,records,self.normal,self.bold)

    def test_all_authored_ko_en_and_25_beats_are_preserved_at_fixed_caption_size(self):
        timing,records,(cues,beats,paragraphs,reviews)=self.aligned()
        self.assertEqual(len(beats),25);self.assertEqual(len(paragraphs),6)
        for i,(ko,en) in enumerate(zip(self.n['narrationKo'],self.n['paragraphsEn']),1):
            rows=[c for c in cues if c['paragraph']==i]
            self.assertEqual(timeline.text_identity(' '.join(c['ko'] for c in rows)),timeline.text_identity(ko))
            self.assertEqual(timeline.text_identity(' '.join(c['en'] for c in rows)),timeline.text_identity(en))
            for c in rows:
                for language in ['ko','en']:
                    self.assertLessEqual(len(c[language+'Lines']),2)
                    for line in c[language+'Lines']:self.assertLessEqual(max(self.normal.getlength(line),self.bold.getlength(line)),800)
        self.assertEqual(beats[0]['startFrame'],0)
        self.assertEqual(beats[-1]['endFrameExclusive'],timeline.frame(timing['duration_seconds']))

    def test_word_boundaries_follow_changed_actual_word_clock_not_lesson_proportion(self):
        timing,records=self.fixture(False)
        _,before,_,_=timeline.caption_and_beat_frames(self.n,self.plan,timing,records,self.normal,self.bold)
        # Move a measured literal-word boundary without changing paragraph length.
        target=next(w for w in records[0]['globalWords'] if '팀'==w['text'])
        target['timestamp'][0]+=.12
        _,after,_,_=timeline.caption_and_beat_frames(self.n,self.plan,timing,records,self.normal,self.bold)
        old=next(b for b in before if b['id']=='P1b');new=next(b for b in after if b['id']=='P1b')
        self.assertGreater(new['startFrame'],old['startFrame'])
        self.assertEqual(before[-1]['endFrameExclusive'],after[-1]['endFrameExclusive'])

    def test_literal_metric_ae_e_error_survives_with_canonical_display_and_no_pass(self):
        timing,records,(cues,beats,paragraphs,reviews)=self.aligned()
        fifth=reviews[4]
        self.assertIn('매트릭스',fifth['recognizedLiteral']);self.assertIn('메트릭스',fifth['expectedLiteral'])
        self.assertTrue(fifth['comparison']['characterDifferences']);self.assertFalse(fifth['aliasesApplied'])
        self.assertFalse(fifth['automaticSpeechPass']);self.assertFalse(fifth['humanListening'])
        self.assertTrue(any('메트릭스' in c['ko'] for c in cues))
        self.assertFalse(any('매트릭스' in c['ko'] for c in cues))
        cue=next(c for c in cues if '메트릭스' in c['ko'])
        mapping=cue['literalDisplayAlignment']
        self.assertIn('매트릭스',mapping['recognizedLiteral']);self.assertIn('메트릭스',mapping['displayLiteral'])
        self.assertTrue(mapping['rawRecognitionSHA256']);self.assertFalse(mapping['aliasesApplied'])
        self.assertFalse(mapping['canonicalDisplayReview']['audioPronunciationVerified'])
        self.assertFalse(mapping['canonicalDisplayReview']['globalReplacementApplied'])

    def test_unknown_asr_time_or_stale_authored_text_is_a_real_blocker(self):
        timing,records=self.fixture();records[1]['globalWords'][3]['timestamp'][0]=None
        with self.assertRaisesRegex(timeline.Pending,'timestamp missing'):
            timeline.caption_and_beat_frames(self.n,self.plan,timing,records,self.normal,self.bold)
        timing,records=self.fixture();n=copy.deepcopy(self.n);n['paragraphsEn'][2]+=' Unapproved addition.'
        with self.assertRaisesRegex(AssertionError,'EN authored clauses stale'):
            timeline.caption_and_beat_frames(n,self.plan,timing,records,self.normal,self.bold)

    def test_complete_native_trials_once_1x_and_actual_sources_never_repeat_or_pad(self):
        timing,records,(cues,beats,paragraphs,reviews)=self.aligned()
        sources={s['id']:s for s in timeline.read(timeline.PROJECT/'source-footage.json')['sources'] if s['id'] in [timeline.A,timeline.B]}
        sections=timeline.make_sections(beats,cues,sources,self.n['glossary'])
        self.assertEqual(sections[0]['sourceId'],timeline.A);self.assertEqual(sections[0]['sourceLocalInPts'],25)
        self.assertEqual(sections[0]['rate'],1)
        for left,right in zip(sections,sections[1:]):self.assertEqual(left['endFrameExclusive'],right['startFrame'])
        for mode in ['narrow','wide']:
            actual=[s['native'] for s in sections if s.get('native',{}).get('mode')==mode and s['native']['holdPolicy'] is None]
            self.assertEqual([f for x in actual for f in range(x['startNativeFrame'],x['startNativeFrame']+x['frameCount'])],list(range(270)))
        for s in sections:
            if s.get('native',{}).get('holdPolicy'):
                self.assertTrue(s['native']['holdPolicy']['reason']);self.assertTrue(s['native']['holdPolicy']['activeExplanation'])
            if s.get('native',{}).get('layout')=='dual':self.assertIsNone(s['catPose'])
        with self.assertRaisesRegex(timeline.Pending,'budget exhausted'):timeline.SourcePool([(timeline.A,25,26)]).take(61)

    def test_ko_en_srt_share_exact_plain_cue_clocks(self):
        _,_,(cues,_,_,_)=self.aligned()
        ko=timeline.srt(cues,'ko');en=timeline.srt(cues,'en')
        self.assertEqual([l for l in ko.splitlines() if '-->' in l],[l for l in en.splitlines() if '-->' in l])
        self.assertNotIn('{\\',ko);self.assertNotIn('<font',ko)
        self.assertEqual(ko.count(' --> '),len(cues))

    def test_renderer_pure_structure_contract_accepts_the_built_fixture(self):
        timing,records,(cues,beats,paragraphs,reviews)=self.aligned()
        sources={s['id']:s for s in timeline.read(timeline.PROJECT/'source-footage.json')['sources'] if s['id'] in [timeline.A,timeline.B]}
        sections=timeline.make_sections(beats,cues,sources,self.n['glossary'])
        renderer=timeline.asr.module('first_timeline_renderer_contract_fixture',HERE/'render-first-film.py')
        with patch.object(renderer.subprocess,'Popen',side_effect=AssertionError('No render/encoder in pure contract check')):
            result=renderer.validate_structure(dict(schemaVersion='03-02-final-timeline-v1',format=dict(width=1080,height=1920,fps=60),
                totalFrames=beats[-1]['endFrameExclusive'],sections=sections,captions=cues))
        self.assertEqual(result['nativeMovingFrames'],{'narrow':270,'wide':270})
        for c in cues:
            for lang in ['ko','en']:
                self.assertEqual(timeline.one_line_emphasis(c[lang],c[lang+'Lines'],c['emphasis'][lang]),c['emphasis'][lang])

    def test_guides_reveal_gap_then_defined_collision_then_spoken_input(self):
        timing,records,(cues,beats,paragraphs,reviews)=self.aligned()
        sources={s['id']:s for s in timeline.read(timeline.PROJECT/'source-footage.json')['sources'] if s['id'] in [timeline.A,timeline.B]}
        sections=timeline.make_sections(beats,cues,sources,self.n['glossary'])
        expected={'P3a':None,'P3b':['clearance'],'P3c':['clearance'],
                  'P3d':['clearance','footprint'],'P3e':['clearance','footprint'],
                  'P4a':['clearance','footprint'],'P4b':['clearance','footprint','input']}
        for section in sections:
            if section['beatId'] not in expected:continue
            guides=[c for c in section['annotationCues'] if c['kind']=='native-guides']
            self.assertEqual([c['guideParts'] for c in guides],[] if expected[section['beatId']] is None else [expected[section['beatId']]])
            for cue in guides:
                self.assertEqual(cue['startFrame'],section['startFrame']);self.assertEqual(cue['endFrameExclusive'],section['endFrameExclusive'])

    def test_ieee_float_final_mix_is_read_without_rewriting_integer_voice(self):
        import numpy as np,soundfile as sf
        with tempfile.TemporaryDirectory(prefix='first-timeline-float-mix-') as folder:
            path=Path(folder)/'mix.wav';sf.write(path,np.zeros((4800,2),dtype=np.float32),48000,subtype='FLOAT')
            before=path.read_bytes();info=timeline.mix_info(path)
            self.assertEqual(info['subtype'],'FLOAT');self.assertEqual(info['frames'],4800);self.assertEqual(info['channels'],2)
            self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main(verbosity=2)
