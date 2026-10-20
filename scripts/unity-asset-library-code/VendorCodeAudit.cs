using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

static class VendorCodeAudit
{
    static readonly JsonSerializerOptions Json = new() { WriteIndented = true };
    static readonly string[] EditorSymbols = { "UNITY_EDITOR", "UNITY_EDITOR_WIN", "UNITY_STANDALONE", "UNITY_STANDALONE_WIN", "UNITY_64", "ENABLE_INPUT_SYSTEM", "UNITY_6000_0_OR_NEWER", "UNITY_6000_6_OR_NEWER" };
    static readonly string[] AutoAttributes = { "InitializeOnLoad", "InitializeOnLoadMethod", "DidReloadScripts", "ExecuteAlways", "ExecuteInEditMode", "RuntimeInitializeOnLoadMethod" };
    static readonly string[] SideEffects = { "OpenURL", "Process.Start", "GetWindow", "ShowWindow", "DisplayDialog", "File.Write", "File.Delete", "Directory.Delete", "Directory.Move", "SaveAssets", "SaveScene", "SaveOpenScenes", "ImportAsset", "Refresh", "DeleteAsset" };
    public class Declaration
    {
        public string metadataFullName { get; set; }
        public string name { get; set; }
        public string ns { get; set; }
        public string kind { get; set; }
        public string[] baseTypes { get; set; }
        public string[] attributes { get; set; }
        public int line { get; set; }
        public bool playerDeclaration { get; set; }
        public bool partial { get; set; }
    }
    public class Script
    {
        public string product { get; set; }
        public string status { get; set; }
        public string path { get; set; }
        public string absolutePath { get; set; }
        public string sha256 { get; set; }
        public string guid { get; set; }
        public Declaration[] declarations { get; set; }
        public string[] usingNamespaces { get; set; }
        public string[] runtimeUsingNamespaces { get; set; }
        public string[] automaticAttributes { get; set; }
        public object[] automaticMembers { get; set; }
        public object[] staticConstructors { get; set; }
        public object[] externalOrAssetOperations { get; set; }
        public string[] shaderFindNames { get; set; }
        public string[] typeLookupNames { get; set; }
        public bool inEditorDirectory { get; set; }
        public bool unguardedEditorOnlyCode { get; set; }
        public string assembly { get; set; }
        public string asmdefPath { get; set; }
        public bool assemblyEditorOnly { get; set; }
        public string[] syntaxErrors { get; set; }
    }
    public class Shader
    {
        public string product { get; set; }
        public string path { get; set; }
        public string absolutePath { get; set; }
        public string sha256 { get; set; }
        public string shaderName { get; set; }
        public string[] customEditors { get; set; }
    }
    public class Dll
    {
        public string product { get; set; }
        public string path { get; set; }
        public string absolutePath { get; set; }
        public string sha256 { get; set; }
        public long bytes { get; set; }
        public string assembly { get; set; }
        public string[] types { get; set; }
        public string[] assemblyReferences { get; set; }
        public string[] automaticEditorTypes { get; set; }
        public string[] automaticEditorMethods { get; set; }
        public string[] editorOrExternalReferences { get; set; }
        public object[] typeDeclarations { get; set; }
        public string[] runtimeComponentTypes { get; set; }
    }
    static string Text(JsonElement value, string property, string fallback = null) => value.TryGetProperty(property, out var item) && item.ValueKind == JsonValueKind.String ? item.GetString() : fallback;
    static string Hash(string path)
    { using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete); return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant(); }
    static string SharedText(string path)
    { using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete); using var reader = new StreamReader(stream); return reader.ReadToEnd(); }
    static string Guid(string path) => File.Exists(path + ".meta") ? Regex.Match(File.ReadAllText(path + ".meta"), @"(?m)^guid:\s*([a-fA-F0-9]{32})").Groups[1].Value : null;
    static int Line(SyntaxTree tree, SyntaxNode node) => tree.GetLineSpan(node.Span).StartLinePosition.Line + 1;
    static string Arity(TypeParameterListSyntax parameters) => parameters == null || parameters.Parameters.Count == 0 ? "" : "`" + parameters.Parameters.Count;
    static string Name(SyntaxNode node) => node is DelegateDeclarationSyntax del ? del.Identifier.ValueText + Arity(del.TypeParameterList) : node is TypeDeclarationSyntax type ? type.Identifier.ValueText + Arity(type.TypeParameterList) : ((BaseTypeDeclarationSyntax)node).Identifier.ValueText;
    static string Namespace(SyntaxNode node) => string.Join(".", node.Ancestors().OfType<BaseNamespaceDeclarationSyntax>().Reverse().Select(ns => ns.Name.ToString()));
    static string Qualified(SyntaxNode node)
    {
        string ns = Namespace(node), name = string.Join("+", node.Ancestors().OfType<TypeDeclarationSyntax>().Reverse().Select(type => Name(type)).Append(Name(node)));
        return ns.Length == 0 ? name : ns + "." + name;
    }
    static IEnumerable<SyntaxNode> Types(SyntaxNode root) => root.DescendantNodes().Where(node => node is BaseTypeDeclarationSyntax || node is DelegateDeclarationSyntax);
    static string AttributeName(AttributeSyntax attribute) => attribute.Name.ToString().Split('.').Last().Replace("Attribute", "");
    static SyntaxNode EnclosingMember(SyntaxNode node) => node.Ancestors().FirstOrDefault(parent => parent is MethodDeclarationSyntax || parent is ConstructorDeclarationSyntax || parent is ClassDeclarationSyntax);
    static string Literal(InvocationExpressionSyntax call) => call.ArgumentList.Arguments.FirstOrDefault()?.Expression is LiteralExpressionSyntax literal && literal.IsKind(SyntaxKind.StringLiteralExpression) ? literal.Token.ValueText : null;
    static Script Inspect(string product, string status, string relative, string path)
    {
        string source = File.ReadAllText(path);
        var tree = CSharpSyntaxTree.ParseText(source, CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.Latest).WithPreprocessorSymbols(EditorSymbols));
        var runtime = CSharpSyntaxTree.ParseText(source, CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.Latest).WithPreprocessorSymbols(EditorSymbols.Where(symbol => !symbol.StartsWith("UNITY_EDITOR"))));
        var root = tree.GetRoot(); var runtimeRoot = runtime.GetRoot();
        var runtimeTypes = Types(runtimeRoot).Select(Qualified).ToHashSet();
        var runtimeUsings = runtimeRoot.DescendantNodes().OfType<UsingDirectiveSyntax>().Select(use => use.Name.ToString()).Distinct().ToArray();
        var declarations = Types(root).Select(node => new Declaration { metadataFullName = Qualified(node), name = Name(node), ns = Namespace(node), kind = node.Kind().ToString(), line = Line(tree, node),
            baseTypes = node is BaseTypeDeclarationSyntax baseType ? baseType.BaseList?.Types.Select(type => type.Type.ToString()).ToArray() ?? Array.Empty<string>() : Array.Empty<string>(),
            attributes = node.ChildNodes().OfType<AttributeListSyntax>().SelectMany(list => list.Attributes).Select(attribute => attribute.Name.ToString()).ToArray(), playerDeclaration = runtimeTypes.Contains(Qualified(node)),
            partial = node is TypeDeclarationSyntax declaration && declaration.Modifiers.Any(token => token.IsKind(SyntaxKind.PartialKeyword)) }).ToArray();
        var automatic = root.DescendantNodes().OfType<AttributeSyntax>().Where(attribute => AutoAttributes.Contains(AttributeName(attribute))).ToArray();
        var calls = root.DescendantNodes().OfType<InvocationExpressionSyntax>().ToArray();
        bool editorDirectory = relative.Replace('\\', '/').Split('/').Contains("Editor");
        return new Script { product = product, status = status, path = relative, absolutePath = path, sha256 = Hash(path), guid = Guid(path), declarations = declarations,
            usingNamespaces = root.DescendantNodes().OfType<UsingDirectiveSyntax>().Select(use => use.Name.ToString()).Distinct().ToArray(), runtimeUsingNamespaces = runtimeUsings,
            automaticAttributes = automatic.Select(AttributeName).Distinct().ToArray(),
            automaticMembers = automatic.Select(attribute => { var member = EnclosingMember(attribute); return (object)new { attribute = AttributeName(attribute), line = Line(tree, attribute),
                member = member is MethodDeclarationSyntax method ? method.Identifier.ValueText : member is ConstructorDeclarationSyntax constructor ? constructor.Identifier.ValueText : member is ClassDeclarationSyntax klass ? klass.Identifier.ValueText : "unknown",
                calls = member?.DescendantNodes().OfType<InvocationExpressionSyntax>().Select(call => call.Expression.ToString()).Distinct().ToArray() ?? Array.Empty<string>() }; }).ToArray(),
            staticConstructors = root.DescendantNodes().OfType<ConstructorDeclarationSyntax>().Where(constructor => constructor.Modifiers.Any(token => token.IsKind(SyntaxKind.StaticKeyword)))
                .Select(constructor => (object)new { type = constructor.Identifier.ValueText, line = Line(tree, constructor), calls = constructor.DescendantNodes().OfType<InvocationExpressionSyntax>().Select(call => call.Expression.ToString()).Distinct().ToArray(),
                    subscriptions = constructor.DescendantNodes().OfType<AssignmentExpressionSyntax>().Where(assign => assign.IsKind(SyntaxKind.AddAssignmentExpression)).Select(assign => assign.ToString()).ToArray() }).ToArray(),
            externalOrAssetOperations = calls.Where(call => SideEffects.Any(marker => call.Expression.ToString().Contains(marker))).Select(call => (object)new { line = Line(tree, call), call = call.Expression.ToString(), firstStringArgument = Literal(call),
                member = EnclosingMember(call) is MethodDeclarationSyntax method ? method.Identifier.ValueText : EnclosingMember(call) is ConstructorDeclarationSyntax constructor ? constructor.Identifier.ValueText : "other" }).ToArray(),
            shaderFindNames = calls.Where(call => call.Expression.ToString().EndsWith("Shader.Find")).Select(Literal).Where(value => value != null).Distinct().ToArray(),
            typeLookupNames = calls.Where(call => call.Expression.ToString().EndsWith("Type.GetType")).Select(Literal).Where(value => value != null).Distinct().ToArray(), inEditorDirectory = editorDirectory,
            unguardedEditorOnlyCode = !editorDirectory && runtimeTypes.Count > 0 && (runtimeUsings.Any(name => name == "UnityEditor" || name.StartsWith("UnityEditor.")) ||
                runtimeRoot.DescendantNodes().OfType<QualifiedNameSyntax>().Any(name => name.ToString().StartsWith("UnityEditor."))),
            syntaxErrors = tree.GetDiagnostics().Where(diagnostic => diagnostic.Severity == DiagnosticSeverity.Error).Select(diagnostic => diagnostic.ToString()).ToArray() };
    }
    static string MetadataName(MetadataReader reader, EntityHandle handle)
    {
        if (handle.Kind == HandleKind.TypeReference)
        { var type = reader.GetTypeReference((TypeReferenceHandle)handle); string ns = reader.GetString(type.Namespace); return (ns.Length == 0 ? "" : ns + ".") + reader.GetString(type.Name); }
        if (handle.Kind == HandleKind.TypeDefinition)
        { var type = reader.GetTypeDefinition((TypeDefinitionHandle)handle); if (!type.GetDeclaringType().IsNil) return MetadataName(reader, type.GetDeclaringType()) + "+" + reader.GetString(type.Name); string ns = reader.GetString(type.Namespace); return (ns.Length == 0 ? "" : ns + ".") + reader.GetString(type.Name); }
        return handle.Kind.ToString();
    }
    static string Attribute(MetadataReader reader, CustomAttributeHandle handle)
    {
        var attribute = reader.GetCustomAttribute(handle);
        if (attribute.Constructor.Kind == HandleKind.MemberReference) return MetadataName(reader, reader.GetMemberReference((MemberReferenceHandle)attribute.Constructor).Parent);
        if (attribute.Constructor.Kind == HandleKind.MethodDefinition) return MetadataName(reader, reader.GetMethodDefinition((MethodDefinitionHandle)attribute.Constructor).GetDeclaringType());
        return "unknown";
    }
    static Dll InspectDll(string product, string relative, string path)
    {
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        using var pe = new PEReader(stream);
        var reader = pe.GetMetadataReader();
        var automaticTypes = new List<string>(); var automaticMethods = new List<string>();
        var declarations = new List<object>(); var runtimeComponents = new List<string>();
        foreach (var handle in reader.TypeDefinitions)
        {
            var type = reader.GetTypeDefinition(handle); string name = MetadataName(reader, handle);
            string baseType = type.BaseType.IsNil ? null : MetadataName(reader, type.BaseType);
            declarations.Add(new { name, baseType, attributes = type.GetCustomAttributes().Select(attribute => Attribute(reader, attribute)).ToArray() });
            if (baseType == "UnityEngine.MonoBehaviour" || baseType == "UnityEngine.ScriptableObject") runtimeComponents.Add(name);
            if (type.GetCustomAttributes().Any(attribute => Attribute(reader, attribute) == "UnityEditor.InitializeOnLoadAttribute")) automaticTypes.Add(name);
            foreach (var methodHandle in type.GetMethods())
            {
                var method = reader.GetMethodDefinition(methodHandle);
                if (method.GetCustomAttributes().Any(attribute => Attribute(reader, attribute) == "UnityEditor.InitializeOnLoadMethodAttribute")) automaticMethods.Add(name + "." + reader.GetString(method.Name));
            }
        }
        var members = reader.MemberReferences.Select(handle => { var member = reader.GetMemberReference(handle); return MetadataName(reader, member.Parent) + "." + reader.GetString(member.Name); }).ToArray();
        stream.Position = 0; string hash = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        return new Dll { product = product, path = relative, absolutePath = path, sha256 = hash, bytes = stream.Length,
            assembly = reader.GetString(reader.GetAssemblyDefinition().Name), types = reader.TypeDefinitions.Select(handle => MetadataName(reader, handle)).Where(name => !name.Contains('<')).OrderBy(name => name).ToArray(),
            assemblyReferences = reader.AssemblyReferences.Select(handle => reader.GetString(reader.GetAssemblyReference(handle).Name)).OrderBy(name => name).ToArray(),
            automaticEditorTypes = automaticTypes.ToArray(), automaticEditorMethods = automaticMethods.ToArray(),
            editorOrExternalReferences = members.Where(member => member.StartsWith("UnityEditor.") || SideEffects.Any(marker => member.Contains(marker))).Distinct().OrderBy(member => member).ToArray(),
            typeDeclarations = declarations.ToArray(), runtimeComponentTypes = runtimeComponents.ToArray() };
    }
    public static int Main(string[] args)
    {
        if (args[0] == "--dll-metadata")
        {
            var requests = JsonSerializer.Deserialize<Dll[]>(File.ReadAllText(args[1]));
            var result = requests.Select(request => InspectDll(request.product, request.path, request.absolutePath)).ToArray();
            File.WriteAllText(args[2], JsonSerializer.Serialize(result, Json));
            Console.WriteLine(JsonSerializer.Serialize(new { output = args[2], dlls = result.Length, foreignAssemblyCodeExecuted = false }));
            return 0;
        }
        string manifestPath = Path.GetFullPath(args[0]), existingPath = Path.GetFullPath(args[1]), output = Path.GetFullPath(args[2]);
        using var manifest = JsonDocument.Parse(SharedText(manifestPath));
        using var existing = JsonDocument.Parse(File.ReadAllText(existingPath));
        string stage = Text(manifest.RootElement, "stageRoot");
        var mainTypes = existing.RootElement.GetProperty("mainTypeNames").EnumerateArray().Select(value => value.GetString()).ToHashSet();
        var packageTypes = existing.RootElement.GetProperty("packageAssemblies").EnumerateArray().SelectMany(assembly => assembly.GetProperty("types").EnumerateArray()).Select(value => value.GetString()).ToHashSet();
        var scripts = new List<Script>(); var shaders = new List<Shader>(); var assemblies = new List<object>(); var dlls = new List<Dll>(); var missing = new List<object>();
        var assemblyScopes = new Dictionary<string, (string name, string path, bool editorOnly)>(StringComparer.OrdinalIgnoreCase);
        int productCount = 0;
        foreach (var product in manifest.RootElement.GetProperty("products").EnumerateArray())
        {
            productCount++; string id = Text(product, "id"), status = Text(product, "status"), work = Text(product, "workDirectory");
            string workTree = string.IsNullOrEmpty(work) ? null : Path.Combine(work, "tree");
            IEnumerable<string> receiptPaths = product.TryGetProperty("files", out var productFiles) && productFiles.ValueKind == JsonValueKind.Array ?
                productFiles.EnumerateArray().Select(file => Text(file, "path")).ToArray() :
                workTree != null && Directory.Exists(workTree) ? Directory.GetFiles(workTree, "*", SearchOption.AllDirectories).Select(path => Path.GetRelativePath(workTree, path).Replace('\\', '/')).ToArray() : Array.Empty<string>();
            foreach (string relative in receiptPaths)
            {
                string extension = Path.GetExtension(relative).ToLowerInvariant();
                if (extension != ".cs" && extension != ".shader" && extension != ".asmdef" && extension != ".asmref" && extension != ".dll") continue;
                string path = Path.Combine(stage, relative.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(path) && !string.IsNullOrEmpty(work)) path = Path.Combine(work, "tree", relative.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(path)) { missing.Add(new { product = id, relative, status }); continue; }
                if (extension == ".cs") scripts.Add(Inspect(id, status, relative, path));
                else if (extension == ".shader")
                {
                    string source = File.ReadAllText(path);
                    shaders.Add(new Shader { product = id, path = relative, absolutePath = path, sha256 = Hash(path), shaderName = Regex.Match(source, "(?m)^\\s*Shader\\s+\"([^\"]+)\"").Groups[1].Value,
                        customEditors = Regex.Matches(source, "\\bCustomEditor(?:ForRenderPipeline)?\\s+\"([^\"]+)\"").Select(match => match.Groups[1].Value).Distinct().ToArray() });
                }
                else if (extension == ".dll") dlls.Add(InspectDll(id, relative, path));
                else
                {
                    using var parsed = JsonDocument.Parse(File.ReadAllText(path));
                    var definition = parsed.RootElement.Clone();
                    assemblies.Add(new { product = id, path = relative, absolutePath = path, sha256 = Hash(path), definition });
                    if (extension == ".asmdef") assemblyScopes[Path.GetDirectoryName(path)] = (Text(definition, "name"), relative,
                        definition.TryGetProperty("includePlatforms", out var platforms) && platforms.ValueKind == JsonValueKind.Array && platforms.EnumerateArray().Any(platform => platform.GetString() == "Editor"));
                }
            }
        }
        foreach (var script in scripts)
        {
            string directory = Path.GetDirectoryName(script.absolutePath);
            bool found = false;
            while (directory != null)
            {
                if (assemblyScopes.TryGetValue(directory, out var scope))
                { script.assembly = scope.name; script.asmdefPath = scope.path; script.assemblyEditorOnly = scope.editorOnly; found = true; break; }
                directory = Path.GetDirectoryName(directory);
            }
            if (!found) { script.assembly = script.inEditorDirectory ? "Assembly-CSharp-Editor" : "Assembly-CSharp"; script.assemblyEditorOnly = script.inEditorDirectory; }
            if (script.assemblyEditorOnly) script.unguardedEditorOnlyCode = false;
        }
        var owners = scripts.SelectMany(script => script.declarations.Select(declaration => new { declaration.metadataFullName, script.product, script.path, declaration.ns, declaration.kind, declaration.baseTypes, declaration.partial }));
        var duplicates = owners.GroupBy(type => type.metadataFullName).Where(group => group.Select(type => type.path).Distinct().Count() > 1).Select(group => new { type = group.Key, allPartialWithinOneProduct = group.Select(type => type.product).Distinct().Count() == 1 && group.All(type => type.partial), owners = group.ToArray() }).ToArray();
        var mainCollisions = owners.Where(type => mainTypes.Contains(type.metadataFullName)).ToArray();
        var packageCollisions = owners.Where(type => packageTypes.Contains(type.metadataFullName)).ToArray();
        var namespaces = owners.Select(type => type.ns).Where(value => !string.IsNullOrEmpty(value)).ToHashSet();
        var packageNamespaces = packageTypes.Concat(dlls.SelectMany(dll => dll.types)).Select(type => type.Contains('.') ? type.Substring(0, type.LastIndexOf('.')) : "").ToHashSet();
        var nonStandardUsingCandidates = scripts.SelectMany(script => script.usingNamespaces.Select(ns => new { script.product, script.path, ns }))
            .Where(use => !use.ns.StartsWith("System") && !use.ns.StartsWith("UnityEditor") && !use.ns.StartsWith("UnityEngine") && !use.ns.StartsWith("Microsoft") &&
                !namespaces.Any(ns => use.ns == ns || use.ns.StartsWith(ns + ".")) && !packageNamespaces.Any(ns => ns == use.ns || ns.StartsWith(use.ns + "."))).ToArray();
        var duplicateShaderNames = shaders.Where(shader => !string.IsNullOrEmpty(shader.shaderName)).GroupBy(shader => shader.shaderName).Where(group => group.Count() > 1)
            .Select(group => new { shaderName = group.Key, owners = group.Select(shader => new { shader.product, shader.path }).ToArray() }).ToArray();
        var report = new { schemaVersion = 1, generatedUtc = DateTime.UtcNow.ToString("o"), manifestPath, manifestSha256 = Hash(manifestPath), existingInventoryPath = existingPath,
            scope = "Read-only Roslyn declaration/conditional/initializer audit of completed or blocked receipt-owned staged files. No Unity process, DLL execution, vendor mutation or script compilation. Full type comparisons use metadata names and nested/generic notation.",
            productsInSnapshot = productCount, scripts, assemblies, dlls, shaders, missingReceiptFiles = missing, duplicateTypes = duplicates,
            existingMainTypeCollisions = mainCollisions, installedPackageTypeCollisions = packageCollisions,
            nonStandardUsingCandidates, duplicateShaderNames,
            adaptationCandidates = new { productScopeRGTools = duplicates.Where(group => group.type.StartsWith("RGTools.")).SelectMany(group => group.owners.Select(owner => owner.product)).Distinct().OrderBy(value => value).ToArray(),
                editorOnlyGuards = scripts.Where(script => script.unguardedEditorOnlyCode).Select(script => new { script.product, script.path, script.sha256 }).ToArray(),
                automaticEditorReview = scripts.Where(script => script.automaticAttributes.Any(attribute => attribute.StartsWith("InitializeOnLoad") || attribute == "DidReloadScripts")).Select(script => new { script.product, script.path, script.automaticAttributes, script.staticConstructors, script.automaticMembers }).ToArray(),
                legacyTMPro = scripts.Where(script => script.declarations.Any(type => type.ns == "TMPro" || type.ns.StartsWith("TMPro."))).Select(script => new { script.product, script.path, script.guid, types = script.declarations.Select(type => type.metadataFullName).ToArray() }).ToArray() } };
        Directory.CreateDirectory(Path.GetDirectoryName(output)); string temporary = output + ".tmp";
        File.WriteAllText(temporary, JsonSerializer.Serialize(report, Json)); File.Move(temporary, output, true);
        Console.WriteLine(JsonSerializer.Serialize(new { output, products = productCount, scripts = scripts.Count, shaders = shaders.Count, duplicateTypes = duplicates.Length, mainCollisions = mainCollisions.Length,
            packageCollisions = packageCollisions.Length, unguardedEditorScripts = scripts.Count(script => script.unguardedEditorOnlyCode), missingReceiptFiles = missing.Count }));
        return 0;
    }
}
