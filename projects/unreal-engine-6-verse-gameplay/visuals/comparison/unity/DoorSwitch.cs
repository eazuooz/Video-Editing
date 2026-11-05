using UnityEngine;

public sealed class DoorSwitch : MonoBehaviour
{
    [SerializeField] private Transform hinge;
    [SerializeField] private bool hasKey;

    public void PressSwitch()
    {
        if (hasKey)
            hinge.localRotation = Quaternion.Euler(0f, 90f, 0f);
    }
}
