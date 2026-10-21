using UnityEngine;

namespace YamyamCoding.Shorts.NormalMap {
 // Editable Scene-view evidence, not an invented live normal detector. The
 // capture editor fills these vectors from one actual ARGBFloat shader pass.
 public sealed class NormalMapGridSnapshot : MonoBehaviour {
  [TextArea] public string provenance="Representative 9x7 GPU pixel samples. Stored snapshot, not every pixel and not automatically resampled after material changes.";
  public int columns=9,rows=7;
  public float sampledNormalStrength=1,displayLength=.34f;
  public Vector3 sampledLightDirection;
  public Vector3[]worldPoints,worldNormals;
  public bool showSceneGizmos=true;
  void OnDrawGizmos(){
   if(!showSceneGizmos||worldPoints==null||worldNormals==null)return;
   Gizmos.color=sampledNormalStrength<.5f?Color.white:new Color(.30f,1,.56f);
   for(int i=0;i<Mathf.Min(worldPoints.Length,worldNormals.Length);i++){
    var direction=worldNormals[i].normalized;var end=worldPoints[i]+direction*displayLength;
    var side=Vector3.Cross(direction,Vector3.up);if(side.sqrMagnitude<.01f)side=Vector3.Cross(direction,Vector3.right);side=side.normalized*displayLength*.16f;
    Gizmos.DrawLine(worldPoints[i],end);Gizmos.DrawLine(end,end-direction*displayLength*.25f+side);Gizmos.DrawLine(end,end-direction*displayLength*.25f-side);
   }
  }
 }
}
