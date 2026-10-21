using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.Rendering;
using Object=UnityEngine.Object;
namespace YamyamCoding.Shorts.NormalMap.Editor {
public static partial class NormalMapCapture {
 static GameObject spatialGrid;static Transform[] shafts,heads;static Mesh coneMesh;
 static Material gridWhite,gridGreen,gridGold,bracketMaterial;static LineRenderer rightAngle,surfaceTangent;
 static float activeGridArrowLength=GridArrowLength;
 static Vector3[] rightAngleWorld;
 static Material GridMaterial(string name,string colour){var m=Mat(name,Hex(colour));m.SetFloat("_NormalStrength",0);m.SetFloat("_OutputMode",0);m.SetFloat("_Ambient",.42f);m.SetVector("_LightDir",new Vector3(-.3f,.8f,-.7f).normalized);return m;}
 static Mesh GridCone(){
  string path=Root+"/Meshes/GridArrowCone.asset";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(mesh)return mesh;
  mesh=new Mesh{name="Native normal arrow cone"};var v=new List<Vector3>();var triangles=new List<int>();
  for(int i=0;i<12;i++){float a=i*Mathf.PI*2/12,b=(i+1)*Mathf.PI*2/12;var p=new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));var q=new Vector3(Mathf.Cos(b),0,Mathf.Sin(b));int k=v.Count;v.AddRange(new[]{p,Vector3.up,q,Vector3.zero,p,q});triangles.AddRange(new[]{k,k+1,k+2,k+3,k+4,k+5});}
  mesh.SetVertices(v);mesh.SetTriangles(triangles,0);mesh.RecalculateNormals();mesh.tangents=mesh.normals.Select(n=>{var t=Vector3.Cross(n,Mathf.Abs(n.y)>.99f?Vector3.right:Vector3.up).normalized;return new Vector4(t.x,t.y,t.z,1);}).ToArray();mesh.uv=Enumerable.Repeat(Vector2.zero,v.Count).ToArray();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,path);return mesh;
 }
 static LineRenderer WorldLine(string name,float width){var g=new GameObject(name);g.layer=8;g.transform.SetParent(spatialGrid.transform);var line=g.AddComponent<LineRenderer>();line.sharedMaterial=bracketMaterial;line.useWorldSpace=true;line.startWidth=width;line.endWidth=width;line.numCapVertices=2;line.shadowCastingMode=ShadowCastingMode.Off;line.receiveShadows=false;return line;}
 static void MakeSpatialGrid(){
  if(spatialGrid)return;coneMesh=GridCone();gridWhite=GridMaterial("GridArrowWhite","#FFFFFF");gridGreen=GridMaterial("GridArrowGreen","#92DF9C");gridGold=GridMaterial("GridArrowGold","#FFD25A");
  string mp=Root+"/Materials/GridRightAngle.mat";bracketMaterial=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!bracketMaterial){bracketMaterial=new Material(Shader.Find("Unlit/Color"));bracketMaterial.color=Hex("#FFD25A");AssetDatabase.CreateAsset(bracketMaterial,mp);}
  spatialGrid=new GameObject("63 actual GPU normals — native3D display arrows");spatialGrid.layer=8;shafts=new Transform[63];heads=new Transform[63];
  for(int i=0;i<63;i++){
   var shaft=GameObject.CreatePrimitive(PrimitiveType.Cylinder);shaft.name="Normal shaft "+i;shaft.layer=8;shaft.transform.SetParent(spatialGrid.transform);Object.DestroyImmediate(shaft.GetComponent<Collider>());shafts[i]=shaft.transform;
   var head=new GameObject("Normal cone "+i);head.layer=8;head.transform.SetParent(spatialGrid.transform);head.AddComponent<MeshFilter>().sharedMesh=coneMesh;head.AddComponent<MeshRenderer>();heads[i]=head.transform;
   foreach(var obj in new[]{shaft,head}){var renderer=obj.GetComponent<Renderer>();renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;}
  }
  rightAngle=WorldLine("Actual tangent-normal right angle",.017f);surfaceTangent=WorldLine("Reference tangent on the surface",.012f);
 }
 static void PlaceSpatialGrid(Section s,float seconds){
  float t=s.rotationSeconds>0?Mathf.Clamp01(seconds/s.rotationSeconds):1;t=t*t*(3-2*t);
  wall.transform.rotation=Quaternion.Euler(0,Mathf.Lerp(s.wallYawFrom,s.wallYawTo,t),0);
  cam.cullingMask=1<<8;cam.orthographicSize=2.65f;var focus=wall.transform.position;cam.transform.position=focus+new Vector3(0,s.cameraElevation,-6);cam.transform.LookAt(focus);activeGridArrowLength=s.arrowLength;
 }
 static void ShowSpatialGrid(GridSample[] samples,Probe probe,float seconds){
  MakeSpatialGrid();spatialGrid.SetActive(true);bool flat=demo.normalStrength<.00001f;float length=activeGridArrowLength;
  for(int i=0;i<samples.Length;i++){
   var p=samples[i].worldPoint;var n=samples[i].gpuShadingNormal.normalized;var rotation=Quaternion.FromToRotation(Vector3.up,n);float headLength=.13f;bool selected=i==31;var material=selected&&flat?gridGold:flat?gridWhite:gridGreen;
   shafts[i].position=p+n*(length-headLength)*.5f;shafts[i].rotation=rotation;shafts[i].localScale=new Vector3(.025f,(length-headLength)*.5f,.025f);heads[i].position=p+n*(length-headLength);heads[i].rotation=rotation;heads[i].localScale=new Vector3(.055f,headLength,.055f);
   shafts[i].GetComponent<Renderer>().sharedMaterial=material;heads[i].GetComponent<Renderer>().sharedMaterial=material;bool visible=seconds>=(i/9)*.055f;shafts[i].gameObject.SetActive(visible);heads[i].gameObject.SetActive(visible);
  }
  var anchor=samples[31].worldPoint;var tangent=probe.tangent.normalized;var normal=probe.geometryNormal.normalized;
  rightAngleWorld=new[]{anchor+tangent*.22f,anchor+(tangent+normal)*.22f,anchor+normal*.22f};rightAngle.positionCount=3;rightAngle.SetPositions(rightAngleWorld);surfaceTangent.positionCount=2;surfaceTangent.SetPositions(new[]{anchor-tangent*.05f,anchor+tangent*.38f});rightAngle.enabled=flat;surfaceTangent.enabled=flat;
 }
 static void SaveSpatialVariant(string name,float strength){
  var originalWallMaterial=wallMat;string materialPath=Root+"/Materials/"+name+"-Wall.mat";
  var sceneMaterial=AssetDatabase.LoadAssetAtPath<Material>(materialPath);if(!sceneMaterial){sceneMaterial=new Material(originalWallMaterial);AssetDatabase.CreateAsset(sceneMaterial,materialPath);}else sceneMaterial.CopyPropertiesFromMaterial(originalWallMaterial);
  wallMat=sceneMaterial;demo.wallMaterial=sceneMaterial;wall.GetComponent<Renderer>().sharedMaterial=sceneMaterial;
  if(spatialGrid)spatialGrid.SetActive(false);demo.normalStrength=strength;demo.Apply();wallMat.SetFloat("_OutputMode",0);
  PlaceSpatialGrid(new Section{wallYawFrom=-58,wallYawTo=-58,cameraElevation=2.2f,arrowLength=.58f},4);
  var probe=ReadProbe(name,true);wallMat.SetFloat("_OutputMode",0);ShowSpatialGrid(lastNormalGrid,probe,4);
  var snapshot=wall.AddComponent<NormalMapGridSnapshot>();snapshot.provenance="Saved actual GPU-sampled3Darrow snapshot; recapture after changing wall/material. 9x7 representativepixels, displaylength0.58units.";snapshot.sampledNormalStrength=strength;snapshot.displayLength=.58f;snapshot.showSceneGizmos=false;snapshot.worldPoints=lastNormalGrid.Select(x=>x.worldPoint).ToArray();snapshot.worldNormals=lastNormalGrid.Select(x=>x.gpuShadingNormal).ToArray();
  demo.animateLight=false;cam.targetTexture=null;cam.enabled=true;EditorUtility.SetDirty(sceneMaterial);AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Root+"/Scenes/"+name+".unity");cam.enabled=false;cam.targetTexture=rt;Object.DestroyImmediate(snapshot);
  wallMat=originalWallMaterial;demo.wallMaterial=originalWallMaterial;wall.GetComponent<Renderer>().sharedMaterial=originalWallMaterial;
 }
}
}
