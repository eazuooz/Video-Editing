Shader "Yamyam/DistinctiveSurface" {Properties{_Color("Color",Color)=(1,1,1,1) _MainTex("Texture",2D)="white"{}}
 SubShader{Tags{"RenderType"="Opaque"} Pass{CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct appdata{float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;};struct v2f{float4 p:SV_POSITION;float3 n:TEXCOORD0;float2 uv:TEXCOORD1;};sampler2D _MainTex;float4 _Color;
 v2f vert(appdata v){v2f o;o.p=UnityObjectToClipPos(v.vertex);o.n=UnityObjectToWorldNormal(v.normal);o.uv=v.uv;return o;}
 fixed4 frag(v2f i):SV_Target{float d=.48+.52*max(0,dot(normalize(i.n),normalize(float3(-.5,1,-.7))));return fixed4(tex2D(_MainTex,i.uv).rgb*_Color.rgb*d,1);}
 ENDCG}}}
