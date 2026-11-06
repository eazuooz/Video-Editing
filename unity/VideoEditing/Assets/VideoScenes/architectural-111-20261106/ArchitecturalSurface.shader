// Self-contained unlit pass with illustrative directional shading. It is not
// a measured lighting result. No pipeline tag / default pass permits the same
// scene asset to be opened in Built-in and the main URP project.
Shader "Yamyam/ArchitecturalSurface" {
    Properties {
        _Color ("Surface tint", Color) = (1,1,1,1)
        _MainTex ("Surface texture", 2D) = "white" {}
    }
    SubShader {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }
        Pass {
            ZWrite On
            ZTest LEqual
            Cull Back
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _Color;
            struct Input { float4 vertex:POSITION; float3 normal:NORMAL; float2 uv:TEXCOORD0; };
            struct Output { float4 position:SV_POSITION; float3 normal:TEXCOORD0; float2 uv:TEXCOORD1; };
            Output vert(Input v) {
                Output o; o.position=UnityObjectToClipPos(v.vertex);
                o.normal=UnityObjectToWorldNormal(v.normal);
                o.uv=TRANSFORM_TEX(v.uv,_MainTex); return o;
            }
            fixed4 frag(Output i):SV_Target {
                float shade=.45+.55*saturate(dot(normalize(i.normal),normalize(float3(-.3,.8,-.5))));
                fixed4 tex=tex2D(_MainTex,i.uv)*_Color;
                return fixed4(tex.rgb*shade,tex.a);
            }
            ENDCG
        }
    }
}
