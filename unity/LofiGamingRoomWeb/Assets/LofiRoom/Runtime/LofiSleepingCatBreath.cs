using UnityEngine;
namespace Yamyam.LofiRoom
{
    // The complete sleeping anatomy and fur come from the actual Tripo model.
    // Only the tiny breathing cycle is added; no replacement primitive body.
    public sealed class LofiSleepingCatBreath:MonoBehaviour
    {
        Vector3 rest;
        void Awake(){rest=transform.localScale;}
        void Update(){float b=Mathf.Sin(Time.time*1.15f);transform.localScale=Vector3.Scale(rest,new Vector3(1,1+b*.007f,1+b*.002f));}
    }
}
