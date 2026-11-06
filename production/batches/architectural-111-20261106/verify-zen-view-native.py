"""07.04 disposable CPU contract fixtures; no real image decode/Unity/GPU/job."""
import copy,csv,importlib.util,json,struct,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('zen_view_native_cpu_fixture',HERE/'run-zen-view-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value)+'\n',encoding='utf8')

class MockImage:
    size=(1920,1080)
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def load(self):pass

class ZenNativeTests(unittest.TestCase):
    def test_additional_game_cmd_renderer_and_headless_jobs_block_but_hub_does_not(self):
        cases=[('sc2_x64.exe',[],True),('UnrealEditor-Cmd.exe',[],True),('chrome.exe',['--headless=new'],True),('Unity.exe',['serve'],False)]
        with patch.object(native.runtime,'busy_reason',return_value=None),patch.object(native,'idle_browser_members',return_value=set()):
            for name,args,blocked in cases:
                with self.subTest(name=name),patch.object(native.psutil,'process_iter',return_value=[SimpleNamespace(info={'name':name,'cmdline':args})]):
                    self.assertEqual(native.busy_reason() is not None,blocked)
        with patch.object(native.runtime,'busy_reason',return_value='foreign lease'),patch.object(native.psutil,'process_iter',side_effect=AssertionError('No reason to bypass prior gate')):
            self.assertEqual(native.busy_reason(),'foreign lease')
    def test_inspected_idle_browser_identity_does_not_exempt_unknown_or_game_processes(self):
        process=SimpleNamespace(pid=123,info={'name':'msedge.exe','cmdline':['--headless=new']})
        with patch.object(native.runtime,'busy_reason',return_value=None),patch.object(native.psutil,'process_iter',return_value=[process]):
            with patch.object(native,'idle_browser_members',return_value={123}):self.assertIsNone(native.busy_reason())
            with patch.object(native,'idle_browser_members',return_value={999}):self.assertIn('unverified',native.busy_reason())
            process.info={'name':'sc2_x64.exe','cmdline':[]}
            with patch.object(native,'idle_browser_members',return_value={123}):self.assertIn('game process',native.busy_reason())
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='yamyam-zen-native-cpu-');self.base=Path(self.temp.name)
        self.config=json.loads((HERE/'zen-view-unity-source/capture-config.json').read_text(encoding='utf8'));self.fp='a'*64
    def tearDown(self):self.temp.cleanup()
    def mode(self,name='narrow'):
        folder=self.base/name;folder.mkdir();width=self.config[name+'Width']
        save(folder/'mode-complete.json',dict(fingerprint=self.fp,mode=name,**{k:v for k,v in native.CONTRACT.items() if k!='modes'}))
        save(folder/'capture-config.json',dict(contract=self.config,mode=name,openingWidth=width))
        fields='frame,timeSeconds,openingWidth,eyeX,eyeY,eyeZ,centerInFrustum,centerBlocked,centerVisible,sampleVisibleCount,sampleCount'.split(',')
        with (folder/'trace.csv').open('w',newline='',encoding='utf8') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
            for i in range(480):
                visible=name=='wide' or 225<=i<=254
                writer.writerow(dict(frame=i,timeSeconds=i/60,openingWidth=width,
                    eyeX=self.config['pathStartX']+(self.config['pathEndX']-self.config['pathStartX'])*i/479,
                    eyeY=self.config['eyeHeight'],eyeZ=self.config['pathZ'],centerInFrustum=1,
                    centerBlocked=int(not visible),centerVisible=int(visible),sampleVisibleCount=int(visible),sampleCount=5))
        ray=dict(target='fixture-guide',origin=dict(x=0,y=0,z=0),desiredEndpoint=dict(x=1,y=0,z=1),
            actualEndpoint=dict(x=.5,y=0,z=.5),blocked=True,inFrustum=True,visible=False)
        (folder/'rays.jsonl').write_text(''.join(json.dumps(dict(frame=i,rays=[ray]*7))+'\n' for i in range(480)),encoding='utf8')
        anchor=dict(name='eye',world=dict(x=0,y=0,z=0),playerViewport=dict(x=.5,y=.5,z=1),observerViewport=dict(x=.5,y=.5,z=1))
        (folder/'projected-anchors.jsonl').write_text(''.join(json.dumps(dict(frame=i,anchors=[anchor]))+'\n' for i in range(480)),encoding='utf8')
        for camera in ('player','observer'):
            (folder/camera).mkdir()
            for i in range(480):(folder/camera/f'{i:04}.jpg').write_bytes(b'CPU fixture; not actual JPEG or render')
        return folder
    def validate(self,name='narrow'):
        with patch('PIL.Image.open',return_value=MockImage()):return native.check_mode(self.base,name,self.fp,self.config)
    def test_current_schema_accepts_two_clocks_five_samples_and_seven_guides(self):
        self.mode('narrow');self.mode('wide')
        narrow,wide=self.validate('narrow'),self.validate('wide')
        self.assertEqual(sum(r['centerVisible']=='1' for r in narrow),30)
        self.assertEqual(sum(r['centerVisible']=='1' for r in wide),480)
        self.assertEqual([(r['frame'],r['eyeX']) for r in narrow],[(r['frame'],r['eyeX']) for r in wide])
    def test_wrong_mode_fingerprint_is_rejected(self):
        folder=self.mode();record=native.read(folder/'mode-complete.json');record['fingerprint']='b'*64;save(folder/'mode-complete.json',record)
        with self.assertRaisesRegex(AssertionError,'receipt'):self.validate()
    def test_missing_actual_frame_cannot_be_completed(self):
        folder=self.mode();(folder/'observer/0479.jpg').unlink()
        with self.assertRaises(AssertionError):self.validate()
    def test_changed_camera_clock_or_sixth_sample_is_rejected(self):
        folder=self.mode();path=folder/'trace.csv';original=path.read_text(encoding='utf8')
        with path.open(newline='',encoding='utf8') as stream:rows=list(csv.DictReader(stream));fields=list(rows[0])
        for key,value in [('eyeX','999'),('timeSeconds','0.7'),('sampleCount','7')]:
            with self.subTest(field=key):
                changed=[dict(row) for row in rows];changed[239][key]=value
                with path.open('w',newline='',encoding='utf8') as stream:
                    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(changed)
                with self.assertRaises(AssertionError):self.validate()
        path.write_text(original,encoding='utf8')
    def test_live_prior_state_is_not_replaced_by_failed_new_worker(self):
        state=self.base/'state.json';prep=self.base/'prep.json';save(state,dict(pid=123,createTime=4,child=dict(pid=456,createTime=5),keep='exact prior evidence'));before=state.read_bytes()
        save(prep,dict(config=self.config))
        class Worker:
            previous=None
            def acquire(self):return self
            def close(self,**kwargs):pass
        with (patch.multiple(native,STATE=state,PREP=prep),patch.object(native,'authorize',return_value={}),patch.object(native,'completed_native',return_value=None),
            patch.object(native,'scan',return_value=(None,{})),patch.object(native.runtime,'SingleWorker',return_value=Worker()),
            patch.object(native.runtime,'alive',return_value=True),patch.object(native.subprocess,'Popen',side_effect=AssertionError('No actual job')),
            patch.object(sys,'argv',['run-zen-view-native.py','--execute'])):
            with self.assertRaisesRegex(RuntimeError,'Existing worker'):native.main()
        self.assertEqual(state.read_bytes(),before)
    def test_verified_completed_capture_reuses_cpu_without_any_worker_or_launch(self):
        prep=self.base/'prep.json';save(prep,dict(config=self.config))
        prior=dict(output='immutable-actual-capture',fingerprint='old-actual-native-fingerprint',actualVisualReview=False)
        with (patch.object(native,'PREP',prep),patch.object(native,'authorize',return_value={'fingerprint':'new-validator-fingerprint'}),
            patch.object(native,'completed_native',return_value=prior),patch.object(native,'scan',side_effect=AssertionError('No new attempt')),
            patch.object(native.runtime,'SingleWorker',side_effect=AssertionError('No new worker')),
            patch.object(native.subprocess,'Popen',side_effect=AssertionError('No engine launch')),
            patch.object(sys,'argv',['run-zen-view-native.py','--execute'])):
            native.main()

    def test_staged_metadata_requires_exact_source_guid_and_post_or_recorded_allowance(self):
        source=self.base/'original.meta';target=self.base/'staged.meta';guid='a'*32
        original=f'fileFormatVersion: 2\nguid: {guid}\nImporter:\n  version: 1\n'
        imported=original.replace('version: 1','version: 2')
        source.write_text(original,encoding='utf8');target.write_text(original,encoding='utf8')
        row=dict(target='Assets/ThirdParty/KayKitAdventurers/Knight.fbx.meta',sha256=native.sha(source))
        self.assertIsNone(native.staged_input(row,source,target,{}))
        target.write_text(imported,encoding='utf8')
        with self.assertRaisesRegex(AssertionError,'Unrecorded'):native.staged_input(row,source,target,{})
        known=native.staged_input(row,source,target,{},allow_imported_meta=True)
        self.assertEqual(known['guid'],guid);self.assertEqual(source.read_text(encoding='utf8'),original)
        self.assertEqual(native.staged_input(row,source,target,{row['target']:known}),known)
        target.write_text(imported.replace('version: 2','version: 3'),encoding='utf8')
        with self.assertRaisesRegex(AssertionError,'Unrecorded'):native.staged_input(row,source,target,{row['target']:known})
        target.write_text(imported.replace(guid,'b'*32),encoding='utf8')
        with self.assertRaisesRegex(AssertionError,'GUID'):native.staged_input(row,source,target,{},allow_imported_meta=True)
        code=self.base/'original.cs';staged_code=self.base/'staged.cs';code.write_text('original');staged_code.write_text('changed')
        with self.assertRaisesRegex(AssertionError,'Staged native input'):native.staged_input(dict(row,sha256=native.sha(code)),code,staged_code,{},allow_imported_meta=True)
        source.write_text(original+'changed source\n',encoding='utf8')
        with self.assertRaisesRegex(AssertionError,'Original source'):native.staged_input(row,source,target,{},allow_imported_meta=True)

    def test_export_paths_accept_only_exact_owned_subtree_or_its_root_meta(self):
        project=(self.base/'capture').resolve();main=(self.base/'main').resolve();project.mkdir();main.mkdir()
        with patch.object(native,'UNITY_ROOT',main):
            source,target=native.export_paths(native.FOLDER+'/S02-ZenView-Narrow.unity',project)
            self.assertEqual(source,project/native.FOLDER/'S02-ZenView-Narrow.unity')
            self.assertEqual(target,main/native.FOLDER/'S02-ZenView-Narrow.unity')
            self.assertEqual(native.export_paths(native.FOLDER+'.meta',project),(project/(native.FOLDER+'.meta'),main/(native.FOLDER+'.meta')))
            bad=[native.FOLDER+'/../03-02/trap.unity',str(self.base/'outside.unity'),
                'Assets/VideoScenes/architectural-111-20261106/03-02/trap.unity',native.FOLDER+'/./scene.unity',native.FOLDER+'//scene.unity']
            for path in bad:
                with self.subTest(path=path):
                    with self.assertRaises(AssertionError):native.export_paths(path,project)

    def test_real_unity_float32_json_preserves_config_but_rejects_changed_bits_or_schema(self):
        # Literal values from the actual JsonUtility snapshot; remaining float
        # fields use the sameIEEEfloat32 representation, not a tolerance.
        actual={k:struct.unpack('<f',struct.pack('<f',v))[0] if type(v) is float else v for k,v in self.config.items()}
        actual.update(eyeHeight=1.649999976158142,wallHeight=4.400000095367432,
            openingBottom=0.6499999761581421,openingTop=3.299999952316284,narrowWidth=0.4000000059604645,wideWidth=6.800000190734863)
        native.validate_capture_config(actual,self.config)
        self.assertEqual(native.float32_bits(actual['narrowWidth']),native.float32_bits(.4))
        for key,value in [('eyeHeight',1.650001),('eyeHeight',float('nan')),('eyeHeight',float('inf')),('eyeHeight',True),('frames',480.0),('fps',True)]:
            with self.subTest(key=key,value=value):
                changed=dict(actual);changed[key]=value
                with self.assertRaises(AssertionError):native.validate_capture_config(changed,self.config)
        changed=dict(actual);changed['extra']=0
        with self.assertRaises(AssertionError):native.validate_capture_config(changed,self.config)
        changed=dict(actual);changed.pop('frontZ')
        with self.assertRaises(AssertionError):native.validate_capture_config(changed,self.config)
        folder=self.mode();snapshot=native.read(folder/'capture-config.json');snapshot.update(contract=actual,openingWidth=0.4000000059604645);save(folder/'capture-config.json',snapshot)
        self.assertEqual(len(self.validate()),480)

    def test_canonical_unity_version_ignores_added_revision_format_only_in_identity(self):
        path=self.base/'ProjectVersion.txt';expected='6000.6.0f1'
        path.write_text('m_EditorVersion: '+expected+'\n',encoding='utf8');before=native.project_version(path,expected)
        path.write_text('m_EditorVersion: '+expected+'\nm_EditorVersionWithRevision: '+expected+' (f7f8ed4d1e24)\n',encoding='utf8');after=native.project_version(path,expected)
        self.assertEqual(before['editorVersion'],after['editorVersion'])
        self.assertNotEqual(before['sourceAudit']['sha256'],after['sourceAudit']['sha256'])
        self.assertEqual(after['sourceAudit']['withRevision'],'f7f8ed4d1e24')
        self.assertEqual(native.digest(dict(editorVersion=before['editorVersion'])),native.digest(dict(editorVersion=after['editorVersion'])))
        for text in ['m_EditorVersion: 6000.6.0f2\n','m_EditorVersion: '+expected+'\nm_EditorVersionWithRevision: 6000.6.0f2 (f7f8ed4d1e24)\n',
            'm_EditorVersion: '+expected+'\nm_EditorVersionWithRevision: '+expected+' (short)\n','m_EditorVersion: '+expected+'\nm_EditorVersion: '+expected+'\n']:
            path.write_text(text,encoding='utf8')
            with self.assertRaises(AssertionError):native.project_version(path,expected)

if __name__=='__main__':unittest.main(verbosity=2)
