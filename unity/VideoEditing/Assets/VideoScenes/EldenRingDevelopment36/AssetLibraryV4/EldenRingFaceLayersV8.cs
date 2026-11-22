using System;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        static readonly Vector3 FaceRadiiV8 = new Vector3(.94f, 1.08f, .83f);
        static readonly Color SkinV8 = new Color32(238, 174, 136, 255);
        static readonly Color HairV8 = new Color32(49, 35, 36, 255);
        const int TextureWidthV8 = 512;
        const int TextureHeightV8 = 256;

        Action<float> FaceLayersV8()
        {
            FrameCamera(V(0, 2.02f, -13f), V(0, 1.57f, 0), 2.19f);
            RenderSettings.ambientLight = new Color(.31f, .31f, .34f);
            var light = stage.Find("Key light").GetComponent<Light>();
            light.intensity = 1.45f;

            var surface = MakeFaceMeshV8(false);
            var hair = MakeFaceMeshV8(true);
            var painted = FaceTextureV8("Painted skin and scar", false);
            var normal = FaceTextureV8("Masked tangent-space normal", true);
            var colorMaterial = new Material(Paint(Color.white)) { name = "Skin color texture only" };
            colorMaterial.mainTexture = painted;
            owned.Add(colorMaterial);
            var normalMaterial = new Material(colorMaterial) { name = "Identical skin color plus normal texture" };
            normalMaterial.SetTexture("_BumpMap", normal);
            normalMaterial.SetFloat("_BumpScale", 0);
            normalMaterial.EnableKeyword("_NORMALMAP");
            owned.Add(normalMaterial);

            var left = FaceBustV8("Color texture only", -1.56f, surface, hair, colorMaterial);
            var right = FaceBustV8("Same color with normal map", 1.56f, surface, hair, normalMaterial);
            for (int layer = 0; layer < 3; layer++)
                FaceSwatchV8(layer, FaceSwatchTextureV8(layer));

            var baseArrow = FaceNormalArrowV8(left, false, Aqua, -.012f);
            var adjustedArrow = FaceNormalArrowV8(right, true, Gold, -.012f);
            return t =>
            {
                var comparisonReference = stage.Find("Library face reference");
                if (comparisonReference && comparisonReference.gameObject.activeSelf)
                    comparisonReference.gameObject.SetActive(false);

                // Both heads have the same mesh and the same shared light.
                // The only material variable in the comparison is normal strength.
                float strength = Second ? 1f : Range(t, .40f, .57f);
                normalMaterial.SetFloat("_BumpScale", strength);
                float sweep = Second ? Range(t, .27f, .86f) : Range(t, .53f, .93f);
                light.transform.rotation = Quaternion.LookRotation(V(Mathf.Lerp(-.88f, .88f, sweep), -.38f, .81f));
                bool showDirection = Second && t >= .05f && t <= .27f;
                baseArrow.SetActive(showDirection);
                adjustedArrow.SetActive(showDirection);
            };
        }

        Transform FaceBustV8(string name, float x, Mesh face, Mesh hair, Material skin)
        {
            var root = Group(name, V(x, 1.72f, 0));
            FaceMeshObjectV8(root, "Identical face surface", face, skin);
            FaceMeshObjectV8(root, "Original swept hair cap", hair, Paint(HairV8));
            Shape(PrimitiveType.Sphere, "Neck", V(0, -.94f, .03f), V(.72f, .92f, .67f), SkinV8, root);
            Shape(PrimitiveType.Sphere, "Jacket shoulders", V(0, -1.11f, .06f), V(1.78f, .38f, .82f), Slate, root);
            Shape(PrimitiveType.Sphere, "Nose bridge", V(0, -.12f, -.78f), V(.32f, .48f, .36f), SkinV8, root);
            Shape(PrimitiveType.Sphere, "Mouth", V(0, -.43f, -.76f), V(.41f, .072f, .032f),
                new Color32(126, 71, 63, 255), root);

            foreach (float side in new[] { -1f, 1f })
            {
                Shape(PrimitiveType.Sphere, "Ear", V(side * .90f, 0, .02f), V(.30f, .47f, .24f), SkinV8, root);
                var eye = Shape(PrimitiveType.Sphere, "Eye white", V(side * .36f, .205f, -.742f),
                    V(.38f, .202f, .102f), Paper, root);
                eye.localRotation = Quaternion.Euler(0, side * -17f, 0);
                Shape(PrimitiveType.Sphere, "Iris", V(side * .345f, .198f, -.796f), V(.145f, .150f, .044f),
                    new Color32(73, 62, 55, 255), root);
                Shape(PrimitiveType.Sphere, "Pupil and lid", V(side * .347f, .196f, -.820f),
                    V(.063f, .105f, .014f), HairV8, root);
                var brow = Shape(PrimitiveType.Sphere, "Swept brow", V(side * .365f, .376f, -.713f),
                    V(.42f, .10f, .080f), HairV8, root);
                brow.localRotation = Quaternion.Euler(0, side * -14f, side * -8f);
            }
            return root;
        }

        void FaceMeshObjectV8(Transform parent, string name, Mesh mesh, Material material)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.AddComponent<MeshFilter>().sharedMesh = mesh;
            item.AddComponent<MeshRenderer>().sharedMaterial = material;
        }

        Mesh MakeFaceMeshV8(bool hair)
        {
            const int columns = 64;
            const int rows = 36;
            int stride = columns + 1;
            var vertices = new Vector3[stride * (rows + 1)];
            var normals = new Vector3[vertices.Length];
            var tangents = new Vector4[vertices.Length];
            var uv = new Vector2[vertices.Length];
            var triangles = new int[columns * rows * 6];
            int index = 0;
            for (int row = 0; row <= rows; row++)
            for (int column = 0; column <= columns; column++)
            {
                float u = column / (float)columns;
                float v = Mathf.Lerp(.001f, .999f, row / (float)rows);
                if (hair)
                {
                    float angle = (u - .5f) * Mathf.PI * 2f;
                    float front = Mathf.Pow(Mathf.Clamp01(.5f + .5f * Mathf.Cos(angle)), 2.4f);
                    float fringe = .638f + .045f * Mathf.Sin(angle * 2.6f) - .025f * Mathf.Cos(angle * 6f);
                    v = Mathf.Lerp(Mathf.Lerp(.34f, fringe, front), .999f, v);
                }
                int vertex = row * stride + column;
                FacePointV8(u, v, out var point, out var direction, out var tangent);
                vertices[vertex] = hair ? point * 1.043f + V(0, .027f, 0) : point;
                normals[vertex] = direction;
                tangents[vertex] = new Vector4(tangent.x, tangent.y, tangent.z, -1);
                uv[vertex] = new Vector2(u, v);
                if (row == rows || column == columns) continue;
                triangles[index++] = vertex;
                triangles[index++] = vertex + stride;
                triangles[index++] = vertex + 1;
                triangles[index++] = vertex + 1;
                triangles[index++] = vertex + stride;
                triangles[index++] = vertex + stride + 1;
            }
            var mesh = new Mesh { name = hair ? "Original face hair cap" : "Shared ellipsoid face geometry" };
            mesh.vertices = vertices;
            mesh.normals = normals;
            mesh.tangents = tangents;
            mesh.uv = uv;
            mesh.triangles = triangles;
            mesh.RecalculateBounds();
            owned.Add(mesh);
            return mesh;
        }

        static void FacePointV8(float u, float v, out Vector3 point, out Vector3 normal, out Vector3 tangent)
        {
            float longitude = (u - .5f) * Mathf.PI * 2f;
            float latitude = (v - .5f) * Mathf.PI;
            var sphere = V(Mathf.Sin(longitude) * Mathf.Cos(latitude),
                Mathf.Sin(latitude), -Mathf.Cos(longitude) * Mathf.Cos(latitude));
            point = Vector3.Scale(sphere, FaceRadiiV8);
            normal = V(sphere.x / FaceRadiiV8.x, sphere.y / FaceRadiiV8.y, sphere.z / FaceRadiiV8.z).normalized;
            tangent = V(Mathf.Cos(longitude) * FaceRadiiV8.x, 0, Mathf.Sin(longitude) * FaceRadiiV8.z).normalized;
        }

        static float FaceScarCenterV8(float v) => .577f - .20f * (v - .48f) + .005f * Mathf.Sin((v - .48f) * 37f);

        static float FaceScarV8(float u, float v)
        {
            float taper = 1f - Mathf.SmoothStep(0, 1, Mathf.InverseLerp(.037f, .099f, Mathf.Abs(v - .48f)));
            float across = (u - FaceScarCenterV8(v)) / .0165f;
            return taper * Mathf.Exp(-across * across);
        }

        static Vector3 FaceTangentNormalV8(float u, float v)
        {
            const float step = .001f;
            const float strength = .034f / (2f * step);
            float du = (FaceScarV8(u + step, v) - FaceScarV8(u - step, v)) * strength;
            float dv = (FaceScarV8(u, v + step) - FaceScarV8(u, v - step)) * strength;
            return V(du, dv, 1).normalized;
        }

        static Color FaceColorV8(float u, float v)
        {
            float patch = FaceScarV8(u, v);
            float cheeks = Mathf.Exp(-Mathf.Pow((v - .47f) * 15f, 2)) *
                Mathf.Clamp01((Mathf.Cos((u - .5f) * Mathf.PI * 2f) - .2f) * 1.4f);
            var skin = Color.Lerp(SkinV8, new Color32(224, 144, 121, 255), cheeks * .34f);
            return Color.Lerp(skin, new Color32(172, 94, 91, 255), patch * .43f);
        }

        static Color NormalPixelV8(float u, float v)
        {
            var normal = FaceTangentNormalV8(u, v);
            return new Color(normal.x * .5f + .5f, normal.y * .5f + .5f, normal.z * .5f + .5f, 1);
        }

        Texture2D FaceTextureV8(string name, bool normal)
        {
            var texture = new Texture2D(TextureWidthV8, TextureHeightV8, TextureFormat.RGBA32, true, normal)
            {
                name = name,
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp
            };
            var pixels = new Color[TextureWidthV8 * TextureHeightV8];
            for (int y = 0; y < TextureHeightV8; y++)
            for (int x = 0; x < TextureWidthV8; x++)
            {
                float u = x / (float)(TextureWidthV8 - 1);
                float v = y / (float)(TextureHeightV8 - 1);
                pixels[y * TextureWidthV8 + x] = normal ? NormalPixelV8(u, v) : FaceColorV8(u, v);
            }
            texture.SetPixels(pixels);
            texture.Apply(true, true);
            owned.Add(texture);
            return texture;
        }

        Texture2D FaceSwatchTextureV8(int layer)
        {
            const int width = 160;
            const int height = 80;
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false) { filterMode = FilterMode.Bilinear };
            texture.name = layer == 0 ? "Color texture sample" : layer == 1 ? "Scar placement mask sample" : "Tangent-space normal sample";
            var pixels = new Color[width * height];
            for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
            {
                float u = Mathf.Lerp(.518f, .633f, x / (float)(width - 1));
                float v = Mathf.Lerp(.375f, .585f, y / (float)(height - 1));
                pixels[y * width + x] = layer == 0 ? FaceColorV8(u, v) :
                    layer == 1 ? Color.Lerp(Color.black, Color.white, FaceScarV8(u, v)) : NormalPixelV8(u, v);
            }
            texture.SetPixels(pixels);
            texture.Apply(false, true);
            owned.Add(texture);
            return texture;
        }

        void FaceSwatchV8(int layer, Texture2D texture)
        {
            float x = (layer - 1) * 1.81f;
            var border = layer == 0 ? Gold : layer == 1 ? Paper : Blue;
            Block(texture.name + " frame", V(x, -.11f, -.91f), V(1.64f, .62f, .035f), border);
            var quad = Shape(PrimitiveType.Quad, texture.name, V(x, -.11f, -.949f), V(1.55f, .53f, 1), Paper);
            var shader = Shader.Find(GraphicsSettings.currentRenderPipeline ?
                "Universal Render Pipeline/Unlit" : "Unlit/Texture");
            var material = new Material(shader) { mainTexture = texture };
            owned.Add(material);
            quad.GetComponent<Renderer>().sharedMaterial = material;
        }

        GameObject FaceNormalArrowV8(Transform head, bool applyMap, Color color, float across)
        {
            const float v = .465f;
            float u = FaceScarCenterV8(v) + across;
            FacePointV8(u, v, out var point, out var normal, out var tangent);
            if (applyMap)
            {
                var mapped = FaceTangentNormalV8(u, v);
                var bitangent = -Vector3.Cross(normal, tangent);
                normal = (tangent * mapped.x + bitangent * mapped.y + normal * mapped.z).normalized;
            }
            Vector3 origin = head.localPosition + point + V(0, 0, -.085f);
            Vector3 end = origin + normal * .72f;
            var arrow = Group("Surface normal direction", Vector3.zero);
            AttachArrowPart(origin, end, .044f);
            Vector3 side = Vector3.Cross(normal, Vector3.forward).normalized * .092f;
            AttachArrowPart(end - normal * .21f + side, end, .040f);
            AttachArrowPart(end - normal * .21f - side, end, .040f);
            return arrow.gameObject;

            void AttachArrowPart(Vector3 a, Vector3 b, float thickness)
            {
                var part = Bar("Normal arrow", a, b, thickness, color);
                part.SetParent(arrow, true);
            }
        }
    }
}
