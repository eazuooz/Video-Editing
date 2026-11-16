"""Project-scoped official Unity MCP operations for the PC atmosphere revision."""
from pathlib import Path
import importlib.util,json,sys
home=Path(__file__).resolve().parent
loader=importlib.util.spec_from_file_location('lofi_mcp',home/'unity-mcp-client.py')
m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
folder=(home/'local/atmosphere-v3').as_posix()
commands={
 'ao-post':'var r=UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Rendering.Universal.UniversalRendererData>("Assets/LofiRoom/GeneratedAtmosphereV3/PcRenderer.asset");var a=r.rendererFeatures[0];var o=new UnityEditor.SerializedObject(a);o.FindProperty("m_Settings.AfterOpaque").boolValue=true;o.FindProperty("m_Settings.Intensity").floatValue=.65f;o.ApplyModifiedPropertiesWithoutUndo();a.SetActive(true);a.Create();return "AO post composite";',
 'disable-ao':'var r=UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Rendering.Universal.UniversalRendererData>("Assets/LofiRoom/GeneratedAtmosphereV3/PcRenderer.asset");r.rendererFeatures[0].SetActive(false);return "AO off";',
 'play':'UnityEditor.EditorApplication.isPlaying=true;return "play";',
 'stop':'UnityEditor.EditorApplication.isPlaying=false;return "stopped";',
 'refresh':'UnityEditor.AssetDatabase.Refresh();return "refreshed";',
 'exit':'UnityEditor.EditorApplication.delayCall+=()=>UnityEditor.EditorApplication.Exit(0);return "exiting this scoped Editor";',
 'preview':'''var s=UnityEngine.Object.FindFirstObjectByType<Yamyam.LofiRoom.LofiRoomSample>();s.Idle();s.SetNight(false);s.CameraRoom();s.showControls=false;var camera=s.roomCamera;var t=new UnityEngine.RenderTexture(1920,1080,24);var p=new UnityEngine.Texture2D(1920,1080,UnityEngine.TextureFormat.RGB24,false);camera.targetTexture=t;camera.Render();UnityEngine.RenderTexture.active=t;p.ReadPixels(new UnityEngine.Rect(0,0,1920,1080),0,0);p.Apply();System.IO.File.WriteAllBytes("FOLDER/initial-day.png",p.EncodeToPNG());camera.targetTexture=null;UnityEngine.RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(t);UnityEngine.Object.DestroyImmediate(p);return "day preview";''',
 'metrics':'''var s=UnityEngine.Object.FindFirstObjectByType<Yamyam.LofiRoom.LofiRoomSample>();var h=s.actor.GetComponent<Yamyam.LofiRoom.LofiHairMotion>();var rp=UnityEngine.Rendering.Universal.UniversalRenderPipeline.asset;var a=s.atmosphere;var detail=UnityEngine.Shader.Find("Yamyam/Lofi Detailed Surface");var shafts=UnityEngine.Shader.Find("Yamyam/Window Light Volume");var result=new {frame=s.observedFrame,root=s.actor.transform.position.ToString("F4"),hairOffset=h.measuredOffset,hairMaximum=h.maximumObservedOffset,hairLengthError=h.maximumLengthError,hairCollisionCorrections=h.collisionCorrections,renderScale=rp.renderScale,msaa=rp.msaaSampleCount,day=a.dayAmount,leafRenderers=UnityEngine.Object.FindObjectsByType<UnityEngine.MeshRenderer>(UnityEngine.FindObjectsSortMode.None).Count(x=>x.name=="curved veined leaf"),detailSupported=detail.isSupported,shaftSupported=shafts.isSupported,shaderErrors=UnityEditor.ShaderUtil.GetShaderMessages(detail).Concat(UnityEditor.ShaderUtil.GetShaderMessages(shafts)).Count(x=>x.severity==UnityEditor.Rendering.ShaderCompilerMessageSeverity.Error),state=s.GetStateJson()};var text=Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented);System.IO.File.WriteAllText("FOLDER/runtime-metrics.json",text);return text;'''
}
if __name__=='__main__':
 action=sys.argv[1]
 if action in commands:tool,args='eval',{'code':commands[action].replace('FOLDER',folder)}
 else:tool,args=action,json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
 path,result=m.call(tool,args,180)
 print(json.dumps({'record':str(path),'result':result},ensure_ascii=True)[:12000])
