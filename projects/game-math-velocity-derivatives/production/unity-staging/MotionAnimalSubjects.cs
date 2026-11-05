using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.MathMotion {
    // Original ellipsoid models for the hare-and-tortoise displacement example.
    // Their positions are supplied by MotionMathModel, the same source as both graphs.
    internal sealed class MotionAnimalSubjects {
        readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
        Material Paint(string hex) {
            if(materials.TryGetValue(hex,out var paint))return paint;
            ColorUtility.TryParseHtmlString("#"+hex,out var color);
            paint=new Material(Shader.Find("Universal Render Pipeline/Lit")){name="MotionAnimal_"+hex};
            paint.SetColor("_BaseColor",color);paint.SetFloat("_Smoothness",.15f);
            materials.Add(hex,paint);return paint;
        }
        void Oval(Transform parent,string name,Vector3 center,Vector3 size,string color,float tilt=0) {
            var part=GameObject.CreatePrimitive(PrimitiveType.Sphere);
            part.name=name;part.transform.SetParent(parent,false);part.transform.localPosition=center;
            part.transform.localScale=size;part.transform.localRotation=Quaternion.Euler(0,0,tilt);
            Object.DestroyImmediate(part.GetComponent<Collider>());
            part.GetComponent<MeshRenderer>().sharedMaterial=Paint(color);
        }
        public void Hare(Transform body) {
            const string fur="F3DEC5",shadow="D1AB89",pink="CE7985";
            Oval(body,"Body",new Vector3(-.10f,-.08f,0),new Vector3(1.02f,.65f,.60f),fur);
            Oval(body,"Tail",new Vector3(-.63f,.03f,.02f),Vector3.one*.27f,fur);
            Oval(body,"Head",new Vector3(.39f,.15f,0),new Vector3(.59f,.55f,.54f),fur);
            foreach(float z in new[]{-.15f,.15f}) {
                float x=z<0?.44f:.25f;float angle=z<0?-12:16;
                Oval(body,"LongEar",new Vector3(x,.64f,z),new Vector3(.17f,.73f,.15f),fur,angle);
                Oval(body,"InnerEar",new Vector3(x,.65f,z-.055f),new Vector3(.09f,.55f,.08f),pink,angle);
                Oval(body,"HindLeg",new Vector3(-.30f,-.20f,z),new Vector3(.51f,.51f,.32f),shadow);
                Oval(body,"HindPaw",new Vector3(-.18f,-.43f,z),new Vector3(.51f,.14f,.22f),fur);
                Oval(body,"FrontPaw",new Vector3(.35f,-.34f,z),new Vector3(.34f,.14f,.18f),fur);
            }
            Oval(body,"Eye",new Vector3(.55f,.24f,-.22f),Vector3.one*.105f,"24272B");
            Oval(body,"EyeCatchlight",new Vector3(.56f,.26f,-.268f),Vector3.one*.032f,"FFFFFF");
            Oval(body,"Nose",new Vector3(.69f,.12f,-.04f),new Vector3(.11f,.09f,.13f),pink);
        }
        public void Tortoise(Transform body) {
            const string shell="72A47B",rim="CAD49A",skin="A3BE7E";
            Oval(body,"ShellRim",new Vector3(-.12f,0,0),new Vector3(1.12f,.36f,.68f),rim);
            Oval(body,"DomedShell",new Vector3(-.12f,.10f,0),new Vector3(1.04f,.58f,.64f),shell);
            foreach(float x in new[]{-.42f,-.10f,.21f})
                Oval(body,"Scute",new Vector3(x,.12f,-.28f),new Vector3(.24f,.23f,.10f),"507F65");
            foreach(float x in new[]{-.46f,.21f})foreach(float z in new[]{-.22f,.22f})
                Oval(body,"Foot",new Vector3(x,-.19f,z),new Vector3(.28f,.23f,.22f),skin);
            Oval(body,"Neck",new Vector3(.40f,-.02f,0),new Vector3(.44f,.18f,.22f),skin);
            Oval(body,"Head",new Vector3(.62f,.04f,0),new Vector3(.38f,.28f,.31f),skin);
            Oval(body,"Eye",new Vector3(.71f,.09f,-.13f),Vector3.one*.075f,"26352B");
            Oval(body,"Tail",new Vector3(-.71f,-.05f,0),new Vector3(.24f,.09f,.11f),skin);
        }
    }
}
