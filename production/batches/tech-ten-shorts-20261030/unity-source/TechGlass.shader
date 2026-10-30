Shader "Yamyam/TechTen/Glass"
{
 Properties { _Color("Tint", Color)=(.45,.85,.9,.16) }
 SubShader {
  Tags {"Queue"="Transparent" "RenderType"="Transparent"}
  Pass {Blend SrcAlpha OneMinusSrcAlpha ZWrite Off Cull Back
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   struct v2f {float4 p:SV_POSITION;float3 n:TEXCOORD0;float3 view:TEXCOORD1;};float4 _Color;
   v2f vert(appdata_base v){v2f o;o.p=UnityObjectToClipPos(v.vertex);float3 w=mul(unity_ObjectToWorld,v.vertex).xyz;o.n=UnityObjectToWorldNormal(v.normal);o.view=_WorldSpaceCameraPos-w;return o;}
   fixed4 frag(v2f i):SV_Target {float f=pow(1-saturate(abs(dot(normalize(i.n),normalize(i.view)))),3);return float4(_Color.rgb,.08+.55*f);}
   ENDCG
  }
 }
}
