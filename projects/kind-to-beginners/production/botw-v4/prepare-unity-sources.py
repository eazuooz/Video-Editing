"""Create isolated authored native sources; never deploy, refresh or capture Unity."""
from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent
R=H.parents[3];OLD=R/'unity/VideoEditing/Assets/VideoScenes/design-25-29-clarity-v3';DEST=H/'unity-source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 DEST.mkdir(parents=True,exist_ok=True);(DEST/'Editor').mkdir(exist_ok=True)
 base=(OLD/'DesignClarityLessonStage.cs').read_text('utf8').replace('DesignClarityLessonStage','DesignBotwLessonStage').replace('design-25-29-clarity-v3','design-d29-botw-v4')
 base=base.replace('public void FlushPoses()','public virtual void FlushPoses()')
 (DEST/'DesignBotwLessonStage.cs').write_text(base,'utf8')
 capture=(OLD/'Editor/DesignClarityCapture.cs').read_text('utf8').replace('DesignClarity','DesignBotw').replace('DesignClarityV3','DesignBotwV4').replace('DesignBotwV3','DesignBotwV4')
 capture=capture.replace('const string MediaRoot = "C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029";','const string MediaRoot = "D:/Github/VideoEditing/projects/kind-to-beginners/production/local/botw-v4";')
 capture=capture.replace('new[]{"D25ColorClarityStage","D29ClarityStage"}','new[]{"D29BotwStage"}')
 capture=capture.replace('case "limited-color-world": return "D25ColorClarityStage";\n   case "kind-to-beginners": return "D29ClarityStage";','case "kind-to-beginners": return "D29BotwStage";')
 capture=capture.replace('Only the two explicitly selected clarity revisions are supported.','Only the explicitly selected D29 botw-v4 revision is supported.')
 capture=capture.replace('MediaRoot+"/"+j.slug+"/clarity-v3"','MediaRoot')
 start=capture.index('  if(j.slug=="limited-color-world") {');end=capture.index('  var request=new RenderPipeline.StandardRequest',start);capture=capture[:start]+capture[end:]
 start=capture.index('  var sceneRoot=');end=capture.index('  var stampPath=',start)
 capture=capture[:start]+'''  var sceneRoot="Assets/VideoScenes/kind-to-beginners/botw-v4/";
  var revision=Path.GetFileName(Path.GetDirectoryName(j.output));
  var saved=sceneRoot+(j.command=="preflight"?"Preflight/":"RenderRevisions/")+revision+"/"+j.cutId+".unity";
'''+capture[end:]
 capture=capture.replace('// D25 captures its grayscale world alone; D29 keeps its single-camera UI.\n   // The failed D25 overlay-stack and two-pass diagnostics are preserved separately.','// This isolated D29 stage uses one camera for world and editorial UI.')
 capture=capture.replace('Editable clarity lesson','Editable BOTW teaching lesson').replace('Clarity stage is not compiled','BOTW stage is not compiled')
 # Never race an older active capture or consume another bridge request.
 start=capture.index(' static bool OtherCapturePending() {');end=capture.index(' static void Poll()',start)
 capture=capture[:start]+''' static bool OtherCapturePending() {
  foreach(var name in new[]{"DesignVisualV2","DesignClarityV3"}) {
   if(File.Exists(Path.Combine(Library,name+".request.json")))return true;
   var path=Path.Combine(Library,name+".status.json");
   if(File.Exists(path)){try{var s=JsonUtility.FromJson<State>(File.ReadAllText(path));if(s.status=="building"||s.status=="capturing")return true;}catch{return true;}}
  }
  return Directory.GetFiles(Library,"*.request",SearchOption.TopDirectoryOnly).Length>0;
 }
'''+capture[end:]
 (DEST/'Editor/DesignBotwCapture.cs').write_text(capture,'utf8')
 (DEST/'DesignBotwBuildVersion.cs').write_text('namespace Yamyam.DesignVisualV2 { public static class DesignBotwBuildVersion { public static string For(string stage) { return "source-not-frozen"; } } }\n','utf8')
 assets=json.loads((OLD/'asset-map.json').read_text('utf8'))
 assets['assets']=[x for x in assets['assets'] if x['key'] in ['hero','heroAlt','table','chair','cup','tree']]
 template=next(x for x in assets['assets'] if x['key']=='cup')
 for key,name in [('cookingPot','CookingPot_1_A_bb23f6ce433b.prefab'),('bowl','Bowl_1_A_d0df87739797.prefab'),('meal','Dish_1_PlateReady_51d78d6ba0c9.prefab')]:
  row=dict(template);row.update(key=key,path='/'.join(template['path'].split('/')[:-1])+'/'+name)
  path=R/'unity/VideoEditing'/row['path'];row['sha256']=sha(path);row['guid']=re.search(r'^guid: (\w+)',Path(str(path)+'.meta').read_text('utf8'),re.M)[1]
  row['runtimeVisualApproval']='pending selected native preflight; same product007 CC0 rights evidence retained'
  assets['assets'].append(row)
 assets['scope']='D29 botw-v4 only; existing verified011 rig/007 kitchen props/023 trees. New cooking props require native pixel verification.'
 (DEST/'asset-map.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n','utf8')
 (H/'native-source-copy-record.json').write_text(json.dumps({'purpose':'New isolated source copies only; no Unity installation or execution','baseOrigin':{'path':str((OLD/'DesignClarityLessonStage.cs').relative_to(R)).replace('\\','/'),'sha256':sha(OLD/'DesignClarityLessonStage.cs')},'bridgeOrigin':{'path':str((OLD/'Editor/DesignClarityCapture.cs').relative_to(R)).replace('\\','/'),'sha256':sha(OLD/'Editor/DesignClarityCapture.cs')},'newRoot':'Assets/VideoScenes/design-d29-botw-v4','savedSceneRoot':'Assets/VideoScenes/kind-to-beginners/botw-v4','requestPrefix':'DesignBotwV4','rawAssetFilesCopied':False,'oldSourcesChanged':False},indent=2)+'\n','utf8')
 print('Isolated source copies prepared. No native deployment/compile/capture performed.')
if __name__=='__main__':main()
