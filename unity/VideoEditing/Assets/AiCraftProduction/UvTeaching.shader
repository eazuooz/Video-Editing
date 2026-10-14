Shader "Yamyam/UvTeaching" {
 Properties { _Highlight("Highlighted UV cell",Vector)=(3,3,0,0) }
 SubShader { Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"}
 Pass { HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 struct A {float4 vertex:POSITION;float2 uv:TEXCOORD0;};
 struct V {float4 position:SV_POSITION;float2 uv:TEXCOORD0;};
 CBUFFER_START(UnityPerMaterial) float4 _Highlight; CBUFFER_END
 V vert(A i){V o;o.position=TransformObjectToHClip(i.vertex.xyz);o.uv=i.uv;return o;}
 half4 frag(V i):SV_Target {
 float2 cell=floor(i.uv*8), f=frac(i.uv*8);
 half3 color=lerp(half3(.14,.30,.32),half3(.45,.78,.76),fmod(cell.x+cell.y,2));
 if(all(abs(cell-_Highlight.xy)<.1))color=half3(.91,.81,.51);
 if(min(min(f.x,f.y),min(1-f.x,1-f.y))<.035)color*=.35;
 return half4(color,1);
 }
 ENDHLSL }
 }
}
