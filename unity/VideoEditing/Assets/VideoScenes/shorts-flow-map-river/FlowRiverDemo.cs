using UnityEngine;
namespace YamyamCoding.FlowShort {
 [ExecuteAlways] public class FlowRiverDemo:MonoBehaviour {
  public Material water;public float clock;public bool animate=true;public float useFlow=1,displayMap,blendPhases=1,longStretch;
  void Update(){if(animate&&Application.isPlaying)clock+=Time.deltaTime;Apply();}
  public void Apply(){if(!water)return;water.SetFloat("_Clock",clock);water.SetFloat("_UseFlow",useFlow);water.SetFloat("_Display",displayMap);water.SetFloat("_Blend",blendPhases);water.SetFloat("_Long",longStretch);}
 }
}
