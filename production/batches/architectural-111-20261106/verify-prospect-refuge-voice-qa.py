"""CPU-only adapter fixtures: temporary synthetic PCM, no recognizer/model."""
import copy, hashlib, importlib.util, json, sys, tempfile, unittest, wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('prospect_asr_fixture', HERE/'run-prospect-refuge-voice-qa.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='prospect-asr-fixture-')
        self.root = Path(self.tmp.name)
        self.project = self.root/'projects'/m.SLUG
        self.project.mkdir(parents=True)
        self.proof_path, self.state_path = self.root/'proof.json', self.root/'state.json'
        self.component_path = self.project/'components.json'
        self.patch = patch.multiple(m, ROOT=self.root, PROOF=self.proof_path,
                                    VOICE_STATE=self.state_path, COMPONENT_PLAN=self.component_path)
        self.patch.start()
        self.alive = patch.object(m.qa.voice, 'alive', return_value=False); self.alive.start()
        self.children = patch.object(m.qa.voice, 'project_children', return_value=[]); self.children.start()
        self.verifier = patch.object(m.qa.voice, 'verify_complete', side_effect=lambda *_: self.read(self.proof_path))
        self.verifier.start()
        self.write(self.root/'shared/publishing/video-production-control.json', {m.qa.AUTH_KEY:dict(
            status='active', automaticAdvanceWithinExactList=True,
            automaticAdvanceOutsideList=False, humanFinalReviewRequired=True)})

    def tearDown(self):
        self.verifier.stop(); self.children.stop(); self.alive.stop(); self.patch.stop(); self.tmp.cleanup()

    def write(self, p, d):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, ensure_ascii=False)+'\n', encoding='utf8')

    def read(self, p): return json.loads(p.read_text(encoding='utf8'))

    def make_voice(self):
        ko, rows = [], []
        for n in range(1, 26):
            parts = [f'문단{n} 문장{j}.' for j in range(1, 4 if 19<=n<=22 else 5)]
            ko.append(' '.join(parts))
            rows.append(dict(paragraph=n, components=[dict(text=t,reason='Complete fixture sentence') for t in parts]))
        draft = dict(titleKo='Fixture', narrationKo=ko, paragraphsEn=['Fixture']*25)
        narration = self.project/'narration-draft.json'; self.write(narration,draft)
        plan = dict(sourceNarrationSHA256=m.sha(narration), paragraphs=rows)
        self.write(self.component_path, plan)
        groups=m.qa.voice.prep.components_for(ko,plan,m.sha(narration))
        script,mapping=m.qa.voice.prep.make_scenes(draft,groups)
        identity=dict(scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']], fixture=True)
        fp=m.digest(identity); out=self.root/'shared/output/architectural-111-20261106/06-02/voice-attempts'/fp[:24]
        out.mkdir(parents=True); chunks, entries, all_pcm, position=[],[],bytearray(),0
        for n,s in enumerate(identity['scenes']):
            pcm=(n+1).to_bytes(2,'little')*240
            p=out/'chunks'/(s['id']+'-scene.wav');p.parent.mkdir(exist_ok=True)
            with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
            chunks.append(dict(path=str(p),frames=240))
            entries.append(dict(scene_id=s['id'],text=' '.join(s['lines']),start=position/24000,end=(position+240)/24000))
            all_pcm.extend(pcm);position+=240
        timing=out/'timing.json';self.write(timing,dict(entries=entries))
        proof=dict(topicId=m.TOPIC,output=str(out),fingerprint=fp,identity=identity,sceneWavs=chunks,
                   aggregateWav=dict(frames=position,pcmSHA256=hashlib.sha256(all_pcm).hexdigest()),
                   timing=dict(path=str(timing),sha256=m.sha(timing)),paragraphMapping=mapping)
        self.write(self.proof_path,proof);self.write(self.state_path,dict(completed=True,fingerprint=fp,child=None))
        return proof

    def test_missing_or_live_voice_is_pending_without_model(self):
        with self.assertRaises(m.Pending):m.exact_voice()
        self.make_voice();s=self.read(self.state_path);s['completed']=False;self.write(self.state_path,s)
        with self.assertRaises(m.Pending):m.exact_voice()

    def test_complete_96_take_25_paragraph_pcm_binding(self):
        self.make_voice();_,proof,timing,draft=m.exact_voice()
        self.assertEqual(len(proof['sceneWavs']),96);self.assertEqual(len(draft['narrationKo']),25)
        self.assertEqual(len(timing['entries']),96)

    def test_old07_output_is_rejected(self):
        p=self.make_voice();p['output']=p['output'].replace('/06-02/','/07-04/').replace('\\06-02\\','\\07-04\\')
        self.write(self.proof_path,p)
        with self.assertRaises(ValueError):m.exact_voice()

    def test_reordered_or_missing_component_mapping_is_rejected(self):
        p=self.make_voice();p['paragraphMapping'][0],p['paragraphMapping'][1]=p['paragraphMapping'][1],p['paragraphMapping'][0]
        self.write(self.proof_path,p)
        with self.assertRaises(ValueError):m.exact_voice()

    def test_changed_raw_pcm_cannot_use_old_aggregate_proof(self):
        p=self.make_voice();w=Path(p['sceneWavs'][0]['path'])
        with wave.open(str(w),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\x7f\x00'*240)
        with self.assertRaises(ValueError):m.exact_voice()

    def test_shifted_sample_clock_is_rejected(self):
        p=self.make_voice();path=Path(p['timing']['path']);t=self.read(path);t['entries'][4]['start']+=2/24000
        self.write(path,t)
        with self.assertRaises(ValueError):m.exact_voice()

    def test_new_job_pins_wrapper_and_unchanged_library_separately(self):
        base=dict(identity=dict(adapterSHA256=m.sha(m.__file__),tasks=[]),voiceOutput=str(self.root/'voice'),
                  sourcePins=[dict(path=str(Path(m.__file__)),sha256=m.sha(m.__file__))],output='old',fingerprint='old')
        original=copy.deepcopy(base)
        with patch.object(m,'_library_prepare_job',return_value=base):job=m.prepare_job()
        self.assertEqual(base,original)
        self.assertEqual(job['identity']['pinnedSelectedAsrLibrarySHA256'],m.BASE_SHA)
        self.assertEqual(job['fingerprint'],m.digest(job['identity']))
        self.assertIn(dict(path=str(m.BASE_PATH),sha256=m.BASE_SHA),job['sourcePins'])

    def test_both_old_and_new_recognizer_children_are_preserved(self):
        rows=[SimpleNamespace(pid=900001,info=dict(cmdline=['python',str(m.BASE_PATH),'--recognize'])),
              SimpleNamespace(pid=900002,info=dict(cmdline=['python',str(Path(m.__file__)),'--recognize']))]
        with patch.object(m.qa.psutil,'process_iter',return_value=rows),patch.object(m.qa.voice,'identity',side_effect=lambda p:dict(pid=p)):
            self.assertEqual([p['pid']for p in m.child_processes()],[900001,900002])

    def test_context_and_child_entry_are_exact06(self):
        self.assertEqual(m.qa.TOPIC,'06.02');self.assertEqual(m.qa.raw.SLUG,m.SLUG)
        self.assertEqual(m.qa.runtime.OWNER,m.OWNER);self.assertEqual(Path(m.qa.__file__),Path(m.__file__))
        self.assertIn('06-02',str(m.qa.STATE));self.assertNotIn('07-04',str(m.qa.WORKER))


if __name__=='__main__': unittest.main(verbosity=2)
