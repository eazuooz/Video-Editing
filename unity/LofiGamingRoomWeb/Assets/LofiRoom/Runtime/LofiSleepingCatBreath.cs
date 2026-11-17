using UnityEngine;
namespace Yamyam.LofiRoom
{
    // Localized motion on the actual Tripo mesh. Model-specific prefab-space
    // masks preserve the face, feet and UVs; this is not a general cat rig.
    public sealed class LofiSleepingCatBreath:MonoBehaviour
    {
        public float breathingAmplitude=.005f,tailAmplitude=.018f;
        Mesh mesh;Vector3[] restRoot,output;float[] chest,tail;Matrix4x4 toMesh;
        static readonly Vector3[] TailCurve={new(.31f,.065f,-.15f),new(.19f,.06f,-.265f),new(-.055f,.055f,-.26f),new(-.21f,.055f,-.16f),new(-.27f,.055f,-.035f)};
        void Awake()
        {
            var filter=GetComponentInChildren<MeshFilter>();if(!filter||!filter.sharedMesh||!filter.sharedMesh.isReadable){enabled=false;return;}
            mesh=Instantiate(filter.sharedMesh);mesh.name="Tripo calico - localized breathing and tail";mesh.MarkDynamic();filter.sharedMesh=mesh;
            var toRoot=transform.worldToLocalMatrix*filter.transform.localToWorldMatrix;toMesh=filter.transform.worldToLocalMatrix*transform.localToWorldMatrix;
            output=mesh.vertices;restRoot=new Vector3[output.Length];chest=new float[output.Length];tail=new float[output.Length];
            for(int i=0;i<output.Length;i++)
            {
                Vector3 p=restRoot[i]=toRoot.MultiplyPoint3x4(output[i]);float dx=(p.x-.12f)/.26f,dz=(p.z-.08f)/.28f;
                chest[i]=Mathf.Exp(-(dx*dx+dz*dz)*1.5f)*Mathf.SmoothStep(0,1,Mathf.InverseLerp(.06f,.17f,p.y))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(-.13f,-.035f,p.x));
                float best=100,along=0;
                for(int s=0;s<TailCurve.Length-1;s++){Vector3 d=TailCurve[s+1]-TailCurve[s];float u=Mathf.Clamp01(Vector3.Dot(p-TailCurve[s],d)/d.sqrMagnitude);float distance=(p-(TailCurve[s]+d*u)).sqrMagnitude;if(distance<best){best=distance;along=(s+u)/(TailCurve.Length-1);}}
                float radial=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(.028f,.067f,Mathf.Sqrt(best)));
                tail[i]=radial*Mathf.SmoothStep(0,1,Mathf.InverseLerp(.24f,.9f,along))*(1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(.105f,.14f,p.y)));
            }
            var bounds=mesh.bounds;bounds.Expand(.12f);mesh.bounds=bounds;
        }
        void Update(){SampleMotion(Time.time);}
        public void SampleMotion(float time)
        {
            float breath=.5f+.5f*Mathf.Sin(time*(2*Mathf.PI/4.8f));float drift=.5f+.5f*Mathf.Sin(time*(2*Mathf.PI/7.5f));float twitch=Mathf.Pow(Mathf.Max(0,Mathf.Sin(time*(2*Mathf.PI/17f))),12)*Mathf.Sin(time*4.2f)*.12f;
            for(int i=0;i<output.Length;i++)
            {
                Vector3 p=restRoot[i];float b=chest[i]*breath;p+=new Vector3((p.x-.12f)*.008f*b,breathingAmplitude*b,(p.z-.08f)*.006f*b);
                // The tip moves out from the chin instead of through the face.
                float w=tail[i];p+=new Vector3(-.003f*drift*w,.003f*drift*w,-tailAmplitude*(drift+twitch)*w);output[i]=toMesh.MultiplyPoint3x4(p);
            }
            mesh.vertices=output;
        }
        void OnDestroy(){if(mesh)Destroy(mesh);}
    }
}
