"""Finalize only the PC atmosphere revision; retain v1/v2 deliveries and sources."""
from pathlib import Path
import datetime,hashlib,json,shutil

root=Path(__file__).resolve().parents[3];project=root/'projects/ai-3d-lofi-gaming-room'
local=project/'production/local/atmosphere-v3'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
d=read(local/'delivery.json');native=read(local/'native-build.json');metrics=read(local/'runtime-metrics.json')
assert native['result']=='Succeeded' and native['errors']==0 and d['videoFrames']==2880
assert metrics['shaderErrors']==0 and metrics['renderScale']==1 and metrics['leafRenderers']==311
assert metrics['hairCollisionCorrections']>0 and metrics['hairLengthError']<.001
assert sha(Path(d['outputs'][1]['path']))==d['outputs'][1]['sha256']
package=local/'windows'
files=[{'path':p.relative_to(package).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(package.rglob('*')) if p.is_file()]
previous=read(project/'production/nature-v2-delivery.json')
for t in previous['textureInputs']:assert sha(root/t['path'])==t['sha256']
save(project/'production/atmosphere-v3-delivery.json',{
 **d,'reviewUrl':'http://127.0.0.1:9321/','updatedAtKst':now,
 'scene':'unity/LofiGamingRoomWeb/Assets/LofiRoom/Scenes/LofiAtmosphereRoom.unity',
 'nativeBuild':native,'nativeExecutable':str(package/'YamyamLofiRoom.exe'),'nativePackageFiles':files,
 'runtimeMetrics':metrics,'textureInputs':previous['textureInputs'],
 'visualReview':{'status':'native-player-and-encoded-samples-reviewed','nativeWalkingActuallyObserved':True,
  'nativeDayNightButtonUsed':True,'nativeProof':'production/local/atmosphere-v3/native-pc-final.png',
  'reviewedSeconds':[2,10,18,24,28,33,39,46],'fullDecodePassed':True,'humanApproval':False},
 'features':{
  'bodyMotion':'Original Tripo Idle/Walk clips retained. Fixed-time 0.38s blending, Humanoid foot IK enabled, continuous curved route and root-motion distance. Walking playback 0.58-0.82x according to heading error; no hand-authored limb poses.',
  'hair':'Five-node constrained secondary-motion chain at 120Hz, inertia, restoring force, length/angle limits and head/upper-shoulder ellipsoid collisions. Four independently weighted shader offsets, fixed scalp mask, 0.085m deformation cap. Maximum observed chain offset includes starts/turns; it is not uniform hair travel.',
  'foliage':'311 curved 3D leaves, pinned roots, size-scaled bending, different spatial phases, slow gusts and slight tip flutter. Self-authored; no extracted Animal Crossing assets.',
  'windowLight':'56-step depth-clipped bounded light-scattering shader, four-pane cookie with a shadowed real-time spot light, sparse slow dust and restrained Bloom. Artistic light shaft rendering, not a global-illumination/path-tracing claim.',
  'materials':'Existing genuine 4K BaseColor and original-resolution PBR maps retained. Native 1.0 render scale replaces 0.8. Dedicated PC URP renderer, MSAA4, SMAA, AfterOpaque SSAO and room reflection probe. No texture upscaling or new Tripo generation.',
  'controls':'On-screen breeze/shafts/hair toggles. Keys 1 walk, 2 rest, 3 day/night, 4 rain, 5 music, 6 desk, 7 room, 8 breeze, 9 shafts, 0 hair.'},
 'implementationReferences':[
  'https://docs.unity.com/en-us/engine/6000.6/script-reference/unityeditor/animations/animatorstate/ikonfeet',
  'https://docs.unity.cn/Packages/com.unity.render-pipelines.universal%4017.0/api/UnityEngine.Rendering.Universal.ScreenSpaceAmbientOcclusion.html',
  'Installed URP 17.6.0 RendererFeatures/ScreenSpaceAmbientOcclusion.cs'],
 'newPaidGenerationJobs':0,'webModuleInstalled':False,
 'pending':['User review of PC v3','Native sitting/reading, notes and timer','Remaining tool demonstrations and full production video','Web build and hosting remain explicitly deferred']})
manifest=read(project/'project.json');manifest.update(status='atmosphere-v3-pc-review-ready',humanReview='v1-approved-v3-pending')
manifest['paths']['sampleDelivery']='projects/ai-3d-lofi-gaming-room/production/atmosphere-v3-delivery.json';save(project/'project.json',manifest)
checkpoint=read(project/'production/checkpoint.json');checkpoint.update(stage='atmosphere-v3-pc-review-ready',sampleDelivery=manifest['paths']['sampleDelivery'],updatedAtKst=now,
 latestUserSteering=['캐릭터 애니메이션·텍스처 전반 품질 개선','머리카락 물리·동숲처럼 잔잔한 잎 흔들림·창가 빛 효과','이전 지시 유지: PC 테스트 먼저, 웹빌드 최종'],
 nextAction='Deliver PC v3 review, effect comparison controls and Windows player. Preserve prior deliveries. Web installation/build/hosting remain deferred.')
checkpoint['completed']=[x for x in checkpoint['completed'] if not x.startswith('PC v3:')]+[
 'PC v3: constrained hair dynamics and collision handling verified during imported native motion',
 'PC v3: gentle size-scaled foliage breeze and depth-clipped window shafts',
 'PC v3: native-resolution renderer, contact occlusion, reflection and material polish',
 'PC v3: Windows build errors 0; real native walking/day-night control visually checked',
 'PC v3: 48-second FHD60 clean/captioned/KO/EN delivery; full decode and PTS verified']
checkpoint['pending']=['User PC v3 review','Detailed native sitting/reading, notes UI and timer','Remaining tool demonstrations and full production video','WebGL installation/build/hosting, explicitly deferred'];save(project/'production/checkpoint.json',checkpoint)
ledger=read(project/'production/review-ledger.json');ledger['checks']=[x for x in ledger['checks'] if x['id']!='atmosphere-v3-pc-review']
ledger['checks'].append({'id':'atmosphere-v3-pc-review','status':'native-runtime-and-sampled-visual-qa-complete','evidence':'production/atmosphere-v3-delivery.json','masterSha256':d['outputs'][1]['sha256'],'humanReviewed':False,'webBuilt':False});save(project/'production/review-ledger.json',ledger)
plan=read(project/'planning/production-plan.json');plan.update(stage='atmosphere-v3-pc-review-ready',sampleDelivery='production/atmosphere-v3-delivery.json')
plan['game']['engine']['sceneTarget']='Assets/LofiRoom/Scenes/LofiAtmosphereRoom.unity'
plan['authorization']['immediatePriority']='PC v3 physics, foliage, window-light and material review. Web remains deferred.'
plan['authorization']['latestUserReplies']=checkpoint['latestUserSteering'];save(project/'planning/production-plan.json',plan)
shutil.copyfile(project/'production/atmosphere-v3-review.html',local/'index.html')
playerLog=Path('C:/Users/1/AppData/LocalLow/YamyamCoding/Yamyam Lofi Room/Player.log')
if playerLog.exists():shutil.copyfile(playerLog,local/'native-player-reviewed.log')
print(json.dumps({'status':manifest['status'],'sha256':d['outputs'][1]['sha256'],'nativeBuild':native,'hairCollisionCorrections':metrics['hairCollisionCorrections']}))
