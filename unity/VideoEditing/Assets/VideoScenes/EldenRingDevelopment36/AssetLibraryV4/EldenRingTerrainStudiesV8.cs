using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        static float VistaPathCenterV8(float z) =>
            .78f * Mathf.Sin((z + 3f) * .19f) + .18f * Mathf.Sin(z * .43f);

        static float VistaGroundV8(float x, float z)
        {
            float distanceFromPath = Mathf.Abs(x - VistaPathCenterV8(z));
            float shoulder = Mathf.SmoothStep(0, 1, Mathf.Clamp01((distanceFromPath - 1.05f) / 5f));
            return .13f + .09f * Mathf.Sin(z * .3f) +
                shoulder * (.29f + .24f * Mathf.Sin(x * .46f - z * .39f));
        }

        Mesh StudySurfaceV8(string name, Vector3[] vertices, int columns, Color color)
        {
            var surface = Group(name, Vector3.zero);
            var mesh = new Mesh { name = name };
            owned.Add(mesh);
            mesh.vertices = vertices;
            int rows = vertices.Length / columns;
            var indices = new int[(rows - 1) * (columns - 1) * 6];
            int triangle = 0;
            for (int row = 0; row < rows - 1; row++)
            for (int column = 0; column < columns - 1; column++)
            {
                int front = row * columns + column;
                indices[triangle++] = front;
                indices[triangle++] = front + columns;
                indices[triangle++] = front + 1;
                indices[triangle++] = front + 1;
                indices[triangle++] = front + columns;
                indices[triangle++] = front + columns + 1;
            }
            mesh.triangles = indices;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            surface.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            surface.gameObject.AddComponent<MeshRenderer>().sharedMaterial = Paint(color);
            return mesh;
        }

        Action<float> VistaV8()
        {
            stage.Find("Model table").gameObject.SetActive(false);
            view.orthographic = false;
            view.fieldOfView = 43f;
            view.backgroundColor = new Color(.48f, .62f, .68f);
            stage.Find("Key light").rotation = Quaternion.Euler(32, -26, 0);

            const int groundColumns = 37;
            const int groundRows = 49;
            var ground = new Vector3[groundColumns * groundRows];
            var path = new Vector3[groundRows * 5];
            for (int row = 0; row < groundRows; row++)
            {
                float z = Mathf.Lerp(-18f, 27f, row / (float)(groundRows - 1));
                for (int column = 0; column < groundColumns; column++)
                {
                    float x = Mathf.Lerp(-20f, 20f, column / (float)(groundColumns - 1));
                    ground[row * groundColumns + column] = V(x, VistaGroundV8(x, z), z);
                }
                float halfWidth = .83f + .10f * Mathf.Sin(z * .7f);
                for (int column = 0; column < 5; column++)
                {
                    float x = VistaPathCenterV8(z) + halfWidth * (column * .5f - 1f);
                    path[row * 5 + column] = V(x, VistaGroundV8(x, z) + .032f, z);
                }
            }
            StudySurfaceV8("Open plain original terrain", ground, groundColumns, new Color(.40f, .47f, .31f));
            StudySurfaceV8("Continuous walking path", path, 5, new Color(.60f, .49f, .32f));

            var vistaTower = Group("Distant destination silhouette", V(.75f, .4f, 17.6f));
            Attach("tower", vistaTower, V(2.8f, 5.4f, 2.75f), true, 26f);
            var farLeft = Group("Left skyline ridge", V(-7f, -.28f, 21.5f));
            var farRight = Group("Right skyline ridge", V(8.4f, -.34f, 24f));
            Attach("cliff", farLeft, V(8.8f, 2.5f, 6.2f), true, 15f);
            Attach("cliff", farRight, V(9.6f, 3.2f, 6.6f), true, -28f);

            // The two states share terrain, camera, actor, tower, and individual tree coordinates.
            Vector3[] plants =
            {
                V(-3.95f, 1.30f, -6.26f), V(2.6f, .84f, -5.59f),
                V(-1.26f, 1.72f, -3.5f), V(-3.05f, .96f, -.43f),
                V(3.74f, 1.17f, 1.6f), V(-1.84f, 1.23f, 3.85f),
                V(5.66f, .70f, 4.76f), V(-4.65f, .79f, 6.63f)
            };
            var tallStand = Group("A foreground canopy", Vector3.zero);
            var smallStand = Group("B low foreground growth", Vector3.zero);
            for (int i = 0; i < plants.Length; i++)
            {
                Vector3 plant = plants[i];
                Vector3 at = V(plant.x, VistaGroundV8(plant.x, plant.z), plant.z);
                var tall = Group("Tall comparison tree " + (i + 1), at);
                var small = Group("Low comparison tree " + (i + 1), at);
                tall.SetParent(tallStand, false);
                small.SetParent(smallStand, false);
                float yaw = i * 57f;
                Attach("tree", tall, V(2.35f, 4.3f, 2.1f) * plant.y, true, yaw);
                Attach("tree", small, V(1.28f, 1.05f, 1.12f) * plant.y, true, yaw);
            }

            Vector3[] grassPatches =
            {
                V(-1.8f, .9f, -9.2f), V(1.5f, 1f, -8.1f), V(-2.7f, 1.15f, -6f),
                V(2.5f, .85f, -4.7f), V(-1.46f, .58f, -3.2f), V(1.8f, .73f, -1.75f),
                V(-2.35f, .82f, .5f), V(2.4f, 1.1f, 2.4f), V(-3.46f, 1.2f, 4.64f)
            };
            for (int i = 0; i < grassPatches.Length; i++)
            {
                Vector3 tuft = grassPatches[i];
                var tuftRoot = Group("Fixed roadside foliage " + (i + 1),
                    V(tuft.x, VistaGroundV8(tuft.x, tuft.z), tuft.z));
                Attach("grass", tuftRoot, V(1.24f, .38f, .87f) * tuft.y, true, 103f * i);
            }

            var player = Pawn("Landscape traveller", V(0, 0, 0), Gold);
            return t =>
            {
                float rail = .54f * Range(t, 0, .43f) + .46f * Range(t, .57f, 1f);
                bool tallTrees = Second ? t < .5f : t >= .5f;
                tallStand.gameObject.SetActive(tallTrees);
                smallStand.gameObject.SetActive(!tallTrees);

                float cameraZ = Mathf.Lerp(-13.2f, -9.0f, rail);
                float playerZ = cameraZ + 3.65f;
                float playerX = VistaPathCenterV8(playerZ);
                player.localPosition = V(playerX, VistaGroundV8(playerX, playerZ) + .045f, playerZ);
                player.localRotation = Quaternion.Euler(0, Mathf.Rad2Deg * Mathf.Atan2(
                    VistaPathCenterV8(playerZ + .4f) - playerX, .4f), 0);
                FrameCamera(V(VistaPathCenterV8(cameraZ) - .32f, 2.45f, cameraZ),
                    V(.62f, 1.94f, 12f), 3f);
            };
        }

        const int TerrainColumnsV8 = 6;
        const int TerrainRowsV8 = 4;
        static readonly float[] TerrainSampleXV8 = { -1.92f, -1.17f, -.42f, .34f, 1.11f, 1.92f };
        static readonly float[] TerrainSampleZV8 = { -1.52f, -.49f, .49f, 1.52f };

        static void UpdateTerrainSamplesV8(Vector3[] vertices, float origin, float lift, float edit)
        {
            for (int row = 0; row < TerrainRowsV8; row++)
            for (int column = 0; column < TerrainColumnsV8; column++)
            {
                float sampleX = TerrainSampleXV8[column];
                // Rows start on exactly the same horizontal sampling grid. A heightmap can only lift a sample.
                // The editable mesh also slides vertices 2 and 3 together to form the adjoining faces of a lip.
                float editedX = column == 2 ? .11f : column == 3 ? .135f : sampleX;
                float z = TerrainSampleZV8[row];
                if (column == 2 || column == 3) editedX += .075f * z;
                float height = column < 3 ? 0 : lift * 1.12f;
                vertices[row * TerrainColumnsV8 + column] =
                    V(origin + Mathf.Lerp(sampleX, editedX, edit), .29f + height, z);
            }
        }

        Action<float> TerrainV8()
        {
            view.backgroundColor = new Color(.14f, .20f, .25f);
            FrameCamera(V(.58f, 6.7f, -13.9f), V(0, .68f, 0), 3.65f);
            var heightmap = new Vector3[TerrainRowsV8 * TerrainColumnsV8];
            var handEdited = new Vector3[heightmap.Length];
            UpdateTerrainSamplesV8(heightmap, -2.42f, 0, 0);
            UpdateTerrainSamplesV8(handEdited, 2.42f, 0, 0);
            var gridMesh = StudySurfaceV8("Heightmap samples on fixed XZ plane", heightmap, TerrainColumnsV8,
                new Color(.48f, .35f, .20f));
            var editedMesh = StudySurfaceV8("Independently edited polygon mesh", handEdited, TerrainColumnsV8,
                new Color(.19f, .46f, .49f));
            gridMesh.MarkDynamic();
            editedMesh.MarkDynamic();

            Block("Left terrain foundation", V(-2.42f, .10f, 0), V(3.96f, .32f, 3.18f), Slate);
            Block("Right terrain foundation", V(2.42f, .10f, 0), V(3.96f, .32f, 3.18f), Slate);
            Bar("Comparison divider", V(0, .03f, -1.89f), V(0, .03f, 1.88f), .032f, Paper);
            var leftWires = new Transform[TerrainRowsV8 * (TerrainColumnsV8 - 1) +
                (TerrainRowsV8 - 1) * TerrainColumnsV8];
            var rightWires = new Transform[leftWires.Length];
            for (int i = 0; i < leftWires.Length; i++)
            {
                leftWires[i] = Block("Heightmap fixed sample connection", Vector3.zero, Vector3.one, new Color(.91f, .68f, .35f));
                rightWires[i] = Block("Polygon edge", Vector3.zero, Vector3.one, new Color(.52f, .88f, .89f));
            }

            var leftControls = new Transform[TerrainRowsV8 * 2];
            var rightControls = new Transform[leftControls.Length];
            for (int i = 0; i < leftControls.Length; i++)
            {
                leftControls[i] = Orb("Height sample", Vector3.zero, .102f, Gold);
                rightControls[i] = Orb("Polygon control point", Vector3.zero, .116f, Aqua);
            }

            const float desiredLipX = .12f;
            foreach (float origin in new[] { -2.42f, 2.42f })
            {
                // A common horizontal design datum shows where the visible edge is meant to start.
                float x = origin + desiredLipX;
                Bar("Design lip location", V(x, .055f, -2.02f), V(x, .055f, -1.64f), .058f, Gold);
                var marker = Orb("Design datum marker", V(x, .055f, -2.03f), .099f, Gold);
                marker.localScale = V(.17f, .055f, .16f);
            }

            return t =>
            {
                float gridLift = Second ? 1f : Range(t, .12f, .49f);
                float edit = Second ? Range(t, .20f, .65f) : Range(t, .42f, .85f);
                float editedLift = Second ? 1f : Range(t, .12f, .49f);
                UpdateTerrainSamplesV8(heightmap, -2.42f, gridLift, 0f);
                UpdateTerrainSamplesV8(handEdited, 2.42f, editedLift, edit);
                PresentTerrainSamplesV8(gridMesh, heightmap, leftWires, leftControls, .032f);
                PresentTerrainSamplesV8(editedMesh, handEdited, rightWires, rightControls, .040f);
            };
        }

        static void PresentTerrainSamplesV8(Mesh mesh, Vector3[] vertices, Transform[] wires, Transform[] controls, float lineWidth)
        {
            mesh.vertices = vertices;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            int wire = 0;
            var offset = V(0, .025f, 0);
            for (int row = 0; row < TerrainRowsV8; row++)
            for (int column = 0; column < TerrainColumnsV8; column++)
            {
                int point = row * TerrainColumnsV8 + column;
                if (column < TerrainColumnsV8 - 1)
                    Segment(wires[wire++], vertices[point] + offset, vertices[point + 1] + offset, lineWidth);
                if (row < TerrainRowsV8 - 1)
                    Segment(wires[wire++], vertices[point] + offset, vertices[point + TerrainColumnsV8] + offset, lineWidth);
            }
            for (int row = 0; row < TerrainRowsV8; row++)
            {
                int point = row * TerrainColumnsV8 + 2;
                controls[row * 2].localPosition = vertices[point] + offset;
                controls[row * 2 + 1].localPosition = vertices[point + 1] + offset;
            }
        }
    }
}
