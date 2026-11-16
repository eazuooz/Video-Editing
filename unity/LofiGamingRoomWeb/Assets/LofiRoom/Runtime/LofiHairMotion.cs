using UnityEngine;

namespace Yamyam.LofiRoom
{
    // Constrained secondary motion; the imported humanoid rig stays intact.
    public sealed class LofiHairMotion : MonoBehaviour
    {
        public Transform head;
        public SkinnedMeshRenderer skin;
        public bool enabledMotion=true;
        public float measuredOffset,maximumObservedOffset,maximumLengthError;
        public int collisionCorrections;
        const int Count=5;
        const float Length=.060f,Step=1f/120f;
        readonly Vector3[] position=new Vector3[Count],previous=new Vector3[Count];
        MaterialPropertyBlock properties;
        Vector3 lastAnchor;
        bool initialized;
        float accumulator;
        void Awake(){properties=new MaterialPropertyBlock();}
        Vector3 Rest(int i)=>head.position-head.forward*.105f+head.up*(.075f-i*Length);
        void ResetChain()
        {
            for(int i=0;i<Count;i++)position[i]=previous[i]=Rest(i);
            lastAnchor=Rest(0);accumulator=0;initialized=true;
        }
        void LateUpdate()
        {
            if(!head || !skin)return;
            properties??=new MaterialPropertyBlock();
            Vector3 anchor=Rest(0);
            if(!initialized || Vector3.Distance(anchor,lastAnchor)>.35f)ResetChain();
            accumulator+=Mathf.Min(Time.deltaTime,.066f);
            int substeps=0;
            while(accumulator>=Step && substeps++<8)
            {
                position[0]=previous[0]=anchor;
                for(int i=1;i<Count;i++)
                {
                    Vector3 p=position[i],inertia=(p-previous[i])*.974f;
                    float t=i/(float)(Count-1);
                    Vector3 breeze=new Vector3(Mathf.Sin(Time.time*1.15f+i*.42f),.08f*Mathf.Sin(Time.time*.8f),Mathf.Cos(Time.time*.93f+i*.3f))*.65f;
                    Vector3 acceleration=(Rest(i)-p)*(125f-45*t)+breeze*t+Vector3.down*.12f;
                    position[i]=p+inertia+acceleration*Step*Step;previous[i]=p;
                }
                for(int iteration=0;iteration<6;iteration++)
                {
                    position[0]=anchor;
                    for(int i=1;i<Count;i++)
                    {
                        Vector3 direction=(position[i]-position[i-1]).normalized;
                        direction=Vector3.RotateTowards(-head.up,direction,32*Mathf.Deg2Rad,0);
                        position[i]=position[i-1]+direction*Length;
                        Collide(i,head.position-head.forward*.012f+head.up*.025f,head,.070f,.10f,.074f);
                        Collide(i,head.position-head.up*.245f+head.forward*.015f,head,.105f,.075f,.080f);
                    }
                }
                accumulator-=Step;
            }
            measuredOffset=0;maximumLengthError=0;
            skin.GetPropertyBlock(properties);
            for(int i=1;i<Count;i++)
            {
                Vector3 offset=Vector3.ClampMagnitude(position[i]-Rest(i),.085f);
                measuredOffset=Mathf.Max(measuredOffset,offset.magnitude);
                maximumLengthError=Mathf.Max(maximumLengthError,Mathf.Abs(Vector3.Distance(position[i],position[i-1])-Length));
                properties.SetVector("_HairOffset"+i,enabledMotion?offset:Vector3.zero);
            }
            maximumObservedOffset=Mathf.Max(maximumObservedOffset,measuredOffset);
            properties.SetVector("_HairMotion",enabledMotion?position[Count-1]-Rest(Count-1):Vector3.zero);
            skin.SetPropertyBlock(properties);lastAnchor=anchor;
        }
        void Collide(int i,Vector3 center,Transform basis,float x,float y,float z)
        {
            Vector3 d=position[i]-center;
            Vector3 local=new Vector3(Vector3.Dot(d,basis.right)/x,Vector3.Dot(d,basis.up)/y,Vector3.Dot(d,basis.forward)/z);
            float length=local.magnitude;
            if(length<1 && length>.0001f)
            {
                local/=length;position[i]=center+basis.right*local.x*x+basis.up*local.y*y+basis.forward*local.z*z;
                collisionCorrections++;
            }
        }
        void OnDisable()
        {
            if(!skin || properties==null)return;
            skin.GetPropertyBlock(properties);
            for(int i=1;i<Count;i++)properties.SetVector("_HairOffset"+i,Vector3.zero);
            properties.SetVector("_HairMotion",Vector3.zero);skin.SetPropertyBlock(properties);
        }
    }
}
