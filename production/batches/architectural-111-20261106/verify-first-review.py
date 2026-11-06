"""CPU-only metadata, timing, AAC and collection-scope regression fixtures."""
import copy, importlib.util, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_review_cpu_fixture',HERE/'collect-first-review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-first-review-cpu-');self.base=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

    def video(self):
        return dict(streams=[dict(codec_type='video',codec_name='h264',width=1080,height=1920,r_frame_rate='60/1',avg_frame_rate='60/1',
            sample_aspect_ratio='1:1',duration='0.1'),dict(codec_type='audio',codec_name='aac',sample_rate='48000',channels=2)],format=dict(duration='.11'))

    def test_actual_pts_count_and_uniform_clock_required_not_nominal_fps_alone(self):
        info=self.video();pts=[i/60 for i in range(6)]
        result=review.video_contract(info,pts,6);self.assertEqual(result['decodedFrames'],6)
        with self.assertRaises(AssertionError):review.video_contract(info,pts[:-1],6)
        pts[3]+=.001
        with self.assertRaises(AssertionError):review.video_contract(info,pts,6)

    def test_fhd_portrait_and_audio_stream_contract(self):
        info=self.video();info['streams'][0]['width']=720
        with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)
        info=self.video();info['streams'][1]['channels']=1
        with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)

    def test_cat_reaction_midpoints_join_section_samples_only_on_valid_movie_ranges(self):
        timeline=dict(totalFrames=120,sections=[dict(kind='gameplay',startFrame=0,endFrameExclusive=120)],
            catCues=[dict(pose='realize',startFrame=90,endFrameExclusive=120,easeInFrames=7,easeOutFrames=9),
                dict(pose='puzzled',startFrame=0,endFrameExclusive=1)])
        kinds,samples=review.section_contract(timeline)
        self.assertEqual(kinds,dict(gameplay=120))
        self.assertEqual(samples,[0,59,104,119])  # Section midpoint misses the later reaction.
        for a,b in [(-1,10),(10,10),(20,19),(110,121),(1.5,20),(False,20)]:
            with self.subTest(start=a,end=b):
                changed=copy.deepcopy(timeline);changed['catCues']=[dict(startFrame=a,endFrameExclusive=b)]
                with self.assertRaisesRegex(AssertionError,'Cat reaction range'):review.section_contract(changed)
    def test_same_codec_or_payload_is_insufficient_when_packet_timing_differs(self):
        first=[dict(pts_time='0.000000',dts_time='0.000000',duration_time='.021333',data_hash='SHA256:actual-payload',flags='K_')]
        self.assertTrue(review.same_audio(first,copy.deepcopy(first))['identicalPacketPayloadAndTiming'])
        second=copy.deepcopy(first);second[0]['pts_time']='.010000'
        with self.assertRaises(AssertionError):review.same_audio(first,second)
        second=copy.deepcopy(first);second[0]['data_hash']='SHA256:different'
        with self.assertRaises(AssertionError):review.same_audio(first,second)

    def fixture_captions(self):
        rows=[];tracks={'ko':[],'en':[]};authored={'narrationKo':[],'paragraphsEn':[]};paragraphs=[]
        for i in range(1,7):
            ko=f'문단 {i}.';en=f'Paragraph {i}.';a=(i-1)*60;b=i*60
            rows.append(dict(id=f'p{i}',paragraph=i,startFrame=a,endFrameExclusive=b,ko=ko,en=en,koLines=[ko],enLines=[en]))
            paragraphs.append(dict(paragraph=i,startFrame=a,endFrameExclusive=b,captionIds=[f'p{i}']))
            for language,text in [('ko',ko),('en',en)]:tracks[language].append(dict(index=i,start=a/60,end=b/60,text=text))
            authored['narrationKo'].append(ko);authored['paragraphsEn'].append(en)
        return dict(totalFrames=360,captions=rows,paragraphFrames=paragraphs,
            alignmentReview=dict(literalDifference='메트릭스 / 매트릭스',humanListening=False)),tracks,authored

    def test_six_complete_bilingual_paragraphs_bind_literal_cues_and_preserve_asr_flags(self):
        timeline,tracks,authored=self.fixture_captions();result=review.caption_contract(timeline,tracks,authored)
        self.assertTrue(result['allSixAuthoredKoEnParagraphsRetained']);self.assertFalse(result['speechQualityPass'])
        self.assertEqual(result['rawAsrDiscrepancies'],timeline['alignmentReview'])
        tracks['en'][3]['end']+=.01
        with self.assertRaises(AssertionError):review.caption_contract(timeline,tracks,authored)

    def test_literal_ae_e_difference_cannot_be_hidden_or_words_omitted(self):
        timeline,tracks,authored=self.fixture_captions();authored['narrationKo'][4]='게임플레이 메트릭스입니다.'
        timeline['captions'][4].update(ko='게임플레이 매트릭스입니다.',koLines=['게임플레이 매트릭스입니다.'])
        tracks['ko'][4]['text']='게임플레이 매트릭스입니다.'
        with self.assertRaises(AssertionError):review.caption_contract(timeline,tracks,authored)

    def test_srt_overlap_or_third_line_rejected(self):
        path=self.base/'ko.srt';path.write_text('1\n00:00:00,000 --> 00:00:01,000\n첫 문장\n\n2\n00:00:00,500 --> 00:00:02,000\n겹칩니다\n',encoding='utf-8')
        with self.assertRaises(AssertionError):review.srt(path)
        path.write_text('1\n00:00:00,000 --> 00:00:01,000\n줄1\n줄2\n줄3\n',encoding='utf-8')
        with self.assertRaises(AssertionError):review.srt(path)

    def test_only_selected_path_and_title_keys_change_advanced_project_state_survives(self):
        original=dict(status='human-reviewed',humanApproval=True,finalMovieComplete=True,unrelated={'keep':7},
            paths=dict(script='same-script',checkpoint='keep-checkpoint'),titles=dict(ko='old',ja='keep'))
        result=review.project_patch(original,dict(videoClean='owned-clean'),dict(ko='new',en='English'))
        self.assertEqual(result['status'],'human-reviewed');self.assertTrue(result['humanApproval']);self.assertTrue(result['finalMovieComplete'])
        self.assertEqual(result['unrelated'],original['unrelated']);self.assertEqual(result['paths']['script'],'same-script')
        self.assertEqual(result['titles']['ja'],'keep');self.assertNotIn('videoClean',original['paths'])

    def test_metadata_exact_credits_retained_and_wrong_master_rejected(self):
        source=dict(topicId='03.02',titleKo='정확한 제목',titleEn='Exact title',descriptionKo='크레딧\nCC BY 4.0\nURL',descriptionEn='Full credits\nCC BY 4.0',masterSHA256=None)
        result=review.metadata_packet(source,'actual-sha');self.assertEqual(result['descriptions']['ko'],source['descriptionKo'])
        self.assertEqual(result['masterSHA256'],'actual-sha');self.assertFalse(result['actualHumanFinalReview'])
        source['masterSHA256']='other'
        with self.assertRaises(AssertionError):review.metadata_packet(source,'actual-sha')

    def test_official_collection_insufficient_disk_stops_before_any_staging(self):
        folder=self.base/'review';folder.mkdir();files={}
        for key,suffix in review.SUFFIX.items():
            path=folder/(review.SLUG+'.'+suffix);path.write_bytes(b'fixture');files[key]=dict(file=path.name,sha256=review.sha(path))
        result=dict(metadata={'masterSHA256':'exact-sha'},output=str(folder),deliverables=files)
        with (patch.object(review,'authorize',return_value=None),patch.object(review.shutil,'disk_usage',return_value=SimpleNamespace(free=0)),
            patch.object(review.subprocess,'run',side_effect=AssertionError('No collector may run on failed preflight'))):
            with self.assertRaisesRegex(AssertionError,'Insufficient D space'):review.official_collect(result)


if __name__=='__main__':unittest.main(verbosity=2)
