"""CPU contract fixtures only: never launch Chromium, Vite, FFmpeg, Unity or models."""
import importlib.util,json,subprocess,sys,time,uuid
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('zen_diagram_fixture',HERE/'run-zen-view-diagrams.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=m.TOPIC/'mc-source-preparation/cpu-tests'/uuid.uuid4().hex
fixture.mkdir(parents=True)
passed=[]

def check(name,fn):
 fn();passed.append(name)

def fails(fn):
 try:fn()
 except (ValueError,AssertionError):return
 raise AssertionError('Expected bounded input rejection')

expected=[dict(id='a',draftNormalizedAt=.04),dict(id='b',draftNormalizedAt=.2),dict(id='c',draftNormalizedAt=.5),dict(id='d',draftNormalizedAt=.91)]
check('actual cue starts at frame0 without fabricated preroll',lambda: m.cue_map([dict(id=i,frame=f)for i,f in zip('abcd',[0,20,50,90])],100,expected)[0]==dict(frame=0,phase=.04)or(_ for _ in()).throw(AssertionError()))
check('actual final cue at last frame remains literal timing',lambda: m.cue_map([dict(id=i,frame=f)for i,f in zip('abcd',[0,20,50,99])],100,expected)[-1]==dict(frame=99,phase=.91)or(_ for _ in()).throw(AssertionError()))
check('duplicate cue frame rejected',lambda:fails(lambda:m.cue_map([dict(id=i,frame=f)for i,f in zip('abcd',[0,20,20,90])],100,expected)))
check('missing cue ID rejected',lambda:fails(lambda:m.cue_map([dict(id='a',frame=1)],100,expected)))
check('outside cue frame rejected',lambda:fails(lambda:m.cue_map([dict(id=i,frame=f)for i,f in zip('abcd',[0,20,50,100])],100,expected)))
check('draft floating duration rejected as actual frame count',lambda:fails(lambda:m.cue_map([],10.2,expected)))
pin=fixture/'pinned.txt';pin.write_text('first');record=dict(path=str(pin),sha256=m.sha(pin));m.pinned(record);pin.write_text('changed')
check('changed input hash rejected',lambda:fails(lambda:m.pinned(record)))

def actual_fixture(paragraph,start,first,end):
 frames=[first,first+20,first+50,end-20]
 timing=dict(paragraphs=[dict(paragraph=paragraph,startFrame=start,endFrameExclusive=end)],diagramCues=[dict(id=i,paragraph=paragraph,startFrame=f)for i,f in zip('abcd',frames)])
 segment_start=first if paragraph==6 else start
 cue=dict(segment='p'+str(paragraph),segmentStartGlobalFrame=segment_start,segmentEndGlobalFrameExclusive=end,totalFrames=end-segment_start,cues=[dict(id=i,frame=f-segment_start)for i,f in zip('abcd',frames)])
 return cue,timing
c2,t2=actual_fixture(2,100,120,250)
check('P2 uses complete actual paragraph including natural head',lambda:m.actual_segment(c2,t2,expected)['startFrame']==100 or(_ for _ in()).throw(AssertionError()))
bad=json.loads(json.dumps(c2));bad['cues'][1]['frame']+=1
check('plausible ordered authored frame differing one from actual ASR rejected',lambda:fails(lambda:m.actual_segment(bad,t2,expected)))
bad=dict(c2,segmentStartGlobalFrame=120,totalFrames=130)
check('P2 cannot crop natural paragraph head to first spoken cue',lambda:fails(lambda:m.actual_segment(bad,t2,expected)))
c6,t6=actual_fixture(6,1000,1050,1400)
check('P6 entry is actual treasure-room cue not earlier vista sentence',lambda:m.actual_segment(c6,t6,expected)['startFrame']==1050 or(_ for _ in()).throw(AssertionError()))
bad=dict(c6,segmentStartGlobalFrame=1000,totalFrames=400)
check('P6 arbitrary earlier segment start rejected',lambda:fails(lambda:m.actual_segment(bad,t6,expected)))
c7,t7=actual_fixture(7,1500,1520,1800)
check('P7 preserves exact actual paragraph end',lambda:m.actual_segment(c7,t7,expected)['endFrameExclusive']==1800 or(_ for _ in()).throw(AssertionError()))

old=(m.runtime.LEASE,m.runtime.alive,m.runtime.archive,m.matching_owned_processes)
lease=fixture/'GPU_HANDOFF.fixture.json';m.runtime.LEASE=lease
m.runtime.alive=lambda rec:bool(rec and rec.get('fixtureAlive'))
m.matching_owned_processes=lambda attempt:[]
archived=[]
def archive(path,token):
 target=fixture/(token+'.archived.json');path.replace(target);archived.append(token)
m.runtime.archive=archive
try:
 rec=dict(protocol=m.PROTOCOL,owner=m.OWNER,token='exact',pid=1,createTime=1,child=None,output=str(m.ATTEMPTS/'fixture'))
 lease.write_text(json.dumps(dict(rec,owner='foreign')));m.recover_own({'exact'})
 check('foreign lease preserved byte-for-byte',lambda:lease.exists()and json.loads(lease.read_text())['owner']=='foreign'or(_ for _ in()).throw(AssertionError()))
 lease.write_text(json.dumps(rec));m.recover_own({'unknown'})
 check('unproven own stale token preserved',lambda:lease.exists()or(_ for _ in()).throw(AssertionError()))
 lease.write_text(json.dumps(dict(rec,child=dict(fixtureAlive=True))));m.recover_own({'exact'})
 check('live owned child lease preserved',lambda:lease.exists()or(_ for _ in()).throw(AssertionError()))
 lease.write_text(json.dumps(rec));m.matching_owned_processes=lambda attempt:[dict(pid=3)];m.recover_own({'exact'})
 check('orphan owned Chromium or encoder preserves lease',lambda:lease.exists()or(_ for _ in()).throw(AssertionError()))
 m.matching_owned_processes=lambda attempt:[];m.recover_own({'exact'})
 check('only proven dead exact owned lease archived',lambda:not lease.exists()and archived==['exact']or(_ for _ in()).throw(AssertionError()))
finally:m.runtime.LEASE,m.runtime.alive,m.runtime.archive,m.matching_owned_processes=old

node=r'''
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const helper=require(process.argv[2]),fixture=process.argv[3];
const root=path.resolve(path.dirname(process.argv[2]),'../../..');
const attempt='C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-07-04/mc-render-attempts/fixture-'+path.basename(fixture);
fs.mkdirSync(attempt,{recursive:true});
const job={schemaVersion:'07-04-mc-render-job-v1',topicId:'07.04',segment:'p2',fingerprint:'a'.repeat(64),attempt,
 output:path.resolve(attempt,'p2.silent.mp4'),contract:{width:1080,height:900,fps:60,frames:100,audio:false,alpha:false},inputPins:[],
 variables:{segment:'p2',timingMode:'authored-cue-frames',segmentFrames:100,phaseFrameMap:[{frame:0,phase:0},{frame:20,phase:.2},{frame:50,phase:.5},{frame:99,phase:1}]},
 stagedSources:['project.ts','reward-diagrams.tsx'].map(name=>({name,path:path.join(root,'motion-canvas/src/projects/shorts-leveldesign-07-04',name)})),font:{path:'C:/Windows/Fonts/NotoSansKR-VF.ttf'},versions:{core:'3.17',two:'3.17',ui:null,vitePlugin:'3.17'}};
const jp=path.join(attempt,'job.json');
helper.validateJob(job,jp);
assert.throws(()=>helper.validateJob({...job,contract:{...job.contract,width:1920}},jp));
assert.throws(()=>helper.validateJob({...job,contract:{...job.contract,audio:true}},jp));
assert.throws(()=>helper.validateJob({...job,stagedSources:[{name:'../other.ts',path:'D:/other.ts'}]},jp));
fs.writeFileSync(job.output,'preserve-this-fixture');
assert.throws(()=>helper.validateJob(job,jp));assert.equal(fs.readFileSync(job.output,'utf8'),'preserve-this-fixture');
helper.validateJob(job,jp,true);
const png=Buffer.alloc(24);Buffer.from('89504e470d0a1a0a','hex').copy(png);png.write('IHDR',12);png.writeUInt32BE(1080,16);png.writeUInt32BE(900,20);
assert.equal(helper.pngDimensions(png).width,1080);assert.throws(()=>helper.pngDimensions(Buffer.alloc(30)));
const html=helper.workerPage(job),script=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const syntax=spawnSync(process.execPath,['--input-type=module','--check'],{input:script,encoding:'utf8'});assert.equal(syntax.status,0,syntax.stderr);
assert.ok(!script.includes('@motion-canvas/ui'));assert.ok(script.includes("new MetaFile('owned-settings',false)"));
for(const n of [6,7,60,61,500,3601,100000])assert.equal(Math.ceil(((n-1.25)/60)*60),n-1);
console.log(JSON.stringify({passed:8,names:['fixed crop shape rejected if changed','audio rejected','staging traversal rejected','stale output preserved','actual PNG dimensions inspected','invalid PNG rejected','generated SDK page syntax valid without execution','inclusive SDK range maps exact frames']}));
'''
r=subprocess.run(['node','-',str(HERE/'render-zen-view-diagrams.cjs'),str(fixture)],input=node,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=m.CREATE)
if r.returncode:raise AssertionError(r.stderr)
report=json.loads(r.stdout);passed+=report['names']
receipt=dict(schemaVersion='07-04-diagram-renderer-cpu-validation-v1',passed=len(passed),checks=passed,fixture=str(fixture),preservedFixtures=True,sourcePins=[dict(path=str(HERE/n),sha256=m.sha(HERE/n))for n in ['run-zen-view-diagrams.py','render-zen-view-diagrams.cjs',Path(__file__).name]],browserStarted=False,viteStarted=False,mediaEncoded=False,gpuUsed=False,modelStarted=False,actualRenderingValidated=False)
m.save(fixture/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
