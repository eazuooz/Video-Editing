"""Import the three locally exported Tripo assets through the scoped Unity MCP."""
from pathlib import Path
import importlib, json

root = Path(__file__).resolve().parents[3]
client = importlib.import_module("unity-mcp-client")
source = root / "projects/ai-3d-lofi-gaming-room/production/local/tripo"
lines = ["UnityEditor.EditorApplication.isPlaying = false;"]
for label in ("hero-walk", "hero-idle", "headphones"):
    src = (source / label).as_posix()
    dest = "Assets/LofiRoom/Models/" + label
    lines.append(f'if (!System.IO.Directory.Exists("{dest}")) UnityEditor.FileUtil.CopyFileOrDirectory("{src}", "{dest}");')
lines.append('UnityEditor.AssetDatabase.Refresh(UnityEditor.ImportAssetOptions.ForceSynchronousImport);')
lines.append('return string.Join("\\n", UnityEditor.AssetDatabase.FindAssets("t:Model", new[]{"Assets/LofiRoom/Models"}).Select(UnityEditor.AssetDatabase.GUIDToAssetPath));')
path, result = client.call("eval", {"code": "\n".join(lines)})
print(json.dumps({"record":str(path),"result":result}, ensure_ascii=False))
