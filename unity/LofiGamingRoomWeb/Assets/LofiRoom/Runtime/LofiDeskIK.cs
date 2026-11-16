using UnityEngine;
namespace Yamyam.LofiRoom
{
    public sealed class LofiDeskIK:MonoBehaviour
    {
        public LofiActivities activities;
        void OnAnimatorIK(int layer){if(activities)activities.FitHands();}
    }
}
