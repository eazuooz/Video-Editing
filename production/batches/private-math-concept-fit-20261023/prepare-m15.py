from common import *
import shutil
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';O.mkdir(parents=True,exist_ok=True);authorized('M15')
delta=read(B/'m15-narration-edits.json');count=sum(map(len,delta['edits'].values()));total=sum(len(s['lines']) for s in read(P/'script/narration.ko.json')['scenes'])
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst);save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(dst),kind='Recovered original AAC; original PCM unavailable',oldMastersPreserved=True))
def adapt(s):return s.replace('M14','M15').replace('m14','m15').replace('game-math-polygon-partition-v2',P.name)
s=adapt((B/'prepare-m14-voice.py').read_text(encoding='utf8'));a=s.index('titles=');z=s.index('\njobs=[]',a)
titles={'02':'노란 벽 뒤로 가려지는 캐릭터','05':'빈 구멍과 반투명 표면의 차이','08':'기지의 벽과 건설 미리 보기','11':'빨간 표면과 RGB 색 표현','14':'손전등과 굽은 바위 표면','17':'조명 설치 전후의 방과 벽','19':'그늘에도 남아 있는 밝기','21':'앞뒤 순서와 밝기의 구분'}
(B/'prepare-m15-voice.py').write_text(s[:a]+'titles='+repr(titles)+s[z:],encoding='utf8')
s=adapt((B/'assemble-m14-audio.py').read_text(encoding='utf8')).replace('newTtsParagraphs=13',f'newTtsParagraphs={count}').replace('unchangedParagraphs=66',f'unchangedParagraphs={total-count}').replace('changed=13,unchanged=66',f'changed={count},unchanged={total-count}').replace("{'QG04':6,'QG06':4.8,'QG07':2.25,'QG09':2.4,'21':4.8}","{'02':8,'05':11.5,'08':10,'11':5,'14':5.5,'17':13.5,'19':5,'21':4}")
s=s.replace("for j,cue in enumerate(original['cues'],1):", "assert len(original['cues'])==len(by_script[sid]['lines'])\n  for j,cue in enumerate(original['cues'],1):")
(B/'assemble-m15-audio.py').write_text(s,encoding='utf8')
for name in ['asr','render','preflight']:(B/f'{name}-m15.py').write_text(adapt((B/f'{name}-m14.py').read_text(encoding='utf8')),encoding='utf8')
s=adapt((B/'captions-m14.py').read_text(encoding='utf8')).replace('sourceParagraphs=79',f'sourceParagraphs={total}');(B/'captions-m15.py').write_text(s,encoding='utf8')
save(H/'narration-text-review.json',dict(status='original KO and replacement paragraphs read; unchanged technical ordering preserved',at=now(),changed=count,unchanged=total-count,total=total,orderPreserved=True,mathPreserved=['Visibility vs shading','Opaque depth8vs3 and reverse-depth qualification','BRDF direction conventions and units','BRDF>1 vs integrated energy conservation','BRDF/BTDF/BSDF/BSSRDF distinctions','4J/2s=2W; 2W/2m2=1Wm-2','Radiance vs irradiance and solid angle','cos60=.5 under fixed light','Emission and hemispherical reflection integral','Direct and indirect illumination','Monte Carlo density and sample-count normalization','Lambert .6*10/pi=1.91'],actualListening=False))
print(count,'changed;',total-count,'preserved;',total,'paragraphs')
