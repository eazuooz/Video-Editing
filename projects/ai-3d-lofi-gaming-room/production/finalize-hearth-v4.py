"""Deliver the selected PC interaction revision without changing earlier deliveries."""
from pathlib import Path
import datetime,hashlib,json,shutil
root=Path(__file__).resolve().parents[3];project=root/'projects/ai-3d-lofi-gaming-room';local=project/'production/local/hearth-v4'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
d=read(local/'delivery.json');build=read(local/'native-build.json');motion=read(local/'motion-import.json');metrics=read(local/'hearth-metrics.json')
assert d['videoFrames']==4320 and build['result']=='Succeeded' and build['errors']==0
assert motion['avatarValid'] and motion['avatarHuman'] and metrics['flameShaderSupported'] and metrics['flameShaderErrors']==0
assert metrics['musicPlaying'] and metrics['firePlaying'] and metrics['music']!='fireplace'
assert all(s['velocityModeX']==s['velocityModeY']==s['velocityModeZ'] for s in metrics['fireSystems'])
assert sha(Path(d['outputs'][1]['path']))==d['outputs'][1]['sha256']
previous=read(project/'production/atmosphere-v3-delivery.json')
for t in previous['textureInputs']:assert sha(root/t['path'])==t['sha256']
package=local/'windows'
files=[{'path':p.relative_to(package).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(package.rglob('*')) if p.is_file()]
save(project/'production/hearth-v4-delivery.json',{**d,'reviewUrl':'http://127.0.0.1:9322/','updatedAtKst':now,
 'scene':'unity/LofiGamingRoomWeb/Assets/LofiRoom/Scenes/LofiHearthRoom.unity','nativeBuild':build,
 'nativeExecutable':str(package/'YamyamLofiRoom.exe'),'nativePackageFiles':files,'textureInputs':previous['textureInputs'],
 'motionImport':motion,'runtimeMetrics':metrics,'assetProvenance':'production/hearth-v4-asset-record.json',
 'visualReview':{'status':'actual-native-controls-and-encoded-scenes-reviewed','reviewedSeconds':[2,10,18,28,36,44,54,61,68],
  'nativeProof':'production/local/hearth-v4/native-pc-final.jpg','humanApproval':False},
 'features':{
  'activities':'Native KayKit sit-down, seated idle and stand-up, plus licensed EmacEArt reading. Native Tripo walk/idle retained. Walk-align-enter-loop-exit, queued requests at safe boundaries, eased state blends, seat/hand/foot contact IK. Original clips are retained; IK and prop movement fit the furniture rather than claiming new captured motion.',
  'desk':'One compact iMac-style all-in-one with keyboard and mouse; desktop tower and dual monitors removed. Smaller oak desk and fitted chair.',
  'shelves':'Two tiers on each side of the central fireplace on the left wall.',
  'fireplace':'Self-authored stone/brick surround, oak mantel, stacked charred logs and glowing ember bed. Layered procedural flame particles, embers, restrained smoke, depth-softened edges and coherent warm light variation. All particle linear velocity axes use Constant mode.',
  'recordPlayer':'Small table beneath window, walnut player, platter with visible asymmetric label, tonearm. Playback follows the existing music source, with 33.333 rpm acceleration/coasting and a 3D click target.',
  'audio':'Same approved CC0 Morning Coffee plus CC0 Fireplace Sound loop. Native music and fire have separate controls and volume sliders. The review mixes the same files to the shot plan, with quieter music during 40-50s fire inspection.',
  'retained':'4K/PBR inputs, constrained hair motion, 311 gently swaying leaves and window shafts from v3 retained.'},
 'remaining':['User PC v4 review','Notes UI, focus timer and remaining full-game polish','Remaining tool demonstrations and complete production video','Final WebGL installation/build/hosting explicitly deferred'],
 'youtubeUploaded':False,'publicWebDeployed':False,'webModuleInstalled':False})
manifest=read(project/'project.json');manifest.update(status='hearth-v4-pc-review-ready',humanReview='v1-approved-v4-pending');manifest['paths']['sampleDelivery']='projects/ai-3d-lofi-gaming-room/production/hearth-v4-delivery.json';save(project/'project.json',manifest)
cp=read(project/'production/checkpoint.json');cp.update(stage='hearth-v4-pc-review-ready',sampleDelivery=manifest['paths']['sampleDelivery'],updatedAtKst=now,
 nextAction='Deliver the native PC interaction review with iMac, two-tier shelves, fireplace and record-player audio. Web build remains deferred; do not publish or upload.')
cp['completed']=[x for x in cp['completed'] if not x.startswith('PC v4:')]+[
 'PC v4: licensed native chair entry/exit, desk and reading states, fitted seat/hands/feet and safe queued transitions',
 'PC v4: compact all-in-one desk, central hearth with two-tier shelves on both sides, window music table',
 'PC v4: flame/ember/smoke particles, warm flicker and CC0 crackle loop with separate volume',
 'PC v4: record playback drives platter and tonearm; actual native controls verified',
 'PC v4: Windows build errors 0 and 72-second FHD60 four-file review with full decode/PTS checks']
cp['pending']=['User PC v4 review','Notes UI, focus timer and remaining polish','Remaining tool demonstrations and full production video','Web build and hosting explicitly deferred'];save(project/'production/checkpoint.json',cp)
ledger=read(project/'production/review-ledger.json');ledger['checks']=[x for x in ledger['checks'] if x['id']!='hearth-v4-pc-review'];ledger['checks'].append({'id':'hearth-v4-pc-review','status':'native-interaction-and-sampled-output-qa-complete','evidence':'production/hearth-v4-delivery.json','masterSha256':d['outputs'][1]['sha256'],'humanReviewed':False,'webBuilt':False});save(project/'production/review-ledger.json',ledger)
plan=read(project/'planning/production-plan.json');plan.update(stage='hearth-v4-pc-review-ready',sampleDelivery='production/hearth-v4-delivery.json');plan['game']['engine']['sceneTarget']='Assets/LofiRoom/Scenes/LofiHearthRoom.unity'
plan['authorization']['latestUserReplies']=cp['latestUserSteering'];plan['authorization']['immediatePriority']='Current PC v4 interactions, smaller iMac desk, two-tier shelves, hearth and window record player; preserve deferred WebGL boundary.';save(project/'planning/production-plan.json',plan)
shutil.copyfile(project/'production/hearth-v4-review.html',local/'index.html')
print(json.dumps({'status':manifest['status'],'masterSha256':d['outputs'][1]['sha256'],'nativeBytes':build['bytes']}))
