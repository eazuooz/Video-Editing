Shader "Yamyam/TechTen/LiquidCap"
{
 Properties { _Color("Color",Color)=(1,.65,.2,1) }
 SubShader { Tags {"RenderType"="Opaque"} Pass {Cull Off
  CGPROGRAM
  #pragma vertex vert
  #pragma fragment frag
  #include "UnityCG.cginc"
  struct v2f {float4 p:SV_POSITION;float3 world:TEXCOORD0;};float4 _Color;float4x4 _WorldToBottle;
  v2f vert(appdata_base v){v2f o;o.p=UnityObjectToClipPos(v.vertex);o.world=mul(unity_ObjectToWorld,v.vertex).xyz;return o;}
  fixed4 frag(v2f i):SV_Target{float3 p=mul(_WorldToBottle,float4(i.world,1)).xyz;clip(.445-length(p.xz));clip(1.195-abs(p.y));return _Color;}
  ENDCG
 } }
}
