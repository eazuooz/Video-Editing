using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

// Read-only parser for the two actual Unity Material texture-map layouts.
// Every raw reference must map to an actual native property; unknown shapes fail.
public static class YamyamAssetLibraryMaterialTextureParser
{
    public sealed class Reference { public string property, fileId, guid; }
    const string Scalar = @"(?<property>""(?:[^""\\\r\n]|\\.)*""|'(?:[^'\r\n]|'')*'|[^:'""\r\n]+)";
    const string Value = @"\{fileID:[ \t]*(?<fileId>-?\d+)(?:,[ \t]*guid:[ \t]*(?<guid>[a-fA-F0-9]{32}))?(?:,[ \t]*type:[ \t]*\d+)?[ \t]*\}[ \t]*\r?$";
    static readonly Regex Marker = new Regex(@"(?m)^[ \t]*m_Texture[ \t]*:", RegexOptions.Compiled);
    static readonly Regex RawReference = new Regex(@"m_Texture:\s*\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([a-fA-F0-9]{32}))?", RegexOptions.Compiled);
    static readonly Regex Modern = new Regex(@"(?m)^(?<indent> *)-[ \t]+" + Scalar + @":[ \t]*\r?\n\k<indent>    m_Texture:[ \t]*" + Value, RegexOptions.Compiled);
    static readonly Regex Legacy = new Regex(@"(?m)^(?<indent> *)data:[ \t]*\r?\n\k<indent>  first:[ \t]*\r?\n\k<indent>    name:[ \t]*" + Scalar + @"[ \t]*\r?\n\k<indent>  second:[ \t]*\r?\n\k<indent>    m_Texture:[ \t]*" + Value, RegexOptions.Compiled);

    static string PropertyName(string token)
    {
        token = token.Trim(); if (token.Length == 0) return null;
        if (token[0] == '\'')
        {
            if (token.Length < 2 || token[token.Length - 1] != '\'') return null;
            string inner = token.Substring(1, token.Length - 2);
            if (inner.Replace("''", "").Contains("'")) return null;
            return inner.Replace("''", "'");
        }
        if (token[0] != '"') return token.IndexOfAny(new[] { '\'', '"', '#', '\t', ' ' }) < 0 ? token : null;
        if (token.Length < 2 || token[token.Length - 1] != '"') return null;
        var result = new StringBuilder();
        for (int index = 1; index < token.Length - 1; index++)
        {
            char value = token[index];
            if (value != '\\') { if (value == '"') return null; result.Append(value); continue; }
            if (++index >= token.Length - 1) return null;
            switch (token[index])
            {
                case '\\': result.Append('\\'); break;
                case '"': result.Append('"'); break;
                case '/': result.Append('/'); break;
                case 'u':
                    if (index + 4 >= token.Length - 1) return null;
                    ushort code; if (!ushort.TryParse(token.Substring(index + 1, 4), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out code)) return null;
                    result.Append((char)code); index += 4; break;
                default: return null; // Shader property names do not need control/newline escapes.
            }
        }
        return result.ToString();
    }

    public static bool TryParse(string text, ISet<string> nativeSavedNames, out List<Reference> references)
    {
        references = new List<Reference>();
        if (text == null || nativeSavedNames == null) return false;
        var matches = Modern.Matches(text).Cast<Match>().Concat(Legacy.Matches(text).Cast<Match>()).OrderBy(value => value.Index).ToArray();
        if (matches.Length != Marker.Matches(text).Count || matches.Length != RawReference.Matches(text).Count) return false;
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (Match match in matches)
        {
            string property = PropertyName(match.Groups["property"].Value);
            if (string.IsNullOrEmpty(property) || property.Any(char.IsControl) || !nativeSavedNames.Contains(property) || !seen.Add(property)) return false;
            references.Add(new Reference { property = property, fileId = match.Groups["fileId"].Value, guid = match.Groups["guid"].Value.ToLowerInvariant() });
        }
        // Preserve the existing native SerializedObject checks for properties with
        // no textual YAML entry, including the two source binary .mat files.
        return true;
    }
}
