Shader "Yamyam/PortalTraversalSurface" {
 Properties {_Color("Color",Color)=(1,1,1,1) _MainTex("Texture",2D)="white"{} _ClipPlane("World clip plane",Vector)=(0,0,0,1)}
 SubShader {Tags {"RenderType"="Opaque"} Cull Off Pass {CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct A{float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;};
 struct V{float4 pos:SV_POSITION;float3 normal:TEXCOORD0;float2 uv:TEXCOORD1;float3 world:TEXCOORD2;};
 sampler2D _MainTex;float4 _Color,_ClipPlane;
 V vert(A v){V o;o.pos=UnityObjectToClipPos(v.vertex);o.world=mul(unity_ObjectToWorld,v.vertex).xyz;o.normal=UnityObjectToWorldNormal(v.normal);o.uv=v.uv;return o;}
 fixed4 frag(V i):SV_Target{clip(dot(float4(i.world,1),_ClipPlane));float light=.55+.45*max(0,dot(normalize(i.normal),normalize(float3(-.4,1,-.7))));return float4(tex2D(_MainTex,i.uv).rgb*_Color.rgb*light,1);}
 ENDCG}}
}
