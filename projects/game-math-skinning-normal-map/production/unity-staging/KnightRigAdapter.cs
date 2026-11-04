using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.SkinNormal {
    [Serializable] public class RigProbe {
        public string rendererName;public int vertexIndex;public string[] bones;public float[] weights;
        public Vector3 bindPosition;public Vector3[] proposalsWorld;public Vector3 weightedWorld,bakedWorld;
        public float cpuVsBakeWorldError;
    }
    // Adapts an instance; no changes to imported FBX, meshes, materials or clips.
    public sealed class KnightRigAdapter {
        readonly GameObject hero;readonly Transform[] transforms;readonly Vector3[] positions,scales;readonly Quaternion[] rotations;
        readonly SkinnedMeshRenderer[] renderers;readonly Dictionary<string,AnimationClip> clips=new Dictionary<string,AnimationClip>();
        SkinnedMeshRenderer probeRenderer;Mesh bakeMesh;int probeIndex=-1;BoneWeight probeWeight;
        public GameObject Instance=>hero;
        public KnightRigAdapter(GameObject instance,AnimationClip[] availableClips){
            if(instance==null)throw new ArgumentNullException(nameof(instance));hero=instance;
            foreach(var a in hero.GetComponentsInChildren<Animator>(true))a.enabled=false;
            foreach(var a in hero.GetComponentsInChildren<Animation>(true))a.enabled=false;
            foreach(var clip in availableClips??Array.Empty<AnimationClip>())if(clip!=null&&!clip.name.StartsWith("__preview__"))clips[clip.name]=clip;
            transforms=hero.GetComponentsInChildren<Transform>(true);positions=new Vector3[transforms.Length];rotations=new Quaternion[transforms.Length];scales=new Vector3[transforms.Length];
            for(int i=0;i<transforms.Length;i++){positions[i]=transforms[i].localPosition;rotations[i]=transforms[i].localRotation;scales[i]=transforms[i].localScale;}
            renderers=hero.GetComponentsInChildren<SkinnedMeshRenderer>(true);if(renderers.Length==0)throw new InvalidOperationException("Knight has no imported skinned renderer.");
            foreach(var r in renderers)r.updateWhenOffscreen=true;
        }
        public void Restore(){for(int i=1;i<transforms.Length;i++){transforms[i].localPosition=positions[i];transforms[i].localRotation=rotations[i];transforms[i].localScale=scales[i];}}
        public Transform Bone(string exactName){foreach(var t in transforms)if(t.name==exactName)return t;throw new InvalidOperationException("Imported rig bone missing: "+exactName);}
        public void Sample(string exactClip,float clipSeconds){
            if(!clips.TryGetValue(exactClip,out var clip))throw new InvalidOperationException("Required imported clip missing: "+exactClip);
            if(clipSeconds<0||clipSeconds>clip.length+.0001f)throw new ArgumentOutOfRangeException(nameof(clipSeconds),"Choose a finite observed clip interval; never loop or clamp silently.");
            Restore();Vector3 p=hero.transform.localPosition,s=hero.transform.localScale;Quaternion q=hero.transform.localRotation;
            clip.SampleAnimation(hero,Mathf.Min(clipSeconds,clip.length));
            hero.transform.localPosition=p;hero.transform.localRotation=q;hero.transform.localScale=s;
        }
        public float ClipLength(string exactClip){if(!clips.TryGetValue(exactClip,out var c))throw new InvalidOperationException("Clip missing: "+exactClip);return c.length;}
        public void RotateLocalBone(string name,Vector3 localAxis,float degrees){var b=Bone(name);b.localRotation=b.localRotation*Quaternion.AngleAxis(degrees,localAxis.normalized);}
        static float W(BoneWeight w,int i)=>i==0?w.weight0:i==1?w.weight1:i==2?w.weight2:w.weight3;
        static int I(BoneWeight w,int i)=>i==0?w.boneIndex0:i==1?w.boneIndex1:i==2?w.boneIndex2:w.boneIndex3;
        public void SelectActualArmProbe(){
            float best=-1;foreach(var r in renderers){if(!r.gameObject.activeInHierarchy)continue;Mesh m=r.sharedMesh;if(m==null||!m.isReadable)throw new InvalidOperationException("Readable mesh required in the isolated import only: "+r.name);var weights=m.boneWeights;if(weights.Length!=m.vertexCount)throw new InvalidOperationException("Four-weight layout unavailable: "+r.name);if(m.bindposes.Length!=r.bones.Length)throw new InvalidOperationException("Bindpose/bone array mismatch.");
                for(int v=0;v<weights.Length;v++){float upper=0,lower=0,total=0;int positive=0;for(int k=0;k<4;k++){float w=W(weights[v],k);if(w<0)throw new InvalidOperationException("Negative imported weight.");total+=w;if(w==0)continue;positive++;int bi=I(weights[v],k);if(bi<0||bi>=r.bones.Length)throw new InvalidOperationException("Invalid bone index.");string name=r.bones[bi].name;if(name=="upperarm.l")upper+=w;if(name=="lowerarm.l")lower+=w;}
                    if(Mathf.Abs(total-1)>.002f)throw new InvalidOperationException("Imported weights do not sum to one.");
                    float score=Mathf.Min(upper,lower);if(positive>=2&&score>best&&score>.05f){best=score;probeRenderer=r;probeIndex=v;probeWeight=weights[v];}
                }
            }
            if(probeIndex<0)throw new InvalidOperationException("No verified upper/lower-arm blended vertex; do not label a rigid vertex as blended.");
            bakeMesh=new Mesh{name="KnightProbeBake_ReadOnlySource"};
        }
        public RigProbe Probe(bool compareActualBake){
            if(probeIndex<0)throw new InvalidOperationException("SelectActualArmProbe first.");var r=probeRenderer;var m=r.sharedMesh;Vector3 p=m.vertices[probeIndex],weighted=Vector3.zero;var names=new List<string>();var weights=new List<float>();var proposals=new List<Vector3>();
            for(int k=0;k<4;k++){float w=W(probeWeight,k);if(w==0)continue;int j=I(probeWeight,k);
                // Unity bindposes include mesh-local to bone-bind transform. Left multiplication returns world space.
                Vector3 proposal=(r.bones[j].localToWorldMatrix*m.bindposes[j]).MultiplyPoint3x4(p);
                weighted+=w*proposal;names.Add(r.bones[j].name);weights.Add(w);proposals.Add(proposal);
            }
            var result=new RigProbe{rendererName=r.name,vertexIndex=probeIndex,bones=names.ToArray(),weights=weights.ToArray(),bindPosition=p,proposalsWorld=proposals.ToArray(),weightedWorld=weighted,cpuVsBakeWorldError=float.NaN};
            if(compareActualBake){r.BakeMesh(bakeMesh,false);result.bakedWorld=r.transform.TransformPoint(bakeMesh.vertices[probeIndex]);result.cpuVsBakeWorldError=Vector3.Distance(weighted,result.bakedWorld);}
            return result;
        }
        public void Dispose(){if(bakeMesh!=null)UnityEngine.Object.DestroyImmediate(bakeMesh);}
    }
}
