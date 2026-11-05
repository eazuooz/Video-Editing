using System;
using UnityEngine;

// The recording contains inputs at simulation ticks, never sampled transforms.
public sealed class CommandReplay : MonoBehaviour
{
    [Serializable] public struct Order { public int tick; public bool attack; public Vector3 target; }
    public Transform[] squad;
    public Vector3[] spawn;
    public Transform enemy, tracer;
    public Order[] inputs;
    public int hitPoints { get; private set; }
    private int tick, next;
    private Vector3 destination;
    private bool moving, shooting;
    private float speed;
    private System.Random random;
    private readonly int[] nextShot = new int[8];

    public void ResetMatch(float moveSpeed)
    {
        tick = next = 0; moving = shooting = false; speed = moveSpeed;
        hitPoints = 100; random = new System.Random(42);
        Array.Clear(nextShot, 0, nextShot.Length);
        for (int i = 0; i < squad.Length; i++) squad[i].position = spawn[i];
        tracer.gameObject.SetActive(false);
    }

    public void Step()
    {
        while (next < inputs.Length && inputs[next].tick == tick)
        {
            Order order = inputs[next++];
            if (order.attack) shooting = true;
            else { moving = true; destination = order.target; }
        }
        bool flash = false;
        for (int i = 0; i < squad.Length; i++)
        {
            Transform unit = squad[i];
            Vector3 goal = destination + spawn[i] - spawn[0];
            if (moving) unit.position = Vector3.MoveTowards(unit.position, goal, speed / 60f);
            if (!shooting || tick < nextShot[i] || Vector3.Distance(unit.position,enemy.position) > 7.8f) continue;
            nextShot[i] = tick + random.Next(35, 64);
            hitPoints = Mathf.Max(0, hitPoints - 2);
            Vector3 a = unit.position + Vector3.up * .5f, b = enemy.position + Vector3.up * .6f;
            tracer.position = (a+b)*.5f; tracer.rotation = Quaternion.FromToRotation(Vector3.up,b-a);
            tracer.localScale = new Vector3(.07f,(b-a).magnitude*.5f,.07f);
            flash = true;
        }
        if (flash || tick % 4 == 0) tracer.gameObject.SetActive(flash);
        tick++;
    }
    void Start() { Time.fixedDeltaTime=1f/60f; ResetMatch(2.85f); }
    void FixedUpdate() { Step(); }
}
