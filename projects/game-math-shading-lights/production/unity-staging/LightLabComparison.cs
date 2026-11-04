using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabStage {
  [SerializeField] Material[] comparisonMaterials;
  [SerializeField] Text[] comparisonLabels;
  [SerializeField] float[] comparisonStrengths,comparisonExponents;
  void BuildGlossReference(Vector3 centre,float diameter,Material material){
   var sample=GameObject.CreatePrimitive(PrimitiveType.Sphere);
   sample.name="Curved material sample · same shader, camera and light";
   sample.transform.SetParent(transform,false);sample.transform.position=centre;
   sample.transform.localScale=Vector3.one*diameter;sample.layer=29;
   var filter=sample.GetComponent<MeshFilter>();var mesh=TeachingMesh(filter.sharedMesh);
   GeneratedObjects.Add(mesh);filter.sharedMesh=mesh;
   sample.GetComponent<Renderer>().sharedMaterial=material;
  }
  void BuildComparison(Font font){
   objectRoot.gameObject.SetActive(false);
   surfaceProbe.gameObject.SetActive(false);
   lampRoot.gameObject.SetActive(false);
   bool shading=Cue.diagram=="shadingComparison";
   comparisonMaterials=new Material[shading?3:9];comparisonLabels=new Text[comparisonMaterials.Length];
   comparisonStrengths=new[]{0f,.35f,.8f};comparisonExponents=new[]{64f,16f,4f};
   Vector3 centre=new Vector3(0,1.35f,0);
   for(int y=0;y<(shading?1:3);y++)for(int x=0;x<3;x++){
    int i=y*3+x;
    var instance=Instantiate(objectRoot.gameObject,transform);instance.name="Same model · strength "+comparisonStrengths[x]+" · exponent "+comparisonExponents[y];
    instance.SetActive(true);
    instance.transform.localScale=objectRoot.localScale*(shading?.75f:.44f);
    var rr=instance.GetComponentsInChildren<Renderer>(true);Bounds bounds=rr[0].bounds;foreach(var r in rr)bounds.Encapsulate(r.bounds);
    Vector3 target=centre+RenderCamera.transform.right*((x-1)*2.65f)+RenderCamera.transform.up*(shading?.2f:(1-y)*1.48f+.15f);
    instance.transform.position+=target-bounds.center-(shading?Vector3.zero:RenderCamera.transform.right*.48f);
    var material=new Material(teaching);GeneratedObjects.Add(material);comparisonMaterials[i]=material;
    foreach(var r in rr){var materials=r.sharedMaterials;for(int m=0;m<materials.Length;m++)materials[m]=material;r.sharedMaterials=materials;}
    if(!shading)BuildGlossReference(target+RenderCamera.transform.right*.5f,.92f,material);
    var screen=RenderCamera.WorldToViewportPoint(target-RenderCamera.transform.up*(shading?1.1f:.67f));
    string label=shading?new[]{"플랫 · 면에서 계산","구로 · 정점에서 계산","퐁 · 픽셀에서 계산"}[x]:"세기 "+comparisonStrengths[x].ToString("0.00")+" · 지수 "+comparisonExponents[y].ToString("0");
    comparisonLabels[i]=Label(font,label,shading?40:36,screen.x*1920-210,(1-screen.y)*1080,440,100,Color.white);
   }
   // All nine variants share direction, camera, diffuse/ambient and geometry.
   // An orthographic view keeps V constant across their different positions.
  }
  void ApplyComparison(float seconds){
   if(comparisonMaterials==null)return;
   objectRoot.gameObject.SetActive(false);surfaceProbe.gameObject.SetActive(false);lampRoot.gameObject.SetActive(false);
   normal.enabled=towardLight.enabled=reflection.enabled=towardViewer.enabled=halfway.enabled=false;
   foreach(var t in vectorLabels)t.gameObject.SetActive(false);
   value.gameObject.SetActive(false);formula.gameObject.SetActive(false);
   int phase=0;if(Cue.stepTimes!=null)for(int i=0;i<Cue.stepTimes.Length;i++)if(seconds>=Cue.stepTimes[i])phase=i;
   for(int i=0;i<comparisonMaterials.Length;i++){
    var material=comparisonMaterials[i];material.CopyPropertiesFromMaterial(teaching);
    if(Cue.diagram=="shadingComparison"){
     material.SetFloat("_ShadingMode",new[]{1,2,0}[i]);
     comparisonLabels[i].color=i==phase%3?Yellow:Color.white;
     continue;
    }
    material.SetColor("_SpecColor",Color.white*comparisonStrengths[i%3]);
    material.SetFloat("_Exponent",comparisonExponents[i/3]);
    comparisonLabels[i].color=phase==0?Color.white:phase==1&&i%3==2?Yellow:phase==2&&i/3==2?Yellow:phase>=3&&i%3==0?Yellow:Color.white;
   }
  }
 }
}
