using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

// Physical filesystem access only. AssetDatabase paths, manifests and ownership
// comparisons keep ordinary canonical paths; enumeration never leaks a prefix.
public static class YamyamAssetLibraryIO
{
    public static string NormalPath(string path)
    {
        if (path == null) throw new ArgumentNullException("path");
        if (Path.DirectorySeparatorChar != '\\') return Path.GetFullPath(path);
        string value = path.Replace('/', '\\');
        if (value.StartsWith(@"\\.\", StringComparison.Ordinal) || value.StartsWith(@"\??\", StringComparison.Ordinal))
            throw new IOException("Device paths are outside asset-library filesystem access.");
        if (value.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) value = @"\\" + value.Substring(8);
        else if (value.StartsWith(@"\\?\", StringComparison.Ordinal))
        {
            value = value.Substring(4);
            if (value.Length < 3 || !char.IsLetter(value[0]) || value[1] != ':' || value[2] != '\\')
                throw new IOException("Only drive and UNC extended paths are supported.");
        }
        return Path.GetFullPath(value);
    }
    public static string ExtendedPath(string path)
    {
        string normal = NormalPath(path);
        if (Path.DirectorySeparatorChar != '\\') return normal;
        return normal.StartsWith(@"\\", StringComparison.Ordinal) ? @"\\?\UNC\" + normal.Substring(2) : @"\\?\" + normal;
    }
    public static class Files
    {
        public static bool Exists(string path) { return path != null && System.IO.File.Exists(ExtendedPath(path)); }
        public static FileAttributes GetAttributes(string path) { return System.IO.File.GetAttributes(ExtendedPath(path)); }
        public static System.IO.FileStream OpenRead(string path) { return System.IO.File.OpenRead(ExtendedPath(path)); }
        public static string ReadAllText(string path) { return System.IO.File.ReadAllText(ExtendedPath(path)); }
        public static byte[] ReadAllBytes(string path) { return System.IO.File.ReadAllBytes(ExtendedPath(path)); }
        public static void WriteAllText(string path, string contents) { System.IO.File.WriteAllText(ExtendedPath(path), contents); }
        public static void WriteAllText(string path, string contents, Encoding encoding) { System.IO.File.WriteAllText(ExtendedPath(path), contents, encoding); }
        public static void WriteAllBytes(string path, byte[] contents) { System.IO.File.WriteAllBytes(ExtendedPath(path), contents); }
        public static void Delete(string path) { System.IO.File.Delete(ExtendedPath(path)); }
        public static void Move(string source, string destination) { System.IO.File.Move(ExtendedPath(source), ExtendedPath(destination)); }
        public static void Copy(string source, string destination, bool overwrite) { System.IO.File.Copy(ExtendedPath(source), ExtendedPath(destination), overwrite); }
        public static void Replace(string source, string destination, string backup) { System.IO.File.Replace(ExtendedPath(source), ExtendedPath(destination), backup == null ? null : ExtendedPath(backup)); }
    }
    public static class Directories
    {
        public static bool Exists(string path) { return path != null && System.IO.Directory.Exists(ExtendedPath(path)); }
        public static DirectoryInfo CreateDirectory(string path) { return System.IO.Directory.CreateDirectory(ExtendedPath(path)); }
        public static IEnumerable<string> EnumerateFileSystemEntries(string path) { return System.IO.Directory.EnumerateFileSystemEntries(ExtendedPath(path)).Select(NormalPath); }
        public static IEnumerable<string> EnumerateFiles(string path, string pattern) { return System.IO.Directory.EnumerateFiles(ExtendedPath(path), pattern).Select(NormalPath); }
        public static string[] GetFiles(string path, string pattern, SearchOption option) { return System.IO.Directory.GetFiles(ExtendedPath(path), pattern, option).Select(NormalPath).ToArray(); }
        public static void Delete(string path, bool recursive) { System.IO.Directory.Delete(ExtendedPath(path), recursive); }
        public static void Move(string source, string destination) { System.IO.Directory.Move(ExtendedPath(source), ExtendedPath(destination)); }
    }
    public sealed class Info
    {
        readonly FileInfo value;
        public Info(string path) { value = new FileInfo(ExtendedPath(path)); }
        public string FullName { get { return NormalPath(value.FullName); } }
        public bool Exists { get { return value.Exists; } }
        public long Length { get { return value.Length; } }
        public DateTime LastWriteTimeUtc { get { return value.LastWriteTimeUtc; } }
        public DateTime CreationTimeUtc { get { return value.CreationTimeUtc; } }
    }
    public sealed class Stream : System.IO.FileStream
    {
        public Stream(string path, FileMode mode, FileAccess access, FileShare share) : base(ExtendedPath(path), mode, access, share) { }
    }
}
