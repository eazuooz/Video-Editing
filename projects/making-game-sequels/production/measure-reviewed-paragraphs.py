"""Current13 PCM paragraph proposals; no resynthesis, shortening or final approval."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
source=ROOT/'projects/avoid-game-comparisons/production/measure-reviewed-paragraphs.py'
spec=importlib.util.spec_from_file_location('paragraph_measure',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.ROOT=ROOT
def read(p):return json.loads(p.read_text(encoding='utf-8'))
ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json');index=read(BASE/'narration-expanded13-index.json')
portable=read(BASE/'current-asr-word-index.json') if (BASE/'current-asr-word-index.json').exists() else None
assert index['wholeCurrent13TechnicalReview'] and len(index['measurements'])==13
target=BASE/'measured-paragraphs-expanded13.json';assert not target.exists(),'Preserve measured evidence; inspect rather than repeat.'
rows=[]
for scene in ko['scenes']:
    sid=scene['id'];m=next(m for m in index['measurements'] if m['scene']==sid)
    if sid=='13':p=BASE/'asr-additive-whole-local/13-whole.json'
    elif sid in ['01','04','07','11']:p=BASE/f'asr-post-repair-local/{sid}-whole-v2.json'
    else:p=ROOT/f'shared/output/narration/making-game-sequels/qwen3-1.7b-balanced-v1/asr/{sid}.json'
    evidence=next(s for s in portable['scenes'] if s['scene']==sid) if portable else read(p)
    row=module.measure(scene,m,evidence,next(s for s in en['scenes'] if s['id']==sid)['lines']);row['asrEvidence']={'path':p.relative_to(ROOT).as_posix(),'sha256':evidence['readbackSha256'] if portable else module.sha(p)};rows.append(row)
value=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),status='Current13 quiet PCM paragraph proposals; final joins/native words/captions pending',sceneCount=13,paragraphs=52,scenes=rows,speechSeconds=sum(r['speechSeconds'] for r in rows),scriptKoSha256=module.sha(BASE.parent/'script/narration.ko.json'),scriptEnSha256=module.sha(BASE.parent/'script/narration.en.json'),allPcmUnchanged=True,finalTimingApproved=False,finalRatioApproved=False,humanWholeListening='pending')
target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([dict(id=r['id'],seconds=r['speechSeconds'],paragraphs=[[p['paragraph'],round(p['speechStart'],3),round(p['speechEnd'],3),round(p['pcmSeconds'],3)] for p in r['paragraphs']]) for r in rows]))
