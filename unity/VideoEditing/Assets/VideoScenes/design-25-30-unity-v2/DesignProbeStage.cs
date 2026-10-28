using UnityEngine;
namespace Yamyam.DesignVisualV2 {
public class DesignProbeStage:DesignLessonStage {
 GameObject a,b;
 public override void Build(){Title("장면·동작 확인");a=Actor("Player",new Vector3(-4,0,0));b=Actor("Opponent",new Vector3(-1,0,0),true);Asset("chest",new Vector3(2,0,0),1.5f);Asset("car",new Vector3(5,0,0),1.4f,35);Label("실제 리그 동작 · 소품 식별",960,820,44,White,1500);}
 public override void Apply(float t){Pose(a,"Walk_A",t);Pose(b,"Fight_Punch_A",t);}
}
}
