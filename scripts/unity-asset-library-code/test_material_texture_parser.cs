// Compile this synthetic-only executable together with
// YamyamAssetLibraryMaterialTextureParser.cs; only standard .NET libraries are needed.
// This preserves the 35 synthetic cases already exercised by the owned Mono fixture.
using System;
using System.Collections.Generic;
using T = YamyamAssetLibraryMaterialTextureParser;
public static class MaterialTextureParserRegression
{
    static int passed;
    static void Check(bool value, string context) { if (!value) throw new Exception("Fixture failed: " + context); passed++; }
    static bool Parse(string text, string[] names, out List<T.Reference> references) { return T.TryParse(text, new HashSet<string>(names, StringComparer.Ordinal), out references); }
    static string Modern(string property, string reference) { return "    - " + property + ":\n        m_Texture: " + reference + "\n        m_Scale: {x: 1, y: 1}\n"; }
    static string Legacy(string property, string reference) { return "      data:\n        first:\n          name: " + property + "\n        second:\n          m_Texture: " + reference + "\n          m_Scale: {x: 1, y: 1}\n"; }
    public static void Main()
    {
        const string guid="abcdef0123456789abcdef0123456789";
        string nonnull="{fileID: 2800000, guid: " + guid + ", type: 3}";
        string zero="{fileID: 0}"; List<T.Reference> refs;
        foreach (string body in new[] { Modern("_MainTex",nonnull), Legacy("_MainTex",nonnull) }) {
            Check(Parse(body,new[]{"_MainTex"},out refs),"plain two layouts");
            Check(refs.Count==1 && refs[0].property=="_MainTex" && refs[0].guid==guid && refs[0].fileId=="2800000","exact identity retained");
            Check(Parse(body.Replace("\n","\r\n"),new[]{"_MainTex"},out refs),"CRLF");
        }
        foreach(string property in new[]{"\"_MainTex\"","'_MainTex'","\"\\u005fMainTex\""}) {
            Check(Parse(Modern(property,zero),new[]{"_MainTex"},out refs),"modern quoted scalar");
            Check(Parse(Legacy(property,zero),new[]{"_MainTex"},out refs),"legacy quoted scalar");
        }
        Check(Parse("    m_TexEnvs: []\n",new string[0],out refs) && refs.Count==0,"empty map");
        Check(Parse(Modern("_MainTex",zero)+Modern("_BumpMap",nonnull),new[]{"_MainTex","_BumpMap"},out refs) && refs[0].fileId=="0" && refs[0].guid=="","modern zero and nonzero");
        Check(Parse(Legacy("_MainTex",zero)+Legacy("_BumpMap",nonnull),new[]{"_MainTex","_BumpMap"},out refs),"legacy repeated data pairs");
        Check(Parse(Modern("_MainTex","{fileID: -2800000, guid: "+guid.ToUpperInvariant()+", type: 3}"),new[]{"_MainTex"},out refs) && refs[0].guid==guid && refs[0].fileId=="-2800000","negative ID and uppercase GUID");
        Check(Parse(Modern("_MainTex","{fileID: 10300, guid: 0000000000000000f000000000000000, type: 0}"),new[]{"_MainTex"},out refs),"builtin reference kept for existing resolver");
        string valid=Modern("_MainTex",nonnull);
        foreach(string bad in new[]{
            valid.Replace("guid: "+guid,"guid: invalid"),valid.Replace("fileID: 2800000","fileID: unknown"),
            valid.Replace(", type: 3}",", type: 3, unrecognized: 1}"),valid.Replace("m_Texture: ","m_Texture:\n          "),
            valid+"        m_Texture: {fileID: 0}\n",valid+valid,
            valid.Replace("        m_Texture:","      m_Texture:"),valid.Replace("_MainTex:","\"_MainTex:"),
            valid.Replace("_MainTex:","\"\\x5fMainTex\":"),valid.Replace("_MainTex:","\"\\nMainTex\":"),
            Legacy("_MainTex",nonnull).Replace("        second:\n", ""),Legacy("_MainTex",nonnull).Replace("          name:","        name:"),
            valid.Replace("}","") }) Check(!Parse(bad,new[]{"_MainTex"},out refs),"malformed shape/reference must fail");
        Check(!Parse(valid,new[]{"_Other"},out refs),"native property mismatch");
        Check(Parse(valid,new[]{"_MainTex","_BumpMap"},out refs),"native-only slots retain separate SerializedObject reference validation");
        Check(!Parse(valid,new string[0],out refs),"unmapped raw reference");
        Check(!Parse(null,new string[0],out refs),"null text");
        Check(!T.TryParse(valid,null,out refs),"missing native map");
        Console.WriteLine("MaterialTextureParserRegression PASS "+passed+" synthetic preservation/refusal cases. No Unity APIs, vendor fixtures, filesystem reads, or arguments required.");
    }
}
