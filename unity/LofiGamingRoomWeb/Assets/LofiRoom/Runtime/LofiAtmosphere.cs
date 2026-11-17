using UnityEngine;

namespace Yamyam.LofiRoom
{
    public sealed class LofiAtmosphere:MonoBehaviour
    {
        public Material shaftMaterial,outsideMaterial;
        public Light windowLight;
        public ParticleSystem dust;
        public Renderer shaftRenderer;
        public bool breeze=true,shafts=true;
        public float dayAmount=1;
        float targetDay=1;
        public void SetNight(bool night){targetDay=night?0:1;}
        public void ToggleBreeze(){breeze=!breeze;}
        public void ToggleShafts(){shafts=!shafts;}
        void Awake(){Shader.SetGlobalFloat("_LofiWind",1);}
        void Update()
        {
            dayAmount=Mathf.MoveTowards(dayAmount,targetDay,Time.deltaTime*.65f);
            Shader.SetGlobalFloat("_LofiWind",breeze?1:0);
            if(shaftRenderer)shaftRenderer.enabled=shafts;
            if(shaftMaterial)
            {
                shaftMaterial.SetFloat("_Strength",Mathf.Lerp(.15f,1,dayAmount));
                shaftMaterial.SetColor("_BeamColor",Color.Lerp(new Color(.40f,.58f,1f),new Color(1f,.83f,.53f),dayAmount));
            }
            if(windowLight){windowLight.intensity=Mathf.Lerp(1.4f,7.5f,dayAmount);windowLight.color=Color.Lerp(new Color(.4f,.58f,1f),new Color(1f,.87f,.63f),dayAmount);}
            if(outsideMaterial)
            {
                if(outsideMaterial.HasProperty("_DayAmount")){outsideMaterial.SetFloat("_DayAmount",dayAmount);return;}
                Color c=Color.Lerp(new Color(.035f,.10f,.17f),new Color(.35f,.57f,.59f),dayAmount);
                outsideMaterial.SetColor("_BaseColor",c);outsideMaterial.SetColor("_EmissionColor",c*.6f);
            }
        }
        void OnDestroy(){Shader.SetGlobalFloat("_LofiWind",1);}
    }
}
