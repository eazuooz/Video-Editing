using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        static readonly Color Field20 = new Color32(79, 101, 73, 255);
        static readonly Color Path20 = new Color32(153, 123, 87, 255);
        static readonly Color Rock20 = new Color32(111, 109, 100, 255);
        static readonly Color Dust20 = new Color32(164, 129, 98, 255);

        Action<float> BuildObserved20To28()
        {
            switch (episode)
            {
                case 20: return ObservedTraversal20();
                case 21: return ObservedTactics21();
                case 22: return ObservedDiscovery22();
                case 23: return ObservedHandoff23(false);
                case 24: return ObservedDetour24();
                case 25: return ObservedHandoff23(true);
                case 26: return ObservedWeight26();
                case 27: return ObservedAcoustics27();
                case 28: return ObservedChoir28();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        void VistaFloor20(string label, Color ground)
        {
            view.backgroundColor = new Color32(102, 125, 126, 255);
            Floor(label, 0, 0, 16.4f, 16.4f, .008f, ground);
        }

        void Follow20(Vector3 focus, Vector3 offset, Vector3 ahead, float height)
        {
            FrameCamera(focus + offset, focus + ahead, height);
        }

        static Vector3 TwoLegRoute20(Vector3 start, Vector3 bend, Vector3 end, float t, float split = .5f)
        {
            return t < split ? Vector3.Lerp(start, bend, Range(t, 0, split)) :
                Vector3.Lerp(bend, end, Range(t, split, 1));
        }

        void Prop20(string role, Transform anchor, Vector3 fit, float yaw = 0)
        {
            Attach(role, anchor, fit, true, yaw);
        }

        Action<float, float> ArticulatedMount20(Transform root)
        {
            var coat = new Color32(159, 101, 67, 255);
            var lightCoat = new Color32(189, 135, 91, 255);
            var mane = new Color32(55, 42, 36, 255);

            Transform Joint(string name, Vector3 local, Transform parent)
            {
                var joint = Group(name, local);
                joint.SetParent(parent, false);
                return joint;
            }

            Shape(PrimitiveType.Sphere, "Horse torso", V(-.08f, .84f, 0), V(1.65f, .60f, .63f), coat, root);
            Shape(PrimitiveType.Sphere, "Front shoulder", V(.46f, .77f, 0), V(.72f, .65f, .62f), lightCoat, root);
            Shape(PrimitiveType.Sphere, "Round hindquarters", V(-.62f, .76f, 0), V(.69f, .65f, .65f), coat, root);
            Block("Saddle blanket", V(-.24f, 1.09f, 0), V(.48f, .09f, .61f), Aqua, root);
            Shape(PrimitiveType.Sphere, "Saddle seat", V(-.25f, 1.14f, 0), V(.54f, .15f, .49f), mane, root);

            var neck = Joint("Neck pivot", V(.43f, .92f, 0), root);
            var neckShape = Shape(PrimitiveType.Capsule, "Rising neck", V(.22f, .24f, 0), V(.32f, .35f, .33f), coat, neck);
            neckShape.localRotation = Quaternion.Euler(0, 0, -37f);
            var crest = Block("Dark raised mane", V(.07f, .29f, 0), V(.11f, .59f, .17f), mane, neck);
            crest.localRotation = Quaternion.Euler(0, 0, -37f);
            Shape(PrimitiveType.Sphere, "Horse head", V(.41f, .43f, 0), V(.59f, .32f, .34f), lightCoat, neck);
            Shape(PrimitiveType.Sphere, "Long muzzle", V(.64f, .33f, 0), V(.38f, .22f, .28f), lightCoat, neck);
            for (int side = -1; side <= 1; side += 2)
            {
                Block("Ear", V(.25f, .62f, .105f * side), V(.11f, .21f, .07f), coat, neck).localRotation = Quaternion.Euler(0, 0, -11f);
                Orb("Eye", V(.47f, .48f, .149f * side), .075f, mane, neck);
                Block("Stirrup", V(-.30f, .76f, .35f * side), V(.13f, .07f, .11f), mane, root);
            }

            var tail = Joint("Swishing tail pivot", V(-.81f, .88f, 0), root);
            var tailShape = Shape(PrimitiveType.Capsule, "Dark tail", V(-.11f, -.22f, 0), V(.12f, .33f, .14f), mane, tail);
            tailShape.localRotation = Quaternion.Euler(0, 0, -28f);
            var upper = new Transform[4];
            var lower = new Transform[4];
            for (int i = 0; i < upper.Length; i++)
            {
                bool front = i < 2;
                float side = i % 2 == 0 ? -.232f : .232f;
                upper[i] = Joint("Horse upper leg", V(front ? .48f : -.64f, .69f, side), root);
                lower[i] = Joint("Horse lower leg and hoof", V(0, -.30f, 0), upper[i]);
                Shape(PrimitiveType.Capsule, "Upper leg muscle", V(0, -.12f, 0), V(.20f, .20f, .17f), coat, upper[i]);
                Shape(PrimitiveType.Capsule, "Articulated lower leg", V(0, -.13f, 0), V(.13f, .16f, .12f), coat, lower[i]);
                Block("Hoof", V(.029f, -.323f, 0), V(.19f, .122f, .15f), mane, lower[i]);
            }

            return (phase, strength) =>
            {
                for (int i = 0; i < upper.Length; i++)
                {
                    float distance = Mathf.Sin(phase + (i == 0 || i == 3 ? 0 : Mathf.PI));
                    upper[i].localRotation = Quaternion.Euler(0, 0, 26f * strength * distance);
                    lower[i].localRotation = Quaternion.Euler(0, 0, -33f * strength * Mathf.Max(0, distance));
                }
                neck.localRotation = Quaternion.Euler(0, 0, 7f * strength * Mathf.Sin(phase + .4f));
                tail.localRotation = Quaternion.Euler(0, Mathf.Sin(phase * .53f) * 16f * strength, 3f * strength);
            };
        }

        Action<float> ObservedTraversal20()
        {
            VistaFloor20("Traversal field", Field20);
            Floor("Crest route", 0, 0, 10.5f, 4.8f, .031f, Path20);
            Prop20("tower", Group("Distant navigation silhouette", V(5.55f, .012f, 2.65f)), V(1.8f, 3.25f, 2.2f));
            Prop20("rock", Group("Foreground rock edge", V(-4, .01f, 2.3f)), V(1.7f, .84f, 1));
            Tree(V(-4.75f, .01f, 3.4f), 1.37f);
            Tree(V(2.9f, .01f, 3.25f), 1.0f);
            if (!Second)
            {
                GroundGate("Entrance before the exposed field", V(-4.8f, .03f, -.11f), 2.1f, 2.5f, Rock20);
                var foot = Pawn("Walking comparison", V(-4.8f, .03f, -.85f), Gold);
                var rider = Pawn("Mounted route comparator", V(-4.8f, .03f, 1.0f), Aqua);
                rider.localScale = Vector3.one * .82f;
                var riding = walkthroughActors[walkthroughActors.Count - 1];
                riding.FixedFacing = true;
                rider.localRotation = Quaternion.Euler(0, 90, 0);
                var horse = Group("Horse follows the longer line through the meadow", V(-4.8f, .035f, 1.0f));
                var horsePose = ArticulatedMount20(horse);
                riding.AfterPose = () =>
                {
                    for (int side = 0; side < 2; side++)
                    {
                        float direction = side == 0 ? -1 : 1;
                        PoseLimb(riding.Legs[side], rider.TransformPoint(V(direction * .39f, .51f, .22f)), rider.forward);
                        PoseLimb(riding.Arms[side], rider.TransformPoint(V(direction * .22f, 1.06f, .62f)), -rider.up);
                    }
                    foreach (var part in riding.Parts) part.Source.BakeMesh(part.PosedMesh, false);
                };
                var cadence = Ring("Mounted distance marker", V(5.2f, .05f, 1), .42f, Aqua);
                var start = Ring("Common start zone", V(-4.8f, .05f, .2f), .43f, Gold);
                return t =>
                {
                    float distance = Range(t, .08f, .91f);
                    float mounted = Range(t, .19f, .73f);
                    foot.localPosition = V(-4.8f + 5.5f * distance, .035f, -.85f);
                    float x = -4.8f + 10f * mounted;
                    float gaitStrength = (1f - Range(t, .68f, .75f)) * Range(t, .19f, .26f);
                    float phase = mounted * Mathf.PI * 22f;
                    float trot = Mathf.Sin(phase) * gaitStrength;
                    horse.localPosition = V(x, .035f + .095f * Mathf.Abs(trot), 1f);
                    horse.localRotation = Quaternion.Euler(0, 0, 3.5f * trot);
                    horsePose(phase, gaitStrength);
                    rider.localPosition = V(x - .27f, .43f + .095f * Mathf.Abs(trot), 1f);
                    riding.Cast = .26f;
                    start.gameObject.SetActive(t < .32f);
                    cadence.localScale = Vector3.one * (.95f + .20f * Range(t, .70f, .86f));
                    Follow20(V(Mathf.Lerp(-1.9f, .85f, distance), 0, .2f), V(-1.2f, 5.2f, -9.4f), V(0, 1.1f, .25f), 3.91f);
                };
            }

            const float stepTop = .51f;
            Floor("Walkable raised landing", 2.80f, 0, 3.7f, 2.2f, stepTop, Rock20);
            var jumper = Pawn("Player choosing the nearby ledge", V(-4.1f, .039f, -.04f), Gold);
            var rig = walkthroughActors[walkthroughActors.Count - 1];
            var obstacle = Ring("Ledge changes the short route", V(1.45f, stepTop + .025f, -.04f), .40f, Gold);
            rig.FixedFacing = true;
            jumper.localRotation = Quaternion.Euler(0, 90, 0);
            rig.GroundHeight = point => point.x >= .95f ? stepTop : .039f;
            Vector3 stagePoint = V(.55f, .06f, -.04f);
            return t =>
            {
                float takeoff = Range(t, .35f, .68f);
                float x = Mathf.Lerp(-4.10f, .36f, Range(t, .05f, .35f)) + 2.1f * takeoff + 1.65f * Range(t, .68f, .94f);
                float lift = Mathf.Sin(takeoff * Mathf.PI) * 1.18f;
                jumper.localPosition = V(x, Mathf.Lerp(.039f, stepTop, takeoff) + lift, -.04f);
                // Ground compensation remains on the actual platform except during the authored airborne arc.
                rig.GroundHeight = t > .35f && t < .68f ? (Func<Vector3, float>)null : point => point.x >= .95f ? stepTop : .039f;
                rig.Cast = .39f * Mathf.Sin(takeoff * Mathf.PI);
                obstacle.gameObject.SetActive(t >= .31f);
                Follow20(Vector3.Lerp(stagePoint, jumper.localPosition, .42f), V(-1.0f, 3.25f, -7.2f), V(.6f, .94f, .12f), 2.95f);
            };
        }

        Action<float> ObservedTactics21()
        {
            VistaFloor20("Same test court for both tactics", Field20);
            Floor("Clear arena path", 0, 0, 9.8f, 5.4f, .03f, Path20);
            GroundGate("Rear arena exit for depth reference", V(1.7f, .035f, 3.1f), 2.8f, 2.4f, Rock20);
            var player = Pawn("Player choosing distance", V(-3.8f, .037f, -.8f), Gold);
            var rig = walkthroughActors[walkthroughActors.Count - 1];
            var enemy = Pawn("Fixed practice encounter", V(2.35f, .037f, .65f), Red);
            var enemyRig = walkthroughActors[walkthroughActors.Count - 1];
            enemy.localScale = Vector3.one * 1.32f;
            rig.FixedFacing = enemyRig.FixedFacing = true;
            var tool = Group("Tool secured to the visible right hand", Vector3.zero);
            Prop20("sword", tool, V(.23f, .98f, .34f));
            var bolt = Orb("Illustrated ranged effect", Vector3.zero, .22f, Blue);
            var aura = Ring("Ranged setup marker", V(-2.6f, .057f, -.52f), .56f, Blue);
            var near = Ring("Close tactic contact distance", V(1.52f, .052f, .23f), .42f, Gold);
            rig.AfterPose = () =>
            {
                var wrist = rig.Arms[1].End.position;
                tool.position = wrist;
                tool.rotation = Quaternion.LookRotation(player.forward) * Quaternion.Euler(16 + 69 * rig.Cast, -9, 11);
            };
            return t =>
            {
                Vector3 end = Second ? V(-2.45f, .037f, -.52f) : V(1.18f, .037f, .30f);
                player.localPosition = Vector3.Lerp(V(-3.8f, .037f, -.80f), end, Range(t, .04f, .43f));
                enemy.localPosition = V(2.35f, .037f, .65f + .24f * Range(t, .62f, .81f));
                player.rotation = Quaternion.LookRotation(enemy.position - player.position);
                enemy.rotation = Quaternion.LookRotation(player.position - enemy.position);
                rig.Cast = Range(t, .40f, .61f) * (1 - Range(t, .70f, .89f));
                enemyRig.Cast = .34f * Range(t, .27f, .49f);
                aura.gameObject.SetActive(Second && t > .39f);
                near.gameObject.SetActive(!Second && t > .38f);
                bolt.gameObject.SetActive(Second && t > .59f && t < .83f);
                bolt.localPosition = Vector3.Lerp(player.localPosition + V(.28f, 1.23f, 0), enemy.localPosition + V(0, 1.06f, 0), Range(t, .59f, .83f));
                Vector3 focus = Vector3.Lerp(player.localPosition, enemy.localPosition, Second ? .54f : .40f);
                Follow20(focus, V(Second ? -.7f : -1.8f, 3.4f, -7.2f), V(.10f, .86f, .23f), Second ? 3.30f : 2.65f);
            };
        }

        Action<float> ObservedDiscovery22()
        {
            VistaFloor20("Same connected landscape in both orders", Field20);
            Floor("Paved route from hill to stone threshold", 0, -.6f, 11.6f, 4.55f, .04f, Path20);
            var west = V(-3.75f, .041f, 1.42f);
            var east = V(3.7f, .041f, 1.62f);
            GroundGate("Recognizable passage", east + V(0, 0, .55f), 2.05f, 2.45f, Rock20);
            Prop20("cliff", Group("Rock shelf blocks the near-to-far view", V(-3.9f, .045f, 2.5f)), V(3.7f, 1.4f, 1.65f));
            Prop20("tower", Group("Far silhouette shared in both visits", V(.72f, .04f, 4.9f)), V(1.64f, 2.9f, 1.8f));
            for (int i = 0; i < 3; i++) Tree(V(-3.2f + i * 3.6f, .02f, 4.2f), 1f + i * .10f);
            var middle = V(0, .042f, -1.10f);
            var player = Pawn("Explorer with two possible discovery orders", middle, Gold);
            var westMemory = Ring("Hill landmark remembered", west + V(0, .022f, 0), .49f, Aqua);
            var eastMemory = Ring("Gateway remembered", east + V(0, .022f, 0), .49f, Gold);
            var route = Bar("Orientation on the visible route", middle, middle + V(0, 0, .2f), .06f, Paper);
            return t =>
            {
                var first = Second ? east : west;
                var last = Second ? west : east;
                float distance = Range(t, .04f, .91f);
                var position = TwoLegRoute20(middle, first, last, distance, .45f);
                player.localPosition = position;
                var destination = distance < .49f ? first : last;
                westMemory.gameObject.SetActive(distance >= (Second ? .81f : .32f));
                eastMemory.gameObject.SetActive(distance >= (Second ? .32f : .81f));
                Segment(route, position + V(0, .055f, 0), destination + V(0, .05f, .05f), .06f);
                float turn = Mathf.Lerp(Second ? 1.3f : -1.3f, Second ? -2.75f : 2.75f, Range(t, .38f, .77f));
                Follow20(Vector3.Lerp(Vector3.zero, position, .55f), V(turn, 4.45f, -8.25f), V(0, 1.0f, .90f), 3.6f);
            };
        }

        Action<float> ObservedHandoff23(bool expansion)
        {
            VistaFloor20("Walkable shared frame", expansion && Second ? Dust20 : Field20);
            Floor("One playable alignment route", 0, .15f, 9.6f, 3.3f, .033f, Path20);
            var gateway = V(2.3f, .035f, .42f);
            bool enclosed = Second && !expansion;
            bool newField = Second && expansion;
            if (enclosed)
            {
                Block("Low roof at corridor threshold", gateway + V(.65f, 2.44f, 0), V(3.05f, .28f, 2.95f), Rock20);
                Block("Near stone side of narrow route", gateway + V(.66f, 1.07f, 1.53f), V(3.33f, 2.10f, .28f), Slate);
                Block("Far side with opening left visible to camera", gateway + V(1.22f, .75f, -1.53f), V(2.1f, 1.48f, .28f), Slate);
            }
            else
            {
                Prop20("rock", Group("Rock mass frames the hillside route", gateway + V(-.10f, 0, 1.8f)), V(2.2f, 1.15f, 1.6f));
                Tree(gateway + V(1.40f, 0, 2.1f), newField ? .85f : 1.28f);
            }
            Prop20(newField ? "bridge" : "tower", Group("Visible destination beyond route", V(5.0f, .012f, 3.7f)),
                newField ? V(3.7f, 1.95f, 1.60f) : V(2.4f, 2.7f, 1.90f));
            var actors = new[] { Pawn("Player validating the interdependent scene", V(-4.3f, .039f, -.48f), Gold),
                Pawn("Encounter placement reference", V(3.75f, .039f, .76f), Aqua) };
            var checks = new Transform[3];
            for (int i = 0; i < checks.Length; i++)
                checks[i] = Block("Illustrative production checkpoint", V(-3.1f + i * 2.85f, .09f, -1.68f), V(1.63f, .12f, .41f), Slate);
            var torch = Group("Lighting boundary at the route", gateway + V(.44f, 1.53f, 1.17f));
            Orb("Visible local warm practical", Vector3.zero, .21f, Gold, torch);
            var light = torch.gameObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = 3.55f;
            light.color = new Color(1.0f, .61f, .24f);
            return t =>
            {
                float progression = Range(t, .04f, .91f);
                Vector3 end = newField ? V(4.05f, .039f, 1.28f) : V(4.1f, .039f, .38f);
                var traveler = TwoLegRoute20(V(-4.3f, .039f, -.48f), V(-.2f, .039f, .30f), end, progression, .58f);
                actors[0].localPosition = traveler;
                actors[1].localPosition = V(3.85f, .04f, .88f + .48f * Range(t, .51f, .88f));
                light.intensity = .3f + .70f * Range(t, .44f, .77f);
                for (int i = 0; i < checks.Length; i++) Tint(checks[i], t >= .18f + i * .23f ? Aqua : Slate);
                Follow20(Vector3.Lerp(Vector3.zero, traveler, .70f), V(-1.0f, 4.85f - 1.35f * progression, -8.1f),
                    V(1.0f, 1.04f, .25f), Mathf.Lerp(3.8f, enclosed ? 2.58f : 3.08f, progression));
            };
        }

        Action<float> ObservedDetour24()
        {
            VistaFloor20("Approach and side-lane practice scene", Field20);
            Floor("Visible bypass on same ground", 0, 0, 10.7f, 6.6f, .033f, Path20);
            var initial = V(-4.18f, .038f, -.88f);
            var stop = V(-1.25f, .038f, -.61f);
            var opponent = V(1.7f, .038f, -.38f);
            Prop20("rock", Group("Rock masks part of the view on the bypass", V(.25f, .037f, .76f)), V(1.55f, .98f, .94f));
            Tree(V(.2f, .038f, 2.30f), 1.32f);
            Prop20("tower", Group("Landmark seen again while returning", V(4.7f, .008f, 3.3f)), V(1.60f, 2.68f, 1.56f));
            var player = Pawn("Player may pull away or prepare help", initial, Gold);
            var guard = Pawn("Large practice opponent", opponent, Red);
            guard.localScale = Vector3.one * 1.56f;
            var ally = Second ? Pawn("Illustrated supporting actor", V(-2.65f, .04f, -1.63f), Aqua) : null;
            var support = Ring("Visible support setup marker", V(-3.3f, .053f, -.65f), .51f, Blue);
            Route(Aqua, stop + V(0, .02f, 0), V(-.6f, .058f, 1.76f), V(2.8f, .058f, 1.76f));
            return t =>
            {
                var p = Vector3.Lerp(initial, stop, Range(t, .03f, .33f));
                guard.localPosition = opponent + V(-.32f * Range(t, .27f, .53f), 0, .22f * Range(t, .52f, .77f));
                if (Second)
                {
                    p = Vector3.Lerp(p, V(-3.05f, .04f, -.69f), Range(t, .35f, .59f));
                    ally.gameObject.SetActive(t > .49f);
                    ally.localPosition = Vector3.Lerp(V(-3.36f, .039f, -1.70f), V(.40f, .039f, -.30f), Range(t, .51f, .92f));
                }
                else
                {
                    p = TwoLegRoute20(p, V(-.6f, .038f, 1.76f), V(2.8f, .038f, 1.76f), Range(t, .39f, .92f));
                }
                player.localPosition = p;
                support.gameObject.SetActive(Second && t > .37f);
                Follow20(Vector3.Lerp(p, guard.localPosition, .42f), V(-1.65f - 1.2f * Range(t, .35f, .70f), 4.0f, -7.35f),
                    V(.14f, .94f, .32f), 3.15f);
            };
        }

        Action<float> ObservedWeight26()
        {
            VistaFloor20("Weapon motion timing practice area", Field20);
            Floor("Same flat contact surface for both weapons", 0, 0, 10.8f, 4.4f, .03f, Path20);
            var actors = new[] { Pawn("Shorter blade", V(-2.25f, .034f, .42f), Aqua), Pawn("Longer and heavier axe", V(2.08f, .034f, .42f), Gold) };
            var rigs = new[] { walkthroughActors[walkthroughActors.Count - 2], walkthroughActors[walkthroughActors.Count - 1] };
            var tools = new[] { Group("Actual sword held by wrist", Vector3.zero), Group("Actual axe held by wrist", Vector3.zero) };
            Prop20("sword", tools[0], V(.30f, 1.03f, .32f));
            Prop20("axe", tools[1], V(.86f, 1.72f, .49f));
            var phases = new Transform[3];
            for (int i = 0; i < phases.Length; i++) phases[i] = Block("Preparation, swing and recovery phase", V(-2.6f + i * 2.6f, .090f, -1.36f), V(2.12f, .11f, .37f), Slate);
            for (int i = 0; i < rigs.Length; i++)
            {
                var rig = rigs[i];
                var tool = tools[i];
                bool heavy = i == 1;
                rig.FixedFacing = true;
                rig.AfterPose = () =>
                {
                    float t = rig.PosePhase;
                    float stroke = Range(t, heavy ? .50f : .29f, heavy ? .67f : .44f);
                    float clear = Range(t, heavy ? .69f : .48f, heavy ? .97f : .71f);
                    tool.position = rig.Arms[1].End.position;
                    tool.rotation = rig.Root.rotation * Quaternion.Euler(12 + 83 * stroke - 83 * clear, 16, 22 * rig.Cast);
                };
            }
            return t =>
            {
                for (int i = 0; i < rigs.Length; i++)
                {
                    bool heavy = i == 1;
                    float charge = Range(t, .09f, heavy ? .49f : .28f);
                    float sweep = Range(t, heavy ? .50f : .29f, heavy ? .67f : .44f);
                    float recover = Range(t, heavy ? .69f : .48f, heavy ? .97f : .71f);
                    var rig = rigs[i];
                    rig.PosePhase = t;
                    rig.Cast = Mathf.Clamp01(charge - .48f * sweep - .52f * recover);
                    float twist = heavy ? 54 : 34;
                    actors[i].rotation = Quaternion.Euler(0, 164 - twist * charge + 1.76f * twist * sweep - .76f * twist * recover, 0);
                    actors[i].localPosition = V((heavy ? 2.08f : -2.25f) - (heavy ? .46f : .25f) * sweep + .12f * recover, .034f, .42f);
                }
                for (int i = 0; i < phases.Length; i++) Tint(phases[i], i == (t < .50f ? 0 : t < .68f ? 1 : 2) ? Gold : Slate);
                float emphasis = Second ? Range(t, .32f, .75f) : 0;
                Follow20(V(.7f * emphasis, 0, .2f), V(.55f + .65f * emphasis, 3.1f, -9.0f), V(0, 1.05f, .10f), 3.18f - .22f * emphasis);
            };
        }

        Action<float> ObservedAcoustics27()
        {
            VistaFloor20("Open stones and covered path at the same level", Field20);
            Floor("Walkable section across the acoustic boundary", 0, .05f, 11.5f, 4.55f, .042f, Rock20);
            float entrance = -.8f;
            // A cutaway near wall keeps both the feet and the bounce schematic readable.
            Block("Cave roof", V(-3.23f, 2.40f, .66f), V(4.83f, .36f, 3.43f), Slate);
            Block("Far cave wall", V(-3.23f, 1.12f, 2.34f), V(4.83f, 2.24f, .30f), Slate);
            Block("Low front wall for cutaway", V(-3.23f, .31f, -1.02f), V(4.83f, .58f, .30f), Slate);
            Prop20("rock", Group("Exposed rock and water edge reference", V(3.1f, .01f, 2.9f)), V(2.56f, 1.05f, 1.4f));
            var walker = Pawn("Same walking actor in both spaces", V(4.25f, .042f, .15f), Gold);
            var waves = new Transform[4];
            for (int i = 0; i < waves.Length; i++) waves[i] = Ring("Illustration of successive arrivals", V(0, .05f, .15f), .62f, i == 0 ? Gold : Aqua);
            var wallBounce = Bar("Example reflection across the cutaway room", V(-2.35f, .32f, .20f), V(-2.35f, 1.35f, 2.18f), .048f, Aqua);
            return t =>
            {
                float p = Range(t, .055f, .93f);
                var x = Second ? Mathf.Lerp(-4.44f, 3.88f, p) : Mathf.Lerp(4.25f, -4.48f, p);
                walker.localPosition = V(x, .042f, .15f + .15f * Mathf.Sin(p * Mathf.PI));
                bool inside = x < entrance;
                float step = Mathf.Repeat(t * 3f, 1f);
                for (int i = 0; i < waves.Length; i++)
                {
                    float phase = step - i * .18f;
                    waves[i].gameObject.SetActive(phase >= 0 && phase < (i == 0 ? .44f : .54f) && (inside || i == 0));
                    waves[i].localPosition = i == 0 ? walker.localPosition + V(0, .017f, 0) : V(Mathf.Clamp(x + .45f * (i - 2), -5.1f, -.94f), .06f, 1.03f);
                    waves[i].localScale = Vector3.one * (.32f + 1.1f * Mathf.Clamp01(phase));
                }
                wallBounce.gameObject.SetActive(inside && step > .22f && step < .76f);
                Segment(wallBounce, walker.localPosition + V(0, .17f, 0), V(Mathf.Clamp(x, -5.1f, -.9f), 1.42f, 2.19f), .048f);
                Follow20(V(x * .46f, 0, .2f), V(1.1f + 1f * (p - .5f), 4.4f, -8.4f), V(0, .88f, .66f), 3.5f);
            };
        }

        Action<float> ObservedChoir28()
        {
            VistaFloor20("Gathering courtyard before the exit", Dust20);
            Floor("Warm gathering ground opens toward the route", 0, 0, 11.6f, 6.0f, .041f, Rock20);
            GroundGate("Rear route from gathered people to open terrain", V(3.35f, .04f, 2.15f), 2.18f, 2.36f, Slate);
            Prop20("crate", Group("Supplies beside gathered people", V(-3.54f, .045f, 1.93f)), V(1.05f, .65f, .9f));
            Prop20("bench", Group("Staging furniture in the gathering", V(1.70f, .045f, 1.83f)), V(1.65f, .63f, .72f));
            for (int i = 0; i < 2; i++)
            {
                var brazier = Group("Warm point at the edge of the group", V(-3.42f + i * 6.9f, .67f, 1.57f));
                Orb("Firelight cue", Vector3.zero, .32f, Gold, brazier);
                var glow = brazier.gameObject.AddComponent<Light>();
                glow.type = LightType.Point;
                glow.color = new Color(1f, .51f, .28f);
                glow.intensity = 1.15f;
                glow.range = 3.55f;
            }
            var group = new Transform[3];
            var rigs = new WalkthroughActor[group.Length];
            var cue = new Transform[group.Length];
            for (int i = 0; i < group.Length; i++)
            {
                var position = V(-1.98f + i * 1.82f, .045f, .9f - .33f * i);
                group[i] = Pawn("Illustrative ensemble performer", position, i == 1 ? Gold : Aqua);
                rigs[i] = walkthroughActors[walkthroughActors.Count - 1];
                rigs[i].FixedFacing = true;
                cue[i] = Block("Illustrative independent voice shading", V(position.x, .10f, -1.36f), V(.40f, .12f, .33f), Aqua);
            }
            return t =>
            {
                float advance = Range(t, .08f, .76f);
                float turn = Second ? Range(t, .47f, .94f) : .25f * advance;
                for (int i = 0; i < group.Length; i++)
                {
                    float phase = t * 3.6f + (Second ? i * .17f : 0);
                    float strength = Pulse(phase);
                    var p = group[i];
                    p.localRotation = Quaternion.Euler(0, 174 - 37 * turn + (Second ? (i - 1) * 14f : 0), 0);
                    rigs[i].Cast = (Second ? .28f + .06f * i : .29f) * strength;
                    float bar = .20f + strength * (Second ? .38f + i * .12f : .57f);
                    cue[i].localScale = V(.40f, bar, .33f);
                    cue[i].localPosition = V(p.localPosition.x, .05f + bar * .5f, -1.36f);
                    Tint(cue[i], strength > .63f ? Gold : Aqua);
                }
                FrameCamera(V(Mathf.Lerp(-2.20f, 2.75f, turn), Mathf.Lerp(4.5f, 2.65f, advance), -9.9f),
                    V(Mathf.Lerp(-.25f, 1.28f, turn), 1.07f, .47f + .33f * turn), Mathf.Lerp(3.85f, 3.15f, advance));
            };
        }
    }
}
