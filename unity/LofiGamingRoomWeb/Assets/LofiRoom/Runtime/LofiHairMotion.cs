using UnityEngine;

namespace Yamyam.LofiRoom
{
    // Secondary motion only: preserves the imported humanoid animation and rig.
    public sealed class LofiHairMotion : MonoBehaviour
    {
        public Transform head;
        public SkinnedMeshRenderer skin;
        public bool enabledMotion=true;
        public float measuredOffset;
        Vector3 tip,velocity;
        bool initialized;
        MaterialPropertyBlock properties;
        void Awake(){properties=new MaterialPropertyBlock();}
        void LateUpdate()
        {
            if(!head || !skin)return;
            properties??=new MaterialPropertyBlock();
            Vector3 anchor=head.position-head.forward*.12f;
            if(!initialized){tip=anchor;initialized=true;}
            float dt=Mathf.Min(Time.deltaTime,.025f);
            Vector3 wind=new Vector3(Mathf.Sin(Time.time*1.35f)*.012f,Mathf.Sin(Time.time*1.7f)*.004f,Mathf.Cos(Time.time*1.2f)*.009f);
            velocity+=(anchor+wind-tip)*105*dt;
            velocity*=Mathf.Exp(-11*dt);tip+=velocity*dt;
            Vector3 offset=Vector3.ClampMagnitude(tip-anchor,.045f);
            measuredOffset=enabledMotion?offset.magnitude:0;
            skin.GetPropertyBlock(properties);properties.SetVector("_HairMotion",enabledMotion?offset:Vector3.zero);skin.SetPropertyBlock(properties);
        }
        void OnDisable(){if(skin && properties!=null){skin.GetPropertyBlock(properties);properties.SetVector("_HairMotion",Vector3.zero);skin.SetPropertyBlock(properties);}}
    }
}
