using UnityEngine;
namespace Yamyam.LofiRoom
{
    public sealed class LofiHearth:MonoBehaviour
    {
        public AudioSource crackle;
        public Light fireLight;
        public Renderer[] embers;
        public bool lit=true;
        public float flickerIntensity;
        MaterialPropertyBlock block;
        void Awake(){block=new MaterialPropertyBlock();}
        void Start(){if(crackle && crackle.clip){crackle.loop=true;crackle.Play();}}
        public void ToggleSound(){if(crackle)crackle.mute=!crackle.mute;}
        void Update()
        {
            float low=Mathf.PerlinNoise(Time.time*.85f,2.7f),high=Mathf.PerlinNoise(Time.time*4.5f,8.4f);
            flickerIntensity=(.75f+low*.40f+high*.10f)*(lit?1:0);
            if(fireLight)fireLight.intensity=flickerIntensity*3.2f;
            if(embers!=null)foreach(var r in embers)
            {
                r.GetPropertyBlock(block);block.SetColor("_EmissionColor",new Color(1,.12f,.008f)*flickerIntensity*2.1f);r.SetPropertyBlock(block);
            }
        }
    }
}
