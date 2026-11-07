"""Synthetic103physical/96logical CPU contracts; no recognizer/model/job runs."""
import copy,hashlib,importlib.util,json,struct,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('prospect_103_asr_cpu',HERE/'run-prospect-refuge-voice-qa-v2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return p

class Source103Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='prospect-asr103-cpu-');cls.root=Path(cls.temp.name)
  old=json.loads((m.ROOT/'projects/shorts-leveldesign-06-02/caption-clauses-v3.json').read_text(encoding='utf8'));cls.draft=dict(topicId='06.02',titleKo='Synthetic fixture',narrationKo=[],paragraphsEn=['Synthetic translation.']*25);cls.plan=dict(topicId='06.02',sourceNarrationSHA256='a'*64,paragraphs=[],logicalGroups=[])
  for p in range(1,26):
   rows=[g for g in old['groups']if g['paragraph']==p];components=[];cursor=0
   for j,g in enumerate(rows):
    logical=f'p{p:03}-c{j+1:02}';text=g['ko'];parts=text.split(', ',1)if logical in m.SPLIT_LOGICAL_IDS else[text]
    if len(parts)==2:parts[0]+=','
    assert len(parts)==(2 if logical in m.SPLIT_LOGICAL_IDS else 1)
    ids=[];begin=cursor
    for k,part in enumerate(parts,1):
     sid=f'p{p:03}-c{len(components)+1:02}';ids.append(sid);end=cursor+len(part);components.append(dict(text=part,reason='Synthetic exact semantic source unit',physicalSceneId=sid,sourceCharRange=[cursor,end],logicalSceneId=logical,logicalSentenceIndexZeroBased=j,logicalPartIndex=k,logicalPartCount=len(parts)));cursor=end+1
    for k,part in enumerate(components[-len(parts):],1):part['logicalSourceCharRange']=[part['sourceCharRange'][0]-begin,part['sourceCharRange'][1]-begin];part['canonicalJoinerAfter']=' 'if k<len(parts)else''
    cls.plan['logicalGroups'].append(dict(id=logical,groupId=f'P{p}{chr(97+j)}',beatId=f'06.02-P{p:02}-S{j+1:02}',paragraph=p,logicalSentenceIndexZeroBased=j,logicalSceneId=logical,canonicalText=text,sourceCharRange=[begin,cursor-1],physicalSceneIds=ids,physicalParts=[dict(physicalSceneId=q['physicalSceneId'],sourceCharRange=q['sourceCharRange'],logicalSourceCharRange=q['logicalSourceCharRange'],logicalPartIndex=q['logicalPartIndex'])for q in components[-len(parts):]],canonicalInterComponentJoiner=' '))
   cls.plan['paragraphs'].append(dict(paragraph=p,components=components));cls.draft['narrationKo'].append(' '.join(g['ko']for g in rows))
  cls.groups,cls.logical=m.component_groups(cls.draft,cls.plan,'a'*64)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_exact103_96_25(self):self.assertEqual(sum(map(len,self.groups.values())),103);self.assertEqual(len(self.logical),96);self.assertEqual(len(self.groups),25)
 def test_exact_seven_comma_splits(self):self.assertEqual({g['logicalSceneId']for g in self.logical if len(g['physicalSceneIds'])==2},m.SPLIT_LOGICAL_IDS)
 def test_source_char_coverage_reconstructs_whole_paragraphs(self):
  for p in range(1,26):self.assertEqual(' '.join(c['text']for c in self.groups[p]),self.draft['narrationKo'][p-1])
 def test_generic_mapping_retains103physical_not96logical_ids(self):
  script,mapping=m.qa.voice.prep.make_scenes(self.draft,self.groups);self.assertEqual(len(script['scenes']),103);self.assertEqual(len(mapping),103);self.assertEqual(mapping[0]['sourceCharRange'],self.groups[1][0]['sourceCharRange']);self.assertNotIn('logicalSceneId',mapping[0])
 def test_wrong_narration_hash_rejected(self):
  with self.assertRaises(m.Pending):m.component_groups(self.draft,self.plan,'0'*64)
 def test_old96component_plan_rejected(self):
  p=copy.deepcopy(self.plan);p['logicalGroups']=p['logicalGroups'][:-1]
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_renumbered_physical_id_rejected(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][0]['components'][0]['physicalSceneId']='p001-c99'
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_rewritten_physical_text_rejected(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][0]['components'][0]['text']+='changed'
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_missing_one_source_char_rejected(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][3]['components'][3]['sourceCharRange'][1]-=1
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_reordered_logical_group_rejected(self):
  p=copy.deepcopy(self.plan);p['logicalGroups'][0],p['logicalGroups'][1]=p['logicalGroups'][1],p['logicalGroups'][0]
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_duplicate_physical_unit_in_logical_group_rejected(self):
  p=copy.deepcopy(self.plan);p['logicalGroups'][0]['physicalSceneIds']=p['logicalGroups'][1]['physicalSceneIds']
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_changed_part_metadata_rejected(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][3]['components'][3]['logicalPartCount']=1
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_logical_physical_parts_metadata_tamper_rejected(self):
  p=copy.deepcopy(self.plan);p['logicalGroups'][0]['physicalParts'][0]['logicalSourceCharRange'][1]-=1
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_synthetic_audio_joiner_cannot_replace_canonical_space(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][3]['components'][3]['canonicalJoinerAfter']=''
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_three_parts_or_noncomma_split_rejected(self):
  p=copy.deepcopy(self.plan);p['logicalGroups'][15]['physicalSceneIds']*=3
  with self.assertRaises(m.Pending):m.component_groups(self.draft,p,'a'*64)
 def test_synthetic_exact103_pcm_scope_and_tamper(self):
  root=self.root/'voice';draft=copy.deepcopy(self.draft);np=dump(root/'projects/shorts-leveldesign-06-02/narration-expanded-draft-v4.json',draft);plan=copy.deepcopy(self.plan);plan['sourceNarrationSHA256']=m.sha(np);plan['sourceNarrationPath']=str(np);pp=dump(root/'components.json',plan);groups,_=m.component_groups(draft,plan,m.sha(np));script,mapping=m.qa.voice.prep.make_scenes(draft,groups);identity=dict(topicId='06.02',scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']]);fp=m.digest(identity);out=root/'shared/output/architectural-111-20261106/06-02/voice-attempts'/fp[:24]
  for i,s in enumerate(script['scenes']):
   p=out/'chunks'/(s['id']+'-scene.wav');p.parent.mkdir(parents=True,exist_ok=True)
   with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,48,'NONE','not compressed'));w.writeframes(struct.pack('<h',i)*48)
  prov=dict(topicId='06.02',identity=identity,fingerprint=fp,paragraphMapping=mapping);proof=m.qa.voice.canonical_outputs(prov,out,{});m.qa.voice.immutable_json(out/'voice-complete-proof.json',proof);vp=dump(root/'voice-proof.json',proof);state=dump(root/'state.json',dict(completed=True,fingerprint=fp,child=None));dump(root/'shared/publishing/video-production-control.json',{m.qa.AUTH_KEY:dict(status='active',automaticAdvanceWithinExactList=True,automaticAdvanceOutsideList=False,humanFinalReviewRequired=True)})
  with patch.object(m,'ROOT',root),patch.object(m,'PROOF',vp),patch.object(m,'VOICE_STATE',state),patch.object(m,'COMPONENT_PLAN',pp),patch.object(m.qa.voice,'project_children',return_value=[]):
   result=m.exact_voice();self.assertEqual(len(result[1]['sceneWavs']),103);tasks=m.qa.build_tasks(result[1],result[2]);self.assertEqual(len(tasks),205);self.assertEqual(sum(t['kind']=='take'for t in tasks),103);self.assertEqual(sum(t['kind']=='boundary'for t in tasks),102)
   timing_path=Path(proof['timing']['path']);original_timing=timing_path.read_bytes();altered=json.loads(original_timing);altered['entries'][0]['start']+=1/24000;dump(timing_path,altered);clockproof=copy.deepcopy(proof);clockproof['timing']['sha256']=m.sha(timing_path);dump(out/'voice-complete-proof.json',clockproof);dump(vp,clockproof)
   with self.assertRaisesRegex(ValueError,'sample boundary'):m.exact_voice()
   timing_path.write_bytes(original_timing);dump(out/'voice-complete-proof.json',proof);dump(vp,proof)
   changed=copy.deepcopy(proof);changed['paragraphMapping'][0]['sourceCharRange'][1]-=1;dump(vp,changed)
   with self.assertRaises(ValueError):m.exact_voice()
 def test_unknown_or_previous_adapter_children_preserved(self):
  class P:
   pid=987654
   info=dict(pid=987654,cmdline=['python','run-prospect-refuge-voice-qa.py','--recognize','--job','foreign.json'])
  with patch.object(m.qa.psutil,'process_iter',return_value=[P()]),patch.object(m.qa.voice,'identity',return_value={'pid':987654,'createTime':1}):self.assertEqual(len(m.child_processes()),1)
 def test_new_default_pending_does_not_call_model(self):
  with patch.object(m,'PROOF',self.root/'missing.json'),patch.object(m.qa,'recognize',side_effect=AssertionError('no model')):
   with self.assertRaises(m.Pending):m.exact_voice()

if __name__=='__main__':unittest.main(verbosity=2)
