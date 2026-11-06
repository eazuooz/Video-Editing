"""Synthetic CPU alignment fixtures only. No ASR/media/model or actual timing claim."""
import copy,importlib.util,unittest,tempfile,wave,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('selected_caption_fixture_target',P/'build-selected-caption-timing.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class CaptionTimingTests(unittest.TestCase):
    def voice_fixture(self,folder,counts):
        folder=Path(folder);chunks=[];entries=[];mapping=[];scenes=[];paragraphs=[];texts=[];payload=[];position=0
        def wav(path,data):
            with wave.open(str(path),'wb')as f:f.setparams((1,2,24000,len(data)//2,'NONE','not compressed'));f.writeframes(data)
            return dict(path=str(path),sha256=m.sha(path),pcmSHA256=hashlib.sha256(data).hexdigest(),frames=len(data)//2)
        for n,count in enumerate(counts,1):
            start=position;ids=[];words=[]
            for j in range(count):
                sid=f'p{n:03}-c{j+1:02}';text=f'합성 검증 문장 {n} {j}.';data=(n*10+j).to_bytes(2,'little',signed=True)*480;row=wav(folder/(sid+'.wav'),data);chunks.append(row);payload.append(data);scenes.append(dict(id=sid,lines=[text]));mapping.append(dict(sceneId=sid,paragraph=n,canonicalText=text));entries.append(dict(scene_id=sid,text=text,start=position/24000,end=(position+480)/24000));position+=480;ids.append(sid);words.append(text)
            text=' '.join(words);texts.append(text);paragraphs.append(dict(paragraph=n,sceneIds=ids,startSample=start,endSample=position,start=start/24000,end=position/24000))
        aggregate=wav(folder/'canonical.wav',b''.join(payload));timing=folder/'timing.json';timing.write_text(json.dumps(dict(sample_rate=24000,entries=entries)),encoding='utf-8');pin=dict(path=str(timing),sha256=m.sha(timing));voice=dict(topicId='07.04',fingerprint='a'*64,identity=dict(scenes=scenes),sceneWavs=chunks,aggregateWav=aggregate,timing=pin,paragraphMapping=mapping);review=dict(voiceFingerprint='a'*64,aggregateSHA256=aggregate['sha256'],timingSHA256=pin['sha256'],paragraphs=paragraphs)
        return voice,review,dict(narrationKo=texts)
    def test_exact_current_component_identity_supports_fourteen_and_twenty_nine(self):
        for counts in [[2]*7,[4,5,5,5,4,2,4]]:
            with tempfile.TemporaryDirectory()as t:
                v,r,n=self.voice_fixture(t,counts);out=m.voice_binding(v,r,n);self.assertEqual(out['rawSelectedTakes'],sum(counts));self.assertTrue(out['canonicalExactConcatVerified'])
    def test_variable_component_count_does_not_accept_reordered_identity(self):
        with tempfile.TemporaryDirectory()as t:
            v,r,n=self.voice_fixture(t,[4,5,5,5,4,2,4]);v['identity']['scenes'][0],v['identity']['scenes'][1]=v['identity']['scenes'][1],v['identity']['scenes'][0]
            with self.assertRaises(m.Pending):m.voice_binding(v,r,n)
    def test_unknown_or_backwards_word_clock_is_rejected(self):
        for words in [[dict(text='가',timestamp=[None,1])],[dict(text='가',timestamp=[1,.5])]]:
            with self.assertRaises(m.Pending):m.literal_alignment('가','가',words,0,2)
    def test_phonetic_difference_remains_visible_without_alias(self):
        get,span,report=m.literal_alignment('스페이셜 디나이얼','스페이셜 디나이아',[dict(text='스페이셜',timestamp=[0,.8]),dict(text='디나이아',timestamp=[.9,1.6])],0,2)
        self.assertTrue(report['alignmentDifferences']);self.assertFalse(report['aliasesApplied']);self.assertFalse(report['automaticSpeechPass']);self.assertEqual(span(0,8)['recognizedLiteral'],'스페이셜 디나이아')
    def test_raw_word_transcript_tampering_is_rejected(self):
        with self.assertRaises(m.Pending):m.literal_alignment('가','나',[dict(text='가',timestamp=[0,1])],0,1)
    def test_long_anchorless_boundary_is_rejected(self):
        get,_,_=m.literal_alignment('가'+'나'*40+'다','가다',[dict(text='가',timestamp=[0,.4]),dict(text='다',timestamp=[.6,1])],0,1)
        with self.assertRaises(m.Pending):get(20)
    def fixture(self):
        narration=m.read(m.PROJECT/'narration-draft.json');clauses=m.read(m.PROJECT/'caption-clauses-v1.json');diagram=m.read(m.PROJECT/'2d-scene-plan-v1.json');rows=[];tick=0
        for n,text in enumerate(narration['narrationKo'],1):
            start=tick;words=[]
            for i,word in enumerate(text.split()):
                words.append(dict(text=word,timestamp=[tick/100,(tick+7)/100],sourceSceneId='synthetic',sourceWordIndex=i));tick+=8
            rows.append(dict(paragraph=n,expectedLiteral=text,recognizedLiteral=text,globalWords=words,start=start/100,end=tick/100,startSample=start*240,endSample=tick*240,sceneIds=['synthetic'],recognitionBasis='assembled-from-blind-component-takes'));tick+=10
        return narration,clauses,dict(paragraphs=rows),diagram
    def test_separate_languages_preserve_all_54_62_cues_and_12_diagram_cues(self):
        args=self.fixture();out=m.build(*args)
        self.assertEqual([len(out['captions'][k]) for k in ['ko','en']],[54,62]);self.assertEqual(len(out['diagramCues']),12)
        self.assertFalse(out['automaticSpeechPass']);self.assertTrue(all(c['humanTimingReviewRequired'] for a in out['captions'].values() for c in a))
        self.assertEqual(sum(c.get('translatedTimingReviewPending',False) for c in out['captions']['en']),16)
    def test_undeclared_translation_split_cannot_be_invented(self):
        args=list(self.fixture());args[1]=copy.deepcopy(args[1]);row=next(g for g in args[1]['groups'] if g['id']=='P2d');row['translatedTimingReviewPending']=False
        with self.assertRaises(m.Pending):m.build(*args)
    def test_missing_source_clause_is_rejected(self):
        args=list(self.fixture());args[1]=copy.deepcopy(args[1]);args[1]['groups'].pop()
        with self.assertRaises(m.Pending):m.build(*args)
    def test_plain_srt_uses_actual_display_text(self):
        text=m.srt([dict(startFrame=60,endFrameExclusive=120,text='정확한 절입니다.')],'ko')
        self.assertIn('00:00:01,000 --> 00:00:02,000',text);self.assertIn('정확한 절입니다.',text);self.assertNotIn('<',text)
    def test_cue_plans_use_whole_paragraph_or_actual_p6_treasure_entry(self):
        timing=m.build(*self.fixture());ref=dict(path='synthetic-fixture',sha256='0'*64);refs={k:ref for k in ['scenePlan','narration','voiceEvidence','captionTiming','asrReview']};voice=dict(fingerprint='1'*64,aggregateWav=dict(path='synthetic-not-read',pcmSHA256='2'*64))
        for segment in ('p2','p6','p7'):
            n=int(segment[1:]);out=m.diagram_cue_payload(timing,segment,refs,voice);para=next(p for p in timing['paragraphs'] if p['paragraph']==n);actual=[c for c in timing['diagramCues'] if c['paragraph']==n]
            self.assertEqual(out['segmentStartGlobalFrame'],actual[0]['startFrame'] if n==6 else para['startFrame']);self.assertEqual(out['segmentEndGlobalFrameExclusive'],para['endFrameExclusive']);self.assertEqual(out['cues'],[dict(id=c['id'],frame=c['startFrame']-out['segmentStartGlobalFrame']) for c in actual]);self.assertFalse(out['rendererStarted'])
    def test_final_nonintegral_pcm_end_is_visually_covered_without_audio_padding(self):
        args=list(self.fixture());args[2]['paragraphs'][-1]['end']+=1/24000
        out=m.build(*args);self.assertEqual(out['paragraphs'][-1]['endFrameExclusive'],out['totalFrames']);self.assertGreaterEqual(out['totalFrames']/60,args[2]['paragraphs'][-1]['end']);self.assertFalse(out['actualListening'])

if __name__=='__main__':unittest.main(verbosity=2)
