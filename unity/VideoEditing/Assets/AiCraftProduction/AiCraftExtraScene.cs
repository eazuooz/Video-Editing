using UnityEngine;

// Authored illustrations: UV sampling, a small interaction and tool control.
// These are not commercial-game footage, force measurements or AI benchmarks.
[ExecuteAlways]
public class AiCraftExtraScene : MonoBehaviour
{
    public Transform subject, movingPart, reward, door;
    public Renderer uvBody, uvPlane;
    public AiCraftLessonScene.State ApplyFrame(int frame,AiCraftLessonScene lesson)
    {
        float t=frame/(float)lesson.captureFps;
        var state=new AiCraftLessonScene.State{frame=frame,scene=lesson.sceneId,scenario="authored-illustration",result="illustration"};
        if(lesson.sceneId=="06"){
            subject.localRotation=Quaternion.Euler(0,Mathf.Lerp(-25,35,Mathf.Clamp01(t/12)),0);
            var props=new MaterialPropertyBlock();props.SetVector("_Highlight",new Vector4(Mathf.Floor(Mathf.Clamp01(t/18)*7),3,0,0));
            uvBody.SetPropertyBlock(props);uvPlane.SetPropertyBlock(props);
            state.scenario="actual-mesh-uv-sampling";state.result="same-uv-cell-on-surface-and-flat-map";
        }else if(lesson.sceneId=="14"||lesson.sceneId=="02"){
            // First reach the locked door, return for the key, then try again.
            float x=t<5?Mathf.Lerp(-3.8f,2.3f,Mathf.Clamp01((t-1)/3)):t<9?Mathf.Lerp(2.3f,-.8f,(t-5)/4):Mathf.Lerp(-.8f,4.4f,Mathf.Clamp01((t-10)/6));
            subject.localPosition=new Vector3(x,-.8f+Mathf.Abs(Mathf.Sin(t*8))*.05f,0);
            bool collected=t>=9;reward.gameObject.SetActive(!collected);door.localPosition=new Vector3(3.6f,-.25f+Mathf.Clamp01((t-13)/1.2f)*1.8f,0);
            state.scenario="locked-door-key-retry";state.result=t<4?"approaching-door":t<9?"locked-key-required":t<13?"key-collected":"door-open";state.items=collected?1:0;
        }else if(lesson.sceneId=="08"){
            subject.localRotation=Quaternion.Euler(0,Mathf.Lerp(-25,35,Mathf.Clamp01(t/16)),0);state.scenario="authored-furniture-detail";
        }else if(lesson.sceneId=="26"){
            float part=t,drive=Mathf.Clamp01((part-1)/4);
            movingPart.localRotation=Quaternion.Euler(drive*1080,0,90);
            reward.localPosition=new Vector3(0,1.4f-drive*1.115f,0);
            subject.localPosition=new Vector3(-.15f,2f-drive*1.115f,0);
            state.scenario="tool-stop-timing-illustration";state.result=part<1?"position-tool":part<5?"drive-screw":"stop-at-seat";
        }
        lesson.state=state;return state;
    }
}
