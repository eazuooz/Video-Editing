Shader "Yamyam/FlowSolid" { Properties {_Color("Colour",Color)=(.3,.3,.3,1)} SubShader { Tags {"RenderType"="Opaque"} Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 float4 _Color;struct a{float4 vertex:POSITION;float3 n:NORMAL;};struct v{float4 p:SV_POSITION;float3 n:TEXCOORD0;};v vert(a i){v o;o.p=UnityObjectToClipPos(i.vertex);o.n=UnityObjectToWorldNormal(i.n);return o;}float4 frag(v i):SV_Target{float d=saturate(dot(normalize(i.n),normalize(float3(-.6,1,-.7))));return float4(_Color.rgb*(.32+.68*d),1);}
 ENDCG } } }
