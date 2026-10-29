"""Freeze only the independent D29 BOTW stage; no refresh or capture."""
from pathlib import Path
import argparse,hashlib,json
H=Path(__file__).resolve().parent
R=H.parents[3]
U=R/'unity/VideoEditing'
C=U/'Assets/VideoScenes/design-d29-botw-v4'
STAGES={'kind-to-beginners':'D29BotwStage'}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def records_for(stage):
 assert stage=='D29BotwStage'
 paths=[C/'DesignBotwLessonStage.cs',C/'D29BotwStage.cs',C/'Editor/DesignBotwCapture.cs',C/'asset-map.json',H/'unity-cues.json',H/'capture-jobs.json',H/'rasterize_unity_labels.py',Path('C:/Windows/Fonts/malgun.ttf'),U/'Packages/packages-lock.json',U/'ProjectSettings/ProjectVersion.txt',U/'ProjectSettings/GraphicsSettings.asset',U/'ProjectSettings/QualitySettings.asset']
 paths += list((U/'Assets/Settings').glob('*.asset'))+list((U/'Assets/Settings').glob('*.asset.meta'))
 # Exact prefab bytes/import settings and native model inputs used by these instances.
 assets=read(C/'asset-map.json')
 rows=assets.get('assets',assets.get('entries',[])) if isinstance(assets,dict) else assets
 if isinstance(rows,dict):rows=list(rows.values())
 for a in rows:
  for key in ('path','assetPath','animationSource'):
   value=a.get(key)
   if value and value.startswith('Assets/'):
    p=U/value;paths.append(p)
    if Path(str(p)+'.meta').exists():paths.append(Path(str(p)+'.meta'))
 return [{'path':p.relative_to(R).as_posix() if p.is_relative_to(R) else p.as_posix(),'sha256':digest(p)} for p in sorted(set(paths))]
def fingerprint(records):return hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
def ensure_idle():
 for n in ['DesignVisualV2','DesignClarityV3','DesignBotwV4']:
  assert not (U/'Library'/f'{n}.request.json').exists(),'Pending request preserved: '+n
  p=U/'Library'/f'{n}.status.json'
  if p.exists():assert read(p).get('status') not in ('building','capturing'),'Active capture preserved: '+n
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 records=records_for('D29BotwStage');fp=fingerprint(records)
 if a.check:
  assert read(H/'botw-code-fingerprint.json')['fingerprints']['D29BotwStage']==fp,'Changed source: refreeze/recompile required'
  print('UNCHANGED '+fp);return
 ensure_idle();auth=read(H/'authorization.json');assert auth['slug']=='kind-to-beginners' and auth['revision']=='botw-v4' and auth['localProductionAuthorized']
 code='namespace Yamyam.DesignVisualV2 { public static class DesignBotwBuildVersion { public static string For(string stage) { return stage=="D29BotwStage"?"'+fp+'":"unknown"; } } }\n'
 target=C/'DesignBotwBuildVersion.cs'
 if not target.exists() or target.read_text('utf-8')!=code:target.write_text(code,encoding='utf-8')
 result={'schemaVersion':1,'scope':'D29 botw-v4 only','fingerprints':{'D29BotwStage':fp},'filesByStage':{'D29BotwStage':records},'generatedBuildVersion':target.relative_to(R).as_posix(),'generatedBuildVersionSha256':digest(target),'refreshOrCaptureStarted':False}
 (H/'botw-code-fingerprint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(fp)
if __name__=='__main__':main()
