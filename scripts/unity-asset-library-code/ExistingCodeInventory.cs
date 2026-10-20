using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

static class ExistingCodeInventory
{
    static readonly JsonSerializerOptions Json = new() { WriteIndented = true };
    static string Relative(string root, string path) => Path.GetRelativePath(root, path).Replace('\\', '/');
    static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
    static string Guid(string path)
    {
        if (!File.Exists(path + ".meta")) return null;
        return Regex.Match(File.ReadAllText(path + ".meta"), @"(?m)^guid:\s*([a-fA-F0-9]{32})").Groups[1].Value;
    }
    static string Qualified(SyntaxNode node)
    {
        var spaces = node.Ancestors().OfType<BaseNamespaceDeclarationSyntax>().Reverse().Select(ns => ns.Name.ToString());
        var parents = node.Ancestors().OfType<TypeDeclarationSyntax>().Reverse().Select(TypeName);
        string name = node is DelegateDeclarationSyntax del ? del.Identifier.ValueText + Arity(del.TypeParameterList) :
            node is TypeDeclarationSyntax type ? TypeName(type) : ((BaseTypeDeclarationSyntax)node).Identifier.ValueText;
        string ns = string.Join(".", spaces), nesting = string.Join("+", parents.Append(name));
        return ns.Length == 0 ? nesting : ns + "." + nesting;
    }
    static string Arity(TypeParameterListSyntax parameters) => parameters == null || parameters.Parameters.Count == 0 ? "" : "`" + parameters.Parameters.Count;
    static string TypeName(TypeDeclarationSyntax type) => type.Identifier.ValueText + Arity(type.TypeParameterList);
    static string AssemblyFor(string root, string path, Dictionary<string, string> assemblies)
    {
        string directory = Path.GetDirectoryName(path), assetRoot = Path.Combine(root, "Assets");
        while (directory != null && directory.StartsWith(assetRoot, StringComparison.OrdinalIgnoreCase))
        {
            if (assemblies.TryGetValue(directory, out string name)) return name;
            if (directory == assetRoot) break;
            directory = Path.GetDirectoryName(directory);
        }
        return Relative(root, path).Split('/').Contains("Editor") ? "Assembly-CSharp-Editor" : "Assembly-CSharp";
    }
    static string MetadataName(MetadataReader reader, TypeDefinitionHandle handle)
    {
        var type = reader.GetTypeDefinition(handle);
        string name = reader.GetString(type.Name);
        if (!type.GetDeclaringType().IsNil) return MetadataName(reader, type.GetDeclaringType()) + "+" + name;
        string ns = reader.GetString(type.Namespace);
        return ns.Length == 0 ? name : ns + "." + name;
    }
    static string ExportedName(MetadataReader reader, ExportedTypeHandle handle)
    {
        var type = reader.GetExportedType(handle);
        string name = reader.GetString(type.Name);
        if (type.Implementation.Kind == HandleKind.ExportedType) return ExportedName(reader, (ExportedTypeHandle)type.Implementation) + "+" + name;
        string ns = reader.GetString(type.Namespace);
        return ns.Length == 0 ? name : ns + "." + name;
    }
    public static int Main(string[] args)
    {
        string root = Path.GetFullPath(args[0]), output = args[1], assets = Path.Combine(root, "Assets");
        var assemblyRoots = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var asmdefs = new List<object>();
        foreach (string path in Directory.GetFiles(assets, "*.asmdef", SearchOption.AllDirectories).OrderBy(p => p))
        {
            using var parsed = JsonDocument.Parse(File.ReadAllText(path));
            var definition = parsed.RootElement.Clone();
            assemblyRoots[Path.GetDirectoryName(path)] = definition.GetProperty("name").GetString();
            asmdefs.Add(new { path = Relative(root, path), sha256 = Hash(path), guid = Guid(path), definition });
        }
        string[] symbols = { "UNITY_EDITOR", "UNITY_EDITOR_WIN", "UNITY_STANDALONE", "UNITY_STANDALONE_WIN", "UNITY_64", "ENABLE_INPUT_SYSTEM", "UNITY_6000_0_OR_NEWER", "UNITY_6000_6_OR_NEWER" };
        var options = CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.Latest).WithPreprocessorSymbols(symbols);
        var scripts = new List<object>();
        var types = new List<(string name, string path, string assembly, bool partial)>();
        foreach (string path in Directory.GetFiles(assets, "*.cs", SearchOption.AllDirectories).OrderBy(p => p))
        {
            string relative = Relative(root, path), assembly = AssemblyFor(root, path, assemblyRoots);
            var tree = CSharpSyntaxTree.ParseText(File.ReadAllText(path), options);
            var declarations = tree.GetRoot().DescendantNodes().Where(node => node is BaseTypeDeclarationSyntax || node is DelegateDeclarationSyntax).Select(node =>
            {
                string name = Qualified(node);
                var modifiers = node is BaseTypeDeclarationSyntax b ? b.Modifiers : ((DelegateDeclarationSyntax)node).Modifiers;
                bool partial = modifiers.Any(token => token.IsKind(SyntaxKind.PartialKeyword));
                types.Add((name, relative, assembly, partial));
                return new { metadataFullName = name, kind = node.Kind().ToString(), line = tree.GetLineSpan(node.Span).StartLinePosition.Line + 1,
                    modifiers = modifiers.Select(token => token.ValueText).ToArray(), isPartial = partial };
            }).ToArray();
            scripts.Add(new { path = relative, guid = Guid(path), sha256 = Hash(path), assembly, declarations,
                syntaxErrors = tree.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).Select(d => d.ToString()).ToArray() });
        }
        var packages = new List<object>();
        var packageTypes = new HashSet<string>();
        foreach (string path in Directory.GetFiles(Path.Combine(root, "Library/ScriptAssemblies"), "*.dll").OrderBy(p => p))
        {
            if (Path.GetFileName(path).StartsWith("Assembly-CSharp") || Path.GetFileName(path).StartsWith("Yamyam.")) continue;
            using var stream = File.OpenRead(path); using var pe = new PEReader(stream);
            if (!pe.HasMetadata) continue;
            var reader = pe.GetMetadataReader();
            string name = reader.GetString(reader.GetAssemblyDefinition().Name);
            var names = reader.TypeDefinitions.Select(handle => MetadataName(reader, handle))
                .Concat(reader.ExportedTypes.Select(handle => ExportedName(reader, handle))).Where(type => !type.Contains('<'))
                .Distinct().OrderBy(type => type).ToArray();
            foreach (string type in names) packageTypes.Add(type);
            packages.Add(new { assembly = name, path = Relative(root, path), types = names });
        }
        var duplicates = types.GroupBy(type => new { type.name, type.assembly }).Where(group => group.Count() > 1)
            .Select(group => new { metadataFullName = group.Key.name, assembly = group.Key.assembly,
                allPartial = group.All(type => type.partial), paths = group.Select(type => type.path).Distinct().ToArray() }).ToArray();
        var report = new { schemaVersion = 1, generatedUtc = DateTime.UtcNow.ToString("o"), project = root,
            method = "Roslyn syntax trees for Assets declarations; PE metadata only for currently compiled package assemblies. No assembly code executes and no Unity process is started.",
            limits = "Declaration inventory and candidate comparison, not main-project compilation. Package DLL metadata reflects the existing Library cache. Inactive preprocessor branches are excluded using the recorded symbols; nested types use '+' and generic arity uses backtick notation.",
            parseSymbols = symbols, scripts, assemblies = asmdefs,
            assemblyReferences = Directory.GetFiles(assets, "*.asmref", SearchOption.AllDirectories).Select(path => new { path = Relative(root, path), text = File.ReadAllText(path) }).ToArray(),
            mainTypeNames = types.Select(type => type.name).Distinct().OrderBy(type => type).ToArray(), duplicateMainDeclarations = duplicates,
            packageAssemblies = packages,
            packageCollisionCandidates = types.Where(type => packageTypes.Contains(type.name)).Select(type => new { metadataFullName = type.name, path = type.path, type.assembly }).ToArray(),
            textMeshPro = new { present = packageTypes.Any(type => type.StartsWith("TMPro.")), packageTypeNames = packageTypes.Where(type => type.StartsWith("TMPro.")).OrderBy(type => type).ToArray(),
                assetSourcePaths = Directory.GetFiles(assets, "*.cs", SearchOption.AllDirectories).Where(path => File.ReadAllText(path).Contains("namespace TMPro")).Select(path => Relative(root, path)).ToArray() } };
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        File.WriteAllText(output, JsonSerializer.Serialize(report, Json));
        Console.WriteLine(JsonSerializer.Serialize(new { output, scripts = scripts.Count, sourceTypes = types.Count, asmdefs = asmdefs.Count,
            packageAssemblies = packages.Count, packageTypeNames = packageTypes.Count, duplicateGroups = duplicates.Length }));
        return 0;
    }
}
