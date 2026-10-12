"""Read-only inventory delta before refreshing the current distinct review."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
report=json.loads((ROOT/'production/preflight/game-lighting-history-04-1.json').read_text(encoding='utf-8-sig'))
old={x['path']:x['sha256'] for x in report['inputFiles']}
current={}
for base in sorted((ROOT/'projects').iterdir()):
    if not base.is_dir() or base.name=='game-lighting-history-04-1' or not (base/'project.json').exists():continue
    manifest=json.loads((base/'project.json').read_text(encoding='utf-8-sig'))
    paths=manifest.get('paths',{});pub=manifest.get('publishing',{})
    names={str((base/'project.json').relative_to(ROOT)).replace('\\','/'),str((base/'script/narration.ko.json').relative_to(ROOT)).replace('\\','/'),str((base/'script/narration.en.json').relative_to(ROOT)).replace('\\','/'),str((base/'planning/outline.md').relative_to(ROOT)).replace('\\','/'),str((base/'sources/SOURCES.md').relative_to(ROOT)).replace('\\','/'),str((base/'README.md').relative_to(ROOT)).replace('\\','/'),str((base/'publishing/youtube-upload.json').relative_to(ROOT)).replace('\\','/')}
    names.update(v for v in (paths.get('script'),paths.get('scriptEn'),paths.get('scriptEnglish'),pub.get('receipt')) if v)
    for name in names:
        p=ROOT/name
        if p.exists():current[name]=hashlib.sha256(p.read_bytes()).hexdigest()
delta=[{'path':name,'old':old.get(name),'current':current.get(name),'bytes':(ROOT/name).stat().st_size if (ROOT/name).exists() else None} for name in sorted(set(old)|set(current)) if old.get(name)!=current.get(name)]
out=ROOT/'production/research/game-lighting-history/local/part1-duplicate-delta-v350';out.mkdir(parents=True,exist_ok=True)
(out/'previous-preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(delta,ensure_ascii=False,indent=2))
