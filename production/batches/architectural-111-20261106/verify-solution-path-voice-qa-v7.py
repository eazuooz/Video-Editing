"""Synthetic repair-proof/PCM fixtures and retained V5 guard regressions only."""
import ast
import hashlib
import math
import re
import copy
import importlib.util
import io
import json
import struct
import sys
import tempfile
import unittest
import wave
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result

SOURCE = HERE/'run-solution-path-voice-qa-v7.py'
SOURCE_TEXT=SOURCE.read_text(encoding='utf8');TREE=ast.parse(SOURCE_TEXT)
CONSTANTS={n.targets[0].id:ast.literal_eval(n.value) for n in TREE.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ('PINS','EXPECTED_REPAIR_VOICE_FP')}
FROZEN=CONSTANTS['EXPECTED_REPAIR_VOICE_FP']is not None and all(v is not None for v in CONSTANTS['PINS'].values())
m = load('solution_v7_asr_cpu',SOURCE) if FROZEN else None
previous = load('solution_v7_retained_v5_cpu', HERE/'verify-solution-path-voice-qa-v5.py') if FROZEN else None
if previous is not None:previous.m=m


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return path

def wav(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as stream:
        stream.setparams((1, 2, 24000, 48, 'NONE', 'not compressed'))
        stream.writeframes(struct.pack('<h', value)*48)

@unittest.skipUnless(FROZEN,'V3 source/full voice fingerprint not frozen; full PCM integration remains Pending')
class RepairProof(unittest.TestCase):
    def fixture(self, change_profile=False, wrong_reuse_count=False):
        temporary = tempfile.TemporaryDirectory(prefix='solution-v7-repair-cpu-')
        self.addCleanup(temporary.cleanup)
        self.root = root = Path(temporary.name)
        counts = [4]*6+[3]*8  # Current episode has48 complete sentences in14 paragraphs.
        draft = dict(topicId='11.05', titleKo='Synthetic repair fixture', narrationFinalized=True, ttsReady=True,
                     narrationKo=[' '.join(f'{j+1}번 문을 확인합니다.' for j in range(n)) for n in counts],
                     paragraphsEn=['Synthetic exact source.']*14)
        narration = dump(root/'projects/shorts-leveldesign-11-05/narration-final-fixture.json', draft)
        cp = dict(expandedNarrationDraft=dict(finalized=True),
                  currentProduction=dict(narrationFinalized=True, ttsReady=True))
        script, mapping = m.prep.sentence_plan(draft, m.sha(narration))
        scenes = [dict(id=s['id'], lines=s['lines']) for s in script['scenes']]
        profile = m.qa.read(m.PROFILE_PATH)
        identity = m.profile_identity(scenes, profile)
        if change_profile:
            identity['tts']['language'] = 'English'
        selection = dict(protocol=m.repair.PROTOCOL, newNarration=m.pin(narration),
                         repairSceneIds=list(m.repair.TARGETS), sourceVoiceFingerprint='e'*64,
                         expectedFullCount=48, expectedByteReusedCount=45, expectedNewCount=3)
        identity['repairSelection'] = selection
        fingerprint = m.digest(identity)
        out = root/'shared/output/architectural-111-20261106/11-05/voice-attempts'/fingerprint[:24]
        rows = []
        for index, scene in enumerate(scenes):
            target = out/'chunks'/(scene['id']+'-scene.wav')
            wav(target, index+1)
            if scene['id'] not in m.repair.TARGETS:
                source = root/'preserved-old-raw'/target.name
                wav(source, index+1)
                rows.append(dict(oldSceneId=scene['id'], newSceneId=scene['id'],
                                 canonicalText=scene['lines'][0], sourceWav=m.qa.voice.wav_info(source)))
        if wrong_reuse_count:
            rows = rows[:-1]
        missing = [s for s in scenes if s['id'] in m.repair.TARGETS]
        repair_identity = dict(repairSelection=selection, missingScenes=missing, reuse=rows)
        repair = dict(identity=repair_identity, fingerprint=m.digest(repair_identity), rows=rows, missing=missing)
        prov = dict(topicId='11.05', slug=m.SLUG, identity=identity, fingerprint=fingerprint,
                    paragraphMapping=mapping, voiceOutputDirectory=str(out), repair=repair,
                    inputs=[m.pin(narration)])
        stage = (root/'projects'/m.SLUG/'production/voice-preparation'/('a'*24)/
                 ('repair-subset-'+repair['fingerprint'][:24]))
        dump(stage/'narration-missing-only.json', dict(scenes=missing))
        dump(stage/'voice-missing-only-manifest.json', dict(engineSceneIds=list(m.repair.TARGETS)))
        dump(stage/'subset-repair-preparation.json', dict(fullVoiceFingerprint=fingerprint,
                                                        repairFingerprint=repair['fingerprint']))
        (stage/'repair-adapter-source.py').write_bytes((HERE/'run-solution-path-voice-repair-v3.py').read_bytes())
        payload, entries, position = [], [], 0
        for scene in missing:
            with wave.open(str(out/'chunks'/(scene['id']+'-scene.wav')), 'rb') as stream:
                data=stream.readframes(stream.getnframes())
            start=position;position+=len(data)//2;payload.append(data)
            entries.append(dict(scene_id=scene['id'],text=scene['lines'][0],start=start/24000,end=position/24000))
        with wave.open(str(out/'narration.wav'), 'wb') as stream:
            stream.setparams((1,2,24000,position,'NONE','not compressed'));stream.writeframes(b''.join(payload))
        dump(out/'narration.timing.json',dict(sample_rate=24000,render_mode='scene',
                                            duration_seconds=position/24000,entries=entries))
        (out/'narration.srt').write_text('\n\n'.join(
            f"{i+1}\n00:00:00,{i*2:03} --> 00:00:00,{(i+1)*2:03}\n{scene['lines'][0]}"
            for i,scene in enumerate(missing))+'\n',encoding='utf-8')
        engine = dict(engineSceneScope='missing-subset-only', subsetAggregateAndTimingValidated=True,
                      engineSceneIds=list(m.repair.TARGETS),engineSceneCount=3,fullCanonicalSceneCount=48,
                      reusedSceneIds=[r['newSceneId'] for r in rows],
                      aggregateWav=m.qa.voice.wav_info(out/'narration.wav'),
                      timing=m.pin(out/'narration.timing.json'),srt=m.pin(out/'narration.srt'),
                      subsetInputs=[m.pin(stage/name) for name in ('narration-missing-only.json',
                          'voice-missing-only-manifest.json','subset-repair-preparation.json','repair-adapter-source.py')])
        # Invoke the real pure PCM/lifecycle primitive, not a mocked completion stub.
        proof = m.voice_worker.life.canonical_outputs(prov, out, engine)
        immutable = dump(out/'voice-complete-proof.json', proof)
        dump(out/'voice-inputs.json', dict(protocol=m.qa.voice.PROTOCOL,
                                         fingerprint=fingerprint, identity=identity,
                                         inputs=[m.pin(narration)]))
        dump(out/'repair-inputs.json', m.voice_worker.life.repair_receipt(prov))
        pointer = dump(root/'voice-evidence.json', proof)
        state = dump(root/'voice-state.json', dict(completed=True, fingerprint=fingerprint, child=None))
        dump(root/'shared/publishing/video-production-control.json',
             {m.qa.AUTH_KEY:dict(status='active', automaticAdvanceWithinExactList=True,
                                automaticAdvanceOutsideList=False, humanFinalReviewRequired=True,
                                youtubeAuthorized=False)})
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name, value in [('ROOT', root), ('PROOF', pointer), ('VOICE_STATE', state),
                            ('EXPECTED_REPAIR_VOICE_FP', fingerprint)]:
            stack.enter_context(patch.object(m, name, value))
        stack.enter_context(patch.object(m, 'legacy_barrier'))
        stack.enter_context(patch.object(m.prep, 'current_inputs', return_value=(cp,narration,draft,narration)))
        stack.enter_context(patch.object(m.repair, 'prepare', return_value=prov))
        stack.enter_context(patch.object(m.qa.voice, 'project_children', return_value=[]))
        return prov, proof, out, pointer, state, narration, immutable

    def republish(self, proof, out, pointer):
        dump(out/'voice-complete-proof.json', proof)
        dump(pointer, proof)

    def test_full_repair_prov_reaches_both_real_verifiers_and_exact95_windows(self):
        prov, proof, out, *_ = self.fixture()
        life = m.voice_worker.life
        with patch.object(life, 'verify_complete', wraps=life.verify_complete) as complete, \
             patch.object(life, 'validate_receipt', wraps=life.validate_receipt) as receipt:
            actual_out, actual, timing, _ = m.exact_voice()
        complete.assert_called_once_with(prov, out)
        receipt.assert_called_once_with(prov, out)
        tasks = m.qa.build_tasks(actual, timing)
        self.assertEqual(actual_out, out)
        self.assertEqual(len(tasks), 95)
        self.assertEqual(sum(t['kind']=='take' for t in tasks), 48)
        self.assertEqual(sum(t.get('joinType')=='paragraph-boundary' for t in tasks), 13)
        self.assertEqual(tasks[47]['endSample'], proof['aggregateWav']['frames'])

    def test_old_voice_alias_pending_before_source_repair_profile_or_pcm(self):
        _, proof, _, pointer, *_ = self.fixture()
        proof['identity'].pop('repairSelection')
        proof['fingerprint'] = 'e'*64
        dump(pointer, proof)
        with patch.object(m, 'source_context', side_effect=AssertionError('no source/profile read')), \
             patch.object(m.repair, 'prepare', side_effect=AssertionError('no repair/model hashing')), \
             patch.object(m.qa, 'pcm_bytes', side_effect=AssertionError('no PCM read')):
            self.assertRaises(m.Pending, m.exact_voice)

    def test_approved_profile_is_exact_except_only_repair_selection(self):
        self.fixture(change_profile=True)
        self.assertRaisesRegex(ValueError, 'approved voice profile', m.exact_voice)

    def test_preparer_identity_cannot_be_replaced_by_matching_base_stub(self):
        prov, *_ = self.fixture()
        prov['identity'] = {k:v for k,v in prov['identity'].items() if k!='repairSelection'}
        self.assertRaisesRegex(ValueError, 'identity', m.exact_voice)

    def test_missing_one_of45_raw_reuses_rejected(self):
        self.fixture(wrong_reuse_count=True)
        self.assertRaisesRegex(ValueError, 'repair selection', m.exact_voice)

    def test_missing_immutable_repair_receipt_rejected(self):
        _, _, out, *_ = self.fixture()
        (out/'repair-inputs.json').unlink()
        self.assertRaisesRegex(RuntimeError, 'subset-repair identity', m.exact_voice)

    def test_engine_cannot_claim_full_script_or_include_reused_take(self):
        _, proof, out, pointer, *_ = self.fixture()
        proof['engineOutputsPreserved']['engineSceneIds'].append('p001-c01')
        self.republish(proof, out, pointer)
        self.assertRaisesRegex(RuntimeError, 'subset engine scope', m.exact_voice)

    def test_missing_actual_engine_artifact_or_count_is_rejected(self):
        _,proof,out,pointer,*_=self.fixture()
        for key in ('aggregateWav','timing','srt','engineSceneCount','fullCanonicalSceneCount','reusedSceneIds'):
            wrong=copy.deepcopy(proof);wrong['engineOutputsPreserved'].pop(key)
            self.republish(wrong,out,pointer)
            self.assertRaises(ValueError,m.exact_voice)

    def test_subset_input_proof_cannot_be_empty_or_point_to_another_adapter(self):
        _,proof,out,pointer,*_=self.fixture()
        wrong=copy.deepcopy(proof);wrong['engineOutputsPreserved']['subsetInputs']=[]
        self.republish(wrong,out,pointer)
        self.assertRaisesRegex(ValueError,'Four exact',m.exact_voice)
        adapter=Path(proof['engineOutputsPreserved']['subsetInputs'][3]['path'])
        adapter.write_text('foreign adapter',encoding='utf-8')
        proof['engineOutputsPreserved']['subsetInputs'][3]=m.pin(adapter)
        self.republish(proof,out,pointer)
        self.assertRaisesRegex(ValueError,'reviewed V3 worker',m.exact_voice)

    def test_rebound_actual_three_engine_timing_is_independently_recomputed(self):
        _,proof,out,pointer,*_=self.fixture()
        path=out/'narration.timing.json';timing=m.qa.read(path)
        timing['entries'][0]['end']+=.5;dump(path,timing)
        proof['engineOutputsPreserved']['timing']=m.pin(path)
        self.republish(proof,out,pointer)
        self.assertRaisesRegex(ValueError,'Engine timing boundaries',m.exact_voice)

    def test_reused_chunk_mutation_is_detected_by_full_lifecycle(self):
        _, proof, *_ = self.fixture()
        path = Path(proof['sceneWavs'][0]['path'])
        payload = bytearray(path.read_bytes());payload[-2] ^= 1;path.write_bytes(payload)
        self.assertRaisesRegex(RuntimeError, 'PCM changed', m.exact_voice)

    def test_one_raw_sample_clock_shift_rejected_at1e9(self):
        _, proof, out, pointer, *_ = self.fixture()
        path = Path(proof['timing']['path']);timing=m.qa.read(path)
        timing['entries'][0]['end'] += 1/24000
        dump(path,timing);proof['timing']['sha256']=m.sha(path)
        self.republish(proof,out,pointer)
        self.assertRaisesRegex(ValueError,'sample boundary',m.exact_voice)

    def test_raw_aggregate_cannot_gain_or_reorder_even_with_rebound_hashes(self):
        _, proof, out, pointer, *_ = self.fixture()
        path=Path(proof['aggregateWav']['path']);payload=bytearray(path.read_bytes())
        payload[-2]^=1;path.write_bytes(payload);proof['aggregateWav']=m.qa.voice.wav_info(path)
        self.republish(proof,out,pointer)
        self.assertRaisesRegex(ValueError,'concatenation',m.exact_voice)

    def test_job_pins_current_repair_and_immutable_proof_without_cache_migration(self):
        prov, proof, out, pointer, *_ = self.fixture()
        tasks=m.qa.build_tasks(proof,m.qa.read(proof['timing']['path']))
        job=dict(identity=dict(tasks=tasks,voiceFingerprint=prov['fingerprint'],
                               modelPins=m.qa.APPROVED['modelPins'],
                               trustedUtilitySHA256=m.qa.APPROVED['trustedSHA256']),
                 voiceOutput=str(out),voiceEvidence=m.pin(pointer),sourcePins=[])
        with patch.object(m,'_library_prepare_job',return_value=job):actual=m.prepare_job()
        self.assertEqual(actual['voiceEvidence'],m.pin(out/'voice-complete-proof.json'))
        self.assertEqual(actual['identity']['repairSelection'],prov['identity']['repairSelection'])
        self.assertEqual(actual['identity']['currentVoiceWorkerSHA256'],m.PINS['run-solution-path-voice-repair-v3.py'])
        self.assertEqual(actual['identity']['currentRepairPreparerSHA256'],m.PINS['prepare-solution-path-voice-repair-v3.py'])
        cache=m.qa.raw_cache_path(actual,tasks[0]).resolve()
        self.assertTrue(cache.is_relative_to(out/'review/blind-raw-cache-v1'))

@unittest.skipUnless(FROZEN,'V3 source freeze Pending')
class RetainedGuards(previous.ResourceAndEvidenceTests if previous is not None else unittest.TestCase):
    def launcher(self):
        info,own,parent=super().launcher()
        for row in (info,own,parent):row['cmdline'][4]=str(Path(m.__file__).resolve())
        return info,own,parent

    def test_old_v5_recognizer_script_is_not_this_launcher(self):
        info,own,parent=self.launcher()
        for row in (info,own,parent):row['cmdline'][4]=str(HERE/'run-solution-path-voice-qa-v5.py')
        self.assertFalse(m.launcher_matches(info,own,parent))

    def test_versions_are_separate_and_resource_hook_is_nested_repair_instance(self):
        self.assertEqual(m.qa.PROTOCOL,'architectural111-11-05-voice-asr-v7')
        self.assertEqual(m.qa.WORKER.name,'11-05-asr-v7-worker.json')
        self.assertIs(m.resource,m.repair.voice_entry.resource)
        self.assertIs(m.resource.process_reason,m.scoped_process_reason)
        self.assertIs(m.prep,m.repair.prep)
        self.assertEqual(m.PINS['run-solution-path-voice-qa-v5.py'],
                         '1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c')

@unittest.skipUnless(FROZEN,'V3 source freeze Pending')
class LegacyReadOnly(unittest.TestCase):
    def fixture(self, record=None, processes=()):
        temporary=tempfile.TemporaryDirectory(prefix='solution-v7-legacy-cpu-')
        self.addCleanup(temporary.cleanup);root=Path(temporary.name)
        stack=ExitStack();self.addCleanup(stack.close)
        markers=tuple(root/n for n in ('11-05-asr-v4-progress.json','11-05-asr-v4-worker.json','11-05-asr-v5-progress.json','11-05-asr-v5-worker.json','11-05-asr-v6-progress.json','11-05-asr-v6-worker.json'))
        stack.enter_context(patch.object(m,'LEGACY_MARKERS',markers))
        stack.enter_context(patch.object(m.qa.psutil,'process_iter',return_value=processes))
        stack.enter_context(patch.object(m.qa.voice,'alive',side_effect=lambda x:bool(x and x.get('syntheticLive'))))
        if record is not None:
            record=dict(legacy_record(5),**record)
            if record.get('child')is not None:record['child']=dict(legacy_record(5),**record['child'])
            dump(markers[2],record)
        return markers

    def test_dead_v4_v5_markers_preserved(self):
        markers=self.fixture(dict(syntheticLive=False,child=None));dump(markers[0],legacy_record(4,syntheticLive=False))
        before={p:p.read_bytes() for p in markers if p.exists()}
        m.legacy_barrier()
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_live_old_coordinator_child_or_unreadable_marker_blocks(self):
        for row in (dict(syntheticLive=True),dict(child=dict(syntheticLive=True))):
            self.fixture(row);self.assertRaises(m.Pending,m.legacy_barrier)
        markers=self.fixture();markers[1].write_text('{broken',encoding='utf-8')
        self.assertRaises(m.Pending,m.legacy_barrier)

    def test_unregistered_v4_v5_and_unknown_python_barriers(self):
        for name in m.LEGACY_ENTRIES:
            self.fixture(processes=[SimpleNamespace(info=dict(name='python.exe',cmdline=['python',name,'--recognize']))])
            self.assertRaises(m.Pending,m.legacy_barrier)
        self.fixture(processes=[SimpleNamespace(info=dict(name='python.exe',cmdline=None))])
        self.assertRaises(m.Pending,m.legacy_barrier)

    def test_cross_output_raw_cache_never_migrates(self):
        with tempfile.TemporaryDirectory(prefix='solution-v7-cache-scope-') as temp:
            root=Path(temp);job,task,source,cache=previous.LegacyAndCacheV5.cache_fixture(self,root)
            row=m.qa.read(cache)
            row['originJob']['path']=str(root/'foreign-old-voice/review/job.json')
            dump(cache,row)
            self.assertRaises(ValueError,m.qa.restore_raw_cache,job)
            self.assertFalse((Path(job['output'])/(task['key']+'.json')).exists())

# Retain only the V5-specific pure matcher negatives, not its old version labels.
for name in (() if previous is None else ('test_only_argv0_differs_not_full_tail','test_wrong_actual_body_executable_or_argv0',
             'test_extra_or_abbreviated_cli_rejected_even_matching_tails',
             'test_old_or_foreign_script_never_exempted','test_foreign_job_or_decline_path_rejected',
             'test_invalid_process_time_relation_rejected','test_changed_runtime_pin_fails_closed')):
    setattr(RetainedGuards,name,getattr(previous.LauncherV5Regression,name))

def local_digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def legacy_record(version=6,**overrides):
    args=['python',f'run-solution-path-voice-qa-v{version}.py','--execute']
    row=dict(protocol=f'architectural111-11-05-voice-asr-v{version}',owner=f'architectural-111-11-05-asr-v{version}',pid=123,createTime=100.0,argv=args,commandSHA256=local_digest(args),child=None)
    row.update(overrides);return row

class NewPureGuards(unittest.TestCase):
    def namespace(self,**values):
        class Pending(RuntimeError):pass
        ns=dict(Path=Path,hashlib=hashlib,math=math,re=re,Pending=Pending)
        ns.update(values)
        names={'SourceFreezePending','check_sources','inspected_identity','legacy_barrier'}
        nodes=[n for n in TREE.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual-v7-pure-guards','exec'),ns)
        return ns
    def test_pending_freeze_before_runtime_or_dependency_reads(self):
        ns=self.namespace(__file__=str(SOURCE),SELF_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),EXPECTED_REPAIR_VOICE_FP=None,PINS={'missing':None},LAUNCHER_RUNTIME_PINS=[{'path':'never-read','sha256':'x'}])
        self.assertRaises(ns['SourceFreezePending'],ns['check_sources'])
    def test_source_drift_rejected_before_pending(self):
        ns=self.namespace(__file__=str(SOURCE),SELF_SHA='0'*64,EXPECTED_REPAIR_VOICE_FP=None,PINS={})
        self.assertRaisesRegex(RuntimeError,'changed after import',ns['check_sources'])
    def test_three_engine_contract_rejects_wrong_count_or_ids_before_files(self):
        node=next(n for n in TREE.body if isinstance(n,ast.FunctionDef)and n.name=='verify_subset_engine')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-three-engine-count-gate','exec'),ns)
        targets=['p008-c01','p008-c02','p013-c01']
        for ids,reuses,full in [(targets[:2],45,48),(targets[::-1],45,48),(targets,44,48),(targets,45,47)]:
            prov={'repair':{'missing':[{'id':x}for x in ids],'rows':[{'newSceneId':str(i)}for i in range(reuses)]},'identity':{'scenes':[{}]*full}}
            self.assertRaisesRegex(ValueError,'Exact missing3',ns['verify_subset_engine'],prov,Path('unused'),{})
    def test_three_engine_contract_still_requires_real_engine_proof(self):
        node=next(n for n in TREE.body if isinstance(n,ast.FunctionDef)and n.name=='verify_subset_engine')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-three-engine-count-gate','exec'),ns)
        prov={'repair':{'missing':[{'id':x}for x in ['p008-c01','p008-c02','p013-c01']],'rows':[{'newSceneId':str(i)}for i in range(45)]},'identity':{'scenes':[{}]*48}}
        self.assertRaisesRegex(ValueError,'scope proof differs',ns['verify_subset_engine'],prov,Path('unused'),{})
    def test_valid_identity_and_unknown_corrupt_identity(self):
        ns=self.namespace(qa=SimpleNamespace(digest=local_digest));self.assertTrue(ns['inspected_identity'](legacy_record()))
        for row in ({},None,legacy_record(pid=True),legacy_record(createTime=float('nan')),legacy_record(argv=[]),legacy_record(commandSHA256='wrong')):
            self.assertFalse(ns['inspected_identity'](row))
    def legacy(self,rows=None,processes=()):
        temp=tempfile.TemporaryDirectory(prefix='v7-legacy-pure-');self.addCleanup(temp.cleanup);root=Path(temp.name)
        markers=tuple(root/f'11-05-asr-v{v}-progress.json' for v in (4,5,6))
        for p,row in zip(markers,rows or[]):dump(p,row)
        class Gone(Exception):pass
        class Denied(Exception):pass
        qa=SimpleNamespace(read=lambda p:json.loads(p.read_text(encoding='utf8')),digest=local_digest,voice=SimpleNamespace(alive=lambda r:bool(r and r.get('syntheticLive'))),psutil=SimpleNamespace(process_iter=lambda _:processes,NoSuchProcess=Gone,AccessDenied=Denied))
        ns=self.namespace(qa=qa,LEGACY_MARKERS=markers,LEGACY_ENTRIES={f'run-solution-path-voice-qa-v{v}.py'for v in (4,5,6)})
        return ns,markers
    def test_all_three_valid_dead_histories_accepted_without_mutation(self):
        ns,markers=self.legacy([legacy_record(v)for v in (4,5,6)]);before={p:p.read_bytes()for p in markers};ns['legacy_barrier']();self.assertEqual(before,{p:p.read_bytes()for p in markers})
    def test_unknown_empty_or_wrong_topic_marker_blocks(self):
        for row in ({},legacy_record(4,owner='foreign'),legacy_record(6)):
            ns,_=self.legacy([row]);self.assertRaises(ns['Pending'],ns['legacy_barrier'])
    def test_legacy_live_controller_or_child_blocks(self):
        for row in (legacy_record(4,syntheticLive=True),legacy_record(4,child=legacy_record(4,syntheticLive=True))):
            ns,_=self.legacy([row]);self.assertRaises(ns['Pending'],ns['legacy_barrier'])
    def test_unknown_child_and_unresolved_durable_launch_gap_blocks(self):
        for row in (legacy_record(4,child={}),legacy_record(4,phase='launching')):
            ns,_=self.legacy([row]);self.assertRaises(ns['Pending'],ns['legacy_barrier'])
    def test_unregistered_v6_execute_and_recognize_blocks(self):
        for flag in ('--execute','--recognize'):
            ns,_=self.legacy(processes=[SimpleNamespace(info={'name':'python.exe','cmdline':['python','run-solution-path-voice-qa-v6.py',flag]})]);self.assertRaises(ns['Pending'],ns['legacy_barrier'])
    def test_unknown_python_command_and_unreadable_marker_blocks(self):
        ns,_=self.legacy(processes=[SimpleNamespace(info={'name':'python.exe','cmdline':None})]);self.assertRaises(ns['Pending'],ns['legacy_barrier'])
        ns,markers=self.legacy();markers[0].write_text('{bad',encoding='utf8');self.assertRaises(ns['Pending'],ns['legacy_barrier'])

if __name__=='__main__':
    suite=unittest.TestSuite()
    for group in (NewPureGuards,RepairProof,RetainedGuards,LegacyReadOnly):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(group))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
