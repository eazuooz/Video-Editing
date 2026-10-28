from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;C=R/'unity/VideoEditing/Assets/VideoScenes/design-25-30-unity-v2'
files=sorted([p for p in C.rglob('*.cs') if p.name!='DesignBuildVersion.cs']+[C/'asset-map.json'])
records=[dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
fingerprints={}
for stage in ['D25D26Stage','D27D28Stage','D29D30Stage','DesignProbeStage']:
 subset=[x for x in records if not Path(x['path']).name.endswith('Stage.cs') or Path(x['path']).name in ['DesignLessonStage.cs',stage+'.cs']]
 fingerprints[stage]=hashlib.sha256(json.dumps(subset,sort_keys=True).encode()).hexdigest()
code='namespace Yamyam.DesignVisualV2 { public static class DesignBuildVersion { public static string For(string stage) { switch(stage) { '+''.join('case "'+k+'":return "'+v+'";' for k,v in fingerprints.items())+'default:return "unknown";} } } }\n'
target=C/'DesignBuildVersion.cs'
if not target.exists() or target.read_text()!=code:target.write_text(code,encoding='utf8')
(H/'code-fingerprint.json').write_text(json.dumps(dict(fingerprints=fingerprints,files=records),indent=2)+'\n',encoding='utf8')
print(json.dumps(fingerprints))
