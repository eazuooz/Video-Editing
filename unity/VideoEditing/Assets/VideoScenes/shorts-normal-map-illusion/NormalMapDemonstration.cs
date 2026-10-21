using UnityEngine;
namespace YamyamCoding.Shorts.NormalMap {
 [ExecuteAlways] public class NormalMapDemonstration:MonoBehaviour {
  public Material wallMaterial,spriteMaterial,sourceMaterial;
  public Light movingLight;
  [Range(0,1)]public float normalStrength=1;
  public bool animateLight=true;
  [Range(-75,75)]public float lightAngle=40;
  public float lightSpeed=25;
  public void Apply(){
   if(!movingLight)return;
   var direction=new Vector3(Mathf.Sin(lightAngle*Mathf.Deg2Rad),.3f,-Mathf.Cos(lightAngle*Mathf.Deg2Rad)).normalized;
   movingLight.transform.rotation=Quaternion.LookRotation(-direction,Vector3.up);
   foreach(var material in new[]{wallMaterial,spriteMaterial})if(material){material.SetFloat("_NormalStrength",normalStrength);material.SetVector("_LightDir",-movingLight.transform.forward);}
   if(sourceMaterial)sourceMaterial.SetVector("_LightDir",-movingLight.transform.forward);
  }
  void Update(){if(animateLight)lightAngle=Mathf.Sin(Time.time*lightSpeed*Mathf.Deg2Rad)*65;Apply();}
  void OnValidate(){Apply();}
 }
}
