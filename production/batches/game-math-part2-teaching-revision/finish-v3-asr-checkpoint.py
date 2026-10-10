"""End only our now-idle CPU watcher once all retained15 hashes are cached."""
from pathlib import Path
import json,hashlib
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
out=ROOT/'shared/output/narration/game-math-quaternion-teaching-additions-v3/qwen3-1.7b-balanced-v1'
for i in range(1,16):
 wav=out/f'chunks/{i:02}-scene.wav';asr=json.loads((out/f'asr/{i:02}.json').read_text(encoding='utf8'))
 assert asr['audio_sha256']==hashlib.sha256(wav.read_bytes()).hexdigest()
p=psutil.Process(64812);cmd=p.cmdline()
assert 'qwen3-tts/review_project_narration.py' in cmd and '--watch' in cmd
assert cmd[cmd.index('--project')+1]=='game-math-quaternion-teaching-additions-v3'
record={'currentHashCachedChunks':15,'full30JobWatchCompleted':False,'reason':'Only the first15 useful chunks were retained. End our watcher waiting for unrendered gameplay drafts; no research process touched.','ownedIdleCpuWatcherPid':p.pid,'creationTime':p.create_time(),'trainingProcessModified':False}
p.terminate();p.wait(timeout=30)
(B/'quaternion-v3-asr-checkpoint.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record))
