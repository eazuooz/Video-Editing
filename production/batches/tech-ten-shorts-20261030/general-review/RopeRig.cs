using UnityEngine;

// A teaching rig. Both routes share a fixed anchor and a moving winch.
public sealed class RopeRig : MonoBehaviour
{
    public Transform jeep, winchArm;
    public LineRenderer rope, intersection;
    public GameObject cornerMark;
    public const float HalfWidth = 0.95f, HalfDepth = 0.85f;
    public Vector3 Anchor { get; private set; }
    public Vector3 End { get; private set; }
    public Vector3 Contact { get; private set; }
    public bool Wrapped { get; private set; }
    public float Sag { get; private set; }
    public bool Intersects { get; private set; }
    static float SagForLength(float span,float ropeLength)
    {
        float low=0,high=1.5f;
        for(int step=0;step<18;step++){
            float sag=(low+high)/2, length=0, oldY=0;
            for(int i=1;i<=40;i++){
                float u=i/40f,y=-4*u*(1-u)*sag;
                length+=Mathf.Sqrt(span*span/1600+(y-oldY)*(y-oldY));oldY=y;
            }
            if(length<ropeLength)low=sag;else high=sag;
        }
        return (high+low)/2;
    }
    static bool ClipAxis(float origin, float step, float extent, ref float enter, ref float leave)
    {
        if (Mathf.Abs(step) < 0.0001f) return Mathf.Abs(origin) <= extent;
        float a = (-extent - origin) / step, b = (extent - origin) / step;
        enter = Mathf.Max(enter, Mathf.Min(a,b));
        leave = Mathf.Min(leave, Mathf.Max(a,b));
        return enter < leave;
    }
    public void Pose(string mode, float progress)
    {
        progress = Mathf.SmoothStep(0f,1f,progress);
        bool side = mode == "side";
        Anchor = new Vector3(side?-2.15f:-3.65f,.96f,side ? 0f : 1.50f);
        End = new Vector3(side ? Mathf.Lerp(.55f,1f,progress) : 3.4f,.96f,
                          side ? 0f : Mathf.Lerp(2.1f,-1.85f,progress));
        jeep.position = End + new Vector3(.48f,-.95f,0);
        Vector3 bumper=End+new Vector3(.22f,-.52f,0);
        winchArm.position=(End+bumper)/2;winchArm.up=(End-bumper).normalized;
        winchArm.localScale=new Vector3(.12f,(End-bumper).magnitude,.12f);
        Sag = side ? SagForLength(End.x-Anchor.x,3.15f) : 0;
        Vector3 span = End - Anchor;
        float enter=0f,leave=1f;
        Intersects = !side && ClipAxis(Anchor.x,span.x,HalfWidth,ref enter,ref leave)
                           && ClipAxis(Anchor.z,span.z,HalfDepth,ref enter,ref leave);
        Wrapped = mode == "wrapped" && Intersects;
        Contact = new Vector3(HalfWidth+.013f,.96f,HalfDepth+.013f);
        cornerMark.SetActive(Wrapped);cornerMark.transform.position=Contact;
        intersection.gameObject.SetActive(Intersects && !Wrapped);
        if (Intersects && !Wrapped) {
            intersection.SetPosition(0,Anchor+enter*span+Vector3.up*.06f);
            intersection.SetPosition(1,Anchor+leave*span+Vector3.up*.06f);
        }
        if (side) {
            rope.positionCount=41;
            for(int i=0;i<=40;i++){float u=i/40f;rope.SetPosition(i,Anchor+u*span-Vector3.up*(4*u*(1-u)*Sag));}
        } else {
            rope.positionCount=Wrapped?3:2;rope.SetPosition(0,Anchor);
            if(Wrapped)rope.SetPosition(1,Contact);
            rope.SetPosition(rope.positionCount-1,End);
        }
    }
    void Update(){Pose("wrapped",Mathf.PingPong(Time.time/3,1));}
}
