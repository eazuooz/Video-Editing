Shader "Hidden/Yamyam/NaiveHistory" {SubShader{Cull Off ZWrite Off ZTest Always Pass{
    CGPROGRAM
    #pragma vertex vert_img
    #pragma fragment frag
    #include "UnityCG.cginc"
    sampler2D _MainTex,_PreviousTex;float _Feedback;
    fixed4 frag(v2f_img i):SV_Target{return lerp(tex2D(_MainTex,i.uv),tex2D(_PreviousTex,i.uv),_Feedback);}
    ENDCG
}}}
