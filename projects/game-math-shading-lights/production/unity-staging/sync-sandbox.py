"""Update our stopped isolated editor project, preserving previous source snapshots."""
from pathlib import Path
import json,hashlib,subprocess,shutil,importlib.util
S=Path(__file__).resolve().parent
record=json.loads((S/'sandbox-preparation.json').read_text(encoding='utf-8'))
dest=Path(record['sandbox']).resolve()
assert dest.parent==S and dest.name.startswith('LocalUnity-') and (dest/'M21_SANDBOX.json').is_file()
escaped=str(dest).replace("'","''")
query="$p='"+escaped+"'; @(Get-CimInstance Win32_Process -Filter \"Name='Unity.exe'\" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($p) } | Select-Object -ExpandProperty ProcessId) | ConvertTo-Json -Compress"
running=subprocess.check_output(['powershell','-NoProfile','-Command',query],text=True).strip()
if running and running not in ('[]','null'):raise RuntimeError('Our isolated project is still running; do not mutate or terminate it: '+running)
spec=importlib.util.spec_from_file_location('prepare',S/'prepare-sandbox.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
fingerprint=hashlib.sha256(b''.join(n.encode()+b'\0'+(S/n).read_bytes()+b'\0' for n in module.CODE)).hexdigest()
if fingerprint==record['fingerprint']:print('Sources already synchronized; no mutation.');raise SystemExit(0)
root=dest/'Assets/VideoScenes/game-math-shading-lights'
archive=S/'local-source-history'/record['fingerprint'];archive.mkdir(parents=True,exist_ok=True)
for path in root.rglob('*'):
    if path.is_file() and path.suffix in ('.cs','.shader'):
        out=archive/path.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True)
        if not out.exists():shutil.copy2(path,out)
for name in module.CODE:shutil.copy2(S/name,root/('Editor' if name=='LightLabCapture.cs' else '')/name)
(root/'LightLabBuildVersion.cs').write_text('namespace Yamyam.GameMath.LightLab { public static class LightLabBuildVersion { public const string Value="'+fingerprint+'"; } }\n',encoding='utf-8')
marker=json.loads((dest/'M21_SANDBOX.json').read_text(encoding='utf-8'));marker['fingerprint']=fingerprint
(dest/'M21_SANDBOX.json').write_text(json.dumps(marker,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record.update(fingerprint=fingerprint,status='sources-updated-awaiting-own-editor-import')
(S/'sandbox-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated stopped isolated project; prior source snapshot retained:',fingerprint)
