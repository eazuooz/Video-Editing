using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

// Produces reviewable candidate files only. It never changes the input vendor source.
static class VendorSourceRewrite
{
    public class Operation
    {
        public string inputPath { get; set; }
        public string expectedSha256 { get; set; }
        public string outputPath { get; set; }
        public string globalNamespace { get; set; }
        public string wholeFileGuard { get; set; }
        public bool portGzip { get; set; }
        public bool portZipExtraction { get; set; }
        public bool portCausticsRenderGraph { get; set; }
        public bool optionalCinemachineInjection { get; set; }
        public bool guardEditorUsings { get; set; }
        public Dictionary<string, string> conditionalEditorMembers { get; set; } = new();
        public Dictionary<string, string> namespaceMap { get; set; } = new();
        public Dictionary<string, string> literalMap { get; set; } = new();
        public string reason { get; set; }
    }
    sealed class Rewriter : CSharpSyntaxRewriter
    {
        readonly Operation operation;
        readonly HashSet<string> gzipOutputs = new();
        public Rewriter(Operation operation) { this.operation = operation; }
        public override SyntaxNode VisitCompilationUnit(CompilationUnitSyntax node)
        {
            if (operation.portGzip)
                foreach (var variable in node.DescendantNodes().OfType<VariableDeclaratorSyntax>())
                    if (variable.Initializer?.Value is ObjectCreationExpressionSyntax create && create.Type.ToString().EndsWith("GZipOutputStream")) gzipOutputs.Add(variable.Identifier.ValueText);
            return base.VisitCompilationUnit(node);
        }
        string Mapped(string value)
        {
            foreach (var pair in operation.namespaceMap.OrderByDescending(pair => pair.Key.Length))
                if (value == pair.Key || value.StartsWith(pair.Key + ".", StringComparison.Ordinal)) return pair.Value + value.Substring(pair.Key.Length);
            return value;
        }
        public override SyntaxNode VisitNamespaceDeclaration(NamespaceDeclarationSyntax node)
        {
            var changed = (NamespaceDeclarationSyntax)base.VisitNamespaceDeclaration(node);
            string mapped = Mapped(node.Name.ToString());
            return changed.WithName(SyntaxFactory.ParseName(mapped).WithTriviaFrom(node.Name));
        }
        public override SyntaxNode VisitFileScopedNamespaceDeclaration(FileScopedNamespaceDeclarationSyntax node)
        {
            var changed = (FileScopedNamespaceDeclarationSyntax)base.VisitFileScopedNamespaceDeclaration(node);
            return changed.WithName(SyntaxFactory.ParseName(Mapped(node.Name.ToString())).WithTriviaFrom(node.Name));
        }
        public override SyntaxNode VisitUsingDirective(UsingDirectiveSyntax node)
        {
            string name = node.Name.ToString();
            if (operation.optionalCinemachineInjection && (name == "Unity.Cinemachine" || name == "TimeWarp.Modules.Cameras")) return null;
            string mapped = (operation.portGzip && name == "Unity.SharpZipLib.GZip") ||
                (operation.portZipExtraction && name == "Unity.SharpZipLib.Utils") ? "System.IO.Compression" : Mapped(name);
            var changed = node.WithName(SyntaxFactory.ParseName(mapped).WithTriviaFrom(node.Name));
            return changed;
        }
        public override SyntaxNode VisitIdentifierName(IdentifierNameSyntax node)
        {
            if (operation.portGzip && (node.Identifier.ValueText == "GZipOutputStream" || node.Identifier.ValueText == "GZipInputStream"))
                return SyntaxFactory.IdentifierName("GZipStream").WithTriviaFrom(node);
            return base.VisitIdentifierName(node);
        }
        public override SyntaxNode VisitObjectCreationExpression(ObjectCreationExpressionSyntax node)
        {
            string type = node.Type.ToString();
            var changed = (ObjectCreationExpressionSyntax)base.VisitObjectCreationExpression(node);
            if (operation.portGzip && (type.EndsWith("GZipOutputStream") || type.EndsWith("GZipInputStream")))
            {
                string mode = type.EndsWith("GZipOutputStream") ? "CompressionMode.Compress" : "CompressionMode.Decompress";
                return changed.WithArgumentList(changed.ArgumentList.AddArguments(SyntaxFactory.Argument(SyntaxFactory.ParseExpression(mode)),
                    SyntaxFactory.Argument(SyntaxFactory.LiteralExpression(SyntaxKind.TrueLiteralExpression))));
            }
            return changed;
        }
        public override SyntaxNode VisitLocalDeclarationStatement(LocalDeclarationStatementSyntax node)
        {
            bool gzip = operation.portGzip && node.Declaration.Variables.Any(variable => variable.Initializer?.Value is ObjectCreationExpressionSyntax create &&
                (create.Type.ToString().EndsWith("GZipOutputStream") || create.Type.ToString().EndsWith("GZipInputStream")));
            var changed = (LocalDeclarationStatementSyntax)base.VisitLocalDeclarationStatement(node);
            return gzip ? changed.WithoutLeadingTrivia().WithUsingKeyword(SyntaxFactory.Token(SyntaxKind.UsingKeyword)
                .WithTrailingTrivia(SyntaxFactory.Space)).WithLeadingTrivia(node.GetLeadingTrivia()) : changed;
        }
        public override SyntaxNode VisitInvocationExpression(InvocationExpressionSyntax node)
        {
            var changed = (InvocationExpressionSyntax)base.VisitInvocationExpression(node);
            if (operation.portZipExtraction && node.Expression.ToString() == "ZipUtility.UncompressFromZip")
            {
                if (node.ArgumentList.Arguments.Count != 3 || !node.ArgumentList.Arguments[1].Expression.IsKind(SyntaxKind.NullLiteralExpression))
                    throw new InvalidDataException("Only the reviewed unencrypted ZIP extraction may use this port.");
                return changed.WithExpression(SyntaxFactory.ParseExpression("ZipFile.ExtractToDirectory"))
                    .WithArgumentList(SyntaxFactory.ArgumentList(SyntaxFactory.SeparatedList(new[] { changed.ArgumentList.Arguments[0], changed.ArgumentList.Arguments[2] })));
            }
            if (operation.portGzip && node.Expression is MemberAccessExpressionSyntax member && member.Name.Identifier.ValueText == "Finish" &&
                member.Expression is IdentifierNameSyntax variable && gzipOutputs.Contains(variable.Identifier.ValueText))
                return changed.WithExpression(((MemberAccessExpressionSyntax)changed.Expression).WithName(SyntaxFactory.IdentifierName("Dispose").WithTriviaFrom(member.Name)));
            return changed;
        }
        public override SyntaxNode VisitExpressionStatement(ExpressionStatementSyntax node)
        {
            if (operation.portGzip && node.Expression is InvocationExpressionSyntax call && call.Expression is MemberAccessExpressionSyntax member &&
                member.Name.Identifier.ValueText == "Finish" && member.Expression is IdentifierNameSyntax variable && gzipOutputs.Contains(variable.Identifier.ValueText))
                // An empty source stream never enters the vendor's copy loop. A zero
                // byte write initializes the framework compressor so Dispose emits a
                // valid empty GZip member, matching SharpZipLib.Finish semantics.
                return SyntaxFactory.ParseStatement("{ " + variable.Identifier.ValueText + ".Write(System.Array.Empty<byte>(), 0, 0); " +
                    variable.Identifier.ValueText + ".Dispose(); }").WithTriviaFrom(node);
            return base.VisitExpressionStatement(node);
        }
        public override SyntaxNode VisitMethodDeclaration(MethodDeclarationSyntax node)
        {
            var changed = (MethodDeclarationSyntax)base.VisitMethodDeclaration(node);
            if (!operation.conditionalEditorMembers.TryGetValue(node.Identifier.ValueText, out string fallback)) return changed;
            if (changed.Body == null) throw new InvalidDataException("Conditional editor method has no block body: " + node.Identifier.ValueText);
            string body = "{\n#if UNITY_EDITOR\n" + changed.Body.Statements.ToFullString() + "\n#else\n" + fallback + "\n#endif\n}";
            return changed.WithBody((BlockSyntax)SyntaxFactory.ParseStatement(body).WithTriviaFrom(changed.Body));
        }
        public override SyntaxNode VisitAccessorDeclaration(AccessorDeclarationSyntax node)
        {
            var changed = (AccessorDeclarationSyntax)base.VisitAccessorDeclaration(node);
            if (node.Parent?.Parent is not PropertyDeclarationSyntax property ||
                !operation.conditionalEditorMembers.TryGetValue(property.Identifier.ValueText + "." + node.Keyword.ValueText, out string fallback)) return changed;
            if (changed.Body == null) throw new InvalidDataException("Conditional editor accessor has no block body: " + property.Identifier.ValueText);
            string body = "{\n#if UNITY_EDITOR\n" + changed.Body.Statements.ToFullString() + "\n#else\n" + fallback + "\n#endif\n}";
            return changed.WithBody((BlockSyntax)SyntaxFactory.ParseStatement(body).WithTriviaFrom(changed.Body));
        }
        public override SyntaxNode VisitIfStatement(IfStatementSyntax node)
        {
            if (!operation.optionalCinemachineInjection || node.Condition.ToString() != "rule.InjectTimeCinemachine") return base.VisitIfStatement(node);
            // Preserve the optional feature without a compile-time edge from core to its adapter assembly.
            return SyntaxFactory.ParseStatement(@"if (rule.InjectTimeCinemachine)
{
    var brainType = System.Type.GetType(""Unity.Cinemachine.CinemachineBrain, Unity.Cinemachine"");
    var cameraType = System.Type.GetType(""Unity.Cinemachine.CinemachineCamera, Unity.Cinemachine"");
    var adapterType = System.Type.GetType(""TimeWarp.Modules.Cameras.TimeCinemachineBrain, TimeWarp.Cinemachine"");
    if (adapterType != null && ((brainType != null && target.GetComponent(brainType) != null) ||
        (cameraType != null && target.GetComponent(cameraType) != null)) && target.GetComponent(adapterType) == null)
        target.AddComponent(adapterType);
}").WithTriviaFrom(node);
        }
        public override SyntaxNode VisitQualifiedName(QualifiedNameSyntax node)
        {
            string before = node.ToString(), after = Mapped(before);
            return before == after ? base.VisitQualifiedName(node) : SyntaxFactory.ParseName(after).WithTriviaFrom(node);
        }
        public override SyntaxNode VisitMemberAccessExpression(MemberAccessExpressionSyntax node)
        {
            string before = node.ToString(), after = Mapped(before);
            return before == after ? base.VisitMemberAccessExpression(node) : SyntaxFactory.ParseExpression(after).WithTriviaFrom(node);
        }
        public override SyntaxNode VisitLiteralExpression(LiteralExpressionSyntax node)
        {
            if (node.IsKind(SyntaxKind.StringLiteralExpression) && operation.literalMap.TryGetValue(node.Token.ValueText, out string value))
                return SyntaxFactory.LiteralExpression(SyntaxKind.StringLiteralExpression, SyntaxFactory.Literal(value)).WithTriviaFrom(node);
            return base.VisitLiteralExpression(node);
        }
    }
    static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    static readonly CSharpParseOptions Parse = CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.Latest)
        .WithPreprocessorSymbols("UNITY_EDITOR", "UNITY_EDITOR_WIN", "UNITY_STANDALONE", "UNITY_STANDALONE_WIN", "ENABLE_INPUT_SYSTEM", "UNITY_6000_0_OR_NEWER", "UNITY_6000_6_OR_NEWER");
    static string PortCaustics(string source)
    {
        var root = CSharpSyntaxTree.ParseText(source, Parse).GetRoot();
        var pass = root.DescendantNodes().OfType<ClassDeclarationSyntax>().Single(type => type.Identifier.ValueText == "CausticsPass");
        var setup = pass.Members.OfType<MethodDeclarationSyntax>().Single(method => method.Identifier.ValueText == "OnCameraSetup");
        var execute = pass.Members.OfType<MethodDeclarationSyntax>().Single(method => method.Identifier.ValueText == "Execute");
        var scope = execute.Body.DescendantNodes().OfType<UsingStatementSyntax>().Single(statement => statement.Expression?.ToString().StartsWith("new ProfilingScope(") == true);
        var statements = ((BlockSyntax)scope.Statement).Statements;
        var draw = statements.OfType<ExpressionStatementSyntax>().Single(statement => statement.Expression is InvocationExpressionSyntax call && call.Expression.ToString() == "cmd.DrawMesh");
        if (statements.OfType<ExpressionStatementSyntax>().Count(statement => statement.Expression is InvocationExpressionSyntax call && call.Expression.ToString() == "cmd.SetRenderTarget") != 1)
            throw new InvalidDataException("Unexpected caustics target setup; manual render graph review required.");
        string uniforms = string.Concat(statements.Where(statement => statement is not ExpressionStatementSyntax expression ||
            expression.Expression is not InvocationExpressionSyntax call || (call.Expression.ToString() != "cmd.DrawMesh" && call.Expression.ToString() != "cmd.SetRenderTarget")).Select(statement => statement.ToFullString()));
        string drawCode = draw.ToString().Replace("cmd.DrawMesh", "context.cmd.DrawMesh").Replace("_mat,", "data.material,");
        string modern = @"
#if UNITY_6000_6_OR_NEWER
            sealed class CausticsRenderGraphData { public Material material; }
            public override void RecordRenderGraph(UnityEngine.Rendering.RenderGraphModule.RenderGraph renderGraph, ContextContainer frameData)
            {
                var resources = frameData.Get<UniversalResourceData>();
                if (_mat == null || !resources.activeColorTexture.IsValid() || !resources.cameraDepthTexture.IsValid()) return;
" + uniforms + @"
                using (var builder = renderGraph.AddRasterRenderPass<CausticsRenderGraphData>(""EmaceArt.Caustics"", out var data, _sampler))
                {
                    data.material = _mat;
                    builder.UseTexture(resources.cameraDepthTexture, UnityEngine.Rendering.RenderGraphModule.AccessFlags.Read);
                    builder.SetRenderAttachment(resources.activeColorTexture, 0, UnityEngine.Rendering.RenderGraphModule.AccessFlags.ReadWrite);
                    builder.SetRenderFunc((CausticsRenderGraphData data, UnityEngine.Rendering.RenderGraphModule.RasterGraphContext context) =>
                    {
                        " + drawCode + @"
                    });
                }
            }
#else
" + source.Substring(setup.FullSpan.Start, execute.FullSpan.End - setup.FullSpan.Start) + "\n#endif\n";
        source = source.Substring(0, setup.FullSpan.Start) + modern + source.Substring(execute.FullSpan.End);
        root = CSharpSyntaxTree.ParseText(source, Parse).GetRoot();
        var constructor = root.DescendantNodes().OfType<ConstructorDeclarationSyntax>().Single(method => method.Identifier.ValueText == "CausticsPass");
        int insert = constructor.Body.OpenBraceToken.Span.End;
        return source.Insert(insert, "\n                ConfigureInput(ScriptableRenderPassInput.Depth);\n");
    }
    static string GuardEditorUsings(string source, string newline)
    {
        var tree = CSharpSyntaxTree.ParseText(source, Parse); var text = tree.GetText();
        var edits = tree.GetRoot().DescendantNodes().OfType<UsingDirectiveSyntax>()
            .Where(use => use.Name.ToString() == "UnityEditor" || use.Name.ToString().StartsWith("UnityEditor."))
            .Select(use => (start: text.Lines.GetLineFromPosition(use.SpanStart).Start,
                end: text.Lines.GetLineFromPosition(use.Span.End).EndIncludingLineBreak)).Distinct().OrderByDescending(edit => edit.start);
        foreach (var edit in edits)
            source = source.Substring(0, edit.start) + "#if UNITY_EDITOR" + newline + source.Substring(edit.start, edit.end - edit.start) + "#endif" + newline + source.Substring(edit.end);
        return source;
    }
    public static int Main(string[] args)
    {
        var operations = JsonSerializer.Deserialize<Operation[]>(File.ReadAllText(args[0]));
        var receipts = new List<object>();
        foreach (var operation in operations)
        {
            byte[] before = File.ReadAllBytes(operation.inputPath);
            if (!string.Equals(Hash(before), operation.expectedSha256, StringComparison.OrdinalIgnoreCase)) throw new IOException("Source hash changed: " + operation.inputPath);
            if (Path.GetFullPath(operation.inputPath).Equals(Path.GetFullPath(operation.outputPath), StringComparison.OrdinalIgnoreCase)) throw new IOException("Candidate output must differ from vendor input.");
            string source = File.ReadAllText(operation.inputPath), newline = source.Contains("\r\n") ? "\r\n" : "\n";
            var tree = CSharpSyntaxTree.ParseText(source, Parse);
            var root = (CompilationUnitSyntax)new Rewriter(operation).Visit(tree.GetRoot());
            if (!string.IsNullOrEmpty(operation.globalNamespace))
            {
                if (root.Members.OfType<BaseNamespaceDeclarationSyntax>().Any()) throw new InvalidDataException("Global wrapping requested for an already namespaced file: " + operation.inputPath);
                var wrapper = SyntaxFactory.NamespaceDeclaration(SyntaxFactory.ParseName(operation.globalNamespace))
                    .WithNamespaceKeyword(SyntaxFactory.Token(SyntaxKind.NamespaceKeyword).WithTrailingTrivia(SyntaxFactory.Space))
                    .WithOpenBraceToken(SyntaxFactory.Token(SyntaxKind.OpenBraceToken).WithLeadingTrivia(SyntaxFactory.EndOfLine(newline)).WithTrailingTrivia(SyntaxFactory.EndOfLine(newline)))
                    .WithMembers(root.Members)
                    .WithCloseBraceToken(SyntaxFactory.Token(SyntaxKind.CloseBraceToken).WithLeadingTrivia(SyntaxFactory.EndOfLine(newline)).WithTrailingTrivia(SyntaxFactory.EndOfLine(newline)));
                root = root.WithMembers(SyntaxFactory.SingletonList<MemberDeclarationSyntax>(wrapper));
            }
            string result = root.ToFullString();
            if (operation.portCausticsRenderGraph) result = PortCaustics(result);
            if (operation.guardEditorUsings) result = GuardEditorUsings(result, newline);
            if (!string.IsNullOrEmpty(operation.wholeFileGuard))
                result = "// Yamyam local integration: explicit opt-in; original archive remains unchanged." + newline + "#if " + operation.wholeFileGuard + newline + result + newline + "#endif" + newline;
            var checkedTree = CSharpSyntaxTree.ParseText(result, Parse);
            var errors = checkedTree.GetDiagnostics().Where(error => error.Severity == DiagnosticSeverity.Error).ToArray();
            // Validate both default (possibly excluded) and the guarded/opted-in full source.
            var guardSymbols = (operation.wholeFileGuard ?? "").Split(new[] { ' ', '&', '|', '!', '(', ')' }, StringSplitOptions.RemoveEmptyEntries).Where(symbol => symbol.StartsWith("YAMYAM_"));
            var enabled = CSharpSyntaxTree.ParseText(result, Parse.WithPreprocessorSymbols(Parse.PreprocessorSymbolNames.Concat(guardSymbols)));
            errors = errors.Concat(enabled.GetDiagnostics().Where(error => error.Severity == DiagnosticSeverity.Error)).ToArray();
            var player = CSharpSyntaxTree.ParseText(result, Parse.WithPreprocessorSymbols(Parse.PreprocessorSymbolNames.Where(symbol => !symbol.StartsWith("UNITY_EDITOR"))));
            errors = errors.Concat(player.GetDiagnostics().Where(error => error.Severity == DiagnosticSeverity.Error)).ToArray();
            if (errors.Length > 0) throw new InvalidDataException(operation.inputPath + ": " + string.Join("; ", errors.Select(error => error.ToString())));
            Directory.CreateDirectory(Path.GetDirectoryName(operation.outputPath));
            bool bom = before.Length >= 3 && before[0] == 0xef && before[1] == 0xbb && before[2] == 0xbf;
            File.WriteAllText(operation.outputPath, result, new UTF8Encoding(bom));
            receipts.Add(new { operation.inputPath, operation.outputPath, originalSha256 = Hash(before), adaptedSha256 = Hash(File.ReadAllBytes(operation.outputPath)), operation.reason,
                operation.namespaceMap, operation.globalNamespace, operation.wholeFileGuard, operation.literalMap, operation.portGzip,
                operation.portZipExtraction, operation.portCausticsRenderGraph,
                operation.optionalCinemachineInjection, operation.guardEditorUsings, operation.conditionalEditorMembers, syntaxCheckedDefaultAndOptInAndPlayer = true });
        }
        File.WriteAllText(args[1], JsonSerializer.Serialize(receipts, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine(JsonSerializer.Serialize(new { candidates = receipts.Count, receiptPath = args[1], vendorInputsChanged = false }));
        return 0;
    }
}
