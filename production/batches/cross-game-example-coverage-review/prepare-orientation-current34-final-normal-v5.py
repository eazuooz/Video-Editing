"""Expose the new assembled V5 media through the verified existing helper."""
from pathlib import Path
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw';rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
p=psutil.Process(27140);assert abs(p.create_time()-1791509666.837781)<.01 and p.cwd()==str(ROOT) and 'serve-native-review-v1.py' in ' '.join(p.cmdline())
sp=O/'current34-final-pair-execution-v5.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
v=s['pair'][1];source=ROOT/v['path'];assert sha(source)==v['sha256']
target=RAW/'orientation-current34-final-captioned-v5.mp4';assert not target.exists();os.link(source,target);assert os.path.samefile(source,target)
html=RAW/'orientation-current34-final-review-v5.html';assert not html.exists()
text=(RAW/'orientation-current34-final-review-v3.html').read_text('utf-8').replace('reviewV3','reviewV5').replace('captioned-v3.mp4','captioned-v5.mp4').replace('기존 팔레트','상세 대상과06a 자막 여백 교정 · 기존 팔레트')
html.write_text(text,'utf-8')
print(json.dumps(dict(url='http://127.0.0.1:9250/'+html.name,sha256=v['sha256'],samefile=True)))
