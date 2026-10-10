"""A separate preview page on the existing loopback server; no media changes."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[4];PROOF=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=read(PROOF/'additional-role-action-direct-review-v2.json')
assert review['all38NativeAnd38FramedSamplesDirectlyRead']
folder=ROOT/'shared/assets/presenting-game-scores/raw'
old=folder/'character-parameters-native-playback-v1.html'
target=folder/'character-parameters-additional-action-playback-v2.html'
assert not target.exists()
source=folder/'character-parameters-gBbKFYZYvbc.mp4'
assert sha(source)==review['sourceSha256']
text=old.read_text('utf-8-sig')
a=text.index('const windows=');b=text.index(",v=document.querySelector('#source')",a)
candidate={**review['candidate'], 'startSeconds':268, 'endSeconds':280,
           'file':source.name, 'purpose':'Additional unused official ground/air exchange; no victory or exact ability formula claim.'}
text=text[:a]+'const windows='+json.dumps([candidate],ensure_ascii=False)+text[b:]
text=text.replace('Character parameters native action review v1','Character parameters additional action review v2')
text=text.replace('캐릭터마다 규칙이 다릅니다.','강점은 선택으로 이어집니다.')
target.write_text(text,'utf-8')
proof=dict(page=target.relative_to(ROOT).as_posix(),pageSha256=sha(target),
           url='http://127.0.0.1:9250/'+target.name,sourceSha256=sha(source),
           originalPagePreserved=True,newMedia=0,serverRestarted=False,
           playbackStarted=False,sourceAdoptionApproved=False)
(PROOF/'additional-playback-preparation-v2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(proof))
