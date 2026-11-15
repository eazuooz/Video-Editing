using UnityEngine;
namespace Yamyam.OriginalTechTwelve.Temporal {
    [ExecuteInEditMode] public class NaiveHistoryBlend:MonoBehaviour {
        public Shader shader;public float feedback=.9f;Material material;RenderTexture history;
        void OnRenderImage(RenderTexture source,RenderTexture destination){
            if(!material)material=new Material(shader){hideFlags=HideFlags.HideAndDontSave};
            if(!history||history.width!=source.width||history.height!=source.height){if(history)DestroyImmediate(history);history=new RenderTexture(source.width,source.height,0,RenderTextureFormat.ARGB32){hideFlags=HideFlags.HideAndDontSave};history.Create();Graphics.Blit(source,history);}
            material.SetTexture("_PreviousTex",history);material.SetFloat("_Feedback",feedback);var temp=RenderTexture.GetTemporary(source.width,source.height,0,RenderTextureFormat.ARGB32);Graphics.Blit(source,temp,material);Graphics.Blit(temp,destination);Graphics.Blit(temp,history);RenderTexture.ReleaseTemporary(temp);
        }
        void OnDisable(){if(history)DestroyImmediate(history);if(material)DestroyImmediate(material);}
    }
}
