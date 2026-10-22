from common import *
import shutil
P=R/'projects/game-math-bounds-transform-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';O.mkdir(parents=True,exist_ok=True);authorized('M10')
delta=read(B/'m10-narration-edits.json');count=sum(map(len,delta['edits'].values()));total=sum(len(s['lines']) for s in read(P/'script/narration.ko.json')['scenes'])
source=read(R/'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/source.json');assert sha(R/source['path'])==source['sha256']
source.update(id='tinyglade',game='Tiny Glade',role='independent-gameplay-from-official-press-kit',selected=[dict(scene='LG05',start=11.8,end=16.3,observed='Building placement preview becomes a solid structure; width/roof dimensions change. Do not claim this is object rotation or collision data.'),dict(scene='LG07',start=17,end=19.4,observed='Building height stretches and returns while surrounding buildings and camera remain fixed. A distinct action from the first cut.')],nativePlayback=[dict(start=11.8,end=16.520871,rate=1),dict(start=17,end=19.593934,rate=1)],sampleEvidence=['shared/output/private-math-concept-fit-20261023/candidates/tiny-glade-building/sheet-12-01.jpg','shared/output/private-math-concept-fit-20261023/candidates/tiny-glade-building/sheet-12-02.jpg'],actualListening=False,sourceAudio='Original embedded mix; isolated effects/music clearance not inferred from press distribution.')
save(H/'source-evidence.json',dict(checkedAt=now(),sources=[source],rejected=['Serious Sam2 repeated combat/traversal does not isolate bounds or object rotation.','Portal2 narrated official demonstration omitted.','Camera travel is replaced by a fixed building model with controlled camera motion.'],selectionReason='Two different construction operations illustrate changing occupied extent; mathematical world bounds and exact numbers are calculated in our own models.',actualListening=False))
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst);save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(dst),kind='Recovered original AAC; original PCM unavailable',oldMastersPreserved=True))
def adapt(s):return s.replace('M09','M10').replace('m09','m10').replace('game-math-lines-circles-v2',P.name)
s=adapt((B/'prepare-m09-voice.py').read_text(encoding='utf8'));a=s.index('titles=');z=s.index('\njobs=[]',a)
titles={'10':'둥근 표면과 계산용 구','LG04':'머리와 팔다리를 각각 감싸기','13':'팔을 펼치면 경계도 달라집니다','LG05':'건물을 놓고 크기를 바꿀 때','16':'상자 겹침과 물체 접촉은 다릅니다','LG06':'제자리 회전과 카메라 이동 구분','19':'고정된 건물을 다른 쪽에서 보기','LG07':'높이를 바꾸면 다시 계산할 경계','21':'구조물과 몸의 경계 비교'}
(B/'prepare-m10-voice.py').write_text(s[:a]+'titles='+repr(titles)+s[z:],encoding='utf8')
s=adapt((B/'assemble-m09-audio.py').read_text(encoding='utf8')).replace('newTtsParagraphs=16',f'newTtsParagraphs={count}').replace('unchangedParagraphs=62',f'unchangedParagraphs={total-count}').replace('changed=16,unchanged=62',f'changed={count},unchanged={total-count}').replace("{'02':12.5,'LG01':4.3}","{'LG05':4.5,'LG07':2.4}")
(B/'assemble-m10-audio.py').write_text(s,encoding='utf8');(B/'asr-m10.py').write_text(adapt((B/'asr-m09.py').read_text(encoding='utf8')),encoding='utf8')
# Use the general caption aligner, not M09's specific isolated-ASR correction.
s=(B/'captions-m06.py').read_text(encoding='utf8').replace('M06','M10').replace('m06','m10').replace('game-math-quaternion-calculations-v3',P.name).replace('sourceParagraphs=145',f'sourceParagraphs={total}')
(B/'captions-m10.py').write_text(s,encoding='utf8')
save(H/'narration-text-review.json',dict(status='all-original-paragraphs-and-replacement-text-read',at=now(),changed=count,unchanged=total-count,total=total,orderPreserved=True,mathPreserved=['sphere forms and squared distance','radius scaling versus area/volume','AABB min/max, center and half-extent','overlap versus contact and touching convention','rotation of8 corners, not just min and max','c prime=A c+t; e prime=abs(A)e','transformed point set versus transformed old box'],actualListening=False))
print(count,'changed;',total-count,'preserved')
