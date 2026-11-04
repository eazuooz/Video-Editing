using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabStage {
  [SerializeField] Material[] comparisonMaterials;
  [SerializeField] Text[] comparisonLabels;
  [SerializeField] float[] comparisonStrengths,comparisonExponents;
  void BuildComparison(Font font){
   objectRoot.gameObject.SetActive(false);
   surfaceProbe.gameObject.SetActive(false);
   lampRoot.gameObject.SetActive(false);
   comparisonMaterials=new Material[9];comparisonLabels=new Text[9];
   comparisonStrengths=new[]{0f,.35f,.8f};comparisonExponents=new[]{64f,16f,4f};
   Vector3 centre=new Vector3(0,1.35f,0);
   for(int y=0;y<3;y++)for(int x=0;x<3;x++){
    int i=y*3+x;
    var instance=Instantiate(objectRoot.gameObject,transform);instance.name="Same model · strength "+comparisonStrengths[x]+" · exponent "+comparisonExponents[y];
    instance.SetActive(true);
    instance.transform.localScale=objectRoot.localScale*.44f;
    var rr=instance.GetComponentsInChildren<Renderer>(true);Bounds bounds=rr[0].bounds;foreach(var r in rr)bounds.Encapsulate(r.bounds);
    Vector3 target=centre+RenderCamera.transform.right*((x-1)*2.65f)+RenderCamera.transform.up*((1-y)*1.48f+.15f);
    instance.transform.position+=target-bounds.center;
    var material=new Material(teaching);GeneratedObjects.Add(material);comparisonMaterials[i]=material;
    foreach(var r in rr){var materials=r.sharedMaterials;for(int m=0;m<materials.Length;m++)materials[m]=material;r.sharedMaterials=materials;}
    var screen=RenderCamera.WorldToViewportPoint(target-RenderCamera.transform.up*.67f);
    comparisonLabels[i]=Label(font,"세기 "+comparisonStrengths[x].ToString("0.00")+" · 지수 "+comparisonExponents[y].ToString("0"),36,screen.x*1920-190,(1-screen.y)*1080,400,52,Color.white);
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
   for(int i=0;i<9;i++){
    var material=comparisonMaterials[i];material.CopyPropertiesFromMaterial(teaching);
    material.SetColor("_SpecColor",Color.white*comparisonStrengths[i%3]);
    material.SetFloat("_Exponent",comparisonExponents[i/3]);
    comparisonLabels[i].color=phase==0?Color.white:phase==1&&i%3==2?Yellow:phase==2&&i/3==2?Yellow:phase>=3&&i%3==0?Yellow:Color.white;
   }
  }
 }
}
