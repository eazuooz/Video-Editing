"""Cancel only this turn's TTS child after the 15 useful chunks are saved.

The unchanged handoff coordinator observes its exit and restores research.
No training process, queue config, checkpoint or foreign pause file is touched.
"""
from pathlib import Path
import json,time,hashlib
import psutil,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
token='64959105-2306-4969-8e17-6398037d9616'
out=ROOT/'shared/output/narration/game-math-quaternion-teaching-additions-v3/qwen3-1.7b-balanced-v1/chunks'
while not (out/'15-scene.wav').exists():time.sleep(.25)
time.sleep(.2)
lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text(encoding='utf8'))
assert lease['token']==token and lease['project']=='game-math-quaternion-teaching-additions-v3' and lease['state']=='tts_running'
saved={}
for i in range(1,16):
 p=out/f'{i:02}-scene.wav';samples,rate=sf.read(p);assert rate==24000 and len(samples)>24000
 saved[f'{i:02}']={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':len(samples)/rate}
owner=lease['ttsOwner'];process=psutil.Process(owner['pid'])
assert abs(process.create_time()-owner['createTime'])<.01
assert process.cmdline()==owner['command']
assert 'render-narration-v3.py' in ' '.join(process.cmdline())
record={'token':token,'savedChunks':saved,'reason':'Queued new gameplay narration exceeds played source capacities at measured voice pace; preserve useful first15 chunks and rewrite only the new gameplay drafts in a separate v4 project.','stoppedOnlyOwnedTtsPid':process.pid,'trainingProcessModified':False,'originalQueueRestoration':'unchanged cooperative coordinator finally handler; verify fresh state after exit','v3ScriptsAndOldMediaChanged':False,'humanListeningApproved':False,'time':time.time()}
process.terminate();process.wait(timeout=30)
(B/'quaternion-v3-owned-tts-checkpoint.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'savedChunks':15,'stoppedOnlyOwnedTtsPid':owner['pid'],'originalQueueRestoreMustBeVerified':True}))
