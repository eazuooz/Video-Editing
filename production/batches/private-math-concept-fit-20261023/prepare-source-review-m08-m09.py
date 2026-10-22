from common import *
import html
shots=[dict(id='M08 stationary assembly viewpoint',source='shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/sources/besiege-uWKEJ92486U.mp4',start=42,end=47.7),dict(id='M09 grapple endpoints',source='shared/output/private-game-math-polish-20261022/fhd-candidates/5u3sUKuncSU.mp4',start=407,end=419.5),dict(id='M09 factory connections',source='shared/output/private-math-concept-fit-20261023/sources/satisfactory-official/SATISFACTORY_1.2_LAUNCHTRAILER_MASTER.mp4',start=71.5,end=75.8)]
src=R/'output/private-math-source-review/m06.html';s=src.read_text(encoding='utf8');a=s.index('<button');b=s.index('<p id="state">',a)
s=s[:a]+''.join(f'<button data-i="{i}">{html.escape(x["id"])}</button>' for i,x in enumerate(shots))+s[b:]
a=s.index('const shots=');b=s.index(';const v=',a);s=s[:a]+'const shots='+json.dumps(shots)+s[b:]
(src.parent/'m08-m09.html').write_text(s,encoding='utf8');save(B/'m08-m09-source-review-plan.json',dict(shots=shots,review='moving review pending'))
