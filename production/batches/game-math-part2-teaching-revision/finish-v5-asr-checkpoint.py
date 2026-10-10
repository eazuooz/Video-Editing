"""Close this task's idle CPU watcher after its four complete hashes are cached."""
from pathlib import Path
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
out=ROOT/'shared/output/narration/game-math-quaternion-teaching-additions-v5/qwen3-1.7b-balanced-v1'
for ident in ['01','03','05','06']:
 wav=out/f'chunks/{ident}-scene.wav';asr=json.loads((out/f'asr/{ident}.json').read_text(encoding='utf8'))
 assert asr['audio_sha256']==hashlib.sha256(wav.read_bytes()).hexdigest()
owners=[]
for pid in [72864,71820]:
 p=psutil.Process(pid);cmd=p.cmdline()
 assert 'qwen3-tts/review_project_narration.py' in cmd and '--watch' in cmd
 assert cmd[cmd.index('--project')+1]=='game-math-quaternion-teaching-additions-v5'
 owners.append({'pid':pid,'createTime':p.create_time(),'command':cmd})
record={'currentHashCachedChunks':['01','03','05','06'],'twoRejectedScenesNotApproved':['02','04'],'ownedIdleCpuWatchers':owners,'researchProcessesTouched':False}
(B/'quaternion-v5-asr-checkpoint.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for owner in owners:
 try:
  p=psutil.Process(owner['pid']);assert p.create_time()==owner['createTime'];p.terminate();p.wait(timeout=20)
 except psutil.NoSuchProcess:pass
print(json.dumps({'cachedScenes':4,'closedOwnIdleWatchers':len(owners),'researchProcessesTouched':False}))
