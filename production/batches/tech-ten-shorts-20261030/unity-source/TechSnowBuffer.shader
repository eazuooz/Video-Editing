Shader "Yamyam/TechTen/SnowBuffer" {
 Properties { _MainTex("Actual buffer",2D)="white"{} _Color("Tint",Color)=(1,1,1,1) }
 SubShader { Tags {"Queue"="Overlay" "RenderType"="Opaque"} Pass {
  ZWrite Off ZTest Always Cull Off
  CGPROGRAM
  #pragma vertex vert
  #pragma fragment frag
  #include "UnityCG.cginc"
  sampler2D _MainTex;float4 _Color;
  struct v2f{float4 pos:SV_POSITION;float2 uv:TEXCOORD0;};
  v2f vert(appdata_base v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.texcoord;return o;}
  fixed4 frag(v2f i):SV_Target{return tex2D(_MainTex,i.uv)*_Color;}
  ENDCG
 } }
}
