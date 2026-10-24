Shader "Yamyam/PortalTraversalView" {Properties {_MainTex("Portal view",2D)="black"{}} SubShader {Tags {"Queue"="Geometry+5"} Cull Off Pass {CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _MainTex;struct V{float4 pos:SV_POSITION;float4 screen:TEXCOORD0;};
 V vert(float4 v:POSITION){V o;o.pos=UnityObjectToClipPos(v);o.screen=ComputeScreenPos(o.pos);return o;}
 fixed4 frag(V i):SV_Target{return tex2Dproj(_MainTex,UNITY_PROJ_COORD(i.screen));}
 ENDCG}}}
