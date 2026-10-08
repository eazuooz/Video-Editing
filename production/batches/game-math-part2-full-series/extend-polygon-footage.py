"""Add directly inspected tile placement; preserve all narration and diagrams."""
from pathlib import Path
import datetime, hashlib, json, shutil
from production_control import require_current_authorization
R=Path(__file__).resolve().parents[3];slug='game-math-polygons-triangulation'
require_current_authorization(slug,'inspected polygon footage capacity refinement')
P=R/f'projects/{slug}';lesson=Path(__file__).parent/f'lessons/{slug}.json';author=Path(__file__).parent/'author-geometry-polygons.py';cuts=P/'sources/gameplay-cuts.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(lesson);c=read(cuts);s=next(x for x in d['scenes'] if x['id']=='11');cut=next(x for x in c['cuts'] if x['scene']=='11')
assert s['maxSeconds']==cut['maxSeconds']==45,'Already extended or unexpected source plan'
assert read(R/f'shared/output/{slug}/render-job-result.json')['exitCode']==0
sheet=R/f'shared/output/{slug}/inspection/dorf-capacity-extension/154-177-seconds.jpg';assert sheet.is_file()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=R/f'shared/output/{slug}/spoken-clarity/footage-extent-{stamp}';backup.mkdir(parents=True)
for f in [lesson,author,cuts,P/'production/script-review.json',R/f'shared/output/{slug}/render-receipts.json']:shutil.copy2(f,backup/f.name)
before_ko=sha(P/'script/narration.ko.json');before_en=sha(P/'script/narration.en.json')
segments=[dict(**{'in':90},maxSeconds=33),dict(**{'in':154},maxSeconds=3),dict(**{'in':173},maxSeconds=17)]
s.update(sourceSegments=segments,maxSeconds=53);cut.update(sourceSegments=segments,maxSeconds=53)
text=author.read_text(encoding='utf8');old="A(11,'타일 하나와 연결된 땅은 다릅니다',D,[(90,123),(178,190)],[";new="A(11,'타일 하나와 연결된 땅은 다릅니다',D,[(90,123),(154,157),(173,190)],[";assert text.count(old)==1;author.write_text(text.replace(old,new),encoding='utf8')
source=c['sources']['dorfromantik-official-trailer'];assert sha(R/source['file'])==source['sha256']
note='Additional native source pixels154–177s directly reviewed at1-second intervals2026-10-08. Select154–157 actual tile placement/deck update, and173–178 tile preview/placement and camera movement over the connected notched land. Preserve previously approved178–190. Exclude157–173 scenic biome montage and its transitions, and190 onward scenic montage; do not use them to fill the actual-action quota. No loop, slowing, generated replacement or source audio. Existing narration about convex individual tiles versus a potentially concave union matches these actions; no game algorithm inference.'
source['inspection']+=' '+note;source['inspectionSheets'].append(sheet.relative_to(R).as_posix());source.setdefault('inspectionEvidence',[]).append(dict(path=sheet.relative_to(R).as_posix(),sha256=sha(sheet)))
source['approvedIntervals']=[[0,17],[21,56],[67,79.5],[82,89.5],[90,123],[154,157],[173,190]]
for x in c['cuts']:
 if x['sourceId']=='dorfromantik-official-trailer':x['inspection']=source['inspection']
write(lesson,d);write(cuts,c)
review=read(P/'production/script-review.json');review.update(lessonSha256=sha(lesson),actualCapacitySeconds=393,sourceExtentReview=note);write(P/'production/script-review.json',review)
assert before_ko==sha(P/'script/narration.ko.json') and before_en==sha(P/'script/narration.en.json')
write(P/'production/footage-capacity-extension.json',dict(status='passed-direct-source-action-pixel-review',scene='11',baseline=backup.relative_to(R).as_posix(),beforeCapacitySeconds=385,afterCapacitySeconds=393,addedIntervals=[[154,157],[173,178]],sourceSha256=source['sha256'],inspectionSheet=sheet.relative_to(R).as_posix(),inspectionSha256=sha(sheet),visibleActionAndConnection=note,narrationPreserved=True,allExplanationScenesPreserved=True,publicGameIpReview='pending'))
with (P/'sources/SOURCES.md').open('a',encoding='utf8') as f:f.write('\n\n2026-10-08 실측 비율 보완: '+note+'\n검사 원본: '+sheet.relative_to(R).as_posix()+' / SHA256 '+sha(sheet)+'\n')
print(backup.relative_to(R).as_posix())
