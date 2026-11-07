"""Bounded CPU validation of11.05 V2 animation diagnostics, never pixel/gait approval.

validate(folder, request_fp, mode) reads only an existing completed mode folder.
--self-test uses synthetic temporary JSON fixtures; no Unity/model/media imports.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,re,struct,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
FRAMES=[0,480,481,495,510,525,540,555,570,585,600,612,900,928,1199]
ACTORS=['player','enemy'];STAGES=['pre-sample','post-sample','post-root-restore','post-render-player','post-render-observer']
MODES=['construction','branches-a','branches-b','templates-a','templates-b','threats-a','threats-b','broken-link']
ASSET='Assets/ThirdParty/KayKitAdventurers/Knight.fbx';GUID='274e91da352f3104c8313348b836daf7'
CLIPS={'Idle':-3100369314251171874,'Walking_A':110800004}
BONES=[('model-root',''),('rig-root','Rig/root'),('hips','Rig/root/hips'),('upperleg-left','Rig/root/hips/upperleg.l'),('lowerleg-left','Rig/root/hips/upperleg.l/lowerleg.l'),('foot-left','Rig/root/hips/upperleg.l/lowerleg.l/foot.l'),('upperleg-right','Rig/root/hips/upperleg.r'),('lowerleg-right','Rig/root/hips/upperleg.r/lowerleg.r'),('foot-right','Rig/root/hips/upperleg.r/lowerleg.r/foot.r')]
SKINS=sorted(['Knight_ArmRight','Knight_LegLeft','Knight_ArmLeft','Knight_LegRight','Knight_Body','Knight_Head'])
SPACE='renderer-local; BakeMesh(useScale:false); little-endian float32 XYZ'
TOL=2e-5
class Invalid(ValueError):pass
def need(ok,message):
 if not ok:raise Invalid(message)
def sha(p):
 with Path(p).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def read(p,limit=4*1024*1024):
 p=Path(p);need(p.is_file()and p.stat().st_size<=limit,'Missing/oversized diagnostic input')
 return json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda x:(_ for _ in()).throw(Invalid('Nonfinite JSON constant')))
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def finite(value):
 if isinstance(value,dict):return all(finite(x)for x in value.values())
 if isinstance(value,list):return all(finite(x)for x in value)
 return type(value)not in(int,float)or math.isfinite(value)
def vector(d,keys='xyz'):
 need(isinstance(d,dict)and set(d)==set(keys)and all(type(d[k])in(int,float)and math.isfinite(d[k])for k in keys),'Finite vector/quaternion required');return[d[k]for k in keys]
def near(a,b,tol=TOL):return len(a)==len(b)and all(abs(x-y)<=tol for x,y in zip(a,b))
def quat(d):
 q=vector(d,'xyzw');need(abs(sum(x*x for x in q)-1)<=.001,'Nonunit diagnostic quaternion');return q
def qclose(a,b):return min(math.dist(a,b),math.dist(a,[-x for x in b]))<=TOL
def qmul(a,b):
 x,y,z,w=a;u,v,t,s=b;return[w*u+x*s+y*t-z*v,w*v-x*t+y*s+z*u,w*t+x*v-y*u+z*s,w*s-x*u-y*v-z*t]
def rotate(q,v):return qmul(qmul(q,[*v,0]),[-q[0],-q[1],-q[2],q[3]])[:3]
def bone_equal(a,b,local_only=False):
 names=['localPosition','localScale']+([]if local_only else['worldPosition','worldScale'])
 return all(near(vector(a[k]),vector(b[k]))for k in names)and qclose(quat(a['localRotation']),quat(b['localRotation']))and(local_only or qclose(quat(a['worldRotation']),quat(b['worldRotation'])))
def world_after_root(before,after,root_before,root_after):
 # A model-root restoration may move descendants in world space, never their local pose.
 qa=quat(root_before['worldRotation']);qb=quat(root_after['worldRotation']);sa=vector(root_before['worldScale']);sb=vector(root_after['worldScale'])
 local=rotate([-qa[0],-qa[1],-qa[2],qa[3]],[x-y for x,y in zip(vector(before['worldPosition']),vector(root_before['worldPosition']))]);local=[x/y for x,y in zip(local,sa)]
 expected=[x+y for x,y in zip(vector(root_after['worldPosition']),rotate(qb,[x*y for x,y in zip(local,sb)]))]
 expected_q=qmul(qmul(qb,[-qa[0],-qa[1],-qa[2],qa[3]]),quat(before['worldRotation']))
 return near(expected,vector(after['worldPosition']),1e-4)and qclose(expected_q,quat(after['worldRotation']))and near([x*y/z for x,y,z in zip(vector(before['worldScale']),sb,sa)],vector(after['worldScale']),1e-4)
def validate(folder,request_fp,mode):
 folder=Path(folder).resolve();need(re.fullmatch('[0-9a-f]{64}',request_fp or'')and mode in MODES,'Exact request fingerprint/mode required')
 cfg=read(folder/'config.json');need(cfg.get('animationDiagnosticFrames')==FRAMES and(cfg.get('frames'),cfg.get('fps'))==(1200,60),'Exact15-frame/1200-at60 diagnostic contract required')
 specs=[r for r in cfg.get('modes',[])if r.get('id')==mode];need(len(specs)==1,'Actual selected mode config required');spec=specs[0]
 done=read(folder/'mode-complete.json');need(done.get('fingerprint')==request_fp and done.get('mode')==mode,'Completed mode identity differs')
 summary=read(folder/'animation-diagnostics-summary.json');path=folder/'animation-diagnostics.jsonl'
 need(summary.get('schemaVersion')=='11-05-animation-diagnostics-summary-v2'and summary.get('fingerprint')==request_fp and summary.get('mode')==mode,'Diagnostic summary identity differs')
 need(summary.get('file')==path.name and summary.get('sha256')==sha(path)and summary.get('records')==150 and summary.get('selectedFrames')==FRAMES and summary.get('actors')==ACTORS and summary.get('stages')==STAGES and summary.get('actualVisualMotionApproved')is False,'Diagnostic summary/hash/coverage or false visual-approval flag differs')
 need(path.stat().st_size<=32*1024*1024,'Oversized diagnostic stream')
 lines=path.read_text(encoding='utf-8-sig').splitlines();need(len(lines)==150 and all(lines),'Exactly150 nonempty diagnostic records required')
 rows=[json.loads(x,parse_constant=lambda x:(_ for _ in()).throw(Invalid('Nonfinite JSON constant')))for x in lines]
 state_lines=(folder/'states.jsonl').read_text(encoding='utf-8-sig').splitlines();need(len(state_lines)==1200,'Actual1200-frame state clock required')
 states={i:json.loads(state_lines[i])for i in FRAMES};need(all(v.get('frame')==i and v.get('mode')==mode and finite(v)for i,v in states.items()),'Diagnostic frame/state clock differs')
 scene=read(folder/'mode-scene-record.json');need(scene.get('fingerprint')==request_fp and scene.get('mode')==mode and scene.get('animationClips')==['Idle','Walking_A'],'Actual saved clip names/identity differ')
 indexed={};clips={};renderer_shapes={};record_order=[]
 for row in rows:
  need(isinstance(row,dict)and finite(row)and row.get('schemaVersion')=='11-05-animation-diagnostic-v2'and row.get('fingerprint')==request_fp and row.get('mode')==mode and row.get('cpuBakeMeshDiagnostic')is True and row.get('actualVisualMotionApproved')is False,'Malformed/mismatched/claimed-approved diagnostic')
  frame,actor,stage=row.get('frame'),row.get('actor'),row.get('stage');key=(frame,actor,stage)
  need(type(frame)is int and frame in FRAMES and actor in ACTORS and stage in STAGES and key not in indexed,'Unexpected/duplicate diagnostic identity');indexed[key]=row;record_order.append(key)
  moving=sum(x*x for x in vector(states[frame]['actualDelta']))>1e-7;clip='Walking_A'if actor=='player'and moving else'Idle'
  need(row.get('clipName')==clip and row.get('clipAssetPath')==ASSET and row.get('clipGUID')==GUID and type(row.get('clipLocalID'))is int and row['clipLocalID']==CLIPS[clip],'Actual selected clip asset/GUID/localID differs')
  length=row.get('clipLength');time=row.get('clipSampleTime');need(type(length)in(int,float)and math.isfinite(length)and 0<length<10000 and type(time)in(int,float)and math.isfinite(time),'Finite positive clip length/sample time required')
  expected=f32(math.fmod(f32(frame/60),f32(length)));need(0<=time<length and abs(time-expected)<=2e-6,'Clip sample time is not actual frame60 modulo length')
  value=(row['clipLocalID'],length);need(clip not in clips or clips[clip]==value,'Clip identity/length changed across records');clips[clip]=value
  bones=row.get('bones');need(isinstance(bones,list)and[(r.get('role'),r.get('path'))for r in bones]==BONES,'Exact9 actual bone paths required')
  for bone in bones:
   need(bone.get('name')==(bone['path'].split('/')[-1]if bone['path']else'CC0 articulated Knight'if actor=='player'else'CC0 articulated enemy Knight'),'Bone name/path differs')
   for k in('localPosition','worldPosition'):vector(bone[k])
   for k in('localScale','worldScale'):need(all(x>0 for x in vector(bone[k])),'Positive bone scales required')
   quat(bone['localRotation']);quat(bone['worldRotation'])
  skins=row.get('renderers');need(isinstance(skins,list)and[r.get('path')for r in skins]==SKINS,'Exact6 sorted actual SMRs required')
  active=actor=='player'or(spec.get('content')is True and(not spec.get('construction')or frame>=450))
  for skin in skins:
   need(skin.get('rootBonePath')=='Rig/root'and skin.get('meshName')==skin['path']and skin.get('enabled')is True and skin.get('activeInHierarchy')is active and skin.get('forceMatrixRecalculationPerRender')is True and skin.get('updateWhenOffscreen')is True,'SMR identity/actual flags differ')
   need(skin.get('boneCount')==41 and type(skin.get('vertexCount'))is int and skin['vertexCount']>0 and re.fullmatch('[0-9a-f]{64}',skin.get('bakedVertexSHA256',''))and skin.get('vertexCoordinateSpace')==SPACE,'Actual SMR mesh/hash/coordinate contract differs')
   matrix=skin.get('localToWorld');need(isinstance(matrix,list)and len(matrix)==16 and all(type(x)in(int,float)and math.isfinite(x)for x in matrix)and near(matrix[12:],[0,0,0,1]),'Finite affine skin matrix required')
   shape=(skin['meshName'],skin['boneCount'],skin['vertexCount']);sk=(actor,skin['path']);need(sk not in renderer_shapes or renderer_shapes[sk]==shape,'Mesh identity/vertex count changed');renderer_shapes[sk]=shape
 expected_order=[]
 for f in FRAMES:
  expected_order.extend((f,a,s)for a in ACTORS for s in STAGES[:3]);expected_order.extend((f,a,s)for s in STAGES[3:]for a in ACTORS)
 need(record_order==expected_order,'Diagnostic callback/render stage order differs')
 for f in FRAMES:
  for actor in ACTORS:
   pre,post,rest,render1,render2=[indexed[(f,actor,s)]for s in STAGES]
   need(bone_equal(pre['bones'][0],rest['bones'][0]),'Model root was not restored to its declared pre-sample pose')
   for x,y in zip(post['bones'][1:],rest['bones'][1:]):need(bone_equal(x,y,local_only=True)and world_after_root(x,y,post['bones'][0],rest['bones'][0]),'Root restoration changed a descendant pose beyond its actual root transform')
   need([r['bakedVertexSHA256']for r in post['renderers']]==[r['bakedVertexSHA256']for r in rest['renderers']],'Renderer-local baked vertices changed during root restoration')
   for rendered in(render1,render2):
    need(all(bone_equal(x,y)for x,y in zip(rest['bones'],rendered['bones'])),'Camera.Render changed sampled bone transforms')
    need(rest['renderers']==rendered['renderers'],'Camera.Render changed actual renderer flags/matrix/local vertex evidence')
 variation={'required':mode=='construction','eligibleWalkingFrames':[],'varyingLegBonePaths':[],'varyingLegMeshPaths':[],'actualJpegGaitApproved':False,'naturalPaceApproved':False}
 if mode=='construction':
  eligible=[f for f in FRAMES if indexed[(f,'player','post-root-restore')]['clipName']=='Walking_A'and not(states[f].get('collisionFlags',0)&1)and sum(x*x for x in vector(states[f]['actualDelta'])[:1]+vector(states[f]['actualDelta'])[2:])>1e-6]
  need(len(eligible)>=3,'Construction requires at least3 unblocked actual walking samples for a useful diagnostic')
  sampled=[indexed[(f,'player','post-root-restore')]for f in eligible];variation['eligibleWalkingFrames']=eligible
  for i in range(3,9):
   if any(not qclose(quat(sampled[0]['bones'][i]['localRotation']),quat(r['bones'][i]['localRotation']))for r in sampled[1:]):variation['varyingLegBonePaths'].append(BONES[i][1])
  for path in['Knight_LegLeft','Knight_LegRight']:
   if len({next(s['bakedVertexSHA256']for s in r['renderers']if s['path']==path)for r in sampled})>1:variation['varyingLegMeshPaths'].append(path)
  need(any(x.endswith('.l')for x in variation['varyingLegBonePaths'])and any(x.endswith('.r')for x in variation['varyingLegBonePaths'])and len(variation['varyingLegMeshPaths'])==2,'Construction walking leg quaternions and both renderer-local leg meshes must actually vary')
 return dict(schemaVersion='11-05-animation-diagnostics-validation-v2',fingerprint=request_fp,mode=mode,records=150,selectedFrames=FRAMES,diagnosticsSHA256=sha(folder/'animation-diagnostics.jsonl'),summarySHA256=sha(folder/'animation-diagnostics-summary.json'),stageConsistencyPassed=True,variation=variation,actualVisualMotionApproved=False,humanApproval=False)

def fixture(folder):
 """Synthetic serialization fixture, deliberately no real asset/capture approval."""
 fp='a'*64;mode='construction';v=lambda a:dict(zip('xyz',a));q=lambda x=0:dict(x=math.sin(x/2),y=0,z=0,w=math.cos(x/2))
 cfg=dict(frames=1200,fps=60,animationDiagnosticFrames=FRAMES,modes=[dict(id=mode,construction=True,content=True)])
 states=[dict(frame=f,mode=mode,actualDelta=v([.1,0,0]if 480<f<930 else[0,0,0]),collisionFlags=4)for f in range(1200)];rows=[]
 for f in FRAMES:
  pair={}
  for actor in ACTORS:
   clip='Walking_A'if actor=='player'and 480<f<930 else'Idle';angle=(f%64)/64 if clip=='Walking_A'else 0
   bones=[]
   for i,(role,path)in enumerate(BONES):bones.append(dict(role=role,path=path,name=path.split('/')[-1]if path else'CC0 articulated Knight'if actor=='player'else'CC0 articulated enemy Knight',localPosition=v([0,0,0]),localScale=v([1,1,1]),worldPosition=v([0,0,0]),worldScale=v([1,1,1]),localRotation=q(angle if i in(4,7)else 0),worldRotation=q(angle if i in(4,7)else 0)))
   skins=[dict(path=s,rootBonePath='Rig/root',meshName=s,enabled=True,activeInHierarchy=actor=='player'or f>=450,forceMatrixRecalculationPerRender=True,updateWhenOffscreen=True,boneCount=41,vertexCount=8,bakedVertexSHA256=hashlib.sha256((s+str(angle if s in('Knight_LegLeft','Knight_LegRight')else 0)).encode()).hexdigest(),vertexCoordinateSpace=SPACE,localToWorld=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])for s in SKINS]
   pair[actor]=dict(schemaVersion='11-05-animation-diagnostic-v2',fingerprint=fp,mode=mode,actor=actor,frame=f,clipName=clip,clipAssetPath=ASSET,clipGUID=GUID,clipLocalID=CLIPS[clip],clipLength=f32(1.0666666667),clipSampleTime=f32(math.fmod(f32(f/60),f32(1.0666666667))),cpuBakeMeshDiagnostic=True,actualVisualMotionApproved=False,bones=bones,renderers=skins)
  order=[(a,s)for a in ACTORS for s in STAGES[:3]]+[(a,s)for s in STAGES[3:]for a in ACTORS]
  rows.extend(dict(copy.deepcopy(pair[a]),stage=s)for a,s in order)
 def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False)+'\n',encoding='utf-8')
 save(folder/'config.json',cfg);save(folder/'mode-complete.json',dict(fingerprint=fp,mode=mode));save(folder/'mode-scene-record.json',dict(fingerprint=fp,mode=mode,animationClips=['Idle','Walking_A']))
 (folder/'states.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in states),encoding='utf-8')
 def write_rows(values):
  (folder/'animation-diagnostics.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in values),encoding='utf-8');save(folder/'animation-diagnostics-summary.json',dict(schemaVersion='11-05-animation-diagnostics-summary-v2',fingerprint=fp,mode=mode,file='animation-diagnostics.jsonl',sha256=sha(folder/'animation-diagnostics.jsonl'),records=150,selectedFrames=FRAMES,actors=ACTORS,stages=STAGES,actualVisualMotionApproved=False))
 write_rows(rows);return fp,mode,rows,write_rows
class Tests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name);self.fp,self.mode,self.rows,self.write=fixture(self.folder)
 def test_complete_synthetic_contract(self):
  self.assertFalse(validate(self.folder,self.fp,self.mode)['actualVisualMotionApproved'])
  # A clip may animate the model root; its restoration must preserve local bones.
  row=self.rows[1];row['bones'][0]['localPosition']['x']=1
  for bone in row['bones']:bone['worldPosition']['x']=1
  for skin in row['renderers']:skin['localToWorld'][3]=1
  self.write(self.rows);self.assertTrue(validate(self.folder,self.fp,self.mode)['stageConsistencyPassed'])
 def test_missing_stage(self):self.write(self.rows[:-1]);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
 def test_changed_stream_hash(self):
  p=self.folder/'animation-diagnostics.jsonl';p.write_bytes(p.read_bytes()+b' ');self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
 def test_nan_rejected(self):self.rows[0]['bones'][0]['worldPosition']['x']=float('nan');self.write(self.rows);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
 def test_clip_identity_and_phase_rejection(self):
  original=copy.deepcopy(self.rows)
  for key,value in [('clipLocalID',7),('clipGUID','0'*32),('clipSampleTime',.1)]:
   rows=copy.deepcopy(original);rows[0][key]=value;self.write(rows);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
  self.write(original);self.assertRaises(Invalid,validate,self.folder,'b'*64,self.mode)
 def test_renderer_flag_rejection(self):self.rows[0]['renderers'][0]['updateWhenOffscreen']=False;self.write(self.rows);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
 def test_post_render_mutation_rejection(self):
  original=copy.deepcopy(self.rows)
  self.rows[6]['bones'][4]['localRotation']={'x':.1,'y':0,'z':0,'w':math.sqrt(.99)};self.write(self.rows);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
  original[6]['renderers'][0]['bakedVertexSHA256']='c'*64;self.write(original);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
 def test_static_walk_rejected(self):
  for r in self.rows:
   if r['actor']=='player':
    for bone in r['bones']:bone['localRotation']=bone['worldRotation']=dict(x=0,y=0,z=0,w=1)
    for skin in r['renderers']:skin['bakedVertexSHA256']='d'*64
  self.write(self.rows);self.assertRaises(Invalid,validate,self.folder,self.fp,self.mode)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--folder');p.add_argument('--request-fp');p.add_argument('--mode');a=p.parse_args()
 if a.self_test:unittest.main(argv=[sys.argv[0]],verbosity=2);return
 if not a.folder:print(json.dumps(dict(ready=False,reason='Actual completed V2 mode folder/fingerprint required',actualVisualMotionApproved=False)));return
 print(json.dumps(validate(a.folder,a.request_fp,a.mode),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
